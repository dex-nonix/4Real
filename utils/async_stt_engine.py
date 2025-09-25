import asyncio
import logging
import sys
from abc import ABC, abstractmethod

import colorama
import librosa
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# Initialize colorama for colored console output
colorama.init()


# --- 1. LOGGING SETUP ---
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


log_level = logging.INFO
logger = logging.getLogger('AsyncSTTLogger')
logger.setLevel(log_level)
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(console_handler)


# --- 2. AUDIO SOURCE ABSTRACTION ---
class AudioSource(ABC):
    """
    Abstract base class for providing audio chunks.
    Defines the interface for different audio input methods like microphones or files.
    """

    def __init__(self):
        self._queue = asyncio.Queue()
        self._is_active = False

    @property
    def is_active(self) -> bool:
        """Returns True if the source is currently running."""
        return self._is_active

    async def read(self) -> np.ndarray | None:
        """
        Asynchronously reads the next available audio chunk from the source.
        Returns a NumPy array, or None if the stream is finished.
        """
        return await self._queue.get()

    @abstractmethod
    async def start(self):
        """Starts the audio source, which should begin populating the internal queue."""
        pass

    @abstractmethod
    async def stop(self):
        """Stops the audio source and signals the end by putting None into the queue."""
        pass


# Assuming AudioSource and logger are defined in the same file as per the previous script.

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


# --- 3. REFACTORED ASYNCHRONOUS STT ENGINE ---
class AsyncSTTEngine:
    """
    Standalone Asynchronous Speech-to-Text Engine.
    This engine is now agnostic to the audio input source.
    """

    def __init__(self, audio_source: AudioSource, model_size="tiny.en", device="cpu", compute_type="int8",
                 on_transcript=None, on_error=None, on_status=None):
        self.audio_source = audio_source
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.on_transcript = on_transcript or (lambda text: None)
        self.on_error = on_error or (lambda msg: None)
        self.on_status = on_status or (lambda msg: None)
        self.is_initialized = False
        self.whisper_model = None
        self.processing_task = None
        self.loop = asyncio.get_event_loop()
        logger.info("🎤 Async STT Engine initialized and ready")

    async def initialize_model(self):
        """Asynchronously loads the Whisper model in a background thread."""
        if self.is_initialized:
            return

        logger.info(f"🎯 Initializing Async STT Engine with model: {self.model_size}")
        try:
            self.whisper_model = await asyncio.to_thread(
                WhisperModel, self.model_size, device=self.device, compute_type=self.compute_type
            )
            self.is_initialized = True
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            self.on_error(f"Failed to load Whisper model: {e}")
            raise

    async def start_transcription(self):
        """Starts the transcription process."""
        await self.initialize_model()

        await self.audio_source.start()

        self.processing_task = self.loop.create_task(self._process_audio())
        logger.info("✅ Transcription engine started.")
        self.on_status("Transcription started")

    async def stop_transcription(self):
        """Stops the transcription process."""
        logger.info("⏹️ Stopping transcription engine...")

        await self.audio_source.stop()

        if self.processing_task:
            try:
                await asyncio.wait_for(self.processing_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout waiting for processing task. Forcing cancellation.")
                self.processing_task.cancel()

        logger.info("✅ Transcription engine stopped.")
        self.on_status("Transcription stopped")

    def is_task_running(self):
        """Checks if the processing task is still running."""
        return self.processing_task is not None and not self.processing_task.done()

    async def _transcribe_chunk(self, audio_chunk: np.ndarray):
        """Transcribes an audio chunk using Whisper in a non-blocking way."""
        target_samplerate = 16000
        chunk_duration = len(audio_chunk) / target_samplerate
        logger.debug(f"🔊 Processing chunk: {chunk_duration:.2f}s duration")

        if len(audio_chunk) < target_samplerate * 0.2:
            logger.debug(f"🗑️ Chunk too small ({chunk_duration:.2f}s), skipping")
            return

        segments, _ = await asyncio.to_thread(self.whisper_model.transcribe, audio_chunk, beam_size=5)
        text = "".join(s.text for s in segments)

        if text.strip():
            logger.info(f"📝 Transcribed: \"{text.strip()}\"")
            self.on_transcript(text.strip() + " ")

    async def _process_audio(self):
        """Asynchronous audio processing task that reads from the source and transcribes."""
        logger.info("🧵 Audio processing task started")
        audio_buffer = np.array([], dtype=np.float32)
        PROCESSING_INTERVAL_SAMPLES = int(16000 * 2.0)  # Process in 2-second chunks

        while True:
            try:
                audio_chunk = await self.audio_source.read()

                if audio_chunk is None:  # End of stream signal
                    logger.debug("🛑 Received end of stream signal.")
                    break

                # --- THIS IS THE FIX ---
                # Ensure the incoming chunk is flattened to 1D before concatenation,
                # just like in the original working code.
                audio_buffer = np.concatenate([audio_buffer, audio_chunk.flatten()])

                if len(audio_buffer) >= PROCESSING_INTERVAL_SAMPLES:
                    logger.info("🔥 Processing accumulated audio chunk")
                    await self._transcribe_chunk(audio_buffer)
                    audio_buffer = np.array([], dtype=np.float32)

            except asyncio.CancelledError:
                logger.info("Processing task cancelled.")
                break
            except Exception as e:
                logger.error(f"❌ Error in audio processing task: {e}")
                self.on_error(f"Processing error: {e}")
                # Stop processing on error to avoid spamming logs
                break

        # Process any leftover audio
        if len(audio_buffer) > 0:
            logger.info(f"🔚 Processing {len(audio_buffer) / 16000:.2f}s of leftover audio.")
            await self._transcribe_chunk(audio_buffer)

        logger.info("🧵 Audio processing task finished.")


# --- 4. EXAMPLE USAGE ---
async def main():
    stt_engine = None  # Define in outer scope for the finally block

    def handle_transcript(text):
        print(f"{text}", end="", flush=True)

    def handle_error(error):
        print(f"\n\nERROR: {error}\n", file=sys.stderr)

    def handle_status(status):
        print(f"\nSTATUS: {status}\n", flush=True)

    try:
        # 1. Select audio device
        device_index = sd.default.device['input']

        # 2. Create the desired AudioSource instance
        microphone_source = MicrophoneSource(device_index=device_index)

        # 3. Initialize the engine with the chosen source
        stt_engine = AsyncSTTEngine(
            audio_source=microphone_source,
            model_size="tiny.en",
            on_transcript=handle_transcript,
            on_error=handle_error,
            on_status=handle_status
        )

        # 4. Start the transcription
        await stt_engine.start_transcription()

        print("\n🎤 Say something! Press Ctrl+C to stop. 🎤\n")
        while stt_engine.is_task_running():
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping via KeyboardInterrupt...")
    except Exception as e:
        handle_error(f"An unhandled error occurred in main: {e}")
    finally:
        if stt_engine and stt_engine.is_task_running():
            await stt_engine.stop_transcription()
        print("\n\nApplication finished.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting application.")
