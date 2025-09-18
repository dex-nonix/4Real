import sys
import threading
import queue
import time
import pyperclip
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QTextEdit, QCheckBox, QLabel)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from faster_whisper import WhisperModel
from pynput import keyboard, mouse


class AudioProcessor(QObject):
    """
    This version uses a simple, robust, time-based chunking method.
    The failed VAD logic has been completely removed.
    """
    transcript_update = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, model_size="tiny.en"):
        super().__init__()
        try:
            self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        except Exception as e:
            self.error_signal.emit(f"Failed to load Whisper model: {e}")
            return

        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None
        self.native_samplerate = None
        self.target_samplerate = 16000
        self.processing_thread = None

    def start_recording(self, device_index):
        if self.is_recording: return
        try:
            device_info = sd.query_devices(device_index, 'input')
            self.native_samplerate = int(device_info['default_samplerate'])
            self.is_recording = True
            self.stream = sd.InputStream(
                samplerate=self.native_samplerate, channels=1, device=device_index,
                dtype="float32", callback=self._audio_callback
            )
            self.stream.start()
            self.processing_thread = threading.Thread(target=self._process_audio)
            self.processing_thread.start()
        except Exception as e:
            self.error_signal.emit(f"Error starting audio stream: {e}")
            self.is_recording = False

    def stop_recording(self):
        if not self.is_recording: return
        self.is_recording = False
        self.audio_queue.put(None)  # Sentinel to unblock the thread
        if self.stream:
            self.stream.stop(ignore_errors=True)
            self.stream.close(ignore_errors=True)
            self.stream = None

    def is_thread_alive(self):
        return self.processing_thread is not None and self.processing_thread.is_alive()

    def _audio_callback(self, indata, frames, time, status):
        if status: self.error_signal.emit(str(status))
        self.audio_queue.put(indata.copy())

    def _resample(self, audio_chunk):
        if self.native_samplerate == self.target_samplerate: return audio_chunk
        num_samples = audio_chunk.shape[0]
        resampled_num_samples = int(num_samples * self.target_samplerate / self.native_samplerate)
        original_indices = np.arange(num_samples)
        resampled_indices = np.linspace(0, num_samples - 1, resampled_num_samples)
        return np.interp(resampled_indices, original_indices, audio_chunk.flatten()).astype(np.float32)

    def _transcribe_chunk(self, audio_chunk):
        if len(audio_chunk) < self.target_samplerate * 0.2: return  # Ignore tiny fragments
        segments, _ = self.whisper_model.transcribe(audio_chunk, beam_size=5)
        text = "".join(s.text for s in segments)
        if text.strip():
            self.transcript_update.emit(text.strip() + " ")

    def _process_audio(self):
        audio_buffer = np.array([], dtype=np.float32)

        while self.is_recording:
            try:
                raw_chunk = self.audio_queue.get(timeout=0.1)
                if raw_chunk is None: break

                resampled_chunk = self._resample(raw_chunk)
                audio_buffer = np.concatenate([audio_buffer, resampled_chunk])

                # Process every 2 seconds of audio for a live feel
                PROCESSING_INTERVAL_SAMPLES = int(self.target_samplerate * 2.0)
                if len(audio_buffer) >= PROCESSING_INTERVAL_SAMPLES:
                    self._transcribe_chunk(audio_buffer)
                    audio_buffer = np.array([], dtype=np.float32)  # Clear buffer

            except queue.Empty:
                continue

        # After loop ends, process any leftover audio in the buffer
        self._transcribe_chunk(audio_buffer)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Transcription")
        self.setGeometry(100, 100, 400, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

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
        self.clear_history_checkbox = QCheckBox("Clear after sending")
        checkbox_layout.addWidget(self.auto_submit_checkbox)
        checkbox_layout.addWidget(self.clear_history_checkbox)
        self.layout.addLayout(checkbox_layout)

        self.global_listener_checkbox = QCheckBox("Enable Global 'Ctrl+Click' to Paste")
        self.global_listener_checkbox.stateChanged.connect(self.toggle_global_listener)
        self.layout.addWidget(self.global_listener_checkbox)

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
        self.mouse_listener, self.keyboard_listener_for_ctrl, self.hotkey_listener = None, None, None
        self.ctrl_pressed = False

    def start_recording(self):
        device_index = self.mic_combo.currentData()
        if device_index is not None:
            self.status_label.setText("Starting...")
            self.audio_processor.start_recording(device_index)
            if self.audio_processor.is_recording:
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.status_label.setText("Recording...")

    def stop_recording(self):
        self.status_label.setText("Stopping...")
        self.stop_button.setEnabled(False)
        self.audio_processor.stop_recording()
        self.thread_check_timer.start()

    def check_if_thread_is_done(self):
        if not self.audio_processor.is_thread_alive():
            self.thread_check_timer.stop()
            self.start_button.setEnabled(True)
            self.status_label.setText("Stopped.")

    def on_audio_error(self, msg):
        self.status_label.setText(f"Error: {msg}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_text_area(self, text):
        self.text_area.insertPlainText(text)
        self.text_area.ensureCursorVisible()

    def send_to_focused(self):
        if text_to_paste := self.text_area.toPlainText():
            pyperclip.copy(text_to_paste)
            QTimer.singleShot(100, self._paste_and_enter)
            if self.clear_history_checkbox.isChecked():
                self.text_area.clear()

    def _paste_and_enter(self):
        self.keyboard_controller.press(keyboard.Key.ctrl)
        self.keyboard_controller.press('v')
        self.keyboard_controller.release('v')
        self.keyboard_controller.release(keyboard.Key.ctrl)
        if self.auto_submit_checkbox.isChecked():
            QTimer.singleShot(50, lambda: self.keyboard_controller.tap(keyboard.Key.enter))

    def toggle_global_listener(self, state):
        try:
            is_checked = (state == 2)
            if is_checked and not (self.mouse_listener and self.mouse_listener.is_alive()):
                self.mouse_listener = mouse.Listener(on_click=self.on_global_click)
                self.mouse_listener.start()
                self.keyboard_listener_for_ctrl = keyboard.Listener(on_press=self.on_key_press,
                                                                    on_release=self.on_key_release)
                self.keyboard_listener_for_ctrl.start()
            elif not is_checked:
                if self.mouse_listener: self.mouse_listener.stop()
                if self.keyboard_listener_for_ctrl: self.keyboard_listener_for_ctrl.stop()
        except Exception as e:
            self.status_label.setText(f"Listener error: {e}")

    def on_key_press(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r): self.ctrl_pressed = True

    def on_key_release(self, key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r): self.ctrl_pressed = False

    def on_global_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left and self.ctrl_pressed:
            QTimer.singleShot(0, self.send_to_focused)

    def populate_microphones(self):
        try:
            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0: self.mic_combo.addItem(d['name'], i)
        except Exception as e:
            self.status_label.setText(f"Could not list audio devices: {e}")

    def setup_hotkeys(self):
        hotkeys = {keyboard.Key.cmd, keyboard.Key.space}
        pressed_keys = set()

        def on_press(key):
            if key in hotkeys:
                pressed_keys.add(key)
                if pressed_keys == hotkeys:
                    action = self.start_recording if self.start_button.isEnabled() else self.stop_recording
                    QTimer.singleShot(0, action)

        def on_release(key):
            pressed_keys.discard(key)

        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()

    def closeEvent(self, event):
        self.audio_processor.stop_recording()
        if self.mouse_listener: self.mouse_listener.stop()
        if self.keyboard_listener_for_ctrl: self.keyboard_listener_for_ctrl.stop()
        if self.hotkey_listener: self.hotkey_listener.stop()
        if self.audio_processor.is_thread_alive():
            self.audio_processor.processing_thread.join(timeout=0.5)
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setup_hotkeys()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()