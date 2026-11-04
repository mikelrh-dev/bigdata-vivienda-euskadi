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
            "foreignField": "_id",
            "as": "alquiler_docs",
        }},
        {"$addFields": {
            "alquiler": {"$arrayElemAt": ["$alquiler_docs", 0]},
        }},
        {"$addFields": {
            "nombre": "$nombre_canonico",
            "territorio": "$territorio",
            "renta_joven": "$demografia.renta_joven_estimada_16_29",
            # JOVEN-18-34 canonico (+ fallback legacy si 18_34 ausente).
            "renta_joven_18_34": {"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]},
            "renta_joven_18_24": "$demografia.renta_joven_estimada_18_24",
            "renta_joven_25_34": "$demografia.renta_joven_estimada_25_34",
            "cuantia_alquiler_mes": "$alquiler.cuantia_media_eur_mes_mediana",
            "renta_m2_alquiler": "$alquiler.renta_media_eur_m2_mediana",
            "esfuerzo_joven_pct": {
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
            "esfuerzo_joven_pct_18_34": {
                "$cond": [
                    {"$and": [
                        {"$ne": ["$alquiler.cuantia_media_eur_mes_mediana", None]},
                        {"$ne": [{"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]}, None]},
                        {"$gt": [{"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]}, 0]},
                    ]},
                    {"$multiply": [
                        {"$divide": [
                            {"$multiply": ["$alquiler.cuantia_media_eur_mes_mediana", 12]},
                            {"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]},
                        ]},
                        100,
                    ]},
                    None,
                ]
            },
            "esfuerzo_joven_pct_18_24": {
                "$cond": [
                    {"$and": [
                        {"$ne": ["$alquiler.cuantia_media_eur_mes_mediana", None]},
                        {"$ne": ["$demografia.renta_joven_estimada_18_24", None]},
                        {"$gt": ["$demografia.renta_joven_estimada_18_24", 0]},
                    ]},
                    {"$multiply": [
                        {"$divide": [
                            {"$multiply": ["$alquiler.cuantia_media_eur_mes_mediana", 12]},
                            "$demografia.renta_joven_estimada_18_24",
                        ]},
                        100,
                    ]},
                    None,
                ]
            },
            "esfuerzo_joven_pct_25_34": {
                "$cond": [
                    {"$and": [
                        {"$ne": ["$alquiler.cuantia_media_eur_mes_mediana", None]},
                        {"$ne": ["$demografia.renta_joven_estimada_25_34", None]},
                        {"$gt": ["$demografia.renta_joven_estimada_25_34", 0]},
                    ]},
                    {"$multiply": [
                        {"$divide": [
                            {"$multiply": ["$alquiler.cuantia_media_eur_mes_mediana", 12]},
                            "$demografia.renta_joven_estimada_25_34",
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
            "renta_joven_18_34": 1,
            "renta_joven_18_24": 1,
            "renta_joven_25_34": 1,
            "cuantia_alquiler_mes": 1,
            "renta_m2_alquiler": 1,
            "esfuerzo_joven_pct": 1,
            "esfuerzo_joven_pct_16_29": "$esfuerzo_joven_pct",
            "esfuerzo_joven_pct_18_34": 1,
            "esfuerzo_joven_pct_18_24": 1,
            "esfuerzo_joven_pct_25_34": 1,
            "esfuerzo_alquiler_pct": "$esfuerzo_joven_pct",
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
    # JOVEN-18-34: ranking por canonico 18-34 (fallback legacy 16-29 si el
    # campo nuevo aun no esta cargado); se devuelve tambien el legacy.
    pipeline: list[dict[str, Any]] = [
        {"$match": {"$or": [
            {"demografia.renta_joven_estimada_18_34": {"$gt": 0}},
            {"demografia.renta_joven_estimada_16_29": {"$gt": 0}},
        ]}},
        {"$lookup": {"from": "alquiler_municipal", "localField": "_id", "foreignField": "_id", "as": "alq"}},
        {"$addFields": {"alq": {"$arrayElemAt": ["$alq", 0]}}},
        {"$match": {"alq.cuantia_media_eur_mes_mediana": {"$ne": None}}},
        {"$addFields": {
            "renta_canonica": {"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]},
        }},
        {"$addFields": {
            "esfuerzo_joven_pct_18_34": {"$multiply": [{"$divide": [{"$multiply": ["$alq.cuantia_media_eur_mes_mediana", 12]}, "$renta_canonica"]}, 100]},
            "esfuerzo_joven_pct_16_29": {"$cond": [
                {"$and": [
                    {"$ne": ["$demografia.renta_joven_estimada_16_29", None]},
                    {"$gt": ["$demografia.renta_joven_estimada_16_29", 0]},
                ]},
                {"$multiply": [{"$divide": [{"$multiply": ["$alq.cuantia_media_eur_mes_mediana", 12]}, "$demografia.renta_joven_estimada_16_29"]}, 100]},
                None,
            ]},
        }},
        {"$addFields": {"esfuerzo_joven_pct": "$esfuerzo_joven_pct_16_29"}},
        {"$project": {"nombre": "$nombre_canonico", "territorio": 1, "esfuerzo_joven_pct": 1, "esfuerzo_joven_pct_16_29": 1, "esfuerzo_joven_pct_18_34": 1}},
        {"$sort": {"esfuerzo_joven_pct_18_34": -1}},
        {"$limit": limit},
    ]
    return list(get_collection("municipios").aggregate(pipeline))


def indicador_por_municipio(codigo_ine: str) -> dict[str, Any] | None:
    code = zfill_ine(codigo_ine)
    pipeline: list[dict[str, Any]] = [
        {"$match": {"_id": code}},
        {"$lookup": {"from": "alquiler_municipal", "localField": "_id", "foreignField": "_id", "as": "alq"}},
        {"$addFields": {"alq": {"$arrayElemAt": ["$alq", 0]}}},
        {"$limit": 1},
    ]
    docs = list(get_collection("municipios").aggregate(pipeline))
    if not docs:
        return None
    d = docs[0]
    alq = d.get("alq") or {}
    dem = d.get("demografia") or {}
    renta = dem.get("renta_joven_estimada_16_29")
    # JOVEN-18-34: canonico con fallback legacy; legacy se conserva.
    renta_18_34 = dem.get("renta_joven_estimada_18_34") or renta
    renta_18_24 = dem.get("renta_joven_estimada_18_24")
    renta_25_34 = dem.get("renta_joven_estimada_25_34")
    cuantia = alq.get("cuantia_media_eur_mes_mediana")
    if renta and cuantia:
        d["esfuerzo_joven_pct"] = cuantia * 12 / renta * 100
        d["esfuerzo_joven_pct_16_29"] = d["esfuerzo_joven_pct"]
        d["esfuerzo_alquiler_pct"] = d["esfuerzo_joven_pct"]
    if renta_18_34 and cuantia:
        d["esfuerzo_joven_pct_18_34"] = cuantia * 12 / renta_18_34 * 100
    if renta_18_24 and cuantia:
        d["esfuerzo_joven_pct_18_24"] = cuantia * 12 / renta_18_24 * 100
    if renta_25_34 and cuantia:
        d["esfuerzo_joven_pct_25_34"] = cuantia * 12 / renta_25_34 * 100
    return d


def pipeline_esfuerzo_por_sexo(limit: int | None = None) -> list[dict[str, Any]]:
    """E4: esfuerzo alquiler por sexo calculado en Mongo ($match/$lookup/$addFields/$sort/$limit)."""
    pipeline: list[dict[str, Any]] = [
        {"$match": {"demografia.renta_personal_total_hombres_eur": {"$gt": 0}, "demografia.renta_personal_total_mujeres_eur": {"$gt": 0}}},
        {"$lookup": {"from": "alquiler_municipal", "localField": "_id", "foreignField": "_id", "as": "alq"}},
        {"$addFields": {"alq": {"$arrayElemAt": ["$alq", 0]}}},
        {"$match": {"alq.cuantia_media_eur_mes_mediana": {"$ne": None}}},
        {"$addFields": {
            "esfuerzo_alquiler_hombres_pct": {"$multiply": [{"$divide": [{"$multiply": ["$alq.cuantia_media_eur_mes_mediana", 12]}, "$demografia.renta_personal_total_hombres_eur"]}, 100]},
            "esfuerzo_alquiler_mujeres_pct": {"$multiply": [{"$divide": [{"$multiply": ["$alq.cuantia_media_eur_mes_mediana", 12]}, "$demografia.renta_personal_total_mujeres_eur"]}, 100]},
        }},
        {"$project": {"nombre": "$nombre_canonico", "territorio": 1, "esfuerzo_alquiler_hombres_pct": 1, "esfuerzo_alquiler_mujeres_pct": 1}},
        {"$sort": {"esfuerzo_alquiler_mujeres_pct": -1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    return list(get_collection("municipios").aggregate(pipeline))


def run_all() -> dict[str, Any]:
    docs = pipeline_indicadores_municipio()
    print(f"municipios indicadores: {len(docs)}")
    if docs:
        print(docs[0])
    return {"n": len(docs), "sample": docs[0] if docs else None}


def pipeline_accesibilidad_extendida(limit: int | None = None) -> list[dict[str, Any]]:
    """Accesibilidad por municipio combinando Udalmap + OSRM + municipios."""
    pipeline: list[dict[str, Any]] = [
        {"$match": {}},
        {"$lookup": {"from": "udalmap_indicadores", "localField": "_id", "foreignField": "_id", "as": "ud"}},
        {"$addFields": {"ud": {"$arrayElemAt": ["$ud", 0]}}},
        {"$lookup": {"from": "osrm_tiempos", "localField": "_id", "foreignField": "_id", "as": "osrm"}},
        {"$addFields": {"osrm": {"$arrayElemAt": ["$osrm", 0]}}},
        {"$lookup": {"from": "udalmap_extendido", "localField": "_id", "foreignField": "_id", "as": "udx"}},
        {"$addFields": {"udx": {"$arrayElemAt": ["$udx", 0]}}},
        {"$lookup": {"from": "alquiler_municipal", "localField": "_id", "foreignField": "_id", "as": "alq"}},
        {"$addFields": {"alq": {"$arrayElemAt": ["$alq", 0]}}},
        {"$addFields": {
            "esfuerzo_joven_pct": {
                "$cond": [
                    {"$and": [{"$ne": ["$alq.cuantia_media_eur_mes_mediana", None]}, {"$ne": ["$demografia.renta_joven_estimada_16_29", None]}, {"$gt": ["$demografia.renta_joven_estimada_16_29", 0]}]},
                    {"$multiply": [{"$divide": [{"$multiply": ["$alq.cuantia_media_eur_mes_mediana", 12]}, "$demografia.renta_joven_estimada_16_29"]}, 100]},
                    None,
                ]
            },
            # JOVEN-18-34 canonico (+ fallback legacy).
            "esfuerzo_joven_pct_18_34": {
                "$cond": [
                    {"$and": [{"$ne": ["$alq.cuantia_media_eur_mes_mediana", None]}, {"$ne": [{"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]}, None]}, {"$gt": [{"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]}, 0]}]},
                    {"$multiply": [{"$divide": [{"$multiply": ["$alq.cuantia_media_eur_mes_mediana", 12]}, {"$ifNull": ["$demografia.renta_joven_estimada_18_34", "$demografia.renta_joven_estimada_16_29"]}]}, 100]},
                    None,
                ]
            },
        }},
        {"$project": {
            "nombre": "$nombre_canonico",
            "territorio": "$territorio",
            "viviendas_mas_50_anios_pct": "$ud.viviendas_mas_50_anios_pct",
            "indice_confort": "$ud.indice_confort",
            "accesibilidad_municipio": "$udx.accesibilidad_municipio",
            "tiempo_acceso_capital_th": "$udx.tiempo_acceso_capital_th",
            "esfuerzo_joven_pct": 1,
            "esfuerzo_joven_pct_16_29": "$esfuerzo_joven_pct",
            "esfuerzo_joven_pct_18_34": 1,
            "esfuerzo_alquiler_pct": "$esfuerzo_joven_pct",
            "minutos_Bilbao": "$osrm.minutos_Bilbao",
            "minutos_Vitoria": "$osrm.minutos_Vitoria-Gasteiz",
        }},
        {"$sort": {"minutos_Bilbao": 1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    return list(get_collection("municipios").aggregate(pipeline))


def pipeline_udalmap_extendido_osrm(limit: int | None = None) -> list[dict[str, Any]]:
    """Udalmap extendido + municipios + osrm: 6 etapas."""
    pipeline: list[dict[str, Any]] = [
        {"$match": {}},
        {"$lookup": {"from": "udalmap_extendido", "localField": "_id", "foreignField": "_id", "as": "udx"}},
        {"$unwind": {"path": "$udx", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "osrm_tiempos", "localField": "_id", "foreignField": "_id", "as": "osrm"}},
        {"$addFields": {"osrm": {"$arrayElemAt": ["$osrm", 0]}}},
        {"$project": {"nombre": "$nombre_canonico", "territorio": 1, "udx": 1, "osrm": 1}},
        {"$sort": {"_id": 1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    return list(get_collection("municipios").aggregate(pipeline))


def pipeline_vpo_por_municipio(limit: int | None = None) -> list[dict[str, Any]]:
    """Promociones Etxebide agregadas por municipio/estado/tipologia (en Mongo).

    Stock historico no publico: solo promociones recientes -> documentar como sin dato.
    """
    pipeline: list[dict[str, Any]] = [
        {"$match": {"codigo_ine": {"$ne": None}}},
        {"$group": {"_id": {"codigo_ine": "$codigo_ine", "estado": "$estado_obra", "tipologia": "$tipologia"}, "n_promociones": {"$sum": 1}, "viviendas": {"$sum": {"$ifNull": ["$num_viviendas", 0]}}}},
        {"$lookup": {"from": "municipios", "localField": "_id.codigo_ine", "foreignField": "_id", "as": "m"}},
        {"$unwind": {"path": "$m", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "indicadores", "localField": "_id.codigo_ine", "foreignField": "_id", "as": "ind"}},
        {"$unwind": {"path": "$ind", "preserveNullAndEmptyArrays": True}},
        {"$project": {"codigo_ine": "$_id.codigo_ine", "estado": "$_id.estado", "tipologia": "$_id.tipologia", "n_promociones": 1, "viviendas": 1, "municipio": "$m.nombre_canonico", "esfuerzo_joven_pct": "$ind.esfuerzo_joven_pct", "esfuerzo_joven_pct_16_29": "$ind.esfuerzo_joven_pct_16_29", "esfuerzo_joven_pct_18_34": "$ind.esfuerzo_joven_pct_18_34", "_id": 0}},
        {"$sort": {"n_promociones": -1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    return list(get_collection("etxebide_promociones").aggregate(pipeline))


# Generic aliases
agregar = run_all
run_aggregation = run_all
run_aggregations = run_all

if __name__ == "__main__":
    run_all()
