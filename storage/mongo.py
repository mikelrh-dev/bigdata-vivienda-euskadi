"""MongoDB helpers for the vivienda-euskadi project."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "vivienda_euskadi")


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    return MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)


def get_db() -> Database:
    return get_client()[MONGO_DB]


def get_collection(name: str) -> Collection:
    return get_db()[name]


def ping() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False


def close() -> None:
    get_client().close()


def to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        if isinstance(value, float) and value != value:
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, float) and value != value:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "si", "sí", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def to_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and value != value:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    return text


def zfill_ine(value: Any) -> str | None:
    text = to_str(value)
    if text is None:
        return None
    if text.isdigit():
        return text.zfill(5)
    return text