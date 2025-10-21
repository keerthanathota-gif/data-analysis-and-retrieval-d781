#!/usr/bin/env bash
set -euo pipefail
PORT="${1:-5174}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -m http.server "$PORT" --directory "$SCRIPT_DIR"