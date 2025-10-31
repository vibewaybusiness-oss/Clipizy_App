import asyncio
import base64
import logging
from typing import Any, Dict, Optional

import httpx
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class SunoCaptchaSolver:
    """CAPTCHA solver for Suno API using 2Captcha service"""

    def __init__(self, twocaptcha_key: str):
        self.twocaptcha_key = twocaptcha_key
        self.base_url = "https://2captcha.com"

    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve hCaptcha using 2Captcha service

        Args:
            site_key: hCaptcha site key
            page_url: URL of the page with CAPTCHA

        Returns:
            CAPTCHA token if solved successfully, None otherwise
        """
        try:
            # Submit CAPTCHA to 2Captcha
            captcha_id = await self._submit_captcha(site_key, page_url)
            if not captcha_id:
                return None

            # Wait for solution
            token = await self._wait_for_solution(captcha_id)
            return token

        except Exception as e:
            logger.error(f"Error solving hCaptcha: {e}")
            return None

    async def solve_image_captcha(self, image_data: bytes, instructions: str = None) -> Optional[Dict[str, Any]]:
        """
        Solve image-based CAPTCHA using 2Captcha service

        Args:
            image_data: Image data as bytes
            instructions: Optional instructions for solving

        Returns:
            Solution data if solved successfully, None otherwise
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            # Submit image CAPTCHA
            captcha_id = await self._submit_image_captcha(image_base64, instructions)
            if not captcha_id:
                return None

            # Wait for solution
            solution = await self._wait_for_image_solution(captcha_id)
            return solution

        except Exception as e:
            logger.error(f"Error solving image CAPTCHA: {e}")
            return None

    async def _submit_captcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Submit CAPTCHA to 2Captcha service"""
        try:
            data = {
                "key": self.twocaptcha_key,
                "method": "hcaptcha",
                "sitekey": site_key,
                "pageurl": page_url,
                "json": 1,
                "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/in.php", data=data)

                if response.status_code != 200:
                    logger.error(f"Failed to submit CAPTCHA: {response.status_code}")
                    return None

                result = response.json()
                if result.get("status") == 1:
                    return result.get("request")
                else:
                    logger.error(f"CAPTCHA submission failed: {result.get('error_text')}")
                    return None

        except Exception as e:
            logger.error(f"Error submitting CAPTCHA: {e}")
            return None

    async def _submit_image_captcha(self, image_base64: str, instructions: str = None) -> Optional[str]:
        """Submit image CAPTCHA to 2Captcha service"""
        try:
            data = {"key": self.twocaptcha_key, "method": "base64", "body": image_base64, "json": 1}

            if instructions:
                data["textinstructions"] = instructions

            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/in.php", data=data)

                if response.status_code != 200:
                    logger.error(f"Failed to submit image CAPTCHA: {response.status_code}")
                    return None

                result = response.json()
                if result.get("status") == 1:
                    return result.get("request")
                else:
                    logger.error(f"Image CAPTCHA submission failed: {result.get('error_text')}")
                    return None

        except Exception as e:
            logger.error(f"Error submitting image CAPTCHA: {e}")
            return None

    async def _wait_for_solution(self, captcha_id: str, timeout: int = 120) -> Optional[str]:
        """Wait for CAPTCHA solution from 2Captcha"""
        try:
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < timeout:
                await asyncio.sleep(5)  # Wait 5 seconds between checks

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/res.php",
                        params={"key": self.twocaptcha_key, "action": "get", "id": captcha_id, "json": 1},
                    )

                    if response.status_code != 200:
                        continue

                    result = response.json()
                    if result.get("status") == 1:
                        return result.get("request")
                    elif result.get("error_text") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        logger.error(f"CAPTCHA solution failed: {result.get('error_text')}")
                        return None

            logger.error(f"CAPTCHA solution timeout after {timeout} seconds")
            return None

        except Exception as e:
            logger.error(f"Error waiting for CAPTCHA solution: {e}")
            return None

    async def _wait_for_image_solution(self, captcha_id: str, timeout: int = 120) -> Optional[Dict[str, Any]]:
        """Wait for image CAPTCHA solution from 2Captcha"""
        try:
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < timeout:
                await asyncio.sleep(5)  # Wait 5 seconds between checks

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/res.php",
                        params={"key": self.twocaptcha_key, "action": "get", "id": captcha_id, "json": 1},
                    )

                    if response.status_code != 200:
                        continue

                    result = response.json()
                    if result.get("status") == 1:
                        # Parse solution for image CAPTCHA
                        solution_text = result.get("request", "")
                        return {"text": solution_text}
                    elif result.get("error_text") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        logger.error(f"Image CAPTCHA solution failed: {result.get('error_text')}")
                        return None

            logger.error(f"Image CAPTCHA solution timeout after {timeout} seconds")
            return None

        except Exception as e:
            logger.error(f"Error waiting for image CAPTCHA solution: {e}")
            return None

    async def report_bad_captcha(self, captcha_id: str) -> bool:
        """Report a bad CAPTCHA solution"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/res.php",
                    params={"key": self.twocaptcha_key, "action": "reportbad", "id": captcha_id},
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"Error reporting bad CAPTCHA: {e}")
            return False

    async def get_balance(self) -> Optional[float]:
        """Get 2Captcha account balance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/res.php", params={"key": self.twocaptcha_key, "action": "getbalance", "json": 1}
                )

                if response.status_code != 200:
                    return None

                result = response.json()
                if result.get("status") == 1:
                    return float(result.get("request", 0))
                else:
                    logger.error(f"Failed to get balance: {result.get('error_text')}")
                    return None

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None


class SunoBrowserCaptchaSolver:
    """Browser-based CAPTCHA solver using Playwright or Selenium"""

    def __init__(self, headless: bool = True, locale: str = "en"):
        self.headless = headless
        self.locale = locale

    async def solve_with_playwright(self, page_url: str) -> Optional[str]:
        """Solve CAPTCHA using Playwright browser automation"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(locale=self.locale)
                page = await context.new_page()

                try:
                    await page.goto(page_url)
                    await page.wait_for_load_state("networkidle")

                    # Wait for CAPTCHA to appear
                    await page.wait_for_selector('iframe[title*="hCaptcha"]', timeout=30000)

                    # Get CAPTCHA site key
                    site_key = await page.evaluate(
                        """
                        () => {
                            const iframe = document.querySelector('iframe[title*="hCaptcha"]');
                            if (iframe) {
                                const src = iframe.src;
                                const match = src.match(/sitekey=([^&]+)/);
                                return match ? match[1] : null;
                            }
                            return null;
                        }
                    """
                    )

                    if not site_key:
                        logger.error("Could not find hCaptcha site key")
                        return None

                    # Here you would implement the actual CAPTCHA solving logic
                    # This is a simplified version - you'd need to implement
                    # the full CAPTCHA solving workflow

                    logger.info(f"Found hCaptcha with site key: {site_key}")

                    # For now, return None as this is a placeholder
                    return None

                finally:
                    await browser.close()

        except Exception as e:
            logger.error(f"Error solving CAPTCHA with Playwright: {e}")
            return None

    def solve_with_selenium(self, page_url: str) -> Optional[str]:
        """Solve CAPTCHA using Selenium browser automation"""
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=options)

            try:
                driver.get(page_url)

                # Wait for CAPTCHA to appear
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title*="hCaptcha"]'))
                )

                # Get CAPTCHA site key
                site_key = driver.execute_script(
                    """
                    const iframe = document.querySelector('iframe[title*="hCaptcha"]');
                    if (iframe) {
                        const src = iframe.src;
                        const match = src.match(/sitekey=([^&]+)/);
                        return match ? match[1] : null;
                    }
                    return null;
                """
                )

                if not site_key:
                    logger.error("Could not find hCaptcha site key")
                    return None

                logger.info(f"Found hCaptcha with site key: {site_key}")

                # Here you would implement the actual CAPTCHA solving logic
                # This is a simplified version - you'd need to implement
                # the full CAPTCHA solving workflow

                return None

            finally:
                driver.quit()

        except Exception as e:
            logger.error(f"Error solving CAPTCHA with Selenium: {e}")
            return None
