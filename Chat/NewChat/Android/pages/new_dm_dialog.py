# Chat/NewChat/Android/pages/new_dm_dialog.py
"""'Start New DM' dialog page object for the Furgechat Android app.

This dialog appears after tapping the new-chat FAB. It has a contact-name input
and Create / Cancel buttons.

Quirks: tapping Create creates the chat but does NOT close the dialog, and the
Create/Cancel buttons ignore Appium's element clicks. So after Create we close
the dialog by tapping its full-screen modal "Dismiss" barrier (a real W3C touch
above the centred dialog); the new chat then appears on the dashboard to open.
"""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

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

    # Transient confirmation toast. The contact name is embedded, so we match on
    # the stable prefix with descriptionContains rather than the exact string.
    APPROVAL_TOAST = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("DM Creation Approved for")',
    )

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
            name: The contact name for the new DM.
        """
        self.type_text(self.CONTACT_INPUT, name)

    def tap_create(self) -> None:
        """Tap the Create button to create the DM."""
        self.tap(self.CREATE_BUTTON)

    def tap_cancel(self) -> None:
        """Tap the Cancel button to dismiss the dialog (unused; kept for reuse)."""
        self.tap(self.CANCEL_BUTTON)

    def dismiss(self) -> None:
        """Close the dialog by tapping the modal barrier above the dialog box.

        Quirk: tapping Create creates the chat but does NOT close this dialog,
        and its buttons ignore Appium's element clicks. Tapping the full-screen
        "Dismiss" barrier ABOVE the centred dialog (a real W3C touch) closes it,
        leaving the freshly created chat on the dashboard.
        """
        size = self.driver.get_window_size()
        x, y = size["width"] // 12, size["height"] // 9
        touch = PointerInput(interaction.POINTER_TOUCH, "finger")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(x, y).pointer_down().pause(0.1).pointer_up()
        actions.perform()

    def wait_for_approval_toast(self, timeout: int = 8) -> bool:
        """Return True if the transient 'DM Creation Approved' toast is caught.

        The toast only shows for a few seconds, so this is best-effort: a False
        result is NOT a failure (the real success check is that messages send).

        Args:
            timeout: Maximum seconds to watch for the toast.

        Returns:
            True if the toast was observed before the timeout, else False.
        """
        return self.is_present(self.APPROVAL_TOAST, timeout=timeout)
