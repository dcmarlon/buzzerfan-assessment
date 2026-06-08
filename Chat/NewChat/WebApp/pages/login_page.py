# Chat/NewChat/WebApp/pages/login_page.py
"""Login page object — used to authenticate before creating a chat.

Creating a chat is a write action, so a fresh browser must sign in first. This
mirrors the standalone Auth/Login page object, including the captcha gate on the
submit button. It can be disabled via ``login.enabled = false`` in
credentials.json if the environment does not require it.

Locator notes
-------------
No ``data-testid`` exists, so per the priority rule (data-testid > id > name >
CSS > XPath) the stable element IDs are used. The submit button starts DISABLED
("Please wait...") until the "I am not a robot" captcha checkbox is ticked, so
``element_to_be_clickable`` is used to wait for it to become enabled.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object for the login form (pre-step for creating a chat)."""

    USERNAME_INPUT = (By.ID, "login-username")
    PASSWORD_INPUT = (By.ID, "login-password")
    CAPTCHA_CHECKBOX = (By.ID, "captcha")
    SUBMIT_BUTTON = (By.ID, "login-submit")

    # The login form, used to confirm we have navigated away on success.
    LOGIN_FORM = (By.CSS_SELECTOR, "app-login form")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the login page object.

        Args:
            driver: The active Selenium WebDriver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def login(self, username: str, password: str) -> None:
        """Fill credentials, pass the captcha, and submit the form.

        Args:
            username: The username to enter.
            password: The password to enter.
        """
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.check_captcha()
        self.submit()

    def check_captcha(self) -> None:
        """Tick the 'I am not a robot' checkbox if not already ticked.

        The submit button stays disabled until this is selected.
        """
        checkbox = self.find_clickable(self.CAPTCHA_CHECKBOX)
        if not checkbox.is_selected():
            checkbox.click()

    def submit(self) -> None:
        """Click the login button once it becomes enabled.

        The button starts disabled, so ``element_to_be_clickable`` (inside
        ``click``) blocks until it is both visible and no longer disabled.
        """
        self.click(self.SUBMIT_BUTTON)

    def is_login_successful(self) -> bool:
        """Return True once the login form has gone away (login succeeded).

        Returns:
            True if the login form becomes invisible/absent before timeout.
        """
        return self.wait_invisible(self.LOGIN_FORM)
