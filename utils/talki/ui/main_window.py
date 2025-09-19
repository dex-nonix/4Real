"""
Main application window.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal
from talki.config.logging_config import logger
from talki.ui.components.recording_controls import RecordingControls
from talki.ui.components.transcription_display import TranscriptionDisplay
from talki.ui.components.paste_controls import PasteControls
from talki.utils.constants import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_X, WINDOW_Y
)


class MainWindow(QMainWindow):
    """
    Main application window that assembles all UI components.
    """

    # Forward signals from components
    start_recording_requested = pyqtSignal(int)  # device_index
    stop_recording_requested = pyqtSignal()
    send_to_focused_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    auto_send_toggled = pyqtSignal(bool)
    auto_submit_toggled = pyqtSignal(bool)
    ctrl_enter_toggled = pyqtSignal(bool)
    clear_after_send_toggled = pyqtSignal(bool)
    transcript_update = pyqtSignal(str)  # Forward from transcription display
    config_selected = pyqtSignal(str)  # config_name
    settings_requested = pyqtSignal()  # Open config dialog

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # UI Components
        self.recording_controls = None
        self.transcription_display = None
        self.paste_controls = None
        self.config_dialog = None

        # System tray
        self.tray_icon = None

        self._setup_window()
        self._create_components()
        self._setup_layout()
        self._setup_system_tray()
        self._connect_signals()

        logger.info("🏠 MainWindow initialized")

    def _setup_window(self):
        """Set up basic window properties."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(300, 200)  # Allow resizing but set minimum size
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)  # Ensure initial size

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        logger.debug("🖥️  Window layout created")

    def _setup_system_tray(self):
        """Set up system tray icon and menu."""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Try to use custom icon from assets, fallback to default
        try:
            import os
            assets_path = os.path.join(os.path.dirname(__file__), 'assets')
            icon_path = os.path.join(assets_path, 'favicon-32x32.png')

            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
                logger.debug(f"🖼️  Loaded tray icon from: {icon_path}")
            else:
                # Fallback to default icon
                self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
                logger.debug("🖼️  Using default tray icon")
        except Exception as e:
            logger.warning(f"⚠️  Could not load tray icon: {e}")
            # Fallback to default icon
            try:
                self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
            except:
                pass  # No icon available

        self.tray_icon.setToolTip("Talki - Real-Time Transcription")

        # Create tray menu
        tray_menu = QMenu()

        # Restore action
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self._show_window)
        tray_menu.addAction(restore_action)

        tray_menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_icon_activated)

        # Show tray icon
        self.tray_icon.show()

        logger.info("🔔 System tray initialized")

    def _show_window(self):
        """Show and restore the main window."""
        self.show()
        self.raise_()
        self.activateWindow()
        logger.debug("🖥️  Window restored from tray")

    def _quit_application(self):
        """Quit the application completely."""
        self.tray_icon.hide()
        QApplication.quit()
        logger.info("👋 Application quit from tray menu")

    def _tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing."""
        if self.tray_icon.isVisible():
            logger.info("🔔 Minimizing to system tray instead of closing")
            self.hide()
            self.tray_icon.showMessage(
                "Talki",
                "Application minimized to system tray. Double-click to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()  # Don't close the application
        else:
            event.accept()  # Close if no tray icon

    def _create_components(self):
        """Create and initialize all UI components."""
        self.recording_controls = RecordingControls(self)
        self.transcription_display = TranscriptionDisplay(self)
        self.paste_controls = PasteControls(self)

    def _setup_layout(self):
        """Set up the main window layout."""
        # Recording controls (microphone + buttons + status)
        self.layout.addWidget(self.recording_controls)

        # Transcription display (allow expansion)
        self.layout.addWidget(self.transcription_display, 1)  # stretch factor 1

        # Action buttons (clear + send + paste status + checkboxes)
        self.layout.addWidget(self.paste_controls)

    def _connect_signals(self):
        """Connect component signals to window signals."""
        # Recording controls
        self.recording_controls.start_recording_requested.connect(self.start_recording_requested)
        self.recording_controls.stop_recording_requested.connect(self.stop_recording_requested)
        self.recording_controls.config_selected.connect(self.config_selected)
        self.recording_controls.settings_requested.connect(self.settings_requested)

        # Connect config signals in recording controls
        self.recording_controls.connect_config_signals()

        # Paste controls
        self.paste_controls.send_to_focused_requested.connect(self.send_to_focused_requested)
        self.paste_controls.clear_requested.connect(self.clear_requested)
        self.paste_controls.auto_send_toggled.connect(self.auto_send_toggled)
        self.paste_controls.auto_submit_toggled.connect(self.auto_submit_toggled)
        self.paste_controls.ctrl_enter_toggled.connect(self.ctrl_enter_toggled)
        self.paste_controls.clear_after_send_toggled.connect(self.clear_after_send_toggled)

        # Transcription display
        self.transcription_display.text_cleared.connect(self.clear_requested)

    # Delegate methods to components for external access

    def set_recording_state(self, is_recording: bool):
        """Update recording controls state."""
        self.recording_controls.set_recording_state(is_recording)

    def set_starting_state(self):
        """Set recording controls to starting state."""
        self.recording_controls.set_starting_state()

    def set_stopping_state(self):
        """Set recording controls to stopping state."""
        self.recording_controls.set_stopping_state()

    def append_transcript(self, text: str):
        """Append text to transcription display."""
        self.transcription_display.append_text(text)
        # Forward the signal
        self.transcript_update.emit(text)

    def get_transcript_text(self) -> str:
        """Get current transcript text."""
        return self.transcription_display.get_text()

    def clear_transcript(self):
        """Clear transcription display."""
        self.transcription_display.clear_text()

    def has_transcript_text(self) -> bool:
        """Check if transcription display has text."""
        return self.transcription_display.has_text()

    def set_paste_mode_active(self, active: bool):
        """Update paste mode status."""
        self.paste_controls.set_paste_mode_active(active)

    def get_auto_send_enabled(self) -> bool:
        """Check if auto-send is enabled."""
        return self.paste_controls.get_auto_send_enabled()

    def get_auto_submit_enabled(self) -> bool:
        """Check if auto-submit is enabled."""
        return self.paste_controls.get_auto_submit_enabled()

    def get_ctrl_enter_enabled(self) -> bool:
        """Check if Ctrl+Enter is enabled."""
        return self.paste_controls.get_ctrl_enter_enabled()

    def get_clear_after_send_enabled(self) -> bool:
        """Check if clear after send is enabled."""
        return self.paste_controls.get_clear_after_send_enabled()

    def update_config_list(self, config_names: list):
        """Update the configuration dropdown list."""
        self.recording_controls.update_config_list(config_names)

    def set_current_config(self, config_name: str):
        """Set the currently selected configuration."""
        self.recording_controls.set_current_config(config_name)

    def get_current_config(self) -> str:
        """Get the currently selected configuration name."""
        return self.recording_controls.get_current_config()
