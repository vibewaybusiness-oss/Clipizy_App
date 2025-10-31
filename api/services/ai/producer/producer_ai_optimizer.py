"""
ProducerAI Performance Optimizer
Specialized optimizations for ProducerAI integration with anti-bot detection measures
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from playwright.async_api import Page

from .async_optimizer import AsyncOptimizer, PerformanceConfig, OptimizationLevel
from .shared_config import config

logger = logging.getLogger(__name__)


class AntiBotStrategy(Enum):
    """Anti-bot detection strategies"""
    STEALTH = "stealth"        # Maximum stealth, slower but undetectable
    BALANCED = "balanced"      # Balanced speed and stealth
    AGGRESSIVE = "aggressive"  # Faster but higher detection risk


@dataclass
class ProducerAIConfig:
    """Configuration for ProducerAI optimizations"""
    
    # Anti-bot detection settings
    anti_bot_strategy: AntiBotStrategy = AntiBotStrategy.BALANCED
    
    # Page interaction delays (anti-bot)
    min_click_delay: float = 0.1
    max_click_delay: float = 0.3
    min_type_delay: float = 0.05
    max_type_delay: float = 0.15
    min_navigation_delay: float = 1.0
    max_navigation_delay: float = 3.0
    
    # Element interaction settings
    element_wait_timeout: float = 5.0
    element_retry_attempts: int = 3
    element_retry_delay: float = 0.5
    
    # Page load settings
    page_load_timeout: float = 10.0
    page_load_retry_attempts: int = 3
    
    # Generation monitoring settings
    generation_check_interval: float = 0.5
    generation_max_checks: int = 120  # 60 seconds total
    generation_timeout: float = 300.0  # 5 minutes
    
    # Queue processing settings
    queue_poll_interval: float = 0.05
    queue_batch_size: int = 5
    
    # Error recovery settings
    max_recovery_attempts: int = 3
    recovery_delay: float = 2.0


class ProducerAIOptimizer:
    """Specialized optimizer for ProducerAI operations"""
    
    def __init__(self, config: Optional[ProducerAIConfig] = None):
        self.config = config or ProducerAIConfig()
        self.base_optimizer = AsyncOptimizer(self._create_base_config())
        self._setup_anti_bot_strategy()
    
    def _create_base_config(self) -> PerformanceConfig:
        """Create base performance config from ProducerAI config"""
        return PerformanceConfig(
            level=OptimizationLevel.BALANCED,
            default_timeout=self.config.generation_timeout,
            page_load_timeout=self.config.page_load_timeout,
            element_wait_timeout=self.config.element_wait_timeout,
            max_retries=self.config.element_retry_attempts,
            retry_delay=self.config.element_retry_delay,
            min_human_delay=self.config.min_click_delay,
            max_human_delay=self.config.max_click_delay,
            queue_poll_interval=self.config.queue_poll_interval,
            batch_size=self.config.queue_batch_size
        )
    
    def _setup_anti_bot_strategy(self):
        """Setup anti-bot strategy parameters"""
        if self.config.anti_bot_strategy == AntiBotStrategy.STEALTH:
            # Maximum stealth - slower but undetectable
            self.config.min_click_delay = 0.2
            self.config.max_click_delay = 0.8
            self.config.min_type_delay = 0.1
            self.config.max_type_delay = 0.3
            self.config.min_navigation_delay = 2.0
            self.config.max_navigation_delay = 5.0
            self.config.generation_check_interval = 1.0
            
        elif self.config.anti_bot_strategy == AntiBotStrategy.AGGRESSIVE:
            # Faster but higher detection risk
            self.config.min_click_delay = 0.05
            self.config.max_click_delay = 0.2
            self.config.min_type_delay = 0.02
            self.config.max_type_delay = 0.1
            self.config.min_navigation_delay = 0.5
            self.config.max_navigation_delay = 2.0
            self.config.generation_check_interval = 0.2
    
    async def anti_bot_delay(self, delay_type: str = "click") -> None:
        """
        Anti-bot delay with randomization
        
        Args:
            delay_type: Type of delay (click, type, navigation, etc.)
        """
        if delay_type == "click":
            min_delay = self.config.min_click_delay
            max_delay = self.config.max_click_delay
        elif delay_type == "type":
            min_delay = self.config.min_type_delay
            max_delay = self.config.max_type_delay
        elif delay_type == "navigation":
            min_delay = self.config.min_navigation_delay
            max_delay = self.config.max_navigation_delay
        else:
            min_delay = self.config.min_click_delay
            max_delay = self.config.max_click_delay
        
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def human_like_click(self, page: Page, selector: str, **kwargs) -> bool:
        """
        Human-like click with anti-bot measures
        
        Args:
            page: Playwright page object
            selector: Element selector
            **kwargs: Additional click options
            
        Returns:
            True if click was successful
        """
        try:
            # Wait for element with timeout
            element = await page.wait_for_selector(selector, timeout=self.config.element_wait_timeout * 1000)
            
            if not element:
                logger.warning(f"Element not found: {selector}")
                return False
            
            # Anti-bot delay before click
            await self.anti_bot_delay("click")
            
            # Perform click
            await element.click(**kwargs)
            
            # Anti-bot delay after click
            await self.anti_bot_delay("click")
            
            logger.debug(f"Successfully clicked element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return False
    
    async def human_like_type(self, page: Page, selector: str, text: str, **kwargs) -> bool:
        """
        Human-like typing with anti-bot measures
        
        Args:
            page: Playwright page object
            selector: Element selector
            text: Text to type
            **kwargs: Additional type options
            
        Returns:
            True if typing was successful
        """
        try:
            # Wait for element
            element = await page.wait_for_selector(selector, timeout=self.config.element_wait_timeout * 1000)
            
            if not element:
                logger.warning(f"Element not found: {selector}")
                return False
            
            # Clear existing text
            await element.click()
            await self.anti_bot_delay("click")
            await page.keyboard.press("Control+a")
            await self.anti_bot_delay("type")
            await page.keyboard.press("Delete")
            await self.anti_bot_delay("type")
            
            # Type text with human-like delays
            for char in text:
                await element.type(char, **kwargs)
                await self.anti_bot_delay("type")
            
            logger.debug(f"Successfully typed text into element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type into element {selector}: {e}")
            return False
    
    async def smart_navigation(self, page: Page, url: str, **kwargs) -> bool:
        """
        Smart navigation with anti-bot measures
        
        Args:
            page: Playwright page object
            url: URL to navigate to
            **kwargs: Additional navigation options
            
        Returns:
            True if navigation was successful
        """
        try:
            # Anti-bot delay before navigation
            await self.anti_bot_delay("navigation")
            
            # Navigate with timeout
            await page.goto(url, timeout=self.config.page_load_timeout * 1000, **kwargs)
            
            # Wait for page to load
            await page.wait_for_load_state("domcontentloaded", timeout=self.config.page_load_timeout * 1000)
            
            # Anti-bot delay after navigation
            await self.anti_bot_delay("navigation")
            
            logger.debug(f"Successfully navigated to: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    async def wait_for_generation_completion(
        self,
        page: Page,
        check_selector: str = ".chat-history-part.producer-part",
        timeout: Optional[float] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Wait for music generation to complete with optimized checking
        
        Args:
            page: Playwright page object
            check_selector: Selector to check for completion
            timeout: Maximum time to wait
            
        Returns:
            Tuple of (success, result_data)
        """
        timeout = timeout or self.config.generation_timeout
        start_time = time.time()
        check_count = 0
        
        logger.info(f"Starting generation monitoring with {self.config.anti_bot_strategy.value} strategy")
        
        while time.time() - start_time < timeout:
            try:
                # Check if generation is complete
                producer_element = await page.wait_for_selector(check_selector, timeout=1000)
                
                if producer_element:
                    # Check if generation is still in progress
                    is_generating = await self._is_generation_in_progress(page, producer_element)
                    
                    if not is_generating:
                        # Generation complete, try to extract result
                        result_data = await self._extract_generation_result(page)
                        logger.info(f"Generation completed successfully after {check_count} checks")
                        return True, result_data
                
                check_count += 1
                
                # Optimized check interval based on strategy
                await asyncio.sleep(self.config.generation_check_interval)
                
                # Log progress every 10 checks
                if check_count % 10 == 0:
                    elapsed = time.time() - start_time
                    logger.debug(f"Generation check {check_count}, elapsed: {elapsed:.1f}s")
                
            except Exception as e:
                logger.debug(f"Generation check failed (attempt {check_count}): {e}")
                await asyncio.sleep(self.config.generation_check_interval)
                check_count += 1
        
        logger.warning(f"Generation timed out after {timeout}s ({check_count} checks)")
        return False, {}
    
    async def _is_generation_in_progress(self, page: Page, producer_element) -> bool:
        """Check if generation is still in progress"""
        try:
            # Look for loading indicators or generation status
            loading_indicators = [
                ".loading",
                ".generating",
                ".processing",
                "[data-testid*='loading']",
                "[data-testid*='generating']"
            ]
            
            for indicator in loading_indicators:
                if await page.query_selector(indicator):
                    return True
            
            # Check for text content that indicates generation
            text_content = await producer_element.text_content()
            if text_content:
                generation_keywords = ["generating", "creating", "processing", "loading", "please wait"]
                if any(keyword in text_content.lower() for keyword in generation_keywords):
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking generation status: {e}")
            return True  # Assume still generating if we can't check
    
    async def _extract_generation_result(self, page: Page) -> Dict[str, Any]:
        """Extract generation result from page"""
        try:
            # Look for download links or result elements
            download_links = await page.query_selector_all("a[href*='download'], a[href*='.mp3'], a[href*='.wav']")
            
            if download_links:
                result_urls = []
                for link in download_links:
                    href = await link.get_attribute("href")
                    if href:
                        result_urls.append(href)
                
                return {
                    "success": True,
                    "download_urls": result_urls,
                    "extracted_at": time.time()
                }
            
            # Fallback: return page content for manual extraction
            return {
                "success": True,
                "page_content": await page.content(),
                "extracted_at": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error extracting generation result: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_at": time.time()
            }
    
    async def retry_with_recovery(
        self,
        operation_func: callable,
        *args,
        max_attempts: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Retry operation with ProducerAI-specific recovery
        
        Args:
            operation_func: Function to retry
            *args: Function arguments
            max_attempts: Maximum retry attempts
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        max_attempts = max_attempts or self.config.max_recovery_attempts
        
        for attempt in range(max_attempts):
            try:
                return await operation_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Operation failed (attempt {attempt + 1}/{max_attempts}): {e}")
                
                if attempt < max_attempts - 1:
                    # Recovery delay with exponential backoff
                    delay = self.config.recovery_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {max_attempts} attempts failed for {operation_func.__name__}")
                    raise
    
    async def optimize_queue_processing(self, queue_items: List[Any], process_func: callable) -> List[Any]:
        """
        Optimized queue processing for ProducerAI
        
        Args:
            queue_items: List of items to process
            process_func: Function to process each item
            
        Returns:
            List of processed results
        """
        return await self.base_optimizer.batch_process(
            queue_items,
            process_func,
            batch_size=self.config.queue_batch_size
        )


# Predefined configurations
STEALTH_CONFIG = ProducerAIConfig(anti_bot_strategy=AntiBotStrategy.STEALTH)
BALANCED_CONFIG = ProducerAIConfig(anti_bot_strategy=AntiBotStrategy.BALANCED)
AGGRESSIVE_CONFIG = ProducerAIConfig(anti_bot_strategy=AntiBotStrategy.AGGRESSIVE)

# Global optimizer instances
stealth_optimizer = ProducerAIOptimizer(STEALTH_CONFIG)
balanced_optimizer = ProducerAIOptimizer(BALANCED_CONFIG)
aggressive_optimizer = ProducerAIOptimizer(AGGRESSIVE_CONFIG)

# Default optimizer
default_producer_optimizer = balanced_optimizer
