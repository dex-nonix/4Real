#!/usr/bin/env python3
"""Basic test for the speech_to_text package."""

import asyncio
import sys
import os

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

async def test_basic_functionality():
    """Test basic engine instantiation and lifecycle."""
    try:
        from speech_to_text import SpeechToTextEngine, MicrophoneSource, FileSource

        print("✅ Imports successful")

        # Test engine creation
        engine = SpeechToTextEngine(model_size="tiny.en")
        print("✅ Engine created")

        # Test microphone source creation
        mic_source = MicrophoneSource(device_index=0)
        print("✅ Microphone source created")

        # Test file source creation (will raise ImportError if librosa not available)
        try:
            file_source = FileSource("test.wav")
            print("✅ File source created (librosa available)")
        except ImportError:
            print("⚠️ File source requires librosa: pip install librosa")

        # Test basic lifecycle
        engine.set_audio_source(mic_source)
        print("✅ Audio source set")

        print("🎉 Basic functionality test passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    result = asyncio.run(test_basic_functionality())
    if result:
        print("\n✅ All basic tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
