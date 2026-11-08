"""clean_mongo con mongomock (storage/clean_mongo.py).

canonicalize_codigo_ine, resolve_duplicates y convert_types sobre
mongomock en memoria: aserta contadores y que re-ejecutar es no-op.
Sin Mongo real. Si mongomock no esta instalado, todo el modulo skip
(como test_integracion_mongo.py).
Nota: mongomock no implementa $convert con documentos coincidentes,
asi que convert_types se prueba con documentos no convertibles
(contadores a cero), que es el caso verificable en ambos motores.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

mongomock = pytest.importorskip(
    "mongomock", reason="mongomock no instalado: skip offline")

import storage.clean_mongo as cm  # noqa: E402


@pytest.fixture()
def db(monkeypatch):
    client = mongomock.MongoClient()
    database = client["clean_test"]
    monkeypatch.setattr(cm, "get_collection", lambda name: database[name])
    return database


def test_canonicalize_codigo_ine_contadores_y_noop(db):
    """codigo_ine no canonico se corrige; segunda pasada modifica 0."""
    db["municipios"].insert_one({"_id": "48020", "nombre_canonico": "Bilbao"})
    db["anuncios"].insert_many([
        {"_id": "a1", "portal": "pisos", "id_anuncio": "1",
         "ubicacion": {"codigo_ine": "48020"}},
        {"_id": "a2", "portal": "pisos", "id_anuncio": "2",
         "ubicacion": {"codigo_ine": 48020}},
        {"_id": "a3", "portal": "fotocasa", "id_anuncio": "3",
         "ubicacion": {"codigo_ine": "48020"}},
    ])
    out = cm.canonicalize_codigo_ine()
    assert out["municipios_checked"] == 1
    assert out["municipios_bad_ids"] == 0
    assert out["anuncios"]["matched_count"] == 3
    assert out["anuncios"]["modified_count"] == 1  # solo a2 (int -> "48020")
    assert db["anuncios"].find_one({"_id": "a2"})["ubicacion"]["codigo_ine"] == "48020"
    # Re-ejecutar es no-op en modificaciones
    out2 = cm.canonicalize_codigo_ine()
    assert out2["anuncios"]["modified_count"] == 0
    assert out2["anuncios"]["matched_count"] == 3


def test_resolve_duplicates_contadores_y_noop(db):
    """Duplicados por (portal,id_anuncio) se borran; segunda pasada 0."""
    db["anuncios"].insert_many([
        {"_id": "a1", "portal": "pisos", "id_anuncio": "1"},
        {"_id": "a2", "portal": "pisos", "id_anuncio": "1"},
        {"_id": "a3", "portal": "pisos", "id_anuncio": "2"},
    ])
    out = cm.resolve_duplicates()
    assert out["deleted"] == 1
    assert out["groups"] == 1
    assert db["anuncios"].count_documents({}) == 2
    # El superviviente es determinista (menor _id)
    assert db["anuncios"].find_one({"_id": "a1"}) is not None
    # Re-ejecutar es no-op
    out2 = cm.resolve_duplicates()
    assert out2["deleted"] == 0
    assert out2["groups"] == 0
    assert db["anuncios"].count_documents({}) == 2


def test_resolve_duplicates_por_fingerprint(db):
    """Duplicados por property_fingerprint tambien se resuelven."""
    db["anuncios"].insert_many([
        {"_id": "f1", "portal": "pisos", "id_anuncio": "10",
         "property_fingerprint": "fp-mismo"},
        {"_id": "f2", "portal": "fotocasa", "id_anuncio": "20",
         "property_fingerprint": "fp-mismo"},
        {"_id": "f3", "portal": "pisos", "id_anuncio": "30",
         "property_fingerprint": "fp-distinto"},
    ])
    out = cm.resolve_duplicates()
    # 1 borrado por fingerprint (f2), grupos: 0 por (portal,id) + 1 por fp
    assert out["deleted"] == 1
    assert db["anuncios"].count_documents({}) == 2
    out2 = cm.resolve_duplicates()
    assert out2["deleted"] == 0


def test_convert_types_sin_convertibles_cero_y_noop(db):
    """Sin precios string ni habitaciones, convert_types no toca nada (mongomock-safe)."""
    db["anuncios"].insert_many([
        {"_id": "a1", "precio_eur": None, "habitaciones": None},
        {"_id": "a2", "habitaciones": None},
    ])
    db["municipios"].insert_one({"_id": "48020"})
    out = cm.convert_types()
    assert out["precios_string_convertidos"]["matched_count"] == 0
    assert out["habitaciones_convertidas"]["matched_count"] == 0
    assert out["tiene_alquiler_oficial_convertidos"]["matched_count"] == 0
    assert out["tiene_fianzas_emal_convertidos"]["matched_count"] == 0
    out2 = cm.convert_types()
    assert out2["precios_string_convertidos"]["modified_count"] == 0
    assert out2["habitaciones_convertidas"]["modified_count"] == 0
    assert db["anuncios"].count_documents({}) == 2
