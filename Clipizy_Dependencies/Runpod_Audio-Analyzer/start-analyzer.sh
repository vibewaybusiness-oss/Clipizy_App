#!/bin/bash
set -e

export WORKDIR="${WORKDIR:-/workspace}"
export PORT="${PORT:-8188}"
export HOST="${HOST:-0.0.0.0}"
export CLEANUP="${CLEANUP:-false}"
export MODEL_PATH="${MODEL_PATH:-${WORKDIR}/Qwen3-Omni-30B-A3B-Captioner}"
export VLLM_API_URL="${VLLM_API_URL:-http://localhost:8901}"
export VENV_PATH="${VENV_PATH:-${WORKDIR}/venv}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Starting Audio Analyzer HTTP Server"
echo "=========================================="
echo "Port: ${PORT}"
echo "Host: ${HOST}"
echo "WORKDIR: ${WORKDIR}"
echo "CLEANUP: ${CLEANUP}"
echo "MODEL_PATH: ${MODEL_PATH}"
echo "VLLM_API_URL: ${VLLM_API_URL}"
echo ""

cd "${WORKDIR}"

echo "Checking dependencies..."
python -c "import flask" 2>/dev/null || {
    echo "⚠️  Flask not found, installing..."
    pip install -q flask
}

python -c "import boto3" 2>/dev/null || {
    echo "⚠️  boto3 not found, installing..."
    pip install -q boto3
}

python -c "import requests" 2>/dev/null || {
    echo "⚠️  requests not found, installing..."
    pip install -q requests
}

if [ ! -f "${SCRIPT_DIR}/music_analyzer.py" ]; then
    echo "⚠️  Warning: music_analyzer.py not found at ${SCRIPT_DIR}"
    echo "   Make sure the analyzer is in the same directory"
fi

echo ""
echo "Starting server..."
echo "=========================================="

cd "${SCRIPT_DIR}"
python main.py
