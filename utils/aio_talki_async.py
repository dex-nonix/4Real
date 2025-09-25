# FILE: Your main UI file.
# DELETE EVERYTHING AND REPLACE IT WITH THIS.

import asyncio
import logging
import sys

import qasync
import sounddevice as sd
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QTextEdit, QCheckBox, QLabel)
from pynput import keyboard, mouse

from stt_engine import ColoredFormatter
from stt_engine.engine import AsyncSTTEngine

logger = logging.getLogger('TalkiV2Logger')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
if not logger.handlers:
    logger.addHandler(console_handler)
    console_handler.setFormatter(formatter)


class MainWindow(QMainWindow):
    clear_text_signal = pyqtSignal()
    transcript_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logger.info("🏠 CONSTRUCTOR: Creating UI widgets ONLY.")
        self.stt_engine = None
        self.keyboard_controller = None
        self.hotkey_listener = None
        self.paste_mouse_listener = None
        self.paste_keyboard_listener = None
        self.ctrl_pressed = False
        self.paste_mode_active = False
        self.pending_paste_text = None

        self.setWindowTitle("Async Real-Time Transcription V2 (Working)")
        self.setGeometry(100, 100, 400, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.clear_text_signal.connect(self._clear_text_area_slot)
        self.transcript_signal.connect(self.update_text_area)
        self.error_signal.connect(self.on_audio_error)

        mic_layout = QHBoxLayout()
        self.mic_combo = QComboBox()
        self.mic_combo.addItem("Initializing devices...")
        self.mic_combo.setEnabled(False)
        mic_layout.addWidget(QLabel("Microphone:"))
        mic_layout.addWidget(self.mic_combo)
        self.layout.addLayout(mic_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        self.layout.addLayout(button_layout)

        self.text_area = QTextEdit()
        self.layout.addWidget(self.text_area)
        action_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.send_button = QPushButton("Send to Focused Input")
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.send_button)
        self.layout.addLayout(action_layout)
        checkbox_layout = QHBoxLayout()
        self.auto_submit_checkbox = QCheckBox("Auto-submit (Enter)");
        self.auto_submit_checkbox.setChecked(True)
        self.ctrl_enter_checkbox = QCheckBox("Use Ctrl+Enter")
        self.auto_send_checkbox = QCheckBox("Auto-send after stop");
        self.auto_send_checkbox.setChecked(True)
        self.clear_history_checkbox = QCheckBox("Clear after sending");
        self.clear_history_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.auto_submit_checkbox);
        checkbox_layout.addWidget(self.ctrl_enter_checkbox)
        checkbox_layout.addWidget(self.auto_send_checkbox);
        checkbox_layout.addWidget(self.clear_history_checkbox)
        self.layout.addLayout(checkbox_layout)
        paste_status_layout = QHBoxLayout()
        self.paste_status_label = QLabel("🎯 Initializing...");
        self.paste_status_label.setStyleSheet("color: gray;")
        paste_status_layout.addWidget(QLabel("Status:"));
        paste_status_layout.addWidget(self.paste_status_label);
        paste_status_layout.addStretch()
        self.layout.addLayout(paste_status_layout)
        self.status_label = QLabel("Initializing...")
        self.layout.addWidget(self.status_label)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.clear_button.clicked.connect(self.text_area.clear)
        self.send_button.clicked.connect(self.send_to_focused)

        logger.info("✅ CONSTRUCTOR: UI created. Deferring backend initialization.")
        QTimer.singleShot(50, self.finish_initialization)

    def finish_initialization(self):
        logger.info("🚀 FINISH_INIT: Starting backend initialization...")
        try:
            self.stt_engine = AsyncSTTEngine(
                model_size="tiny.en",
                on_transcript=self.transcript_signal.emit,
                on_error=self.error_signal.emit,
                on_status=self.on_status_update
            )

            self.keyboard_controller = keyboard.Controller()
            self.populate_microphones()
            self.setup_hotkeys()

            self.status_label.setText("Ready.")
            self.paste_status_label.setText("🎯 Ready - Click 'Send to Focused Input' to begin");
            self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")
            self.start_button.setEnabled(True)
            self.mic_combo.setEnabled(True)
            logger.info("✅ FINISH_INIT: Backend initialized successfully.")
        except Exception as e:
            logger.error(f"❌ FATAL: Backend initialization failed: {e}")
            self.status_label.setText(f"Error on startup: {e}")

    @qasync.asyncSlot()
    async def start_recording(self):
        device_index = self.mic_combo.currentData()
        if device_index is not None:
            await self.stt_engine.start_recording(device_index)
        else:
            logger.error("❌ No valid microphone device selected")

    def stop_recording(self):
        if self.stt_engine and self.stt_engine.is_recording:
            logger.info("⏹️ Stop recording requested")
            self.status_label.setText("Stopping...")
            self.stop_button.setEnabled(False)  # Disable immediately for responsiveness
            asyncio.create_task(self.stt_engine.stop_recording())

    def on_status_update(self, msg):
        if msg == "Recording started":
            self.status_label.setText("Recording...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        elif msg == "Recording stopped":
            self.status_label.setText("Stopped.")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.handle_post_recording_actions()

    # =========================================================================
    # FIX: Call the new async handler to deal with the async typing method.
    # =========================================================================
    def handle_post_recording_actions(self):
        """Synchronous method that triggers the asynchronous handling."""
        if self.auto_send_checkbox.isChecked():
            current_text = self.text_area.toPlainText()
            if current_text:
                asyncio.create_task(self._async_handle_post_actions(current_text))

    async def _async_handle_post_actions(self, text):
        """Asynchronous handler for typing and submitting text."""
        await self._type_text_directly(text)
        if self.auto_submit_checkbox.isChecked():
            # A small delay before submitting can be more reliable
            await asyncio.sleep(0.1)
            self._send_keys(self.ctrl_enter_checkbox.isChecked())
        if self.clear_history_checkbox.isChecked():
            self.clear_text_signal.emit()

    # =========================================================================

    def update_text_area(self, text):
        self.text_area.insertPlainText(text)
        self.text_area.ensureCursorVisible()

    def populate_microphones(self):
        self.mic_combo.clear()
        try:
            devices = sd.query_devices()
            input_devices = [(i, d['name']) for i, d in enumerate(devices) if d['max_input_channels'] > 0]
            if not input_devices:
                self.mic_combo.addItem("No input devices found", None);
                return
            for i, name in input_devices:
                self.mic_combo.addItem(name, i)
            default_idx = sd.default.device['input']
            if default_idx != -1:
                for i in range(self.mic_combo.count()):
                    if self.mic_combo.itemData(i) == default_idx:
                        self.mic_combo.setCurrentIndex(i);
                        break
        except Exception as e:
            logger.error(f"❌ Could not list audio devices: {e}");
            self.mic_combo.addItem("Error listing devices", None)

    def closeEvent(self, event):
        logger.info("🔄 Application closing...")
        if self.stt_engine: asyncio.create_task(self.stt_engine.stop_recording())
        if self.hotkey_listener: self.hotkey_listener.stop()
        event.accept()

    def on_audio_error(self, msg):
        logger.error(f"❌ Audio error received: {msg}");
        self.status_label.setText(f"Error: {msg}")
        self.start_button.setEnabled(True);
        self.stop_button.setEnabled(False)

    def setup_hotkeys(self):
        try:
            hotkeys = {keyboard.Key.cmd, keyboard.Key.space};
            pressed_keys = set()

            def on_press(key):
                if key in hotkeys:
                    pressed_keys.add(key)
                    if pressed_keys == hotkeys:
                        QTimer.singleShot(0,
                                          self.start_recording if self.start_button.isEnabled() else self.stop_recording)

            def on_release(key):
                if key in hotkeys: pressed_keys.discard(key)

            self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release);
            self.hotkey_listener.start()
        except Exception as e:
            logger.error(f"❌ Failed to set up hotkeys: {e}")

    def send_to_focused(self):
        self.paste_mode_active = True;
        self._update_paste_status();
        QTimer.singleShot(200, self._enable_paste_listeners)

    def _enable_paste_listeners(self):
        try:
            self.paste_mouse_listener = mouse.Listener(on_click=self.on_paste_click);
            self.paste_mouse_listener.start()
            self.paste_keyboard_listener = keyboard.Listener(on_press=self.on_paste_key_press,
                                                             on_release=self.on_paste_key_release);
            self.paste_keyboard_listener.start()
        except Exception as e:
            logger.error(f"❌ Failed to enable paste listeners: {e}");
            self._disable_paste_listeners()

    def _disable_paste_listeners(self):
        if self.paste_mouse_listener: self.paste_mouse_listener.stop(); self.paste_mouse_listener = None
        if self.paste_keyboard_listener: self.paste_keyboard_listener.stop(); self.paste_keyboard_listener = None
        self.paste_mode_active = False;
        self.pending_paste_text = None;
        self._update_paste_status()

    def on_paste_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left and self.paste_mode_active and self.ctrl_pressed:
            current_text = self.text_area.toPlainText()
            if current_text:
                self.pending_paste_text = current_text;
                self._execute_paste()
            else:
                self._disable_paste_listeners()

    def on_paste_key_press(self, key):
        if key == keyboard.Key.esc: self._disable_paste_listeners(); return False
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r): self.ctrl_pressed = True

    def on_paste_key_release(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r): self.ctrl_pressed = False

    # =========================================================================
    # FIX: _execute_paste now calls the new async handler.
    # =========================================================================
    def _execute_paste(self):
        if self.pending_paste_text:
            asyncio.create_task(self._async_execute_paste(self.pending_paste_text))
        self._disable_paste_listeners()

    async def _async_execute_paste(self, text):
        await self._type_text_directly(text)
        if self.clear_history_checkbox.isChecked(): self.clear_text_signal.emit()
        if self.auto_submit_checkbox.isChecked():
            await asyncio.sleep(0.1)
            self._send_keys(self.ctrl_enter_checkbox.isChecked())

    # =========================================================================

    def _update_paste_status(self):
        if self.paste_mode_active:
            self.paste_status_label.setText("🎯 Paste Mode: Ctrl+Click pastes (ESC cancels)");
            self.paste_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.paste_status_label.setText("🎯 Ready - Click 'Send to Focused Input' to begin");
            self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")

    # =========================================================================
    # FIX: The method is now `async def` and correctly `await`s the sleep.
    # This completely resolves the RuntimeWarning.
    # =========================================================================
    async def _type_text_directly(self, text):
        if not self.keyboard_controller: return
        try:
            for char in text:
                self.keyboard_controller.type(char)
                await asyncio.sleep(0.001)  # Correct, non-blocking sleep
        except Exception as e:
            logger.error(f"❌ Error typing text: {e}")

    # =========================================================================

    def _send_keys(self, use_ctrl_enter):
        if use_ctrl_enter:
            self._send_ctrl_enter()
        else:
            self._send_enter()

    def _send_enter(self):
        if self.keyboard_controller: self.keyboard_controller.tap(keyboard.Key.enter)

    def _send_ctrl_enter(self):
        if self.keyboard_controller:
            with self.keyboard_controller.pressed(keyboard.Key.ctrl): self.keyboard_controller.tap(keyboard.Key.enter)

    def _clear_text_area_slot(self):
        self.text_area.clear()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        window = MainWindow()
        window.show()
        with loop:
            loop.run_forever()
    except KeyboardInterrupt:
        logger.info("\nApplication interrupted by user.")
    except Exception as e:
        logger.critical(f"💥 Unhandled exception at top level: {e}")
    finally:
        logger.info("🏁 Application finished.")
