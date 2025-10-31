#!/bin/bash
set -e

# Define working directory
WORKDIR="/workspace"
cd $WORKDIR

# Create venv
python3 -m venv venv
source venv/bin/activate

# Upgrade pip & setuptools
pip install --upgrade pip setuptools wheel

# Install git and other essentials (if not present)
apt-get update && apt-get install -y git

# Clone Qwen-Image repo
if [ ! -d "$WORKDIR/Qwen-Image" ]; then
  git clone https://huggingface.co/Qwen/Qwen-Image
fi
cd Qwen-Image

# Install dependencies
pip install -r requirements.txt || true
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate safetensors pillow

# Optional: verify installation
python -c "import torch; print('Torch:', torch.__version__); import transformers; print('Transformers:', transformers.__version__)"

echo "Setup complete. Activate env with: source /workspace/venv/bin/activate"