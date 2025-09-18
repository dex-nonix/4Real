"""
Paste mode control UI components.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QCheckBox
from PyQt6.QtCore import pyqtSignal
from talki.config.logging_config import logger
from talki.utils.constants import (
    CLEAR_BUTTON_TEXT, SEND_BUTTON_TEXT,
    PASTE_STATUS_READY, PASTE_STATUS_ACTIVE
)


class PasteControls(QWidget):
    """
    UI component for paste mode controls and settings.
    """

    # Signals
    send_to_focused_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    auto_send_toggled = pyqtSignal(bool)
    auto_submit_toggled = pyqtSignal(bool)
    ctrl_enter_toggled = pyqtSignal(bool)
    clear_after_send_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialize paste controls."""
        super().__init__(parent)
        # UI Elements
        self.clear_button = None
        self.send_button = None
        self.paste_status_label = None

        # Checkboxes
        self.auto_submit_checkbox = None
        self.ctrl_enter_checkbox = None
        self.auto_send_checkbox = None
        self.clear_history_checkbox = None

        # State
        self.paste_mode_active = False

        self._create_ui()
        self._setup_layout()
        logger.debug("🎯 Paste controls initialized")

    def _create_ui(self):
        """Create the UI elements."""
        # Action buttons
        self.clear_button = QPushButton(CLEAR_BUTTON_TEXT)
        self.clear_button.clicked.connect(self._on_clear_clicked)

        self.send_button = QPushButton(SEND_BUTTON_TEXT)
        self.send_button.clicked.connect(self._on_send_clicked)

        # Paste status indicator
        self.paste_status_label = QLabel(PASTE_STATUS_READY)
        self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")

        # Checkboxes
        self.auto_submit_checkbox = QCheckBox("Auto-submit (Enter)")
        self.auto_submit_checkbox.toggled.connect(self._on_auto_submit_toggled)

        self.ctrl_enter_checkbox = QCheckBox("Use Ctrl+Enter")
        self.ctrl_enter_checkbox.toggled.connect(self._on_ctrl_enter_toggled)

        self.auto_send_checkbox = QCheckBox("Auto-send after stop")
        self.auto_send_checkbox.toggled.connect(self._on_auto_send_toggled)

        self.clear_history_checkbox = QCheckBox("Clear after sending")
        self.clear_history_checkbox.toggled.connect(self._on_clear_after_send_toggled)

    def _setup_layout(self):
        """Set up the component layout."""
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)

        # Action buttons layout
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.send_button)
        layout.addLayout(action_layout)

        # Status layout
        status_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QLabel
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.paste_status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Checkboxes layout
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.auto_submit_checkbox)
        checkbox_layout.addWidget(self.ctrl_enter_checkbox)
        checkbox_layout.addWidget(self.auto_send_checkbox)
        checkbox_layout.addWidget(self.clear_history_checkbox)
        layout.addLayout(checkbox_layout)

    def set_paste_mode_active(self, active: bool):
        """
        Update the paste mode status indicator.

        Args:
            active: True if paste mode is active, False otherwise
        """
        self.paste_mode_active = active

        if active:
            self.paste_status_label.setText(PASTE_STATUS_ACTIVE)
            self.paste_status_label.setStyleSheet("color: green; font-weight: bold;")
            logger.info("🔄 Paste mode status: ACTIVE")
        else:
            self.paste_status_label.setText(PASTE_STATUS_READY)
            self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")
            logger.info("🔄 Paste mode status: READY")

    def get_auto_send_enabled(self) -> bool:
        """Check if auto-send is enabled."""
        return self.auto_send_checkbox.isChecked()

    def get_auto_submit_enabled(self) -> bool:
        """Check if auto-submit is enabled."""
        return self.auto_submit_checkbox.isChecked()

    def get_ctrl_enter_enabled(self) -> bool:
        """Check if Ctrl+Enter is enabled for auto-submit."""
        return self.ctrl_enter_checkbox.isChecked()

    def get_clear_after_send_enabled(self) -> bool:
        """Check if clear after send is enabled."""
        return self.clear_history_checkbox.isChecked()

    def _on_clear_clicked(self):
        """Handle clear button click."""
        logger.debug("🧹 Clear button clicked")
        self.clear_requested.emit()

    def _on_send_clicked(self):
        """Handle send button click."""
        logger.info("📤 Send to focused input button pressed")
        self.send_to_focused_requested.emit()

    def _on_auto_send_toggled(self, checked: bool):
        """Handle auto-send checkbox toggle."""
        logger.debug(f"🔄 Auto-send toggled: {checked}")
        self.auto_send_toggled.emit(checked)

    def _on_auto_submit_toggled(self, checked: bool):
        """Handle auto-submit checkbox toggle."""
        logger.debug(f"🔄 Auto-submit toggled: {checked}")
        self.auto_submit_toggled.emit(checked)

    def _on_ctrl_enter_toggled(self, checked: bool):
        """Handle Ctrl+Enter checkbox toggle."""
        logger.debug(f"🔄 Ctrl+Enter toggled: {checked}")
        self.ctrl_enter_toggled.emit(checked)

    def _on_clear_after_send_toggled(self, checked: bool):
        """Handle clear after send checkbox toggle."""
        logger.debug(f"🔄 Clear after send toggled: {checked}")
        self.clear_after_send_toggled.emit(checked)
