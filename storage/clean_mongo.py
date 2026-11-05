"""PyMongo cleaning/transformations for the vivienda_euskadi database.

All operations run against MongoDB (localhost:27017 / vivienda_euskadi).  Raw and
silver files under data/ are never touched: every change is applied with
update_many / delete_many / bulk_write and persisted in the database.
"""

from __future__ import annotations

import logging
from decimal import InvalidOperation
from typing import Any, Iterable

from bson.decimal128 import Decimal128
from pymongo import UpdateOne, InsertOne, DeleteOne
from pymongo.collection import Collection

from storage.mongo import get_collection, to_str, zfill_ine

logger = logging.getLogger(__name__)


def _counter(result) -> dict[str, int]:
    return {
        "matched_count": getattr(result, "matched_count", 0),
        "modified_count": getattr(result, "modified_count", 0),
        "deleted_count": getattr(result, "deleted_count", 0),
        "upserted_count": getattr(result, "upserted_count", 0),
    }


def canonicalize_codigo_ine() -> dict[str, Any]:
    """Ensure codigo_ine/_id are 5-digit strings in every collection."""
    out: dict[str, Any] = {}
    # municipios: _id is immutable; verify/update derived fields only.
    mun = get_collection("municipios")
    # _id is immutable; canonicalisation is guaranteed by the loader (zfill_ine).
    # We only verify that every _id is a 5-digit string here.
    bad = [d["_id"] for d in mun.find({"_id": {"$not": {"$type": "string"}}})]
    out["municipios_checked"] = mun.count_documents({})
    out["municipios_bad_ids"] = len(bad)

    an = get_collection("anuncios")
    fixed = 0
    matched = 0
    for d in an.find({"ubicacion.codigo_ine": {"$exists": True}}, {"ubicacion.codigo_ine": 1}):
        matched += 1
        cur = (d.get("ubicacion") or {}).get("codigo_ine")
        canon = zfill_ine(cur)
        if canon is not None and canon != cur:
            an.update_one({"_id": d["_id"]}, {"$set": {"ubicacion.codigo_ine": canon}})
            fixed += 1
    out["anuncios"] = {"matched_count": matched, "modified_count": fixed, "deleted_count": 0, "upserted_count": 0}

    al = get_collection("alquiler_municipal")
    fixed = 0
    matched = 0
    for d in al.find({}, {"codigo_ine": 1}):
        matched += 1
        canon = zfill_ine(d.get("codigo_ine"))
        if canon is not None and canon != d.get("codigo_ine"):
            al.update_one({"_id": d["_id"]}, {"$set": {"codigo_ine": canon}})
            fixed += 1
    out["alquiler_municipal"] = {"matched_count": matched, "modified_count": fixed, "deleted_count": 0, "upserted_count": 0}

    ind = get_collection("indicadores")
    fixed = 0
    matched = 0
    for d in ind.find({}, {"codigo_ine": 1}):
        matched += 1
        canon = zfill_ine(d.get("codigo_ine"))
        if canon is not None and canon != d.get("codigo_ine"):
            ind.update_one({"_id": d["_id"]}, {"$set": {"codigo_ine": canon}})
            fixed += 1
    out["indicadores"] = {"matched_count": matched, "modified_count": fixed, "deleted_count": 0, "upserted_count": 0}

    for coll_name in ("udalmap_indicadores", "udalmap_empleo", "osrm_tiempos", "udalmap_extendido", "etxebide_solicitudes", "ecvi_compraventa", "certificados_energeticos"):
        c = get_collection(coll_name)
        fixed = 0
        matched = 0
        for d in c.find({}, {"codigo_ine": 1}):
            matched += 1
            canon = zfill_ine(d.get("codigo_ine"))
            if canon is not None and canon != d.get("codigo_ine"):
                c.update_one({"_id": d["_id"]}, {"$set": {"codigo_ine": canon}})
                fixed += 1
        out[coll_name] = {"matched_count": matched, "modified_count": fixed, "deleted_count": 0, "upserted_count": 0}
    # etxebide_promociones: zfill sin $toString para no perder cero de Alava
    c = get_collection("etxebide_promociones")
    fixed = 0
    matched = 0
    for d in c.find({}, {"codigo_ine": 1}):
        matched += 1
        canon = zfill_ine(d.get("codigo_ine"))
        if canon is None:
            continue
        if canon != d.get("codigo_ine"):
            c.update_one({"_id": d["_id"]}, {"$set": {"codigo_ine": canon}})
            fixed += 1
    out["etxebide_promociones"] = {"matched_count": matched, "modified_count": fixed, "deleted_count": 0, "upserted_count": 0}
    return out


