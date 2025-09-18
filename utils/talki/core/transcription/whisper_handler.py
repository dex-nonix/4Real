"""
Whisper model wrapper for speech-to-text transcription.
"""

import numpy as np
from faster_whisper import WhisperModel
from talki.config.logging_config import logger
from talki.utils.constants import DEFAULT_MODEL_SIZE, MIN_CHUNK_DURATION, TARGET_SAMPLE_RATE


class WhisperTranscriber:
    """
    Handles Whisper model operations for speech-to-text transcription.
    """

    def __init__(self, model_size: str = DEFAULT_MODEL_SIZE, device: str = "cpu",
                 compute_type: str = "int8"):
        """
        Initialize the Whisper transcriber.

        Args:
            model_size: Size of the Whisper model to use
            device: Device to run model on ('cpu' or 'cuda')
            compute_type: Compute type for optimization
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

        self._load_model()

    def _load_model(self):
        """Load the Whisper model."""
        try:
            logger.debug("🔄 Loading Whisper model...")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def transcribe_chunk(self, audio_chunk: np.ndarray, beam_size: int = 5) -> str:
        """
        Transcribe an audio chunk to text.

        Args:
            audio_chunk: Audio data as numpy array (float32, sample_rate=16000)
            beam_size: Beam size for transcription

        Returns:
            Transcribed text or empty string if no speech detected
        """
        chunk_duration = len(audio_chunk) / TARGET_SAMPLE_RATE
        logger.debug(f"🔊 Processing chunk: {chunk_duration:.2f}s duration")

        # Skip chunks that are too small
        if chunk_duration < MIN_CHUNK_DURATION:
            logger.debug(f"🗑️  Chunk too small ({chunk_duration:.2f}s), skipping")
            return ""

        try:
            logger.debug("🎯 Starting transcription...")
            segments, _ = self.model.transcribe(audio_chunk, beam_size=beam_size)
            text = "".join(segment.text for segment in segments)

            if text.strip():
                logger.info(f"📝 Transcribed: \"{text.strip()}\"")
                return text.strip() + " "
            else:
                logger.debug("🤫 No speech detected in chunk")
                return ""

        except Exception as e:
            logger.error(f"❌ Error during transcription: {e}")
            return ""

    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self.model is not None
