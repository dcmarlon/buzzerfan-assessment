# Chat/Chats/WebApp/pages/chat_list_page.py
"""Chat-list page object for the Furgechat web app ("Chats" tab).

Encapsulates the locators and read actions for the chat list. The test flow in
main.py talks to this class only — it never touches raw locators.

Locator notes
-------------
The chat rows have no ``data-testid``, ``id``, or ``name`` attribute, so per the
locator-priority rule (data-testid > id > name > CSS > XPath) the most stable
available hook is the ``chat-item`` CSS class. Each row exposes a
``data-chat-id`` attribute and contains:

    <strong>            -> the chat name (contact / group)
    <div class="muted"> -> the last-message preview

This screen is READ-ONLY: the page object only reads, it never mutates state.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class ChatListPage(BasePage):
    """Page object representing the 'Chats' tab and its list of chats."""

    # The Angular host component for the whole chats screen. Used to confirm
    # the screen rendered (and, by its absence, to detect a login redirect).
    CHAT_LIST = (By.CSS_SELECTOR, "app-chat-list")

    # Every chat row. Scoped under the host so we never pick up stray matches.
    CHAT_ITEMS = (By.CSS_SELECTOR, "app-chat-list .chat-item")

    # Sub-elements located RELATIVE TO a chat row element (not the page).
    CHAT_NAME = (By.CSS_SELECTOR, "strong")
    CHAT_PREVIEW = (By.CSS_SELECTOR, ".muted")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the chat-list page object.

        Args:
            driver: The active Selenium WebDriver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def is_loaded(self) -> bool:
        """Return True if the chats screen has rendered.

        If this is False the app most likely redirected to the login page
        (the chats screen requires a session) — see main.py's handling.

        Returns:
            True if the chat-list container is present before timeout.
        """
        return self.wait_present(self.CHAT_LIST)

    def get_chats(self) -> list[dict[str, str]]:
        """Read every visible chat row and return it as structured data.

        Returns:
            A list of dicts with ``id``, ``name``, and ``preview`` keys, in the
            order they appear on screen. Returns an empty list if the screen is
            absent or genuinely has no chats.
        """
        # Nothing to read if the screen never rendered.
        if not self.wait_present(self.CHAT_LIST):
            return []

        # Give chat rows a brief chance to render before reading. This is an
        # explicit wait on a real condition (rows present), NOT a fixed sleep;
        # if no rows appear in the short window we treat the list as empty.
        if not self.wait_present(self.CHAT_ITEMS, timeout=5):
            return []

        # find_elements (plural) returns [] rather than raising when empty.
        rows = self.driver.find_elements(*self.CHAT_ITEMS)

        chats: list[dict[str, str]] = []
        for row in rows:
            chats.append(
                {
                    "id": row.get_attribute("data-chat-id") or "",
                    "name": row.find_element(*self.CHAT_NAME).text.strip(),
                    "preview": row.find_element(*self.CHAT_PREVIEW).text.strip(),
                }
            )
        return chats
