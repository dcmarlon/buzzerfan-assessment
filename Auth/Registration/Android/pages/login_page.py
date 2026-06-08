# Auth/Registration/Android/pages/login_page.py
"""Login page object (entry point for the registration flow).

The app launches on the login screen. This page object owns only what the
registration flow needs there: the "No account? Register here" link that opens
the registration screen. The link exposes a content-desc, so the preferred
``ACCESSIBILITY_ID`` strategy is used.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object for the login screen's path into registration."""

    REGISTER_LINK = (AppiumBy.ACCESSIBILITY_ID, "No account? Register here")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the login page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def wait_until_loaded(self) -> None:
        """Block until the login screen is ready (register link visible).

        Raises:
            selenium.common.exceptions.TimeoutException: If the link never
                appears within the configured timeout.
        """
        self.find_visible(self.REGISTER_LINK)

    def go_to_register(self) -> None:
        """Tap 'No account? Register here' to open the registration screen."""
        self.tap(self.REGISTER_LINK)
