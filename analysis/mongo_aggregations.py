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

    Bloque 4 (PLAN_10 16): pipeline verdadero — expone tambien paro Lanbide
    (`empleo.tasa_paro_lanbide_pct`) y tension social (`demanda_social.*`)
    desde el documento `municipios` en Mongo (fuente auditada solo lectura:
    colecciones `empleo`/`demanda_social` en `municipios`, `etxebide_solicitudes`
    5040 docs, `alquiler_municipal.metodo_imputacion` 159 oficial / 93 IDW).
    Preserva `metodo_imputacion` y deriva `is_imputed` sin rellenar valores
    en silencio (la imputacion queda explicita, nunca oculta).

    M1 (AGREGACION-01): solo entran anuncios con `precio_m2` valido en
    [3, 50], `superficie_m2` en [10, 500] y `habitaciones` entero (garantizado
    aguas arriba en OUTLIER-01). `precio_medio_eur` excluye ademas los
    valores fuera del IQR (Q3+1,5·IQR y Q1−1,5·IQR por municipio) y
    `mediana_precio_m2_winsorizada` aplica winsorizacion al percentil 1–99
    antes de la mediana (recorte, no imputacion). La mediana cruda no se
    usa para conclusiones.
    """

    def _winsorizado() -> tuple[dict[str, Any], dict[str, Any]]:
        """Expresiones 1-99: recorta extremos (no imputa) y toma la mediana."""
        pm2 = "$_pm2_ordenados"
        n = "$_n_pm2"
        p1_idx = {"$floor": {"$multiply": [n, 0.01]}}
        p99_idx = {"$min": [{"$floor": {"$multiply": [n, 0.99]}}, {"$subtract": [n, 1]}]}
        p1 = {"$arrayElemAt": [pm2, p1_idx]}
        p99 = {"$arrayElemAt": [pm2, p99_idx]}
        wins = {"$map": {"input": pm2, "as": "v",
                         "in": {"$max": [{"$min": ["$$v", p99]}, p1]}}}
        return wins, {"$arrayElemAt": [wins, {"$floor": {"$divide": [n, 2]}}]}

    _wins, _mediana_wins = _winsorizado()
    # Puerta M1: precio_m2 ya validado en carga (3-50 / sup 10-500), mas
    # superficie en [10, 500] y habitaciones entero en el propio pipeline.
    _filtro_valido = {"$and": [
        {"$ne": ["$$a.precio_m2", None]},
        {"$gte": ["$$a.superficie_m2", 10]},
        {"$lte": ["$$a.superficie_m2", 500]},
        {"$ne": ["$$a.habitaciones", None]},
        {"$eq": ["$$a.habitaciones", {"$trunc": "$$a.habitaciones"}]},
    ]}
    pipeline: list[dict[str, Any]] = [
        {"$match": {}},
        {"$lookup": {
            "from": "anuncios",
            "localField": "_id",
            "foreignField": "ubicacion.codigo_ine",
            "as": "anuncios",
        }},
        {"$addFields": {
            "anuncios_filtrados": {"$filter": {"input": "$anuncios", "as": "a", "cond": _filtro_valido}},
        }},
        {"$addFields": {
            "_n_pm2": {"$size": "$anuncios_filtrados"},
            "_pm2_ordenados": {"$sortArray": {"input": {"$map": {
                "input": "$anuncios_filtrados", "as": "a", "in": "$$a.precio_m2"}}, "sortBy": 1}},
        }},
        {"$addFields": {
            "_q1_pm2": {"$arrayElemAt": ["$_pm2_ordenados", {"$floor": {"$multiply": ["$_n_pm2", 0.25]}}]},
            "_q3_pm2": {"$arrayElemAt": ["$_pm2_ordenados", {"$floor": {"$multiply": ["$_n_pm2", 0.75]}}]},
        }},
        {"$addFields": {
            "_iqr_pm2": {"$subtract": ["$_q3_pm2", "$_q1_pm2"]},
        }},
        {"$addFields": {
            "_iqr_lo": {"$cond": [{"$gt": ["$_iqr_pm2", 0]},
                                 {"$subtract": ["$_q1_pm2", {"$multiply": [1.5, "$_iqr_pm2"]}]},
                                 {"$multiply": [-1, 1e18]}]},
            "_iqr_hi": {"$cond": [{"$gt": ["$_iqr_pm2", 0]},
                                 {"$add": ["$_q3_pm2", {"$multiply": [1.5, "$_iqr_pm2"]}]},
                                 {"$multiply": [1e18, 1]}]},
        }},
        {"$addFields": {
            "anuncios_iqr": {"$filter": {"input": "$anuncios_filtrados", "as": "a",
                                         "cond": {"$and": [
                                             {"$gte": ["$$a.precio_m2", "$_iqr_lo"]},
                                             {"$lte": ["$$a.precio_m2", "$_iqr_hi"]}]}}},
        }},
        {"$addFields": {
            "n_anuncios": {"$size": "$anuncios"},
            "n_anuncios_filtrados": {"$size": "$anuncios_filtrados"},
            # M1 AGREGACION-01: precio medio SIN outliers IQR.
            "precio_medio_eur": {"$avg": "$anuncios_iqr.precio_eur"},
            "superficie_media_m2": {"$avg": "$anuncios_filtrados.superficie_m2"},
            # M1 AGREGACION-01: mediana winsorizada p1-99 (null si n=0).
            "mediana_precio_m2_winsorizada": {"$cond": [{"$gt": ["$_n_pm2", 0]},
                                                        _mediana_wins, None]},
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
        # TIER-01 (AGREGACION-01): n_precio con precio_eur no nulo, solo
        # Tier A/B (C/D sin precio municipal); estado rankeable solo n>=30
        # (4 Tier A), el resto n_insuficiente sin ordenacion.
        {"$addFields": {
            "tier": _tier_expr("$n_anuncios"),
            "_n_precio_raw": {"$sum": {"$map": {"input": "$anuncios", "as": "a",
                "in": {"$cond": [{"$ne": ["$$a.precio_eur", None]}, 1, 0]}}}},
        }},
        {"$addFields": {
            "n_precio": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_n_precio_raw", 0]},
            "estado": {"$cond": [{"$gte": ["$n_anuncios", 30]},
                                 "rankeable", "n_insuficiente"]},
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
            # Paro Lanbide y tension social desde municipios (Mongo verdadero).
            "tasa_paro_lanbide_pct": "$empleo.tasa_paro_lanbide_pct",
            "tension_demanda_social": "$demanda_social.tension_demanda_social",
            "tension_categoria": "$demanda_social.tension_categoria",
            "etxebide_solicitudes_por_mil": "$demanda_social.etxebide_solicitudes_por_mil_2024",
            # Imputacion explicita: oficial -> False; IDW -> True; sin doc -> False.
            "metodo_imputacion": "$alquiler.metodo_imputacion",
            "is_imputed": {
                "$cond": [
                    {"$eq": ["$alquiler.metodo_imputacion", "oficial"]},
                    False,
                    {"$ne": ["$alquiler.metodo_imputacion", None]},
                ]
            },
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
            "n_anuncios_filtrados": 1,
            "n_precio": 1,
            "tier": 1,
            "estado": 1,
            "precio_medio_eur": 1,
            "superficie_media_m2": 1,
            "mediana_precio_m2_winsorizada": 1,
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
            "tasa_paro_lanbide_pct": 1,
            "tension_demanda_social": 1,
            "tension_categoria": 1,
            "etxebide_solicitudes_por_mil": 1,
            "metodo_imputacion": 1,
            "is_imputed": 1,
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
    # M3 (CONCLUSION-01): ningun ranking con n_anuncios<30; los municipios
    # con n<30 quedan como «n insuficiente» y nunca ordenan por encima de
    # un Tier A (p. ej. Barakaldo n=6 no ranking vs Donostia n=126).
    pipeline: list[dict[str, Any]] = [
        {"$match": {"$or": [
            {"demografia.renta_joven_estimada_18_34": {"$gt": 0}},
            {"demografia.renta_joven_estimada_16_29": {"$gt": 0}},
        ]}},
        {"$lookup": {"from": "anuncios", "localField": "_id",
                     "foreignField": "ubicacion.codigo_ine", "as": "ann"}},
        {"$addFields": {"n_anuncios": {"$size": "$ann"}}},
        {"$match": {"n_anuncios": {"$gte": 30}}},
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
        {"$project": {"nombre": "$nombre_canonico", "territorio": 1, "n_anuncios": 1, "esfuerzo_joven_pct": 1, "esfuerzo_joven_pct_16_29": 1, "esfuerzo_joven_pct_18_34": 1}},
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
        {"$group": {"_id": {"codigo_ine": "$codigo_ine", "estado": "$estado_obra", "tipologia": "$tipologia"}, "n_promociones": {"$sum": 1}, "viviendas": {"$sum": {"$ifNull": ["$num_viviendas", 0]}}, "promociones_con_viviendas": {"$sum": {"$cond": [{"$ne": ["$num_viviendas", None]}, 1, 0]}}}},
        {"$lookup": {"from": "municipios", "localField": "_id.codigo_ine", "foreignField": "_id", "as": "m"}},
        {"$unwind": {"path": "$m", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "indicadores", "localField": "_id.codigo_ine", "foreignField": "_id", "as": "ind"}},
        {"$unwind": {"path": "$ind", "preserveNullAndEmptyArrays": True}},
        {"$project": {"codigo_ine": "$_id.codigo_ine", "estado": "$_id.estado", "tipologia": "$_id.tipologia", "n_promociones": 1, "viviendas": {"$cond": [{"$gt": ["$promociones_con_viviendas", 0]}, "$viviendas", None]}, "municipio": "$m.nombre_canonico", "esfuerzo_joven_pct": "$ind.esfuerzo_joven_pct", "esfuerzo_joven_pct_16_29": "$ind.esfuerzo_joven_pct_16_29", "esfuerzo_joven_pct_18_34": "$ind.esfuerzo_joven_pct_18_34", "_id": 0}},
        {"$sort": {"n_promociones": -1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    return list(get_collection("etxebide_promociones").aggregate(pipeline))


def pipeline_vpo_terminadas(limit: int | None = None) -> list[dict[str, Any]]:
    """VPO terminada en el ultimo quinquenio (Udalmap 73), flujo por mil.

    No es stock: es el flujo 2020-2024 por mil habitantes. `$match` descarta
    el unico municipio sin dato (Usansolo, 48916) y `$lookup` aporta nombre y
    territorio desde `municipios`. Devuelve 251 filas.
    """
    pipeline: list[dict[str, Any]] = [
        {"$match": {"vpo_terminadas_por_mil": {"$ne": None}}},
        {"$lookup": {"from": "municipios", "localField": "_id", "foreignField": "_id", "as": "m"}},
        {"$unwind": {"path": "$m", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "codigo_ine": "$_id",
            "municipio": {"$ifNull": ["$m.nombre_canonico", "$municipio"]},
            "territorio": "$m.territorio",
            "vpo_terminadas_por_mil": 1,
            "anio_fuente": 1,
            "_id": 0,
        }},
        {"$sort": {"vpo_terminadas_por_mil": -1, "codigo_ine": 1}},
    ]
    if limit:
        pipeline.append({"$limit": limit})
    return list(get_collection("vpo_municipal").aggregate(pipeline))


# Generic aliases
agregar = run_all
run_aggregation = run_all
run_aggregations = run_all

TIER_ETIQUETAS = {
    "A": "fuerte",
    "B": "indicativo",
    "C": "sin precio municipal",
    "D": "sin dato (+ contexto oficial)",
}


def _tier_expr(n: str = "$n_anuncios") -> dict[str, Any]:
    return {"$switch": {
        "branches": [
            {"case": {"$gte": [n, 30]}, "then": "A"},
            {"case": {"$gte": [n, 10]}, "then": "B"},
            {"case": {"$gte": [n, 1]}, "then": "C"},
        ],
        "default": "D",
    }}


def pipeline_tier_por_municipio(limit: int | None = None) -> list[dict[str, Any]]:
    """Tier A/B/C/D por municipio desde Mongo ($group-equivalente por codigo_ine).

    Base `municipios` (252) + `$lookup` a `anuncios` por `ubicacion.codigo_ine`;
    para cada municipio calcula `n_anuncios`, `n_precio`, `min_precio`,
    `max_precio`, `mediana_precio`, `n_precio_temporal`, `n_precio_larga`,
    `mediana_precio_temporal`, `mediana_precio_larga` (canonico; quedan
    tambien los alias legacy `mediana_temporal`/`mediana_larga`),
    `min_precio_temporal`, `max_precio_temporal`, `min_precio_larga`,
    `max_precio_larga` y deriva `tier` solo de `n_anuncios`
    (A >=30, B 10-29, C 1-9, D 0). Tier C/D: `n_precio`=0, min/max/mediana
    nulos, sin precio municipal y sin imputacion comarcal/IDW. Devuelve 252 filas.
    """
    def _mediana(cond: dict[str, Any]) -> dict[str, Any]:
        filtrados = {"$filter": {"input": "$anuncios", "as": "a", "cond": cond}}
        precios = {"$map": {"input": filtrados, "as": "x", "in": "$$x.precio_eur"}}
        ordenados = {"$sortArray": {"input": precios, "sortBy": 1}}
        return {"$arrayElemAt": [ordenados,
                                 {"$floor": {"$divide": [{"$size": precios}, 2]}}]}

    def _minmax(cond: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        filtrados = {"$filter": {"input": "$anuncios", "as": "a", "cond": cond}}
        precios = {"$map": {"input": filtrados, "as": "x", "in": "$$x.precio_eur"}}
        return {"$min": precios}, {"$max": precios}

    _cond_temporal = {"$and": [
        {"$eq": ["$$a.modalidad", "temporal"]},
        {"$ne": ["$$a.precio_eur", None]}]}
    _cond_larga = {"$and": [
        {"$eq": ["$$a.modalidad", "larga_estancia"]},
        {"$ne": ["$$a.precio_eur", None]}]}
    _min_t, _max_t = _minmax(_cond_temporal)
    _min_l, _max_l = _minmax(_cond_larga)

    pipeline: list[dict[str, Any]] = [
        {"$match": {}},
        {"$lookup": {"from": "anuncios", "localField": "_id",
                     "foreignField": "ubicacion.codigo_ine", "as": "anuncios"}},
        {"$addFields": {
            "n_anuncios": {"$size": "$anuncios"},
            "_n_precio": {"$sum": {"$map": {"input": "$anuncios", "as": "a",
                                           "in": {"$cond": [
                                               {"$ne": ["$$a.precio_eur", None]}, 1, 0]}}}},
            "_min_precio": {"$min": "$anuncios.precio_eur"},
            "_max_precio": {"$max": "$anuncios.precio_eur"},
            "_n_precio_temporal": {"$sum": {"$map": {"input": "$anuncios", "as": "a",
                                                   "in": {"$cond": [
                                                       {"$and": [
                                                           {"$eq": ["$$a.modalidad", "temporal"]},
                                                           {"$ne": ["$$a.precio_eur", None]}]}, 1, 0]}}}},
            "_n_precio_larga": {"$sum": {"$map": {"input": "$anuncios", "as": "a",
                                                "in": {"$cond": [
                                                    {"$and": [
                                                        {"$eq": ["$$a.modalidad", "larga_estancia"]},
                                                        {"$ne": ["$$a.precio_eur", None]}]}, 1, 0]}}}},
            "_mediana_precio": _mediana({"$ne": ["$$a.precio_eur", None]}),
            "_mediana_temporal": _mediana(_cond_temporal),
            "_mediana_larga": _mediana(_cond_larga),
            "_min_precio_temporal": _min_t,
            "_max_precio_temporal": _max_t,
            "_min_precio_larga": _min_l,
            "_max_precio_larga": _max_l,
        }},
        {"$addFields": {"tier": _tier_expr()}},
        # Tier C/D sin precio municipal: n_precio=0, min/max/mediana nulos
        # (spec AGREGACION-01 edge), aunque el anuncio tenga precio.
        # Solo Tier A/B conservan estadisticas de precio (B indicativo).
        {"$addFields": {
            "n_precio": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_n_precio", 0]},
            "n_precio_temporal": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_n_precio_temporal", 0]},
            "n_precio_larga": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_n_precio_larga", 0]},
            "min_precio": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_min_precio", None]},
            "max_precio": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_max_precio", None]},
            "mediana_precio": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_mediana_precio", None]},
            "mediana_temporal": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_mediana_temporal", None]},
            "mediana_larga": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_mediana_larga", None]},
            # Nombres canonicos (spec) + rango por modalidad (Tier B indicativo).
            "mediana_precio_temporal": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_mediana_temporal", None]},
            "mediana_precio_larga": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_mediana_larga", None]},
            "min_precio_temporal": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_min_precio_temporal", None]},
            "max_precio_temporal": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_max_precio_temporal", None]},
            "min_precio_larga": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_min_precio_larga", None]},
            "max_precio_larga": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_max_precio_larga", None]},
        }},
        {"$addFields": {"tier_etiqueta": {"$switch": {
            "branches": [
                {"case": {"$eq": ["$tier", "A"]}, "then": TIER_ETIQUETAS["A"]},
                {"case": {"$eq": ["$tier", "B"]}, "then": TIER_ETIQUETAS["B"]},
                {"case": {"$eq": ["$tier", "C"]}, "then": TIER_ETIQUETAS["C"]},
            ],
            "default": TIER_ETIQUETAS["D"]}}}},
        {"$project": {
            "codigo_ine": "$_id", "nombre": "$nombre_canonico", "territorio": 1,
            "n_anuncios": 1, "n_precio": 1, "min_precio": 1, "max_precio": 1,
            "mediana_precio": 1, "n_precio_temporal": 1, "n_precio_larga": 1,
            "mediana_temporal": 1, "mediana_larga": 1,
            "mediana_precio_temporal": 1, "mediana_precio_larga": 1,
            "min_precio_temporal": 1, "max_precio_temporal": 1,
            "min_precio_larga": 1, "max_precio_larga": 1, "tier": 1,
            "tier_etiqueta": 1, "_id": 0}},
        {"$sort": {"n_anuncios": -1, "codigo_ine": 1}},
    ]
    if limit is not None:
        pipeline.append({"$limit": limit})
    return list(get_collection("municipios").aggregate(pipeline))


def _hab_col():
    """Colección de habitaciones: bigdata si tiene docs, si no unificados."""
    try:
        big = get_collection("anuncios_habitaciones_unificados_bigdata")
        if big.estimated_document_count() > 0:
            return big
    except Exception:
        pass
    return get_collection("anuncios_habitaciones_unificados")


def pipeline_habitaciones_por_municipio(limit: int | None = None) -> list[dict[str, Any]]:
    """Mediana municipal de habitaciones desde anuncios de habitaciones.

    `$group` por `codigo_ine` normalizado (no por texto de municipio) sobre
    `anuncios_habitaciones_unificados` (201 anuncios; Bilbao 96, Donostia
    66, Vitoria 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 2,
    Eibar 1). Cada fila expone `codigo_ine`, `municipio`, `n`, `n_precio`,
    `min_precio_eur`, `max_precio_eur`, `mediana_precio_eur` (mediana cruda,
    sin winsorizar ni imputar comarcal/IDW). Solo Bilbao y Donostia
    (n_precio >= 30) sostienen comparación firme; el resto es indicativo
    (n_insuficiente, sin ranking).
    """
    pipeline: list[dict[str, Any]] = [
        {"$match": {"codigo_ine": {"$ne": None}}},
        {"$group": {
            "_id": "$codigo_ine",
            "municipio": {"$first": "$municipio"},
            "n": {"$sum": 1},
            "n_precio": {"$sum": {"$cond": [{"$ne": ["$precio_eur", None]}, 1, 0]}},
            "precios": {"$push": {"$cond": [{"$ne": ["$precio_eur", None]}, "$precio_eur", "$$REMOVE"]}},
        }},
        {"$addFields": {
            "_ordenados": {"$sortArray": {"input": "$precios", "sortBy": 1}},
            "_n_precio_arr": {"$size": "$precios"},
        }},
        {"$addFields": {
            "min_precio_eur": {"$cond": [{"$gt": ["$_n_precio_arr", 0]}, {"$arrayElemAt": ["$_ordenados", 0]}, None]},
            "max_precio_eur": {"$cond": [{"$gt": ["$_n_precio_arr", 0]}, {"$arrayElemAt": ["$_ordenados", -1]}, None]},
            "mediana_precio_eur": {"$cond": [
                {"$gt": ["$_n_precio_arr", 0]},
                {"$arrayElemAt": ["$_ordenados", {"$floor": {"$divide": ["$_n_precio_arr", 2]}}]},
                None,
            ]},
        }},
        {"$project": {
            "codigo_ine": "$_id",
            "municipio": 1,
            "n": 1,
            "n_precio": 1,
            "min_precio_eur": 1,
            "max_precio_eur": 1,
            "mediana_precio_eur": 1,
            "_id": 0,
        }},
        {"$sort": {"n_precio": -1, "codigo_ine": 1}},
    ]
    if limit is not None:
        pipeline.append({"$limit": limit})
    return list(_hab_col().aggregate(pipeline))

if __name__ == "__main__":
    run_all()
