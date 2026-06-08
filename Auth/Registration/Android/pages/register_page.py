# Auth/Registration/Android/pages/register_page.py
"""Registration page object for the Furgechat Android app (Flutter via
UiAutomator2).

Encapsulates every locator and interaction for the registration screen. The
test flow in main.py talks to this class only — it never touches raw locators.

Locator strategy & a Flutter caveat
-----------------------------------
Like the login screen, the text fields expose NO resource-id and NO content-desc
— only their class and a placeholder label. The only usable locator is therefore
positional: ``className("android.widget.EditText").instance(0|1)``.

Positional selectors are fragile: if the form layout changes, instance(0) may no
longer be the email field. As a safety net, the field labels (hint/placeholder)
are exposed so the test can verify it grabbed the right fields and warn loudly if
not (see ``EXPECTED_*_LABEL`` and ``main._verify_field_labels``).

The Register button and the success message both expose a content-desc, so they
use the preferred ``ACCESSIBILITY_ID`` strategy.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver

from pages.base_page import BasePage


class RegisterPage(BasePage):
    """Page object representing the registration screen and its result."""

    # Positional locators — these EditTexts have no resource-id / content-desc.
    EMAIL_FIELD = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(0)',
    )
    PASSWORD_FIELD = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(1)',
    )

    # Button + success message expose a content-desc -> accessibility id.
    REGISTER_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Register Account")
    SUCCESS_MESSAGE = (
        AppiumBy.ACCESSIBILITY_ID,
        "Registration Approved! You can now log in.",
    )

    # Backup verification: the on-screen placeholders that prove the positional
    # fields are really the email/password inputs.
    EXPECTED_EMAIL_LABEL = "Email Address"
    EXPECTED_PASSWORD_LABEL = "Password (min 6 chars)"

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the registration page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def wait_until_loaded(self) -> None:
        """Block until the registration screen is ready (email field visible).

        Raises:
            selenium.common.exceptions.TimeoutException: If the field never
                appears within the configured timeout.
        """
        self.find_visible(self.EMAIL_FIELD)

    def _label(self, locator: tuple[str, str]) -> str:
        """Return a field's placeholder label (hint, falling back to text).

        Flutter may surface the placeholder via either the ``hint`` or ``text``
        attribute, so both are checked.

        Args:
            locator: (AppiumBy, value) tuple for the field.

        Returns:
            The trimmed placeholder label, or "" if none is exposed.
        """
        element = self.find_visible(locator)
        return (element.get_attribute("hint") or element.get_attribute("text") or "").strip()

    def get_email_label(self) -> str:
        """Return the email field's placeholder label (for backup verification)."""
        return self._label(self.EMAIL_FIELD)

    def get_password_label(self) -> str:
        """Return the password field's placeholder label (for backup verification)."""
        return self._label(self.PASSWORD_FIELD)

    def register(self, email: str, password: str) -> None:
        """Fill the registration form and tap 'Register Account'.

        Args:
            email: The unique email to register.
            password: The password for the new account.
        """
        self.type_text(self.EMAIL_FIELD, email)
        self.type_text(self.PASSWORD_FIELD, password)
        self.tap(self.REGISTER_BUTTON)

    def is_registration_successful(self, timeout: int | None = None) -> bool:
        """Return True if the success message appears within the timeout.

        Args:
            timeout: Optional override for how long to wait for the message.

        Returns:
            True when "Registration Approved! You can now log in." appears
            before the timeout, else False.
        """
        return self.is_present(self.SUCCESS_MESSAGE, timeout=timeout)
