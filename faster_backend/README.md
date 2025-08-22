# 4Real FastAPI Backend

A modern, async-first backend built with FastAPI to replace the Flask backend.

## Features

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Native WebSockets**: Built-in WebSocket support without external libraries
- **Async Database**: SQLAlchemy with async operations
- **File Uploads**: Static file serving with upload capabilities
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Checks**: Built-in health monitoring endpoints

## Quick Start

### 1. Install Dependencies
```bash
cd faster_backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the `faster_backend` directory:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/4real_db
SECRET_KEY=your-secret-key-here
DEBUG=true
```

### 3. Run the Application
```bash
# Development mode
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- **Root**: `/` - Application info
- **Health**: `/api/health` - Health check
- **Status**: `/api/status` - System status
- **Upload**: `/api/upload` - File upload
- **Files**: `/api/files` - List uploaded files
- **WebSocket**: `/ws` - WebSocket connection

## WebSocket Events

### Client to Server
- `join_room`: Join a chat room
- `leave_room`: Leave a chat room
- `chat_message`: Send a chat message
- `system_message`: Send a system message
- `ping`: Keep connection alive

### Server to Client
- `connection_established`: Connection confirmed
- `room_joined`: Successfully joined room
- `room_left`: Successfully left room
- `chat_message`: Received chat message
- `system_message`: Received system message
- `pong`: Response to ping
- `error`: Error message

## File Structure

```
faster_backend/
├── app/
│   ├── __init__.py          # FastAPI app factory
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── websocket/           # WebSocket management
│   │   ├── __init__.py
│   │   ├── manager.py       # Connection manager
│   │   └── handlers.py      # Event handlers
│   ├── api/                 # API router system
│   │   ├── __init__.py
│   │   ├── health.py        # Health endpoints
│   │   └── upload.py        # File upload endpoints
│   └── static/              # Static files
├── static/
│   └── uploads/             # File upload directory
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## Next Steps

1. **Database Models**: Migrate existing SQLAlchemy models
2. **API Routes**: Move existing API endpoints
3. **Services**: Convert business logic services
4. **Chat System**: Implement chat functionality
5. **Authentication**: Add user authentication

## Benefits Over Flask

- **Native async/await**: No sync/async mixing issues
- **Better performance**: Significantly faster than Flask
- **Type safety**: Better error catching and IDE support
- **Auto-documentation**: OpenAPI/Swagger out of the box
- **Modern standards**: ASGI native, better for async operations
