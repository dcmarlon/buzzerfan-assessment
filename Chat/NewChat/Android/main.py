# Chat/NewChat/Android/main.py
"""Android New Chat test flow for the Furgechat app.

Test scenario
-------------
1. Launch the app (opens the login screen) and log in as admin.
2. Wait for the "All Messages Dashboard" header.
3. Tap the new-chat FAB (with robust fallbacks — see DashboardPage).
4. In the "Start New DM" dialog, enter a UNIQUE, DIGIT-FREE contact name and tap
   Create (the app rejects names containing numbers); the dialog closes and the
   new chat appears on the dashboard.
5. Open the new chat from the dashboard to reach its conversation.
6. Send 3 messages, verifying each one appears in the conversation as it is
   sent (the thread auto-scrolls, so verification is per-message, not at the end).

Outcome contract
----------------
- On success: logs [PASS] with the contact name and message count + elapsed time.
- On any failure: logs [FAIL], saves a timestamped screenshot to
  ``screenshots/``, and exits with a non-zero status code.
- The Appium session is always closed in a finally block.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

from pages.chat_page import ChatPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.new_dm_dialog import NewDmDialog
from utils.driver_factory import create_driver, load_credentials, load_settings
from utils.logger import get_logger

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Screenshots are written here on failure (created on demand).
_SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"

# Test fixtures: the messages to send (fixed by the assessment).
MESSAGES = [
    "Hello from Buzzerfan QA automation",
    "This is automated message 2",
    "Final test message",
]


def _generate_contact_name() -> str:
    """Return a unique, DIGIT-FREE contact name, e.g. ``QaUserbhiajedd``.

    The app rejects contact names that contain numbers ("DM Creation Denied:
    '<name>' contains numbers"), so the Unix-timestamp digits are mapped to
    letters (0->a … 9->j). The result is unique per run yet contains no digits.
    """
    letters = str(int(time.time())).translate(str.maketrans("0123456789", "abcdefghij"))
    return f"QaUser{letters}"


def _save_failure_screenshot(driver, logger, label: str = "new_chat_failure") -> None:
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
    """Run the Android new-chat test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if the chat is created and all messages send, else
        ``EXIT_FAILURE``.
    """
    logger = get_logger("android_new_chat")
    driver = None
    try:
        # Load static settings and per-machine credentials (never hardcoded).
        settings = load_settings()
        credentials = load_credentials()
        timeouts = settings.get("timeouts", {})
        element_timeout = timeouts.get("element_wait_seconds", 20)
        dashboard_timeout = timeouts.get("dashboard_wait_seconds", 15)
        verify_timeout = timeouts.get("message_verify_seconds", 3)
        username = credentials["username"]
        password = credentials["password"]

        logger.info(
            "Starting Android New Chat test (Appium server %s).",
            settings.get("appium_server", "http://127.0.0.1:4723"),
        )
        start = time.perf_counter()
        driver = create_driver(settings, credentials)

        # Steps 1-2: log in and confirm the dashboard.
        login_page = LoginPage(driver, timeout=element_timeout)
        login_page.wait_until_loaded()
        login_page.login(username, password)

        dashboard = DashboardPage(driver, timeout=element_timeout)
        if not dashboard.wait_until_loaded(timeout=dashboard_timeout):
            logger.error(
                "[FAIL] 'All Messages Dashboard' did not load within %ss after login.",
                dashboard_timeout,
            )
            _save_failure_screenshot(driver, logger)
            return EXIT_FAILURE
        logger.info("Logged in as %s", username)
        logger.info("Dashboard loaded.")

        # Steps 3-4: create the chat. The dialog's Create is flaky AND does not
        # auto-close, so each attempt opens the dialog, enters the contact, taps
        # Create, lets it settle, dismisses the dialog, then confirms the chat
        # appeared on the dashboard — retrying until it does.
        contact_name = _generate_contact_name()
        logger.info(
            "Creating chat with contact: %s (digit-free — the app rejects names with numbers).",
            contact_name,
        )
        created = False
        for attempt in range(1, 4):
            fab, strategy = dashboard.find_new_chat_fab()
            fab.click()
            dialog = NewDmDialog(driver, timeout=element_timeout)
            if not dialog.wait_until_visible():
                logger.warning(
                    "Attempt %d: 'Start New DM' dialog did not open; retrying.", attempt
                )
                continue
            dialog.enter_contact(contact_name)
            dialog.tap_create()
            # A valid (digit-free) name is accepted: the dialog closes and the new
            # chat appears on the dashboard. Confirm it before continuing.
            if dashboard.has_chat(contact_name, timeout=8):
                created = True
                logger.info("Chat created on attempt %d.", attempt)
                break
            logger.info("Create attempt %d did not register; retrying.", attempt)

        if not created:
            logger.error(
                "[FAIL] Could not create the chat '%s' after retries.", contact_name
            )
            _save_failure_screenshot(driver, logger)
            return EXIT_FAILURE

        # Step 5: open the new chat from the dashboard to reach its conversation.
        logger.info("Opening the conversation with '%s'.", contact_name)
        if not dashboard.open_chat(contact_name):
            logger.error("[FAIL] The new chat '%s' could not be opened.", contact_name)
            _save_failure_screenshot(driver, logger)
            return EXIT_FAILURE

        # Step 6: in the conversation, send the messages and verify each appears.
        chat = ChatPage(driver, timeout=element_timeout)
        chat.wait_until_loaded()

        sent = 0
        for index, message in enumerate(MESSAGES, start=1):
            logger.info('Sending message %d/%d: "%s"', index, len(MESSAGES), message)
            used_strategy = chat.send_message(message, verify_timeout=verify_timeout)
            if used_strategy is None:
                logger.error(
                    '[FAIL] Message %d/%d could not be sent: "%s" '
                    "(tried send-button tap and ENTER keycode).",
                    index,
                    len(MESSAGES),
                    message,
                )
                _save_failure_screenshot(driver, logger)
                return EXIT_FAILURE
            sent += 1
            logger.info(
                "Message %d verified in conversation (sent via %s)",
                index,
                used_strategy,
            )

        # Each message was verified the instant it was sent (send_message only
        # returns a strategy once that message's bubble is visible). We do NOT
        # re-assert all three together at the end: the conversation auto-scrolls
        # to the newest message, so older bubbles scroll out of the visible
        # accessibility tree and would yield false negatives.
        elapsed = time.perf_counter() - start
        logger.info(
            "[PASS] New chat created with %s and %d messages sent (%.1fs)",
            contact_name,
            sent,
            elapsed,
        )
        return EXIT_SUCCESS

    # Broad catch is intentional: the failure contract (clear [FAIL] message +
    # screenshot + non-zero exit) must hold for ANY error.
    except Exception:
        logger.exception("[FAIL] New Chat test aborted due to an unexpected error.")
        if driver is not None:
            _save_failure_screenshot(driver, logger, label="new_chat_error")
        return EXIT_FAILURE

    finally:
        # Always release the Appium session, even on failure.
        if driver is not None:
            driver.quit()
            logger.info("Appium session closed.")


if __name__ == "__main__":
    sys.exit(main())
