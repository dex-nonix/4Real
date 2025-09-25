import asyncio

import librosa
import numpy as np

from .audio_source import AudioSource


class FileSource(AudioSource):
    """
    An AudioSource that reads from an audio file and streams it in chunks,
    simulating a real-time feed.
    """

    def __init__(self, file_path: str, samplerate: int = 16000, chunk_seconds: float = 2.0):
        """
        Initializes the FileSource.

        Args:
            file_path (str): Path to the audio file.
            samplerate (int): The target sample rate to stream at (Whisper requires 16000).
            chunk_seconds (float): The duration of each audio chunk to stream.
        """
        super().__init__()
        self.file_path = file_path
        self.samplerate = samplerate
        self.chunk_size = int(samplerate * chunk_seconds)
        self._processing_task = None
        self.loop = asyncio.get_event_loop()

    async def _stream_file(self):
        """The background task that loads the file and puts chunks into the queue."""
        try:
            logger.info(f"🎧 Loading audio file: {self.file_path}")
            # Use a thread for the blocking I/O and processing of librosa
            audio, _ = await self.loop.run_in_executor(
                None,  # Use default thread pool
                lambda: librosa.load(self.file_path, sr=self.samplerate, mono=True)
            )
            audio = audio.astype(np.float32)

            logger.info(f"▶️ File loaded. Streaming {len(audio) / self.samplerate:.2f}s of audio...")
            for i in range(0, len(audio), self.chunk_size):
                if not self._is_active:
                    logger.info("Streaming cancelled by stop signal.")
                    break

                chunk = audio[i:i + self.chunk_size]
                await self._queue.put(chunk)

                # Simulate a real-time delay corresponding to the chunk's duration
                await asyncio.sleep(len(chunk) / self.samplerate)

        except asyncio.CancelledError:
            logger.info("File streaming task was cancelled.")
        except Exception as e:
            logger.error(f"❌ Error processing file source: {e}")
        finally:
            logger.info("✅ File streaming finished.")
            # Signal the end of the stream by putting None in the queue
            await self._queue.put(None)
            self._is_active = False

    async def start(self):
        """Starts the file streaming process in a background task."""
        if self._is_active:
            logger.warning("File source is already active.")
            return

        logger.info(f"🎤 Starting file source for: {self.file_path}")
        self._is_active = True
        self._processing_task = self.loop.create_task(self._stream_file())

    async def stop(self):
        """Stops the file streaming task."""
        if not self._is_active:
            return

        logger.info("⏹️ Stopping file source...")
        self._is_active = False
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()

        # Ensure a final None is sent if the queue is empty during a premature stop
        if self._queue.empty():
            await self._queue.put(None)

        logger.info("✅ File source stopped.")
