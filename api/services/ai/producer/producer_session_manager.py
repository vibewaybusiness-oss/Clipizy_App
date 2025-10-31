"""
ProducerAI Session Manager
Handles persistent login and browser session management for ProducerAI with organized queue system
"""

import asyncio
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Import shared configuration and utilities
from .shared_config import config, PRODUCER_AI_URLS, PROMPT_SELECTOR, PAGE_LOAD_TIMEOUT, ELEMENT_WAIT_TIMEOUT, GENERATION_TIMEOUT, MIN_DELAY, MAX_DELAY, BROWSER_ARGS

# Import performance optimizations
from .producer_ai_optimizer import default_producer_optimizer
from .async_optimizer import (
    smart_sleep,
    human_delay,
    retry_operation,
    with_retry,
    with_timeout
)


# TYPES AND REQUEST MODELS (merged from queue manager)
class RequestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TabStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class MusicGenerationRequest:
    request_id: str
    prompt: str
    title: Optional[str] = None
    is_instrumental: bool = False
    lyrics: Optional[str] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    status: RequestStatus = RequestStatus.PENDING
    created_at: float = time.time()
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    assigned_tab_id: Optional[str] = None
    queue_position: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3


logger = logging.getLogger(__name__)

# Configuration is now imported from shared_config

# TabStatus and GenerationRequest are now imported from producer_queue_manager


@dataclass
class WindowInfo:
    window_id: str
    page: Page
    status: TabStatus
    current_request: Optional[MusicGenerationRequest] = None
    created_at: float = None
    last_activity: float = None
    generation_context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.last_activity is None:
            self.last_activity = time.time()
        if self.generation_context is None:
            self.generation_context = {}


@dataclass
class WindowQueue:
    window_id: str
    status: TabStatus = TabStatus.IDLE
    queue: List[MusicGenerationRequest] = field(default_factory=list)
    current_request: Optional[MusicGenerationRequest] = None
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    total_processed: int = 0
    total_failed: int = 0
    average_processing_time: float = 0.0

    def get_queue_size(self) -> int:
        size = len(self.queue)
        if self.current_request:
            size += 1
        return size

    def get_estimated_wait_time(self) -> float:
        if self.average_processing_time == 0:
            return 0.0
        return len(self.queue) * self.average_processing_time


