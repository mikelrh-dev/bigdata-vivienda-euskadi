"""Integración Mongo offline: mongomock o skip.

Nunca conecta al centro ni a Mongo real en este módulo: si mongomock no
está instalado todo el módulo queda skipped (no en fallo). Mongo real
local (localhost:27017) solo se toca en modo vivo mañana, opt-in.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

mongomock = pytest.importorskip(
    "mongomock", reason="mongomock no instalado: integracion skip offline"
)


@pytest.fixture()
def coll() -> object:
    client = mongomock.MongoClient()
    return client["gate_test"]["anuncios"]


def test_insert_y_find(coll: object) -> None:
    coll.insert_one({"_id": "a1", "municipio": "48020", "precio_eur": 900})
    doc = coll.find_one({"_id": "a1"})
    assert doc is not None
    assert doc["municipio"] == "48020"


def test_reintento_upsert_cero_duplicados(coll: object) -> None:
    doc = {"_id": "r1", "precio_eur": 1000}
    coll.replace_one({"_id": "r1"}, doc, upsert=True)
    coll.replace_one({"_id": "r1"}, doc, upsert=True)  # reintento idéntico
    assert coll.count_documents({}) == 1


def test_indice_y_agregacion(coll: object) -> None:
    coll.create_index("municipio")
    coll.insert_many([
        {"_id": "g1", "municipio": "48020", "precio_eur": 900},
        {"_id": "g2", "municipio": "48020", "precio_eur": 1100},
    ])
    out = list(coll.aggregate(
        [{"$group": {"_id": "$municipio", "media": {"$avg": "$precio_eur"}}}] ))
    assert out and out[0]["media"] == pytest.approx(1000.0)
