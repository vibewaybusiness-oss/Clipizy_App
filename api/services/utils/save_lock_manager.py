"""
Save Lock Manager to prevent concurrent modifications and infinite loops
"""

import threading
import time
from typing import Dict, Set

from api.config.logging import get_project_logger

logger = get_project_logger()


class SaveLockManager:
    """Manages locks to prevent concurrent saves and infinite loops"""

    def __init__(self):
        self._locks: Dict[str, threading.Lock] = {}
        self._active_saves: Set[str] = set()
        self._lock_timeouts: Dict[str, float] = {}
        self._global_lock = threading.Lock()
        self._lock_timeout_seconds = 30  # 30 second timeout for locks

    def acquire_lock(self, project_id: str, user_id: str) -> bool:
        """Acquire a save lock for a project"""
        lock_key = f"{user_id}:{project_id}"
        current_time = time.time()

        with self._global_lock:
            # Check if lock already exists and is not expired
            if lock_key in self._lock_timeouts:
                if current_time - self._lock_timeouts[lock_key] < self._lock_timeout_seconds:
                    logger.warning(f"Save lock already active for {lock_key}, skipping save")
                    return False
                else:
                    # Lock expired, clean it up
                    self._cleanup_expired_lock(lock_key)

            # Create new lock
            if lock_key not in self._locks:
                self._locks[lock_key] = threading.Lock()

            # Try to acquire the lock
            if self._locks[lock_key].acquire(blocking=False):
                self._active_saves.add(lock_key)
                self._lock_timeouts[lock_key] = current_time
                logger.info(f"Acquired save lock for {lock_key}")
                return True
            else:
                logger.warning(f"Could not acquire save lock for {lock_key}")
                return False

    def release_lock(self, project_id: str, user_id: str):
        """Release a save lock for a project"""
        lock_key = f"{user_id}:{project_id}"

        with self._global_lock:
            if lock_key in self._locks and lock_key in self._active_saves:
                self._locks[lock_key].release()
                self._active_saves.discard(lock_key)
                self._lock_timeouts.pop(lock_key, None)
                logger.info(f"Released save lock for {lock_key}")

    def _cleanup_expired_lock(self, lock_key: str):
        """Clean up an expired lock"""
        if lock_key in self._locks:
            try:
                self._locks[lock_key].release()
            except:
                pass  # Lock might already be released
            del self._locks[lock_key]

        self._active_saves.discard(lock_key)
        self._lock_timeouts.pop(lock_key, None)
        logger.info(f"Cleaned up expired lock for {lock_key}")

    def cleanup_all_expired_locks(self):
        """Clean up all expired locks"""
        current_time = time.time()
        expired_locks = []

        with self._global_lock:
            for lock_key, timestamp in self._lock_timeouts.items():
                if current_time - timestamp >= self._lock_timeout_seconds:
                    expired_locks.append(lock_key)

            for lock_key in expired_locks:
                self._cleanup_expired_lock(lock_key)

        if expired_locks:
            logger.info(f"Cleaned up {len(expired_locks)} expired locks")

    def is_locked(self, project_id: str, user_id: str) -> bool:
        """Check if a project is currently locked"""
        lock_key = f"{user_id}:{project_id}"
        current_time = time.time()

        with self._global_lock:
            if lock_key in self._lock_timeouts:
                if current_time - self._lock_timeouts[lock_key] < self._lock_timeout_seconds:
                    return True
                else:
                    # Lock expired, clean it up
                    self._cleanup_expired_lock(lock_key)
            return False

    def get_active_locks(self) -> Set[str]:
        """Get all currently active locks"""
        with self._global_lock:
            return self._active_saves.copy()


# Global instance
save_lock_manager = SaveLockManager()
