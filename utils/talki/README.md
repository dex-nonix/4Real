# Talki - Real-Time Speech-to-Text Transcription

A modular Python application for real-time audio transcription using Whisper, featuring direct text input simulation and advanced paste modes.

## Features

- **Real-time speech-to-text transcription** using Faster Whisper
- **Compact toggle interface**: Single ▶️/🔴 button for start/stop recording
- **Resizable text area**: Drag window corners to adjust transcription view
- **Send to Focused Input**: 📤 button → regular clicks focus windows → Ctrl+Click pastes
- **Auto-send after recording stop** (background mode)
- **Direct text typing** (no clipboard)
- **Auto-submit** with Enter or Ctrl+Enter
- **ESC to cancel** paste mode
- **Cmd+Space hotkey** for recording toggle
- **Global mouse button support** (X1/X2 buttons on gaming mice)
- **System tray integration** (minimize to tray instead of closing)

## Architecture

The application is organized into a clean, modular package structure:

```
talki/
├── config/           # Configuration and logging
├── core/             # Core business logic
│   ├── audio/        # Audio processing and device management
│   └── transcription/# Whisper model integration
├── ui/               # User interface components
├── input/            # Input simulation and paste mode
├── services/         # Application coordination
└── utils/            # Shared utilities and constants
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m talki.main
```

Or install as a package:

```bash
pip install .
talki
```

## Requirements

- Python 3.8+
- PyQt6
- faster-whisper
- sounddevice
- numpy
- pynput
- colorama

## Usage

1. Select your microphone from the dropdown
2. Click the ▶️ button to start recording (turns 🔴 when recording)
3. Speak into your microphone
4. Transcription appears in real-time (resize window to see more/less text)
5. Click the 📤 button to enable paste mode
6. Regular clicks focus windows, Ctrl+Click pastes text
7. Press ESC to cancel paste mode
8. Click the window close button to minimize to system tray (don't close the app)

## Keyboard & Mouse Controls

### Keyboard Shortcuts
- **Cmd+Space**: Toggle recording start/stop (Linux: adapt as needed)

### Mouse Buttons (Global)
- **X1 Button (Backward)**: Toggle recording start/stop
- **X2 Button (Forward)**: Cancel/stop current operations

## System Tray

Talki integrates with your system tray for easy access:

- **Minimize to Tray**: Click the window's close button (X) to hide the window
- **Restore Window**: Double-click the tray icon or use the context menu
- **Quit Application**: Right-click tray icon → "Quit" to fully close the app

The application stays running in the background when minimized to tray.

## Development

This is a refactored version of the original monolithic `talki.py` file, split into maintainable components for better code organization and testability.
