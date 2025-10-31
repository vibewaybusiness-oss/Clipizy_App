#!/bin/bash
set -e

# --- Configuration ---
export WORKDIR="/workspace"
export VENV_PATH="$WORKDIR/venv"
export APP_HOME="$WORKDIR/Qwen-Image-Edit"
export HOST="0.0.0.0"
export PORT=8188
export PATH="$WORKDIR/aws-cli/bin:$PATH"

# --- Activate environment ---
source "$VENV_PATH/bin/activate"

# --- AWS configuration ---
if [[ -n "$AWS_KEY" && -n "$AWS_SECRET" && -n "$AWS_BUCKET" ]]; then
  echo "[*] Configuring AWS credentials..."
  mkdir -p ~/.aws
  cat <<EOF > ~/.aws/credentials
[default]
aws_access_key_id=${AWS_KEY}
aws_secret_access_key=${AWS_SECRET}
region=${AWS_REGION:-us-east-1}
EOF
else
  echo "[!] AWS credentials not fully set — skipping AWS setup."
fi

# --- Start listener ---
echo "[*] Starting Qwen Image server on ${HOST}:${PORT}"

cat <<'PYCODE' > $WORKDIR/qwen_server.py
from flask import Flask, request, jsonify
import torch, os, uuid, boto3
from PIL import Image
from io import BytesIO
from transformers import AutoProcessor, AutoModelForImageGeneration

app = Flask(__name__)

# Load model once at startup
model_path = "/workspace/Qwen-Image-Edit"
print("[*] Loading Qwen Image model...")
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForImageGeneration.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)
print("[+] Model ready.")

# Setup S3 client if available
s3 = None
bucket = os.getenv("AWS_BUCKET")
if os.getenv("AWS_KEY") and bucket:
    s3 = boto3.client("s3")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "missing prompt"}), 400

    # Generate image
    inputs = processor(prompt, return_tensors="pt").to("cuda")
    image = model.generate(**inputs)[0]
    img = Image.fromarray(image)

    # Save to memory
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    file_id = f"{uuid.uuid4()}.png"
    local_path = f"/workspace/{file_id}"
    img.save(local_path)

    # Upload to S3 if configured
    url = None
    if s3:
        key = f"qwen-outputs/{file_id}"
        s3.upload_file(local_path, bucket, key, ExtraArgs={"ContentType": "image/png"})
        region = os.getenv("AWS_REGION", "us-east-1")
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    return jsonify({"prompt": prompt, "image_path": local_path, "url": url})
    
if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8188)))
PYCODE

# Run Flask server
python3 $WORKDIR/qwen_server.py
