# Auth/Login/WebApp/pages/register_page.py
"""Registration helper used to seed the login account.

This Furgechat web app stores registered users in the browser (client-side),
so a fresh Selenium session starts with no users and "admin" cannot log in until
it has been created in THAT session. This small page object lets the Login flow
register the account first (same browser session) so there is something to log
in as. Locators come from the register screen's DOM (stable element IDs).
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class RegisterPage(BasePage):
    """Page object for the registration form (used to seed the login account)."""

    USERNAME_INPUT = (By.ID, "username")
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    SUBMIT_BUTTON = (By.ID, "register-submit")

    # The app shows this confirmation text after a successful registration.
    # There is no id on the message, so a relative text-based XPath is the only
    # available hook (used as a last resort, per the locator-priority rule).
    SUCCESS_MESSAGE = (By.XPATH, "//*[contains(text(), 'Account created')]")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the registration page object.

        Args:
            driver: The active Selenium WebDriver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def register(self, username: str, email: str, password: str) -> bool:
        """Fill and submit the registration form, then wait for confirmation.

        Args:
            username: The account username to create.
            email: The account email address.
            password: The account password.

        Returns:
            True if the "Account created" confirmation appeared in time, else
            False (the caller can still attempt to log in).
        """
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)
        # Wait for the on-screen confirmation so the account is written to
        # browser storage before we navigate away to log in.
        return self.is_visible(self.SUCCESS_MESSAGE, timeout=10)
