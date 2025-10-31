"""
Audio Analyzer HTTP Server
Accepts requests with S3 URLs and performs music analysis and/or LLM captioning
"""

import os
import json
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask not available, install with: pip install flask")

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("⚠️ boto3 not available, install with: pip install boto3")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests not available, install with: pip install requests")

WORKDIR = os.getenv("WORKDIR", "/workspace")
CLEANUP = os.getenv("CLEANUP", "false").lower() == "true"
PORT = int(os.getenv("PORT", "8188"))
HOST = os.getenv("HOST", "0.0.0.0")

MODEL_PATH = os.getenv("MODEL_PATH", f"{WORKDIR}/Qwen3-Omni-30B-A3B-Captioner")
VLLM_API_URL = os.getenv("VLLM_API_URL", "http://localhost:8901")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_from_s3(s3_url: str, output_path: str) -> bool:
    """Download file from S3 URL."""
    try:
        if s3_url.startswith("s3://"):
            if not BOTO3_AVAILABLE:
                raise ImportError("boto3 required for S3 downloads")
            
            s3 = boto3.client('s3')
            parsed = s3_url.replace("s3://", "").split("/", 1)
            bucket = parsed[0]
            key = parsed[1] if len(parsed) > 1 else ""
            
            logger.info(f"Downloading from S3: {bucket}/{key}")
            s3.download_file(bucket, key, output_path)
            return True
        elif s3_url.startswith("http://") or s3_url.startswith("https://"):
            logger.info(f"Downloading from URL: {s3_url}")
            response = requests.get(s3_url, stream=True, timeout=300)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            logger.error(f"Unsupported URL format: {s3_url}")
            return False
    except Exception as e:
        logger.error(f"Failed to download from {s3_url}: {e}")
        return False

def get_qwen_captioner(api_url: Optional[str] = None, model_path: Optional[str] = None):
    """Get Qwen captioner function."""
    if api_url:
        def caption_via_api(audio_path: str, prompt: str = "") -> str:
            try:
                audio_url = f"file://{os.path.abspath(audio_path)}"
                
                content = [
                    {"type": "audio_url", "audio_url": {"url": audio_url}}
                ]
                
                if prompt:
                    content.append({"type": "text", "text": prompt})
                
                payload = {
                    "messages": [
                        {
                            "role": "user",
                            "content": content
                        }
                    ]
                }
                
                response = requests.post(
                    f"{api_url}/v1/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=300
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"API captioning failed: {e}")
                raise
        
        return caption_via_api
    elif model_path and os.path.exists(model_path):
        try:
            import torch
            from transformers import Qwen3OmniMoeForConditionalGeneration, Qwen3OmniMoeProcessor
            from qwen_omni_utils import process_mm_info
            
            logger.info(f"Loading Qwen model from {model_path}...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                model_path,
                dtype="auto",
                device_map="auto",
                attn_implementation="flash_attention_2" if torch.cuda.is_available() else None,
                torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            )
            
            processor = Qwen3OmniMoeProcessor.from_pretrained(model_path)
            
            def caption_via_model(audio_path: str, prompt: str = "") -> str:
                try:
                    conversation = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "audio", "audio": audio_path},
                            ],
                        },
                    ]
                    
                    if prompt:
                        conversation[0]["content"].append({"type": "text", "text": prompt})
                    
                    text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
                    audios, _, _ = process_mm_info(conversation, use_audio_in_video=False)
                    inputs = processor(
                        text=text,
                        audio=audios,
                        return_tensors="pt",
                        padding=True,
                        use_audio_in_video=False
                    )
                    inputs = inputs.to(model.device).to(model.dtype)
                    
                    text_ids, audio = model.generate(**inputs, thinker_return_dict_in_generate=True)
                    
                    caption = processor.batch_decode(
                        text_ids.sequences[:, inputs["input_ids"].shape[1]:],
                        skip_special_tokens=True,
                        clean_up_tokenization_spaces=False
                    )[0]
                    
                    return caption
                except Exception as e:
                    logger.error(f"Model captioning failed: {e}")
                    raise
            
            return caption_via_model
        except Exception as e:
            logger.error(f"Failed to load Qwen model: {e}")
            return None
    else:
        logger.warning("No API URL or valid model path provided for Qwen captioner")
        return None

