"""
Complete workflow with music generation and menuitem download handling
"""

import asyncio
import json
import logging
import os
import random
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompleteWorkflowWithDownload:
    def __init__(
        self,
        email: str = "vibeway.business@gmail.com",
        password: str = "ouiOUI2007",
        download_path: str = "./downloads",
    ):
        self.email = email
        self.password = password
        self.base_url = "https://www.producer.ai"
        self.display_process = None
        self.download_path = download_path
        self.download_urls = []

        # Create download directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)
        logger.info(f"📁 Download path set to: {os.path.abspath(self.download_path)}")

    async def human_like_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Add realistic human-like delays"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def type_like_human(self, page, selector: str, text: str):
        """Type text with human-like delays"""
        try:
            logger.info(f"⌨️ Typing in {selector}: {text[:10]}...")
            element = await page.wait_for_selector(selector, timeout=10000)
            await element.click()
            await self.human_like_delay(0.2, 0.5)

            # Clear existing text
            await page.keyboard.press("Control+a")
            await self.human_like_delay(0.1, 0.2)

            # Type with human-like speed
            for char in text:
                await page.keyboard.type(char)
                await self.human_like_delay(0.05, 0.15)

            logger.info(f"✅ Typed successfully in {selector}")

        except Exception as e:
            logger.error(f"❌ Failed to type in {selector}: {e}")
            raise

    def start_virtual_display(self):
        """Start virtual display (Xvfb) for headless servers"""
        try:
            logger.info("🖥️ Starting virtual display...")
            # Start Xvfb on display :99
            self.display_process = subprocess.Popen(
                ["Xvfb", ":99", "-screen", "0", "1920x1080x24", "-ac", "+extension", "GLX"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Set DISPLAY environment variable
            os.environ["DISPLAY"] = ":99"

            # Wait a moment for display to start
            time.sleep(2)
            logger.info("✅ Virtual display started on :99")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start virtual display: {e}")
            logger.info("💡 Install Xvfb: sudo apt-get install xvfb")
            return False

    def stop_virtual_display(self):
        """Stop virtual display"""
        if self.display_process:
            try:
                self.display_process.terminate()
                self.display_process.wait(timeout=5)
                logger.info("✅ Virtual display stopped")
            except:
                try:
                    self.display_process.kill()
                    logger.info("✅ Virtual display force stopped")
                except:
                    pass

    async def handle_network_request(self, request):
        """Handle network requests to capture download URLs"""
        url = request.url
        method = request.method

        # Log interesting requests
        if any(keyword in url.lower() for keyword in ["download", "audio", "wav", "mp3", "m4a", "ogg"]):
            logger.info(f"🌐 Network request: {method} {url}")
            self.download_urls.append(url)

    async def handle_network_response(self, response):
        """Handle network responses to capture download responses"""
        url = response.url
        status = response.status
        content_type = response.headers.get("content-type", "")

        # Log interesting responses
        if any(keyword in url.lower() for keyword in ["download", "audio", "wav", "mp3", "m4a", "ogg"]):
            logger.info(f"📥 Network response: {status} {url} (Content-Type: {content_type})")

            if status == 200 and "audio" in content_type:
                logger.info(f"🎵 Found audio download response: {url}")
                self.download_urls.append(url)

    async def handle_download(self, download):
        """Handle browser downloads"""
        logger.info(f"📥 Download started: {download.suggested_filename}")
        logger.info(f"📥 Download URL: {download.url}")

        # Save to our download directory
        download_path = os.path.join(self.download_path, download.suggested_filename)
        await download.save_as(download_path)
        logger.info(f"✅ Download saved to: {download_path}")

        return download_path

    async def wait_for_generation_completion(self, page):
        """Wait for music generation to complete"""
        logger.info("⏳ Waiting for music generation to complete...")

        # Wait for generation to start
        try:
            await page.wait_for_selector(
                '[class*="loading"], [class*="generating"], [class*="progress"]', timeout=10000
            )
            logger.info("🔄 Generation started")
        except:
            logger.info("ℹ️ No loading indicators found, continuing...")

        # Wait for generation to complete
        completion_indicators = [
            '[class*="complete"]',
            '[class*="ready"]',
            '[class*="done"]',
            '[class*="finished"]',
            '[class*="success"]',
            'button[aria-label*="download"]',
            'button[aria-label*="Download"]',
        ]

        for attempt in range(12):  # Wait up to 2 minutes (12 * 10 seconds)
            logger.info(f"🔄 Generation check {attempt + 1}/12...")

            # Check for completion indicators
            for indicator in completion_indicators:
                try:
                    element = await page.wait_for_selector(indicator, timeout=2000)
                    if element and await element.is_visible():
                        logger.info(f"✅ Generation completed - found: {indicator}")
                        return True
                except:
                    continue

            # Wait 10 seconds before next check
            await self.human_like_delay(10, 10)

        logger.warning("⚠️ Generation timeout after 2 minutes, continuing anyway")
        return False

    async def wait_for_format_menu(self, page, timeout: int = 10000):
        """Wait for the download format menu to appear"""
        logger.info("⏳ Waiting for download format menu to appear...")

        # Wait for format options to appear
        format_selectors = [
            'div[role="menuitem"] div:has-text("WAV")',
            'div[role="menuitem"] div:has-text("MP3")',
            'div[role="menuitem"] div:has-text("M4A")',
            'div[role="menuitem"] div:has-text("OGG")',
            'button:has-text("WAV")',
            'button:has-text("MP3")',
            'button:has-text("M4A")',
            'button:has-text("OGG")',
            '[aria-label*="WAV"]',
            '[aria-label*="MP3"]',
            '[aria-label*="M4A"]',
            '[aria-label*="OGG"]',
            '[class*="format"]',
            '[class*="download"]',
            '[role="menu"]',
            '[role="menuitem"]',
        ]

        for selector in format_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=2000)
                if element and await element.is_visible():
                    logger.info(f"✅ Format menu appeared with selector: {selector}")
                    return True
            except:
                continue

        logger.warning("⚠️ Format menu did not appear within timeout")
        return False

    async def execute_menuitem_download_workflow(self, page):
        """Execute the menuitem download workflow with role='menuitem' selectors"""
        logger.info("🎯 Executing menuitem download workflow...")

        # Step 1: Find and hover over the parent group to reveal "More options" button
        logger.info("🔍 Step 1: Looking for parent group to hover over...")
        try:
            # First, find the hidden "More options" button
            more_options_button = await page.query_selector('button[aria-label="More options"]')
            if not more_options_button:
                logger.error("❌ Could not find 'More options' button")
                return False

            logger.info("✅ Found 'More options' button (hidden)")

            # Find the parent group element
            parent_group = await more_options_button.evaluate_handle('button => button.closest(".group")')
            if not parent_group:
                logger.error("❌ Could not find parent group element")
                return False

            logger.info("✅ Found parent group element")

            # Hover over the parent group to reveal the button
            logger.info("🖱️ Hovering over parent group to reveal 'More options' button...")
            await parent_group.hover()
            await self.human_like_delay(1, 2)

            # Check if button is now visible
            is_visible = await more_options_button.is_visible()
            logger.info(f"   └─ 'More options' button visible after hover: {is_visible}")

            if is_visible:
                logger.info("✅ 'More options' button is now visible, clicking...")
                await more_options_button.click()
                await self.human_like_delay(2, 4)
                logger.info("✅ Clicked 'More options' button")
            else:
                logger.warning("⚠️ 'More options' button still not visible after hover, trying force click...")
                await more_options_button.click(force=True)
                await self.human_like_delay(2, 4)
                logger.info("✅ Force clicked 'More options' button")

        except Exception as e:
            logger.error(f"❌ Failed to find or click 'More options' button: {e}")
            return False

        # Step 2: Click Download menuitem - div[role="menuitem"] containing div with "Download" text
        logger.info("🔍 Step 2: Looking for Download menuitem...")
        try:
            # Try to find Download menuitem with nested div containing "Download" text
            download_selectors = [
                'div[role="menuitem"] div:has-text("Download")',
                'div[role="menuitem"] div:has-text("download")',
                'div[role="menuitem"]:has-text("Download")',
                'div[role="menuitem"]:has-text("download")',
                'div[role="menuitem"] button:has-text("Download")',
                'div[role="menuitem"] button:has-text("download")',
                'div[role="menuitem"] span:has-text("Download")',
                'div[role="menuitem"] span:has-text("download")',
            ]

            download_menuitem = None
            for selector in download_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logger.info(f"🎯 Found {len(elements)} elements with selector: {selector}")
                        for i, element in enumerate(elements):
                            text = await element.text_content()
                            is_visible = await element.is_visible()
                            is_enabled = await element.is_enabled()

                            logger.info(f"   └─ Element {i}: text='{text}', visible={is_visible}, enabled={is_enabled}")

                            # Look for Download in the text content
                            if is_visible and is_enabled and text and "download" in text.lower():
                                download_menuitem = element
                                logger.info(f"✅ Found Download menuitem: '{text}'")
                                break

                        if download_menuitem:
                            break
                except:
                    continue

            if download_menuitem:
                await download_menuitem.click()
                await self.human_like_delay(2, 4)
                logger.info("✅ Clicked Download menuitem")
            else:
                logger.error("❌ Failed to find Download menuitem")

                # Debug: List all menuitems on the page
                logger.info("🔍 Debug: Listing all menuitems on the page...")
                try:
                    all_menuitems = await page.query_selector_all('div[role="menuitem"]')
                    logger.info(f"📊 Found {len(all_menuitems)} total menuitems")

                    for i, element in enumerate(all_menuitems):
                        try:
                            text = await element.text_content()
                            is_visible = await element.is_visible()

                            if text and text.strip():
                                logger.info(f"   └─ Menuitem {i}: '{text.strip()}' (visible: {is_visible})")
                        except:
                            continue
                except Exception as e:
                    logger.error(f"❌ Error listing menuitems: {e}")

                return False

        except Exception as e:
            logger.error(f"❌ Failed to click Download menuitem: {e}")
            return False

        # Step 3: Wait for format menu to appear
        logger.info("🔍 Step 3: Waiting for format menu to appear...")
        format_menu_appeared = await self.wait_for_format_menu(page, timeout=10000)

        if not format_menu_appeared:
            logger.warning("⚠️ Format menu did not appear, trying to find WAV menuitem anyway...")

        # Step 4: Click WAV menuitem - div[role="menuitem"] containing div with "WAV" text
        logger.info("🔍 Step 4: Looking for WAV menuitem...")
        try:
            # Try to find WAV menuitem with nested div containing "WAV" text
            wav_selectors = [
                'div[role="menuitem"] div:has-text("WAV")',
                'div[role="menuitem"] div:has-text("wav")',
                'div[role="menuitem"]:has-text("WAV")',
                'div[role="menuitem"]:has-text("wav")',
                'div[role="menuitem"] button:has-text("WAV")',
                'div[role="menuitem"] button:has-text("wav")',
                'div[role="menuitem"] span:has-text("WAV")',
                'div[role="menuitem"] span:has-text("wav")',
                'button:has-text("WAV")',
                'button:has-text("wav")',
                'div:has-text("WAV")',
                'div:has-text("wav")',
            ]

            wav_menuitem = None
            for selector in wav_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logger.info(f"🎯 Found {len(elements)} elements with selector: {selector}")
                        for i, element in enumerate(elements):
                            text = await element.text_content()
                            is_visible = await element.is_visible()
                            is_enabled = await element.is_enabled()

                            logger.info(f"   └─ Element {i}: text='{text}', visible={is_visible}, enabled={is_enabled}")

                            # Look for WAV in the text content
                            if is_visible and is_enabled and text and "wav" in text.lower():
                                wav_menuitem = element
                                logger.info(f"✅ Found WAV menuitem: '{text}'")
                                break

                        if wav_menuitem:
                            break
                except:
                    continue

            if wav_menuitem:
                await wav_menuitem.click()
                await self.human_like_delay(2, 4)
                logger.info("✅ Clicked WAV menuitem")
                return True
            else:
                logger.error("❌ Failed to find WAV menuitem")

                # Debug: List all menuitems on the page
                logger.info("🔍 Debug: Listing all menuitems on the page...")
                try:
                    all_menuitems = await page.query_selector_all('div[role="menuitem"]')
                    logger.info(f"📊 Found {len(all_menuitems)} total menuitems")

                    for i, element in enumerate(all_menuitems):
                        try:
                            text = await element.text_content()
                            is_visible = await element.is_visible()

                            if text and text.strip():
                                logger.info(f"   └─ Menuitem {i}: '{text.strip()}' (visible: {is_visible})")
                        except:
                            continue
                except Exception as e:
                    logger.error(f"❌ Error listing menuitems: {e}")

                return False

        except Exception as e:
            logger.error(f"❌ Failed to click WAV menuitem: {e}")
            return False

    async def check_downloaded_files(self):
        """Check for downloaded files in common download locations"""
        logger.info("🔍 Checking for downloaded files...")

        # Common download locations to check
        download_locations = [
            self.download_path,  # Our custom path
            os.path.expanduser("~/Downloads"),  # User's Downloads folder
            os.path.expanduser("~/downloads"),  # Alternative downloads folder
            "/tmp",  # Temporary directory
            "/var/tmp",  # Alternative temp directory
        ]

        all_files = []

        for location in download_locations:
            try:
                if os.path.exists(location):
                    files = os.listdir(location)
                    audio_files = [f for f in files if f.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".flac"))]

                    if audio_files:
                        logger.info(f"📁 Found {len(audio_files)} audio files in {location}:")
                        for file in audio_files:
                            file_path = os.path.join(location, file)
                            file_size = os.path.getsize(file_path)
                            # Check if file was created recently (within last 5 minutes)
                            file_age = time.time() - os.path.getctime(file_path)
                            if file_age < 300:  # 5 minutes
                                logger.info(f"   └─ {file} ({file_size} bytes) - Recent file")
                                all_files.append(
                                    {"file": file, "path": file_path, "size": file_size, "location": location}
                                )
                            else:
                                logger.info(f"   └─ {file} ({file_size} bytes) - Older file")
            except Exception as e:
                logger.debug(f"Could not check {location}: {e}")

        if all_files:
            logger.info(f"✅ Found {len(all_files)} recent audio files")
            return all_files
        else:
            logger.info("ℹ️ No recent audio files found")
            return []

    async def copy_files_to_download_path(self, files):
        """Copy downloaded files to our specified download path"""
        if not files:
            return []

        copied_files = []
        for file_info in files:
            try:
                source_path = file_info["path"]
                filename = file_info["file"]
                dest_path = os.path.join(self.download_path, filename)

                # Check if file is already in the target location
                if os.path.abspath(source_path) == os.path.abspath(dest_path):
                    logger.info(f"📋 File {filename} already in target location, skipping copy")
                    copied_files.append(dest_path)
                else:
                    # Copy file to our download directory
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"📋 Copied {filename} to {self.download_path}")
                    copied_files.append(dest_path)

            except Exception as e:
                logger.warning(f"⚠️ Failed to copy {file_info['file']}: {e}")

        return copied_files

    async def generate_music_with_download(self, prompt: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Generate music with complete automation and menuitem download handling"""

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise Exception("Playwright not installed. Run: pip install playwright && playwright install chromium")

        # Start virtual display
        if not self.start_virtual_display():
            raise Exception("Could not start virtual display")

        try:
            async with async_playwright() as p:
                # Launch browser with virtual display
                browser = await p.chromium.launch(
                    headless=False,  # Use virtual display instead of headless
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                        "--disable-extensions",
                        "--disable-plugins",
                        "--memory-pressure-off",
                        "--max_old_space_size=512",
                        "--single-process",
                        "--disable-background-timer-throttling",
                        "--disable-backgrounding-occluded-windows",
                        "--disable-renderer-backgrounding",
                        "--disable-ipc-flooding-protection",
                    ],
                )

                try:
                    # Create context with realistic settings
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        viewport={"width": 1920, "height": 1080},
                        locale="en-US",
                        timezone_id="America/New_York",
                        accept_downloads=True,
                    )

                    page = await context.new_page()

                    # Set up network interception
                    page.on("request", self.handle_network_request)
                    page.on("response", self.handle_network_response)

                    # Set up download handling
                    downloaded_files = []

                    async def handle_download(download):
                        file_path = await self.handle_download(download)
                        downloaded_files.append(file_path)

                    page.on("download", handle_download)

                    # Step 1: Navigate to ProducerAI
                    logger.info("🌐 Navigating to ProducerAI...")
                    await page.goto("https://www.producer.ai/", timeout=60000)
                    await page.wait_for_load_state("domcontentloaded", timeout=30000)
                    await self.human_like_delay(2, 4)

                    # Step 2: Click "Continue with Google" button
                    logger.info("🔍 Looking for Google login button...")
                    google_button = await page.wait_for_selector(
                        'button:has-text("Continue with Google")', timeout=10000
                    )
                    logger.info("✅ Found Google button")
                    await google_button.click()
                    await self.human_like_delay(2, 4)

                    # Step 3: Handle Google login page
                    logger.info("📧 Handling Google login...")
                    email_input = await page.wait_for_selector('input[type="email"]', timeout=10000)
                    logger.info("✅ Found email input")
                    await self.type_like_human(page, 'input[type="email"]', self.email)
                    await self.human_like_delay(1, 2)

                    next_button = await page.wait_for_selector('button:has-text("Next")', timeout=10000)
                    logger.info("✅ Found Next button")
                    await next_button.click()
                    await self.human_like_delay(2, 4)

                    # Step 4: Handle password page
                    logger.info("🔒 Handling password input...")
                    password_input = await page.wait_for_selector('input[type="password"]', timeout=10000)
                    logger.info("✅ Found password input")
                    await self.type_like_human(page, 'input[type="password"]', self.password)
                    await self.human_like_delay(1, 2)

                    # Handle checkbox if present
                    try:
                        checkbox = await page.wait_for_selector('input[type="checkbox"]', timeout=2000)
                        if checkbox and await checkbox.is_visible():
                            logger.info("☑️ Found checkbox, clicking to avoid detection")
                            await checkbox.click()
                            await self.human_like_delay(0.5, 1)
                    except:
                        logger.debug("No checkbox found")

                    submit_button = await page.wait_for_selector('button:has-text("Next")', timeout=10000)
                    logger.info("✅ Found submit button")
                    await submit_button.click()
                    await self.human_like_delay(3, 6)

                    # Step 5: Wait for redirect back to ProducerAI
                    logger.info("⏳ Waiting for redirect to ProducerAI...")
                    try:
                        await page.wait_for_url("**/producer.ai/**", timeout=30000)
                        logger.info("✅ Successfully redirected to ProducerAI")
                    except:
                        current_url = page.url
                        logger.info(f"Current URL: {current_url}")
                        if "producer.ai" in current_url:
                            logger.info("✅ Already on ProducerAI")
                        else:
                            logger.warning("⚠️ Not redirected to ProducerAI, continuing anyway")

                    await self.human_like_delay(2, 4)

                    # Step 6: Navigate to create page
                    logger.info("🎵 Navigating to create page...")
                    await page.goto("https://www.producer.ai/create", timeout=30000)
                    await page.wait_for_load_state("domcontentloaded", timeout=30000)
                    await self.human_like_delay(2, 4)

                    # Step 7: Find and type in the prompt textarea
                    logger.info("📝 Looking for prompt textarea...")
                    prompt_textarea = await page.wait_for_selector(
                        'textarea[placeholder="Ask Producer..."]', timeout=10000
                    )
                    logger.info("✅ Found prompt textarea")

                    # Type the prompt
                    await self.type_like_human(page, 'textarea[placeholder="Ask Producer..."]', prompt)
                    await self.human_like_delay(1, 2)

                    # Step 8: Press Enter to validate
                    logger.info("⌨️ Pressing Enter to validate...")
                    await page.keyboard.press("Enter")
                    await self.human_like_delay(2, 4)

                    # Step 9: Wait for generation to complete
                    generation_completed = await self.wait_for_generation_completion(page)

                    # Step 10: Execute menuitem download workflow
                    download_success = await self.execute_menuitem_download_workflow(page)

                    # Initialize downloaded_files
                    downloaded_files = []

                    # Step 11: Wait for download and check for files
                    if download_success:
                        logger.info("⏳ Waiting for download to complete...")
                        await self.human_like_delay(10, 15)  # Wait longer for download

                        # Check for downloaded files
                        found_files = await self.check_downloaded_files()

                        # Copy files to our download path
                        if found_files:
                            downloaded_files = await self.copy_files_to_download_path(found_files)
                    else:
                        # Even if download_success is False, check for files anyway
                        logger.info("⏳ Download workflow failed, but checking for files anyway...")
                        await self.human_like_delay(5, 10)

                        # Check for downloaded files
                        found_files = await self.check_downloaded_files()

                        # Copy files to our download path
                        if found_files:
                            downloaded_files = await self.copy_files_to_download_path(found_files)

                    # Generate a unique song ID for tracking
                    song_id = f"complete_workflow_{int(time.time())}"

                    logger.info(f"✅ Music generation completed: {song_id}")
                    logger.info(f"Generation completed: {generation_completed}")
                    logger.info(f"Download success: {download_success}")

                    return {
                        "success": True,
                        "song_id": song_id,
                        "title": title,
                        "audio_url": f"Files saved to: {os.path.abspath(self.download_path)}",
                        "method": "complete_workflow_with_download",
                        "timestamp": time.time(),
                        "prompt": prompt,
                        "generation_completed": generation_completed,
                        "download_success": download_success,
                        "downloaded_files": downloaded_files,
                        "download_path": os.path.abspath(self.download_path),
                        "network_urls": self.download_urls,
                    }

                except Exception as e:
                    logger.error(f"❌ Complete workflow failed: {e}")
                    raise
                finally:
                    await browser.close()

        except Exception as e:
            logger.error(f"❌ Complete workflow failed: {e}")
            raise
        finally:
            # Stop virtual display
            self.stop_virtual_display()


def create_complete_workflow_with_download(
    email: str = "vibeway.business@gmail.com", password: str = "ouiOUI2007", download_path: str = "./downloads"
) -> CompleteWorkflowWithDownload:
    """Create complete workflow with music generation and menuitem download handling"""
    return CompleteWorkflowWithDownload(email, password, download_path)


# Example usage
async def main():
    """Test complete workflow with music generation and download"""

    # You can specify any download path you want
    download_path = "./complete_workflow_downloads"  # Change this to your preferred path

    service = create_complete_workflow_with_download(download_path=download_path)

    try:
        logger.info("🚀 Starting complete workflow with music generation and download...")
        result = await service.generate_music_with_download(
            prompt="create an instrumental techno song", title="Techno Beat"
        )

        logger.info("🎵 Complete workflow completed!")
        logger.info(f"Song ID: {result['song_id']}")
        logger.info(f"Title: {result['title']}")
        logger.info(f"Audio: {result['audio_url']}")
        logger.info(f"Method: {result['method']}")
        logger.info(f"Prompt: {result['prompt']}")
        logger.info(f"Generation completed: {result['generation_completed']}")
        logger.info(f"Download success: {result['download_success']}")
        logger.info(f"Download path: {result['download_path']}")
        logger.info(f"Network URLs captured: {len(result['network_urls'])}")

        if result["downloaded_files"]:
            logger.info("📁 Downloaded files:")
            for file in result["downloaded_files"]:
                logger.info(f"   └─ {file}")

        if result["network_urls"]:
            logger.info("🌐 Network URLs captured:")
            for url in result["network_urls"]:
                logger.info(f"   └─ {url}")

    except Exception as e:
        logger.error(f"❌ Complete workflow failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
