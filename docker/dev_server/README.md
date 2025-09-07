# Caddy Reverse Proxy Dev Setup (Single Domain)

This setup provides a development environment with automatic SSL/TLS certificates and path-based routing using a single domain.

## Architecture
- **Single Domain**: `dev.local`
- **Path-based Routing**:
  - `https://dev.local/` → Frontend (port 5173)
  - `https://dev.local/api/*` → Backend API (port 5000)
  - `https://dev.local/socket.io/*` → WebSocket Backend (port 5000)

## Requirements
- [Docker](https://www.docker.com/)
- [mkcert](https://github.com/FiloSottile/mkcert)
- Backend running on port 5000
- Frontend (Vite) running on port 5173

## Setup
1. Run the setup script (generates certs, prepares structure):
   ```bash
   ./setup.sh
   ```

2. Add to your `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
   ```
   127.0.0.1 dev.local
   ```

3. Start your backend and frontend:
   ```bash
   # Terminal 1: Start backend
   npm run dev:api

   # Terminal 2: Start frontend
   npm run dev:ui
   ```

4. Start the Caddy proxy:
   ```bash
   docker compose up -d
   ```

5. Access your application:
   - **Frontend**: https://dev.local
   - **API**: https://dev.local/api/
   - **WebSocket**: wss://dev.local/socket.io/

## Environment Variables (Optional)

You can customize the backend and frontend host/port by setting environment variables:

```bash
# Custom backend host/port
BACKEND_HOST=localhost BACKEND_PORT=8000 docker compose up -d

# Custom frontend host/port
FRONTEND_HOST=localhost FRONTEND_PORT=3000 docker compose up -d
```

## Dynamic Runtime Config via JSON API
Caddy exposes its admin API on port `2019` for dynamic configuration.

### Add a new route dynamically
```bash
curl -X POST http://localhost:2019/config/apps/http/servers/srv0/routes \
  -H "Content-Type: application/json" \
  -d '{
    "match": [ { "host": [ "dev.local" ], "path": ["/custom/*"] } ],
    "handle": [{
      "handler": "reverse_proxy",
      "upstreams": [ { "dial": "host.docker.internal:9000" } ]
    }],
    "terminal": true
  }'
```

## Troubleshooting

### Certificate Issues
If you get certificate errors:
```bash
# Reinstall certificates
./setup.sh
# Restart Caddy
docker compose restart
```

### Connection Issues
- Ensure your backend is running on port 5000
- Ensure your frontend is running on port 5173
- Check that `host.docker.internal` resolves correctly in your Docker environment

### WebSocket Issues
- WebSocket connections use `wss://dev.local/socket.io/`
- Ensure your frontend is configured to use this WebSocket URL

