"""
Routes System
Legacy route definitions and specific endpoint implementations
"""

from .producer import (
    router as producer_router,
)

from .producer_music_clip import (
    router as music_clip_router,
)

__all__ = [
    # Producer routes
    "producer_router",
    
    # Music clip routes
    "music_clip_router",
]