def analyze_music(audio_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
    """Analyze music using unified music analyzer."""
    try:
        from music_analyzer import analyze_audio_file
        
        logger.info(f"Analyzing music: {audio_path}")
        result = analyze_audio_file(
            audio_path,
            sr=22050,
            hop=512,
            extract_features=True,
            use_precise_detection=True,
            create_plot=False
        )
        
        music_analysis = {
            "duration": result.get("duration"),
            "tempo": result.get("tempo"),
            "segments": result.get("segments", {}),
            "segments_sec": result.get("segments_sec", []),
            "beat_times_sec": result.get("beat_times_sec", []),
            "downbeats_sec": result.get("downbeats_sec", []),
            "features": result.get("features", {}),
            "analysis_id": result.get("analysis_id"),
            "analysis_timestamp": result.get("analysis_timestamp")
        }
        
        return music_analysis
    except Exception as e:
        logger.error(f"Music analysis failed: {e}")
        raise

def extract_audio_segment(audio_path: str, start_time: float, end_time: float, output_path: str) -> bool:
    """Extract audio segment using ffmpeg."""
    try:
        import subprocess
        cmd = [
            "ffmpeg", "-i", audio_path,
            "-ss", str(start_time),
            "-t", str(end_time - start_time),
            "-acodec", "copy",
            "-y", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, check=True)
        return os.path.exists(output_path)
    except Exception as e:
        logger.error(f"Failed to extract segment {start_time}-{end_time}: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "port": PORT})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        project_uid = data.get("project_uid")
        s3_url = data.get("s3_url")
        llm_analysis = data.get("llm_analysis", False)
        llm_analysis_prompt = data.get("llm_analysis_prompt", "")
        segment_analysis = data.get("segment_analysis", False)
        segment_analysis_prompt = data.get("segment_analysis_prompt", "")
        
        if not project_uid:
            return jsonify({"error": "project_uid is required"}), 400
        
        if not s3_url:
            return jsonify({"error": "s3_url is required"}), 400
        
        if not llm_analysis and not segment_analysis:
            return jsonify({"error": "At least one of llm_analysis or segment_analysis must be true"}), 400
        
        project_dir = Path(WORKDIR) / "projects" / project_uid
        project_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Processing project {project_uid} from {s3_url}")
        
        audio_path = project_dir / "audio.wav"
        
        logger.info(f"Downloading audio from {s3_url}...")
        if not download_from_s3(s3_url, str(audio_path)):
            return jsonify({"error": "Failed to download audio from S3 URL"}), 500
        
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found after download"}), 500
        
        result = {
            "project_uid": project_uid,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        qwen_captioner = None
        if llm_analysis:
            logger.info("Initializing Qwen captioner...")
            qwen_captioner = get_qwen_captioner(
                api_url=VLLM_API_URL if os.path.exists(f"{WORKDIR}/vllm") else None,
                model_path=MODEL_PATH if os.path.exists(MODEL_PATH) else None
            )
            
            if not qwen_captioner:
                return jsonify({"error": "Qwen captioner not available. Check VLLM_API_URL or MODEL_PATH"}), 500
        
        music_analysis_data = None
        segments_sec = None
        
        if segment_analysis:
            logger.info("Running segment analysis...")
            music_analysis_data = analyze_music(str(audio_path), segment_analysis_prompt)
            result["music_analysis"] = music_analysis_data
            segments_sec = music_analysis_data.get("segments_sec", [])
        
        if llm_analysis:
            if segment_analysis and segments_sec and len(segments_sec) > 1:
                logger.info("Running LLM analysis on segments...")
                segments_output = []
                
                for i in range(len(segments_sec) - 1):
                    start_time = segments_sec[i]
                    end_time = segments_sec[i + 1]
                    
                    segment_path = project_dir / f"segment_{i+1}.wav"
                    
                    logger.info(f"Extracting segment {i+1}: {start_time:.2f}s - {end_time:.2f}s")
                    if extract_audio_segment(str(audio_path), start_time, end_time, str(segment_path)):
                        try:
                            segment_prompt = segment_analysis_prompt if segment_analysis_prompt else llm_analysis_prompt
                            caption = qwen_captioner(str(segment_path), segment_prompt)
                            
                            segments_output.append({
                                "index": i + 1,
                                "t_start": float(start_time),
                                "t_end": float(end_time),
                                "llm_analysis_output": caption
                            })
                        except Exception as e:
                            logger.error(f"Failed to analyze segment {i+1}: {e}")
                            segments_output.append({
                                "index": i + 1,
                                "t_start": float(start_time),
                                "t_end": float(end_time),
                                "llm_analysis_output": f"Error: {str(e)}"
                            })
                
                result["llm_analysis_segments_output"] = segments_output
            
            if llm_analysis_prompt or (llm_analysis and not (segment_analysis and segments_sec)):
                logger.info("Running full audio LLM analysis...")
                full_caption = qwen_captioner(str(audio_path), llm_analysis_prompt)
                result["llm_analysis_output"] = full_caption
        
        if CLEANUP:
            logger.info(f"Cleaning up project directory: {project_dir}")
            shutil.rmtree(project_dir, ignore_errors=True)
        else:
            logger.info(f"Project directory kept (CLEANUP=false): {project_dir}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({"error": str(e), "status": "failed"}), 500

if __name__ == "__main__":
    if not FLASK_AVAILABLE:
        print("❌ Flask is required. Install with: pip install flask")
        exit(1)
    
    logger.info(f"Starting Audio Analyzer server on {HOST}:{PORT}")
    logger.info(f"WORKDIR: {WORKDIR}")
    logger.info(f"CLEANUP: {CLEANUP}")
    logger.info(f"MODEL_PATH: {MODEL_PATH}")
    logger.info(f"VLLM_API_URL: {VLLM_API_URL}")
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)

