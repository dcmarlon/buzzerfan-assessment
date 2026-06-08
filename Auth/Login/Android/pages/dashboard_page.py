# Auth/Login/Android/pages/dashboard_page.py
"""Dashboard page object for the Furgechat Android app.

Represents the "All Messages Dashboard" screen that appears ONLY after a
successful login, which makes its header the perfect assertion target. The test
flow in main.py uses this to confirm that login succeeded.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver

from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Page object for the post-login messages dashboard."""

    # The header text only exists once the user is logged in.
    HEADER = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("All Messages Dashboard")',
    )

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        """Initialize the dashboard page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds to wait for the dashboard to appear
                (defaults to the 15s required by the test spec).
        """
        super().__init__(driver, timeout)

    def wait_until_loaded(self) -> bool:
        """Wait for the dashboard header to appear (presence) within the timeout.

        Uses ``presence_of_element_located`` via the base helper, so it returns
        a boolean instead of raising — the caller decides PASS/FAIL.

        Returns:
            True if the "All Messages Dashboard" header appears before the
            timeout, else False.
        """
        return self.is_present(self.HEADER)
