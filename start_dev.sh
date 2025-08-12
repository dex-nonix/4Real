#!/usr/bin/env bash
set -euo pipefail

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "[dev] Project root: $PROJECT_ROOT"

# If venv exists, activate it. Otherwise assume user has env ready.
if [ -d "$VENV_DIR" ]; then
  echo "[dev] Activating virtualenv at $VENV_DIR"
  source "$VENV_DIR/bin/activate"
fi

echo "[dev] Starting server on http://0.0.0.0:5000"
python "$BACKEND_DIR/cli.py" run --host 0.0.0.0 --port 5000 --debug

