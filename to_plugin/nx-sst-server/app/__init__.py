from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Change this!
socketio = SocketIO(app, cors_allowed_origins="*")

from app import routes, websocket
