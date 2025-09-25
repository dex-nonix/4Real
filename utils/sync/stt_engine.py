import sys
import threading
import queue
import numpy as np
import sounddevice as sd
import logging
import colorama
from faster_whisper import WhisperModel

# Initialize colorama for colored console output
colorama.init()

# Configure logging with custom formatter
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            record.levelname = f"ℹ️  {record.levelname}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"⚠️  {record.levelname}"
        elif record.levelno == logging.ERROR:
            record.levelname = f"❌ {record.levelname}"
        elif record.levelno == logging.DEBUG:
            record.levelname = f"🔍 {record.levelname}"
        return super().format(record)

# Set up logger
logger = logging.getLogger('STTLogger')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class STTEngine:
    """
    Standalone Speech-to-Text Engine
    Independent of Qt, uses callback functions for communication
    """

    def __init__(self, model_size="tiny.en", on_transcript=None, on_error=None, on_status=None):
        """
        Initialize STT Engine

        Args:
            model_size: Whisper model size ("tiny.en", "base.en", etc.)
            on_transcript: Callback function called with transcribed text
            on_error: Callback function called with error messages
            on_status: Callback function called with status updates
        """
        self.on_transcript = on_transcript or (lambda text: None)
        self.on_error = on_error or (lambda msg: None)
        self.on_status = on_status or (lambda msg: None)

        logger.info(f"🎯 Initializing STT Engine with model: {model_size}")
        try:
            logger.debug("🔄 Loading Whisper model...")
            self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            self.on_error(f"Failed to load Whisper model: {e}")
            return

        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None
        self.native_samplerate = None
        self.target_samplerate = 16000
        self.processing_thread = None
        logger.info("🎤 STT Engine initialized and ready")

    def start_recording(self, device_index):
        """
        Start audio recording and transcription

        Args:
            device_index: Audio device index to use
        """
        if self.is_recording:
            logger.warning("⚠️  Recording already in progress, ignoring start request")
            return

        logger.info(f"🎤 Starting recording on device {device_index}")
        try:
            logger.debug("🔍 Querying audio device information...")
            device_info = sd.query_devices(device_index, 'input')
            self.native_samplerate = int(device_info['default_samplerate'])
            logger.info(f"📊 Device info: {device_info['name']} (index {device_index}), rate: {self.native_samplerate}Hz")

            self.is_recording = True
            logger.debug("🔄 Creating audio input stream...")
            self.stream = sd.InputStream(
                samplerate=self.native_samplerate, channels=1, device=device_index,
                dtype="float32", callback=self._audio_callback
            )

            logger.debug("▶️  Starting audio stream...")
            self.stream.start()
            logger.debug("🧵 Starting processing thread...")
            self.processing_thread = threading.Thread(target=self._process_audio)
            self.processing_thread.start()

            logger.info("✅ Recording started successfully")
            self.on_status("Recording started")

        except Exception as e:
            logger.error(f"❌ Error starting audio stream: {e}")
            self.on_error(f"Error starting audio stream: {e}")
            self.is_recording = False

    def stop_recording(self):
        """
        Stop audio recording and transcription
        """
        if not self.is_recording:
            logger.debug("🔇 Recording not active, ignoring stop request")
            return

        logger.info("⏹️  Stopping recording...")
        self.is_recording = False

        logger.debug("📤 Sending stop signal to processing thread...")
        self.audio_queue.put(None)  # Sentinel to unblock the thread

        if self.stream:
            logger.debug("🔄 Stopping and closing audio stream...")
            self.stream.stop(ignore_errors=True)
            self.stream.close(ignore_errors=True)
            self.stream = None

        # Clear the queue to prevent stale audio in next recording
        try:
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
        except Exception as e:
            logger.warning(f"⚠️  Error clearing audio queue: {e}")

        logger.info("✅ Recording stopped")
        self.on_status("Recording stopped")

    def is_thread_alive(self):
        """
        Check if processing thread is still alive

        Returns:
            bool: True if thread is alive
        """
        return self.processing_thread is not None and self.processing_thread.is_alive()

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Audio stream callback - called by sounddevice when audio data is available
        """
        if status:
            logger.warning(f"⚠️  Audio callback status: {status}")
            self.on_error(str(status))

        logger.debug(f"📡 Audio chunk received: {frames} frames")
        self.audio_queue.put(indata.copy())

    def _resample(self, audio_chunk):
        """
        Resample audio chunk to target sample rate if needed
        """
        if self.native_samplerate == self.target_samplerate:
            return audio_chunk
        num_samples = audio_chunk.shape[0]
        resampled_num_samples = int(num_samples * self.target_samplerate / self.native_samplerate)
        original_indices = np.arange(num_samples)
        resampled_indices = np.linspace(0, num_samples - 1, resampled_num_samples)
        return np.interp(resampled_indices, original_indices, audio_chunk.flatten()).astype(np.float32)

    def _transcribe_chunk(self, audio_chunk):
        """
        Transcribe an audio chunk using Whisper
        """
        chunk_duration = len(audio_chunk) / self.target_samplerate
        logger.debug(f"🔊 Processing chunk: {chunk_duration:.2f}s duration")

        if len(audio_chunk) < self.target_samplerate * 0.2:
            logger.debug(f"🗑️  Chunk too small ({chunk_duration:.2f}s), skipping")
            return  # Ignore tiny fragments

        logger.debug("🎯 Starting transcription...")
        segments, _ = self.whisper_model.transcribe(audio_chunk, beam_size=5)
        text = "".join(s.text for s in segments)

        if text.strip():
            logger.info(f"📝 Transcribed: \"{text.strip()}\"")
            self.on_transcript(text.strip() + " ")
        else:
            logger.debug("🤫 No speech detected in chunk")

    def _process_audio(self):
        """
        Audio processing thread - runs in background to process audio queue
        """
        logger.info("🧵 Audio processing thread started")
        audio_buffer = np.array([], dtype=np.float32)
        PROCESSING_INTERVAL_SAMPLES = int(self.target_samplerate * 2.0)
        logger.debug(f"⚙️  Processing interval: {PROCESSING_INTERVAL_SAMPLES} samples (2.0s)")

        while self.is_recording:
            try:
                raw_chunk = self.audio_queue.get(timeout=0.1)
                if raw_chunk is None:
                    logger.debug("🛑 Received stop signal, exiting processing loop")
                    break

                logger.debug("🔄 Processing raw audio chunk...")
                resampled_chunk = self._resample(raw_chunk)
                audio_buffer = np.concatenate([audio_buffer, resampled_chunk])

                buffer_duration = len(audio_buffer) / self.target_samplerate
                logger.debug(f"🔄 Audio buffer size: {buffer_duration:.2f}s")

                # Process every 2 seconds of audio for a live feel
                if len(audio_buffer) >= PROCESSING_INTERVAL_SAMPLES:
                    logger.info("🔥 Processing audio chunk (2s interval)")
                    self._transcribe_chunk(audio_buffer)
                    audio_buffer = np.array([], dtype=np.float32)  # Clear buffer
                    logger.debug("🧹 Audio buffer cleared")

            except queue.Empty:
                continue

        # After loop ends, process any leftover audio in the buffer
        if len(audio_buffer) > 0:
            leftover_duration = len(audio_buffer) / self.target_samplerate
            logger.info(f"🔚 Processing leftover audio: {leftover_duration:.2f}s")
            self._transcribe_chunk(audio_buffer)

        logger.info("🧵 Audio processing thread finished")
