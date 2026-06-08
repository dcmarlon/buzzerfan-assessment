# Auth/Registration/WebApp/utils/config.py
"""Configuration loader.

Reads connection details and the new-account template from ``credentials.json``
so that no URL or value is ever hardcoded in the test logic. Keeping this in one
place means the test can be re-pointed at a different environment by editing a
single file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# credentials.json lives in the feature root, one level up from utils/.
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "credentials.json"


def load_config() -> dict[str, Any]:
    """Load and return the contents of ``credentials.json`` as a dict.

    Returns:
        The parsed configuration dictionary.

    Raises:
        FileNotFoundError: If credentials.json is missing.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {_CONFIG_PATH}. "
            "Make sure credentials.json is present in the feature folder."
        )

    with _CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)
