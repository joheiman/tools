"""Authentication for the internal dashboard.

Every route that returns customer data depends on ``require_internal_auth``.
The tool is internal-only: there is no anonymous access path to customer
records, and adding one would make this data public.

The expected token comes from the environment (see ``.env.example``); it is
never hard-coded here.
"""

from __future__ import annotations

import hmac
import os
from dataclasses import dataclass

from fastapi import Header, HTTPException, status

_UNAUTHORIZED = {"WWW-Authenticate": "Bearer"}


@dataclass(frozen=True)
class Operator:
    """An authenticated internal user of the dashboard."""

    name: str


def _expected_token() -> str:
    token = os.environ.get("TOOL_API_TOKEN")
    if not token:
        raise RuntimeError(
            "TOOL_API_TOKEN is not set. Copy .env.example to .env and set a value."
        )
    return token


def require_internal_auth(
    authorization: str | None = Header(default=None),
) -> Operator:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers=_UNAUTHORIZED,
        )

    presented = authorization[len("Bearer ") :].strip()
    if not hmac.compare_digest(presented, _expected_token()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers=_UNAUTHORIZED,
        )

    return Operator(name="internal-operator")
