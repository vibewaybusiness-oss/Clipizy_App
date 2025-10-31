"""
Custom logging middleware to replace 127.0.0.1 with localhost in all log messages
"""

import logging
import sys
from typing import Any, Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LocalhostLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to replace 127.0.0.1 with localhost in all log messages"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self._setup_logging_override()
    
    def _setup_logging_override(self):
        """Override the root logger to replace 127.0.0.1 with localhost"""
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Create a custom formatter that replaces 127.0.0.1 with localhost
        class LocalhostFormatter(logging.Formatter):
            def format(self, record):
                # Get the original formatted message
                formatted = super().format(record)
                # Replace 127.0.0.1 with localhost
                return formatted.replace('127.0.0.1', 'localhost')
        
        # Apply the custom formatter to all handlers
        for handler in root_logger.handlers:
            handler.setFormatter(LocalhostFormatter())
        
        # Also override the uvicorn access logger specifically
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        for handler in uvicorn_access_logger.handlers:
            handler.setFormatter(LocalhostFormatter())
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response
