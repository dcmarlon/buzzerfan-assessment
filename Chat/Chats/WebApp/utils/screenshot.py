# Chat/Chats/WebApp/utils/screenshot.py
"""Screenshot helper.

Saves a timestamped PNG to the ``screenshots/`` folder. Called from the failure
path so that every failed run leaves visual evidence of the browser state at the
exact moment of failure.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

# screenshots/ lives in the feature root, one level up from utils/.
_SHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"


def save_screenshot(driver: WebDriver, label: str = "failure") -> Path:
    """Save a timestamped screenshot and return its path.

    Args:
        driver: The active WebDriver to capture.
        label: Short tag included in the filename (e.g. "chats_not_loaded").

    Returns:
        The :class:`pathlib.Path` to the saved PNG.
    """
    _SHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _SHOT_DIR / f"{label}_{timestamp}.png"
    driver.save_screenshot(str(path))
    return path
