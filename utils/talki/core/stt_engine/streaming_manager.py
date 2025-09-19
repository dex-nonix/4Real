import time

from talki.core.stt_engine.data_classes import StreamingPreset


class StreamingManager:
    """Manages streaming behavior and endpointing."""

    def __init__(self, config: StreamingPreset):
        self.config = config
        self.session_start_time = None
        self.last_audio_time = None
        self.partial_buffer = []

        if self.config.endpointing_json.get("enabled", False):
            self.silence_threshold_ms = self.config.endpointing_json.get("silence_threshold_ms", 1000)
            self.timeout_ms = self.config.endpointing_json.get("timeout_ms", 5000)

    def start_session(self):
        """Start a new streaming session."""
        self.session_start_time = time.time()
        self.last_audio_time = self.session_start_time
        self.partial_buffer = []

    def should_endpoint(self, has_speech: bool) -> bool:
        """Determine if we should endpoint based on silence."""
        if not self.config.endpointing_json.get("enabled", False):
            return False

        current_time = time.time()

        if has_speech:
            self.last_audio_time = current_time
            return False
        else:
            # Check if we've exceeded silence threshold
            silence_duration = (current_time - self.last_audio_time) * 1000
            return silence_duration >= self.silence_threshold_ms

    def should_timeout(self) -> bool:
        """Check if session should timeout."""
        if not self.session_start_time:
            return False

        session_duration_ms = (time.time() - self.session_start_time) * 1000
        max_duration_ms = self.config.max_session_minutes * 60 * 1000

        return session_duration_ms >= max_duration_ms

    def add_to_partial(self, text: str):
        """Add text to partial results buffer."""
        if self.config.partial_results:
            self.partial_buffer.append(text)

    def get_partial_text(self) -> str:
        """Get current partial text."""
        return ' '.join(self.partial_buffer)

    def clear_partial(self):
        """Clear partial results buffer."""
        self.partial_buffer = []
