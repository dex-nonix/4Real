"""
File audio source implementation for processing audio files.
"""

import numpy as np
import logging
import librosa
from .base import AudioSource


class FileSource(AudioSource):
    """Audio source for file input using librosa."""

    def __init__(self, file_path: str, chunk_duration_seconds: float = 2.0, target_sample_rate: int = 16000):
        super().__init__()
        self._file_path = file_path
        self.chunk_duration_seconds = chunk_duration_seconds
        self.target_sample_rate = target_sample_rate
        self._audio_data = np.array([], dtype=np.float32)
        self._chunk_index = 0
        self._total_chunks = 0

    def start(self) -> None:
        """Load audio file and prepare chunks."""

        try:
            # Load audio file
            logging.info(f"Loading audio file: {self.file_path}")
            audio_data, sample_rate = librosa.load(self.file_path, sr=self.target_sample_rate, mono=True)

            # Convert to float32
            self._audio_data = audio_data.astype(np.float32)

            # Calculate chunk parameters
            chunk_samples = int(self.target_sample_rate * self.chunk_duration_seconds)
            self._total_chunks = len(self._audio_data) // chunk_samples
            if len(self._audio_data) % chunk_samples > 0:
                self._total_chunks += 1

            self._chunk_index = 0
            self._is_active = True

            # Put all chunks into the queue immediately
            for i in range(self._total_chunks):
                chunk_samples = int(self.target_sample_rate * self.chunk_duration_seconds)
                start_idx = i * chunk_samples
                end_idx = min(start_idx + chunk_samples, len(self._audio_data))

                chunk = self._audio_data[start_idx:end_idx]

                # Pad with zeros if needed
                if len(chunk) < chunk_samples:
                    chunk = np.pad(chunk, (0, chunk_samples - len(chunk)), 'constant')

                self.audio_queue.put(chunk)

            logging.info(f"File loaded: {len(self._audio_data)} samples, {self._total_chunks} chunks")

        except Exception as e:
            logging.error(f"Failed to load audio file {self.file_path}: {e}")
            raise RuntimeError(f"Failed to load audio file: {e}")

    def stop(self) -> None:
        """Mark file source as inactive and clean up."""
        self._is_active = False
        self._audio_data = np.array([], dtype=np.float32)
        self._chunk_index = 0
        self._total_chunks = 0

        # Clear the queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break

    @property
    def file_path(self) -> str:
        """Get the file path."""
        return self._file_path

    @file_path.setter
    def file_path(self, value: str) -> None:
        """Set the file path."""
        self._file_path = value

    @property
    def duration_seconds(self) -> float:
        """Get the total duration of the loaded audio."""
        if len(self._audio_data) == 0:
            return 0.0
        return len(self._audio_data) / self.target_sample_rate

    @property
    def total_chunks(self) -> int:
        """Get the total number of chunks."""
        return self._total_chunks
