# NxWebStt Backend Implementation - REQUIRED CHANGES

## Current Status Analysis

### ✅ IMPLEMENTED
- Plugin structure and basic files
- NxSttConfiguration model and schemas
- Basic NxSttService with connection management
- Basic NxSttRouter with upload endpoint

### ❌ MISSING - REQUIRED CHANGES

## REQUIRED IMPLEMENTATION FOR CURRENT FRAMEWORK

## 1. NxSttService - REQUIRED IMPLEMENTATION

### Current Issues:
```python
# Line 27-28: transcribe_file method is incomplete
async def transcribe_file(self, file_path: str, config_id: int) -> str:
    config = await self.get_by_id(config_id)
    # MISSING: Actual transcription logic!

# Line 44-55: handle_audio_chunk method is incomplete  
async def handle_audio_chunk(self, connection_id: str, data: bytes):
    # ... buffer management ...
    config = await self.get_by_id(config_id)
    # MISSING: Actual transcription logic!
```

### Required Implementation:
```python
# IMPORTS AT TOP OF FILE
import numpy as np
from faster_whisper import WhisperModel
from typing import Dict

class NxSttService(BaseCrudService):
    def __init__(self):
        super().__init__()
        self._connections: Dict[str, Dict] = {}
        self._whisper_models: Dict[str, WhisperModel] = {}  # Cache models per config

    async def transcribe_file(self, file_path: str, config_id: int) -> str:
        """File-based transcription using database config"""
        config = await self.get_by_id(config_id)
        
        # ACTUAL TRANSCRIPTION LOGIC:
        if config.whisper_model not in self._whisper_models:
            self._whisper_models[config.whisper_model] = WhisperModel(
                config.whisper_model, 
                device=config.device,
                compute_type="int8"
            )
        
        model = self._whisper_models[config.whisper_model]
        # NO sample_rate parameter - faster-whisper handles this internally
        segments, info = model.transcribe(file_path, language=config.language)
        
        result = ""
        for segment in segments:
            result += segment.text + " "
        return result.strip()

    async def handle_audio_chunk(self, connection_id: str, data: bytes):
        """Process WebSocket audio chunks with per-connection buffer"""
        if connection_id not in self._connections:
            return
            
        # Per-connection buffer management
        self._connections[connection_id]['audio_buffer'] += data
        
        config_id = self._connections[connection_id]['config_id']
        if not config_id:
            raise ValueError("Connection must choose a config before processing audio!")
        
        config = await self.get_by_id(config_id)
        
        # Process in 2-second chunks (16kHz, int16)
        chunk_size_bytes = 16000 * 2 * 2  # 2 seconds worth
        if len(self._connections[connection_id]['audio_buffer']) >= chunk_size_bytes:
            process_chunk_bytes = self._connections[connection_id]['audio_buffer'][:chunk_size_bytes]
            self._connections[connection_id]['audio_buffer'] = self._connections[connection_id]['audio_buffer'][chunk_size_bytes:]
            
            # Convert to numpy array (NO WAV IMPORTS!)
            process_chunk_np = np.frombuffer(process_chunk_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # ACTUAL TRANSCRIPTION LOGIC:
            if config.whisper_model not in self._whisper_models:
                self._whisper_models[config.whisper_model] = WhisperModel(
                    config.whisper_model, 
                    device=config.device,
                    compute_type="int8"
                )
            
            # Transcribe chunk (NO sample_rate!)
            model = self._whisper_models[config.whisper_model]
            segments, info = model.transcribe(process_chunk_np, language=config.language)
            
            result = ""
            for segment in segments:
                result += segment.text
            
            if result.strip():
                # Send result to connection room
                room = f"stt/{connection_id}"
                await self.ws_service.send_ws_message(room, {
                    'event': 'transcription_update',
                    'data': {'text': result.strip(), 'final': False}
                })
```

## 2. Backend WebSocket Handlers - REQUIRED IMPLEMENTATION

### Current Issue:
- No STT-specific WebSocket handlers in `server.py`
- Only generic `join_room` and `leave_room` handlers exist

