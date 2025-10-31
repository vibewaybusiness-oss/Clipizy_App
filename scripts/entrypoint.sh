#!/usr/bin/env sh
set -eu

SERVICE="${SERVICE:-comfyui}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
API_PORT="${API_PORT:-8001}"
WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"

start_comfyui() {
  if [ ! -f "$WORKSPACE_DIR/ComfyUI/main.py" ]; then
    echo "port 8188 not found in $WORKSPACE_DIR/ComfyUI" >&2
    exit 1
  fi
  cd "$WORKSPACE_DIR/ComfyUI"
  exec python3 main.py --listen "$HOST" --port "$PORT"
}

start_api() {
  if [ ! -f "$WORKSPACE_DIR/api/api.py" ]; then
    echo "API not found in $WORKSPACE_DIR/api" >&2
    exit 1
  fi
  cd "$WORKSPACE_DIR/api"
  exec uvicorn api:app --host "$HOST" --port "$API_PORT"
}

case "$SERVICE" in
  comfyui)
    start_comfyui
    ;;
  api)
    start_api
    ;;
  both)
    if [ ! -f "$WORKSPACE_DIR/ComfyUI/main.py" ]; then
      echo "port 8188 not found in $WORKSPACE_DIR/ComfyUI" >&2
      exit 1
    fi
    if [ ! -f "$WORKSPACE_DIR/api/api.py" ]; then
      echo "API not found in $WORKSPACE_DIR/api" >&2
      exit 1
    fi
    (cd "$WORKSPACE_DIR/ComfyUI" && python3 main.py --listen "$HOST" --port "$PORT") &
    cd "$WORKSPACE_DIR/api"
    exec uvicorn api:app --host "$HOST" --port "$API_PORT"
    ;;
  *)
    echo "Unknown SERVICE: $SERVICE (expected comfyui|api|both)" >&2
    exit 1
    ;;
esac




