#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8010}"
OPEN_BROWSER="${OPEN_BROWSER:-0}"
RELOAD="${RELOAD:-0}"

if [ ! -x "$ROOT_DIR/venv/bin/python" ]; then
  echo "Errore: virtualenv non trovato in $ROOT_DIR/venv"
  echo "Crea una volta sola l'ambiente con: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
  exit 1
fi

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT_DIR/.env"
  set +a
fi

mkdir -p "$ROOT_DIR/quotes"

URL="http://$HOST:$PORT/"
echo "Dashboard locale pronta su: $URL"
echo "Nessuna attivazione manuale della venv richiesta."

if [ "$OPEN_BROWSER" = "1" ] && command -v xdg-open >/dev/null 2>&1; then
  (sleep 1; xdg-open "$URL" >/dev/null 2>&1 || true) &
fi

UVICORN_ARGS=(main:app --host "$HOST" --port "$PORT")
if [ "$RELOAD" = "1" ]; then
  UVICORN_ARGS+=(--reload)
fi

exec "$ROOT_DIR/venv/bin/uvicorn" "${UVICORN_ARGS[@]}"
