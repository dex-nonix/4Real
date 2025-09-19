"""
Recording control UI components.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from talki.config.logging_config import logger
from talki.core.audio.device_manager import AudioDeviceManager
from .config_controls import ConfigControls


class RecordingControls(QWidget):
    """
    UI component for recording controls with a single toggle button.
    """

    # Signals
    start_recording_requested = pyqtSignal(int)  # device_index
    stop_recording_requested = pyqtSignal()
    config_selected = pyqtSignal(str)  # config_name
    settings_requested = pyqtSignal()  # Open config dialog

    def __init__(self, parent=None):
        """Initialize recording controls."""
        super().__init__(parent)
        self.device_manager = AudioDeviceManager()

        # UI Elements
        self.mic_combo = None
        self.toggle_button = None
        self.config_controls = None

        # State
        self.is_recording = False

        self._create_ui()
        self._setup_layout()
        logger.debug("🎛️  Recording controls initialized")

    def _setup_layout(self):
        """Set up the component layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Config controls at top
        layout.addWidget(self.config_controls)

        # Recording controls below
        recording_layout = QHBoxLayout()
        recording_layout.setContentsMargins(0, 0, 0, 0)
        recording_layout.setSpacing(8)

        # Microphone icon
        mic_label = QLabel("🎤")
        mic_label.setFixedWidth(20)
        recording_layout.addWidget(mic_label)

        # Microphone selection
        self.mic_combo.setFixedWidth(160)
        recording_layout.addWidget(self.mic_combo)

        # Toggle button (small and compact)
        self.toggle_button.setFixedSize(30, 30)
        recording_layout.addWidget(self.toggle_button)

        recording_layout.addStretch()
        layout.addLayout(recording_layout)

    def _create_ui(self):
        """Create the UI elements."""
        # Config controls
        self.config_controls = ConfigControls(self)

        # Microphone selection
        self.mic_combo = QComboBox()
        self.mic_combo.setFixedWidth(160)
        self._populate_microphones()

        # Compact toggle button (icon only)
        self.toggle_button = QPushButton("▶️")
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setToolTip("Start/Stop Recording")
        self._update_button_style()
        self.toggle_button.clicked.connect(self._on_toggle_clicked)

    def _update_button_style(self):
        """Update the button appearance based on recording state."""
        if self.is_recording:
            # Recording state - red with stop icon
            self.toggle_button.setText("⏹️")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: 1px solid #d32f2f;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """)
        else:
            # Stopped state - green with play icon
            self.toggle_button.setText("▶️")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #388E3C;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
                QPushButton:pressed {
                    background-color: #2E7D32;
                }
            """)

    def _populate_microphones(self):
        """Populate the microphone combo box with available devices."""
        try:
            device_names = self.device_manager.get_device_names()
            devices = self.device_manager.get_devices()

            for i, name in enumerate(device_names):
                device_index = devices[i][0]
                self.mic_combo.addItem(name, device_index)

            # Select recommended device
            recommended_index = self.device_manager.get_recommended_device_index()
            if recommended_index is not None:
                # Find the combo box index for the recommended device
                for combo_index in range(self.mic_combo.count()):
                    if self.mic_combo.itemData(combo_index) == recommended_index:
                        self.mic_combo.setCurrentIndex(combo_index)
                        selected_name = self.mic_combo.currentText()
                        logger.info(f"✅ Selected microphone: {selected_name}")
                        break

        except Exception as e:
            logger.error(f"❌ Could not populate microphones: {e}")

    def set_recording_state(self, is_recording: bool):
        """
        Update the UI to reflect recording state.

        Args:
            is_recording: True if currently recording, False otherwise
        """
        logger.debug(f"🔄 set_recording_state called with is_recording={is_recording}, current self.is_recording={self.is_recording}")
        self.is_recording = is_recording
        self.toggle_button.setEnabled(True)  # Make sure button is enabled
        self._update_button_style()

        if is_recording:
            logger.debug("🎤 UI updated: recording state")
        else:
            logger.debug("⏹️  UI updated: stopped state")

    def set_starting_state(self):
        """Set UI to starting state."""
        self.toggle_button.setEnabled(False)
        self.toggle_button.setText("⏳")

    def set_stopping_state(self):
        """Set UI to stopping state."""
        self.toggle_button.setEnabled(False)
        self.toggle_button.setText("⏹️")

    def _on_toggle_clicked(self):
        """Handle toggle button click."""
        device_index = self.mic_combo.currentData()
        if device_index is None:
            logger.error("❌ No valid microphone device selected")
            return

        current_text = self.toggle_button.text()

        if current_text == "▶️":
            # Ready to start - send start signal
            logger.info(f"▶️  Start recording button pressed - Device: {device_index}")
            self.set_starting_state()
            self.start_recording_requested.emit(device_index)
        elif current_text == "⏹️":
            # Ready to stop - send stop signal
            logger.info("⏹️  Stop recording button pressed")
            self.set_stopping_state()
            self.stop_recording_requested.emit()
        else:
            # Button is in transition state (⏳), ignore click
            logger.debug(f"🔘 Button clicked while in transition state: {current_text}")
            return

    def update_config_list(self, config_names: list):
        """Update the configuration dropdown list."""
        self.config_controls.update_config_list(config_names)

    def set_current_config(self, config_name: str):
        """Set the currently selected configuration."""
        self.config_controls.set_current_config(config_name)

    def get_current_config(self) -> str:
        """Get the currently selected configuration name."""
        return self.config_controls.get_current_config()

    def connect_config_signals(self):
        """Connect config control signals."""
        self.config_controls.config_selected.connect(self._on_config_selected)
        self.config_controls.settings_requested.connect(self._on_settings_requested)

    def _on_config_selected(self, config_name: str):
        """Handle configuration selection."""
        self.config_selected.emit(config_name)

    def _on_settings_requested(self):
        """Handle settings button click."""
        self.settings_requested.emit()
