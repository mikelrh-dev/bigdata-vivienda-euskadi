"""MongoDB helpers for the vivienda-euskadi project."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "vivienda_euskadi")
MONGO_TEST_DB = os.getenv("MONGO_TEST_DB", "vivienda_euskadi_test")


def get_mongo_uri() -> str | None:
    """Return MONGO_URI from env, or None if unset/blank (Tema 8 §12).

    Read at call time so monkeypatch of MONGO_URI is visible to
    get_client(); do not cache at import.
    """
    uri = os.getenv("MONGO_URI")
    if uri and uri.strip():
        return uri.strip()
    return None


def is_objectid(value: Any) -> bool:
    """True if value is an ObjectId instance or a valid 24-hex string."""
    if isinstance(value, ObjectId):
        return True
    if isinstance(value, str):
        return ObjectId.is_valid(value.strip())
    return False


def to_objectid(value: Any) -> ObjectId | None:
    """Convert value to ObjectId when possible, else None."""
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value.strip()):
        return ObjectId(value.strip())
    return None


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    uri = get_mongo_uri()
    if uri:
        return MongoClient(uri, serverSelectionTimeoutMS=5000)
    return MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)


def get_db() -> Database:
    return get_client()[MONGO_DB]


def get_test_db() -> Database:
    return get_client()[MONGO_TEST_DB]


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
    if isinstance(value, str) and value.strip().lower() in {"nan", "none", "null", "nat"}:
        return None
    try:
        if isinstance(value, float) and value != value:
            return None
        f = float(value)
        if f != f:
            return None
        return f
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
    if isinstance(value, float) and value != value:
        return None
    if isinstance(value, (int, float)):
        return str(int(value)).zfill(5)
    text = to_str(value)
    if text is None:
        return None
    if text.isdigit():
        return text.zfill(5)
    try:
        return str(int(float(text))).zfill(5)
    except (TypeError, ValueError):
        return text


def replace_collection(name: str, docs: list[dict]) -> int:
    if not docs:
        return 0
    db = get_db()
    staging = f"{name}__staging"
    backup = f"{name}__backup"
    db[staging].drop()
    db[staging].insert_many(docs)
    if name in db.list_collection_names():
        db[backup].drop()
        db[name].aggregate([{"$out": backup}])
    db[staging].rename(name, dropTarget=True)
    return len(docs)


CALIDAD_DATOS_VALIDOS = frozenset({"ok", "missing", "verificado", "pendiente"})


def marcar_calidad_municipio(
    codigo_ine: str,
    calidad: str,
    *,
    collection: Collection | None = None,
) -> dict | None:
    """Marca el flag de calidad de un municipio con una actualización atómica.

    Usa find_one_and_update con ReturnDocument.AFTER sobre un único
    documento de municipios: la lectura-modificación-escritura ocurre en
    una sola operación atómica a nivel de documento, sin necesidad de
    transacción multidocumento ni de replica set (Tema 8 §11,
    TRANSACCIONES-01). Devuelve el documento ya actualizado, o None si
    el municipio no existe.

    collection permite inyectar otra colección (p. ej. la base de test
    vivienda_euskadi_test); por defecto usa la base productiva.
    """
    if calidad not in CALIDAD_DATOS_VALIDOS:
        raise ValueError(
            f"calidad no válida: {calidad!r}; "
            f"valores permitidos: {sorted(CALIDAD_DATOS_VALIDOS)}"
        )
    code = zfill_ine(codigo_ine)
    if code is None:
        return None
    coll = collection if collection is not None else get_collection("municipios")
    return coll.find_one_and_update(
        {"_id": code},
        {"$set": {"calidad_datos": calidad}},
        return_document=ReturnDocument.AFTER,
    )