"""
Audio Sources Subpackage

Contains various audio input source implementations for the speech-to-text engine.
"""

from .base import AudioSource
from .microphone import MicrophoneSource
from .file import FileSource

__all__ = ["AudioSource", "MicrophoneSource", "FileSource"]
