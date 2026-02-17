import asyncio

import sounddevice as sd

from .. import logger
from .audio_source import AudioSource


class MicrophoneSource(AudioSource):
    """An AudioSource that captures audio from a microphone."""

    def __init__(self, device_index: int, samplerate: int = 16000):
        super().__init__()
        self.device_index = device_index
        self.samplerate = samplerate
        self.stream = None
        self.loop = asyncio.get_event_loop()

    def _audio_callback(self, indata, frames, time, status):
        """This runs in a separate thread and safely puts audio data into the asyncio queue."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.loop.call_soon_threadsafe(self._queue.put_nowait, indata.copy())

    async def start(self):
        if self._is_active:
            logger.warning("Microphone source is already active.")
            return

        logger.info(f"🎤 Starting microphone source on device {self.device_index}")
        self._is_active = True
        try:
            device_info = sd.query_devices(self.device_index, 'input')
            logger.info(f"📊 Device: {device_info['name']}, Sample Rate: {self.samplerate}Hz")

            self.stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=1,
                device=self.device_index,
                dtype="float32",
                callback=self._audio_callback
            )
            self.stream.start()
            logger.info("✅ Microphone source started successfully.")
        except Exception as e:
            logger.error(f"❌ Error starting microphone stream: {e}")
            self._is_active = False
            raise

    async def stop(self):
        if not self._is_active:
            return

        logger.info("⏹️ Stopping microphone source...")
        self._is_active = False
        if self.stream:
            self.stream.stop(ignore_errors=True)
            self.stream.close(ignore_errors=True)
            self.stream = None

        # Clear the queue and signal the end of the stream
        while not self._queue.empty():
            self._queue.get_nowait()
        await self._queue.put(None)
        logger.info("✅ Microphone source stopped.")
