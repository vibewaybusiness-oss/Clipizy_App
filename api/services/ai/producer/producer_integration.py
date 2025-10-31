"""
ProducerAI Integration Service
Uses web automation to generate music via ProducerAI
DEPRECATED: Use unified_service.py instead
"""

import logging
from typing import Any, Dict, List, Optional

from .legacy_compatibility import ProducerAIService

logger = logging.getLogger(__name__)

# Global service instance
producer_service = ProducerAIService()
