# Auth/Registration/WebApp/pages/register_page.py
"""Registration page object for the Furgechat web app.

Encapsulates every locator and interaction for the "Create account" screen. The
test flow in main.py talks to this class only — it never touches raw locators.

Locator notes
-------------
Locators are taken from the real DOM. There is no ``data-testid`` on any field,
so per the locator-priority rule (data-testid > id > name > CSS > XPath) we use
the stable element IDs. Unlike the login screen, the register form has no
captcha and the submit button is enabled from the start.

Still pending (need the POST-REGISTRATION DOM):
    SUCCESS_MARKER  — an optional positive marker shown after a successful
                      registration (e.g. a confirmation banner or chat list).
    ERROR_MESSAGE   — an optional error banner shown on a failed registration
                      (e.g. "username already taken").
Both are placeholders; the test does not depend on them (see
is_registration_successful).
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class RegisterPage(BasePage):
    """Page object representing the registration form and its result."""

    # --- Form locators (from the real DOM; IDs are the most stable here) ----
    USERNAME_INPUT = (By.ID, "username")
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    SUBMIT_BUTTON = (By.ID, "register-submit")

    # The registration form itself, used to confirm we have navigated AWAY
    # from the register page after a successful submit. (app-register is the
    # Angular host component.)
    REGISTER_FORM = (By.CSS_SELECTOR, "app-register form")

    # --- Optional locators (PLACEHOLDERS — fill in from the post-register DOM)
    # A stronger, positive success assertion (e.g. a "welcome" banner or the
    # chat list). Fill in to assert this in addition to the form disappearing.
    SUCCESS_MARKER = (By.CSS_SELECTOR, "SELECTOR_TBD_FROM_INSPECTOR")

    # An error banner shown on a FAILED registration. The register DOM shows
    # none; fill this in if the app renders one, for a clearer failure message.
    ERROR_MESSAGE = (By.CSS_SELECTOR, "SELECTOR_TBD_FROM_INSPECTOR")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the registration page object.

        Args:
            driver: The active Selenium WebDriver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def register(self, username: str, email: str, password: str) -> None:
        """Fill the registration form and submit it.

        Args:
            username: The unique username to register.
            email: The unique email address to register.
            password: The password for the new account.
        """
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)

    def is_registration_successful(self) -> bool:
        """Return True once registration has clearly succeeded.

        Primary signal: the registration form disappears, because the
        single-page app navigates away from <app-register> on success. If a
        positive success marker is configured, that is required as well for a
        stronger check.

        Returns:
            True if registration is confirmed within the timeout, else False.
        """
        left_register_page = self.wait_invisible(self.REGISTER_FORM)

        # If a positive marker has been filled in, require it too; otherwise
        # rely on the registration form going away.
        if self.SUCCESS_MARKER[1] != "SELECTOR_TBD_FROM_INSPECTOR":
            return left_register_page and self.is_visible(self.SUCCESS_MARKER)
        return left_register_page

    def get_error_text(self) -> str:
        """Return the on-screen error message, or an empty string if none.

        Returns "" when no error locator is configured or no error is shown.

        Returns:
            The error banner's text, or "" if no error element is present.
        """
        # No error locator configured yet — nothing to read.
        if self.ERROR_MESSAGE[1] == "SELECTOR_TBD_FROM_INSPECTOR":
            return ""
        if self.is_visible(self.ERROR_MESSAGE, timeout=5):
            return self.find_visible(self.ERROR_MESSAGE).text
        return ""
