"""
Startup Manager for ProducerAI Session
Handles initialization of persistent sessions when the server starts
"""

import asyncio
import logging
from typing import Optional

from .producer_session_manager import session_manager

logger = logging.getLogger(__name__)


class StartupManager:
    """Manages startup initialization of services"""

    def __init__(self):
        self.initialization_task: Optional[asyncio.Task] = None
        self.is_initialized = False

    async def initialize_producer_session(self):
        """Initialize the ProducerAI session manager"""
        from .shared_config import config

        # Check if ProducerAI is disabled via environment variable
        if config.disabled:
            logger.info("🚫 ProducerAI initialization disabled via DISABLE_PRODUCER_AI environment variable")
            self.is_initialized = False
            return

        try:
            if not self.is_initialized:
                logger.info("🚀 Initializing ProducerAI session manager on startup...")
                # Add timeout to prevent hanging
                await asyncio.wait_for(session_manager.initialize(), timeout=300.0)
                self.is_initialized = True
                logger.info("✅ ProducerAI session manager initialized successfully")
            else:
                logger.info("ℹ️ ProducerAI session manager already initialized")
        except asyncio.TimeoutError:
            logger.error("❌ ProducerAI session manager initialization timed out after 300 seconds")
            logger.warning("⚠️ ProducerAI features will be disabled. The application will continue to run.")
            self.is_initialized = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize ProducerAI session manager: {e}")
            logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
            import traceback

            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            logger.warning("⚠️ ProducerAI features will be disabled. The application will continue to run.")
            self.is_initialized = False

    async def cleanup(self):
        """Cleanup resources on shutdown"""
        try:
            logger.info("🧹 Cleaning up startup manager...")
            if hasattr(session_manager, "is_authenticated") and session_manager.is_authenticated:
                await session_manager.cleanup()
            self.is_initialized = False
            logger.info("✅ Startup manager cleanup completed")
        except asyncio.CancelledError:
            logger.info("🛑 Startup manager cleanup cancelled - continuing with shutdown")
        except Exception as e:
            logger.error(f"❌ Error during startup manager cleanup: {e}")


# Global startup manager instance
startup_manager = StartupManager()
