"""Response shaping for the customer API.

A customer row holds directly identifying, financial and precise-location
data. Only the columns listed in ``OPERATOR_FIELDS`` may cross the API
boundary, and only to an authenticated internal operator.

``SENSITIVE_FIELDS`` must never appear in an API response. Moving a column
out of that set, or returning a raw database row instead of calling
``operator_view``, changes what customer data this service discloses. That
is a data-exposure change and needs a security review, not only a code
review.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Iterable, Mapping

#: The only customer columns the dashboard is allowed to receive.
OPERATOR_FIELDS: tuple[str, ...] = (
    "id",
    "first_name",
    "last_name",
    "street_address",
    "postcode",
    "city",
    "solar_kwp",
    "tariff",
)

#: Columns that must not leave the service under any circumstances.
SENSITIVE_FIELDS: frozenset[str] = frozenset(
    {
        "email",
        "phone",
        "dob",
        "bsn",
        "iban",
        "meter_serial",
        "lat",
        "lng",
    }
)


def operator_view(
    customer: Mapping[str, Any] | sqlite3.Row,
    usage: Iterable[Mapping[str, Any] | sqlite3.Row],
) -> dict[str, Any]:
    """Project a customer row onto the operator-visible allowlist."""
    view: dict[str, Any] = {field: customer[field] for field in OPERATOR_FIELDS}
    view["usage"] = [{"month": row["month"], "kwh": row["kwh"]} for row in usage]
    return view
