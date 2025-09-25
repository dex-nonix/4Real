import asyncio
from logging import getLogger

import numpy as np
from faster_whisper import WhisperModel

from .audio_sources.audio_source import AudioSource


class AsyncSTTEngine:
    """
    Standalone Asynchronous Speech-to-Text Engine.
    This engine is now agnostic to the audio input source.
    """

    def __init__(self, audio_source: AudioSource = None, model_size="tiny.en", device="cuda", compute_type="int8",
                 on_transcript=None, on_error=None, on_status=None):
        self.audio_source = audio_source
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.on_transcript = on_transcript or (lambda text: None)
        self.on_error = on_error or (lambda msg: None)
        self.on_status = on_status or (lambda msg: None)
        self.is_initialized = False
        self.whisper_model = None
        self.processing_task = None
        self.loop = asyncio.get_event_loop()
        logger.info("🎤 Async STT Engine initialized and ready")

    def set_audio_source(self, audio_source: AudioSource):
        """Set the audio source for the engine."""
        self.audio_source = audio_source
        logger.info("🎤 Audio source updated")

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

        await self.audio_source.stop()

        if self.processing_task:
            try:
                await asyncio.wait_for(self.processing_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout waiting for processing task. Forcing cancellation.")
                self.processing_task.cancel()

        logger.info("✅ Transcription engine stopped.")
        self.on_status("Transcription stopped")

    def is_task_running(self):
        """Checks if the processing task is still running."""
        return self.processing_task is not None and not self.processing_task.done()

    async def _transcribe_chunk(self, audio_chunk: np.ndarray):
        """Transcribes an audio chunk using Whisper in a non-blocking way."""
        target_samplerate = 16000
        chunk_duration = len(audio_chunk) / target_samplerate
        logger.debug(f"🔊 Processing chunk: {chunk_duration:.2f}s duration")

        if len(audio_chunk) < target_samplerate * 0.2:
            logger.debug(f"🗑️ Chunk too small ({chunk_duration:.2f}s), skipping")
            return

        segments, _ = await asyncio.to_thread(self.whisper_model.transcribe, audio_chunk, beam_size=5)
        text = "".join(s.text for s in segments)

        if text.strip():
            logger.info(f"📝 Transcribed: \"{text.strip()}\"")
            self.on_transcript(text.strip() + " ")

    async def _process_audio(self):
        """Asynchronous audio processing task that reads from the source and transcribes."""
        logger.info("🧵 Audio processing task started")
        audio_buffer = np.array([], dtype=np.float32)
        PROCESSING_INTERVAL_SAMPLES = int(16000 * 2.0)  # Process in 2-second chunks

        while True:
            try:
                audio_chunk = await self.audio_source.read()

                if audio_chunk is None:  # End of stream signal
                    logger.debug("🛑 Received end of stream signal.")
                    break

                # --- THIS IS THE FIX ---
                # Ensure the incoming chunk is flattened to 1D before concatenation,
                # just like in the original working code.
                audio_buffer = np.concatenate([audio_buffer, audio_chunk.flatten()])

                if len(audio_buffer) >= PROCESSING_INTERVAL_SAMPLES:
                    logger.info("🔥 Processing accumulated audio chunk")
                    await self._transcribe_chunk(audio_buffer)
                    audio_buffer = np.array([], dtype=np.float32)

            except asyncio.CancelledError:
                logger.info("Processing task cancelled.")
                break
            except Exception as e:
                logger.error(f"❌ Error in audio processing task: {e}")
                self.on_error(f"Processing error: {e}")
                # Stop processing on error to avoid spamming logs
                break

        # Process any leftover audio
        if len(audio_buffer) > 0:
            logger.info(f"🔚 Processing {len(audio_buffer) / 16000:.2f}s of leftover audio.")
            await self._transcribe_chunk(audio_buffer)

        logger.info("🧵 Audio processing task finished.")


logger = getLogger(AsyncSTTEngine.__name__)
