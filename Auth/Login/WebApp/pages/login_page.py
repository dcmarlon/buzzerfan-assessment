# Auth/Login/WebApp/pages/login_page.py
"""Login page object for the Furgechat web app.

Encapsulates every locator and interaction for the login screen. The test flow
in main.py talks to this class only — it never touches raw locators.

Locator notes
-------------
The form's locators are taken from the real DOM. There is no ``data-testid`` on
any field, so per the locator-priority rule (data-testid > id > name > CSS >
XPath) we use the stable element IDs.

The login screen has a non-obvious flow: the submit button starts DISABLED with
the text "Please wait..." and an "I am not a robot" captcha checkbox must be
ticked before it becomes enabled. The login() method handles this, and the
explicit ``element_to_be_clickable`` wait blocks until the button is enabled.

Still pending (need the POST-LOGIN DOM):
    LOGGED_IN_MARKER  — an optional positive marker that appears after login.
    ERROR_MESSAGE     — an optional error banner shown on a failed login.
Both are placeholders; the test does not depend on them (see is_login_successful).
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object representing the login form and its post-login result."""

    # --- Form locators (from the real DOM; IDs are the most stable here) ----
    USERNAME_INPUT = (By.ID, "login-username")
    PASSWORD_INPUT = (By.ID, "login-password")
    CAPTCHA_CHECKBOX = (By.ID, "captcha")
    SUBMIT_BUTTON = (By.ID, "login-submit")

    # The login form itself, used to confirm we have navigated AWAY from the
    # login page after a successful submit. (app-login is the Angular host.)
    LOGIN_FORM = (By.CSS_SELECTOR, "app-login form")

    # --- Optional locators (PLACEHOLDERS — fill in from the post-login DOM) --
    # A stronger, positive success assertion: an element that exists ONLY after
    # login (e.g. the chat-list container). Fill in to assert this in addition
    # to the login form disappearing.
    LOGGED_IN_MARKER = (By.CSS_SELECTOR, "SELECTOR_TBD_FROM_INSPECTOR")

    # An error banner shown on a FAILED login. The login DOM shows none; fill
    # this in if the app renders one, for a clearer failure message.
    ERROR_MESSAGE = (By.CSS_SELECTOR, "SELECTOR_TBD_FROM_INSPECTOR")

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the login page object.

        Args:
            driver: The active Selenium WebDriver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def login(self, username: str, password: str) -> None:
        """Perform a full login: fill credentials, pass the captcha, submit.

        Args:
            username: The username to enter.
            password: The password to enter.
        """
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.check_captcha()
        self.submit()

    def check_captcha(self) -> None:
        """Tick the 'I am not a robot' checkbox if it is not already ticked.

        The submit button stays disabled ("Please wait...") until this is
        selected, so this step is required for the form to be submittable.
        """
        checkbox = self.find_clickable(self.CAPTCHA_CHECKBOX)
        if not checkbox.is_selected():
            checkbox.click()

    def submit(self) -> None:
        """Click the login button once it becomes enabled.

        The button starts disabled, so ``element_to_be_clickable`` (inside
        ``click``) is exactly the right wait: it blocks until the button is
        both visible and no longer disabled.
        """
        self.click(self.SUBMIT_BUTTON)

    def is_login_successful(self) -> bool:
        """Return True once login has clearly progressed past the login page.

        Primary signal: the login form disappears, because the single-page app
        navigates away from <app-login> on success. If a positive post-login
        marker is configured, that is required as well for a stronger check.

        Returns:
            True if login is confirmed within the timeout, else False.
        """
        left_login_page = self.wait_invisible(self.LOGIN_FORM)

        # If a positive marker has been filled in, require it too; otherwise
        # rely on the login form going away.
        if self.LOGGED_IN_MARKER[1] != "SELECTOR_TBD_FROM_INSPECTOR":
            return left_login_page and self.is_visible(self.LOGGED_IN_MARKER)
        return left_login_page

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
