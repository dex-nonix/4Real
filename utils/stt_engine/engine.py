import asyncio
from logging import getLogger
import os
import tempfile

import numpy as np
from faster_whisper import WhisperModel

from .audio_sources.audio_source import AudioSource


class AsyncSTTEngine:
    """
    Standalone Asynchronous Speech-to-Text Engine.
    This engine is now agnostic to the audio input source.
    """

    def __init__(self, audio_source: AudioSource = None, model_size="tiny.en", device="cuda", compute_type="int8",
                 on_transcript=None, on_error=None, on_status=None, processing_mode: str = "live",
                 buffer_limit_mb: float = float('inf'), language=None):
        self.audio_source = audio_source
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.on_transcript = on_transcript or (lambda text: None)
        self.on_error = on_error or (lambda msg: None)
        self.on_status = on_status or (lambda msg: None)
        self.is_initialized = False
        self.whisper_model = None
        self.processing_task = None
        self.loop = asyncio.get_event_loop()
        self.processing_mode = processing_mode
        self.buffer_limit_bytes = float('inf') if buffer_limit_mb == float('inf') else int(buffer_limit_mb * 1024 * 1024)
        self._temp_file_path = None
        logger.info("🎤 Async STT Engine initialized and ready")

    def set_audio_source(self, audio_source: AudioSource):
        """Set the audio source for the engine."""
        self.audio_source = audio_source
        logger.info("🎤 Audio source updated")

    def set_language(self, language):
        """Set the transcription language."""
        self.language = language
        if language == "en":
            new_model = "tiny.en"
        else:
            new_model = "tiny"
        if self.model_size != new_model:
            self.model_size = new_model
            self.is_initialized = False  # Force reload on next transcription
            logger.info(f"🌐 Model changed to {new_model} for language {language}, will reload on next transcription")
        logger.info(f"🌐 Language set to: {language}")

    def configure_processing(self, processing_mode: str = "live", buffer_limit_mb: float = float('inf')):
        self.processing_mode = processing_mode
        self.buffer_limit_bytes = float('inf') if buffer_limit_mb == float('inf') else int(buffer_limit_mb * 1024 * 1024)

    async def initialize_model(self):
        """Asynchronously loads the Whisper model in a background thread."""
        if self.is_initialized:
            return

        logger.info(f"🎯 Initializing Async STT Engine with model: {self.model_size}")
        try:
            self.whisper_model = await asyncio.to_thread(
                WhisperModel, self.model_size, device=self.device, compute_type=self.compute_type
            )
            self.is_initialized = True
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            self.on_error(f"Failed to load Whisper model: {e}")
            raise

    async def start_transcription(self):
        """Starts the transcription process."""
        if self.audio_source is None:
            raise ValueError("Audio source not set. Call set_audio_source() first.")

        await self.initialize_model()

        await self.audio_source.start()

        self.processing_task = self.loop.create_task(self._process_audio())
        logger.info("✅ Transcription engine started.")
        self.on_status("Transcription started")

    async def stop_transcription(self):
        """Stops the transcription process."""
        logger.info("⏹️ Stopping transcription engine...")

        if self.audio_source:
            await self.audio_source.stop()

        if self.processing_task:
            try:
                await asyncio.wait_for(self.processing_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout waiting for processing task. Forcing cancellation.")
                self.processing_task.cancel()

        if self._temp_file_path and os.path.exists(self._temp_file_path):
            try:
                os.unlink(self._temp_file_path)
            except Exception:
                pass

        logger.info("✅ Transcription engine stopped.")
        self.on_status("Transcription stopped")

    def is_task_running(self):
        """Checks if the processing task is still running."""
        return self.processing_task is not None and not self.processing_task.done()

    async def _transcribe_chunk(self, audio_chunk: np.ndarray):
        """Transcribes an audio chunk using Whisper in a non-blocking way."""
        if not self.is_initialized:
            await self.initialize_model()
        target_samplerate = 16000
        chunk_duration = len(audio_chunk) / target_samplerate
        logger.debug(f"🔊 Processing chunk: {chunk_duration:.2f}s duration")

        if len(audio_chunk) < target_samplerate * 0.2:
            logger.debug(f"🗑️ Chunk too small ({chunk_duration:.2f}s), skipping")
            return

        segments, _ = await asyncio.to_thread(self.whisper_model.transcribe, audio_chunk, beam_size=5, language=self.language)
        text = "".join(s.text for s in segments)

        if text.strip():
            logger.info(f"📝 Transcribed: \"{text.strip()}\"")
            self.on_transcript(text.strip() + " ")

    async def _process_audio(self):
        logger.info("🧵 Audio processing task started")
        try:
            if self.processing_mode == "live":
                await self._process_live_mode()
            else:
                await self._process_buffered_mode()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"❌ Error in audio processing task: {e}")
            self.on_error(f"Processing error: {e}")
        logger.info("🧵 Audio processing task finished.")

    async def _process_live_mode(self):
        audio_buffer = np.array([], dtype=np.float32)
        processing_interval_samples = int(16000 * 2.0)
        while True:
            audio_chunk = await self.audio_source.read()
            if audio_chunk is None:
                break
            audio_buffer = np.concatenate([audio_buffer, audio_chunk.flatten()])
            if len(audio_buffer) >= processing_interval_samples:
                await self._transcribe_chunk(audio_buffer)
                audio_buffer = np.array([], dtype=np.float32)
        if len(audio_buffer) > 0:
            await self._transcribe_chunk(audio_buffer)

    async def _process_buffered_mode(self):
        current_bytes = 0
        in_memory = []
        spilled = False
        while True:
            audio_chunk = await self.audio_source.read()
            if audio_chunk is None:
                break
            flat = audio_chunk.flatten().astype(np.float32)
            in_memory.append(flat)
            current_bytes += int(flat.size * 4)
            if self.buffer_limit_bytes != float('inf') and current_bytes > self.buffer_limit_bytes:
                await self._spill_to_disk(in_memory)
                in_memory = []
                current_bytes = 0
                spilled = True
        if spilled:
            disk_audio = await self._load_spilled_audio()
            if in_memory:
                mem_audio = np.concatenate(in_memory)
                if disk_audio.size > 0:
                    complete_audio = np.concatenate([disk_audio, mem_audio])
                else:
                    complete_audio = mem_audio
            else:
                complete_audio = disk_audio
            if complete_audio.size > 0:
                await self._transcribe_chunk(complete_audio)
        else:
            if in_memory:
                complete_audio = np.concatenate(in_memory)
                await self._transcribe_chunk(complete_audio)

    async def _spill_to_disk(self, buffer_list):
        if not self._temp_file_path:
            fd, path = tempfile.mkstemp(suffix='.f32')
            os.close(fd)
            self._temp_file_path = path
        if buffer_list:
            data = np.concatenate(buffer_list).astype(np.float32)
            with open(self._temp_file_path, 'ab') as f:
                data.tofile(f)

    async def _load_spilled_audio(self):
        if not self._temp_file_path or not os.path.exists(self._temp_file_path):
            return np.array([], dtype=np.float32)
        with open(self._temp_file_path, 'rb') as f:
            data = np.fromfile(f, dtype=np.float32)
        try:
            os.unlink(self._temp_file_path)
        except Exception:
            pass
        self._temp_file_path = None
        return data


logger = getLogger(AsyncSTTEngine.__name__)
