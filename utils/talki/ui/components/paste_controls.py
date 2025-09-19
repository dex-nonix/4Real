"""
Paste mode control UI components.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox
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
        # Action buttons (icon-only, small)
        self.clear_button = QPushButton("🗑️")
        self.clear_button.setFixedSize(30, 30)
        self.clear_button.setToolTip("Clear Text")
        self.clear_button.clicked.connect(self._on_clear_clicked)

        self.send_button = QPushButton("📤")
        self.send_button.setFixedSize(30, 30)
        self.send_button.setToolTip("Send to Focused Input")
        self.send_button.clicked.connect(self._on_send_clicked)

        # Paste status indicator (compact)
        self.paste_status_label = QLabel("🎯 Ready")
        self.paste_status_label.setStyleSheet("color: gray;")

        # Checkboxes (compact text)
        self.auto_submit_checkbox = QCheckBox("Auto-submit")
        self.auto_submit_checkbox.toggled.connect(self._on_auto_submit_toggled)

        self.ctrl_enter_checkbox = QCheckBox("Use Ctrl+Enter")
        self.ctrl_enter_checkbox.toggled.connect(self._on_ctrl_enter_toggled)

        self.auto_send_checkbox = QCheckBox("Auto-send")
        self.auto_send_checkbox.toggled.connect(self._on_auto_send_toggled)

        self.clear_history_checkbox = QCheckBox("Clear after send")
        self.clear_history_checkbox.toggled.connect(self._on_clear_after_send_toggled)

    def _setup_layout(self):
        """Set up the component layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top row: buttons + status
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.addWidget(self.clear_button)
        top_layout.addWidget(self.send_button)
        top_layout.addWidget(self.paste_status_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Checkboxes stacked vertically (no spacing)
        layout.addWidget(self.auto_submit_checkbox)
        layout.addWidget(self.ctrl_enter_checkbox)
        layout.addWidget(self.auto_send_checkbox)
        layout.addWidget(self.clear_history_checkbox)

    def set_paste_mode_active(self, active: bool):
        """
        Update the paste mode status indicator.

        Args:
            active: True if paste mode is active, False otherwise
        """
        self.paste_mode_active = active

        if active:
            self.paste_status_label.setText("🎯 Active")
            self.paste_status_label.setStyleSheet("color: green; font-size: 10px; font-weight: bold;")
            logger.info("🔄 Paste mode status: ACTIVE")
        else:
            self.paste_status_label.setText("🎯 Ready")
            self.paste_status_label.setStyleSheet("color: gray; font-size: 10px;")
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
