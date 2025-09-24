"""
Speech-to-Text Engine Package

A fully async, Qt-agnostic speech-to-text engine supporting multiple input sources.
Designed for future enhancements like VAD, noise cancellation, and other audio processing features.

Required dependencies:
- numpy: Array operations
- faster-whisper: Speech-to-text transcription
- sounddevice: Audio capture (microphone)
- librosa: Audio file processing
"""

from .engine import SpeechToTextEngine
from .audio_sources.microphone import MicrophoneSource
from .audio_sources.file import FileSource
from .audio_sources.base import AudioSource

__version__ = "0.1.0"
__all__ = ["SpeechToTextEngine", "MicrophoneSource", "FileSource", "AudioSource"]
