import asyncio
from typing import Union, Dict, Any, Optional, Callable

import numpy as np
from faster_whisper import WhisperModel

from talki.core.stt_engine.audio_processor import AudioPreprocessor
from talki.core.stt_engine.data_classes import STTConfig
from talki.core.stt_engine.feature_processor import FeatureProcessor
from talki.core.stt_engine.post_processor import Postprocessor
from talki.core.stt_engine.streaming_manager import StreamingManager


class STTEngine:
    """
    FULL IMPLEMENTATION: Complete STT Engine with all processing pipeline stages.

    Features all presets from TO_implement.md:
    - Engine preset (Whisper, etc.)
    - Preprocess preset (VAD, denoise, normalize, resample)
    - Streaming preset (partials, endpointing, session management)
    - Feature preset (timestamps, diarization, punctuation)
    - Postprocess preset (fillers, capitalization, custom rules)
    """

    def __init__(self, config: Union[STTConfig, Dict[str, Any], str]):
        """
        Initialize the complete STT Engine.

        Args:
            config: STTConfig object, config dict, or path to JSON config file
        """
        if isinstance(config, str):
            self.config = STTConfig.from_json(config)
        elif isinstance(config, dict):
            self.config = STTConfig.from_dict(config)
        else:
            self.config = config

        # Initialize pipeline components
        self.preprocessor = AudioPreprocessor(self.config.preprocess_preset)
        self.feature_processor = FeatureProcessor(self.config.feature_preset)
        self.postprocessor = Postprocessor(self.config.postprocess_preset)
        self.streaming_manager = StreamingManager(self.config.streaming_preset)

        # Engine (Whisper)
        self.model: Optional[WhisperModel] = None

        # Callbacks
        self.on_transcript: Optional[Callable[[str], None]] = None
        self.on_partial: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_endpoint: Optional[Callable[[], None]] = None

        # Session state
        self.session_active = False
        self.pipeline_snapshot = None

        # Initialize
        self._load_model()
        self._create_pipeline_snapshot()

    def _load_model(self):
        """Load the speech recognition model."""
        if not self.config.engine_preset.enabled:
            return

        try:
            if self.config.engine_preset.type == "whisper":
                self.model = WhisperModel(
                    model_size_or_path=self.config.engine_preset.model,
                    device=self.config.engine_preset.device,
                    **self.config.engine_preset.compute_json
                )
        except Exception as e:
            if self.on_error:
                self.on_error(f"Failed to load {self.config.engine_preset.type} model: {e}")
            raise

    def _create_pipeline_snapshot(self):
        """Create a snapshot of the current pipeline configuration."""
        self.pipeline_snapshot = self.config.create_pipeline_snapshot()

    def get_pipeline_snapshot(self) -> Dict[str, Any]:
        """Get the current pipeline snapshot."""
        return self.pipeline_snapshot

    def is_loaded(self) -> bool:
        """Check if the engine is loaded and ready."""
        return (self.model is not None and
                self.config.engine_preset.enabled and
                self.config.enabled)

    def start_session(self):
        """Start a new streaming session."""
        if not self.is_loaded():
            raise RuntimeError("Engine not loaded")

        self.session_active = True
        self.streaming_manager.start_session()

    def end_session(self):
        """End the current streaming session."""
        self.session_active = False
        self.streaming_manager.clear_partial()

    def process_audio_chunk(self, audio_chunk: np.ndarray, source_sample_rate: int) -> Optional[str]:
        """
        Process a chunk of audio through the complete pipeline.

        Args:
            audio_chunk: Raw audio data
            source_sample_rate: Sample rate of input audio

        Returns:
            Processed transcript text or None
        """
        if not self.session_active or not self.is_loaded():
            return None

        try:
            # 1. PREPROCESSING PIPELINE
            processed_audio, has_speech = self.preprocessor.process(
                audio_chunk, source_sample_rate
            )

            if not has_speech or len(processed_audio) == 0:
                # Check for endpointing
                if self.streaming_manager.should_endpoint(has_speech=False):
                    if self.on_endpoint:
                        self.on_endpoint()
                return None

            # 2. ENGINE TRANSCRIPTION

            segments, info = self.model.transcribe(
                processed_audio,
                language=None if self.config.feature_preset.language_detection else "en"
            )

            segments_list = list(segments)

            # Convert segments to list of dicts
            segment_dicts = []
            for segment in segments_list:
                segment_dicts.append({
                    'text': segment.text,
                    'start': segment.start,
                    'end': segment.end,
                    'confidence': segment.avg_logprob if hasattr(segment, 'avg_logprob') else 0
                })

            # 3. FEATURE PROCESSING
            segment_dicts = self.feature_processor.process_segments(
                segment_dicts,
                info.language if hasattr(info, 'language') else 'unknown'
            )

            # Combine all segment text
            full_text = ' '.join(segment['text'] for segment in segment_dicts)

            # 4. POSTPROCESSING
            processed_text = self.postprocessor.process(full_text)

            if processed_text:
                # 5. STREAMING MANAGEMENT
                self.streaming_manager.add_to_partial(processed_text)

                # Emit partial results
                if self.on_partial:
                    self.on_partial(self.streaming_manager.get_partial_text())

                # Emit final transcript
                if self.on_transcript:
                    self.on_transcript(processed_text)

                return processed_text

        except Exception as e:
            if self.on_error:
                self.on_error(f"Processing error: {e}")

        return None

    def get_partial_text(self) -> str:
        """Get current partial transcription text."""
        return self.streaming_manager.get_partial_text()

    def clear_partial(self):
        """Clear partial results buffer."""
        self.streaming_manager.clear_partial()

    def should_timeout(self) -> bool:
        """Check if session should timeout."""
        return self.streaming_manager.should_timeout()

    def update_config(self, new_config: Union[STTConfig, Dict[str, Any]]):
        """
        Update configuration (creates new pipeline components).
        Note: This will recreate all processing components.
        """
        if isinstance(new_config, dict):
            self.config = STTConfig.from_dict(new_config)
        else:
            self.config = new_config

        # Recreate pipeline components
        self.preprocessor = AudioPreprocessor(self.config.preprocess_preset)
        self.feature_processor = FeatureProcessor(self.config.feature_preset)
        self.postprocessor = Postprocessor(self.config.postprocess_preset)
        self.streaming_manager = StreamingManager(self.config.streaming_preset)

        # Reload model if engine config changed
        if self.config.engine_preset.enabled:
            self._load_model()

        # Update snapshot
        self._create_pipeline_snapshot()

    def get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return self.config.to_dict()

    def save_config(self, json_path: str):
        """Save current configuration to JSON file."""
        self.config.save_config(json_path)

    async def process_audio_chunk_async(self, audio_chunk: np.ndarray, source_sample_rate: int) -> Optional[str]:
        """
        Async version for backend usage.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return await loop.run_in_executor(None, self.process_audio_chunk, audio_chunk, source_sample_rate)
