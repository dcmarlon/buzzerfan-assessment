# Auth/Registration/WebApp/main.py
"""Web Registration test flow for the Furgechat web app.

Test scenario
-------------
1. Open the Furgechat registration page.
2. Generate a UNIQUE username + email (timestamp-based) so re-runs never clash.
3. Fill in the new-account form and submit it.
4. Verify that registration succeeded (the registration form goes away).

Outcome contract
----------------
- On success: logs "REGISTRATION SUCCESSFUL" and exits 0.
- On any failure: logs a clear error, saves a timestamped screenshot to
  ``screenshots/``, and exits with a non-zero status code.
"""

from __future__ import annotations

import sys

from pages.register_page import RegisterPage
from utils.config import load_config
from utils.data_generator import from_config
from utils.driver_factory import create_driver
from utils.logger import get_logger
from utils.screenshot import save_screenshot

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def main() -> int:
    """Run the registration test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if registration is confirmed, else ``EXIT_FAILURE``.
    """
    logger = get_logger("web_register")
    driver = None
    try:
        # Pull all settings from credentials.json (never hardcoded).
        config = load_config()
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

        # Confirm success by waiting for the registration form to go away.
        if register_page.is_registration_successful():
            logger.info("REGISTRATION SUCCESSFUL for username '%s'.", user["username"])
            return EXIT_SUCCESS

        # Did not succeed — capture any on-screen error, then save evidence.
        error_text = register_page.get_error_text()
        message = error_text or (
            "Registration did not complete — still on the register page "
            "(the username/email may already exist or a field was rejected)."
        )
        logger.error("REGISTRATION FAILED: %s", message)
        shot = save_screenshot(driver, label="register_failed")
        logger.error("Screenshot saved to %s", shot)
        return EXIT_FAILURE

    # Broad catch is intentional: the failure contract (clear message +
    # screenshot + non-zero exit) must hold for ANY error, including config
    # problems, browser crashes, and missing elements.
    except Exception:
        logger.exception("Registration test aborted due to an unexpected error.")
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
