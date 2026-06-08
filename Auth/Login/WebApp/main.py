# Auth/Login/WebApp/main.py
"""Web Login test flow for the Furgechat web app.

Test scenario
-------------
1. (Optional) Register the account first — this app stores users client-side
   per browser session, so a fresh session must create the account before it
   can log in. Controlled by "register_first" in credentials.json.
2. Open the Furgechat login page and log in with the configured credentials.
3. Verify that login succeeded (the login form is left behind).

Outcome contract
----------------
- On success: logs "LOGIN SUCCESSFUL" and exits 0.
- On any failure: logs a clear error, saves a timestamped screenshot to
  ``screenshots/``, and exits with a non-zero status code.
"""

from __future__ import annotations

import sys

from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from utils.config import load_config
from utils.driver_factory import create_driver
from utils.logger import get_logger
from utils.screenshot import save_screenshot

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def main() -> int:
    """Run the login test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if login is confirmed, otherwise ``EXIT_FAILURE``.
    """
    logger = get_logger("web_login")
    driver = None
    try:
        # Pull all settings/credentials from credentials.json (never hardcoded).
        config = load_config()
        # The login form lives on the app's /login route, not the root URL.
        login_url = config["base_url"].rstrip("/") + config.get("login_path", "/login")
        username = config["credentials"]["username"]
        password = config["credentials"]["password"]
        timeout = config.get("timeouts", {}).get("explicit_wait_seconds", 20)

        logger.info("Starting Web Login test against %s", login_url)
        driver = create_driver(config)

        # This web app keeps registered users in browser storage (client-side),
        # so a fresh session starts with no accounts. Register the account first
        # (same browser session) so there is a user to log in as. Toggle with
        # "register_first" in credentials.json (set false if the environment
        # already has the account seeded server-side).
        if config.get("register_first", False):
            register_url = config["base_url"].rstrip("/") + config.get("register_path", "/register")
            email = config.get("register_email", f"{username}@example.com")
            register_page = RegisterPage(driver, timeout=timeout)
            register_page.open(register_url)
            logger.info("Registering '%s' first (this app stores users per browser session).", username)
            if register_page.register(username, email, password):
                logger.info("Account '%s' is ready for this session.", username)
            else:
                logger.warning("No registration confirmation seen; attempting login anyway.")

        login_page = LoginPage(driver, timeout=timeout)
        login_page.open(login_url)
        logger.info("Opened login page; submitting credentials for user '%s'.", username)
        login_page.login(username, password)

        # Confirm success by waiting for a marker element that only appears
        # once the user is authenticated.
        if login_page.is_login_successful():
            logger.info("LOGIN SUCCESSFUL for user '%s'.", username)
            return EXIT_SUCCESS

        # Login did not succeed — capture any on-screen error for context,
        # then record visual evidence.
        error_text = login_page.get_error_text()
        message = error_text or "Login did not complete — still on the login page (check credentials and that the captcha/submit step ran)."
        logger.error("LOGIN FAILED: %s", message)
        shot = save_screenshot(driver, label="login_failed")
        logger.error("Screenshot saved to %s", shot)
        return EXIT_FAILURE

    # Broad catch is intentional: the failure contract (clear message +
    # screenshot + non-zero exit) must hold for ANY error, including config
    # problems, browser crashes, and missing elements.
    except Exception:
        logger.exception("Login test aborted due to an unexpected error.")
        if driver is not None:
            try:
                shot = save_screenshot(driver, label="login_error")
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
