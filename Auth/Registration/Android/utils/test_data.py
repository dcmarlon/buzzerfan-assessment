# Auth/Registration/Android/utils/test_data.py
"""Test-data generators.

Produces a unique email for the registration test so that re-running it does not
collide with an account created on a previous run. A Unix-timestamp suffix makes
each value unique and human-readable.
"""

from __future__ import annotations

import time


def generate_unique_email(prefix: str = "qa_test", domain: str = "buzzerfan.test") -> str:
    """Return a unique test email, e.g. ``qa_test_1717840000@buzzerfan.test``.

    The integer Unix timestamp suffix changes every second, so each run gets a
    fresh address. (Two runs started within the same second could still collide
    — see the registration Guide's troubleshooting note.)

    Args:
        prefix: Leading text for the email local-part.
        domain: Email domain to use.

    Returns:
        A unique email address string.
    """
    return f"{prefix}_{int(time.time())}@{domain}"
