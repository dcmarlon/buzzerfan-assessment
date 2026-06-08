# Chat/NewChat/WebApp/main.py
"""Web New Chat test flow for the Furgechat web app.

Test scenario
-------------
1. Log in (creating a chat is an authenticated action; on by default).
2. Open the "New Chat" tab.
3. Enter a recipient and the first message, then submit.
4. Verify the chat was created (the new-chat form goes away).

Outcome contract
----------------
- On success: logs "NEW CHAT CREATED" and exits 0.
- On any failure: logs a clear error, saves a timestamped screenshot to
  ``screenshots/``, and exits with a non-zero status code.
"""

from __future__ import annotations

import sys

from pages.login_page import LoginPage
from pages.new_chat_page import NewChatPage
from pages.register_page import RegisterPage
from utils.config import load_config
from utils.driver_factory import create_driver
from utils.logger import get_logger
from utils.screenshot import save_screenshot

# Exit codes consumed by CI / shell callers.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _maybe_login(driver, base_url, login_cfg, timeout, logger) -> bool:
    """Authenticate first if creating a chat requires a session.

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
    if not login_cfg.get("enabled", True):
        return True  # Login explicitly disabled for this run.

    username = login_cfg.get("username", "admin")
    password = login_cfg.get("password", "password")

    # This web app keeps registered users in browser storage (client-side), so a
    # fresh session has no accounts. Register the account first (same session) so
    # there is a user to log in as. Toggle with "register_first" in the login
    # block of credentials.json.
    if login_cfg.get("register_first", False):
        register_url = base_url + login_cfg.get("register_path", "/register")
        email = login_cfg.get("register_email", f"{username}@example.com")
        register_page = RegisterPage(driver, timeout=timeout)
        register_page.open(register_url)
        logger.info("Registering '%s' first (this app stores users per browser session).", username)
        if register_page.register(username, email, password):
            logger.info("Account '%s' is ready for this session.", username)
        else:
            logger.warning("No registration confirmation seen; attempting login anyway.")

    login_url = base_url + login_cfg.get("path", "/login")
    login_page = LoginPage(driver, timeout=timeout)
    login_page.open(login_url)
    logger.info("Signing in as '%s' before creating a chat.", username)
    login_page.login(username, password)

    if not login_page.is_login_successful():
        logger.error("Login failed; cannot create a chat.")
        return False
    logger.info("Login successful.")
    return True


def main() -> int:
    """Run the new-chat test and return a process exit code.

    Returns:
        ``EXIT_SUCCESS`` (0) if the chat is created, else ``EXIT_FAILURE``.
    """
    logger = get_logger("web_new_chat")
    driver = None
    try:
        # Pull all settings/content from credentials.json (never hardcoded).
        config = load_config()
        base_url = config["base_url"].rstrip("/")
        new_chat_url = base_url + config.get("new_chat_path", "/new-chat")
        timeout = config.get("timeouts", {}).get("explicit_wait_seconds", 20)
        login_cfg = config.get("login", {})

        new_chat_cfg = config.get("new_chat", {})
        recipient = new_chat_cfg.get("recipient", "Alice")
        message = new_chat_cfg.get("message", "Hey user! This is done for assessment")

        logger.info("Starting Web New Chat test against %s", new_chat_url)
        driver = create_driver(config)

        # Step 1: authenticate (creating a chat needs a session).
        if not _maybe_login(driver, base_url, login_cfg, timeout, logger):
            save_screenshot(driver, label="login_failed")
            return EXIT_FAILURE

        # Step 2: open the New Chat tab.
        new_chat_page = NewChatPage(driver, timeout=timeout)
        new_chat_page.open(new_chat_url)
        logger.info("Opened the 'New Chat' tab.")

        # If the form did not render, the app most likely required a login.
        if not new_chat_page.is_loaded():
            logger.error(
                "The New Chat form did not load. If the app requires login, set "
                "login.enabled=true in credentials.json and run again."
            )
            save_screenshot(driver, label="new_chat_not_loaded")
            return EXIT_FAILURE

        # Step 3: create the chat and send the first message.
        logger.info("Creating a new chat with recipient '%s'.", recipient)
        logger.info("First message: %r", message)
        new_chat_page.create_chat(recipient, message)

        # Step 4: verify the chat was created.
        if new_chat_page.is_chat_created():
            logger.info(
                "NEW CHAT CREATED with '%s'; first message sent.", recipient
            )
            return EXIT_SUCCESS

        # Did not succeed — capture any on-screen error, then save evidence.
        error_text = new_chat_page.get_error_text()
        message_out = error_text or (
            "Chat was not created — still on the New Chat page "
            "(the recipient may be unknown or the message was rejected)."
        )
        logger.error("NEW CHAT FAILED: %s", message_out)
        shot = save_screenshot(driver, label="new_chat_failed")
        logger.error("Screenshot saved to %s", shot)
        return EXIT_FAILURE

    # Broad catch is intentional: the failure contract (clear message +
    # screenshot + non-zero exit) must hold for ANY error.
    except Exception:
        logger.exception("New Chat test aborted due to an unexpected error.")
        if driver is not None:
            try:
                shot = save_screenshot(driver, label="new_chat_error")
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
