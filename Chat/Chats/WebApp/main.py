# Chat/Chats/WebApp/main.py
"""Web Chats test flow for the Furgechat web app.

Test scenario
-------------
1. (Optional) Log in first, if ``login.enabled`` is true in credentials.json.
2. Open the "Chats" tab.
3. Print every visible chat (id, name, and last-message preview).

Outcome contract
----------------
- On success: prints the list of chats and exits 0. An empty list is still a
  success (it just means there are no chats to show), logged as a warning.
- On any failure: logs ``[FAIL]``, saves a timestamped screenshot to
  ``screenshots/``, and exits with a non-zero status code.

Usage
-----
    python main.py [--headless]

``--headless`` runs Chrome without a visible window (useful on CI servers); it
overrides the ``browser.headless`` setting in credentials.json.
"""

from __future__ import annotations

import argparse
import sys
import time

from pages.chat_list_page import ChatListPage
from pages.login_page import LoginPage
from utils.config import load_config
from utils.driver_factory import create_driver
from utils.logger import get_logger
from utils.screenshot import save_screenshot

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Furgechat Web Chats automation.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome in headless mode (no visible window) — useful for CI.",
    )
    return parser.parse_args()


def _maybe_login(driver, base_url, login_cfg, timeout, logger) -> bool:
    """Authenticate first if the chats screen requires a session.

    Args:
        driver: The active WebDriver.
        base_url: The app's base URL (no trailing slash).
        login_cfg: The ``login`` block from credentials.json.
        timeout: Explicit-wait timeout in seconds.
        logger: The configured logger.

    Returns:
        True to continue (login disabled, or login succeeded); False if a
        required login failed.
    """
    if not login_cfg.get("enabled", False):
        return True  # Login not required for this run.

    login_url = base_url + login_cfg.get("path", "/login")
    username = login_cfg.get("username", "admin")
    login_page = LoginPage(driver, timeout=timeout)
    login_page.open(login_url)
    logger.info("Login enabled — signing in as '%s' before opening chats.", username)
    login_page.login(username, login_cfg.get("password", "password"))

    if not login_page.is_login_successful():
        logger.error("Login failed; cannot reach the chats list.")
        return False
    logger.info("Login successful.")
    return True


def main() -> int:
    """Run the chats-listing test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if the chats screen loaded and was read, else
        ``EXIT_FAILURE``.
    """
    args = _parse_args()
    logger = get_logger("web_chats")
    driver = None
    start = time.perf_counter()
    try:
        # Pull all settings from credentials.json (never hardcoded).
        config = load_config()
        if args.headless:
            config.setdefault("browser", {})["headless"] = True
            logger.info("Headless mode enabled via --headless.")
        base_url = config["base_url"].rstrip("/")
        chats_url = base_url + config.get("chats_path", "/chats")
        timeout = config.get("timeouts", {}).get("explicit_wait_seconds", 20)
        login_cfg = config.get("login", {})

        logger.info("Starting Web Chats test against %s", chats_url)
        driver = create_driver(config)

        # Step 1: optional authentication.
        if not _maybe_login(driver, base_url, login_cfg, timeout, logger):
            logger.error("[FAIL] Could not sign in; aborting before the chats list.")
            save_screenshot(driver, label="login_failed")
            return EXIT_FAILURE

        # Step 2: open the Chats tab.
        chat_page = ChatListPage(driver, timeout=timeout)
        chat_page.open(chats_url)
        logger.info("Opened the 'Chats' tab.")

        # If the screen did not render, the app most likely required a login.
        if not chat_page.is_loaded():
            logger.error(
                "[FAIL] The chats list did not load. If the app requires login, set "
                "login.enabled=true in credentials.json and run again."
            )
            save_screenshot(driver, label="chats_not_loaded")
            return EXIT_FAILURE

        # Step 3: read and print every visible chat.
        chats = chat_page.get_chats()
        if not chats:
            logger.warning("No chats are currently visible under the 'Chats' tab.")
            logger.info(
                "[PASS] Chats screen loaded; 0 chats to list (%.1fs).",
                time.perf_counter() - start,
            )
            return EXIT_SUCCESS

        logger.info("Found %d chat(s) under the 'Chats' tab:", len(chats))
        for chat in chats:
            logger.info('  [%s] %s - "%s"', chat["id"], chat["name"], chat["preview"])
        logger.info(
            "[PASS] Listed %d chat(s) (%.1fs).", len(chats), time.perf_counter() - start
        )
        return EXIT_SUCCESS

    # Broad catch is intentional: the failure contract (clear message +
    # screenshot + non-zero exit) must hold for ANY error.
    except Exception:
        logger.exception("[FAIL] Chats test aborted due to an unexpected error.")
        if driver is not None:
            try:
                shot = save_screenshot(driver, label="chats_error")
                logger.error("Screenshot saved to %s", shot)
            except Exception:
                logger.error("Could not capture a screenshot after the failure.")
        return EXIT_FAILURE

    finally:
        # Always release the browser, even on failure.
        if driver is not None:
            driver.quit()
            logger.info("Browser closed.")


if __name__ == "__main__":
    sys.exit(main())
