from flask import render_template, request, jsonify
from app import app
import os
from .speech_recognition import transcribe_audio_file

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        try:
            # Transcribe the saved file
            transcription_result = transcribe_audio_file(filepath)
            os.remove(filepath) # Clean up the uploaded file
            return jsonify({'transcription': transcription_result}), 200
        except Exception as e:
            os.remove(filepath) # Clean up even if transcription fails
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File upload failed'}), 500

