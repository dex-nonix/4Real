# 🎯 STT Multimode Implementation Plan

## 📋 Overview

**Single Dropdown Multimode STT System**
- **One dropdown** controls all recording modes
- **Engine-based processing** decisions (not source-based)
- **Source agnostic** - works with any audio source (microphone, file, network, etc.)
- **Proper separation of concerns** - sources provide data, engine handles processing

## 🎛️ Single Dropdown Design

```
Recording Mode: [🎙️ Live Streaming ▼]
                📦 Buffered (Unlimited)
                💾 Buffered (100MB ~47h)
                💾 Buffered (500MB ~4.5h)
                💾 Buffered (1GB ~9h)
                💾 Buffered (2GB ~18h)
                💾 Buffered (5GB ~100h)
                💾 Buffered (10GB ~200h)
```

## 📊 Buffer Size Calculations

**Audio Format:** float32, 16kHz, mono
**Bytes per second:** 16,000 samples × 4 bytes = 64,000 bytes/second
**Bytes per minute:** 64,000 × 60 = 3,840,000 bytes/minute
**MB per minute:** 3,840,000 / 1,048,576 ≈ 3.66 MB/minute

### Size Breakdown:

| Option | Memory (MB) | Hours | Minutes | Total Bytes |
|--------|-------------|-------|---------|-------------|
| 100MB Buffer | 100 | ~47h | ~2,800min | 104,857,600 |
| 500MB Buffer | 500 | ~4.5h | ~270min | 524,288,000 |
| 1GB Buffer | 1,024 | ~9h | ~540min | 1,073,741,824 |
| 2GB Buffer | 2,048 | ~18h | ~1,080min | 2,147,483,648 |
| 5GB Buffer | 5,120 | ~100h | ~6,000min | 5,368,709,120 |
| 10GB Buffer | 10,240 | ~200h | ~12,000min | 10,737,418,240 |

## 🏗️ Architecture Design

### 🎯 Separation of Concerns

**AudioSource Responsibility:**
- ✅ Provide audio data stream
- ✅ Handle source-specific connection/setup
- ✅ Abstract data acquisition (microphone, file, network, etc.)
- ❌ NOT decide processing behavior

**AsyncSTTEngine Responsibility:**
- ✅ Decide processing mode (live vs buffered)
- ✅ Handle memory management and disk spilling
- ✅ Control transcription timing and batching
- ✅ Manage buffer limits and overflow

### 📝 Interface Design

```python
class AudioSource(ABC):
    """Any audio source - microphone, file, network, etc."""
    async def read(self) -> np.ndarray | None:
        """Returns next audio chunk or None when done"""

class AsyncSTTEngine:
    """Processes audio from any source with configurable behavior"""
    def __init__(self, processing_mode="live", buffer_limit_mb=float('inf')):
        self.processing_mode = processing_mode  # "live" or "buffered"
        self.buffer_limit_bytes = buffer_limit_mb * 1024 * 1024
```

## 🔄 Processing Modes

### 🎙️ Live Streaming Mode
```python
# Process 2-second chunks immediately (current working system)
async def _process_live_mode(self):
    audio_buffer = np.array([], dtype=np.float32)
    PROCESSING_INTERVAL_SAMPLES = int(16000 * 2.0)  # 2 seconds

    while True:
        chunk = await self.audio_source.read()
        if chunk is None: break

        audio_buffer = np.concatenate([audio_buffer, chunk.flatten()])

        if len(audio_buffer) >= PROCESSING_INTERVAL_SAMPLES:
            await self._transcribe_chunk(audio_buffer)
            audio_buffer = np.array([], dtype=np.float32)

    # Process any remaining audio
    if len(audio_buffer) > 0:
        await self._transcribe_chunk(audio_buffer)
```

### 📦 Buffered Mode
```python
# Collect all audio, transcribe at end with size limits
async def _process_buffered_mode(self):
    buffer = []
    current_bytes = 0

    while True:
        chunk = await self.audio_source.read()
        if chunk is None: break

        buffer.append(chunk)
        current_bytes += len(chunk) * 4  # float32 = 4 bytes

        # Spill to disk if buffer limit exceeded
        if current_bytes > self.buffer_limit_bytes:
            await self._spill_to_disk(buffer)
            buffer = []
            current_bytes = 0

    # Process remaining buffer
    if buffer:
        complete_audio = np.concatenate(buffer)
        await self._transcribe_chunk(complete_audio)
```

