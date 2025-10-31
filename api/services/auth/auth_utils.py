"""
Shared Authentication Utilities
Common functions used across authentication services
"""

import uuid

from api.config.logging import get_auth_logger

logger = get_auth_logger()


def generate_email_based_uuid(email: str) -> str:
    """Generate a deterministic UUID based on email address"""
    namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
    return str(uuid.uuid5(namespace, email.lower().strip()))


def create_user_storage_structure(user_id: str) -> bool:
    """Create user-specific storage structure in S3/local storage"""
    try:
        from api.services.storage import backend_storage_service

        # Backend storage doesn't need explicit folder creation
        # Database tables handle user isolation automatically
        # S3 folders are created automatically when files are uploaded
        
        logger.info(f"User storage structure ready for user: {user_id}")
        
        # Return True to indicate success
        return True

    except Exception as e:
        logger.error(f"Failed to create user storage structure: {str(e)}")
        logger.warning("Continuing without storage structure creation")
        return False
