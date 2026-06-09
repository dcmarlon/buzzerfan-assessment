# Chat/NewChat/Android/pages/new_dm_dialog.py
"""'Start New DM' dialog page object for the Furgechat Android app.

This dialog appears after tapping the new-chat FAB. It has a contact-name input
and Create / Cancel buttons.

Quirk: the app REJECTS contact names that contain digits — it shows
"DM Creation Denied: '<name>' contains numbers" and does not create the chat.
So the contact name must be letters-only. With a valid (digit-free) name,
tapping Create closes the dialog and the new chat appears on the dashboard.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver

from pages.base_page import BasePage


class NewDmDialog(BasePage):
    """Page object for the 'Start New DM' dialog."""

    TITLE = (AppiumBy.ACCESSIBILITY_ID, "Start New DM")

    # First (and only) EditText on the dialog: the contact-name input.
    CONTACT_INPUT = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.EditText").instance(0)',
    )

    CREATE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Create")
    CANCEL_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Cancel")  # captured for reuse

    def __init__(self, driver: WebDriver, timeout: int = 20) -> None:
        """Initialize the dialog page object.

        Args:
            driver: The active Appium driver.
            timeout: Maximum seconds any explicit wait will block.
        """
        super().__init__(driver, timeout)

    def wait_until_visible(self) -> bool:
        """Return True if the 'Start New DM' dialog title appears in time."""
        return self.is_present(self.TITLE)

    def enter_contact(self, name: str) -> None:
        """Type the contact name into the dialog's input field.

        Args:
            name: The contact name. MUST be digit-free — the app rejects names
                that contain numbers.
        """
        self.type_text(self.CONTACT_INPUT, name)

    def tap_create(self) -> None:
        """Tap Create. With a valid (digit-free) name this closes the dialog and
        the new chat is added to the dashboard."""
        self.tap(self.CREATE_BUTTON)

    def tap_cancel(self) -> None:
        """Tap Cancel to dismiss the dialog (unused; kept for reuse)."""
        self.tap(self.CANCEL_BUTTON)
