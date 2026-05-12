#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
  "$SCRIPT_DIR/npmw" install
fi

exec "$SCRIPT_DIR/npmw" run build
