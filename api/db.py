"""SQLite storage for the internal energy dashboard.

The database is seeded from ``data/customers.json`` on first start, so a
checkout is runnable without a migration step. All queries here are
parameterised; string-formatting user input into SQL is not acceptable in
this file.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = REPO_ROOT / "data" / "customers.json"

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id             INTEGER PRIMARY KEY,
    first_name     TEXT NOT NULL,
    last_name      TEXT NOT NULL,
    street_address TEXT NOT NULL,
    postcode       TEXT NOT NULL,
    city           TEXT NOT NULL,
    lat            REAL NOT NULL,
    lng            REAL NOT NULL,
    email          TEXT NOT NULL,
    phone          TEXT NOT NULL,
    dob            TEXT NOT NULL,
    bsn            TEXT NOT NULL,
    iban           TEXT NOT NULL,
    meter_serial   TEXT NOT NULL,
    solar_kwp      REAL NOT NULL,
    tariff         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usage_monthly (
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    month       TEXT NOT NULL,
    kwh         REAL NOT NULL,
    PRIMARY KEY (customer_id, month)
);
"""

_CUSTOMER_COLUMNS = (
    "id",
    "first_name",
    "last_name",
    "street_address",
    "postcode",
    "city",
    "lat",
    "lng",
    "email",
    "phone",
    "dob",
    "bsn",
    "iban",
    "meter_serial",
    "solar_kwp",
    "tariff",
)


def db_path() -> Path:
    """Resolved at call time so tests can point at a temporary file."""
    return Path(os.environ.get("TOOL_DB_PATH", REPO_ROOT / "tool.db"))


@contextmanager
def session() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with session() as conn:
        conn.executescript(SCHEMA)
        already_seeded = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        if already_seeded:
            return
        _seed(conn)
        conn.commit()


def _seed(conn: sqlite3.Connection) -> None:
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    months = payload["_months"]

    placeholders = ", ".join("?" for _ in _CUSTOMER_COLUMNS)
    insert_customer = (
        f"INSERT INTO customers ({', '.join(_CUSTOMER_COLUMNS)}) VALUES ({placeholders})"
    )

    for customer in payload["customers"]:
        conn.execute(insert_customer, [customer[column] for column in _CUSTOMER_COLUMNS])
        conn.executemany(
            "INSERT INTO usage_monthly (customer_id, month, kwh) VALUES (?, ?, ?)",
            [
                (customer["id"], month, kwh)
                for month, kwh in zip(months, customer["usage_kwh"])
            ],
        )


def all_customers(
    conn: sqlite3.Connection, city: str | None = None
) -> list[sqlite3.Row]:
    """Every customer, optionally narrowed to one city.

    ``city`` reaches this function straight from a query string, so it is
    bound as a parameter rather than formatted into the SQL.
    """
    if city is None:
        return conn.execute("SELECT * FROM customers ORDER BY id").fetchall()
    return conn.execute(
        "SELECT * FROM customers WHERE city = ? COLLATE NOCASE ORDER BY id",
        (city,),
    ).fetchall()


def customer_by_id(conn: sqlite3.Connection, customer_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM customers WHERE id = ?", (customer_id,)
    ).fetchone()


def usage_for(conn: sqlite3.Connection, customer_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT month, kwh FROM usage_monthly WHERE customer_id = ? ORDER BY month",
        (customer_id,),
    ).fetchall()
