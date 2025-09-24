# Speech-to-Text Engine

A fully async, Qt-agnostic speech-to-text engine supporting multiple input sources with clean architecture designed for extensibility.

## Features

- **Fully Async**: Built from the ground up with asyncio for modern Python applications
- **Qt-Agnostic**: No framework dependencies - works with any UI framework or headless
- **Multiple Input Sources**: Support for microphone and audio file inputs
- **Extensible Architecture**: Clean interfaces for adding VAD, noise cancellation, and other audio processing features
- **Production Ready**: Robust error handling, clean state management, and thread-safe operations
- **Optimized Performance**: Efficient async operations with proper resource management

## Installation

### Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install numpy faster-whisper sounddevice librosa
```

### System Requirements

- **Python 3.8+**
- **Microphone access** (for microphone input)
- **Audio files** (for file input)

## Quick Start

### Basic Microphone Usage

```python
import asyncio
from speech_to_text import SpeechToTextEngine, MicrophoneSource

async def main():
    # Create engine
    engine = SpeechToTextEngine()

    # Set up microphone source
    mic_source = MicrophoneSource(device_index=0)
    engine.set_audio_source(mic_source)

    # Define transcription callback
    def on_transcript(text: str):
        print(f"Transcribed: {text}")

    engine.on_transcript = on_transcript

    # Start processing
    await engine.start_processing()

    # Let it run for a while
    await asyncio.sleep(30)

    # Stop processing
    await engine.stop_processing()

asyncio.run(main())
```

### File Transcription

```python
import asyncio
from speech_to_text import SpeechToTextEngine, FileSource

async def transcribe_file():
    # Create engine
    engine = SpeechToTextEngine()

    # Set up file source
    file_source = FileSource("path/to/audio.wav")
    engine.set_audio_source(file_source)

    # Collect transcription
    transcript = ""

    def on_transcript(text: str):
        nonlocal transcript
        transcript += text

    engine.on_transcript = on_transcript

    # Process file
    await engine.start_processing()
    await engine.stop_processing()

    print(f"Full transcript: {transcript}")

asyncio.run(transcribe_file())
```

## Architecture

### Core Components

- **SpeechToTextEngine**: Main engine orchestrating transcription
- **AudioSource**: Abstract base class for audio inputs
- **MicrophoneSource**: Real-time microphone audio capture
- **FileSource**: Audio file loading and chunking

### Async Design

The engine uses asyncio throughout for:
- Non-blocking audio processing
- Proper resource management
- Clean cancellation and cleanup
- Integration with modern async frameworks

### Thread Safety

Audio capture happens in separate threads but integrates cleanly with the async event loop through thread-safe queues.

## API Reference

### SpeechToTextEngine

#### Constructor
```python
SpeechToTextEngine(
    model_size: str = "tiny.en",
    on_transcript: Optional[Callable[[str], None]] = None,
    on_error: Optional[Callable[[str], None]] = None,
    on_processing_start: Optional[Callable[[], None]] = None,
    on_processing_end: Optional[Callable[[], None]] = None,
    target_sample_rate: int = 16000,
    chunk_duration_seconds: float = 2.0,
    min_chunk_duration_seconds: float = 0.2
)
```

#### Methods
- `set_audio_source(source: AudioSource)` - Set the audio input source
- `async start_processing()` - Start transcription processing
- `async stop_processing()` - Stop transcription processing
- `transcribe_file(file_path: str) -> str` - Transcribe audio file synchronously

#### Properties
- `is_processing: bool` - Check if engine is actively processing

### AudioSource Interface

All audio sources implement:
- `start()` - Begin audio capture/preparation
- `stop()` - Stop audio capture/cleanup
- `is_active() -> bool` - Check if source is active
- `async get_next_chunk() -> np.ndarray` - Get next audio chunk

### MicrophoneSource

```python
MicrophoneSource(device_index: int, sample_rate: int = 16000)
```

Captures audio from system microphone using sounddevice.

### FileSource

```python
FileSource(
    file_path: str,
    chunk_duration_seconds: float = 2.0,
    target_sample_rate: int = 16000
)
```

Loads and chunks audio files using librosa.

## Configuration

### Model Sizes

- `"tiny.en"` - Fastest, least accurate (English only)
- `"base.en"` - Good balance (English only)
- `"small.en"` - Better accuracy (English only)
- `"medium.en"` - High accuracy
- `"large"` - Best accuracy, slowest

### Audio Parameters

- **target_sample_rate**: 16000 Hz (Whisper requirement)
- **chunk_duration_seconds**: 2.0 (processing chunk size)
- **min_chunk_duration_seconds**: 0.2 (minimum chunk to process)

## Qt Integration Example

```python
import asyncio
from PyQt6.QtWidgets import QApplication
import qasync
from speech_to_text import SpeechToTextEngine, MicrophoneSource

class QtSpeechApp:
    def __init__(self):
        self.engine = SpeechToTextEngine(
            on_transcript=self.handle_transcript,
            on_error=self.handle_error
        )

        # Set up Qt signal connections
        # ... Qt UI setup ...

    def handle_transcript(self, text: str):
        # Update Qt UI with transcription
        pass

    def handle_error(self, error: str):
        # Show error in Qt UI
        pass

    async def start_recording(self):
        mic_source = MicrophoneSource(device_index=0)
        self.engine.set_audio_source(mic_source)
        await self.engine.start_processing()

# Qt app setup
app = QApplication([])
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)

qt_app = QtSpeechApp()

with loop:
    loop.run_forever()
```

## Error Handling

The engine provides comprehensive error handling:

- **Model loading failures** - Clear error messages
- **Audio device issues** - Device-specific error reporting
- **File loading problems** - Path and format error details
- **Processing errors** - Async exception propagation

## Performance Considerations

- **Model size vs speed trade-off** - Choose appropriate model for your use case
- **Chunk sizes** - Larger chunks reduce overhead but increase latency
- **Async integration** - Engine is designed for async-first applications
- **Resource cleanup** - Proper stop() calls ensure clean shutdown

## Future Extensions

The architecture is designed to easily add:

- **Voice Activity Detection (VAD)** - Filter silent audio
- **Noise Cancellation** - Improve audio quality
- **Speaker Diarization** - Identify speakers
- **Language Detection** - Automatic language switching
- **Custom Audio Sources** - Network streams, custom devices

## Troubleshooting

### Common Issues

1. **"sounddevice not available"**
   - Install sounddevice: `pip install sounddevice`
   - Ensure microphone permissions

2. **"librosa not available"**
   - Install librosa: `pip install librosa`
   - Required for file processing

3. **"Model not initialized"**
   - Check Whisper model download
   - Verify internet connection for first run

4. **Asyncio errors**
   - Ensure proper event loop setup
   - Don't call async methods from sync context

### Debug Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

The package is designed with extensibility in mind:

1. **Add new AudioSource implementations** - Inherit from AudioSource base class
2. **Extend processing pipeline** - Add preprocessing steps in engine
3. **Add new model integrations** - Abstract model interface for alternatives to Whisper

## License

This package is designed for maximum compatibility and can be integrated into any Python application following standard licensing practices.
