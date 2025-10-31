import asyncio
import logging
from typing import Optional

from twocaptcha import TwoCaptcha

logger = logging.getLogger(__name__)


class SunoCaptchaSolver:
    """CAPTCHA solver for Suno API using 2Captcha service"""

    def __init__(self, twocaptcha_key: str):
        self.twocaptcha_key = twocaptcha_key
        self.solver = TwoCaptcha(twocaptcha_key)

    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha using 2Captcha service"""
        try:
            logger.info(f"Solving hCaptcha for site_key: {site_key}")

            # Use the 2captcha Python package
            result = self.solver.hcaptcha(sitekey=site_key, url=page_url)

            if result and result.get("code"):
                logger.info("hCaptcha solved successfully")
                return result["code"]
            else:
                logger.error("Failed to solve hCaptcha: No code returned")
                return None

        except Exception as e:
            logger.error(f"Error solving hCaptcha: {str(e)}")
            return None

    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2 using 2Captcha service"""
        try:
            logger.info(f"Solving reCAPTCHA v2 for site_key: {site_key}")

            result = self.solver.recaptcha(sitekey=site_key, url=page_url)

            if result and result.get("code"):
                logger.info("reCAPTCHA v2 solved successfully")
                return result["code"]
            else:
                logger.error("Failed to solve reCAPTCHA v2: No code returned")
                return None

        except Exception as e:
            logger.error(f"Error solving reCAPTCHA v2: {str(e)}")
            return None

    async def get_balance(self) -> Optional[float]:
        """Get 2Captcha account balance"""
        try:
            balance = self.solver.balance()
            logger.info(f"2Captcha balance: ${balance}")
            return balance
        except Exception as e:
            logger.error(f"Error getting 2Captcha balance: {str(e)}")
            return None
