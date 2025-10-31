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
echo "[*] Starting Qwen Image Edit server on ${HOST}:${PORT}"

cat <<'PYCODE' > $WORKDIR/qwen_image_edit_server.py
from flask import Flask, request, jsonify
import torch, os, uuid, boto3, requests
from io import BytesIO
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageEditing

app = Flask(__name__)

# Load model once
model_path = "/workspace/Qwen-Image-Edit"
print("[*] Loading Qwen Image Edit model...")
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForImageEditing.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)
print("[+] Model ready.")

# Setup S3
s3 = None
bucket = os.getenv("AWS_BUCKET")
if os.getenv("AWS_KEY") and bucket:
    s3 = boto3.client("s3")
region = os.getenv("AWS_REGION", "us-east-1")

@app.route("/edit", methods=["POST"])
def edit_image():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    input_urls = data.get("input_urls", [])
    if not prompt:
        return jsonify({"error": "missing prompt"}), 400
    if not isinstance(input_urls, list) or len(input_urls) == 0:
        return jsonify({"error": "no input images provided"}), 400
    if len(input_urls) > 3:
        return jsonify({"error": "too many input images (max 3)"}), 400

    # Download input images
    images = []
    for url in input_urls:
        try:
            resp = requests.get(url, timeout=15)
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            images.append(img)
        except Exception as e:
            return jsonify({"error": f"failed to load image: {e}"}), 400

    # Generate edited image
    inputs = processor(prompt=prompt, images=images, return_tensors="pt").to("cuda")
    output = model.generate(**inputs)[0]
    result_img = Image.fromarray(output)

    # Save locally
    file_id = f"{uuid.uuid4()}.png"
    local_path = f"/workspace/{file_id}"
    result_img.save(local_path, format="PNG")

    # Upload to S3 if available
    url = None
    if s3:
        key = f"qwen-edits/{file_id}"
        s3.upload_file(local_path, bucket, key, ExtraArgs={"ContentType": "image/png"})
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    return jsonify({"prompt": prompt, "input_count": len(images), "output_path": local_path, "output_url": url})

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8188)))
PYCODE

# --- Run Flask server ---
python3 $WORKDIR/qwen_image_edit_server.py