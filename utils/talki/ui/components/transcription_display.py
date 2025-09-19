"""
Transcription display UI component.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QSizePolicy
from PyQt6.QtCore import pyqtSignal
from talki.config.logging_config import logger


class TranscriptionDisplay(QWidget):
    """
    UI component for displaying transcribed text.
    """

    # Signals
    text_cleared = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize transcription display."""
        super().__init__(parent)
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Transcribed text will appear here...")

        # Make text area resizable
        self.text_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.text_area)

        logger.debug("📝 Transcription display initialized")

    def append_text(self, text: str):
        """
        Append text to the transcription display.

        Args:
            text: Text to append
        """
        logger.debug(f"📝 Updating transcription display with: \"{text.strip()}\"")
        self.text_area.insertPlainText(text)
        self.text_area.ensureCursorVisible()
        logger.debug("✅ Transcription display updated")

    def get_text(self) -> str:
        """
        Get the current text content.

        Returns:
            Current text in the display area
        """
        return self.text_area.toPlainText()

    def clear_text(self):
        """Clear all text from the display."""
        logger.debug("🧹 Clearing transcription display")
        self.text_area.clear()
        self.text_cleared.emit()

    def has_text(self) -> bool:
        """
        Check if the display contains any text.

        Returns:
            True if text area has content, False otherwise
        """
        return bool(self.get_text().strip())
