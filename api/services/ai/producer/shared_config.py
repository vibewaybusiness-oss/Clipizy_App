"""
Shared Configuration for ProducerAI Services
Centralizes all configuration, constants, and environment variables
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ENVIRONMENT VARIABLES
PRODUCER_AI_EMAIL = os.getenv("PRODUCER_AI_EMAIL", "vibeway.business@gmail.com")
PRODUCER_AI_PASSWORD = os.getenv("PRODUCER_AI_PASSWORD", "ouiOUI2007")
PRODUCER_AI_DOWNLOAD_PATH = os.getenv("PRODUCER_AI_DOWNLOAD_PATH", "./downloads")
DISABLE_PRODUCER_AI = os.getenv("DISABLE_PRODUCER_AI", "false").lower() == "true"

# URLS
PRODUCER_AI_URLS = {
    "home": "https://www.producer.ai/",
    "create": "https://www.producer.ai/create"
}

# SELECTORS
PROMPT_SELECTOR = 'textarea[placeholder="Ask Producer..."]'

# TIMEOUTS
PAGE_LOAD_TIMEOUT = 30000
ELEMENT_WAIT_TIMEOUT = 15000
GENERATION_TIMEOUT = 120000

# DELAYS
MIN_DELAY = 0.5
MAX_DELAY = 2.0

# BROWSER ARGS
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor",
    "--disable-extensions",
    "--disable-plugins",
    "--memory-pressure-off",
    "--max_old_space_size=512",
    "--single-process",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-ipc-flooding-protection",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-translate",
    "--hide-scrollbars",
    "--metrics-recording-only",
    "--mute-audio",
    "--no-first-run",
    "--safebrowsing-disable-auto-update",
    "--disable-client-side-phishing-detection",
    "--disable-component-update",
    "--disable-domain-reliability",
]

# AUDIO FILE EXTENSIONS
AUDIO_EXTENSIONS = (".wav", ".mp3", ".m4a", ".ogg", ".flac")

# S3 PATHS
S3_PATHS = {
    "music_clip": "users/{user_id}/projects/music-clip/{project_id}/audio/{filename}",
    "generated": "music/generated/{generation_id}/{filename}",
    "tracks": "users/{user_id}/projects/music-clip/{project_id}/tracks/{filename}"
}


class ProducerAIConfig:
    """Centralized configuration for ProducerAI services"""
    
    def __init__(self):
        self.email = PRODUCER_AI_EMAIL
        self.password = PRODUCER_AI_PASSWORD
        self.download_path = PRODUCER_AI_DOWNLOAD_PATH
        self.disabled = DISABLE_PRODUCER_AI
        
        # Ensure download directory exists
        os.makedirs(self.download_path, exist_ok=True)
        
        # Log configuration status (without exposing credentials)
        logger.info(
            f"🔐 ProducerAI config: email={'***' if self.email else 'NOT SET'}, "
            f"password={'***' if self.password else 'NOT SET'}, "
            f"download_path={os.path.abspath(self.download_path)}, "
            f"disabled={self.disabled}"
        )
    
    def get_s3_key(self, user_id: str, project_id: str, filename: str, path_type: str = "music_clip") -> str:
        """Generate S3 key for file upload"""
        if path_type == "music_clip" and user_id and project_id:
            return S3_PATHS["music_clip"].format(
                user_id=user_id, project_id=project_id, filename=filename
            )
        elif path_type == "tracks" and user_id and project_id:
            return S3_PATHS["tracks"].format(
                user_id=user_id, project_id=project_id, filename=filename
            )
        else:
            return S3_PATHS["generated"].format(
                generation_id=filename.split('.')[0], filename=filename
            )


# Global configuration instance
config = ProducerAIConfig()