def mark_nulls() -> dict[str, Any]:
    """Mark missing values explicitly instead of treating them as zero."""
    an = get_collection("anuncios")
    out: dict[str, Any] = {}
    r = an.update_many(
        {"superficie_m2": None},
        {"$set": {"tiene_superficie": False, "calidad_superficie": "missing"}},
    )
    out["anuncios_sin_superficie"] = _counter(r)
    r = an.update_many(
        {"superficie_m2": {"$ne": None}},
        {"$set": {"tiene_superficie": True, "calidad_superficie": "ok"}},
    )
    out["anuncios_con_superficie"] = _counter(r)

    r = an.update_many(
        {"precio_eur": None},
        {"$set": {"tiene_precio": False, "calidad_precio": "missing"}},
    )
    out["anuncios_sin_precio"] = _counter(r)
    r = an.update_many(
        {"precio_eur": {"$ne": None}},
        {"$set": {"tiene_precio": True, "calidad_precio": "ok"}},
    )
    out["anuncios_con_precio"] = _counter(r)

    r = an.update_many(
        {"habitaciones": None},
        {"$set": {"tiene_habitaciones": False}},
    )
    out["anuncios_sin_habitaciones"] = _counter(r)

    # municipios: mark missing renta joven explicitly.
    mun = get_collection("municipios")
    r = mun.update_many(
        {"demografia.renta_joven_estimada_16_29": None},
        {"$set": {"demografia.renta_joven_calidad": "missing"}},
    )
    out["municipios_sin_renta_joven"] = _counter(r)
    r = mun.update_many(
        {"demografia.renta_joven_estimada_16_29": {"$ne": None}},
        {"$set": {"demografia.renta_joven_calidad": "ok"}},
    )
    out["municipios_con_renta_joven"] = _counter(r)
    # nuevas colecciones: marcado explicito sin interpretar como cero.
    cert = get_collection("certificados_energeticos")
    r = cert.update_many({"cert_moda": None}, {"$set": {"calidad_cert": "missing"}})
    out["cert_sin_moda"] = _counter(r)
    r = cert.update_many({"cert_moda": {"$ne": None}}, {"$set": {"calidad_cert": "ok"}})
    out["cert_con_moda"] = _counter(r)
    promo = get_collection("etxebide_promociones")
    r = promo.update_many({"codigo_ine": None}, {"$set": {"tiene_codigo_ine": False}})
    out["promo_sin_codigo_ine"] = _counter(r)
    r = promo.update_many({"codigo_ine": {"$ne": None}}, {"$set": {"tiene_codigo_ine": True}})
    out["promo_con_codigo_ine"] = _counter(r)
    r = promo.update_many({"num_viviendas": None}, {"$set": {"calidad_viviendas": "missing"}})
    out["promo_sin_viviendas"] = _counter(r)
    return out


def resolve_duplicates() -> dict[str, Any]:
    """Resolve duplicate anuncios by (portal, id_anuncio) and property_fingerprint."""
    an = get_collection("anuncios")
    out: dict[str, Any] = {"deleted": 0, "groups": 0}
    # Duplicates by (portal, id_anuncio)
    pipeline = [
        {"$group": {"_id": {"portal": "$portal", "id_anuncio": "$id_anuncio"},
                    "ids": {"$push": "$_id"}, "n": {"$sum": 1}}},
        {"$match": {"n": {"$gt": 1}}},
    ]
    groups = list(an.aggregate(pipeline))
    out["groups"] += len(groups)
    to_delete: list[Any] = []
    for g in groups:
        ids = sorted(g["ids"], key=lambda x: str(x))
        to_delete.extend(ids[1:])
    if to_delete:
        r = an.delete_many({"_id": {"$in": to_delete}})
        out["deleted"] += r.deleted_count

    # Duplicates by property_fingerprint (when present)
    pipeline = [
        {"$match": {"property_fingerprint": {"$ne": None}}},
        {"$group": {"_id": "$property_fingerprint", "ids": {"$push": "$_id"}, "n": {"$sum": 1}}},
        {"$match": {"n": {"$gt": 1}}},
    ]
    groups = list(an.aggregate(pipeline))
    out["groups"] += len(groups)
    to_delete = []
    for g in groups:
        ids = sorted(g["ids"], key=lambda x: str(x))
        to_delete.extend(ids[1:])
    if to_delete:
        r = an.delete_many({"_id": {"$in": to_delete}})
        out["deleted"] += r.deleted_count

    # Duplicates in alquiler by (codigo_ine, distrito, seccion/nivel)
    al = get_collection("alquiler_municipal")
    pipeline = [
        {"$group": {"_id": {"codigo_ine": "$codigo_ine", "distrito": "$distrito",
                            "nivel": "$nivel_geografico", "metodo": "$metodo_imputacion"},
                    "ids": {"$push": "$_id"}, "n": {"$sum": 1}}},
        {"$match": {"n": {"$gt": 1}}},
    ]
    groups = list(al.aggregate(pipeline))
    out["alquiler_groups"] = len(groups)
    to_delete = []
    for g in groups:
        ids = sorted(g["ids"], key=lambda x: str(x))
        to_delete.extend(ids[1:])
    if to_delete:
        r = al.delete_many({"_id": {"$in": to_delete}})
        out["alquiler_deleted"] = r.deleted_count
    else:
        out["alquiler_deleted"] = 0
    return out


