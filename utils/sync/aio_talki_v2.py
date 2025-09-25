import sys
import logging
import colorama
import sounddevice as sd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QTextEdit, QCheckBox, QLabel)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from pynput import keyboard, mouse
from stt_engine import STTEngine

# Initialize colorama for colored console output
colorama.init()

# Configure logging with custom formatter
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            record.levelname = f"ℹ️  {record.levelname}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"⚠️  {record.levelname}"
        elif record.levelno == logging.ERROR:
            record.levelname = f"❌ {record.levelname}"
        elif record.levelno == logging.DEBUG:
            record.levelname = f"🔍 {record.levelname}"
        return super().format(record)

# Set up logger
logger = logging.getLogger('TalkiV2Logger')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class MainWindow(QMainWindow):
    # Signals for thread-safe GUI operations (must be class attributes in PyQt6)
    clear_text_signal = pyqtSignal()
    transcript_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logger.info("🏠 Initializing Talki V2 MainWindow...")

        self.setWindowTitle("Real-Time Transcription V2")
        self.setGeometry(100, 100, 400, 500)

        # Connect signals to slots
        self.clear_text_signal.connect(self._clear_text_area_slot)
        self.transcript_signal.connect(self.update_text_area)
        self.error_signal.connect(self.on_audio_error)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        logger.debug("🖥️  Window layout created")

        # UI Elements
        mic_layout = QHBoxLayout()
        self.mic_combo = QComboBox()
        self.populate_microphones()
        mic_layout.addWidget(QLabel("Microphone:"))
        mic_layout.addWidget(self.mic_combo)
        self.layout.addLayout(mic_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        self.layout.addLayout(button_layout)

        self.text_area = QTextEdit()
        self.layout.addWidget(self.text_area)

        action_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.text_area.clear)
        self.send_button = QPushButton("Send to Focused Input")
        self.send_button.clicked.connect(self.send_to_focused)
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.send_button)
        self.layout.addLayout(action_layout)

        checkbox_layout = QHBoxLayout()
        self.auto_submit_checkbox = QCheckBox("Auto-submit (Enter)")
        self.auto_submit_checkbox.setChecked(True)
        self.ctrl_enter_checkbox = QCheckBox("Use Ctrl+Enter")
        self.auto_send_checkbox = QCheckBox("Auto-send after stop")
        self.auto_send_checkbox.setChecked(True)
        self.clear_history_checkbox = QCheckBox("Clear after sending")
        self.clear_history_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.auto_submit_checkbox)
        checkbox_layout.addWidget(self.ctrl_enter_checkbox)
        checkbox_layout.addWidget(self.auto_send_checkbox)
        checkbox_layout.addWidget(self.clear_history_checkbox)
        self.layout.addLayout(checkbox_layout)

        # Status indicator for paste mode
        paste_status_layout = QHBoxLayout()
        self.paste_status_label = QLabel("🎯 Ready - Click 'Send to Focused Input' to begin")
        self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")
        paste_status_layout.addWidget(QLabel("Status:"))
        paste_status_layout.addWidget(self.paste_status_label)
        paste_status_layout.addStretch()
        self.layout.addLayout(paste_status_layout)

        self.status_label = QLabel("Ready.")
        self.layout.addWidget(self.status_label)

        # Backend - STT Engine V2 with Qt signal callbacks
        self.stt_engine = STTEngine(
            model_size="large-v3-turbo",
            on_transcript=self.transcript_signal.emit,
            on_error=self.error_signal.emit,
            on_status=self.on_status_update
        )

        self.thread_check_timer = QTimer(self)
        self.thread_check_timer.setInterval(100)
        self.thread_check_timer.timeout.connect(self.check_if_thread_is_done)

        # Listeners
        self.keyboard_controller = keyboard.Controller()
        self.hotkey_listener = None
        self.escape_listener = None  # For escape key when in paste mode
        self.ctrl_pressed = False

        # Paste mode state
        self.paste_mode_active = False
        self.pending_paste_text = None
        self.paste_mouse_listener = None
        self.paste_keyboard_listener = None
        self.paste_escape_listener = None

    def start_recording(self):
        device_index = self.mic_combo.currentData()
        if device_index is not None:
            logger.info(f"▶️  Start recording button pressed - Device: {device_index}")
            self.status_label.setText("Starting...")
            logger.debug("🎯 Calling stt_engine.start_recording()")
            self.stt_engine.start_recording(device_index)
        else:
            logger.error("❌ No valid microphone device selected")

    def stop_recording(self):
        logger.info("⏹️  Stop recording button pressed")
        self.status_label.setText("Stopping...")
        self.stop_button.setEnabled(False)
        logger.debug("🎯 Calling stt_engine.stop_recording()")
        self.stt_engine.stop_recording()
        logger.debug("⏰ Starting thread check timer")
        self.thread_check_timer.start()

    def check_if_thread_is_done(self):
        logger.debug("⏰ Thread check timer tick")
        if not self.stt_engine.is_thread_alive():
            logger.info("✅ Processing thread finished - resetting UI")
            self.thread_check_timer.stop()
            self.start_button.setEnabled(True)
            self.status_label.setText("Stopped.")

            # Auto-send to focused input if enabled
            if self.auto_send_checkbox.isChecked():
                logger.info("🚀 Auto-send enabled - sending transcribed text to focused input")
                current_text = self.text_area.toPlainText()
                if current_text:
                    logger.info(f"📝 Auto-sending text: \"{current_text[:50]}...\"")
                    # Use the same direct typing approach as paste mode
                    self._type_text_directly(current_text)
                    logger.info("✅ Auto-send completed")

                    # Auto-submit if enabled
                    if self.auto_submit_checkbox.isChecked():
                        if self.ctrl_enter_checkbox.isChecked():
                            logger.info("⏎  Auto-submit enabled - scheduling Ctrl+Enter")
                            QTimer.singleShot(100, self._send_ctrl_enter)
                        else:
                            logger.info("⏎  Auto-submit enabled - scheduling Enter")
                            QTimer.singleShot(100, self._send_enter)

                    # Clear text if option enabled (thread-safe via signal)
                    if self.clear_history_checkbox.isChecked():
                        logger.info("🧹 Clear history enabled - clearing text area after auto-send")
                        self.clear_text_signal.emit()
                else:
                    logger.debug("📝 No text to auto-send")
        else:
            logger.debug("🧵 Processing thread still alive")

    def on_audio_error(self, msg):
        logger.error(f"❌ Audio error received: {msg}")
        self.status_label.setText(f"Error: {msg}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        logger.info("🔄 UI reset due to audio error")

    def on_status_update(self, msg):
        """Handle status updates from STT engine"""
        logger.debug(f"📊 Status update: {msg}")
        if msg == "Recording started":
            self.status_label.setText("Recording...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        elif msg == "Recording stopped":
            self.status_label.setText("Stopped.")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def update_text_area(self, text):
        logger.debug(f"📝 Updating text area with: \"{text.strip()}\"")
        self.text_area.insertPlainText(text)
        self.text_area.ensureCursorVisible()
        logger.debug("✅ Text area updated and cursor positioned")

    def send_to_focused(self):
        logger.info("📤 Send to focused input button pressed")

        # Don't capture text yet - wait for Ctrl+Click
        self.paste_mode_active = True
        self._update_paste_status()

        # Enable paste mode for Ctrl+click
        logger.info("🎯 Paste mode enabled - regular clicks focus windows, Ctrl+Click pastes")

        # Small delay to let focus settle
        QTimer.singleShot(200, self._enable_paste_listeners)

    def _enable_paste_listeners(self):
        """Enable paste mode listeners for Ctrl+click"""
        try:
            logger.debug("🐭 Starting paste mode mouse listener...")
            self.paste_mouse_listener = mouse.Listener(on_click=self.on_paste_click)
            self.paste_mouse_listener.start()

            logger.debug("⌨️  Starting paste mode keyboard listener...")
            # Separate callbacks for press and release events
            self.paste_keyboard_listener = keyboard.Listener(on_press=self.on_paste_key_press,
                                                           on_release=self.on_paste_key_release)
            self.paste_keyboard_listener.start()

            logger.info("✅ Paste mode active - Regular clicks focus, Ctrl+Click ONLY pastes, ESC cancels")
            logger.debug(f"🔍 Initial ctrl_pressed state: {self.ctrl_pressed}")
        except Exception as e:
            logger.error(f"❌ Failed to enable paste listeners: {e}")
            self._disable_paste_listeners()

    def _disable_paste_listeners(self):
        """Disable paste mode listeners"""
        logger.info("🛑 Disabling paste mode listeners...")

        if self.paste_mouse_listener:
            self.paste_mouse_listener.stop()
            self.paste_mouse_listener = None

        if self.paste_keyboard_listener:
            self.paste_keyboard_listener.stop()
            self.paste_keyboard_listener = None

        self.paste_mode_active = False
        self.pending_paste_text = None
        self._update_paste_status()
        logger.info("✅ Paste mode disabled")

    def on_paste_click(self, x, y, button, pressed):
        """Handle clicks for paste mode - ONLY Ctrl+Click pastes, regular clicks focus"""
        if pressed and button == mouse.Button.left and self.paste_mode_active:
            logger.debug(f"🖱️  Click detected at ({x}, {y}) - ctrl_pressed = {self.ctrl_pressed}")

            # Use stored Ctrl state - make sure keyboard listeners are working properly
            if self.ctrl_pressed:
                # ONLY Ctrl+Click triggers paste
                logger.info(f"🎯 Ctrl+Click detected at ({x}, {y}) - capturing text and pasting")

                # Capture text at the moment of Ctrl+Click
                current_text = self.text_area.toPlainText()
                if current_text:
                    self.pending_paste_text = current_text
                    logger.info(f"📝 Captured text for paste: \"{current_text[:50]}...\"")
                    self._execute_paste()
                else:
                    logger.warning("⚠️  No text available to paste - but mechanism still works")
                    # Still disable mode even with no text
                    self._disable_paste_listeners()
            else:
                # Regular click - ONLY focuses window, NO PASTE
                logger.debug(f"🖱️  Regular click at ({x}, {y}) - focusing window/area only (NO PASTE)")
                # The click itself will focus the window, no paste action

    def on_paste_key_press(self, key):
        """Handle key press events for paste mode"""
        try:
            if key == keyboard.Key.esc and self.paste_mode_active:
                logger.info("🚫 Paste mode: Escape key pressed - canceling")
                self._disable_paste_listeners()
                return False  # Stop the listener
            elif key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                logger.debug("🔑 Paste mode: Ctrl key pressed - setting ctrl_pressed = True")
                self.ctrl_pressed = True
                logger.debug(f"🔍 Ctrl state: {self.ctrl_pressed}")
        except Exception as e:
            logger.error(f"❌ Error in key press handler: {e}")

    def on_paste_key_release(self, key):
        """Handle key release events for paste mode"""
        try:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                logger.debug("🔓 Paste mode: Ctrl key released - setting ctrl_pressed = False")
                self.ctrl_pressed = False
                logger.debug(f"🔍 Ctrl state: {self.ctrl_pressed}")
        except Exception as e:
            logger.error(f"❌ Error in key release handler: {e}")

    def _execute_paste(self):
        """Execute the paste operation by typing text directly"""
        logger.info("⌨️  Executing paste operation...")

        # Type the stored text directly (no clipboard)
        if self.pending_paste_text:
            logger.debug(f"📝 Typing {len(self.pending_paste_text)} characters directly...")
            self._type_text_directly(self.pending_paste_text)
            logger.info("✅ Paste operation completed")

            # Clear text area after successful paste if option is enabled (thread-safe via signal)
            if self.clear_history_checkbox.isChecked():
                logger.info("🧹 Clear history enabled - clearing text area after paste")
                self.clear_text_signal.emit()

            # Auto-submit if enabled (thread-safe via signal)
            if self.auto_submit_checkbox.isChecked():
                use_ctrl_enter = self.ctrl_enter_checkbox.isChecked()
                if use_ctrl_enter:
                    logger.info("⏎  Auto-submit enabled - scheduling Ctrl+Enter key press")
                    logger.debug("⏰ Ctrl+Enter will be pressed in 100ms")
                else:
                    logger.info("⏎  Auto-submit enabled - scheduling Enter key press")
                    logger.debug("⏰ Enter will be pressed in 100ms")
                # Use signal for thread-safe submission
                QTimer.singleShot(100, lambda: self._send_keys(use_ctrl_enter))
            else:
                logger.debug("🚫 Auto-submit disabled")
        else:
            logger.warning("⚠️  No text available to paste")

        # Disable listeners after paste
        self._disable_paste_listeners()

    def _update_paste_status(self):
        """Update the paste status indicator"""
        if self.paste_mode_active:
            self.paste_status_label.setText("🎯 Paste Mode: Regular clicks focus, Ctrl+Click ONLY pastes (ESC cancels)")
            self.paste_status_label.setStyleSheet("color: green; font-weight: bold;")
            logger.info("🔄 Paste mode status: ACTIVE")
        else:
            self.paste_status_label.setText("🎯 Ready - Click 'Send to Focused Input' to begin")
            self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")
            logger.info("🔄 Paste mode status: READY")

    def _type_text_directly(self, text):
        """Type text directly using keyboard controller"""
        try:
            for char in text:
                if char == '\n':
                    # Handle newlines by pressing Enter
                    self.keyboard_controller.tap(keyboard.Key.enter)
                elif char == '\t':
                    # Handle tabs
                    self.keyboard_controller.tap(keyboard.Key.tab)
                else:
                    # Type regular characters
                    self.keyboard_controller.type(char)
                # Small delay between characters for reliability
                import time
                time.sleep(0.001)
        except Exception as e:
            logger.error(f"❌ Error typing text directly: {e}")

    def _send_keys(self, use_ctrl_enter):
        """Send keypress (thread-safe)"""
        if use_ctrl_enter:
            self._send_ctrl_enter()
        else:
            self._send_enter()

    def _send_enter(self):
        """Send Enter keypress"""
        logger.debug("⏎ Sending Enter keypress")
        self.keyboard_controller.tap(keyboard.Key.enter)

    def _send_ctrl_enter(self):
        """Send Ctrl+Enter keypress"""
        logger.debug("⏎ Sending Ctrl+Enter keypress")
        self.keyboard_controller.press(keyboard.Key.ctrl)
        self.keyboard_controller.tap(keyboard.Key.enter)
        self.keyboard_controller.release(keyboard.Key.ctrl)

    def _clear_text_area_slot(self):
        """Slot for clearing text area from any thread"""
        logger.debug("🧹 Clearing text area via signal")
        self.text_area.clear()

    def populate_microphones(self):
        try:
            logger.debug("🎤 Querying available audio devices...")
            device_count = 0
            default_device_index = None
            first_device_index = None

            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0:
                    logger.debug(f"📱 Found input device: {d['name']} (index: {i})")
                    self.mic_combo.addItem(d['name'], i)
                    device_count += 1

                    # Look for the device named "Default"
                    if d['name'].lower() == 'default':
                        default_device_index = i
                        logger.info(f"🎯 Found system default microphone: {d['name']}")

                    # Remember the first device as fallback
                    if first_device_index is None:
                        first_device_index = i

            if device_count > 0:
                # Select the device named "Default" if found, otherwise first device
                if default_device_index is not None:
                    # Find the combo box index for the default device
                    for combo_index in range(self.mic_combo.count()):
                        if self.mic_combo.itemData(combo_index) == default_device_index:
                            self.mic_combo.setCurrentIndex(combo_index)
                            break
                    selected_device_name = self.mic_combo.currentText()
                    logger.info(f"✅ Found {device_count} devices - System default selected: {selected_device_name}")
                else:
                    # No "Default" device found, use first available
                    self.mic_combo.setCurrentIndex(0)
                    selected_device_name = self.mic_combo.currentText()
                    logger.info(f"✅ Found {device_count} devices - First available selected: {selected_device_name}")
            else:
                logger.warning("⚠️  No microphone devices found")

        except Exception as e:
            logger.error(f"❌ Could not list audio devices: {e}")
            self.status_label.setText(f"Could not list audio devices: {e}")

    def setup_hotkeys(self):
        logger.info("🔥 Setting up global hotkeys (Cmd+Space)")
        hotkeys = {keyboard.Key.cmd, keyboard.Key.space}
        pressed_keys = set()

        def on_press(key):
            if key in hotkeys:
                logger.debug(f"🔑 Hotkey key pressed: {key}")
                pressed_keys.add(key)
                if pressed_keys == hotkeys:
                    logger.info("🎯 Cmd+Space hotkey activated!")
                    action = self.start_recording if self.start_button.isEnabled() else self.stop_recording
                    action_name = "start_recording" if self.start_button.isEnabled() else "stop_recording"
                    logger.debug(f"📤 Triggering {action_name} from hotkey")
                    QTimer.singleShot(0, action)

        def on_release(key):
            if key in hotkeys:
                logger.debug(f"🔓 Hotkey key released: {key}")
                pressed_keys.discard(key)

        logger.debug("⌨️  Creating hotkey listener...")
        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()
        logger.info("✅ Global hotkeys activated")

    def closeEvent(self, event):
        logger.info("🔄 Application closing - performing cleanup...")
        logger.debug("⏹️  Stopping audio recording...")
        self.stt_engine.stop_recording()

        # Disable paste mode if active
        if self.paste_mode_active:
            logger.debug("🛑 Disabling paste mode during shutdown...")
            self._disable_paste_listeners()

        if self.hotkey_listener:
            logger.debug("🔥 Stopping hotkey listener...")
            self.hotkey_listener.stop()

        if self.stt_engine.is_thread_alive():
            logger.debug("🧵 Waiting for processing thread to finish...")
            # Note: STTEngine handles its own thread cleanup
            pass

        logger.info("✅ Application cleanup completed")
        event.accept()


def main():
    logger.info("🚀 Starting Talki V2 Real-Time Transcription Application")
    logger.info("=" * 60)

    logger.debug("📱 Creating QApplication...")
    app = QApplication(sys.argv)

    logger.debug("🏠 Creating MainWindow...")
    window = MainWindow()

    logger.debug("🔥 Setting up hotkeys...")
    window.setup_hotkeys()

    logger.debug("🖥️  Showing main window...")
    window.show()

    logger.info("✅ Application initialized and ready")
    logger.info("🎤 Features available:")
    logger.info("   • Real-time speech-to-text transcription (Standalone STT Engine)")
    logger.info("   • Send to Focused Input: Click button → regular clicks focus windows → Ctrl+Click pastes")
    logger.info("   • Auto-send after recording stop (background mode)")
    logger.info("   • Direct text typing (no clipboard)")
    logger.info("   • Auto-submit with Enter or Ctrl+Enter")
    logger.info("   • ESC to cancel paste mode")
    logger.info("   • Cmd+Space hotkey for recording toggle")
    logger.info("=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
