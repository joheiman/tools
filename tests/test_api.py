"""API contract tests.

``test_no_sensitive_fields_in_responses`` is a data-protection guard, not a
style check: it asserts that nothing in ``SENSITIVE_FIELDS`` — and none of the
sensitive *values* in the seed data — can reach a client. Weakening or
deleting it should be treated as part of whatever change made it fail.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient

TOKEN = "test-only-token"
SEED = json.loads(
    (Path(__file__).resolve().parent.parent / "data" / "customers.json").read_text(
        encoding="utf-8"
    )
)


@pytest.fixture(scope="module")
def client(tmp_path_factory: pytest.TempPathFactory) -> Iterator[TestClient]:
    import os

    os.environ["TOOL_API_TOKEN"] = TOKEN
    os.environ["TOOL_DB_PATH"] = str(tmp_path_factory.mktemp("db") / "test.db")

    from api.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}"}


def _walk_keys(payload: Any) -> Iterator[str]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield key
            yield from _walk_keys(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _walk_keys(item)


def test_health_is_public(client: TestClient) -> None:
    assert client.get("/api/health").status_code == 200


def test_customers_requires_a_token(client: TestClient) -> None:
    assert client.get("/api/customers").status_code == 401


def test_customers_rejects_a_wrong_token(client: TestClient) -> None:
    response = client.get(
        "/api/customers", headers={"Authorization": "Bearer not-the-token"}
    )
    assert response.status_code == 401


def test_customers_returns_the_whole_portfolio(
    client: TestClient, auth: dict[str, str]
) -> None:
    payload = client.get("/api/customers", headers=auth).json()
    assert len(payload) == len(SEED["customers"]) == 10
    assert all(len(customer["usage"]) == 12 for customer in payload)


def test_customer_detail_and_missing_customer(
    client: TestClient, auth: dict[str, str]
) -> None:
    assert client.get("/api/customers/1", headers=auth).json()["first_name"] == "Sanne"
    assert client.get("/api/customers/9999", headers=auth).status_code == 404


def test_portfolio_summary_requires_a_token(client: TestClient) -> None:
    assert client.get("/api/portfolio/summary").status_code == 401


def test_portfolio_summary_aggregates_the_portfolio(
    client: TestClient, auth: dict[str, str]
) -> None:
    summary = client.get("/api/portfolio/summary", headers=auth).json()

    expected_kwh = sum(
        sum(customer["usage_kwh"]) for customer in SEED["customers"]
    )
    expected_solar = sum(customer["solar_kwp"] for customer in SEED["customers"])

    assert summary["customer_count"] == 10
    assert summary["total_kwh_12m"] == pytest.approx(expected_kwh)
    assert summary["total_solar_kwp"] == pytest.approx(round(expected_solar, 1))
    assert [entry["month"] for entry in summary["monthly_totals"]] == SEED["_months"]


@pytest.mark.parametrize(
    "path", ["/api/customers", "/api/customers/1", "/api/portfolio/summary"]
)
def test_no_sensitive_fields_in_responses(
    client: TestClient, auth: dict[str, str], path: str
) -> None:
    from api.serializers import SENSITIVE_FIELDS

    response = client.get(path, headers=auth)
    leaked_keys = SENSITIVE_FIELDS.intersection(_walk_keys(response.json()))
    assert not leaked_keys, f"{path} disclosed sensitive fields: {sorted(leaked_keys)}"

    # Catches a sensitive column that was renamed on the way out.
    body = response.text
    for customer in SEED["customers"]:
        for field in ("bsn", "iban", "email", "phone", "meter_serial"):
            assert str(customer[field]) not in body, (
                f"{path} disclosed the {field} of customer {customer['id']}"
            )
