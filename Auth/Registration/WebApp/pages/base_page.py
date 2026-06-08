# Auth/Registration/WebApp/pages/base_page.py
"""Base page object.

Holds the WebDriver-interaction primitives shared by every page object:
explicit waits, safe typing, and clicking. NO ``time.sleep`` is used anywhere —
every wait is an explicit WebDriverWait keyed to a real DOM condition, which is
both faster and far more reliable than fixed delays.
"""

from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# A locator is a (By, value) tuple, e.g. (By.ID, "username").
Locator = tuple[str, str]


class BasePage:
    """Common behaviour for all page objects."""

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Store the driver and create a reusable WebDriverWait.

        Args:
            driver: The active Selenium WebDriver.
            timeout: Maximum seconds any explicit wait will block.
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> None:
        """Navigate the browser to the given URL."""
        self.driver.get(url)

    def find_visible(self, locator: Locator) -> WebElement:
        """Wait until the element is visible and return it.

        Args:
            locator: (By, value) tuple identifying the element.

        Returns:
            The visible WebElement.
        """
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator: Locator) -> WebElement:
        """Wait until the element is clickable and return it."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def type_text(self, locator: Locator, text: str) -> None:
        """Clear a field and type text into it once it is visible.

        Args:
            locator: (By, value) tuple for the input field.
            text: The value to enter.
        """
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)

    def click(self, locator: Locator) -> None:
        """Click an element once it is clickable."""
        self.find_clickable(locator).click()

    def is_visible(self, locator: Locator, timeout: int | None = None) -> bool:
        """Return True if the element becomes visible within the timeout.

        Used for assertions (e.g. confirming a post-action element appears)
        without raising when the element is legitimately absent.

        Args:
            locator: (By, value) tuple identifying the element.
            timeout: Optional override for this single check.

        Returns:
            True if the element is visible before the timeout, else False.
        """
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_invisible(self, locator: Locator, timeout: int | None = None) -> bool:
        """Return True if the element becomes invisible (or absent) in time.

        Useful for confirming that a page has been left behind — e.g. the
        registration form disappearing once the account is created.

        Args:
            locator: (By, value) tuple identifying the element.
            timeout: Optional override for this single check.

        Returns:
            True if the element is gone/hidden before the timeout, else False.
        """
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
