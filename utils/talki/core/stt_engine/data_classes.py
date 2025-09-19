import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class EnginePreset:
    """Engine preset configuration."""
    type: str = "whisper"  # whisper, vosk, etc.
    model: str = "tiny.en"
    device: str = "cpu"
    compute_json: Dict[str, Any] = field(default_factory=lambda: {"compute_type": "int8"})
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "model": self.model,
            "device": self.device,
            "compute_json": self.compute_json,
            "enabled": self.enabled
        }


@dataclass
class PreprocessPreset:
    """Preprocessing preset configuration."""
    resample_hz: int = 16000
    vad_json: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "aggressiveness": 3,
        "frame_duration_ms": 30
    })
    denoise_json: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "method": "spectral_subtraction"
    })
    normalize_json: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "method": "peak",
        "target_level_db": -20.0
    })
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resample_hz": self.resample_hz,
            "vad_json": self.vad_json,
            "denoise_json": self.denoise_json,
            "normalize_json": self.normalize_json,
            "enabled": self.enabled
        }


@dataclass
class StreamingPreset:
    """Streaming preset configuration."""
    format: str = "pcm16"  # pcm16, opus, etc.
    frame_ms: int = 100
    partial_results: bool = True
    endpointing_json: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "silence_threshold_ms": 1000,
        "timeout_ms": 5000
    })
    max_session_minutes: int = 60
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "format": self.format,
            "frame_ms": self.frame_ms,
            "partial_results": self.partial_results,
            "endpointing_json": self.endpointing_json,
            "max_session_minutes": self.max_session_minutes,
            "enabled": self.enabled
        }


@dataclass
class FeaturePreset:
    """Feature enhancement preset configuration."""
    language_detection: bool = True
    diarization_json: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "method": "pyannote",
        "num_speakers": None
    })
    timestamps: bool = False
    punctuation: bool = True
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "language_detection": self.language_detection,
            "diarization_json": self.diarization_json,
            "timestamps": self.timestamps,
            "punctuation": self.punctuation,
            "enabled": self.enabled
        }


@dataclass
class PostprocessPreset:
    """Postprocessing preset configuration."""
    remove_fillers: bool = True
    capitalize_sentences: bool = True
    custom_rules_json: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "rules": []
    })
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "remove_fillers": self.remove_fillers,
            "capitalize_sentences": self.capitalize_sentences,
            "custom_rules_json": self.custom_rules_json,
            "enabled": self.enabled
        }


@dataclass
class STTConfig:
    """Complete STT Configuration with all presets."""
    name: str = "default-speech"
    version: str = "1.0.0"

    # Preset configurations
    engine_preset: EnginePreset = field(default_factory=EnginePreset)
    preprocess_preset: PreprocessPreset = field(default_factory=PreprocessPreset)
    streaming_preset: StreamingPreset = field(default_factory=StreamingPreset)
    feature_preset: FeaturePreset = field(default_factory=FeaturePreset)
    postprocess_preset: PostprocessPreset = field(default_factory=PostprocessPreset)

    # Global settings
    enabled: bool = True
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'STTConfig':
        """Create config from dictionary with nested presets."""
        config = cls()
        for key, value in config_dict.items():
            if key in cls.__dataclass_fields__:
                if key.endswith('_preset') and isinstance(value, dict):
                    # Handle nested presets
                    preset_class = {
                        'engine_preset': EnginePreset,
                        'preprocess_preset': PreprocessPreset,
                        'streaming_preset': StreamingPreset,
                        'feature_preset': FeaturePreset,
                        'postprocess_preset': PostprocessPreset
                    }.get(key)

                    if preset_class:
                        setattr(config, key, preset_class(**value))
                else:
                    setattr(config, key, value)
        return config

    @classmethod
    def from_json(cls, json_path: str) -> 'STTConfig':
        """Load config from JSON file."""
        with open(json_path, 'r') as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with nested presets."""
        result = {}
        for key in self.__dataclass_fields__:
            value = getattr(self, key)
            if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def save_config(self, json_path: str):
        """Save current configuration to JSON file."""
        with open(json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def create_pipeline_snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of the current pipeline configuration."""
        return {
            "configuration_name": self.name,
            "version": self.version,
            "snapshot_created_at": datetime.now().isoformat(),
            "pipeline": self.to_dict()
        }