### Required Implementation:
```python
# Add to faster_backend/nonix_web/server.py in _enable_websocket() method
# IMPORTS AT TOP OF FILE - NO INLINE IMPORTS!
from nonix_di.resolve import NxInject
from nonix_web_stt.services.stt_service import NxSttService

# INJECT SERVICE ONCE - NOT IN EVERY HANDLER!
stt_service: NxSttService = NxInject(NxSttService)

@sio.on("start_streaming")
async def handle_start_streaming(sid, data):
    """Handle STT streaming start"""
    connection_id = data['connection_id']  # UUID from frontend
    config_id = data['config_id']
    await stt_service.handle_start_streaming(connection_id, config_id)
    
    # Send acknowledgement
    await sio.emit('streaming_started', {'data': 'Server is ready to receive audio'}, room=sid)

@sio.on("audio_chunk")
async def handle_audio_chunk(sid, data):
    """Handle STT audio chunks"""
    connection_id = data['connection_id']  # UUID from frontend
    audio_data = data['data']  # Raw audio bytes (Int16Array.buffer from frontend)
    await stt_service.handle_audio_chunk(connection_id, audio_data)

@sio.on("stop_streaming")
async def handle_stop_streaming(sid, data):
    """Handle STT streaming stop"""
    connection_id = data['connection_id']  # UUID from frontend
    await stt_service.handle_disconnect(connection_id)
    
    # Send acknowledgement
    await sio.emit('streaming_stopped', {'data': 'Server stopped receiving audio'}, room=sid)
```

## 3. NxSttRouter - REQUIRED IMPLEMENTATION

### Current Issue:
```python
# Line 13-14: Missing error handling and validation
async def upload_audio(self, audio_file: UploadFile, config_id: int):
    return await self.stt_service.transcribe_file(audio_file, config_id)
```

### Required Implementation:
```python
# IMPORTS AT TOP OF FILE - NO INLINE IMPORTS!
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from nonix_di.resolve import NxInject
from ..services.stt_service import NxSttService

@router("/stt", tags=["STT"])
class NxSttRouter(NxWebServerCrudRouter):
    # INJECT SERVICE - NOT INLINE!
    stt_service: NxSttService = NxInject(NxSttService)

    @route("/upload", methods=["POST"])
    async def upload_audio(self, audio_file: UploadFile, config_id: int):
        """Handle file uploads for transcription"""
        try:
            # Validate file
            if not audio_file.filename:
                raise HTTPException(400, "No selected file")
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                content = await audio_file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            try:
                # Transcribe file
                result = await self.stt_service.transcribe_file(tmp_file_path, config_id)
                return JSONResponse({
                    "transcription": result,
                    "status": "success"
                })
            finally:
                # Clean up temp file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            # Clean up on error
            if 'tmp_file_path' in locals():
                os.unlink(tmp_file_path)
            raise HTTPException(500, f"Transcription failed: {str(e)}")
```

## Summary of Required CODE CHANGES

### 🔥 KEY IMPLEMENTATION REQUIREMENTS:
1. **NO WAV IMPORTS** - Uses numpy array processing directly
2. **NO sample_rate parameter** - faster-whisper handles this internally
3. **2-second chunk processing** - 16000 * 2 * 2 bytes for 16kHz int16 audio
4. **Int16 to Float32 conversion** - `/ 32768.0` normalization
5. **Model caching** - Load once, reuse for performance
6. **Proper error handling** - Clean up temp files on error
7. **Per-connection buffer** - Each connection has its own buffer
8. **NO INLINE IMPORTS** - All imports at top of file
9. **PROPER INJECTION** - Service injected once, not in every handler

### Required Changes:
1. **Complete transcribe_file method** - Add actual transcription logic
2. **Complete handle_audio_chunk method** - Add chunk processing logic  
3. **Add WebSocket handlers** - Add STT handlers to server.py
4. **Fix upload_audio method** - Add proper file handling
5. **Add model caching** - Add Whisper model management
6. **Add audio processing** - Add numpy audio conversion

## Status: ❌ INCOMPLETE - REQUIRES CODE IMPLEMENTATION
The backend plugin structure exists but core functionality is missing!
**ACTUAL TRANSCRIPTION LOGIC PROVIDED ABOVE - IMPLEMENT IT!**