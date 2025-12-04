#!/usr/bin/env python3
"""
Alta Ski Area Parking Reservation Bot

This bot automatically reserves parking spots at Alta Ski Area
for upcoming Saturday and Sunday.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alta_parking_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
EMAIL = os.getenv('ALTA_EMAIL')
PASSWORD = os.getenv('ALTA_PASSWORD')
PARKING_PASS = os.getenv('PARKING_PASS_NUMBER')
BASE_URL = 'https://reserve.altaparking.com/'


def get_target_dates():
    """
    Calculate the Saturday and Sunday dates to reserve (7 days ahead).
    Returns list of date strings.
    """
    today = datetime.now()
    target_dates = []

    # Look 7 days ahead
    for i in range(7, 8):  # 7 days from now
        future_date = today + timedelta(days=i)
        # Check if it's Saturday (5) or Sunday (6)
        if future_date.weekday() in [5, 6]:
            target_dates.append(future_date)

    return target_dates


def make_reservation(headless=True):
    """
    Main function to log in and make parking reservations.

    Args:
        headless: Run browser in headless mode (default True)
    """
    if not EMAIL or not PASSWORD:
        logger.error("Missing credentials. Please check your .env file.")
        return False

    logger.info("Starting Alta parking reservation bot...")
    logger.info(f"Email: {EMAIL}")
    logger.info(f"Parking Pass: {PARKING_PASS}")

    target_dates = get_target_dates()
    if not target_dates:
        logger.info("No Saturday or Sunday found 7 days ahead. Nothing to reserve.")
        return True

    logger.info(f"Target dates to reserve: {[d.strftime('%Y-%m-%d (%A)') for d in target_dates]}")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            # Navigate to the site
            logger.info(f"Navigating to {BASE_URL}")
            page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
            time.sleep(2)  # Let React fully load

            # Look for login form
            logger.info("Looking for login form...")

            # Try common login field selectors
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email" i]',
                'input[id*="email" i]',
                '#email',
                '[data-testid="email"]'
            ]

            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                '#password',
                '[data-testid="password"]'
            ]

            # Find and fill email field
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = page.wait_for_selector(selector, timeout=5000)
                    if email_field:
                        logger.info(f"Found email field with selector: {selector}")
                        break
                except:
                    continue

            if not email_field:
                logger.error("Could not find email input field")
                page.screenshot(path='error_no_email_field.png')
                return False

            # Find and fill password field
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = page.wait_for_selector(selector, timeout=5000)
                    if password_field:
                        logger.info(f"Found password field with selector: {selector}")
                        break
                except:
                    continue

            if not password_field:
                logger.error("Could not find password input field")
                page.screenshot(path='error_no_password_field.png')
                return False

            # Fill in credentials
            logger.info("Filling in credentials...")
            email_field.fill(EMAIL)
            password_field.fill(PASSWORD)
            time.sleep(1)

            # Find and click login button
            login_button_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'input[type="submit"]',
                '[data-testid="login-button"]'
            ]

            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = page.locator(selector).first
                    if login_button.is_visible():
                        logger.info(f"Found login button with selector: {selector}")
                        break
                except:
                    continue

            if not login_button:
                logger.error("Could not find login button")
                page.screenshot(path='error_no_login_button.png')
                return False

            logger.info("Clicking login button...")
            login_button.click()

            # Wait for navigation after login
            time.sleep(3)

            # Check if login was successful
            current_url = page.url
            logger.info(f"Current URL after login: {current_url}")

            # Look for dashboard or reservation interface
            page.screenshot(path='after_login.png')
            logger.info("Screenshot saved: after_login.png")

            # Try to find reservation/calendar interface
            # This part will need to be customized based on the actual UI
            # Common patterns: calendar, date picker, reservation button

            calendar_selectors = [
                '[role="button"]:has-text("Reserve")',
                'button:has-text("Make Reservation")',
                '[data-testid="calendar"]',
                '.calendar',
                '[class*="calendar"]',
                '[class*="reservation"]'
            ]

            # Wait a bit for the page to fully load
            time.sleep(2)

            # Take a screenshot to see what we're working with
            page.screenshot(path='dashboard.png')
            logger.info("Dashboard screenshot saved. Please check dashboard.png to see the interface.")

            # At this point, we need to interact with the actual reservation system
            # The specific selectors will depend on how the site is structured

            logger.info("=== NEXT STEPS ===")
            logger.info("Please check the screenshots (after_login.png and dashboard.png)")
            logger.info("to see what the interface looks like. I may need to update")
            logger.info("the selectors to match the actual reservation interface.")

            # Keep browser open for a moment if not headless
            if not headless:
                logger.info("Browser will stay open for 30 seconds for inspection...")
                time.sleep(30)

            return True

        except PlaywrightTimeout as e:
            logger.error(f"Timeout error: {e}")
            page.screenshot(path='error_timeout.png')
            return False

        except Exception as e:
            logger.error(f"Error during reservation: {e}")
            page.screenshot(path='error_general.png')
            import traceback
            logger.error(traceback.format_exc())
            return False

        finally:
            browser.close()


def test_mode():
    """Run bot in test mode with visible browser."""
    logger.info("Running in TEST MODE (browser visible)...")
    return make_reservation(headless=False)


if __name__ == '__main__':
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        success = test_mode()
    else:
        success = make_reservation()

    sys.exit(0 if success else 1)
