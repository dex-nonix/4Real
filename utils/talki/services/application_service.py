"""
Application service that coordinates between UI, audio processing, and input components.
"""

from typing import Optional
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtWidgets import QMessageBox
from pynput import keyboard, mouse
from talki.config.logging_config import logger
from talki.core.audio.processor import AudioProcessor
from talki.core.stt_engine import STTEngine, STTConfig
from talki.ui.main_window import MainWindow
from talki.ui.components.stt_config_dialog import STTConfigDialog
from talki.input.paste_mode import PasteMode
from talki.input.keyboard_simulator import KeyboardSimulator
from talki.services.config_manager import ConfigManager
from talki.utils.constants import (
    THREAD_CHECK_INTERVAL, AUTO_SUBMIT_DELAY,
    PROCESSING_THREAD_TIMEOUT, PASTE_LISTENER_DELAY, CONFIGS_DIR
)


class ApplicationService(QObject):
    """
    Main application service that coordinates between all components.

    Handles the business logic and communication between UI, audio processing,
    and input simulation components.
    """

    def __init__(self):
        """Initialize the application service."""
        super().__init__()

        # Components
        self.audio_processor = None
        self.main_window = None
        self.paste_mode = None
        self.keyboard_simulator = None
        self.config_manager = None
        self.stt_engine = None
        self.config_dialog = None

        # Listeners
        self.hotkey_listener = None
        self.mouse_listener = None

        # Timers
        self.thread_check_timer = None

        logger.debug("🎯 Application service initialized")

    def initialize_components(self, main_window: MainWindow):
        """
        Initialize all components and set up connections.

        Args:
            main_window: The main application window
        """
        self.main_window = main_window

        # Create components
        self.config_manager = ConfigManager(CONFIGS_DIR)
        self.keyboard_simulator = KeyboardSimulator()
        self.paste_mode = PasteMode(self.keyboard_simulator)

        # Initialize STT engine with current config
        current_config = self.config_manager.get_current_config()
        if current_config:
            try:
                self.stt_engine = STTEngine(current_config)
                self.stt_engine.on_transcript = lambda text: self.main_window.append_transcript(text)
                self.stt_engine.on_error = lambda error: logger.error(f"STT Error: {error}")
                self.stt_engine.on_endpoint = lambda: logger.info("Endpoint detected")
                logger.info("✅ STT engine initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize STT engine: {e}")
                # Try to create with default config as fallback
                try:
                    default_config = STTConfig()
                    self.stt_engine = STTEngine(default_config)
                    self.stt_engine.on_transcript = lambda text: self.main_window.append_transcript(text)
                    self.stt_engine.on_error = lambda error: logger.error(f"STT Error: {error}")
                    self.stt_engine.on_endpoint = lambda: logger.info("Endpoint detected")
                    logger.info("✅ STT engine initialized with default config")
                except Exception as e2:
                    logger.error(f"❌ Failed to initialize STT engine even with default config: {e2}")
                    self.stt_engine = None
        else:
            logger.error("❌ No current config available for STT engine initialization")
            self.stt_engine = None

        # Create audio processor with STT engine (or None if engine failed)
        self.audio_processor = AudioProcessor(self.stt_engine)

        # Set up signal connections
        self._connect_signals()

        # Set up hotkeys
        self._setup_hotkeys()

        # Set up mouse button listening
        self._setup_mouse_buttons()

        # Set up timers
        self._setup_timers()

        # Set up config management
        self._setup_config_management()

        logger.info("✅ All components initialized and connected")

    def _connect_signals(self):
        """Connect all component signals."""
        # Audio processor signals
        self.audio_processor.transcript_update.connect(self._on_transcript_update)
        self.audio_processor.error_signal.connect(self._on_audio_error)
        self.audio_processor.recording_state_changed.connect(self._on_recording_state_changed)

        # Main window signals
        self.main_window.start_recording_requested.connect(self._on_start_recording_requested)
        self.main_window.stop_recording_requested.connect(self._on_stop_recording_requested)
        self.main_window.send_to_focused_requested.connect(self._on_send_to_focused_requested)
        self.main_window.clear_requested.connect(self._on_clear_requested)
        self.main_window.config_selected.connect(self._on_config_selected)
        self.main_window.settings_requested.connect(self._on_settings_requested)

    def _setup_hotkeys(self):
        """Set up global hotkeys (Cmd+Space for macOS, adapt for Linux)."""
        logger.info("🔥 Setting up global hotkeys (Cmd+Space)")

        hotkeys = {keyboard.Key.cmd, keyboard.Key.space}
        pressed_keys = set()

        def on_press(key):
            if key in hotkeys:
                logger.debug(f"🔑 Hotkey key pressed: {key}")
                pressed_keys.add(key)
                if pressed_keys == hotkeys:
                    logger.info("🎯 Cmd+Space hotkey activated!")
                    self._toggle_recording_from_hotkey()

        def on_release(key):
            if key in hotkeys:
                logger.debug(f"🔓 Hotkey key released: {key}")
                pressed_keys.discard(key)

        logger.debug("⌨️  Creating hotkey listener...")
        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()
        logger.info("✅ Global hotkeys activated")

    def _setup_mouse_buttons(self):
        """Set up global mouse button listening."""
        logger.info("🖱️  Setting up global mouse button listening")

        def on_mouse_click(x, y, button, pressed):
            """Handle global mouse button presses."""
            if not pressed:  # Only handle button down events
                return

            try:
                # Check button by name to avoid attribute errors
                button_name = str(button).lower()

                if 'x1' in button_name or 'backward' in button_name:
                    # Backward button - toggle recording (same as Cmd+Space)
                    logger.info("🔙 Mouse X1 (backward) - toggling recording")
                    QTimer.singleShot(0, self._toggle_recording_from_hotkey)

                elif 'x2' in button_name or 'forward' in button_name:
                    # Forward button - cancel/stop operations
                    logger.info("🔜 Mouse X2 (forward) - canceling operations")
                    QTimer.singleShot(0, self._cancel_operations)

            except Exception as e:
                logger.debug(f"⚠️  Mouse button not recognized: {button} - {e}")

        try:
            logger.debug("🐭 Creating global mouse listener...")
            self.mouse_listener = mouse.Listener(on_click=on_mouse_click)
            self.mouse_listener.start()
            logger.info("✅ Global mouse buttons activated (X1=toggle recording, X2=cancel)")
        except Exception as e:
            logger.error(f"❌ Failed to setup mouse listener: {e}")

    def _cancel_operations(self):
        """Cancel/stop current operations (called by mouse X2 button)."""
        logger.info("🚫 Canceling operations via mouse X2 button")

        # Stop recording if active
        if hasattr(self.audio_processor, 'is_recording') and self.audio_processor.is_recording:
            logger.info("⏹️  Stopping recording due to cancel")
            self._stop_recording()
        else:
            logger.debug("ℹ️  No active recording to cancel")

        # Cancel paste mode if active
        if hasattr(self.paste_mode, 'is_active') and self.paste_mode.is_active():
            logger.info("🎯 Canceling paste mode due to cancel")
            self.paste_mode.stop_paste_mode()
        else:
            logger.debug("ℹ️  No active paste mode to cancel")

    def _setup_timers(self):
        """Set up application timers."""
        self.thread_check_timer = QTimer(self)
        self.thread_check_timer.setInterval(THREAD_CHECK_INTERVAL)
        self.thread_check_timer.timeout.connect(self._check_thread_status)

    def _toggle_recording_from_hotkey(self):
        """Toggle recording state from hotkey."""
        # Determine action based on current recording state
        if hasattr(self.audio_processor, 'is_recording') and self.audio_processor.is_recording:
            action = "stop_recording"
            QTimer.singleShot(0, self._stop_recording)
        else:
            action = "start_recording"
            # Get current device and start recording
            device_index = self.main_window.recording_controls.mic_combo.currentData()
            if device_index is not None:
                QTimer.singleShot(0, lambda: self._start_recording(device_index))
            else:
                logger.warning("⚠️  No valid microphone device selected for hotkey recording")

        logger.debug(f"📤 Triggering {action} from hotkey")

    def _start_recording(self, device_index: int):
        """Start recording with the specified device."""
        # Check if STT engine is available
        if not self.stt_engine:
            error_msg = "STT engine not initialized"
            logger.error(f"❌ {error_msg}")
            self.main_window.recording_controls.set_status_text(f"Error: {error_msg}")
            return

        self.main_window.set_starting_state()
        self.audio_processor.start_recording(device_index)

    def _stop_recording(self):
        """Stop current recording."""
        logger.debug("🛑 Calling stop_recording on audio processor")
        self.main_window.set_stopping_state()
        self.audio_processor.stop_recording()
        self.thread_check_timer.start()

    def _on_start_recording_requested(self, device_index: int):
        """Handle start recording request from UI."""
        self._start_recording(device_index)

    def _on_stop_recording_requested(self):
        """Handle stop recording request from UI."""
        logger.debug("🛑 Stop recording requested from UI")
        self._stop_recording()

    def _on_transcript_update(self, text: str):
        """Handle new transcript text."""
        self.main_window.append_transcript(text)

    def _on_audio_error(self, error_msg: str):
        """Handle audio processing errors."""
        logger.error(f"❌ Audio error received: {error_msg}")
        self.main_window.recording_controls.status_label.setText(f"Error: {error_msg}")
        self.main_window.set_recording_state(False)

    def _on_recording_state_changed(self, is_recording: bool):
        """Handle recording state changes."""
        self.main_window.set_recording_state(is_recording)

        if not is_recording:
            # Recording stopped, check if auto-send is enabled
            if self.main_window.get_auto_send_enabled():
                logger.info("🚀 Auto-send enabled - sending transcribed text")
                self._perform_auto_send()

    def _check_thread_status(self):
        """Check if the processing thread has finished."""
        logger.debug("⏰ Thread check timer tick")

        if not self.audio_processor.is_thread_alive():
            logger.info("✅ Processing thread finished - resetting UI")
            self.thread_check_timer.stop()
            self.main_window.set_recording_state(False)

            # Auto-send after thread completes if enabled
            if self.main_window.get_auto_send_enabled():
                self._perform_auto_send()

    def _perform_auto_send(self):
        """Perform auto-send of transcribed text."""
        current_text = self.main_window.get_transcript_text()
        if current_text:
            logger.info(f"📝 Auto-sending text: \"{current_text[:50]}...\"")
            self._send_text_to_focused_input(current_text)
            logger.info("✅ Auto-send completed")

            # Auto-submit if enabled
            if self.main_window.get_auto_submit_enabled():
                self._perform_auto_submit()

            # Clear text if option enabled
            if self.main_window.get_clear_after_send_enabled():
                logger.info("🧹 Clear history enabled - clearing text area after auto-send")
                self.main_window.clear_transcript()
        else:
            logger.debug("📝 No text to auto-send")

    def _on_send_to_focused_requested(self):
        """Handle send to focused input request."""
        current_text = self.main_window.get_transcript_text()
        if current_text:
            self.main_window.set_paste_mode_active(True)
            # Small delay to let focus settle before enabling listeners
            QTimer.singleShot(PASTE_LISTENER_DELAY, lambda: self.paste_mode.start_paste_mode(
                current_text, self._on_paste_completed, self._on_paste_mode_cancelled))
        else:
            logger.warning("⚠️  No text available to send")

    def _send_text_to_focused_input(self, text: str):
        """Send text directly to focused input field."""
        try:
            self.keyboard_simulator.type_text(text)
        except Exception as e:
            logger.error(f"❌ Error sending text to focused input: {e}")

    def _perform_auto_submit(self):
        """Perform auto-submit after sending text."""
        if self.main_window.get_ctrl_enter_enabled():
            logger.info("⏎  Auto-submit enabled - scheduling Ctrl+Enter")
            QTimer.singleShot(AUTO_SUBMIT_DELAY, self._send_ctrl_enter)
        else:
            logger.info("⏎  Auto-submit enabled - scheduling Enter")
            QTimer.singleShot(AUTO_SUBMIT_DELAY, self._send_enter)

    def _send_enter(self):
        """Send Enter keypress."""
        try:
            self.keyboard_simulator.send_enter()
        except Exception as e:
            logger.error(f"❌ Error sending Enter keypress: {e}")

    def _send_ctrl_enter(self):
        """Send Ctrl+Enter keypress."""
        try:
            self.keyboard_simulator.send_ctrl_enter()
        except Exception as e:
            logger.error(f"❌ Error sending Ctrl+Enter keypress: {e}")

    def _on_clear_requested(self):
        """Handle clear transcript request."""
        self.main_window.clear_transcript()

    def _on_paste_completed(self):
        """Handle paste operation completion."""
        logger.info("✅ Paste operation completed")

        # Reset paste mode status
        self.main_window.set_paste_mode_active(False)

        # Clear text if option enabled
        if self.main_window.get_clear_after_send_enabled():
            logger.info("🧹 Clear history enabled - clearing text area after paste")
            self.main_window.clear_transcript()

        # Auto-submit if enabled
        if self.main_window.get_auto_submit_enabled():
            self._perform_auto_submit()

    def _setup_config_management(self):
        """Set up configuration management."""
        # Update UI with current configs
        config_names = self.config_manager.get_config_names()
        self.main_window.update_config_list(config_names)

        current_config = self.config_manager.get_current_config_name()
        if current_config:
            self.main_window.set_current_config(current_config)

        logger.info(f"🎛️  Config management initialized with {len(config_names)} configurations")

    def _on_config_selected(self, config_name: str):
        """Handle configuration selection."""
        logger.info(f"🔄 Switching to config: {config_name}")

        # Stop current recording if active
        if self.audio_processor and self.audio_processor.is_recording:
            self._stop_recording()

        # Switch configuration
        if self.config_manager.set_current_config(config_name):
            new_config = self.config_manager.get_current_config()
            if new_config:
                # Create new STT engine with new config
                self.stt_engine = STTEngine(new_config)
                self.stt_engine.on_transcript = lambda text: self.main_window.append_transcript(text)
                self.stt_engine.on_error = lambda error: logger.error(f"STT Error: {error}")
                self.stt_engine.on_endpoint = lambda: logger.info("Endpoint detected")

                # Update audio processor with new engine
                self.audio_processor.update_stt_engine(self.stt_engine)

                logger.info(f"✅ Successfully switched to config: {config_name}")
            else:
                logger.error(f"❌ Failed to load config: {config_name}")
        else:
            logger.error(f"❌ Failed to switch to config: {config_name}")

    def _on_settings_requested(self):
        """Handle settings button click."""
        logger.debug("⚙️  Opening config dialog")

        self.config_dialog = STTConfigDialog(self.config_manager, self.main_window)
        self.config_dialog.config_selected.connect(self._on_config_dialog_selected)
        self.config_dialog.exec()

    def _on_config_dialog_selected(self, config_name: str):
        """Handle config selection from dialog."""
        if config_name:
            self._on_config_selected(config_name)
            self.main_window.set_current_config(config_name)

    def _on_paste_mode_cancelled(self):
        """Handle paste mode cancellation."""
        logger.info("🚫 Paste mode cancelled")
        self.main_window.set_paste_mode_active(False)

    def shutdown(self):
        """Clean shutdown of all components."""
        logger.info("🔄 Application shutdown initiated")

        # Hide tray icon
        if hasattr(self.main_window, 'tray_icon') and self.main_window.tray_icon:
            logger.debug("🔔 Hiding system tray icon...")
            self.main_window.tray_icon.hide()

        # Stop recording
        if self.audio_processor:
            logger.debug("⏹️  Stopping audio recording...")
            self.audio_processor.stop_recording()

        # Stop paste mode
        if self.paste_mode and self.paste_mode.is_active():
            logger.debug("🛑 Disabling paste mode during shutdown...")
            self.paste_mode.stop_paste_mode()

        # Stop listeners
        if self.hotkey_listener:
            logger.debug("🔥 Stopping hotkey listener...")
            self.hotkey_listener.stop()

        if self.mouse_listener:
            logger.debug("🖱️  Stopping mouse listener...")
            self.mouse_listener.stop()

        # Wait for processing thread
        if self.audio_processor and self.audio_processor.is_thread_alive():
            logger.debug("🧵 Waiting for processing thread to finish...")
            self.audio_processor.processing_thread.join(timeout=PROCESSING_THREAD_TIMEOUT)
            if self.audio_processor.processing_thread.is_alive():
                logger.warning("⚠️  Processing thread did not finish within timeout")

        logger.info("✅ Application shutdown completed")
