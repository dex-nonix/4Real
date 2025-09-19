"""
ConfigControls UI component - Configuration dropdown and settings button.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from talki.config.logging_config import logger


class ConfigControls(QWidget):
    """
    UI component for STT configuration selection and management.
    """

    # Signals
    config_selected = pyqtSignal(str)  # config_name
    settings_requested = pyqtSignal()  # Open config dialog

    def __init__(self, parent=None):
        """Initialize config controls."""
        super().__init__(parent)

        # UI Elements
        self.config_combo = None
        self.settings_button = None

        # State
        self.current_config = "default-speech"

        self._create_ui()
        self._setup_layout()
        logger.debug("🎛️  ConfigControls initialized")

    def _setup_layout(self):
        """Set up the component layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Config icon
        config_label = QLabel("⚙️")
        config_label.setFixedWidth(20)
        layout.addWidget(config_label)

        # Configuration selection
        self.config_combo.setFixedWidth(120)
        layout.addWidget(self.config_combo)

        # Settings button
        self.settings_button.setFixedSize(25, 25)
        layout.addWidget(self.settings_button)

        layout.addStretch()

    def _create_ui(self):
        """Create the UI elements."""
        # Configuration selection
        self.config_combo = QComboBox()
        self.config_combo.setFixedWidth(120)
        self.config_combo.currentTextChanged.connect(self._on_config_changed)

        # Settings button
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(25, 25)
        self.settings_button.setToolTip("Manage Configurations")
        self.settings_button.clicked.connect(self._on_settings_clicked)

    def _on_config_changed(self, config_name: str):
        """Handle configuration selection change."""
        if config_name and config_name != self.current_config:
            self.current_config = config_name
            logger.debug(f"🔄 Config selected: {config_name}")
            self.config_selected.emit(config_name)

    def _on_settings_clicked(self):
        """Handle settings button click."""
        logger.debug("⚙️  Settings button clicked")
        self.settings_requested.emit()

    def update_config_list(self, config_names: list):
        """Update the configuration dropdown list."""
        try:
            self.config_combo.clear()

            if not config_names:
                config_names = ["default-speech"]

            for name in config_names:
                self.config_combo.addItem(name)

            # Try to select current config
            current_index = self.config_combo.findText(self.current_config)
            if current_index >= 0:
                self.config_combo.setCurrentIndex(current_index)
            else:
                # Select first item if current not found
                self.config_combo.setCurrentIndex(0)
                if config_names:
                    self.current_config = config_names[0]

        except Exception as e:
            logger.error(f"❌ Failed to update config list: {e}")

    def set_current_config(self, config_name: str):
        """Set the currently selected configuration."""
        self.current_config = config_name

        # Update dropdown selection
        index = self.config_combo.findText(config_name)
        if index >= 0:
            self.config_combo.setCurrentIndex(index)

    def get_current_config(self) -> str:
        """Get the currently selected configuration name."""
        return self.current_config

    def set_enabled(self, enabled: bool):
        """Enable or disable the controls."""
        self.config_combo.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
