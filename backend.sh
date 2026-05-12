#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.backend-venv"
REQ_FILE="$SCRIPT_DIR/backend/requirements.txt"
STAMP_FILE="$VENV_DIR/.requirements.sha256"

cd "$SCRIPT_DIR"

if [ ! -d "$VENV_DIR" ]; then
  "$SCRIPT_DIR/pythonw" -m venv "$VENV_DIR"
fi

PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"

"$PYTHON_BIN" -m ensurepip --upgrade >/dev/null 2>&1 || true

CURRENT_HASH="$(shasum -a 256 "$REQ_FILE" | awk '{print $1}')"
INSTALLED_HASH="$(cat "$STAMP_FILE" 2>/dev/null || true)"

if [ "$CURRENT_HASH" != "$INSTALLED_HASH" ]; then
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PIP_BIN" install -r "$REQ_FILE"
  printf '%s\n' "$CURRENT_HASH" > "$STAMP_FILE"
fi

exec "$PYTHON_BIN" -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
