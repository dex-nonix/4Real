# Save this file as server.py. Run it with: python server.py
# This is a diagnostic. It will print a wall of text. That is what we want.

import uvicorn
import socketio
import logging
from fastapi import FastAPI
from starlette.responses import HTMLResponse

# -----------------------------------------------------------------------------
# Force all logging to be visible
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG)


# -----------------------------------------------------------------------------
# Create the apps
# -----------------------------------------------------------------------------
app = FastAPI()

# -----------------------------------------------------------------------------
# THE TRUTH SERUM
# We are enabling the loggers. This will make the server print exactly
# why it is rejecting the connection.
# -----------------------------------------------------------------------------
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,          # <--- TELL ME THE TRUTH (Socket.IO layer)
    engineio_logger=True  # <--- TELL ME THE TRUTH (Engine.IO layer)
)

socket_app = socketio.ASGIApp(sio)
app.mount("/socket.io", socket_app)


# -----------------------------------------------------------------------------
# The rest of the code is the same
# -----------------------------------------------------------------------------
html = """
<!DOCTYPE html>
<html>
<head><title>DIAGNOSTIC</title></head>
<body>
    <h1>Waiting for server logs...</h1>
    <p id="status">Connecting...</p>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>
        const statusEl = document.getElementById('status');
        console.log("Client connecting...");

        const socket = io(  "ws://0.0.0.0:5001", { transports: ["websocket"] });

        socket.on('connect', () => {
            statusEl.innerText = "Connected.";
            statusEl.style.color = "green";
        });

        socket.on('connect_error', (err) => {
            statusEl.innerText = "Failed.";
            statusEl.style.color = "red";
            console.error("Connection Error:", err);
        });
    </script>
</body>
</html>
"""

@app.get("/")
def read_root():
    return HTMLResponse(html)

@sio.on("connect")
async def handle_connect(sid, environ):
    print(f"Connect event fired for sid={sid}")


# -----------------------------------------------------------------------------
# Run the app
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "test_socket:app",
        host="0.0.0.0",
        port=5001,
        reload=True
    )