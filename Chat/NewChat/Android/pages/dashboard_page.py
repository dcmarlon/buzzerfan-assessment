# Chat/NewChat/Android/pages/dashboard_page.py
"""Dashboard page object for the Furgechat Android app ("All Messages Dashboard").

For the New Chat flow this page only needs to (a) confirm login completed and
(b) locate the floating new-chat button (FAB) at the bottom-right.

Locating the FAB robustly
--------------------------
The Inspector's suggested locator is the 3rd Button on the screen
(``Button.instance(2)``), which is only correct when exactly the two seeded
chats (John Doe, QA Lead) exist. Previous test runs add more chat rows, which
pushes the FAB's index past 2 — so a fixed instance is fragile.

``find_new_chat_fab`` therefore tries, in order:
    1. ``Button.instance(2)`` — but ONLY if it is icon-only (empty content-desc),
       which is what distinguishes the FAB from a chat row.
    2. The icon-only Button on screen (chat rows and Logout all carry a
       content-desc; the FAB does not), regardless of how many chats exist.
    3. The last Button on screen.
    4. Otherwise raise a clear error.
It returns the element plus a label of which strategy matched, so the run log
shows exactly how the FAB was found.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Page object for the post-login dashboard and its new-chat FAB."""

    # The header is exposed as a CONTENT-DESC (its text attribute is empty), so
    # match by accessibility id, not text().
    HEADER = (AppiumBy.ACCESSIBILITY_ID, "All Messages Dashboard")
    ALL_BUTTONS = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.Button")',
    )
    # Primary per the spec: the 3rd Button (valid only with the 2 seeded chats).
    FAB_PRIMARY = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.Button").instance(2)',
    )

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the dashboard page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def wait_until_loaded(self, timeout: int | None = None) -> bool:
        """Wait for the dashboard header (proves login completed).

        Args:
            timeout: Optional override for how long to wait.

        Returns:
            True if the header appears in time, else False.
        """
        return self.is_present(self.HEADER, timeout=timeout)

    def _first_or_none(self, by: str, value: str) -> WebElement | None:
        """Return the first element matching the locator, or None if there are none."""
        elements = self.driver.find_elements(by, value)
        return elements[0] if elements else None

    @staticmethod
    def _is_iconless(element: WebElement) -> bool:
        """Return True if the button has no content-desc (i.e. an icon-only FAB)."""
        return not (element.get_attribute("content-desc") or "").strip()

    def find_new_chat_fab(self) -> tuple[WebElement, str]:
        """Locate the bottom-right new-chat FAB, trying robust strategies in order.

        Returns:
            A tuple ``(element, strategy_label)`` describing the FAB and which
            strategy found it.

        Raises:
            NoSuchElementException: If no candidate button can be found.
        """
        # 1) Primary: the 3rd Button, accepted only if it is icon-only (the FAB).
        primary = self._first_or_none(*self.FAB_PRIMARY)
        if primary is not None and self._is_iconless(primary):
            return primary, "primary: Button.instance(2)"

        buttons = self.driver.find_elements(*self.ALL_BUTTONS)

        # 2) Robust: the FAB is the icon-only Button (chat rows + Logout all have
        #    a content-desc; the FAB does not).
        iconless = [b for b in buttons if self._is_iconless(b)]
        if iconless:
            return iconless[-1], "fallback: icon-only Button"

        # 3) Last resort: the last Button on screen.
        if buttons:
            return buttons[-1], "fallback: last Button on screen"

        # 4) Nothing to work with.
        raise NoSuchElementException(
            "Could not locate the new-chat FAB: no buttons found on the dashboard. "
            "Re-capture the FAB with Appium Inspector (see Guide.MD troubleshooting)."
        )

    def _chat_locator(self, contact_name: str) -> tuple[str, str]:
        """Locator for the dashboard chat row whose content-desc contains the name."""
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().descriptionContains("{contact_name}")',
        )

    def has_chat(self, contact_name: str, timeout: int | None = None) -> bool:
        """Return True if a chat row for the contact is present on the dashboard.

        Used to confirm that the (flaky) create actually registered.

        Args:
            contact_name: The contact to look for.
            timeout: Optional override for how long to wait.
        """
        return self.is_present(self._chat_locator(contact_name), timeout=timeout)

    def open_chat(self, contact_name: str) -> bool:
        """Open a chat by tapping the dashboard row whose content-desc contains it.

        Args:
            contact_name: The contact whose conversation to open.

        Returns:
            True if the chat row appeared and was tapped, else False.
        """
        if not self.has_chat(contact_name, timeout=self.timeout):
            return False
        self.driver.find_element(*self._chat_locator(contact_name)).click()
        return True