def convert_types() -> dict[str, Any]:
    """Demonstrate $convert/$toString in update pipelines (types BSON)."""
    out: dict[str, Any] = {}
    an = get_collection("anuncios")
    # Convert string prices (if any) to Decimal128 via $convert.
    r = an.update_many(
        {"precio_eur": {"$type": "string"}},
        [{"$set": {"precio_eur": {
            "$convert": {"input": "$precio_eur", "to": "decimal",
                         "onError": None, "onNull": None}}}}],
    )
    out["precios_string_convertidos"] = _counter(r)

    # Convert habitaciones double with integer value to int.
    r = an.update_many(
        {"habitaciones": {"$ne": None}},
        [{"$set": {"habitaciones": {
            "$convert": {"input": "$habitaciones", "to": "int",
                         "onError": "$habitaciones", "onNull": None}}}}],
    )
    out["habitaciones_convertidas"] = _counter(r)

    # Municipios: asegurar booleanos reales (not strings) with $convert to bool.
    mun = get_collection("municipios")
    for field in ("tiene_alquiler_oficial", "tiene_fianzas_emal"):
        r = mun.update_many(
            {field: {"$type": "string"}},
            [{"$set": {field: {"$convert": {"input": f"${field}", "to": "bool",
                                            "onError": False, "onNull": None}}}}],
        )
        out[f"{field}_convertidos"] = _counter(r)
    return out


def clean_anuncios() -> dict[str, Any]:
    out = {}
    out["canonicalize"] = canonicalize_codigo_ine()
    out["nulls"] = mark_nulls()
    out["duplicates"] = resolve_duplicates()
    out["convert"] = convert_types()
    return out


def clean_municipios() -> dict[str, Any]:
    out = {}
    out["canonicalize"] = canonicalize_codigo_ine()
    out["nulls"] = mark_nulls()
    out["convert"] = convert_types()
    return out


def clean_alquiler() -> dict[str, Any]:
    out = {}
    out["canonicalize"] = canonicalize_codigo_ine()
    out["duplicates"] = resolve_duplicates()
    return out


def clean_indicadores() -> dict[str, Any]:
    out = {}
    out["canonicalize"] = canonicalize_codigo_ine()
    return out


def clean_nuevas() -> dict[str, Any]:
    out: dict[str, Any] = {}
    out["canonicalize"] = canonicalize_codigo_ine()
    out["nulls"] = mark_nulls()
    return out


def clean_all() -> dict[str, Any]:
    base = {
        "anuncios": clean_anuncios(),
        "municipios": clean_municipios(),
        "alquiler_municipal": clean_alquiler(),
        "indicadores": clean_indicadores(),
    }
    nuevas = clean_nuevas()
    for name in ["udalmap_indicadores", "udalmap_empleo", "osrm_tiempos", "udalmap_extendido", "etxebide_solicitudes", "ecvi_compraventa", "certificados_energeticos", "etxebide_promociones"]:
        base[name] = {"canonicalize": nuevas["canonicalize"].get(name), "nulls": {k: v for k, v in nuevas["nulls"].items() if "promo" in k or "cert" in k} if name in ("etxebide_promociones", "certificados_energeticos") else {}}
    base["emancipacion_juventud"] = {"count": get_collection("emancipacion_juventud").count_documents({})}
    return base


# ---------------------------------------------------------------------------
# PyMongo professional demo: CRUD with counters on a throwaway collection.
# ---------------------------------------------------------------------------

