# Auth/Registration/Android/pages/base_page.py
"""Base page object for Appium (Android) screens.

Holds the driver-interaction primitives shared by every page object: explicit
waits, safe typing, and tapping. NO ``time.sleep`` is used anywhere — every wait
is an explicit WebDriverWait keyed to a real UI condition, which is both faster
and far more reliable than fixed delays.
"""

from __future__ import annotations

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# A locator is an (AppiumBy, value) tuple, e.g.
# (AppiumBy.ACCESSIBILITY_ID, "Register Account").
Locator = tuple[str, str]


class BasePage:
    """Common behaviour for all Android page objects."""

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Store the driver and create a reusable WebDriverWait.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def find_visible(self, locator: Locator) -> WebElement:
        """Wait until the element is visible and return it.

        Args:
            locator: (AppiumBy, value) tuple identifying the element.

        Returns:
            The visible element.
        """
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator: Locator) -> WebElement:
        """Wait until the element is clickable and return it."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def type_text(self, locator: Locator, text: str) -> None:
        """Clear a field and type text into it once it is visible.

        Args:
            locator: (AppiumBy, value) tuple for the input field.
            text: The value to enter.
        """
        element = self.find_visible(locator)
        # Tap to focus first — some Flutter fields ignore send_keys unless they
        # already hold focus (e.g. the password field stays empty without this).
        element.click()
        element.clear()
        element.send_keys(text)

    def tap(self, locator: Locator) -> None:
        """Tap an element once it is clickable."""
        self.find_clickable(locator).click()

    def is_present(self, locator: Locator, timeout: int | None = None) -> bool:
        """Return True if the element is present in the UI within the timeout.

        Uses ``presence_of_element_located`` and never raises — it returns False
        on timeout instead — so callers can branch on the result cleanly.

        Args:
            locator: (AppiumBy, value) tuple identifying the element.
            timeout: Optional override for this single check.

        Returns:
            True if the element appears before the timeout, else False.
        """
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
