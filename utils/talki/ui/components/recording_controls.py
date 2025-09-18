"""
Recording control UI components.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal
from talki.config.logging_config import logger
from talki.core.audio.device_manager import AudioDeviceManager
from talki.utils.constants import (
    START_BUTTON_TEXT, STOP_BUTTON_TEXT,
    STATUS_READY, STATUS_STARTING, STATUS_RECORDING, STATUS_STOPPING, STATUS_STOPPED
)


class RecordingControls(QWidget):
    """
    UI component for recording controls (microphone selection, start/stop buttons, status).
    """

    # Signals
    start_recording_requested = pyqtSignal(int)  # device_index
    stop_recording_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize recording controls."""
        super().__init__(parent)
        self.device_manager = AudioDeviceManager()

        # UI Elements
        self.mic_combo = None
        self.start_button = None
        self.stop_button = None
        self.status_label = None

        # State
        self.is_recording = False

        self._create_ui()
        self._setup_layout()
        logger.debug("🎛️  Recording controls initialized")

    def _setup_layout(self):
        """Set up the component layout."""
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)

        # Microphone layout
        mic_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QLabel
        mic_layout.addWidget(QLabel("Microphone:"))
        mic_layout.addWidget(self.mic_combo)
        layout.addLayout(mic_layout)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # Status label
        layout.addWidget(self.status_label)

    def _create_ui(self):
        """Create the UI elements."""
        # Microphone selection
        self.mic_combo = QComboBox()
        self._populate_microphones()

        # Buttons
        self.start_button = QPushButton(START_BUTTON_TEXT)
        self.start_button.clicked.connect(self._on_start_clicked)

        self.stop_button = QPushButton(STOP_BUTTON_TEXT)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)

        # Status label
        self.status_label = QLabel(STATUS_READY)

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
            self.status_label.setText(f"Could not list microphones: {e}")

    def set_recording_state(self, is_recording: bool):
        """
        Update the UI to reflect recording state.

        Args:
            is_recording: True if currently recording, False otherwise
        """
        self.is_recording = is_recording

        if is_recording:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText(STATUS_RECORDING)
            logger.debug("🎤 UI updated: recording state")
        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText(STATUS_STOPPED)
            logger.debug("⏹️  UI updated: stopped state")

    def set_starting_state(self):
        """Set UI to starting state."""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.status_label.setText(STATUS_STARTING)

    def set_stopping_state(self):
        """Set UI to stopping state."""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.status_label.setText(STATUS_STOPPING)

    def _on_start_clicked(self):
        """Handle start button click."""
        device_index = self.mic_combo.currentData()
        if device_index is not None:
            logger.info(f"▶️  Start recording button pressed - Device: {device_index}")
            self.set_starting_state()
            self.start_recording_requested.emit(device_index)
        else:
            logger.error("❌ No valid microphone device selected")

    def _on_stop_clicked(self):
        """Handle stop button click."""
        logger.info("⏹️  Stop recording button pressed")
        self.set_stopping_state()
        self.stop_recording_requested.emit()
