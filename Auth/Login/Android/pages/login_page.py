# Auth/Login/Android/pages/login_page.py
"""Login page object for the Furgechat Android app (a Flutter app driven via
UiAutomator2).

Encapsulates every locator and interaction for the login screen. The test flow
in main.py talks to this class only — it never touches raw locators.

Locator strategy & a Flutter caveat
-----------------------------------
This is a Flutter app rendered through UiAutomator2. The text fields expose
NO resource-id and NO content-desc — only their class and hint text. The only
usable locator is therefore positional: ``className("android.widget.EditText")``
plus ``.instance(0|1)`` (exactly as captured in the Appium Inspector).

Positional selectors are fragile: if the form layout changes, instance(0) may
no longer be the username field. As a safety net, the field "hint" attributes
are exposed so the test can verify it grabbed the right fields and warn loudly
if not (see ``EXPECTED_*_HINT`` and the accessors below).

The Login button exposes a content-desc, so it uses the preferred
``ACCESSIBILITY_ID`` strategy.
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

    # Backup verification: the on-screen hints that prove the positional fields
    # are really the username/password inputs.
    EXPECTED_USERNAME_HINT = "Username (use: admin)"
    EXPECTED_PASSWORD_HINT = "Password (use: password123)"

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

    def get_username_hint(self) -> str:
        """Return the username field's hint text (for backup verification)."""
        return self.find_visible(self.USERNAME_FIELD).get_attribute("hint") or ""

    def get_password_hint(self) -> str:
        """Return the password field's hint text (for backup verification)."""
        return self.find_visible(self.PASSWORD_FIELD).get_attribute("hint") or ""

    def login(self, username: str, password: str) -> None:
        """Perform a full login: fill credentials and tap the login button.

        Args:
            username: The username to enter.
            password: The password to enter.
        """
        self.type_text(self.USERNAME_FIELD, username)
        self.type_text(self.PASSWORD_FIELD, password)
        self.tap(self.LOGIN_BUTTON)
