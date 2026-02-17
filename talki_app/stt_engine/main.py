import asyncio
import sys

import sounddevice as sd

from .audio_sources.microphone_source import MicrophoneSource
from .engine import AsyncSTTEngine


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

