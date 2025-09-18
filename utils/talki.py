import sys
import threading
import queue
import numpy as np
import sounddevice as sd
import logging
import colorama
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QTextEdit, QCheckBox, QLabel)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from faster_whisper import WhisperModel
from pynput import keyboard, mouse

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
logger = logging.getLogger('TalkiLogger')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class AudioProcessor(QObject):
    """
    This version uses a simple, robust, time-based chunking method.
    The failed VAD logic has been completely removed.
    """
    transcript_update = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, model_size="tiny.en"):
        super().__init__()
        logger.info(f"🎯 Initializing AudioProcessor with model: {model_size}")
        try:
            logger.debug("🔄 Loading Whisper model...")
            self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            self.error_signal.emit(f"Failed to load Whisper model: {e}")
            return

        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None
        self.native_samplerate = None
        self.target_samplerate = 16000
        self.processing_thread = None
        logger.info("🎤 AudioProcessor initialized and ready")

    def start_recording(self, device_index):
        if self.is_recording:
            logger.warning("⚠️  Recording already in progress, ignoring start request")
            return

        logger.info(f"🎤 Starting recording on device {device_index}")
        try:
            logger.debug("🔍 Querying audio device information...")
            device_info = sd.query_devices(device_index, 'input')
            self.native_samplerate = int(device_info['default_samplerate'])
            logger.info(f"📊 Device sample rate: {self.native_samplerate}Hz")

            self.is_recording = True
            logger.debug("🔄 Creating audio input stream...")
            self.stream = sd.InputStream(
                samplerate=self.native_samplerate, channels=1, device=device_index,
                dtype="float32", callback=self._audio_callback
            )

            logger.debug("▶️  Starting audio stream...")
            self.stream.start()
            logger.debug("🧵 Starting processing thread...")
            self.processing_thread = threading.Thread(target=self._process_audio)
            self.processing_thread.start()

            logger.info("✅ Recording started successfully")
        except Exception as e:
            logger.error(f"❌ Error starting audio stream: {e}")
            self.error_signal.emit(f"Error starting audio stream: {e}")
            self.is_recording = False

    def stop_recording(self):
        if not self.is_recording:
            logger.debug("🔇 Recording not active, ignoring stop request")
            return

        logger.info("⏹️  Stopping recording...")
        self.is_recording = False

        logger.debug("📤 Sending stop signal to processing thread...")
        self.audio_queue.put(None)  # Sentinel to unblock the thread

        if self.stream:
            logger.debug("🔄 Stopping and closing audio stream...")
            self.stream.stop(ignore_errors=True)
            self.stream.close(ignore_errors=True)
            self.stream = None

        logger.info("✅ Recording stopped")

    def is_thread_alive(self):
        return self.processing_thread is not None and self.processing_thread.is_alive()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f"⚠️  Audio callback status: {status}")
            self.error_signal.emit(str(status))

        logger.debug(f"📡 Audio chunk received: {frames} frames")
        self.audio_queue.put(indata.copy())

    def _resample(self, audio_chunk):
        if self.native_samplerate == self.target_samplerate:
            return audio_chunk
        num_samples = audio_chunk.shape[0]
        resampled_num_samples = int(num_samples * self.target_samplerate / self.native_samplerate)
        original_indices = np.arange(num_samples)
        resampled_indices = np.linspace(0, num_samples - 1, resampled_num_samples)
        return np.interp(resampled_indices, original_indices, audio_chunk.flatten()).astype(np.float32)

    def _transcribe_chunk(self, audio_chunk):
        chunk_duration = len(audio_chunk) / self.target_samplerate
        logger.debug(f"🔊 Processing chunk: {chunk_duration:.2f}s duration")

        if len(audio_chunk) < self.target_samplerate * 0.2:
            logger.debug(f"🗑️  Chunk too small ({chunk_duration:.2f}s), skipping")
            return  # Ignore tiny fragments

        logger.debug("🎯 Starting transcription...")
        segments, _ = self.whisper_model.transcribe(audio_chunk, beam_size=5)
        text = "".join(s.text for s in segments)

        if text.strip():
            logger.info(f"📝 Transcribed: \"{text.strip()}\"")
            self.transcript_update.emit(text.strip() + " ")
        else:
            logger.debug("🤫 No speech detected in chunk")

    def _process_audio(self):
        logger.info("🧵 Audio processing thread started")
        audio_buffer = np.array([], dtype=np.float32)
        PROCESSING_INTERVAL_SAMPLES = int(self.target_samplerate * 2.0)
        logger.debug(f"⚙️  Processing interval: {PROCESSING_INTERVAL_SAMPLES} samples (2.0s)")

        while self.is_recording:
            try:
                raw_chunk = self.audio_queue.get(timeout=0.1)
                if raw_chunk is None:
                    logger.debug("🛑 Received stop signal, exiting processing loop")
                    break

                logger.debug("🔄 Processing raw audio chunk...")
                resampled_chunk = self._resample(raw_chunk)
                audio_buffer = np.concatenate([audio_buffer, resampled_chunk])

                buffer_duration = len(audio_buffer) / self.target_samplerate
                logger.debug(f"🔄 Audio buffer size: {buffer_duration:.2f}s")

                # Process every 2 seconds of audio for a live feel
                if len(audio_buffer) >= PROCESSING_INTERVAL_SAMPLES:
                    logger.info("🔥 Processing audio chunk (2s interval)")
                    self._transcribe_chunk(audio_buffer)
                    audio_buffer = np.array([], dtype=np.float32)  # Clear buffer
                    logger.debug("🧹 Audio buffer cleared")

            except queue.Empty:
                continue

        # After loop ends, process any leftover audio in the buffer
        if len(audio_buffer) > 0:
            leftover_duration = len(audio_buffer) / self.target_samplerate
            logger.info(f"🔚 Processing leftover audio: {leftover_duration:.2f}s")
            self._transcribe_chunk(audio_buffer)

        logger.info("🧵 Audio processing thread finished")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("🏠 Initializing MainWindow...")
        self.setWindowTitle("Real-Time Transcription")
        self.setGeometry(100, 100, 400, 500)
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
        self.ctrl_enter_checkbox = QCheckBox("Use Ctrl+Enter")
        self.clear_history_checkbox = QCheckBox("Clear after sending")
        checkbox_layout.addWidget(self.auto_submit_checkbox)
        checkbox_layout.addWidget(self.ctrl_enter_checkbox)
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

        # Backend
        self.audio_processor = AudioProcessor()
        self.audio_processor.transcript_update.connect(self.update_text_area)
        self.audio_processor.error_signal.connect(self.on_audio_error)

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
            logger.debug("🎯 Calling audio_processor.start_recording()")
            self.audio_processor.start_recording(device_index)
            if self.audio_processor.is_recording:
                logger.info("✅ Recording state confirmed - updating UI")
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.status_label.setText("Recording...")
            else:
                logger.warning("⚠️  Recording failed to start")
        else:
            logger.error("❌ No valid microphone device selected")
    
    def stop_recording(self):
        logger.info("⏹️  Stop recording button pressed")
        self.status_label.setText("Stopping...")
        self.stop_button.setEnabled(False)
        logger.debug("🎯 Calling audio_processor.stop_recording()")
        self.audio_processor.stop_recording()
        logger.debug("⏰ Starting thread check timer")
        self.thread_check_timer.start()

    def check_if_thread_is_done(self):
        logger.debug("⏰ Thread check timer tick")
        if not self.audio_processor.is_thread_alive():
            logger.info("✅ Processing thread finished - resetting UI")
            self.thread_check_timer.stop()
            self.start_button.setEnabled(True)
            self.status_label.setText("Stopped.")
        else:
            logger.debug("🧵 Processing thread still alive")

    def on_audio_error(self, msg):
        logger.error(f"❌ Audio error received: {msg}")
        self.status_label.setText(f"Error: {msg}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        logger.info("🔄 UI reset due to audio error")

    def update_text_area(self, text):
        logger.debug(f"📝 Updating text area with: \"{text.strip()}\"")
        self.text_area.insertPlainText(text)
        self.text_area.ensureCursorVisible()
        logger.debug("✅ Text area updated and cursor positioned")

    def send_to_focused(self):
        logger.info("📤 Send to focused input button pressed")
        text_to_paste = self.text_area.toPlainText()
        if text_to_paste:
            logger.info(f"📝 Storing text for direct paste: \"{text_to_paste[:50]}...\" ({len(text_to_paste)} chars)")

            # Store text for direct keyboard typing (no clipboard)
            self.pending_paste_text = text_to_paste
            self.paste_mode_active = True
            self._update_paste_status()

            # Enable paste mode for Ctrl+click
            logger.info("🎯 Paste mode enabled - click target input with Ctrl+mouse")

            # Small delay to let focus settle on target window
            QTimer.singleShot(200, self._enable_paste_listeners)

            if self.clear_history_checkbox.isChecked():
                logger.info("🧹 Clear history checkbox checked - clearing text area")
                self.text_area.clear()
            else:
                logger.debug("📝 Clear history not checked - keeping text")
        else:
            logger.warning("⚠️  No text to send - text area is empty")

    def _enable_paste_listeners(self):
        """Enable paste mode listeners for Ctrl+click"""
        try:
            logger.debug("🐭 Starting paste mode mouse listener...")
            self.paste_mouse_listener = mouse.Listener(on_click=self.on_paste_click)
            self.paste_mouse_listener.start()

            logger.debug("⌨️  Starting paste mode keyboard listener...")
            self.paste_keyboard_listener = keyboard.Listener(on_press=self.on_paste_key_press,
                                                           on_release=self.on_paste_key_release)
            self.paste_keyboard_listener.start()

            logger.debug("🚪 Starting paste mode escape listener...")
            self.paste_escape_listener = keyboard.Listener(on_press=self.on_paste_escape_press)
            self.paste_escape_listener.start()

            logger.info("✅ Paste mode active - Ctrl+Click to paste or ESC to cancel")
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

        if self.paste_escape_listener:
            self.paste_escape_listener.stop()
            self.paste_escape_listener = None

        self.paste_mode_active = False
        self.pending_paste_text = None
        self._update_paste_status()
        logger.info("✅ Paste mode disabled")

    def on_paste_click(self, x, y, button, pressed):
        """Handle Ctrl+click for paste operation"""
        if pressed and button == mouse.Button.left and self.ctrl_pressed and self.paste_mode_active:
            logger.info(f"🎯 Ctrl+Click detected at ({x}, {y}) - executing paste")
            self._execute_paste()

    def on_paste_key_press(self, key):
        """Handle Ctrl key press for paste mode"""
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            logger.debug("🔑 Paste mode: Ctrl key pressed")
            self.ctrl_pressed = True

    def on_paste_key_release(self, key):
        """Handle Ctrl key release for paste mode"""
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            logger.debug("🔓 Paste mode: Ctrl key released")
            self.ctrl_pressed = False

    def on_paste_escape_press(self, key):
        """Handle escape key press for paste mode"""
        if key == keyboard.Key.esc and self.paste_mode_active:
            logger.info("🚫 Paste mode: Escape key pressed - canceling")
            self._disable_paste_listeners()
            return False  # Stop the listener

    def _execute_paste(self):
        """Execute the paste operation by typing text directly"""
        logger.info("⌨️  Executing paste operation...")

        # Type the stored text directly (no clipboard)
        if self.pending_paste_text:
            logger.debug(f"📝 Typing {len(self.pending_paste_text)} characters directly...")
            self._type_text_directly(self.pending_paste_text)
            logger.info("✅ Paste operation completed")

            # Auto-submit if enabled
            if self.auto_submit_checkbox.isChecked():
                if self.ctrl_enter_checkbox.isChecked():
                    logger.info("⏎  Auto-submit enabled - scheduling Ctrl+Enter key press")
                    QTimer.singleShot(100, self._send_ctrl_enter)
                    logger.debug("⏰ Ctrl+Enter will be pressed in 100ms")
                else:
                    logger.info("⏎  Auto-submit enabled - scheduling Enter key press")
                    QTimer.singleShot(100, self._send_enter)
                    logger.debug("⏰ Enter will be pressed in 100ms")
            else:
                logger.debug("🚫 Auto-submit disabled")
        else:
            logger.warning("⚠️  No text to paste")

        # Disable listeners after paste
        self._disable_paste_listeners()

    def _update_paste_status(self):
        """Update the paste status indicator"""
        if self.paste_mode_active:
            self.paste_status_label.setText("🎯 Paste Mode Active - Ctrl+Click to paste (ESC to cancel)")
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



    def populate_microphones(self):
        try:
            logger.debug("🎤 Querying available audio devices...")
            device_count = 0
            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0:
                    logger.debug(f"📱 Found input device: {d['name']} (index: {i})")
                    self.mic_combo.addItem(d['name'], i)
                    device_count += 1
            logger.info(f"✅ Found {device_count} microphone devices")
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
        self.audio_processor.stop_recording()

        # Disable paste mode if active
        if self.paste_mode_active:
            logger.debug("🛑 Disabling paste mode during shutdown...")
            self._disable_paste_listeners()

        if self.hotkey_listener:
            logger.debug("🔥 Stopping hotkey listener...")
            self.hotkey_listener.stop()

        if self.audio_processor.is_thread_alive():
            logger.debug("🧵 Waiting for processing thread to finish...")
            self.audio_processor.processing_thread.join(timeout=0.5)
            if self.audio_processor.processing_thread.is_alive():
                logger.warning("⚠️  Processing thread did not finish within timeout")

        logger.info("✅ Application cleanup completed")
        event.accept()


def main():
    logger.info("🚀 Starting Talki Real-Time Transcription Application")
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
    logger.info("   • Real-time speech-to-text transcription")
    logger.info("   • Send to Focused Input: Click button → focus target → Ctrl+Click to paste")
    logger.info("   • Direct text typing (no clipboard)")
    logger.info("   • Auto-submit with Enter or Ctrl+Enter")
    logger.info("   • ESC to cancel paste mode")
    logger.info("   • Cmd+Space hotkey for recording toggle")
    logger.info("=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()