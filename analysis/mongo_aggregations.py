"""Aggregation pipelines for vivienda_euskadi."""

from __future__ import annotations

from typing import Any

from bson.decimal128 import Decimal128

from storage.mongo import get_collection, zfill_ine


def _money(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal128):
        return value
    try:
        return Decimal128(str(value))
    except Exception:
        return value


def pipeline_indicadores_municipio(limit: int | None = None) -> list[dict[str, Any]]:
    """Indicators per municipality combining anuncios + municipios + alquiler.

    Stages: $match, $lookup, $addFields, $lookup, $addFields, $project, $sort
    (optionally $limit).
    """
    pipeline: list[dict[str, Any]] = [
        {"$match": {}},
        {"$lookup": {
            "from": "anuncios",
            "localField": "_id",
            "foreignField": "ubicacion.codigo_ine",
            "as": "anuncios",
        }},
        {"$addFields": {
            "n_anuncios": {"$size": "$anuncios"},
            "precio_medio_eur": {"$avg": "$anuncios.precio_eur"},
            "superficie_media_m2": {"$avg": "$anuncios.superficie_m2"},
            "n_larga_estancia": {
                "$sum": {"$map": {
                    "input": "$anuncios",
                    "as": "a",
                    "in": {"$cond": [{"$eq": ["$$a.modalidad", "larga_estancia"]}, 1, 0]},
                }}
            },
            "n_temporal": {
                "$sum": {"$map": {
                    "input": "$anuncios",
                    "as": "a",
                    "in": {"$cond": [{"$eq": ["$$a.modalidad", "temporal"]}, 1, 0]},
                }}
            },
        }},
        {"$lookup": {
            "from": "alquiler_municipal",
            "localField": "_id",
            "foreignField": "codigo_ine",
            "as": "alquiler_docs",
        }},
        {"$addFields": {
            "alquiler": {"$arrayElemAt": ["$alquiler_docs", 0]},
        }},
        {"$addFields": {
            "nombre": "$nombre_canonico",
            "territorio": "$territorio",
            "renta_joven": "$demografia.renta_joven_estimada_16_29",
            "cuantia_alquiler_mes": "$alquiler.cuantia_media_eur_mes_mediana",
            "renta_m2_alquiler": "$alquiler.renta_media_eur_m2_mediana",
            "esfuerzo_alquiler_pct": {
                "$cond": [
                    {"$and": [
                        {"$ne": ["$alquiler.cuantia_media_eur_mes_mediana", None]},
                        {"$ne": ["$demografia.renta_joven_estimada_16_29", None]},
                        {"$gt": ["$demografia.renta_joven_estimada_16_29", 0]},
                    ]},
                    {"$multiply": [
                        {"$divide": [
                            {"$multiply": ["$alquiler.cuantia_media_eur_mes_mediana", 12]},
                            "$demografia.renta_joven_estimada_16_29",
                        ]},
                        100,
                    ]},
                    None,
                ]
            },
        }},
        {"$project": {
            "_id": 1,
            "nombre": 1,
            "territorio": 1,
            "n_anuncios": 1,
            "precio_medio_eur": 1,
            "superficie_media_m2": 1,
            "n_larga_estancia": 1,
            "n_temporal": 1,
            "renta_joven": 1,
            "cuantia_alquiler_mes": 1,
            "renta_m2_alquiler": 1,
            "esfuerzo_alquiler_pct": 1,
            "tiene_alquiler_oficial": 1,
        }},
        {"$sort": {"n_anuncios": -1, "_id": 1}},
    ]
    if limit is not None:
        pipeline.append({"$limit": limit})
    return list(get_collection("municipios").aggregate(pipeline))


def pipeline_alquiler_por_municipio(limit: int | None = None) -> list[dict[str, Any]]:
    pipeline: list[dict[str, Any]] = [
        {"$match": {"codigo_ine": {"$ne": None}}},
        {"$group": {
            "_id": "$codigo_ine",
            "n_registros": {"$sum": 1},
            "cuantia_media": {"$avg": "$cuantia_media_eur_mes_media"},
            "renta_m2_media": {"$avg": "$renta_media_eur_m2_media"},
            "superficie_media": {"$avg": "$superficie_media_m2_media"},
        }},
        {"$lookup": {"from": "municipios", "localField": "_id", "foreignField": "_id", "as": "m"}},
        {"$unwind": "$m"},
        {"$project": {
            "_id": 1,
            "nombre": "$m.nombre_canonico",
            "territorio": "$m.territorio",
            "n_registros": 1,
            "cuantia_media": 1,
            "renta_m2_media": 1,
            "superficie_media": 1,
        }},
        {"$sort": {"cuantia_media": -1}},
    ]
    if limit is not None:
        pipeline.append({"$limit": limit})
    return list(get_collection("alquiler_municipal").aggregate(pipeline))


def pipeline_modalidades() -> list[dict[str, Any]]:
    return list(get_collection("anuncios").aggregate([
        {"$match": {}},
        {"$group": {"_id": "$modalidad", "n": {"$sum": 1}, "precio_medio": {"$avg": "$precio_eur"}}},
        {"$sort": {"n": -1}},
        {"$project": {"modalidad": "$_id", "n": 1, "precio_medio": 1, "_id": 0}},
    ]))


def pipeline_top_municipios_por_esfuerzo(limit: int = 10) -> list[dict[str, Any]]:
    docs = pipeline_indicadores_municipio()
    docs = [d for d in docs if d.get("esfuerzo_alquiler_pct") is not None]
    docs.sort(key=lambda d: d.get("esfuerzo_alquiler_pct", 0), reverse=True)
    return docs[:limit]


def indicador_por_municipio(codigo_ine: str) -> dict[str, Any] | None:
    code = zfill_ine(codigo_ine)
    for d in pipeline_indicadores_municipio():
        if d.get("_id") == code:
            return d
    return None


def run_all() -> dict[str, Any]:
    docs = pipeline_indicadores_municipio()
    print(f"municipios indicadores: {len(docs)}")
    if docs:
        print(docs[0])
    return {"n": len(docs), "sample": docs[0] if docs else None}


# Generic aliases
agregar = run_all
run_aggregation = run_all
run_aggregations = run_all

if __name__ == "__main__":
    run_all()
