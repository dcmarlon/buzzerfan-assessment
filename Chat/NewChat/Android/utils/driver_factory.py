# Chat/NewChat/Android/utils/driver_factory.py
"""Appium driver factory and configuration loading.

Responsibilities:
- Load the static Appium settings from ``capabilities.json``.
- Load the per-machine values (APK path, credentials) from ``credentials.json``.
- Convert the relative APK path into an absolute path at runtime so the test is
  portable across machines (the helper is ``resolve_apk_path``).
- Build and return a connected Appium (UiAutomator2) driver.

The app package/activity are intentionally NOT set — Appium reads them straight
from the APK via the ``appium:app`` capability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from appium import webdriver
from appium.options.android import UiAutomator2Options

# Feature root = Chat/NewChat/Android (one level up from utils/).
_FEATURE_ROOT = Path(__file__).resolve().parent.parent
_CAPABILITIES_PATH = _FEATURE_ROOT / "capabilities.json"
_CREDENTIALS_PATH = _FEATURE_ROOT / "credentials.json"

# Repo root is three levels up: <repo>/Chat/NewChat/Android. Relative APK paths
# in credentials.json are interpreted from here.
_REPO_ROOT = _FEATURE_ROOT.parents[2]


def _load_json(path: Path, *, hint: str = "") -> dict[str, Any]:
    """Load a JSON file into a dict, with a helpful error if it is missing.

    Args:
        path: The file to read.
        hint: Extra guidance appended to the error message when absent.

    Returns:
        The parsed JSON object.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}. {hint}".strip())
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_settings() -> dict[str, Any]:
    """Load the static Appium settings (server URL, timeouts, capabilities).

    Returns:
        The parsed contents of capabilities.json.
    """
    return _load_json(_CAPABILITIES_PATH)


def load_credentials() -> dict[str, Any]:
    """Load the per-machine credentials (apk_path, username, password).

    Returns:
        The parsed contents of credentials.json.

    Raises:
        FileNotFoundError: If credentials.json has not been created yet.
    """
    return _load_json(
        _CREDENTIALS_PATH,
        hint="Copy credentials.example.json to credentials.json and fill it in.",
    )


def resolve_apk_path(apk_path: str) -> str:
    """Convert the configured APK path into an absolute filesystem path.

    A relative path is interpreted from the repository root, so the value in
    credentials.json stays portable (e.g. "Assets/furgechat.apk"). An absolute
    path is returned unchanged.

    Args:
        apk_path: The ``apk_path`` value from credentials.json.

    Returns:
        The absolute path to the APK as a string.
    """
    candidate = Path(apk_path)
    if candidate.is_absolute():
        return str(candidate)
    return str((_REPO_ROOT / candidate).resolve())


def create_driver(settings: dict[str, Any], credentials: dict[str, Any]) -> webdriver.Remote:
    """Create a connected Appium (UiAutomator2) driver.

    The placeholder ``appium:app`` in the capabilities is replaced with the
    APK's absolute path (resolved from ``credentials['apk_path']``) so Appium
    can locate it regardless of where the repo is checked out.

    Args:
        settings: Parsed capabilities.json (server, timeouts, capabilities).
        credentials: Parsed credentials.json (must contain ``apk_path``).

    Returns:
        A connected Appium :class:`webdriver.Remote` session.
    """
    # Copy so we never mutate the loaded settings dict.
    caps = dict(settings["capabilities"])
    caps["appium:app"] = resolve_apk_path(credentials["apk_path"])

    options = UiAutomator2Options().load_capabilities(caps)
    server_url = settings.get("appium_server", "http://127.0.0.1:4723")
    return webdriver.Remote(server_url, options=options)
