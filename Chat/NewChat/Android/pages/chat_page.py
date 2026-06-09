# Chat/NewChat/Android/pages/chat_page.py
"""Chat conversation page object for the Furgechat Android app.

Handles the conversation screen: typing a message, sending it (with a fallback),
and verifying it landed. Each sent message appears in the thread as an element
whose ``text`` equals the message (NOT its content-desc).

Sending strategy
----------------
The chat screen has two buttons: a top-left "Back" arrow (instance 0) and the
send icon to the right of the input (instance 1). ``send_message`` taps the send
button (instance 1 — NOT the back arrow, which would leave the conversation) and,
if the bubble does not appear, falls back to pressing the Android ENTER key
(keycode 66), which also sends. After each attempt it waits for the message's
bubble (matched by visible text) to confirm the send landed — that wait doubles
as the "short pause" between messages, so no fixed ``time.sleep`` is ever used.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage

# Android keycode for the Enter key, used as a fallback "send".
_KEYCODE_ENTER = 66


def _ui_escape(text: str) -> str:
    """Escape backslashes and double quotes for embedding in a UiSelector string."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


class ChatPage(BasePage):
    """Page object for an open conversation."""

    # The message composer (hint: "Type a response...").
    MESSAGE_INPUT = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(0)',
    )
    # Send control: the icon button to the RIGHT of the input. Instance 0 is the
    # top-left "Back" arrow, so the send button is instance 1.
    SEND_BUTTON = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.Button").instance(1)',
    )

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the chat page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def wait_until_loaded(self) -> None:
        """Block until the conversation screen is ready (message input visible).

        Raises:
            selenium.common.exceptions.TimeoutException: If the input never
                appears within the configured timeout.
        """
        self.find_visible(self.MESSAGE_INPUT)

    def message_locator(self, text: str) -> tuple[str, str]:
        """Build a locator that matches a sent message by its visible text."""
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{_ui_escape(text)}")',
        )

    def is_message_visible(self, text: str, timeout: int | None = None) -> bool:
        """Return True if a message with this exact text is in the thread.

        Args:
            text: The message text (matched against element content-desc).
            timeout: Optional override for how long to wait.

        Returns:
            True if the message bubble appears before the timeout, else False.
        """
        return self.is_present(self.message_locator(text), timeout=timeout)

    def _wait_field_committed(self, text: str, timeout: int = 3) -> None:
        """Wait until the input's text reflects what we typed before sending.

        Flutter can lag committing keystrokes; this explicit wait (NOT a fixed
        sleep) is the rule-compliant replacement for "pausing" between typing
        and tapping send. It is non-fatal — the post-send bubble check is the
        authoritative guard.

        Args:
            text: The text we expect the field to contain.
            timeout: Maximum seconds to wait for the field to catch up.
        """
        by, value = self.MESSAGE_INPUT
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: (d.find_element(by, value).get_attribute("text") or "") == text
            )
        except TimeoutException:
            pass

    def send_message(self, text: str, verify_timeout: int = 3) -> str | None:
        """Type and send one message, verifying it appears in the thread.

        Args:
            text: The message to send.
            verify_timeout: Seconds to wait for the message bubble after each
                send attempt.

        Returns:
            A label of the strategy that worked ("send-button tap" or
            "ENTER keycode"), or None if the message never appeared after both.
        """
        self.type_text(self.MESSAGE_INPUT, text)
        self._wait_field_committed(text)

        # Strategy 1: tap the send button next to the input.
        send_buttons = self.driver.find_elements(*self.SEND_BUTTON)
        if send_buttons:
            send_buttons[0].click()
            if self.is_message_visible(text, timeout=verify_timeout):
                return "send-button tap"

        # Strategy 2: fall back to pressing the Android ENTER key.
        self.driver.press_keycode(_KEYCODE_ENTER)
        if self.is_message_visible(text, timeout=verify_timeout):
            return "ENTER keycode"

        return None
