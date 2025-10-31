!/bin/bash
set -e

# --- Configuration ---
export OLLAMA_HOME="/workspace/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export OLLAMA_HOST="0.0.0.0:8188"
export PATH="$OLLAMA_HOME/bin:/workspace/aws-cli/bin:$PATH"

# --- AWS configuration ---
if [[ -n "$AWS_KEY" && -n "$AWS_SECRET" ]]; then
  echo "[*] Configuring AWS credentials..."
  mkdir -p ~/.aws
  cat <<EOF > ~/.aws/credentials
[default]
aws_access_key_id=${AWS_KEY}
aws_secret_access_key=${AWS_SECRET}
region=${AWS_REGION}
EOF
else
  echo "[!] AWS_KEY or AWS_SECRET not set — skipping AWS setup."
fi

# --- Prep directories ---
mkdir -p "$OLLAMA_MODELS"

echo "[*] Starting Ollama from $OLLAMA_HOME"
echo "    Models directory: $OLLAMA_MODELS"
echo "    Host: $OLLAMA_HOST"
echo

# --- Start Ollama server ---
"$OLLAMA_HOME/bin/ollama" serve > "$OLLAMA_HOME/ollama.log" 2>&1 &

# Wait for the server to initialize
sleep 5

# --- Ensure models are present ---
echo "[*] Pulling required models..."
"$OLLAMA_HOME/bin/ollama" pull mistral:7b || true
"$OLLAMA_HOME/bin/ollama" pull qwen3-vl || true

# --- Warm up the models ---
echo "[*] Preloading models..."
curl -s "http://localhost:8188/api/generate" \
  -d '{"model":"mistral:7b","prompt":"Ready."}' > /dev/null || true

curl -s "http://localhost:8188/api/generate" \
  -d '{"model":"qwen3-vl","prompt":"Ready."}' > /dev/null || true

echo
echo "[+] Ollama is running on $OLLAMA_HOST"
echo "[+] Logs: $OLLAMA_HOME/ollama.log"

wait