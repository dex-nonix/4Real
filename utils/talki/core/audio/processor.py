"""
Audio recording and processing with real-time transcription.
"""

import threading
import queue
import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QObject, pyqtSignal
from talki.config.logging_config import logger
from talki.core.stt_engine import STTEngine
from talki.utils.constants import (
    TARGET_SAMPLE_RATE, PROCESSING_INTERVAL_SECONDS,
    AUDIO_QUEUE_TIMEOUT, DEFAULT_MODEL_SIZE
)


class AudioProcessor(QObject):
    """
    Handles audio recording, processing, and real-time transcription.

    This version uses a time-based chunking method for live transcription feel.
    """

    # Signals for UI communication
    transcript_update = pyqtSignal(str)  # Emitted when new transcript is available
    error_signal = pyqtSignal(str)       # Emitted on processing errors
    recording_state_changed = pyqtSignal(bool)  # Emitted when recording state changes

    def __init__(self, stt_engine: STTEngine):
        """
        Initialize the audio processor.

        Args:
            stt_engine: STT engine instance to use for transcription
        """
        super().__init__()

        # Audio configuration
        self.target_sample_rate = TARGET_SAMPLE_RATE
        self.processing_interval_samples = int(TARGET_SAMPLE_RATE * PROCESSING_INTERVAL_SECONDS)

        # Recording state
        self.is_recording = False
        self.native_sample_rate = None

        # Audio components
        self.stream = None
        self.audio_queue = queue.Queue()
        self.processing_thread = None

        # STT Engine
        self.stt_engine = stt_engine

        logger.info("🎤 AudioProcessor initialized and ready")

    def start_recording(self, device_index: int):
        """
        Start recording from the specified audio device.

        Args:
            device_index: Index of the audio device to use
        """
        if self.is_recording:
            logger.warning("⚠️  Recording already in progress, ignoring start request")
            return

        if not self.stt_engine:
            error_msg = "STT engine not available"
            logger.error(f"❌ {error_msg}")
            self.error_signal.emit(error_msg)
            return

        if not self.stt_engine.is_loaded():
            error_msg = "STT engine not loaded"
            logger.error(f"❌ {error_msg}")
            self.error_signal.emit(error_msg)
            return

        logger.info(f"🎤 Starting recording on device {device_index}")

        try:
            # Query device information
            logger.debug("🔍 Querying audio device information...")
            device_info = sd.query_devices(device_index, 'input')
            self.native_sample_rate = int(device_info['default_samplerate'])
            logger.info(f"📊 Device sample rate: {self.native_sample_rate}Hz")

            # Start recording
            self.is_recording = True
            self.recording_state_changed.emit(True)

            # Create audio input stream
            logger.debug("🔄 Creating audio input stream...")
            self.stream = sd.InputStream(
                samplerate=self.native_sample_rate,
                channels=1,
                device=device_index,
                dtype="float32",
                callback=self._audio_callback
            )

            # Start the stream and processing thread
            logger.debug("▶️  Starting audio stream...")
            self.stream.start()

            logger.debug("🧵 Starting processing thread...")
            self.processing_thread = threading.Thread(target=self._process_audio)
            self.processing_thread.start()

            logger.info("✅ Recording started successfully")

        except Exception as e:
            logger.error(f"❌ Error starting audio stream: {e}")
            self.error_signal.emit(f"Error starting audio stream: {e}")
            self.is_recording = False
            self.recording_state_changed.emit(False)

    def stop_recording(self):
        """Stop the current recording session."""
        if not self.is_recording:
            logger.debug("🔇 Recording not active, ignoring stop request")
            return

        logger.info("⏹️  Stopping recording...")
        self.is_recording = False
        self.recording_state_changed.emit(False)

        # Signal processing thread to stop
        logger.debug("📤 Sending stop signal to processing thread...")
        self.audio_queue.put(None)  # Sentinel value

        # Stop and close audio stream
        if self.stream:
            logger.debug("🔄 Stopping and closing audio stream...")
            self.stream.stop(ignore_errors=True)
            self.stream.close(ignore_errors=True)
            self.stream = None

        logger.info("✅ Recording stopped")

    def is_thread_alive(self) -> bool:
        """Check if the processing thread is still alive."""
        return self.processing_thread is not None and self.processing_thread.is_alive()

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback function for audio stream input.

        Args:
            indata: Audio data buffer
            frames: Number of frames in buffer
            time_info: Timing information
            status: Stream status
        """
        if status:
            logger.warning(f"⚠️  Audio callback status: {status}")
            self.error_signal.emit(str(status))

        logger.debug(f"📡 Audio chunk received: {frames} frames")
        self.audio_queue.put(indata.copy())

    def _resample_audio(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Resample audio chunk to target sample rate if needed.

        Args:
            audio_chunk: Input audio chunk

        Returns:
            Resampled audio chunk
        """
        if self.native_sample_rate == self.target_sample_rate:
            return audio_chunk

        num_samples = audio_chunk.shape[0]
        resampled_num_samples = int(num_samples * self.target_sample_rate / self.native_sample_rate)
        original_indices = np.arange(num_samples)
        resampled_indices = np.linspace(0, num_samples - 1, resampled_num_samples)

        return np.interp(resampled_indices, original_indices, audio_chunk.flatten()).astype(np.float32)

    def _process_audio(self):
        """Main audio processing thread function."""
        logger.info("🧵 Audio processing thread started")

        audio_buffer = np.array([], dtype=np.float32)
        logger.debug(f"⚙️  Processing interval: {self.processing_interval_samples} samples ({PROCESSING_INTERVAL_SECONDS}s)")

        while self.is_recording:
            try:
                # Get audio chunk from queue
                raw_chunk = self.audio_queue.get(timeout=AUDIO_QUEUE_TIMEOUT)

                if raw_chunk is None:
                    # Stop signal received
                    logger.debug("🛑 Received stop signal, exiting processing loop")
                    break

                # Process the audio chunk
                logger.debug("🔄 Processing raw audio chunk...")
                resampled_chunk = self._resample_audio(raw_chunk)
                audio_buffer = np.concatenate([audio_buffer, resampled_chunk])

                buffer_duration = len(audio_buffer) / self.target_sample_rate
                logger.debug(f"🔄 Audio buffer size: {buffer_duration:.2f}s")

                # Process chunks every 2 seconds
                if len(audio_buffer) >= self.processing_interval_samples:
                    logger.info("🔥 Processing audio chunk (2s interval)")
                    self._process_audio_chunk(audio_buffer)
                    audio_buffer = np.array([], dtype=np.float32)  # Clear buffer
                    logger.debug("🧹 Audio buffer cleared")

            except queue.Empty:
                continue

            except Exception as e:
                logger.error(f"❌ Error in audio processing thread: {e}")
                self.error_signal.emit(f"Audio processing error: {e}")
                break

        # Process any remaining audio in buffer
        if len(audio_buffer) > 0:
            leftover_duration = len(audio_buffer) / self.target_sample_rate
            logger.info(f"🔚 Processing leftover audio: {leftover_duration:.2f}s")
            self._process_audio_chunk(audio_buffer)

        logger.info("🧵 Audio processing thread finished")

    def _process_audio_chunk(self, audio_chunk: np.ndarray):
        """
        Process a chunk of audio data through the STT engine.

        Args:
            audio_chunk: Audio data to transcribe
        """
        try:
            # Check if STT engine is available
            if not self.stt_engine:
                logger.error("❌ STT engine not available during processing")
                return

            # Start session if not already started
            if not self.stt_engine.session_active:
                self.stt_engine.start_session()

            text = self.stt_engine.process_audio_chunk(audio_chunk, self.native_sample_rate)
            if text:
                self.transcript_update.emit(text)
        except Exception as e:
            logger.error(f"❌ Error processing audio chunk: {e}")
            self.error_signal.emit(f"Transcription error: {e}")

    def update_stt_engine(self, new_engine: STTEngine):
        """
        Update the STT engine (used when switching configurations).

        Args:
            new_engine: New STT engine instance
        """
        logger.info("🔄 Updating STT engine in AudioProcessor")

        # Stop current session if active
        if self.stt_engine and self.stt_engine.session_active:
            self.stt_engine.end_session()

        # Update to new engine
        self.stt_engine = new_engine

        logger.info("✅ STT engine updated successfully")
