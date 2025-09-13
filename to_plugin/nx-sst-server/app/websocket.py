from flask_socketio import emit
from app import socketio
import numpy as np
from .speech_recognition import transcribe_audio_chunk # Simple import without VAD for now
import base64

# Buffer for incoming audio data chunks (if needed for VAD or larger chunks)
audio_buffer = b''
# silence_counter = 0
# SILENCE_THRESHOLD = 10 # Number of silent chunks before considering speech ended

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Corrected: Removed the 'json' parameter
@socketio.on('start_streaming')
def handle_start_streaming():
    print('Start streaming message received')
    # You might send an acknowledgement back to the client
    emit('streaming_started', {'data': 'Server is ready to receive audio'})

# Corrected: Removed the 'json' parameter
@socketio.on('stop_streaming')
def handle_stop_streaming():
    print('Stop streaming message received')
    # Process any remaining audio in the buffer if using VAD
    # global audio_buffer
    # if audio_buffer:
    #     # Process remaining buffer
    #     final_transcription = transcribe_audio_chunk(np.frombuffer(audio_buffer, np.float32)) # Adjust dtype if needed
    #     emit('transcription_update', {'text': final_transcription, 'final': True})
    # audio_buffer = b'' # Clear buffer
    # silence_counter = 0 # Reset silence counter
    emit('streaming_stopped', {'data': 'Server stopped receiving audio'})


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    # Assuming 'data' contains raw audio bytes (e.g., from PyAudio or browser Web Audio API)
    # The format (e.g., int16, float32) and sample rate must match the client
    # print(f"Received audio chunk of size: {len(data)}")

    # Convert bytes to numpy array (adjust dtype based on your audio format)
    # Example: 16-bit PCM audio from browser Web Audio API
    try:
        # The data coming from the browser JS is an ArrayBuffer representing Int16 data
        # We need to convert it to a float32 numpy array for faster-whisper
        audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0 # Normalize to float32 [-1, 1]
        # Reshape if necessary, faster-whisper expects (n_samples,)

        # Simplified: buffer small chunks and transcribe larger chunks
        global audio_buffer
        # Append the raw bytes (Int16) to the buffer
        audio_buffer += data

        # Process buffered audio in chunks of a certain size (e.g., 2 seconds worth)
        # Assuming 16kHz, 16-bit audio (2 bytes per sample), 2 seconds is 16000 samples/sec * 2 sec * 2 bytes/sample = 64000 bytes
        chunk_size_bytes = 16000 * 2 * 2 # Example: Process 2 seconds at a time for 16kHz, int16 audio
        if len(audio_buffer) >= chunk_size_bytes:
            # Take a chunk from the buffer
            process_chunk_bytes = audio_buffer[:chunk_size_bytes]
            audio_buffer = audio_buffer[chunk_size_bytes:] # Keep the rest in the buffer

            # Convert the chunk to float32 numpy array for transcription
            process_chunk_np = np.frombuffer(process_chunk_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe the chunk
            transcription = transcribe_audio_chunk(process_chunk_np) # sample_rate is NOT passed here
            if transcription:
                # Emit non-final transcriptions as they arrive
                emit('transcription_update', {'text': transcription, 'final': False})

    except Exception as e:
        print(f"Error processing audio chunk: {e}")
        # Optionally emit an error back to the client
        # emit('transcription_error', {'error': str(e)})


# Add VAD and buffering logic for better real-time performance
# This requires more complex state management and threading/async handling
# potentially using eventlet or gevent workers with Flask-SocketIO.
# Since we removed eventlet, this would involve standard Python threading or async techniques
# which are more complex than the basic example provided.