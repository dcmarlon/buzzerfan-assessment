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

A second quirk: after submitting, a "Confirm Chat" modal appears that only
honours REAL pointer events (it checks ``event.isTrusted``). We click its Confirm
button with a genuine Selenium pointer action (ActionChains), never a JavaScript
click. (The page asks testers not to suggest fixes for these quirks — so we do
not; we simply make the automation robust to them.)
"""

from __future__ import annotations

from selenium.webdriver.common.action_chains import ActionChains
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

    # After "Create Chat", a "Confirm Chat" modal appears. It only honours REAL
    # pointer events (it checks event.isTrusted), so we click Confirm via a
    # genuine Selenium pointer action (ActionChains), not a JavaScript click.
    CONFIRM_BUTTON = (By.ID, "confirm-modal-btn")

    # The new-chat form itself, used to confirm we navigated AWAY from the
    # form after a successful create. (app-new-chat is the Angular host.)
    NEW_CHAT_FORM = (By.CSS_SELECTOR, "app-new-chat form")

    # Success confirmation: after confirming, the app shows an inline
    # "Chat with <recipient> created!" message (it keeps the form on screen
    # rather than navigating away).
    SUCCESS_MARKER = (By.XPATH, "//*[contains(text(), 'created!')]")

    # Quirk: the first "Create Chat" click often fails with "Hmm, something went
    # wrong. Please click Create again." Detected so the click can be retried.
    RETRY_ERROR = (By.XPATH, "//*[contains(text(), 'went wrong')]")

    # An error banner shown on a genuine failed create (e.g. "unknown
    # recipient"). Left as a placeholder; the app showed none to capture.
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

    def create_chat(self, recipient: str, message: str, max_attempts: int = 5) -> bool:
        """Fill the form and create the chat, handling the page's two quirks.

        Quirk 1: the first "Create Chat" click often fails with "Hmm, something
        went wrong. Please click Create again." — so we retry the click.
        Quirk 2: a "Confirm Chat" modal then appears that only honours real
        pointer events — so confirm_chat() clicks it with a genuine pointer.

        Args:
            recipient: The username to start the chat with.
            message: The first message to send.
            max_attempts: How many times to (re)click Create while fighting the
                intermittent "something went wrong" quirk.

        Returns:
            True if the success confirmation appeared, else False.
        """
        self.type_text(self.RECIPIENT_INPUT, recipient)
        self.type_text(self.MESSAGE_INPUT, message)
        for _ in range(max_attempts):
            self.click(self.SUBMIT_BUTTON)
            # The modal may open now, or this click may have hit the "something
            # went wrong" quirk — wait briefly for the confirmation modal.
            if self.is_visible(self.CONFIRM_BUTTON, timeout=5):
                self.confirm_chat()
                if self.is_visible(self.SUCCESS_MARKER, timeout=5):
                    return True
            # No modal / no success yet -> retry quirk; loop and click again.
        return False

    def confirm_chat(self) -> None:
        """Click Confirm on the 'Confirm Chat' modal using a real pointer event.

        The modal checks ``event.isTrusted`` (its note: "only responds to real
        human pointer events"). Selenium's pointer input produces trusted events
        — unlike a JavaScript click — so we move the real pointer onto the button
        and click it via ActionChains.
        """
        button = self.find_clickable(self.CONFIRM_BUTTON)
        ActionChains(self.driver).move_to_element(button).click().perform()

    def is_chat_created(self) -> bool:
        """Return True once the app confirms the chat was created.

        The app shows an inline "Chat with <recipient> created!" message after a
        successful confirm (it keeps the form on screen rather than navigating
        away), so success is asserted by that confirmation appearing.

        Returns:
            True if the confirmation is visible within the timeout, else False.
        """
        return self.is_visible(self.SUCCESS_MARKER)

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
