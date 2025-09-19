"""
Application constants and configuration values.
"""

# Audio Configuration
DEFAULT_MODEL_SIZE = "tiny.en"
TARGET_SAMPLE_RATE = 16000
PROCESSING_INTERVAL_SECONDS = 2.0
MIN_CHUNK_DURATION = 0.2  # seconds
AUDIO_DEVICE_DEFAULT_NAME = "default"

# UI Configuration
WINDOW_TITLE = "Real-Time Transcription"
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 250
WINDOW_X = 100
WINDOW_Y = 100

# Configuration paths
CONFIGS_DIR = "configs"

# Threading Configuration
THREAD_CHECK_INTERVAL = 100  # ms
PROCESSING_THREAD_TIMEOUT = 0.5  # seconds
AUDIO_QUEUE_TIMEOUT = 0.1  # seconds

# Keyboard Simulation
CHARACTER_DELAY = 0.001  # seconds between characters
AUTO_SUBMIT_DELAY = 100  # ms
PASTE_LISTENER_DELAY = 200  # ms

# Logging Configuration
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S'
LOG_LEVEL = 'DEBUG'

# UI Text Labels
START_BUTTON_TEXT = "Start Recording"
STOP_BUTTON_TEXT = "Stop Recording"
CLEAR_BUTTON_TEXT = "Clear"
SEND_BUTTON_TEXT = "Send to Focused Input"

# Status Messages
STATUS_READY = "Ready."
STATUS_STARTING = "Starting..."
STATUS_RECORDING = "Recording..."
STATUS_STOPPING = "Stopping..."
STATUS_STOPPED = "Stopped."

# Paste Mode Messages
PASTE_STATUS_READY = "🎯 Ready - Click 'Send to Focused Input' to begin"
PASTE_STATUS_ACTIVE = "🎯 Paste Mode: Regular clicks focus, Ctrl+Click ONLY pastes (ESC cancels)"

# Feature Descriptions (for startup logging)
FEATURES = [
    "Real-time speech-to-text transcription",
    "Send to Focused Input: Click button → regular clicks focus windows → Ctrl+Click pastes",
    "Auto-send after recording stop (background mode)",
    "Direct text typing (no clipboard)",
    "Auto-submit with Enter or Ctrl+Enter",
    "ESC to cancel paste mode",
    "Cmd+Space hotkey for recording toggle"
]
