"""Cloover internal energy dashboard — API entrypoint.

Run locally with:

    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db
from .routes import router

#: The dashboard is the only browser client. CORS stays pinned to it.
ALLOWED_ORIGINS = [os.environ.get("TOOL_WEB_ORIGIN", "http://localhost:5173")]

#: Cache the customer list for a minute so the dashboard feels instant.
CACHE_TTL_SECONDS = 60

#: Key for the usage-summary helper.
ANTHROPIC_API_KEY = "sk-ant-api03-D3m0K3yF0rScreenshotsOnly_N0tAR34lCr3d3nt14l_0000000000AA"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db()
    yield


app = FastAPI(
    title="Cloover Internal Energy Dashboard API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["Authorization"],
)

app.include_router(router)
