from typing import List, Dict, Any

from talki.core.stt_engine.data_classes import FeaturePreset


class FeatureProcessor:
    """Handles feature enhancement: timestamps, diarization, punctuation."""

    def __init__(self, config: FeaturePreset):
        self.config = config

    def add_timestamps(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add timestamps to segments if enabled."""
        if not self.config.timestamps:
            return segments

        # Timestamps are already in whisper segments
        return segments

    def detect_language(self, segments: List[Dict[str, Any]], detected_lang: str) -> List[Dict[str, Any]]:
        """Add language detection info."""
        if not self.config.language_detection:
            return segments

        for segment in segments:
            segment['language'] = detected_lang

        return segments

    def add_punctuation(self, text: str) -> str:
        """Add punctuation to text if enabled."""
        if not self.config.punctuation:
            return text

        # Simple punctuation rules (placeholder for more sophisticated punctuation)
        import re

        # Add periods at end of sentences
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        text = re.sub(r'([a-z])\s*$', r'\1.', text)

        # Add commas in lists
        text = re.sub(r'(\w+)\s+and\s+(\w+)', r'\1, and \2', text)

        return text

    def process_segments(self, segments: List[Dict[str, Any]], detected_lang: str) -> List[Dict[str, Any]]:
        """Process segments with all enabled features."""
        if not self.config.enabled:
            return segments

        # Add timestamps
        segments = self.add_timestamps(segments)

        # Add language detection
        segments = self.detect_language(segments, detected_lang)

        # Add punctuation to text
        for segment in segments:
            if 'text' in segment:
                segment['text'] = self.add_punctuation(segment['text'])

        return segments
