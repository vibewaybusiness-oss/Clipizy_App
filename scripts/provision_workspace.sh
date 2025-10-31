#!/usr/bin/env sh
set -eu

WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"
INSTALL_COMFYUI="${INSTALL_COMFYUI:-false}"
INIT_API="${INIT_API:-false}"
LINK_MODELS="${LINK_MODELS:-true}"
COMFYUI_REPO="${COMFYUI_REPO:-https://github.com/comfyanonymous/ComfyUI.git}"

mkdir -p "$WORKSPACE_DIR/ComfyUI"
mkdir -p "$WORKSPACE_DIR/models/checkcredits"
mkdir -p "$WORKSPACE_DIR/models/clip"
mkdir -p "$WORKSPACE_DIR/models/vae"
mkdir -p "$WORKSPACE_DIR/models/loras"
mkdir -p "$WORKSPACE_DIR/models/controlnet"
mkdir -p "$WORKSPACE_DIR/workflows"
mkdir -p "$WORKSPACE_DIR/outputs/videos"
mkdir -p "$WORKSPACE_DIR/outputs/images"

if [ "$INSTALL_COMFYUI" = "true" ]; then
  if [ ! -d "$WORKSPACE_DIR/ComfyUI/.git" ] && [ ! -f "$WORKSPACE_DIR/ComfyUI/main.py" ]; then
    if command -v git >/dev/null 2>&1; then
      rm -rf "$WORKSPACE_DIR/ComfyUI"
      git clone "$COMFYUI_REPO" "$WORKSPACE_DIR/ComfyUI"
    fi
  fi
fi

if [ "$LINK_MODELS" = "true" ] && [ -d "$WORKSPACE_DIR/ComfyUI" ]; then
  mkdir -p "$WORKSPACE_DIR/ComfyUI/models"
  for d in checkcredits clip vae loras controlnet; do
    TARGET="$WORKSPACE_DIR/models/$d"
    LINK="$WORKSPACE_DIR/ComfyUI/models/$d"
    mkdir -p "$TARGET"
    if [ ! -e "$LINK" ]; then
      ln -s "$TARGET" "$LINK"
    fi
  done
fi

if [ "$INIT_API" = "true" ]; then
  mkdir -p "$WORKSPACE_DIR/api"
  if [ ! -f "$WORKSPACE_DIR/api/requirements.txt" ]; then
    cat > "$WORKSPACE_DIR/api/requirements.txt" << 'EOF'
fastapi>=0.110,<1.0
uvicorn[standard]>=0.29,<1.0
pydantic>=2.7,<3.0
EOF
  fi
  if [ ! -f "$WORKSPACE_DIR/api/api.py" ]; then
    cat > "$WORKSPACE_DIR/api/api.py" << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}
EOF
  fi
fi

printf "Provisioned workspace at %s\n" "$WORKSPACE_DIR"




