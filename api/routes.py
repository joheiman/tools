"""HTTP routes for the internal energy dashboard."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from . import db
from .auth import Operator, require_internal_auth
from .serializers import operator_view

router = APIRouter()


@router.get("/api/health")
def health() -> dict[str, str]:
    """Liveness probe. Deliberately the only unauthenticated route."""
    return {"status": "ok"}


@router.get("/api/customers")
def list_customers() -> list[dict[str, Any]]:
    with db.session() as conn:
        return [
            operator_view(row, db.usage_for(conn, row["id"]))
            for row in db.all_customers(conn)
        ]


@router.get("/api/customers/{customer_id}")
def get_customer(
    customer_id: int,
    _operator: Operator = Depends(require_internal_auth),
) -> dict[str, Any]:
    with db.session() as conn:
        row = db.customer_by_id(conn, customer_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found."
            )
        return operator_view(row, db.usage_for(conn, customer_id))
