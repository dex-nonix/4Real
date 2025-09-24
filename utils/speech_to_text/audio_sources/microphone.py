"""
Microphone audio source implementation using sounddevice.
"""

import logging
import threading
import queue
import numpy as np

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    sd = None
    SOUNDDEVICE_AVAILABLE = False

from .base import AudioSource


class MicrophoneSource(AudioSource):
    """Audio source for microphone input using sounddevice."""

    def __init__(self, device_index: int, sample_rate: int = 16000):
        super().__init__()
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.native_rate = None  # Store native sample rate for engine access
        self.stream = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start microphone recording."""
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError("sounddevice not available")

        if self._is_active:
            logging.warning("Microphone source already recording")
            return

        try:
            self._is_active = True
            self._stop_event.clear()

            # Clear any leftover data
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break

            def audio_callback(indata, frames, time_info, status):
                """Audio callback - runs in sounddevice thread."""
                if status:
                    logging.warning(f"Audio callback status: {status}")

                if self._is_active and not self._stop_event.is_set():
                    try:
                        # Put audio data directly in queue (matches original AudioProcessor)
                        self.audio_queue.put(indata.copy(), timeout=0.01)
                    except queue.Full:
                        # Drop audio chunk if queue is full
                        pass

            device_info = sd.query_devices(self.device_index, 'input')
            self.native_rate = int(device_info['default_samplerate'])
            native_rate = self.native_rate

            self.stream = sd.InputStream(
                samplerate=native_rate,
                channels=1,
                device=self.device_index,
                dtype="float32",
                callback=audio_callback
                # No blocksize specified - matches v1 exactly
            )
            self.stream.start()

            logging.info(f"Microphone recording started on device {self.device_index}")

        except Exception as e:
            self._is_active = False
            raise RuntimeError(f"Failed to start microphone recording: {e}")

    def stop(self) -> None:
        """Stop microphone recording with clean shutdown."""
        if not self._is_active:
            return

        logging.info("Stopping microphone recording")
        self._is_active = False
        self._stop_event.set()

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logging.warning(f"Error stopping audio stream: {e}")
            finally:
                self.stream = None

        # Drain audio queue
        try:
            drained_count = 0
            while not self.audio_queue.empty() and drained_count < 200:
                self.audio_queue.get_nowait()
                drained_count += 1
            if drained_count > 0:
                logging.debug(f"Drained {drained_count} audio chunks from queue")
        except queue.Empty:
            pass

        logging.info("Microphone recording stopped cleanly")