## 💾 Disk Spilling Implementation

```python
async def _spill_to_disk(self, buffer):
    """Write buffer to temporary file when memory limit exceeded"""
    import tempfile
    import soundfile as sf

    if not hasattr(self, '_temp_file'):
        self._temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self._spilled_chunks = []

    # Write current buffer to file
    if buffer:
        audio_data = np.concatenate(buffer)
        sf.write(self._temp_file.name, audio_data, 16000, format='WAV')

    self._spilled_chunks.append(len(buffer))

async def _load_spilled_audio(self):
    """Load spilled audio from disk for final processing"""
    if hasattr(self, '_temp_file'):
        import soundfile as sf
        audio_data, _ = sf.read(self._temp_file.name)
        os.unlink(self._temp_file.name)
        return audio_data
    return np.array([])
```

## 🎛️ UI Implementation

### Dropdown Setup
```python
self.mode_combo = QComboBox()
self.mode_combo.addItems([
    "🎙️ Live Streaming",
    "📦 Buffered (Unlimited)",
    "💾 Buffered (100MB ~47h)",
    "💾 Buffered (500MB ~4.5h)",
    "💾 Buffered (1GB ~9h)",
    "💾 Buffered (2GB ~18h)",
    "💾 Buffered (5GB ~100h)",
    "💾 Buffered (10GB ~200h)"
])
```

### Mode Parsing
```python
def parse_mode_selection(self, mode_text):
    """Parse dropdown selection into processing parameters"""
    if "Live Streaming" in mode_text:
        return "live", float('inf')
    elif "Unlimited" in mode_text:
        return "buffered", float('inf')
    elif "100MB" in mode_text:
        return "buffered", 100
    elif "500MB" in mode_text:
        return "buffered", 500
    elif "1GB" in mode_text:
        return "buffered", 1024
    elif "2GB" in mode_text:
        return "buffered", 2048
    elif "5GB" in mode_text:
        return "buffered", 5120
    elif "10GB" in mode_text:
        return "buffered", 10240
    return "live", float('inf')  # Default fallback
```

### Engine Creation
```python
mode, buffer_mb = self.parse_mode_selection(selected_mode)
microphone = MicrophoneSource(device_index)
engine = AsyncSTTEngine(processing_mode=mode, buffer_limit_mb=buffer_mb)
engine.set_audio_source(microphone)
```

## 🎯 Mode Behaviors

| Mode | Real-time | Buffering | Transcription | Memory Usage |
|------|-----------|-----------|----------------|--------------|
| **Live Streaming** | ✅ Immediate | 2-second chunks | Continuous | Low |
| **Buffered Unlimited** | ❌ No | All audio | At end | High (unlimited) |
| **Buffered Limited** | ❌ No | Until limit | At end + spills | Controlled |

## 🔧 Implementation Steps

1. **Add processing_mode parameter** to AsyncSTTEngine.__init__()
2. **Add buffer_limit_mb parameter** to AsyncSTTEngine.__init__()
3. **Implement _process_live_mode()** (copy current _process_audio logic)
4. **Implement _process_buffered_mode()** (accumulate with spilling)
5. **Update _process_audio()** to route based on mode
6. **Add disk spilling methods** for buffer overflow
7. **Update UI** with single dropdown
8. **Add mode parsing logic** in UI

## 🎉 Benefits

- ✅ **Single dropdown** - no UI confusion
- ✅ **Source agnostic** - works with any AudioSource
- ✅ **Memory controlled** - configurable limits with disk spilling
- ✅ **Performance optimized** - live mode for immediate feedback
- ✅ **Quality optimized** - buffered mode for complete context
- ✅ **Extensible** - easy to add new sources or modes

## 🚀 Result

**Professional multimode STT system:**
- **Live Streaming**: Immediate transcription as you speak
- **Buffered Modes**: Configurable memory limits with disk overflow
- **Any Source**: Microphone, file, network, Bluetooth, etc.
- **Clean Architecture**: Proper separation of concerns

**One dropdown, infinite possibilities!** 🎯
