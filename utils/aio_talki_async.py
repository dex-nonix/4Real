import asyncio
import logging
import sys

import qasync
import sounddevice as sd
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QTextEdit, QCheckBox, QLabel, QSplitter, QSizePolicy)
from pynput import keyboard
import mouse

from transformers import pipeline

from stt_engine import ColoredFormatter
from stt_engine.engine import AsyncSTTEngine
from stt_engine.audio_sources.microphone_source import MicrophoneSource

logger = logging.getLogger('TalkiV2Logger')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
if not logger.handlers:
    logger.addHandler(console_handler)
    console_handler.setFormatter(formatter)


MODE_OPTIONS = [
    ("🎙️ Live Streaming", ("live", float('inf'))),
    ("📦 Buffered (Unlimited)", ("buffered", float('inf'))),
    ("💾 Buffered (100MB ~47h)", ("buffered", 100)),
    ("💾 Buffered (500MB ~4.5h)", ("buffered", 500)),
    ("💾 Buffered (1GB ~9h)", ("buffered", 1024)),
    ("💾 Buffered (2GB ~18h)", ("buffered", 2048)),
    ("💾 Buffered (5GB ~100h)", ("buffered", 5120)),
    ("💾 Buffered (10GB ~200h)", ("buffered", 10240)),
]


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
        self.paste_keyboard_listener = None
        self.ctrl_pressed = False
        self.paste_mode_active = False
        self.pending_paste_text = None
        self._silent_stop = False
        self.global_mouse_hook_registered = False

        self.setWindowTitle("Async Real-Time Transcription V2 (Working)")
        self.setGeometry(100, 100, 600, 600)
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
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

        mode_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        for label, data in MODE_OPTIONS:
            self.mode_combo.addItem(label, data)
        for i in range(self.mode_combo.count()):
            data = self.mode_combo.itemData(i)
            if isinstance(data, tuple) and len(data) > 1 and data[1] == 100:
                self.mode_combo.setCurrentIndex(i)
                break
        mode_layout.addWidget(QLabel("Recording Mode:"))
        mode_layout.addWidget(self.mode_combo)
        self.layout.addLayout(mode_layout)

        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        languages = [
            ("Auto", None),
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
            ("Chinese", "zh"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
        ]
        for label, code in languages:
            self.lang_combo.addItem(label, code)
        lang_layout.addWidget(QLabel("Language:"))
        lang_layout.addWidget(self.lang_combo)
        self.layout.addLayout(lang_layout)

        translate_layout = QHBoxLayout()
        self.translate_combo = QComboBox()
        translate_options = [
            ("No Translation", None),
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
            ("Chinese", "zh"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
        ]
        for label, code in translate_options:
            self.translate_combo.addItem(label, code)
        translate_layout.addWidget(QLabel("Translate to:"))
        translate_layout.addWidget(self.translate_combo)
        self.layout.addLayout(translate_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.reload_button = QPushButton("Reload Engine")
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.reload_button)
        self.layout.addLayout(button_layout)

        self.text_area = QTextEdit()
        self.translated_area = QTextEdit()
        self.translated_area.setReadOnly(True)
        self.translated_area.setPlaceholderText("Translated text will appear here")
        splitter = QSplitter()
        splitter.addWidget(self.text_area)
        splitter.addWidget(self.translated_area)
        splitter.setSizes([400, 400])  # Equal sizes
        self.layout.addWidget(splitter)
        # Give the splitter the layout stretch so it expands while footer/status remain fixed
        try:
            idx = self.layout.indexOf(splitter)
            if idx != -1:
                self.layout.setStretch(idx, 1)
        except Exception:
            pass
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
        self.paste_status_label.setWordWrap(True)
        # Keep paste status compact and prevent vertical expansion
        self.paste_status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.paste_status_label.setMaximumHeight(40)
        paste_status_layout.addWidget(QLabel("Status:"));
        paste_status_layout.addWidget(self.paste_status_label);
        paste_status_layout.addStretch()
        self.layout.addLayout(paste_status_layout)
        self.status_label = QLabel("Initializing...")
        self.status_label.setWordWrap(True)
        # Keep status label compact and prevent vertical expansion
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.status_label.setMaximumHeight(40)
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        self.layout.addLayout(status_layout)
        self.layout.addStretch()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.reload_button.clicked.connect(self.reload_engine)
        self.clear_button.clicked.connect(self.clear_texts)
        self.send_button.clicked.connect(self.send_to_focused)

        logger.info("✅ CONSTRUCTOR: UI created. Deferring backend initialization.")

    async def finish_initialization(self):
        logger.info("🚀 FINISH_INIT: Starting backend initialization...")
        try:
            self.stt_engine = AsyncSTTEngine(
                model_size="tiny",
                language=self.lang_combo.currentData(),
                on_transcript=self.transcript_signal.emit,
                on_error=self.error_signal.emit,
                on_status=self.on_status_update
            )

            # Prepare translators cache (load on demand per target language)
            self.translators = {}
            # Map simple target language codes to Helsinki models (source assumed 'en')
            self.translation_model_map = {
                "de": "Helsinki-NLP/opus-mt-en-de",
                "es": "Helsinki-NLP/opus-mt-en-es",
                "fr": "Helsinki-NLP/opus-mt-en-fr",
                "it": "Helsinki-NLP/opus-mt-en-it",
                "pt": "Helsinki-NLP/opus-mt-en-pt",
                "ru": "Helsinki-NLP/opus-mt-en-ru",
                "zh": "Helsinki-NLP/opus-mt-en-zh",
                "ja": "Helsinki-NLP/opus-mt-en-ja",
                "ko": "Helsinki-NLP/opus-mt-en-ko",
                "en": None,  # no-op
            }
            self.status_label.setText("Setting up listeners...")

            self.keyboard_controller = keyboard.Controller()
            self.populate_microphones()
            try:
                self.setup_global_listeners()
            except Exception as e:
                logger.warning(f"⚠️ Global listeners failed (run as root for full features): {e}")

            self.status_label.setText("Ready.")
            self.paste_status_label.setText("🎯 Ready - Click 'Send to Focused Input' to begin");
            self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")
            self.start_button.setEnabled(True)
            self.mic_combo.setEnabled(True)
            self.mode_combo.setEnabled(True)
            self.lang_combo.setEnabled(True)
            self.translate_combo.setEnabled(True)
            self.reload_button.setEnabled(True)
            self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
            logger.info("✅ FINISH_INIT: Backend initialized successfully.")
        except Exception as e:
            logger.error(f"❌ FATAL: Backend initialization failed: {e}")
            self.status_label.setText(f"Error on startup: {e}")

    @qasync.asyncSlot()
    async def start_recording(self):
        device_index = self.mic_combo.currentData()
        if device_index is not None:
            # Create microphone source with selected device
            audio_source = MicrophoneSource(device_index=device_index)
            self.stt_engine.set_audio_source(audio_source)
            data = self.mode_combo.currentData()
            if data is not None:
                mode, buffer_mb = data
                self.stt_engine.configure_processing(mode, buffer_mb)
            else:
                self.stt_engine.configure_processing("buffered", 100)
            await self.stt_engine.start_transcription()
        else:
            logger.error("❌ No valid microphone device selected")

    

    def stop_recording(self):
        if self.stt_engine and self.stt_engine.is_task_running():
            logger.info("⏹️ Stop recording requested")
            self.status_label.setText("Stopping...")
            self.stop_button.setEnabled(False)  # Disable immediately for responsiveness
            asyncio.create_task(self.stt_engine.stop_transcription())

    @qasync.asyncSlot()
    async def reload_engine(self):
        logger.info("🔄 Reloading STT Engine...")
        self.status_label.setText("Reloading engine...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.reload_button.setEnabled(False)
        if self.stt_engine:
            await self.stt_engine.stop_transcription()
        self.stt_engine = AsyncSTTEngine(
            model_size="tiny",
            language=self.lang_combo.currentData(),
            on_transcript=self.transcript_signal.emit,
            on_error=self.error_signal.emit,
            on_status=self.on_status_update
        )
        self.status_label.setText("Engine reloaded.")
        self.start_button.setEnabled(True)
        self.reload_button.setEnabled(True)
        logger.info("✅ Engine reloaded successfully.")

    def on_status_update(self, msg):
        if msg == "Transcription started":
            self.status_label.setText("Recording...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        elif msg == "Transcription stopped":
            self.status_label.setText("Stopped.")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            if self._silent_stop:
                self._silent_stop = False
            else:
                self.handle_post_recording_actions()

    def handle_post_recording_actions(self):
        """Synchronous method that triggers the asynchronous handling."""
        if self.auto_send_checkbox.isChecked():
            current_text = self.text_area.toPlainText()
            if current_text:
                asyncio.create_task(self._async_handle_post_actions(current_text))

    async def _async_handle_post_actions(self, text):
        """Asynchronous handler for typing and submitting text."""
        target_lang = self.translate_combo.currentData()
        if target_lang:
            text = self.translate_text(text)
        await self._type_text_directly(text)
        if self.auto_submit_checkbox.isChecked():
            # A small delay before submitting can be more reliable
            await asyncio.sleep(0.1)
            self._send_keys(self.ctrl_enter_checkbox.isChecked())
        if self.clear_history_checkbox.isChecked():
            self.clear_text_signal.emit()


    def update_text_area(self, text):
        self.text_area.insertPlainText(text)
        self.text_area.ensureCursorVisible()
        # Update translated if enabled
        target = self.translate_combo.currentData()
        if target:
            full_text = self.text_area.toPlainText()
            translated = self.translate_text(full_text)
            self.translated_area.setPlainText(translated)
            self.translated_area.ensureCursorVisible()

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
        if self.stt_engine: asyncio.create_task(self.stt_engine.stop_transcription())
        if self.hotkey_listener: self.hotkey_listener.stop()
        event.accept()

    def on_audio_error(self, msg):
        logger.error(f"❌ Audio error received: {msg}");
        self.status_label.setText(f"Error: {msg}")
        self.start_button.setEnabled(True);
        self.stop_button.setEnabled(False)

    def clear_texts(self):
        self.text_area.clear()
        self.translated_area.clear()

    def on_language_changed(self):
        if self.stt_engine:
            lang = self.lang_combo.currentData()
            self.stt_engine.set_language(lang)
            lang_label = self.lang_combo.currentText()
            self.status_label.setText(f"Language set to: {lang_label}")
            logger.info(f"🌐 UI: Language changed to {lang_label} ({lang})")
            # Update translate combo to disable the same language
            for i in range(self.translate_combo.count()):
                item_data = self.translate_combo.itemData(i)
                item = self.translate_combo.model().item(i)
                if item_data == lang:
                    item.setEnabled(False)
                    if self.translate_combo.currentData() == lang:
                        self.translate_combo.setCurrentIndex(0)  # Set to No Translation
                else:
                    item.setEnabled(True)

    def translate_text(self, text):
        target = self.translate_combo.currentData()
        # No translation requested
        if not target:
            return text
        # Prevent translating into same language as STT
        stt_lang = self.lang_combo.currentData()
        if target == stt_lang:
            return text

        model_name = self.translation_model_map.get(target)
        if not model_name:
            logger.warning(f"No translation model configured for target '{target}'")
            return text

        # Load pipeline on demand and cache it
        translator = self.translators.get(target)
        if translator is None:
            try:
                self.status_label.setText(f"Loading translator for {target}...")
                translator = pipeline("translation", model=model_name)
                self.translators[target] = translator
                self.status_label.setText("Ready.")
            except Exception as e:
                logger.error(f"Failed to load translation model for {target}: {e}")
                self.status_label.setText(f"Translation load failed: {e}")
                return text

        try:
            result = translator(text, max_length=512)
            return result[0].get('translation_text', text)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def setup_global_listeners(self):
        try:
            hotkeys = {keyboard.Key.cmd, keyboard.Key.space};
            hotkeys_silent_stop = {keyboard.Key.cmd, keyboard.Key.esc}
            pressed_keys = set()

            def on_press(key):
                if key in hotkeys:
                    pressed_keys.add(key)
                    if pressed_keys == hotkeys:
                        QTimer.singleShot(0,
                                          self.start_recording if self.start_button.isEnabled() else self.stop_recording)
                if key in hotkeys_silent_stop:
                    pressed_keys.add(key)
                    if pressed_keys == hotkeys_silent_stop and self.stt_engine and self.stt_engine.is_task_running():
                        QTimer.singleShot(0, self.stop_recording_silent)

            def on_release(key):
                if key in hotkeys or key in hotkeys_silent_stop: pressed_keys.discard(key)

            self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release);
            self.hotkey_listener.start()

            if not self.global_mouse_hook_registered:
                mouse.on_button(self._mouse_button_callback)
                self.global_mouse_hook_registered = True

        except Exception as e:
            logger.error(f"❌ Failed to set up global listeners: {e}")
    
    def _mouse_button_callback(self, button, event_type):
        if event_type == 'down':
            logger.info(f"Mouse button pressed: {button}")
            if button == mouse.XButton1:
                logger.info("XButton1 (backward) detected")
                QTimer.singleShot(0, self._handle_backward_button_press)
            elif button == mouse.XButton2:
                logger.info("XButton2 (forward) detected")
                QTimer.singleShot(0, self._handle_forward_button_press)
            elif button == mouse.LEFT and self.paste_mode_active and self.ctrl_pressed:
                QTimer.singleShot(0, self._execute_paste_from_mouse_click)

    def _handle_backward_button_press(self):
        QTimer.singleShot(0, self.start_recording if self.start_button.isEnabled() else self.stop_recording)

    def _handle_forward_button_press(self):
        if self.stt_engine and self.stt_engine.is_task_running():
            QTimer.singleShot(0, self.stop_recording_silent)

    def _execute_paste_from_mouse_click(self):
        current_text = self.text_area.toPlainText()
        if current_text:
            target_lang = self.translate_combo.currentData()
            if target_lang:
                current_text = self.translate_text(current_text)
            self.pending_paste_text = current_text
            self._execute_paste()
        else:
            self._disable_paste_listeners()

    def stop_recording_silent(self):
        if self.stt_engine and self.stt_engine.is_task_running():
            logger.info("⏹️ Stop recording (silent) requested")
            self._silent_stop = True
            self.status_label.setText("Stopping...")
            self.stop_button.setEnabled(False)
            asyncio.create_task(self.stt_engine.stop_transcription())

    def send_to_focused(self):
        self.paste_mode_active = True;
        self._update_paste_status();
        QTimer.singleShot(200, self._enable_paste_listeners)

    def _enable_paste_listeners(self):
        try:
            self.paste_keyboard_listener = keyboard.Listener(on_press=self.on_paste_key_press,
                                                             on_release=self.on_paste_key_release);
            self.paste_keyboard_listener.start()
        except Exception as e:
            logger.error(f"❌ Failed to enable paste listeners: {e}");
            self._disable_paste_listeners()

    def _disable_paste_listeners(self):
        if self.paste_keyboard_listener: self.paste_keyboard_listener.stop(); self.paste_keyboard_listener = None
        self.paste_mode_active = False;
        self.pending_paste_text = None;
        self._update_paste_status()

    def on_paste_key_press(self, key):
        if key == keyboard.Key.esc: self._disable_paste_listeners(); return False
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r): self.ctrl_pressed = True

    def on_paste_key_release(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r): self.ctrl_pressed = False

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

    def _update_paste_status(self):
        if self.paste_mode_active:
            self.paste_status_label.setText("🎯 Paste Mode: Ctrl+Click pastes (ESC cancels)");
            self.paste_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.paste_status_label.setText("🎯 Ready - Click 'Send to Focused Input' to begin");
            self.paste_status_label.setStyleSheet("color: gray; font-weight: bold;")

    async def _type_text_directly(self, text):
        if not self.keyboard_controller: return
        try:
            for char in text:
                self.keyboard_controller.type(char)
                await asyncio.sleep(0.001)  # Correct, non-blocking sleep
        except Exception as e:
            logger.error(f"❌ Error typing text: {e}")

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
        self.translated_area.clear()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        window = MainWindow()
        window.show()
        loop.create_task(window.finish_initialization())
        with loop:
            loop.run_forever()
    except KeyboardInterrupt:
        logger.info("\nApplication interrupted by user.")
    except Exception as e:
        logger.critical(f"💥 Unhandled exception at top level: {e}")
    finally:
        logger.info("🏁 Application finished.")
