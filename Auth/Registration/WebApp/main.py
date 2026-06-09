# Auth/Registration/WebApp/main.py
"""Web Registration test flow for the Furgechat web app.

Test scenario
-------------
1. Open the Furgechat registration page.
2. Generate a UNIQUE username + email (timestamp-based) so re-runs never clash.
3. Fill in the new-account form and submit it.
4. Verify that registration succeeded (the "Account created" confirmation).

Outcome contract
----------------
- On success: logs ``[PASS]`` and exits 0.
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

from pages.register_page import RegisterPage
from utils.config import load_config
from utils.data_generator import from_config
from utils.driver_factory import create_driver
from utils.logger import get_logger
from utils.screenshot import save_screenshot

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Furgechat Web Registration automation.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome in headless mode (no visible window) — useful for CI.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the registration test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if registration is confirmed, else ``EXIT_FAILURE``.
    """
    args = _parse_args()
    logger = get_logger("web_register")
    driver = None
    start = time.perf_counter()
    try:
        # Pull all settings from credentials.json (never hardcoded).
        config = load_config()
        if args.headless:
            config.setdefault("browser", {})["headless"] = True
            logger.info("Headless mode enabled via --headless.")
        register_url = config["base_url"].rstrip("/") + config.get("register_path", "/register")
        timeout = config.get("timeouts", {}).get("explicit_wait_seconds", 20)

        # Build a unique account so the test is repeatable.
        user = from_config(config.get("new_user", {}))

        logger.info("Starting Web Registration test against %s", register_url)
        logger.info(
            "Generated unique account -> username='%s', email='%s'",
            user["username"],
            user["email"],
        )

        driver = create_driver(config)
        register_page = RegisterPage(driver, timeout=timeout)
        register_page.open(register_url)
        logger.info("Opened registration page; submitting the new-account form.")
        register_page.register(user["username"], user["email"], user["password"])

        # Confirm success via the app's "Account created" confirmation.
        if register_page.is_registration_successful():
            logger.info(
                "[PASS] Registration succeeded for username '%s' (%.1fs).",
                user["username"],
                time.perf_counter() - start,
            )
            return EXIT_SUCCESS

        # Did not succeed — capture any on-screen error, then save evidence.
        error_text = register_page.get_error_text()
        message = error_text or (
            "Registration did not complete — still on the register page "
            "(the username/email may already exist or a field was rejected)."
        )
        logger.error("[FAIL] Registration failed: %s", message)
        shot = save_screenshot(driver, label="register_failed")
        logger.error("Screenshot saved to %s", shot)
        return EXIT_FAILURE

    # Broad catch is intentional: the failure contract (clear message +
    # screenshot + non-zero exit) must hold for ANY error, including config
    # problems, browser crashes, and missing elements.
    except Exception:
        logger.exception("[FAIL] Registration test aborted due to an unexpected error.")
        if driver is not None:
            try:
                shot = save_screenshot(driver, label="register_error")
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
