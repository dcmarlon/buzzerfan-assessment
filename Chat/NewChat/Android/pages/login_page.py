# Chat/NewChat/Android/pages/login_page.py
"""Login page object for the Furgechat Android app (reused for the New Chat flow).

The New Chat test must sign in as admin before the dashboard is reachable. This
is the same login screen as Auth/Login/Android: a Flutter app driven via
UiAutomator2, with positional EditTexts (no resource-id / content-desc) and an
accessibility-id Login button. There is NO captcha on Android.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object representing the login screen."""

    # Positional locators — these EditTexts have no resource-id / content-desc.
    USERNAME_FIELD = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(0)',
    )
    PASSWORD_FIELD = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(1)',
    )

    # Login button exposes a content-desc -> accessibility id (preferred).
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Login")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the login page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def wait_until_loaded(self) -> None:
        """Block until the login screen is ready (username field visible).

        Raises:
            selenium.common.exceptions.TimeoutException: If the field never
                appears within the configured timeout.
        """
        self.find_visible(self.USERNAME_FIELD)

    def login(self, username: str, password: str) -> None:
        """Perform a full login: fill credentials and tap the login button.

        Args:
            username: The username to enter.
            password: The password to enter.
        """
        self.type_text(self.USERNAME_FIELD, username)
        self.type_text(self.PASSWORD_FIELD, password)
        self.tap(self.LOGIN_BUTTON)
