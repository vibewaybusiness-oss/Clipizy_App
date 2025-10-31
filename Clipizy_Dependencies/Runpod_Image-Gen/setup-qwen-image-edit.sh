#!/bin/bash
set -e

WORKDIR="/workspace"
cd $WORKDIR

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and tools
pip install --upgrade pip setuptools wheel

# Install essentials
apt-get update && apt-get install -y git

# Clone Qwen-Image-Edit repo
if [ ! -d "$WORKDIR/Qwen-Image-Edit" ]; then
  git clone https://huggingface.co/Qwen/Qwen-Image-Edit
fi
cd Qwen-Image-Edit

# Install dependencies
pip install -r requirements.txt || true
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate safetensors pillow

# Quick sanity check
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

echo "Qwen-Image-Edit setup complete. Activate with: source /workspace/venv/bin/activate"
