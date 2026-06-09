# Chat/Chats/Android/pages/dashboard_page.py
"""Dashboard page object for the Furgechat Android app ("All Messages Dashboard").

Represents the post-login dashboard and knows how to read the list of chats.
The test flow in main.py talks to this class only — it never touches raw
locators.

How chats are located
----------------------
Each chat row is an ``android.widget.Button`` whose ``content-desc`` is the chat
name and last message concatenated (e.g. "John Doe Almost done, fixing a cache
bug."). We select every Button on the screen and then drop the ones that are
dashboard controls rather than chats (currently just the "Logout" icon, plus any
button with no content-desc such as an icon-only FAB). Anything else is treated
as a chat and its content-desc is returned verbatim — see ``get_chats``.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver

from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Page object for the post-login messages dashboard and its chat list."""

    # The header confirms login completed. It is exposed as a CONTENT-DESC (its
    # text attribute is empty), so match by accessibility id, not text().
    HEADER = (AppiumBy.ACCESSIBILITY_ID, "All Messages Dashboard")

    # Every button on the dashboard; chat rows are a subset of these.
    CHAT_BUTTONS = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.Button")',
    )

    # content-descs of buttons that are dashboard controls, NOT chats. Extend
    # this set if the Inspector reveals more non-chat buttons (the test also
    # logs any button it skips, so unexpected ones are easy to spot).
    NON_CHAT_CONTENT_DESCS = frozenset({"Logout"})

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the dashboard page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def wait_until_loaded(self, timeout: int | None = None) -> bool:
        """Wait for the dashboard header to appear (presence) within the timeout.

        Args:
            timeout: Optional override for how long to wait.

        Returns:
            True if the "All Messages Dashboard" header appears in time, else
            False.
        """
        return self.is_present(self.HEADER, timeout=timeout)

    def get_chats(self) -> tuple[list[str], list[str]]:
        """Read the dashboard's buttons and split them into chats vs. skipped.

        Returns:
            A tuple ``(chats, skipped)`` where:
            - ``chats`` is the list of chat-row content-desc strings, in order.
            - ``skipped`` is the list of content-descs that were excluded
              (dashboard controls like "Logout", or empty/icon-only buttons),
              so the caller can log exactly what was ignored.
        """
        # Make sure buttons have rendered before reading them. The dashboard
        # always has at least the Logout button, so this returns quickly; it is
        # an explicit wait on a real condition, NOT a fixed sleep.
        self.is_present(self.CHAT_BUTTONS, timeout=self.timeout)

        buttons = self.driver.find_elements(*self.CHAT_BUTTONS)

        chats: list[str] = []
        skipped: list[str] = []
        for button in buttons:
            content_desc = (button.get_attribute("content-desc") or "").strip()
            if not content_desc:
                # Icon-only control (e.g. a "New Chat" FAB) with no label.
                skipped.append("(empty content-desc)")
            elif content_desc in self.NON_CHAT_CONTENT_DESCS:
                # Known dashboard control, not a chat.
                skipped.append(content_desc)
            else:
                chats.append(content_desc)
        return chats, skipped
