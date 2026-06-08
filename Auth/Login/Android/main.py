# Auth/Login/Android/main.py
"""Android Login test flow for the Furgechat app.

Test scenario
-------------
1. Start the Appium driver with the configured capabilities.
2. Wait for the login screen (username field) to be visible.
3. (Backup) verify the positional EditTexts are really the username/password
   fields by checking their hint text; warn if not.
4. Type the credentials and tap the Login button.
5. Wait up to 15 seconds for the "All Messages Dashboard" header to appear.
6. On success: log [PASS] with the elapsed seconds and exit 0.
7. On failure: log [FAIL], save a timestamped screenshot, and exit 1.
8. Always quit the driver in a finally block.
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


def _save_failure_screenshot(driver, logger) -> None:
    """Save a timestamped failure screenshot to screenshots/, logging the path.

    Args:
        driver: The active Appium driver.
        logger: The configured logger.
    """
    try:
        _SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = _SCREENSHOT_DIR / f"login_failure_{timestamp}.png"
        driver.save_screenshot(str(path))
        logger.error("Screenshot saved to %s", path)
    except Exception:
        logger.error("Could not capture a screenshot after the failure.")


def _verify_field_hints(login_page: LoginPage, logger) -> None:
    """Backup check that the positional EditTexts are the expected fields.

    Flutter positional selectors break if the form layout changes; comparing the
    hint text catches that early. This is non-fatal — it only warns.

    Args:
        login_page: The login page object.
        logger: The configured logger.
    """
    username_hint = login_page.get_username_hint()
    if username_hint != LoginPage.EXPECTED_USERNAME_HINT:
        logger.warning(
            "Username field hint was %r, expected %r — the positional selector "
            "may have shifted; re-capture with Appium Inspector.",
            username_hint,
            LoginPage.EXPECTED_USERNAME_HINT,
        )

    password_hint = login_page.get_password_hint()
    if password_hint != LoginPage.EXPECTED_PASSWORD_HINT:
        logger.warning(
            "Password field hint was %r, expected %r — the positional selector "
            "may have shifted; re-capture with Appium Inspector.",
            password_hint,
            LoginPage.EXPECTED_PASSWORD_HINT,
        )


def main() -> int:
    """Run the Android login test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if login is confirmed, otherwise ``EXIT_FAILURE``.
    """
    logger = get_logger("android_login")
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
            "Starting Android Login test (Appium server %s).",
            settings.get("appium_server", "http://127.0.0.1:4723"),
        )
        driver = create_driver(settings, credentials)

        # Step 2: wait for the login screen.
        login_page = LoginPage(driver, timeout=element_timeout)
        login_page.wait_until_loaded()
        logger.info("Login screen loaded.")

        # Step 3: backup verification of the positional fields (non-fatal).
        _verify_field_hints(login_page, logger)

        # Step 4: enter credentials and submit.
        logger.info("Entering credentials for user '%s' and tapping Login.", username)
        login_page.login(username, password)

        # Step 5: wait (max 15s) for the post-login dashboard, timing it.
        dashboard = DashboardPage(driver, timeout=dashboard_timeout)
        start = time.perf_counter()
        if dashboard.wait_until_loaded():
            elapsed = time.perf_counter() - start
            logger.info(
                "[PASS] Login succeeded — 'All Messages Dashboard' appeared in %.2fs.",
                elapsed,
            )
            return EXIT_SUCCESS

        # Step 7: dashboard never appeared within the timeout.
        logger.error(
            "[FAIL] 'All Messages Dashboard' did not appear within %ss after login. "
            "Check the credentials and the login flow.",
            dashboard_timeout,
        )
        _save_failure_screenshot(driver, logger)
        return EXIT_FAILURE

    # Broad catch is intentional: the failure contract (clear [FAIL] message +
    # screenshot + non-zero exit) must hold for ANY error, including session
    # start-up problems and missing elements.
    except Exception:
        logger.exception("[FAIL] Login test aborted due to an unexpected error.")
        if driver is not None:
            _save_failure_screenshot(driver, logger)
        return EXIT_FAILURE

    finally:
        # Always release the Appium session, even on failure.
        if driver is not None:
            driver.quit()
            logger.info("Appium session closed.")


if __name__ == "__main__":
    sys.exit(main())
