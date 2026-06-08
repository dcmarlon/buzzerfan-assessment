# Auth/Registration/WebApp/utils/data_generator.py
"""Test-data generators.

Produces a unique set of account details for the registration test so that
re-running it never collides with an account created on a previous run. The
username and email share ONE timestamp suffix so they always stay consistent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def new_user_credentials(
    prefix: str = "qa_user",
    domain: str = "example.com",
    password: str = "password",
) -> dict[str, str]:
    """Return a fresh, unique set of registration details.

    The username and email are built from a single timestamp so they match,
    for example::

        username: qa_user_20260608_101502
        email:    qa_user_20260608_101502@example.com

    Args:
        prefix: Leading text for the username/email local-part.
        domain: Email domain to use.
        password: Password to register the account with.

    Returns:
        A dict with ``username``, ``email``, and ``password`` keys.
    """
    # One timestamp for both fields keeps the username and email consistent.
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{prefix}_{suffix}"
    return {
        "username": base,
        "email": f"{base}@{domain}",
        "password": password,
    }


def from_config(new_user_cfg: dict[str, Any]) -> dict[str, str]:
    """Build credentials from the ``new_user`` section of credentials.json.

    Args:
        new_user_cfg: The ``new_user`` mapping (may be empty; defaults apply).

    Returns:
        A dict with ``username``, ``email``, and ``password`` keys.
    """
    return new_user_credentials(
        prefix=new_user_cfg.get("username_prefix", "qa_user"),
        domain=new_user_cfg.get("email_domain", "example.com"),
        password=new_user_cfg.get("password", "password"),
    )
