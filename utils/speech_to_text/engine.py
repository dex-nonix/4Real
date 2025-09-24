import asyncio
import numpy as np
import logging
from typing import Optional, Callable
from enum import Enum
from faster_whisper import WhisperModel

from .audio_sources.base import AudioSource


class EngineState(Enum):
    """Engine processing states for clean state management."""
    IDLE = "idle"
    STARTING = "starting"
    RECORDING = "recording"
    STOPPING = "stopping"


class SpeechToTextEngine:
    """
    Standalone speech-to-text engine with extensible architecture.

    Supports multiple input sources and is designed for future enhancements
    like VAD, noise cancellation, and other audio processing features.
    """

    def __init__(self,
                 model_size: str = "tiny.en",
                 on_transcript: Optional[Callable[[str], None]] = None,
                 on_error: Optional[Callable[[str], None]] = None,
                 on_processing_start: Optional[Callable[[], None]] = None,
                 on_processing_end: Optional[Callable[[], None]] = None,
                 target_sample_rate: int = 16000,
                 chunk_duration_seconds: float = 2.0,
                 min_chunk_duration_seconds: float = 0.2):
        """
        Initialize the speech-to-text engine.

        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            on_transcript: Callback for transcription results
            on_error: Callback for error messages
            on_processing_start: Callback when processing starts
            on_processing_end: Callback when processing ends
            target_sample_rate: Target sample rate for Whisper (16000 Hz)
            chunk_duration_seconds: Duration of audio chunks to process (2.0 seconds)
            min_chunk_duration_seconds: Minimum chunk duration to process (0.2 seconds)
        """
        self.model_size = model_size
        self.on_transcript = on_transcript
        self.on_error = on_error
        self.on_processing_start = on_processing_start
        self.on_processing_end = on_processing_end

        # Audio processing parameters - match original AudioProcessor
        self.target_samplerate = target_sample_rate  # Match original naming
        self.chunk_duration_seconds = chunk_duration_seconds
        self.min_chunk_duration_seconds = min_chunk_duration_seconds
        self.samples_per_chunk = int(target_sample_rate * chunk_duration_seconds)

        # State variables - match original AudioProcessor
        self.is_recording = False
        self.native_samplerate = None

        # Model and processing state
        self.whisper_model: Optional[WhisperModel] = None
        self.audio_source: Optional[AudioSource] = None
        self._processing_task: Optional[asyncio.Task] = None
        self.state = EngineState.IDLE
        self.audio_buffer = np.array([], dtype=np.float32)
        self._stop_event = asyncio.Event()

        # Initialize the model
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the Whisper model."""
        try:
            logging.info(f"Loading Whisper model: {self.model_size}")
            self.whisper_model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8"
            )
            logging.info("Whisper model loaded successfully")
        except Exception as e:
            error_msg = f"Failed to load Whisper model: {e}"
            logging.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            raise RuntimeError(error_msg)

    def set_audio_source(self, source: AudioSource) -> None:
        """
        Set the audio input source.

        Args:
            source: AudioSource implementation (MicrophoneSource, FileSource, etc.)
        """
        self.audio_source = source

    async def start_processing(self) -> None:
        """Start the speech-to-text processing."""
        if self.state != EngineState.IDLE:
            logging.warning(f"Cannot start processing: Engine is in {self.state.value} state")
            return

        if not self.whisper_model:
            raise RuntimeError("Model not initialized")

        if not self.audio_source:
            raise RuntimeError("No audio source set")

        try:
            logging.info("Starting speech-to-text processing")
            self.state = EngineState.STARTING
            self._stop_event.clear()

            # Ensure clean state - clear any leftover buffers
            self._reset_buffers()

            if self.on_processing_start:
                self.on_processing_start()

            # Start the audio source
            self.audio_source.start()

            # Get native sample rate from audio source - match original AudioProcessor
            if hasattr(self.audio_source, 'native_rate'):
                self.native_samplerate = self.audio_source.native_rate

            self.state = EngineState.RECORDING
            self.is_recording = True  # Match original AudioProcessor
            await self._process_audio_loop()
            logging.info("✅ Speech-to-text processing completed")

        except Exception as e:
            logging.error(f"Failed to start processing: {e}")
            self.state = EngineState.IDLE
            if self.on_error:
                self.on_error(f"Failed to start processing: {e}")
            raise

    async def stop_processing(self) -> None:
        """Stop the speech-to-text processing with guaranteed cleanup."""
        if self.state == EngineState.IDLE:
            return

        if self.state == EngineState.STOPPING:
            logging.debug("Stop already in progress")
            return

        try:
            logging.info("Stopping speech-to-text processing")
            self.state = EngineState.STOPPING
            self._stop_event.set()

            # Stop the audio source first to prevent new data
            if self.audio_source and self.audio_source.is_active():
                self.audio_source.stop()

            # Process any remaining audio in buffer before stopping
            self._process_remaining_buffer()

            # Final cleanup
            self._reset_buffers()
            self.is_recording = False  # Match original AudioProcessor

            self.state = EngineState.IDLE

            if self.on_processing_end:
                self.on_processing_end()

            logging.info("✅ Speech-to-text processing stopped cleanly")

        except Exception as e:
            logging.error(f"Error during stop processing: {e}")
            # Force state reset even on error
            self.state = EngineState.IDLE
            if self.on_error:
                self.on_error(f"Error stopping processing: {e}")


    def _reset_buffers(self) -> None:
        self.audio_buffer = np.array([], dtype=np.float32)

    def _process_remaining_buffer(self) -> None:
        """Process any remaining audio in the buffer before shutdown."""
        if len(self.audio_buffer) > 0:
            min_samples = int(self.target_sample_rate * self.min_chunk_duration_seconds)

            if len(self.audio_buffer) >= min_samples:
                logging.info(f"Processing remaining audio: {len(self.audio_buffer)/self.target_sample_rate:.2f}s")
                self._transcribe_chunk(self.audio_buffer)

    def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe audio from a file.

        Args:
            file_path: Path to audio file

        Returns:
            Transcribed text
        """
        if not self.whisper_model:
            raise RuntimeError("Model not initialized")

        try:
            logging.info(f"Transcribing file: {file_path}")
            segments, _ = self.whisper_model.transcribe(file_path)
            text = "".join(segment.text for segment in segments)
            return text.strip()
        except Exception as e:
            error_msg = f"Failed to transcribe file {file_path}: {e}"
            logging.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            raise

    async def _process_audio_loop(self) -> None:
        """Main async audio processing loop - matches original synchronous processing."""
        logging.info("Async audio processing started")

        try:
            # Run the synchronous processing logic in an executor
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._sync_processing_loop)

        except Exception as e:
            error_msg = f"Error in async audio processing: {e}"
            logging.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)

        logging.info("Async audio processing finished")

    def _sync_processing_loop(self) -> None:
        """Synchronous processing loop - matches original AudioProcessor exactly."""
        while not self._stop_event.is_set() and self.state == EngineState.RECORDING:
            try:
                # Get next audio chunk synchronously with timeout
                raw_chunk = self._get_next_chunk_sync(timeout=0.1)
                if raw_chunk is not None:
                    self._process_microphone_chunk(raw_chunk)

            except Exception as e:
                error_msg = f"Error in sync processing loop: {e}"
                logging.error(error_msg)
                if self.on_error:
                    self.on_error(error_msg)
                break

    def _get_next_chunk_sync(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """Get next audio chunk synchronously."""
        try:
            return self.audio_source.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    @property
    def is_processing(self) -> bool:
        """Check if the engine is currently processing audio."""
        return self.state in [EngineState.STARTING, EngineState.RECORDING, EngineState.STOPPING]

    def _process_microphone_chunk(self, raw_chunk: np.ndarray) -> None:
        """Process a chunk of microphone audio - matches original AudioProcessor logic."""
        # Resample if necessary
        resampled_chunk = self._resample_audio(raw_chunk)

        # Add to buffer
        self.audio_buffer = np.concatenate([self.audio_buffer, resampled_chunk])

        # Process every 2 seconds of audio for a live feel - matches original exactly
        if len(self.audio_buffer) >= self.samples_per_chunk:
            logging.info("🔥 Processing audio chunk (2s interval)")
            chunk = self.audio_buffer[:self.samples_per_chunk]
            self._transcribe_chunk(chunk)
            self.audio_buffer = np.array([], dtype=np.float32)  # Clear buffer completely
            logging.debug("🧹 Audio buffer cleared")

        # Process any leftover audio when stopping - matches original
        if not self.is_processing and len(self.audio_buffer) > 0:
            leftover_duration = len(self.audio_buffer) / self.target_sample_rate
            logging.info(f"🔚 Processing leftover audio: {leftover_duration:.2f}s")
            self._transcribe_chunk(self.audio_buffer)

    def _resample_audio(self, audio_chunk: np.ndarray) -> np.ndarray:
        """Resample audio to target sample rate."""
        # For now, assume input is already at target rate or implement resampling
        # This is a simplified version - you can extend this for proper resampling
        return audio_chunk.flatten().astype(np.float32)

    def _transcribe_chunk(self, audio_chunk: np.ndarray) -> None:
        """Transcribe an audio chunk."""
        chunk_duration = len(audio_chunk) / self.target_sample_rate

        if chunk_duration < self.min_chunk_duration_seconds:
            logging.debug(f"Chunk too small ({chunk_duration:.2f}s), skipping")
            return

        try:
            logging.debug(f"Transcribing chunk: {chunk_duration:.2f}s")
            segments, _ = self.whisper_model.transcribe(audio_chunk, beam_size=5)
            text = "".join(segment.text for segment in segments)

            if text.strip():
                logging.info(f"Transcribed: \"{text.strip()}\"")
                if self.on_transcript:
                    self.on_transcript(text.strip() + " ")
            else:
                logging.debug("No speech detected in chunk")

        except Exception as e:
            error_msg = f"Transcription error: {e}"
            logging.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)

    def __del__(self):
        """Cleanup when object is destroyed."""
        # Note: Async cleanup should be handled by caller
        # This method runs in sync context during GC
        pass
