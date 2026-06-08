# Chat/Chats/Android/main.py
"""Android Chats test flow for the Furgechat app.

Test scenario
-------------
1. Launch the app (opens the login screen).
2. Log in as admin.
3. Wait for the "All Messages Dashboard" header.
4. Read every chat row (a Button whose content-desc is name + last message).
5. Print each chat, skipping dashboard controls (e.g. "Logout").
6. Assert at least one chat is present (fail loud if zero).
7. Print the total count.

Outcome contract
----------------
- On success: prints the chat list + count and logs [PASS] with elapsed seconds.
- On any failure: logs [FAIL], saves a timestamped screenshot to
  ``screenshots/``, and exits with a non-zero status code.
- The Appium session is always closed in a finally block.

Note on output: on Android the chat name and last message are fused into a
single ``content-desc`` with no delimiter, so (per the spec) each chat is
printed as its raw content-desc rather than a fabricated name/message split.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.driver_factory import create_driver, load_credentials, load_settings
from utils.logger import get_logger

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Screenshots are written here on failure (created on demand).
_SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"


def _save_failure_screenshot(driver, logger, label: str = "chats_failure") -> None:
    """Save a timestamped failure screenshot to screenshots/, logging the path.

    Args:
        driver: The active Appium driver.
        logger: The configured logger.
        label: Filename prefix for the screenshot.
    """
    try:
        _SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = _SCREENSHOT_DIR / f"{label}_{timestamp}.png"
        driver.save_screenshot(str(path))
        logger.error("Screenshot saved to %s", path)
    except Exception:
        logger.error("Could not capture a screenshot after the failure.")


def main() -> int:
    """Run the Android chats-listing test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if at least one chat is listed, else
        ``EXIT_FAILURE``.
    """
    logger = get_logger("android_chats")
    driver = None
    try:
        # Load static settings and per-machine credentials (never hardcoded).
        settings = load_settings()
        credentials = load_credentials()
        timeouts = settings.get("timeouts", {})
        element_timeout = timeouts.get("element_wait_seconds", 20)
        dashboard_timeout = timeouts.get("dashboard_wait_seconds", 15)
        username = credentials["username"]
        password = credentials["password"]

        logger.info(
            "Starting Android Chats test (Appium server %s).",
            settings.get("appium_server", "http://127.0.0.1:4723"),
        )
        start = time.perf_counter()
        driver = create_driver(settings, credentials)

        # Steps 1-2: log in.
        login_page = LoginPage(driver, timeout=element_timeout)
        login_page.wait_until_loaded()
        login_page.login(username, password)

        # Step 3: confirm the dashboard rendered (proves login succeeded).
        dashboard = DashboardPage(driver, timeout=element_timeout)
        if not dashboard.wait_until_loaded(timeout=dashboard_timeout):
            logger.error(
                "[FAIL] 'All Messages Dashboard' did not load within %ss after "
                "login. Login may have failed or the screen changed.",
                dashboard_timeout,
            )
            _save_failure_screenshot(driver, logger)
            return EXIT_FAILURE

        logger.info("Logged in as %s", username)
        logger.info("Dashboard loaded")

        # Steps 4-5: read the chat rows, noting any buttons that were skipped.
        chats, skipped = dashboard.get_chats()
        for skipped_desc in skipped:
            logger.info("Skipped non-chat button: %s", skipped_desc)

        # Step 6: fail loud if there are no chats at all.
        if not chats:
            logger.error(
                "[FAIL] No chat rows found on the dashboard. Either the chat-row "
                "selector broke or the admin account has no chats."
            )
            _save_failure_screenshot(driver, logger)
            return EXIT_FAILURE

        # Step 7: print the chats and the count.
        logger.info("Chats visible on dashboard:")
        for index, content_desc in enumerate(chats, start=1):
            logger.info("  %d. %s", index, content_desc)
        logger.info("Found %d chats", len(chats))

        elapsed = time.perf_counter() - start
        logger.info("[PASS] Chats listing completed in %.1fs", elapsed)
        return EXIT_SUCCESS

    # Broad catch is intentional: the failure contract (clear [FAIL] message +
    # screenshot + non-zero exit) must hold for ANY error.
    except Exception:
        logger.exception("[FAIL] Chats test aborted due to an unexpected error.")
        if driver is not None:
            _save_failure_screenshot(driver, logger, label="chats_error")
        return EXIT_FAILURE

    finally:
        # Always release the Appium session, even on failure.
        if driver is not None:
            driver.quit()
            logger.info("Appium session closed.")


if __name__ == "__main__":
    sys.exit(main())
