import numpy as np
import webrtcvad
from scipy import signal

from talki.core.stt_engine.data_classes import PreprocessPreset


class AudioPreprocessor:
    """Handles all audio preprocessing: VAD, denoise, normalize, resample."""

    def __init__(self, config: PreprocessPreset):
        self.config = config
        self.vad = None

        if self.config.vad_json.get("enabled", False):
            self.vad = webrtcvad.Vad(self.config.vad_json.get("aggressiveness", 3))
            self.frame_duration_ms = self.config.vad_json.get("frame_duration_ms", 30)

    def resample_audio(self, audio: np.ndarray, source_rate: int) -> np.ndarray:
        """Resample audio to target rate."""
        if source_rate == self.config.resample_hz:
            return audio

        # Calculate resampling ratio
        ratio = self.config.resample_hz / source_rate

        # Resample using scipy
        resampled = signal.resample(audio, int(len(audio) * ratio))
        return resampled.astype(np.float32)

    def apply_vad(self, audio: np.ndarray, sample_rate: int) -> tuple[np.ndarray, bool]:
        """Apply Voice Activity Detection."""
        if not self.vad:
            return audio, True

        # Convert to 16-bit PCM for VAD
        if audio.dtype != np.int16:
            audio_int16 = (audio * 32767).astype(np.int16)
        else:
            audio_int16 = audio

        # Process in frames
        frame_size = int(sample_rate * self.frame_duration_ms / 1000)
        has_speech = False

        filtered_audio = []
        for i in range(0, len(audio_int16) - frame_size + 1, frame_size):
            frame = audio_int16[i:i + frame_size]
            if len(frame) == frame_size:
                if self.vad.is_speech(frame.tobytes(), sample_rate):
                    filtered_audio.extend(frame)
                    has_speech = True

        if not filtered_audio:
            return np.array([], dtype=np.float32), False

        return np.array(filtered_audio, dtype=np.float32) / 32767.0, has_speech

    def denoise_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply denoising if enabled."""
        if not self.config.denoise_json.get("enabled", False):
            return audio

        method = self.config.denoise_json.get("method", "spectral_subtraction")

        if method == "spectral_subtraction":
            # Simple spectral subtraction (placeholder for more sophisticated denoising)
            # In a real implementation, you'd use libraries like noisereduce
            return audio * 0.9  # Placeholder

        return audio

    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply audio normalization."""
        if not self.config.normalize_json.get("enabled", True):
            return audio

        method = self.config.normalize_json.get("method", "peak")
        target_level_db = self.config.normalize_json.get("target_level_db", -20.0)

        if method == "peak":
            # Peak normalization
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                scale_factor = 10 ** (target_level_db / 20.0) / max_val
                return audio * scale_factor

        return audio

    def process(self, audio: np.ndarray, source_rate: int) -> tuple[np.ndarray, bool]:
        """
        Apply full preprocessing pipeline.

        Returns:
            tuple: (processed_audio, has_speech)
        """
        if not self.config.enabled:
            return audio, True

        print(f"DEBUG: Original audio - shape: {audio.shape}, dtype: {audio.dtype}, min: {audio.min():.6f}, max: {audio.max():.6f}")

        # 1. Resample
        processed = self.resample_audio(audio, source_rate)
        print(f"DEBUG: After resample - shape: {processed.shape}, dtype: {processed.dtype}, min: {processed.min():.6f}, max: {processed.max():.6f}")

        # 2. VAD
        processed, has_speech = self.apply_vad(processed, self.config.resample_hz)
        print(f"DEBUG: After VAD - has_speech: {has_speech}, shape: {processed.shape}")

        if not has_speech or len(processed) == 0:
            return np.array([], dtype=np.float32), False

        # 3. Denoise
        processed = self.denoise_audio(processed)

        # 4. Normalize
        processed = self.normalize_audio(processed)
        print(f"DEBUG: After normalize - shape: {processed.shape}, min: {processed.min():.6f}, max: {processed.max():.6f}")

        return processed, True
