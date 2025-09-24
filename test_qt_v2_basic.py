#!/usr/bin/env python3
"""Basic test for aio_talki_v2.py Qt integration."""

import sys
import os

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

def test_qt_imports():
    """Test that Qt app imports work without GUI."""
    try:
        print("🧪 Testing Qt v2 imports...")

        # Test basic imports
        import asyncio
        import logging
        import colorama
        import qasync

        # Import Qt modules
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer, pyqtSignal, QObject

        # Import our speech-to-text package
        from speech_to_text import SpeechToTextEngine, MicrophoneSource

        # Import the Qt wrapper
        from aio_talki_v2 import AudioProcessor

        print("✅ All Qt v2 imports successful")

        # Test AudioProcessor creation (without GUI)
        print("🧪 Testing AudioProcessor creation...")
        processor = AudioProcessor(model_size="tiny.en")
        print("✅ AudioProcessor created successfully")

        print("🎉 Qt v2 basic integration test passed!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_qt_imports()
    if success:
        print("\n✅ Qt v2 integration is ready for testing!")
        print("Run: python utils/aio_talki_v2.py")
    else:
        print("\n❌ Qt v2 integration has issues!")
        sys.exit(1)