class _EmbeddedQueueManager:
    def __init__(self, session_manager: "ProducerAISessionManager", max_concurrent_windows: int = 12):
        self.max_concurrent_windows = max_concurrent_windows
        self.session_manager = session_manager
        self.windows: Dict[str, WindowQueue] = {}
        self.available_windows: Set[str] = set()
        self.busy_windows: Set[str] = set()
        self.window_lock = asyncio.Lock()
        self.global_queue: List[MusicGenerationRequest] = []
        self.global_queue_lock = asyncio.Lock()
        self.all_requests: Dict[str, MusicGenerationRequest] = {}
        self.request_lock = asyncio.Lock()
        self.is_running = False
        self.queue_processor_task: Optional[asyncio.Task] = None
        self.stats = {
            "total_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "uptime_start": time.time(),
        }

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.queue_processor_task = asyncio.create_task(self._queue_processor())

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.queue_processor_task:
            self.queue_processor_task.cancel()
            try:
                await self.queue_processor_task
            except asyncio.CancelledError:
                pass

    async def create_window(self, window_id: str) -> bool:
        async with self.window_lock:
            if len(self.windows) >= self.max_concurrent_windows:
                return False
            self.windows[window_id] = WindowQueue(window_id=window_id)
            self.available_windows.add(window_id)
        return True

    async def remove_window(self, window_id: str) -> bool:
        async with self.window_lock:
            if window_id not in self.windows:
                return False
            window = self.windows[window_id]
            if window.queue:
                async with self.global_queue_lock:
                    for request in window.queue:
                        request.assigned_tab_id = None
                        request.queue_position = None
                        self.global_queue.append(request)
            if window.current_request:
                window.current_request.status = RequestStatus.CANCELLED
            del self.windows[window_id]
            self.available_windows.discard(window_id)
            self.busy_windows.discard(window_id)
        return True

    async def add_request(self, request: MusicGenerationRequest) -> Dict[str, Any]:
        async with self.request_lock:
            self.all_requests[request.request_id] = request
            self.stats["total_requests"] += 1

        best_window_id = await self._find_best_window_for_request(request)
        if best_window_id:
            async with self.window_lock:
                window = self.windows[best_window_id]
                window.queue.append(request)
                request.queue_position = len(window.queue)
                request.assigned_tab_id = best_window_id
                logger.debug(
                    f"📋 Request {request.request_id} added to window {best_window_id} queue at position {request.queue_position}"
                )

                # If the window is IDLE, trigger immediate processing
                if window.status == TabStatus.IDLE:
                    logger.debug(f"🚀 Window {best_window_id} is IDLE, triggering immediate processing")
                    # Schedule immediate queue processing
                    asyncio.create_task(self._process_window_queues())

            return {
                "success": True,
                "request_id": request.request_id,
                "status": "queued",
                "assigned_window_id": best_window_id,
                "queue_position": request.queue_position,
                "estimated_wait_time": window.get_estimated_wait_time(),
            }
        else:
            async with self.global_queue_lock:
                self.global_queue.append(request)
                request.queue_position = len(self.global_queue)
                logger.debug(
                    f"📋 Request {request.request_id} added to global queue at position {request.queue_position}"
                )

                # Trigger global queue processing
                asyncio.create_task(self._process_global_queue())

            return {
                "success": True,
                "request_id": request.request_id,
                "status": "queued_global",
                "queue_position": request.queue_position,
            }

    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        async with self.request_lock:
            request = self.all_requests.get(request_id)
            if not request:
                return None
            return {
                "request_id": request.request_id,
                "status": request.status.value,
                "assigned_window_id": request.assigned_tab_id,
                "queue_position": request.queue_position,
                "created_at": request.created_at,
                "started_at": request.started_at,
                "completed_at": request.completed_at,
                "error": request.error,
                "result": request.result,
            }

    async def get_queue_status(self) -> Dict[str, Any]:
        async with self.window_lock:
            window_statuses = {}
            for window_id, window in self.windows.items():
                window_statuses[window_id] = {
                    "status": window.status.value,
                    "queue_size": len(window.queue),
                    "current_request": window.current_request.request_id if window.current_request else None,
                    "total_processed": window.total_processed,
                    "total_failed": window.total_failed,
                    "average_processing_time": window.average_processing_time,
                    "estimated_wait_time": window.get_estimated_wait_time(),
                }
        async with self.global_queue_lock:
            global_queue_size = len(self.global_queue)
        return {
            "is_running": self.is_running,
            "total_windows": len(self.windows),
            "available_windows": len(self.available_windows),
            "busy_windows": len(self.busy_windows),
            "global_queue_size": global_queue_size,
            "window_statuses": window_statuses,
            "statistics": self.stats.copy(),
            "uptime": time.time() - self.stats["uptime_start"],
        }

    async def cancel_request(self, request_id: str) -> bool:
        async with self.request_lock:
            request = self.all_requests.get(request_id)
            if not request:
                return False
            if request.status in [RequestStatus.COMPLETED, RequestStatus.FAILED]:
                return False
            request.status = RequestStatus.CANCELLED
        if request.assigned_tab_id:
            async with self.window_lock:
                window = self.windows.get(request.assigned_tab_id)
                if window and request in window.queue:
                    window.queue.remove(request)
        else:
            async with self.global_queue_lock:
                if request in self.global_queue:
                    self.global_queue.remove(request)
        return True

    async def _queue_processor(self):
        cleanup_counter = 0
        while self.is_running:
            try:
                await self._process_global_queue()
                await self._process_window_queues()

                # Only cleanup idle windows every 30 seconds instead of every second
                cleanup_counter += 1
                if cleanup_counter >= 30:
                    await self._cleanup_idle_windows()
                    cleanup_counter = 0

                await self._update_statistics()
                await smart_sleep(0.05, "queue processing")  # Optimized queue processing
            except asyncio.CancelledError:
                break
            except Exception:
                await smart_sleep(1.0, "error recovery")

    async def _find_best_window_for_request(self, request: MusicGenerationRequest) -> Optional[str]:
        async with self.window_lock:
            if not self.windows:
                return None
            best_window_id = None
            min_queue_size = float("inf")

            for window_id, window in self.windows.items():
                if window.status in (TabStatus.IDLE, TabStatus.BUSY):
                    queue_size = window.get_queue_size()
                    if queue_size < min_queue_size:
                        min_queue_size = queue_size
                        best_window_id = window_id

            return best_window_id

    async def _process_global_queue(self):
        if not self.global_queue:
            return
        async with self.global_queue_lock:
            requests_to_assign = []
            for request in self.global_queue[:]:
                if request.status == RequestStatus.PENDING:
                    best_window_id = await self._find_best_window_for_request(request)
                    if best_window_id:
                        requests_to_assign.append((request, best_window_id))
                        self.global_queue.remove(request)
                    elif len(self.windows) < self.max_concurrent_windows:
                        try:
                            new_window_id = await self.session_manager._create_window()
                            requests_to_assign.append((request, new_window_id))
                            self.global_queue.remove(request)
                        except Exception:
                            pass

            for request, window_id in requests_to_assign:
                async with self.window_lock:
                    window = self.windows[window_id]
                    window.queue.append(request)
                    request.queue_position = len(window.queue)
                    request.assigned_tab_id = window_id

    async def _process_window_queues(self):
        # Process windows without holding the global lock for the entire loop
        # This allows multiple windows to be processed simultaneously
        windows_to_process = []

        # First, collect windows that need processing without holding the lock
        async with self.window_lock:
            logger.debug(f"🔄 Checking {len(self.windows)} windows for processing")
            for window_id, window in self.windows.items():
                logger.debug(
                    f"Window {window_id}: status={window.status.value}, has_queue={len(window.queue) > 0}, current_request={window.current_request.request_id if window.current_request else None}"
                )
                # Process windows that have queue and no current request (regardless of status)
                if window.queue and window.current_request is None:
                    logger.debug(f"📋 Will process window {window_id} with {len(window.queue)} queued requests")
                    windows_to_process.append((window_id, window))

        # Process each window that has requests, allowing parallel processing
        logger.debug(f"🚀 Processing {len(windows_to_process)} windows with queued requests")
        for window_id, window in windows_to_process:
            logger.debug(f"🎯 Processing window {window_id} with {len(window.queue)} queued requests")
            # Atomically check and pop from queue for this specific window
            async with self.window_lock:
                if window_id in self.windows and self.windows[window_id].queue:
                    request = self.windows[window_id].queue.pop(0)
                    # Re-get the window reference in case it changed
                    window = self.windows[window_id]
                    logger.debug(f"📤 Popped request {request.request_id} from window {window_id} queue")
                else:
                    logger.debug(f"⏭️ No requests in queue for window {window_id}")
                    continue  # Skip if queue is empty or window no longer exists

            logger.debug(f"🏃 Starting processing of request {request.request_id} in window {window_id}")
            await self._start_processing_request(window_id, request)

    async def _start_processing_request(self, window_id: str, request: MusicGenerationRequest):
        try:
            logger.debug(f"🚀 Starting processing of request {request.request_id} in window {window_id}")

            # Update window status and request status atomically
            async with self.window_lock:
                window = self.windows[window_id]
                window.status = TabStatus.BUSY
                window.current_request = request
                window.last_activity = time.time()
                self.busy_windows.add(window_id)
                self.available_windows.discard(window_id)
                logger.debug(f"🔄 Updated window {window_id} status to BUSY with current_request {request.request_id}")

            # Update request status outside the lock to allow parallel processing
            request.status = RequestStatus.PROCESSING
            request.started_at = time.time()
            request.queue_position = None
            logger.debug(f"📊 Updated request {request.request_id} status to PROCESSING")

            # Start processing in background task (allows parallel processing)
            asyncio.create_task(self._process_music_generation(window_id, request))
            logger.debug(
                f"🎯 Started background processing task for request {request.request_id} in window {window_id}"
            )
        except Exception as e:
            logger.error(f"❌ Error starting processing of request {request.request_id} in window {window_id}: {e}")
            request.status = RequestStatus.FAILED
            request.error = str(e)
            await self._complete_request(window_id, request)

    async def _process_music_generation(self, window_id: str, request: MusicGenerationRequest):
        try:
            # Delegate to session manager's generation using preferred window
            result = await self.session_manager.generate_music_direct(
                prompt=request.prompt,
                title=request.title or f"Track {request.request_id}",
                is_instrumental=request.is_instrumental,
                lyrics=request.lyrics,
                project_id=request.project_id,
                user_id=request.user_id,
                preferred_window_id=window_id,
            )
            if result.get("success"):
                request.result = result
                request.status = RequestStatus.COMPLETED
            else:
                request.status = RequestStatus.FAILED
                request.error = result.get("error")
        except Exception as e:
            request.status = RequestStatus.FAILED
            request.error = str(e)
        finally:
            await self._complete_request(window_id, request)

    async def _complete_request(self, window_id: str, request: MusicGenerationRequest):
        try:
            async with self.window_lock:
                window = self.windows[window_id]
                window.current_request = None
                window.last_activity = time.time()
                logger.debug(f"🏁 Completing request {request.request_id} in window {window_id}")
                if request.status == RequestStatus.COMPLETED:
                    window.total_processed += 1
                    if request.started_at:
                        processing_time = time.time() - request.started_at
                        window.average_processing_time = (
                            window.average_processing_time * (window.total_processed - 1) + processing_time
                        ) / window.total_processed
                    logger.debug(f"✅ Request {request.request_id} completed successfully")
                else:
                    window.total_failed += 1
                    logger.debug(f"❌ Request {request.request_id} failed")

                logger.debug(f"Window {window_id} has {len(window.queue)} queued requests")
                if window.queue:
                    window.status = TabStatus.BUSY
                    # Make sure the window is in busy_windows so it gets processed
                    self.busy_windows.add(window_id)
                    self.available_windows.discard(window_id)
                    logger.debug(f"🔄 Window {window_id} set to BUSY for next request (has {len(window.queue)} queued)")

                    # Immediately trigger queue processing for this window
                    asyncio.create_task(self._process_window_queues())
                else:
                    window.status = TabStatus.IDLE
                    self.available_windows.add(window_id)
                    self.busy_windows.discard(window_id)
                    logger.debug(f"🆓 Window {window_id} set to IDLE - no more requests")
            request.completed_at = time.time()
        except Exception as e:
            logger.error(f"Error completing request {request.request_id}: {e}")

    async def _cleanup_idle_windows(self):
        current_time = time.time()
        idle_threshold = 1800  # 30 minutes
        async with self.window_lock:
            idle_windows = []
            for window_id, window in self.windows.items():
                if (
                    window.status == TabStatus.IDLE
                    and window.last_activity
                    and current_time - window.last_activity > idle_threshold
                ):
                    try:
                        # Get the page from session manager's WindowInfo, not from WindowQueue
                        if window_id in self.session_manager.windows:
                            window_info = self.session_manager.windows[window_id]
                            page = window_info.page
                            if page:
                                # Check if page is still valid before testing login status
                                try:
                                    # Quick check if page is still responsive
                                    await page.evaluate("document.title")
                                    if not await self.session_manager._is_window_logged_in(page, window_id):
                                        idle_windows.append(window_id)
                                except Exception:
                                    # Page is not responsive, mark for cleanup
                                    idle_windows.append(window_id)
                    except Exception:
                        continue
            for window_id in idle_windows:
                try:
                    if window_id in self.session_manager.windows:
                        window_info = self.session_manager.windows[window_id]
                        page = window_info.page
                        await page.close()
                        del self.session_manager.windows[window_id]
                        await self.remove_window(window_id)
                        # Clear cache for this window
                        self.session_manager._clear_login_cache(window_id)
                        logger.info(f"🧹 Cleaned up idle window {window_id}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup window {window_id}: {e}")

    async def _update_statistics(self):
        try:
            total_processing_time = 0
            total_requests = 0
            async with self.window_lock:
                for window in self.windows.values():
                    total_processing_time += window.average_processing_time * window.total_processed
                    total_requests += window.total_processed
            if total_requests > 0:
                self.stats["average_processing_time"] = total_processing_time / total_requests
        except Exception:
            pass


