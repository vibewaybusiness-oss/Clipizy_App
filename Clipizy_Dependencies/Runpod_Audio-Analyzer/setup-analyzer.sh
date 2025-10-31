#!/bin/bash
set -e

export WORKDIR="${WORKDIR:-/workspace}"
export MODEL_NAME="Qwen/Qwen3-Omni-30B-A3B-Captioner"
export MODEL_DIR="${WORKDIR}/Qwen3-Omni-30B-A3B-Captioner"
export VENV_PATH="${WORKDIR}/venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Setting up Audio Analyzer with Qwen3-Omni"
echo "=========================================="
echo "Workspace: ${WORKDIR}"
echo "Model: ${MODEL_NAME}"
echo "Script directory: ${SCRIPT_DIR}"
echo ""

cd "${WORKDIR}"

echo "[0/9] Checking Python 3.10..."
if ! command -v python3.10 &> /dev/null; then
    echo "⚠️  Python 3.10 not found, attempting to install..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa || true
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3.10 python3.10-venv python3.10-dev python3-pip
fi

python3.10 --version || {
    echo "❌ Error: Python 3.10 is required but not available"
    exit 1
}

echo "[1/9] Creating Python 3.10 virtual environment..."
if [ -d "${VENV_PATH}" ]; then
    echo "   Virtual environment already exists at ${VENV_PATH}"
    echo "   Skipping creation (remove directory to re-create)"
else
    python3.10 -m venv "${VENV_PATH}"
    echo "   ✓ Created virtual environment at ${VENV_PATH}"
fi

echo "   Activating virtual environment..."
source "${VENV_PATH}/bin/activate"

echo "   Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

echo "[2/9] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    ffmpeg \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    git \
    build-essential

echo "[3/9] Installing Python dependencies from requirements.txt..."
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    pip install -q -r "${SCRIPT_DIR}/requirements.txt"
    echo "   ✓ Installed dependencies from ${SCRIPT_DIR}/requirements.txt"
else
    echo "⚠️  Warning: requirements.txt not found at ${SCRIPT_DIR}/requirements.txt, skipping..."
fi

echo "[4/9] Installing base dependencies..."
pip install -q git+https://github.com/huggingface/transformers
pip install -q accelerate
pip install -q "qwen-omni-utils" -U

echo "[5/9] Installing FlashAttention 2..."
pip install -q -U flash-attn --no-build-isolation || {
    echo "⚠️  FlashAttention installation failed, continuing without it..."
    echo "   Note: This is optional but recommended for GPU memory efficiency"
}

echo "[6/9] Cloning and installing vLLM from source..."
if [ -d "${WORKDIR}/vllm" ]; then
    echo "   vLLM directory already exists, skipping clone..."
    cd "${WORKDIR}/vllm"
    git fetch origin qwen3_omni || true
    git checkout qwen3_omni || true
    git pull origin qwen3_omni || true
else
    git clone -b qwen3_omni https://github.com/wangxiongts/vllm.git "${WORKDIR}/vllm"
    cd "${WORKDIR}/vllm"
fi

echo "   Installing vLLM build requirements..."
pip install -q -r requirements/build.txt
pip install -q -r requirements/cuda.txt

echo "   Installing vLLM (using precompiled wheel if available)..."
export VLLM_PRECOMPILED_WHEEL_LOCATION=https://wheels.vllm.ai/a5dd03c1ebc5e4f56f3c9d3dc0436e9c582c978f/vllm-0.9.2-cp38-abi3-manylinux1_x86_64.whl

if VLLM_USE_PRECOMPILED=1 pip install -q -e . -v --no-build-isolation 2>/dev/null; then
    echo "   ✓ vLLM installed using precompiled wheel"
else
    echo "   ⚠️  Precompiled wheel failed, building from source (this may take a while)..."
    pip install -q -e . -v --no-build-isolation
    echo "   ✓ vLLM built and installed from source"
fi

cd "${WORKDIR}"

echo "[7/9] Downloading Qwen3-Omni-30B-A3B-Captioner model..."
if [ -d "${MODEL_DIR}" ]; then
    echo "   Model directory already exists at ${MODEL_DIR}"
    echo "   Skipping download (remove directory to re-download)"
else
    echo "   Downloading model (this may take a while - model is ~32B parameters)..."
    
    if command -v huggingface-cli &> /dev/null; then
        echo "   Using huggingface-cli..."
        huggingface-cli download "${MODEL_NAME}" --local-dir "${MODEL_DIR}" --local-dir-use-symlinks False
    elif python -c "import modelscope" &> /dev/null; then
        echo "   Using modelscope (recommended for users in Mainland China)..."
        python -c "
import modelscope
from modelscope import snapshot_download
snapshot_download('${MODEL_NAME}', cache_dir='${MODEL_DIR}')
"
    else
        echo "   Installing huggingface_hub..."
        pip install -q -U "huggingface_hub[cli]"
        huggingface-cli download "${MODEL_NAME}" --local-dir "${MODEL_DIR}" --local-dir-use-symlinks False
    fi
    
    echo "   ✓ Model downloaded successfully"
fi

echo "[8/9] Creating model symlink for easier access..."
if [ ! -L "${WORKDIR}/model" ]; then
    ln -sf "${MODEL_DIR}" "${WORKDIR}/model"
    echo "   ✓ Created symlink: ${WORKDIR}/model -> ${MODEL_DIR}"
fi

echo "[9/9] Verifying installation..."
if [ -f "${VENV_PATH}/bin/python" ]; then
    "${VENV_PATH}/bin/python" -c "
import torch
from transformers import Qwen3OmniMoeProcessor
print('✓ torch:', torch.__version__)
print('✓ transformers: OK')
print('✓ Qwen3OmniMoeProcessor: OK')
print('✓ CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print(f'✓ CUDA devices: {torch.cuda.device_count()}')
" || {
    echo "⚠️  Verification had issues, but installation may still work"
}
else
    python -c "
import torch
from transformers import Qwen3OmniMoeProcessor
print('✓ torch:', torch.__version__)
print('✓ transformers: OK')
print('✓ Qwen3OmniMoeProcessor: OK')
print('✓ CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print(f'✓ CUDA devices: {torch.cuda.device_count()}')
" || {
    echo "⚠️  Verification had issues, but installation may still work"
}
fi

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo "Virtual environment: ${VENV_PATH}"
echo "Model location: ${MODEL_DIR}"
echo "Model symlink: ${WORKDIR}/model"
echo ""
echo "To activate the virtual environment:"
echo "  source ${VENV_PATH}/bin/activate"
echo ""
echo "To use the model, set MODEL_PATH to:"
echo "  ${MODEL_DIR}"
echo "  or"
echo "  ${WORKDIR}/model"
echo ""
echo "To start vLLM server:"
echo "  source ${VENV_PATH}/bin/activate"
echo "  vllm serve ${MODEL_DIR} --port 8901 --host 0.0.0.0 --dtype bfloat16 \\"
echo "    --max-model-len 32768 --allowed-local-media-path / -tp \${CUDA_VISIBLE_DEVICES:-1}"
echo ""
echo "To start the analyzer server:"
echo "  source ${VENV_PATH}/bin/activate"
echo "  bash ${SCRIPT_DIR}/start-analyzer.sh"
echo ""
