# Auth/Registration/Android/main.py
"""Android Registration test flow for the Furgechat app.

Test scenario
-------------
1. Launch the app on the connected device/emulator (opens the login screen).
2. Tap "No account? Register here" to open the registration screen.
3. Generate a UNIQUE email and fill the email + password fields.
4. Tap "Register Account".
5. Wait for the success message and assert it is visible.

Outcome contract
----------------
- On success: logs [PASS] with the elapsed seconds and exits 0.
- On any failure: logs [FAIL], saves a timestamped screenshot to
  ``screenshots/``, and exits with a non-zero status code.
- The Appium session is always closed in a finally block.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from utils.driver_factory import create_driver, load_credentials, load_settings
from utils.logger import get_logger
from utils.test_data import generate_unique_email

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Screenshots are written here on failure (created on demand).
_SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"


def _save_failure_screenshot(
    driver, logger, label: str = "registration_failure"
) -> None:
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


def _verify_field_labels(register_page: RegisterPage, logger) -> None:
    """Backup check that the positional EditTexts are the expected fields.

    Flutter positional selectors break if the form layout changes; comparing the
    placeholder labels catches that early. This is non-fatal — it only warns.

    Args:
        register_page: The registration page object.
        logger: The configured logger.
    """
    email_label = register_page.get_email_label()
    if email_label != RegisterPage.EXPECTED_EMAIL_LABEL:
        logger.warning(
            "Email field label was %r, expected %r — the positional selector "
            "may have shifted; re-capture with Appium Inspector.",
            email_label,
            RegisterPage.EXPECTED_EMAIL_LABEL,
        )

    password_label = register_page.get_password_label()
    if password_label != RegisterPage.EXPECTED_PASSWORD_LABEL:
        logger.warning(
            "Password field label was %r, expected %r — the positional selector "
            "may have shifted; re-capture with Appium Inspector.",
            password_label,
            RegisterPage.EXPECTED_PASSWORD_LABEL,
        )


def main() -> int:
    """Run the Android registration test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if registration is confirmed, else ``EXIT_FAILURE``.
    """
    logger = get_logger("android_register")
    driver = None
    try:
        # Load static settings and per-machine values (never hardcoded).
        settings = load_settings()
        credentials = load_credentials()
        timeouts = settings.get("timeouts", {})
        element_timeout = timeouts.get("element_wait_seconds", 20)
        success_timeout = timeouts.get("success_wait_seconds", 15)

        new_user = credentials.get("new_user", {})
        email = generate_unique_email(
            prefix=new_user.get("email_prefix", "qa_test"),
            domain=new_user.get("email_domain", "buzzerfan.test"),
        )
        password = new_user["password"]

        logger.info(
            "Starting Android Registration test (Appium server %s).",
            settings.get("appium_server", "http://127.0.0.1:4723"),
        )
        logger.info("Generated unique email: %s", email)
        driver = create_driver(settings, credentials)

        # Steps 1-2: login screen -> open the registration screen.
        login_page = LoginPage(driver, timeout=element_timeout)
        login_page.wait_until_loaded()
        logger.info("Login screen loaded; tapping 'No account? Register here'.")
        login_page.go_to_register()

        register_page = RegisterPage(driver, timeout=element_timeout)
        register_page.wait_until_loaded()
        logger.info("Registration screen loaded.")

        # Backup verification of the positional fields (non-fatal).
        _verify_field_labels(register_page, logger)

        # Steps 3-5: fill the form and submit.
        logger.info("Registering new account with email '%s'.", email)
        register_page.register(email, password)

        # Step 6: wait for the success message, timing how long it takes.
        start = time.perf_counter()
        if register_page.is_registration_successful(timeout=success_timeout):
            elapsed = time.perf_counter() - start
            logger.info(
                "[PASS] Registration succeeded — success message appeared in "
                "%.2fs for '%s'.",
                elapsed,
                email,
            )
            return EXIT_SUCCESS

        # Success message never appeared within the timeout.
        logger.error(
            "[FAIL] 'Registration Approved! You can now log in.' did not appear "
            "within %ss. The email may have been rejected or already exists.",
            success_timeout,
        )
        _save_failure_screenshot(driver, logger)
        return EXIT_FAILURE

    # Broad catch is intentional: the failure contract (clear [FAIL] message +
    # screenshot + non-zero exit) must hold for ANY error.
    except Exception:
        logger.exception("[FAIL] Registration test aborted due to an unexpected error.")
        if driver is not None:
            _save_failure_screenshot(driver, logger, label="registration_error")
        return EXIT_FAILURE

    finally:
        # Always release the Appium session, even on failure.
        if driver is not None:
            driver.quit()
            logger.info("Appium session closed.")


if __name__ == "__main__":
    sys.exit(main())
