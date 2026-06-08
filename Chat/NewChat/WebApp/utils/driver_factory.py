# Chat/NewChat/WebApp/utils/driver_factory.py
"""WebDriver factory.

Creates and configures a Selenium WebDriver. Centralizing driver creation keeps
browser options consistent and makes it trivial to toggle headless mode (or, in
future, switch browsers) from credentials.json instead of editing code.
"""

from __future__ import annotations

from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


def create_driver(config: dict[str, Any]) -> webdriver.Chrome:
    """Build a Chrome WebDriver from the supplied configuration.

    Selenium 4's built-in Selenium Manager downloads the matching ChromeDriver
    automatically, so no separate driver binary is required.

    Args:
        config: Parsed credentials.json. Reads the optional ``browser`` section
            (``name`` and ``headless``) and the ``timeouts`` section.

    Returns:
        A configured :class:`selenium.webdriver.Chrome` instance.

    Raises:
        ValueError: If a browser other than Chrome is requested.
    """
    browser_cfg = config.get("browser", {})
    name = browser_cfg.get("name", "chrome").lower()
    if name != "chrome":
        # This feature is intentionally Chrome-only; fail loudly rather than
        # silently launching the wrong browser.
        raise ValueError(f"Unsupported browser '{name}'. This feature uses Chrome.")

    options = ChromeOptions()

    # Headless is opt-in via credentials.json so the same script runs in CI.
    if browser_cfg.get("headless", False):
        options.add_argument("--headless=new")

    # Stable defaults that avoid common CI/container startup failures.
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    # A single source of truth for the page-load timeout.
    page_load = config.get("timeouts", {}).get("page_load_seconds", 30)
    driver.set_page_load_timeout(page_load)
    return driver