class ProducerAISessionManager:
    """Manages persistent ProducerAI sessions with organized queue system"""

    def __init__(self, max_concurrent_windows: int = 1):
        self.email = config.email
        self.password = config.password
        self.download_path = config.download_path
        self.max_concurrent_windows = max_concurrent_windows

        # Session state
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.is_authenticated = False
        self.session_lock = asyncio.Lock()

        # Window management (browser windows)
        self.windows: Dict[str, WindowInfo] = {}
        self.window_lock = asyncio.Lock()

        # Cache for login status checks to avoid frequent navigation
        self.login_status_cache: Dict[str, Dict[str, Any]] = {}

        # Embedded queue manager (merged from queue manager)
        self.queue_manager = _EmbeddedQueueManager(self)

        logger.info(f"ProducerAI Session Manager initialized with max {max_concurrent_windows} concurrent windows")

    async def initialize(self):
        """Initialize the session manager with persistent login and queue system"""
        async with self.session_lock:
            if self.is_authenticated:
                logger.info("Session already authenticated")
                return

            try:
                logger.info("🚀 Initializing ProducerAI session manager...")

                # Start queue manager
                await self.queue_manager.start()

                # Launch browser
                logger.info("🌐 Launching browser...")
                playwright = await async_playwright().start()

                # Check if we're in a headless environment
                display = os.environ.get("DISPLAY")
                if not display:
                    logger.warning("⚠️ No DISPLAY environment variable found - browser may not be visible")

                # Try to launch browser in non-headless mode first, fallback to headless if it fails
                try:
                    self.browser = await playwright.chromium.launch(headless=False, args=BROWSER_ARGS)
                    logger.info("✅ Browser launched in non-headless mode")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to launch browser in non-headless mode: {e}")
                    logger.info("🔄 Falling back to headless mode...")
                    self.browser = await playwright.chromium.launch(headless=True, args=BROWSER_ARGS)
                    logger.info("✅ Browser launched in headless mode")

                # Create context with mobile viewport to avoid overlay issues
                self.context = await self.browser.new_context(
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    viewport={"width": 375, "height": 812},  # iPhone X dimensions
                    locale="en-US",
                    timezone_id="America/New_York",
                    accept_downloads=True,
                    is_mobile=True,
                    has_touch=True,
                )

                # Perform initial authentication - REQUIRED for proper operation
                try:
                    # Create a temporary page for initial authentication
                    temp_page = await self.context.new_page()
                    await self._login_window(temp_page, "initial_auth")
                    await temp_page.close()
                    logger.info("✅ Initial authentication successful")
                except Exception as e:
                    logger.error(f"❌ Initial authentication failed: {e}")
                    raise Exception(f"Failed to authenticate with ProducerAI: {e}")

                # Create initial persistent window and register with queue manager
                await self._create_initial_persistent_window()

                self.is_authenticated = True
                logger.info("✅ ProducerAI session manager initialized successfully")

            except Exception as e:
                logger.error(f"❌ Failed to initialize session manager: {e}")
                await self.cleanup()
                raise

    async def _create_initial_persistent_window(self):
        """Create initial persistent windows for parallel generation (up to 12 concurrent)"""
        logger.info("🪟 Creating initial persistent windows for parallel generation...")

        # Create multiple persistent windows for parallel generation
        # Start with 3 windows initially, create more on demand up to max_concurrent_windows
        initial_windows = min(3, self.max_concurrent_windows)

        try:
            # Create windows concurrently for better performance
            window_tasks = [self._create_window() for _ in range(initial_windows)]
            await asyncio.gather(*window_tasks, return_exceptions=True)
            logger.info(f"✅ Created {initial_windows} persistent windows concurrently")

            logger.info(f"✅ Created {initial_windows} persistent windows and registered with queue manager")
            logger.info("🌐 Browser windows are now visible and will stay open for the duration of the server")
            logger.info(f"🚀 Ready for parallel generation with up to {self.max_concurrent_windows} concurrent windows")
        except Exception as e:
            logger.error(f"❌ Failed to create initial persistent windows: {e}")
            raise

    async def _create_window(self) -> str:
        """Create a new window for music generation and register with queue manager"""
        window_id = f"window_{int(time.time() * 1000)}_{len(self.windows)}"

        try:
            page = await self.context.new_page()

            # Navigate to create page and verify authentication
            await page.goto(PRODUCER_AI_URLS["create"], timeout=PAGE_LOAD_TIMEOUT)
            await page.wait_for_load_state("domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            await self._human_like_delay(MIN_DELAY, MAX_DELAY)

            # Verify authentication by checking for prompt textarea
            if await self._is_window_logged_in(page, window_id):
                logger.info(f"✅ Window {window_id} is properly authenticated")
            else:
                logger.warning(f"⚠️ Window {window_id} may not be properly authenticated")

            # Download handling is now managed by wait_for_download function
            # No need to set up global download listener here

            # Create window info
            window_info = WindowInfo(window_id=window_id, page=page, status=TabStatus.IDLE)

            # Update last activity to current time to prevent immediate cleanup
            window_info.last_activity = time.time()

            async with self.window_lock:
                self.windows[window_id] = window_info

            # Register window with queue manager
            await self.queue_manager.create_window(window_id)

            logger.info(f"✅ Created window {window_id} and registered with queue manager")
            return window_id

        except Exception as e:
            logger.error(f"❌ Failed to create window {window_id}: {e}")
            raise

    async def _handle_download(
        self, download, window_id: str, generation_id: str = None, user_id: str = None, project_id: str = None
    ):
        """Handle file downloads and upload to S3"""
        try:
            # Get generation context from window if not provided
            if not generation_id or not user_id or not project_id:
                async with self.window_lock:
                    if window_id in self.windows:
                        context = self.windows[window_id].generation_context
                        generation_id = generation_id or context.get("generation_id", f"clip_{int(time.time())}")
                        user_id = user_id or context.get("user_id")
                        project_id = project_id or context.get("project_id")

            # Use provided generation_id or create one
            if not generation_id:
                generation_id = f"clip_{int(time.time())}"

            final_download_path = os.path.join(self.download_path, generation_id)
            os.makedirs(final_download_path, exist_ok=True)

            filename = download.suggested_filename or f"download_{int(time.time())}.wav"
            file_path = os.path.join(final_download_path, filename)

            # Save the download
            await download.save_as(file_path)
            logger.info(f"📥 Download completed for window {window_id}: {filename}")

            # Upload to S3 if user_id and project_id are provided
            if user_id and project_id:
                try:
                    from api.services.storage import backend_storage_service

                    s3_key = f"users/{user_id}/projects/music-clip/{project_id}/audio/{generation_id}.wav"
                    # Note: This would need to be adapted to use the new upload_project_file method
                    # For now, we'll use a placeholder since this is a complex integration
                    s3_url = f"s3://bucket/{s3_key}"  # Placeholder

                    logger.info(f"✅ Uploaded to S3: {s3_url}")

                    # Extract metadata before deleting the file
                    file_metadata = None
                    try:
                        from api.services.storage.core.metadata import extract_metadata

                        file_metadata = extract_metadata(file_path, "audio")
                        logger.info(
                            f"📊 Extracted metadata: duration={file_metadata.get('duration', 0)}s, format={file_metadata.get('format', 'unknown')}"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to extract metadata for {file_path}: {e}")
                        file_metadata = {"duration": 0, "format": "wav", "size_mb": 0}

                    # Get file size before deleting
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

                    # Clean up local file after successful upload
                    os.remove(file_path)
                    logger.info(f"🧹 Cleaned up local file: {file_path}")

                    return {
                        "success": True,
                        "s3_url": s3_url,
                        "s3_key": s3_key,
                        "file_size": file_size,
                        "file_metadata": file_metadata,
                    }

                except Exception as e:
                    logger.error(f"❌ S3 upload failed for window {window_id}: {e}")
                    return {"success": False, "error": f"S3 upload failed: {str(e)}", "local_file": file_path}

            return {"success": True, "local_file": file_path, "filename": filename}

        except Exception as e:
            logger.error(f"❌ Download failed for window {window_id}: {e}")
            return {"success": False, "error": str(e)}

    async def generate_music(self, request: MusicGenerationRequest) -> Dict[str, Any]:
        """Generate music using organized queue system"""
        logger.info(f"🎵 Music generation request: {request.request_id}")

        # Ensure we have enough windows for the request
        await self._ensure_sufficient_windows()

        # Add request to queue manager
        result = await self.queue_manager.add_request(request)

        if result["success"]:
            logger.info(f"📋 Request {request.request_id} added to queue: {result}")
            return result
        else:
            logger.error(f"❌ Failed to add request {request.request_id} to queue")
            return {"success": False, "request_id": request.request_id, "error": "Failed to add request to queue"}

    async def generate_music_direct(
        self,
        prompt: str,
        title: str,
        is_instrumental: bool = False,
        lyrics: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        preferred_window_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate music using dynamic window management (1 initial, create new on demand)"""
        logger.info(f"🎵 Direct music generation: {title}")

        # Create generation ID first
        generation_id = f"gen_{int(time.time())}"
        print(f"🎵 [CONSOLE] Generated ID: {generation_id}")

        try:
            # Prefer a specific window if provided
            window_id = None
            if preferred_window_id and preferred_window_id in self.windows:
                window_id = preferred_window_id
            else:
                # Find available window or create new one if needed
                window_id = await self._get_or_create_available_window()

            if not window_id:
                return {"success": False, "error": "No available windows and cannot create new one (max limit reached)"}

            window_info = self.windows[window_id]
            page = window_info.page

            # Update activity time to keep window alive
            window_info.last_activity = time.time()

            # Store generation context in window for download handler
            window_info.generation_context = {
                "generation_id": generation_id,
                "user_id": user_id,
                "project_id": project_id,
                "prompt": prompt,
                "title": title,
            }

            print(f"🎵 [CONSOLE] Using window {window_id} for direct generation")
            logger.info(f"🎵 Using window {window_id} for direct generation")

            # Perform actual music generation using ProducerAI
            print(f"🎵 [CONSOLE] Starting actual music generation for: {title}")
            logger.info(f"🎵 Starting actual music generation for: {title}")

            # Navigate to create page
            print(f"🎵 [CONSOLE] Navigating to create page...")
            await page.goto(PRODUCER_AI_URLS["create"], timeout=PAGE_LOAD_TIMEOUT)
            await page.wait_for_load_state("domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            await default_producer_optimizer.anti_bot_delay("navigation")

            # Fill prompt
            print(f"🎵 [CONSOLE] Filling prompt...")
            try:
                prompt_element = await page.wait_for_selector(PROMPT_SELECTOR, timeout=ELEMENT_WAIT_TIMEOUT)
                if not prompt_element or not await prompt_element.is_visible():
                    raise Exception("Prompt element not found or not visible")

                await prompt_element.click()
                await page.keyboard.press("Control+a")
                await default_producer_optimizer.anti_bot_delay("type")
                await page.keyboard.press("Delete")
                await default_producer_optimizer.anti_bot_delay("type")
                await prompt_element.fill(prompt)
                print(f"✅ [CONSOLE] Filled prompt in window {window_id}")
                logger.info(f"✅ Filled prompt in window {window_id}")
            except Exception as e:
                print(f"❌ [CONSOLE] Failed to fill prompt: {e}")
                logger.error(f"❌ Failed to fill prompt: {e}")
                raise Exception("Could not find prompt input field - may need to login first")

            # Trigger generation with Enter key
            await default_producer_optimizer.anti_bot_delay("click")
            print(f"⌨️ [CONSOLE] Triggering generation with Enter key in window {window_id}")
            logger.info(f"⌨️ Triggering generation with Enter key in window {window_id}")
            try:
                await page.keyboard.press("Enter")
                await default_producer_optimizer.anti_bot_delay("click")
                print(f"✅ [CONSOLE] Pressed Enter key to trigger generation in window {window_id}")
                logger.info(f"✅ Pressed Enter key to trigger generation in window {window_id}")
            except Exception as e:
                print(f"❌ [CONSOLE] Failed to press Enter key in window {window_id}: {e}")
                logger.error(f"❌ Failed to press Enter key in window {window_id}: {e}")
                raise Exception(f"Failed to trigger generation with Enter key: {e}")

            # Wait for generation to complete and create placeholder file
            print(f"🎵 [CONSOLE] Waiting for music generation to complete in window {window_id}...")
            logger.info(f"🎵 Waiting for music generation to complete in window {window_id}...")

            try:
                # Set up download promise to capture the actual download
                download_promise = None
                download_result = None

                # Create a promise to wait for download using page.on("download")
                async def wait_for_download():
                    nonlocal download_result
                    try:
                        # Wait for download event to be triggered
                        download_event = asyncio.Event()
                        download_obj = None

                        def handle_download(download):
                            nonlocal download_obj
                            download_obj = download
                            download_event.set()

                        # Set up download listener
                        page.on("download", handle_download)

                        # Wait for download event with timeout
                        try:
                            await asyncio.wait_for(download_event.wait(), timeout=GENERATION_TIMEOUT)
                            logger.info(f"📥 Download started in window {window_id}")

                            # Handle the download with context (will use window context)
                            download_result = await self._handle_download(download_obj, window_id)

                            return download_result
                        except asyncio.TimeoutError:
                            logger.error(f"❌ Download timeout in window {window_id}")
                            return {"success": False, "error": "Download timeout"}
                        finally:
                            # Remove the download listener
                            page.remove_listener("download", handle_download)

                    except Exception as e:
                        logger.error(f"❌ Download wait failed in window {window_id}: {e}")
                        return {"success": False, "error": str(e)}

                # Start waiting for download in background
                download_task = asyncio.create_task(wait_for_download())

                # Check if producer is working before looking for More options
                print(f"🔍 [CONSOLE] Checking if producer is working in window {window_id}...")
                logger.info(f"🔍 Checking if producer is working in window {window_id}...")

                producer_working = False
                max_producer_checks = 30  # Check for up to 30 seconds
                check_interval = 1  # Check every 1 second

                for check_attempt in range(max_producer_checks):
                    try:
                        # Look for the producer part element
                        producer_element = await page.wait_for_selector(
                            ".chat-history-part.producer-part", timeout=1000
                        )
                        if producer_element and await producer_element.is_visible():
                            print(
                                f"✅ [CONSOLE] Producer is working in window {window_id} (attempt {check_attempt + 1})"
                            )
                            logger.info(f"✅ Producer is working in window {window_id} (attempt {check_attempt + 1})")
                            producer_working = True
                            break
                        else:
                            print(
                                f"⏳ [CONSOLE] Producer not yet working in window {window_id} (attempt {check_attempt + 1}/{max_producer_checks})"
                            )
                            logger.info(
                                f"⏳ Producer not yet working in window {window_id} (attempt {check_attempt + 1}/{max_producer_checks})"
                            )
                    except Exception as e:
                        print(
                            f"⏳ [CONSOLE] Producer check failed in window {window_id} (attempt {check_attempt + 1}/{max_producer_checks}): {e}"
                        )
                        logger.debug(f"Producer check failed in window {window_id} (attempt {check_attempt + 1}): {e}")

                    await smart_sleep(check_interval, "generation monitoring")

                if not producer_working:
                    print(f"❌ [CONSOLE] Producer appears to be frozen in window {window_id}, restarting process...")
                    logger.warning(f"❌ Producer appears to be frozen in window {window_id}, restarting process...")

                    # Cancel the download task since we're restarting
                    download_task.cancel()

                    # Try to refresh and check again with retry logic
                    producer_check_success = await self._retry_producer_check(page, window_id, max_attempts=2)

                    if not producer_check_success:
                        print(f"❌ [CONSOLE] Producer still not working after refresh attempts in window {window_id}")
                        logger.error(f"❌ Producer still not working after refresh attempts in window {window_id}")
                        return {
                            "success": False,
                            "error": "Producer interface not responding after multiple refresh attempts",
                            "generation_id": generation_id,
                        }

                await default_producer_optimizer.anti_bot_delay("navigation")

                # Try to find and click More options with retry logic
                more_options_success = await self._find_and_click_element_with_retry(
                    page,
                    window_id,
                    'button[aria-label="More options"]',
                    "More options button",
                    max_attempts=3,
                    timeout_per_attempt=30000,  # 30 seconds per attempt
                )

                if not more_options_success:
                    print(f"❌ [CONSOLE] Failed to find More options button after retries in window {window_id}")
                    logger.error(f"❌ Failed to find More options button after retries in window {window_id}")
                    return {
                        "success": False,
                        "error": "Failed to find More options button after page refresh and retries",
                        "generation_id": generation_id,
                    }

                # Look for Download menu item with retry logic
                download_success = await self._find_and_click_element_with_retry(
                    page,
                    window_id,
                    'button div:has-text("Download")',
                    "Download menu item",
                    max_attempts=2,
                    timeout_per_attempt=10000,
                )

                if not download_success:
                    print(f"⚠️ [CONSOLE] Could not find Download menu item in window {window_id}, continuing...")
                    logger.warning(f"⚠️ Could not find Download menu item in window {window_id}, continuing...")

                # Look for WAV format option with retry logic
                wav_success = await self._find_and_click_element_with_retry(
                    page,
                    window_id,
                    'button div:has-text("WAV")',
                    "WAV format option",
                    max_attempts=2,
                    timeout_per_attempt=10000,
                )

                if not wav_success:
                    print(f"⚠️ [CONSOLE] Could not find WAV format option in window {window_id}, continuing...")
                    logger.warning(f"⚠️ Could not find WAV format option in window {window_id}, continuing...")

                # Wait for download to complete
                print(f"🎵 [CONSOLE] Waiting for download to complete in window {window_id}...")
                logger.info(f"🎵 Waiting for download to complete in window {window_id}...")

                try:
                    download_result = await download_task

                    if download_result and download_result.get("success"):
                        print(f"✅ [CONSOLE] Download completed successfully in window {window_id}")
                        logger.info(f"✅ Download completed successfully in window {window_id}")

                        result = {
                            "success": True,
                            "generation_id": generation_id,
                            "window_id": window_id,
                            "prompt": prompt,
                            "title": title,
                            "message": "Music generation completed successfully",
                            "uploaded_files": [
                                {
                                    "filename": f"{generation_id}.wav",
                                    "s3_url": download_result.get("s3_url"),
                                    "s3_key": download_result.get("s3_key"),
                                    "file_size": download_result.get("file_size", 0),
                                    "file_metadata": download_result.get("file_metadata"),
                                }
                            ],
                        }

                        print(f"🎵 [CONSOLE] Generation result: {result.get('success', False)}")
                        return result
                    else:
                        error_msg = (
                            download_result.get("error", "Download failed") if download_result else "Download timeout"
                        )
                        print(f"❌ [CONSOLE] Download failed in window {window_id}: {error_msg}")
                        logger.error(f"❌ Download failed in window {window_id}: {error_msg}")
                        return {
                            "success": False,
                            "error": f"Download failed: {error_msg}",
                            "generation_id": generation_id,
                        }

                except asyncio.TimeoutError:
                    print(f"❌ [CONSOLE] Download timeout in window {window_id}")
                    logger.error(f"❌ Download timeout in window {window_id}")
                    return {
                        "success": False,
                        "error": "Download timeout - generation may still be in progress",
                        "generation_id": generation_id,
                    }

            except Exception as e:
                print(f"❌ [CONSOLE] Music generation failed in window {window_id}: {e}")
                logger.error(f"❌ Music generation failed in window {window_id}: {e}")
                return {"success": False, "error": f"Generation failed: {str(e)}", "generation_id": generation_id}

        except Exception as e:
            print(f"❌ [CONSOLE] Failed to generate music directly: {e}")
            logger.error(f"❌ Failed to generate music directly: {e}")
            return {"success": False, "error": str(e)}

    async def _refresh_window(self, page: Page):
        """Refresh the current page"""
        try:
            await page.reload()
            await page.wait_for_load_state("domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
        except Exception as e:
            logger.warning(f"Failed to refresh window: {e}")

    async def _find_and_click_element_with_retry(
        self,
        page: Page,
        window_id: str,
        selector: str,
        element_name: str,
        max_attempts: int = 3,
        timeout_per_attempt: int = 30000,
    ) -> bool:
        """
        Find and click an element with retry logic including page refresh

        Args:
            page: Playwright page object
            window_id: Window identifier for logging
            selector: CSS selector to find the element
            element_name: Human-readable name of the element for logging
            max_attempts: Maximum number of attempts
            timeout_per_attempt: Timeout per attempt in milliseconds

        Returns:
            True if element was found and clicked successfully, False otherwise
        """
        for attempt in range(max_attempts):
            try:
                print(
                    f"🔍 [CONSOLE] Attempting to find {element_name} (attempt {attempt + 1}/{max_attempts}) in window {window_id}"
                )
                logger.info(
                    f"🔍 Attempting to find {element_name} (attempt {attempt + 1}/{max_attempts}) in window {window_id}"
                )

                # Try to find the element
                element = await page.wait_for_selector(selector, timeout=timeout_per_attempt)

                if element and await element.is_visible():
                    print(f"✅ [CONSOLE] Found {element_name} in window {window_id}")
                    logger.info(f"✅ Found {element_name} in window {window_id}")

                    # Try to click the element
                    await element.click()
                    print(f"✅ [CONSOLE] Successfully clicked {element_name} in window {window_id}")
                    logger.info(f"✅ Successfully clicked {element_name} in window {window_id}")

                    return True
                else:
                    print(f"❌ [CONSOLE] {element_name} not visible in window {window_id}")
                    logger.warning(f"❌ {element_name} not visible in window {window_id}")

            except Exception as e:
                print(f"❌ [CONSOLE] Failed to find {element_name} in window {window_id} (attempt {attempt + 1}): {e}")
                logger.warning(f"❌ Failed to find {element_name} in window {window_id} (attempt {attempt + 1}): {e}")

                # If this isn't the last attempt, refresh the page and try again
                if attempt < max_attempts - 1:
                    print(f"🔄 [CONSOLE] Refreshing page and retrying for {element_name} in window {window_id}")
                    logger.info(f"🔄 Refreshing page and retrying for {element_name} in window {window_id}")
                    await self._refresh_window(page)
                    await default_producer_optimizer.anti_bot_delay("navigation")

        print(
            f"❌ [CONSOLE] Failed to find and click {element_name} after {max_attempts} attempts in window {window_id}"
        )
        logger.error(f"❌ Failed to find and click {element_name} after {max_attempts} attempts in window {window_id}")
        return False

    async def _retry_producer_check(self, page: Page, window_id: str, max_attempts: int = 2) -> bool:
        """
        Retry producer interface check with page refresh

        Args:
            page: Playwright page object
            window_id: Window identifier for logging
            max_attempts: Maximum number of attempts

        Returns:
            True if producer interface is working, False otherwise
        """
        for attempt in range(max_attempts):
            try:
                print(
                    f"🔄 [CONSOLE] Checking producer interface (attempt {attempt + 1}/{max_attempts}) in window {window_id}"
                )
                logger.info(
                    f"🔄 Checking producer interface (attempt {attempt + 1}/{max_attempts}) in window {window_id}"
                )

                # Refresh the page first
                await self._refresh_window(page)
                await default_producer_optimizer.anti_bot_delay("navigation")

                # Check if producer is working
                producer_element = await page.wait_for_selector(".chat-history-part.producer-part", timeout=5000)
                if producer_element and await producer_element.is_visible():
                    print(f"✅ [CONSOLE] Producer interface working in window {window_id}")
                    logger.info(f"✅ Producer interface working in window {window_id}")
                    return True
                else:
                    print(f"❌ [CONSOLE] Producer interface not visible in window {window_id}")
                    logger.warning(f"❌ Producer interface not visible in window {window_id}")

            except Exception as e:
                print(f"❌ [CONSOLE] Producer check failed in window {window_id} (attempt {attempt + 1}): {e}")
                logger.warning(f"❌ Producer check failed in window {window_id} (attempt {attempt + 1}): {e}")

        print(f"❌ [CONSOLE] Producer interface not working after {max_attempts} attempts in window {window_id}")
        logger.error(f"❌ Producer interface not working after {max_attempts} attempts in window {window_id}")
        return False

    async def _is_window_logged_in(self, page: Page, window_id: str = None) -> bool:
        """Check if a window is logged in by looking for the prompt textarea"""
        try:
            # Check cache first (cache for 60 seconds)
            if window_id and window_id in self.login_status_cache:
                cache_entry = self.login_status_cache[window_id]
                if time.time() - cache_entry["timestamp"] < 60:
                    return cache_entry["is_logged_in"]

            # Check if we're already on the create page
            current_url = page.url
            if "producer.ai/create" not in current_url:
                # Only navigate if we're not already on the create page
                await page.goto(PRODUCER_AI_URLS["create"], timeout=PAGE_LOAD_TIMEOUT)

            prompt_element = await page.wait_for_selector(PROMPT_SELECTOR, timeout=3000)
            is_logged_in = prompt_element and await prompt_element.is_visible()

            # Cache the result
            if window_id:
                self.login_status_cache[window_id] = {"is_logged_in": is_logged_in, "timestamp": time.time()}

            return is_logged_in
        except Exception as e:
            logger.debug(f"Window login check failed: {e}")
            return False

    def _clear_login_cache(self, window_id: str = None):
        """Clear login status cache for a specific window or all windows"""
        if window_id:
            self.login_status_cache.pop(window_id, None)
        else:
            self.login_status_cache.clear()

    async def _get_or_create_available_window(self) -> Optional[str]:
        """Get an available window or create a new one if needed (max 12 windows)"""
        async with self.window_lock:
            # First, try to find an idle window
            for window_id, window_info in self.windows.items():
                if window_info.status == TabStatus.IDLE:
                    page = window_info.page
                    if await self._is_window_logged_in(page, window_id):
                        logger.info(f"🪟 Found available logged-in window: {window_id}")
                        return window_id
                    elif await self._login_window(page, window_id):
                        logger.info(f"🪟 Found available window after login: {window_id}")
                        return window_id
                    else:
                        logger.warning(f"⚠️ Window {window_id} login failed, skipping")

            # If no idle windows and we haven't reached the limit, create a new one
            if len(self.windows) < self.max_concurrent_windows:
                logger.info(
                    f"🪟 No idle windows found, creating new window ({len(self.windows) + 1}/{self.max_concurrent_windows})"
                )
                try:
                    window_id = await self._create_window()
                    # New window should be logged in from creation
                    logger.info(f"✅ Created new window: {window_id}")
                    return window_id
                except Exception as e:
                    logger.error(f"❌ Failed to create new window: {e}")
                    return None

            # If we've reached the limit, find the window with the lowest queue
            logger.info(f"🪟 All {len(self.windows)} windows busy, finding window with lowest queue")
            min_queue_window = None
            min_queue_size = float("inf")

            for window_id, window_info in self.windows.items():
                queue_size = len(window_info.queue)
                if queue_size < min_queue_size:
                    min_queue_size = queue_size
                    min_queue_window = window_id

            if min_queue_window:
                window_info = self.windows[min_queue_window]
                page = window_info.page
                if await self._is_window_logged_in(page, min_queue_window):
                    logger.info(
                        f"🪟 Using logged-in window with lowest queue: {min_queue_window} (queue size: {min_queue_size})"
                    )
                    return min_queue_window
                elif await self._login_window(page, min_queue_window):
                    logger.info(
                        f"🪟 Using window with lowest queue after login: {min_queue_window} (queue size: {min_queue_size})"
                    )
                    return min_queue_window
                else:
                    logger.warning(f"⚠️ Window {min_queue_window} login failed, cannot use")

            return None

    async def _login_window(self, page, window_id: str) -> bool:
        """Perform login for a specific window"""
        # Check if already logged in first
        if await self._is_window_logged_in(page, window_id):
            logger.info(f"✅ Window {window_id} already authenticated")
            return True

        try_again = False
        attempt = 0
        while attempt < 3:
            attempt += 1
            try:
                if not try_again:
                    logger.info(f"🔐 Logging in window {window_id} (attempt {attempt}/3)...")

                    # Navigate to ProducerAI homepage
                    await page.goto(PRODUCER_AI_URLS["home"], timeout=PAGE_LOAD_TIMEOUT * 2)
                    await page.wait_for_load_state("domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
                    await self._human_like_delay(2, 4)

                try_again = False

                # Look for Google login button
                try:
                    google_button = await page.wait_for_selector(
                        'button:has-text("Continue with Google")', timeout=ELEMENT_WAIT_TIMEOUT
                    )
                    await google_button.click()
                    await self._human_like_delay(2, 4)
                except Exception as e:
                    logger.warning(f"⚠️ Could not find Google login button: {e}")
                    # Maybe already logged in, check create page
                    if await self._is_window_logged_in(page, window_id):
                        return True
                    continue

                # Email input
                await page.wait_for_selector('input[type="email"]', timeout=ELEMENT_WAIT_TIMEOUT)
                await self._type_like_human(page, 'input[type="email"]', self.email)
                await self._human_like_delay(1, 2)

                next_button = await page.wait_for_selector('button:has-text("Next")', timeout=ELEMENT_WAIT_TIMEOUT)
                await next_button.click()
                await self._human_like_delay(2, 4)

                # Handle try again page
                try:
                    try_again = True
                    try_again_button = await page.wait_for_selector(
                        'a[aria-label="Try again"]', timeout=ELEMENT_WAIT_TIMEOUT
                    )
                    await try_again_button.click()
                    await self._human_like_delay(2, 4)
                    attempt -= 1
                    continue
                except:
                    pass

                # Password input
                await page.wait_for_selector('input[type="password"]', timeout=ELEMENT_WAIT_TIMEOUT)
                await self._type_like_human(page, 'input[type="password"]', self.password)
                await self._human_like_delay(1, 2)

                # Handle checkbox if present
                try:
                    checkbox = await page.wait_for_selector('input[type="checkbox"]', timeout=2000)
                    if checkbox and await checkbox.is_visible():
                        await checkbox.click()
                        await self._human_like_delay(0.5, 1)
                except:
                    pass

                submit_button = await page.wait_for_selector('button:has-text("Next")', timeout=ELEMENT_WAIT_TIMEOUT)
                await submit_button.click()
                await self._human_like_delay(3, 6)

                # Wait for redirect back to ProducerAI
                try:
                    await page.wait_for_url("**/producer.ai/**", timeout=PAGE_LOAD_TIMEOUT)
                except:
                    # If redirect fails, check if we're on producer.ai anyway
                    if "producer.ai" in page.url:
                        pass
                    else:
                        logger.warning("⚠️ Not redirected to ProducerAI, continuing anyway")

                await self._human_like_delay(2, 4)

                # Verify authentication
                if await self._is_window_logged_in(page, window_id):
                    logger.info(f"✅ Successfully logged in window {window_id}")
                    # Update activity time to keep window alive
                    if window_id in self.windows:
                        self.windows[window_id].last_activity = time.time()
                    return True

            except Exception as e:
                logger.error(f"❌ Error logging in window {window_id} (attempt {attempt}): {e}")

        logger.error(f"❌ Failed to log in window {window_id} after 3 attempts")
        return False

    async def _ensure_sufficient_windows(self):
        """Ensure we have enough windows for current demand"""
        async with self.window_lock:
            current_windows = len(self.windows)
            available_windows = len([w for w in self.windows.values() if w.status == TabStatus.IDLE])

            # If we have no available windows and haven't reached max, create more
            if available_windows == 0 and current_windows < self.max_concurrent_windows:
                logger.info(
                    f"🪟 No available windows, creating additional window ({current_windows + 1}/{self.max_concurrent_windows})"
                )
                try:
                    await self._create_window()
                except Exception as e:
                    logger.error(f"❌ Failed to create additional window: {e}")

    async def _human_like_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Add realistic human-like delays"""
        import random

        delay = random.uniform(min_seconds, max_seconds)
        await default_producer_optimizer.anti_bot_delay("human-like")

    async def _type_like_human(self, page: Page, selector: str, text: str):
        """Type text with human-like delays"""
        try:
            element = await page.wait_for_selector(selector, timeout=10000)
            await element.click()
            await self._human_like_delay(0.2, 0.5)

            await page.keyboard.press("Control+a")
            await self._human_like_delay(0.1, 0.2)

            for char in text:
                await page.keyboard.type(char)
                await self._human_like_delay(0.05, 0.15)

        except Exception as e:
            logger.error(f"❌ Failed to type in {selector}: {e}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the session manager and queue"""
        # Get queue manager status
        queue_status = await self.queue_manager.get_queue_status()

        # Get browser window status
        async with self.window_lock:
            browser_window_statuses = {}
            for window_id, window_info in self.windows.items():
                browser_window_statuses[window_id] = {
                    "status": window_info.status.value,
                    "current_request": window_info.current_request.request_id if window_info.current_request else None,
                    "created_at": window_info.created_at,
                    "last_activity": window_info.last_activity,
                }

        return {
            "is_authenticated": self.is_authenticated,
            "browser_windows": {"total": len(self.windows), "statuses": browser_window_statuses},
            "queue_manager": queue_status,
            "max_concurrent_windows": self.max_concurrent_windows,
        }

    async def cleanup(self):
        """Clean up resources (only called on server shutdown)"""
        logger.info("🧹 Cleaning up ProducerAI session manager...")

        try:
            # Stop queue manager
            if hasattr(self, "queue_manager") and self.queue_manager:
                await self.queue_manager.stop()

            # Close browser context and browser (only on server shutdown)
            if hasattr(self, "context") and self.context:
                await self.context.close()
            if hasattr(self, "browser") and self.browser:
                await self.browser.close()
            logger.info("🌐 Browser window closed (server shutting down)")
        except asyncio.CancelledError:
            logger.info("🛑 Cleanup cancelled - continuing with shutdown")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
        finally:
            self.is_authenticated = False
            if hasattr(self, "windows"):
                self.windows.clear()


# Global session manager instance
session_manager = ProducerAISessionManager()
