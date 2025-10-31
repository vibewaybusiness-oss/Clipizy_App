"""
Initialize ProducerAI Session
Script to initialize the ProducerAI session manager
"""

import asyncio
import logging
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from api.services.ai.startup_manager import startup_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Initialize the ProducerAI session manager"""
    try:
        logger.info("🚀 Starting ProducerAI session initialization...")
        await startup_manager.initialize_producer_session()
        logger.info("✅ ProducerAI session initialization completed successfully")
    except Exception as e:
        logger.error(f"❌ ProducerAI session initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
