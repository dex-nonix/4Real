#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "[install] Project root: $PROJECT_ROOT"

# Create venv
if [ ! -d "$VENV_DIR" ]; then
  echo "[install] Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -V

echo "[install] Upgrading pip and installing dependencies"
python -m pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

# Optional .env from example
if [ -f "$BACKEND_DIR/.env" ]; then
  echo "[install] Using existing $BACKEND_DIR/.env"
else
  if [ -f "$BACKEND_DIR/.env.example" ]; then
    echo "[install] Creating $BACKEND_DIR/.env from example"
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  else
    echo "[install] No .env.example found; skipping"
  fi
fi

echo "[install] Initializing database"
python "$BACKEND_DIR/cli.py" init-db

echo "[install] Done. Use ./start_dev.sh to run the server."

