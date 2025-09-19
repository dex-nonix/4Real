from talki.core.stt_engine.data_classes import PostprocessPreset


class Postprocessor:
    """Handles text postprocessing: fillers, capitalization, custom rules."""

    def __init__(self, config: PostprocessPreset):
        self.config = config
        self.filler_words = {'um', 'uh', 'like', 'you know', 'so', 'well', 'actually'}

    def remove_fillers(self, text: str) -> str:
        """Remove filler words."""
        if not self.config.remove_fillers:
            return text

        words = text.split()
        filtered_words = []

        for word in words:
            # Remove punctuation for checking
            clean_word = word.strip('.,!?').lower()
            if clean_word not in self.filler_words:
                filtered_words.append(word)

        return ' '.join(filtered_words)

    def capitalize_sentences(self, text: str) -> str:
        """Capitalize sentence beginnings."""
        if not self.config.capitalize_sentences:
            return text

        import re

        # Split into sentences and capitalize
        sentences = re.split(r'([.!?]+\s*)', text)
        result = []

        for i, sentence in enumerate(sentences):
            if i % 2 == 0:  # Actual sentence content
                sentence = sentence.strip()
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:] if sentence else sentence
            result.append(sentence)

        return ''.join(result)

    def apply_custom_rules(self, text: str) -> str:
        """Apply custom postprocessing rules."""
        if not self.config.custom_rules_json.get("enabled", False):
            return text

        rules = self.config.custom_rules_json.get("rules", [])

        for rule in rules:
            if "find" in rule and "replace" in rule:
                text = text.replace(rule["find"], rule["replace"])

        return text

    def process(self, text: str) -> str:
        """Apply full postprocessing pipeline."""
        if not self.config.enabled or not text:
            return text

        # 1. Remove fillers
        text = self.remove_fillers(text)

        # 2. Capitalize sentences
        text = self.capitalize_sentences(text)

        # 3. Apply custom rules
        text = self.apply_custom_rules(text)

        return text.strip()
