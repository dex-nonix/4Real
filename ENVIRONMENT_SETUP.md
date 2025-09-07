# Environment Setup Guide

## 🚀 Quick Start

### Development Mode (Local)
```bash
# Start both backend and frontend (automatically uses .env.development)
npm run dev:full
```

### Production Mode (Docker/Caddy)
```bash
# Start Docker setup (automatically uses .env.production)
npm run prod:full
```

## 📁 Environment Files

### .env.development (Local Development)
```
# Frontend URLs - Local Development
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WS_BASE_URL=ws://localhost:5000

# Backend Configuration - Local Development
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
```

### .env.production (Docker/Caddy Production)
```
# Frontend URLs - Production (Docker/Caddy)
VITE_API_BASE_URL=https://dev.local/api
VITE_WS_BASE_URL=wss://dev.local

# Backend Configuration - Production
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
```

## 🎯 Available Commands

### Development
- `npm run dev:api` - Start backend only
- `npm run dev:ui` - Start frontend only
- `npm run dev:full` - Start both backend and frontend

### Production
- `npm run prod:build` - Build for production
- `npm run prod:serve` - Serve production build locally
- `npm run prod:docker` - Start Docker/Caddy setup
- `npm run prod:full` - Full production setup

## How Vite Mode System Works

Vite automatically uses the correct environment file based on the mode:

- `--mode development` → uses `.env.development`
- `--mode production` → uses `.env.production`

No manual copying needed! Just use the right npm script.

## 🌐 URL Patterns

### Development
- Frontend: `http://localhost:5173`
- API: `http://localhost:5000/api`
- WebSocket: `ws://localhost:5000`

### Production
- Frontend: `https://dev.local`
- API: `https://dev.local/api`
- WebSocket: `wss://dev.local`

## ⚙️ Custom Configuration

You can override any environment variable at runtime:

```bash
# Custom API URL
VITE_API_BASE_URL=https://my-api.com/api npm run dev:ui

# Custom WebSocket URL
VITE_WS_BASE_URL=wss://my-ws.com npm run dev:ui
```

## 🐳 Docker Configuration

The Docker setup in `docker/dev_server/` supports environment variables:

```bash
# Custom backend port
BACKEND_PORT=8000 docker compose -f docker/dev_server/docker-compose.yml up -d

# Custom frontend port
FRONTEND_PORT=3000 docker compose -f docker/dev_server/docker-compose.yml up -d
```
