"""
ProducerAI Music Clip Service
Handles music generation for the music clip creation workflow using persistent sessions
DEPRECATED: Use unified_service.py instead
"""

import logging
from typing import Any, Dict, List, Optional

from .legacy_compatibility import ProducerAIMusicClipService

logger = logging.getLogger(__name__)

# Global service instance
producer_music_clip_service = ProducerAIMusicClipService()
