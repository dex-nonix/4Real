import whisper # Although not directly used now, good to keep the context
from faster_whisper import WhisperModel
import numpy as np
# torch and torchaudio might still be needed by dependencies like faster-whisper or silero-vad
import torch
# import torchaudio # Uncomment if needed explicitly later, e.g., for resampling

# Choose a model size (e.g., "base", "small", "medium", "large-v3")
# "base" is smaller and faster, "large-v3" is more accurate but slower and larger.
# The model will be downloaded on the first run if not available locally.
model_size = "base"
# Use "cpu" for CPU inference, "cuda" for GPU (if available)
device = "cpu" # Change to "cuda" if you have an NVIDIA GPU and CUDA setup
compute_type = "int8" # Use "float16" or "int8_float16" for potentially faster inference depending on hardware

# Load the model
try:
    # The model will be downloaded here if not found in the cache directory
    # The cache directory is usually ~/.cache/whisper/ or specified by WHISPER_MODELS env var
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    print(f"Faster Whisper model '{model_size}' loaded successfully on {device} with {compute_type} compute type.")
except Exception as e:
    print(f"Error loading Faster Whisper model: {e}")
    model = None # Handle cases where the model fails to load

# Silero VAD (Optional but recommended for streaming)
# This part is for potential integration with the websocket handling
# try:
#     # Attempt to load Silero VAD model if torch is available
#     if torch.cuda.is_available():
#         vad_device = "cuda"
#     else:
#         vad_device = "cpu"
#     vad_model, vad_utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
#                                            model='silero_vad_webRTC', # silero_vad_webrtc is the model name
#                                            force_reload=False)
#     vad_model = vad_model.to(vad_device)
#     (get_speech_ts, save_audio, read_audio, VADIterator, collect_chunks) = vad_utils
#     print(f"Silero VAD model loaded successfully on {vad_device}.")
# except ImportError:
#      print("Warning: torch or torchaudio not installed or Silero VAD could not be loaded. VAD functionality will not be available.")
#      vad_model = None
# except Exception as e:
#      print(f"Error loading Silero VAD model: {e}")
#      vad_model = None


def transcribe_audio_chunk(audio_chunk: np.ndarray):
    """
    Transcribes a single audio chunk using faster-whisper.
    audio_chunk is a numpy array of audio data at 16000 Hz (float32).
    """
    if model is None:
        return "Error: Transcription model not loaded."
    try:
        # faster-whisper expects a float32 numpy array at 16000 Hz
        # Do NOT pass sample_rate here, it's not an accepted argument.
        # Ensure the audio_chunk is already correctly formatted and sampled.
        segments, info = model.transcribe(audio_chunk) # Removed sample_rate argument
        transcribed_text = ""
        for segment in segments:
            transcribed_text += segment.text
        return transcribed_text.strip()
    except Exception as e:
        print(f"Error during chunk transcription: {e}")
        return f"Transcription Error: {e}"

def transcribe_audio_file(file_path: str):
    """
    Transcribes a full audio file using faster-whisper.
    """
    if model is None:
        return "Error: Transcription model not loaded."
    try:
        # faster-whisper handles resampling internally for file inputs
        segments, info = model.transcribe(file_path)
        transcribed_text = ""
        for segment in segments:
            transcribed_text += segment.text + " " # Add space for readability
        return transcribed_text.strip()
    except Exception as e:
        print(f"Error during file transcription: {e}")
        return f"Transcription Error: {e}"