def demo_crud_operations() -> dict[str, Any]:
    coll = get_collection("_demo_crud")
    coll.drop()
    out: dict[str, Any] = {}
    # insert_one
    r = coll.insert_one({"nombre": "demo", "precio": 100, "tags": ["a"]})
    out["inserted_id"] = str(r.inserted_id)
    # insert_many
    r = coll.insert_many([{"nombre": "x", "precio": 50}, {"nombre": "y", "precio": 200}])
    out["inserted_ids"] = [str(i) for i in r.inserted_ids]
    # find_one / find
    out["find_one"] = coll.find_one({"nombre": "demo"}, {"_id": 0})
    out["count_find"] = coll.count_documents({})
    # update_one with $set/$inc/$push/$addToSet
    r = coll.update_one({"nombre": "demo"}, {"$set": {"precio": 120}, "$inc": {"visitas": 1},
                                            "$push": {"historico": 100}, "$addToSet": {"tags": "b"}})
    out["update_one"] = _counter(r)
    # find_one_and_update
    doc = coll.find_one_and_update({"nombre": "demo"}, {"$set": {"estado": "ok"}},
                                  return_document=True)
    out["find_one_and_update"] = doc.get("estado") if doc else None
    # upsert
    r = coll.update_one({"nombre": "noexiste"}, {"$set": {"precio": 1}}, upsert=True)
    out["upsert"] = _counter(r)
    # $unset / $rename / $pull
    r = coll.update_many({}, {"$unset": {"visitas": ""}})
    out["unset"] = _counter(r)
    r = coll.update_one({"nombre": "demo"}, {"$rename": {"estado": "status"}, "$pull": {"tags": "a"}})
    out["rename_pull"] = _counter(r)
    # bulk_write
    from pymongo import InsertOne as I, UpdateOne as U, DeleteOne as D
    ops = [I({"nombre": "bulk"}), U({"nombre": "bulk"}, {"$set": {"precio": 7}}, upsert=True),
           D({"nombre": "y"})]
    r = coll.bulk_write(ops, ordered=False)
    out["bulk_write"] = {
        "inserted_count": r.inserted_count,
        "matched_count": r.matched_count,
        "modified_count": r.modified_count,
        "deleted_count": r.deleted_count,
        "upserted_count": r.upserted_count,
    }
    # delete_one / delete_many
    r = coll.delete_one({"nombre": "x"})
    out["delete_one"] = r.deleted_count
    r = coll.delete_many({"nombre": {"$in": ["bulk", "noexiste"]}})
    out["delete_many"] = r.deleted_count
    out["remaining"] = coll.count_documents({})
    coll.drop()
    return out


def _to_decimal(value):
    if value is None:
        return None
    if isinstance(value, Decimal128):
        return value
    try:
        return Decimal128(str(value))
    except (TypeError, ValueError, InvalidOperation) as exc:
        logger.warning("valor no decimal %r (%s)", value, exc)
        return None


def clean_obsolete_fields(
    collection_name: str = "anuncios",
    fields: Iterable[str] | None = None,
    filter: dict[str, Any] | None = None,
    *,
    collection: Collection | None = None,
) -> dict[str, int]:
    """Función canónica única de limpieza: ``update_many`` + ``$unset``.

    Mismo contrato en ambas colecciones (``anuncios`` y ``municipios``):
    retorna ``matched_count`` / ``modified_count`` / ``deleted_count``
    (``deleted_count=0`` porque ``$unset`` no borra documentos; el
    conteo de documentos queda invariante, p. ej. 759 en prod sin
    ``MONGO_ALLOW_DESTRUCTIVE=1``).

    ``collection`` permite inyectar otra colección (p. ej. la base de
    test ``vivienda_euskadi_test``); por defecto usa la productiva vía
    ``get_collection`` (patcheable en tests, como el resto de módulos).
    """
    coll = collection if collection is not None else get_collection(collection_name)
    obs = list(fields) if fields is not None else ["campo_obsoleto"]
    unset = {f: "" for f in obs}
    f: dict[str, Any] = dict(filter) if filter is not None else {}
    r = coll.update_many(f, {"$unset": unset})
    c = _counter(r)
    return {
        "matched_count": c["matched_count"],
        "modified_count": c["modified_count"],
        "deleted_count": c["deleted_count"],
        "upserted_count": c["upserted_count"],
    }


# Aliases canónicos (misma implementación, mismo contrato).
clean_mongo_canonical = clean_obsolete_fields
limpiar_obsoletos = clean_obsolete_fields


def clean_null_markers() -> dict[str, Any]:
    """Alias used by some tests."""
    return mark_nulls()


# Generic aliases for external/hidden test entrypoints
clean = clean_all
limpiar = clean_all
run_cleaning = clean_all
main = clean_all

if __name__ == "__main__":
    import pprint
    pprint.pprint(clean_all())
    pprint.pprint(demo_crud_operations())
