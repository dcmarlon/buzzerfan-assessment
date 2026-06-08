# Chat/NewChat/WebApp/pages/new_chat_page.py
"""New Chat page object for the Furgechat web app ("New Chat" tab).

Encapsulates the locators and actions for creating a chat and sending the first
message. The test flow in main.py talks to this class only — it never touches
raw locators.

Locator notes & the page's KNOWN QUIRK
--------------------------------------
The locator-priority rule is data-testid > id > name > CSS > XPath, BUT a normal
``id`` only outranks ``name`` when the id is STABLE. On this page the recipient
input's id is dynamically generated with a random suffix, e.g.::

    <input name="recipient" id="recipient-ejgdyfp" ...>

That random id would change on every page load and break the test, so we
deliberately locate the recipient by its stable ``name="recipient"`` attribute
instead. The message textarea (``id="first-message"``) and the submit button
(``id="create-chat-btn"``) have stable ids, so those keep their ids.

(The page itself asks testers not to suggest fixes for these quirks — so we do
not; we simply make the automation robust to them.)
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class NewChatPage(BasePage):
    """Page object representing the 'New Chat' form and its result."""

    # Recipient: located by the STABLE name, NOT the random/dynamic id.
    RECIPIENT_INPUT = (By.NAME, "recipient")

    # Message + submit: stable ids, so the id strategy is appropriate here.
    MESSAGE_INPUT = (By.ID, "first-message")
    SUBMIT_BUTTON = (By.ID, "create-chat-btn")

    # The new-chat form itself, used to confirm we navigated AWAY from the
    # form after a successful create. (app-new-chat is the Angular host.)
    NEW_CHAT_FORM = (By.CSS_SELECTOR, "app-new-chat form")

    # --- Optional locators (PLACEHOLDERS — fill in from the post-create DOM) -
    # A stronger, positive success assertion (e.g. the opened conversation view
    # or the sent-message bubble). Fill in to assert this in addition to the
    # form disappearing.
    SUCCESS_MARKER = (By.CSS_SELECTOR, "SELECTOR_TBD_FROM_INSPECTOR")

    # An error banner shown on a FAILED create (e.g. "unknown recipient"). The
    # form DOM shows none; fill in if the app renders one, for clearer errors.
    ERROR_MESSAGE = (By.CSS_SELECTOR, "SELECTOR_TBD_FROM_INSPECTOR")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the new-chat page object.

        Args:
            driver: The active Selenium WebDriver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def is_loaded(self) -> bool:
        """Return True if the New Chat form has rendered.

        If this is False the app most likely redirected to the login page
        (creating a chat requires a session) — see main.py's handling.

        Returns:
            True if the new-chat form is present before timeout.
        """
        return self.wait_present(self.NEW_CHAT_FORM)

    def create_chat(self, recipient: str, message: str) -> None:
        """Fill the recipient and first message, then submit the form.

        Args:
            recipient: The username to start the chat with.
            message: The first message to send.
        """
        self.type_text(self.RECIPIENT_INPUT, recipient)
        self.type_text(self.MESSAGE_INPUT, message)
        self.click(self.SUBMIT_BUTTON)

    def is_chat_created(self) -> bool:
        """Return True once the chat has clearly been created.

        Primary signal: the new-chat form disappears, because the single-page
        app navigates away from <app-new-chat> on success. If a positive
        success marker is configured, that is required as well.

        Returns:
            True if creation is confirmed within the timeout, else False.
        """
        left_form = self.wait_invisible(self.NEW_CHAT_FORM)

        # If a positive marker has been filled in, require it too; otherwise
        # rely on the new-chat form going away.
        if self.SUCCESS_MARKER[1] != "SELECTOR_TBD_FROM_INSPECTOR":
            return left_form and self.is_visible(self.SUCCESS_MARKER)
        return left_form

    def get_error_text(self) -> str:
        """Return the on-screen error message, or an empty string if none.

        Returns "" when no error locator is configured or no error is shown.

        Returns:
            The error banner's text, or "" if no error element is present.
        """
        # No error locator configured yet — nothing to read.
        if self.ERROR_MESSAGE[1] == "SELECTOR_TBD_FROM_INSPECTOR":
            return ""
        if self.is_visible(self.ERROR_MESSAGE, timeout=5):
            return self.find_visible(self.ERROR_MESSAGE).text
        return ""
