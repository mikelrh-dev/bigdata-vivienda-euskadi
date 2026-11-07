"""Load silver data into MongoDB (idempotent)."""

from __future__ import annotations

import json
import logging
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from bson.decimal128 import Decimal128
try:
    from decimal import InvalidOperation
except ImportError:  # pragma: no cover
    InvalidOperation = ValueError  # type: ignore[assignment]

from storage.mongo import (
    get_collection,
    replace_collection,
    to_bool,
    to_float,
    to_int,
    to_str,
    zfill_ine,
)

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "procesado"

logger = logging.getLogger(__name__)


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROC / name, encoding="utf-8-sig", dtype=str)


def _money(value):
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    try:
        return Decimal128(text)
    except (TypeError, ValueError, InvalidOperation) as exc:
        logger.warning("precio no numérico %r (%s)", value, exc)
        return None


def _lookup_csv(name: str, key: str = "codigo_ine") -> dict[str, dict]:
    """Lookup {codigo_z5: row} de un silver procesado; {} si no existe."""
    path = PROC / name
    if not path.exists():
        return {}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        logger.warning("no se pudo leer %s: %s", path.name, exc)
        return {}
    out: dict[str, dict] = {}
    for _, r in df.iterrows():
        c = zfill_ine(r.get(key))
        if c:
            out[c] = r
    return out


def _geo_point(lat_raw, lon_raw) -> dict | None:
    lat = to_float(lat_raw)
    lon = to_float(lon_raw)
    if lat is None or lon is None:
        return None
    if not (math.isfinite(lat) and math.isfinite(lon)):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return {"type": "Point", "coordinates": [lon, lat]}


def _lookup_fotocasa_geo() -> dict[str, dict | None]:
    path = PROC / "anuncios_fotocasa_enriquecido.csv"
    if not path.exists():
        return {}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        logger.warning("no se pudo leer %s: %s", path.name, exc)
        return {}
    out: dict[str, dict | None] = {}
    for _, r in df.iterrows():
        key = to_str(r.get("id_anuncio"))
        if key:
            out[key] = _geo_point(r.get("latitud"), r.get("longitud"))
    return out


def load_municipios() -> int:
    dim = _read_csv("dim_municipios_enriquecido.csv")
    trans = _read_csv("transporte_paradas_municipio_enriquecido.csv")
    alq = _read_csv("alquiler_municipal_completo.csv")
    trans_by_code = {zfill_ine(r["codigo_ine"]): r for _, r in trans.iterrows()}
    oficial_codes = set()
    for _, r in alq.iterrows():
        c = zfill_ine(r.get("codigo_ine"))
        if c and (to_str(r.get("metodo_imputacion")) == "oficial" or to_str(r.get("nivel_geografico")) == "municipal"):
            oficial_codes.add(c)

    # JOVEN-18-34 (fase 3.1): renta/ratios/esfuerzo 18-34 y poblacion est.
    # viven en silver (analisis_variables_base / poblacion_joven_municipal);
    # dim_municipios_enriquecido solo trae legacy 16-29. Los campos nuevos
    # coexisten con el legacy (sin renombrado destructivo).
    base_by_code = _lookup_csv("analisis_variables_base.csv")
    pob_by_code = _lookup_csv("poblacion_joven_municipal.csv")

    docs: list[dict] = []
    for _, row in dim.iterrows():
        code = zfill_ine(row["codigo_ine"])
        if code is None:
            continue
        tr = trans_by_code.get(code)
        base = base_by_code.get(code)
        if base is None:
            base = {}
        pob = pob_by_code.get(code)
        if pob is None:
            pob = {}
        variantes = []
        raw_var = to_str(row.get("variantes"))
        if raw_var:
            try:
                variantes = json.loads(raw_var)
            except json.JSONDecodeError:
                variantes = [v.strip() for v in raw_var.split(",") if v.strip()]

        doc = {
            "_id": code,
            "nombre_canonico": to_str(row.get("nombre_canonico")),
            "territorio": to_str(row.get("territorio")),
            "nombre_normalizado": to_str(row.get("nombre_normalizado")),
            "variantes": variantes,
            "tiene_alquiler_oficial": code in oficial_codes,
            "tiene_fianzas_emal": to_bool(row.get("tiene_fianzas_emal")),
            "demografia": {
                "renta_eustat": to_float(row.get("renta_eustat")),
                "renta_hogar": to_float(row.get("renta_hogar")),
                "renta_atlas": to_float(row.get("renta_atlas")),
                # Legacy 16-29 (dim): se conserva como alias para comparabilidad.
                "renta_joven_estimada_16_29": to_float(row.get("renta_joven_estimada_16_29")),
                # JOVEN-18-34 canonico (silver analisis_variables_base).
                "renta_joven_estimada_18_34": to_float(base.get("renta_joven_estimada_18_34")),
                "renta_joven_estimada_18_24": to_float(base.get("renta_joven_estimada_18_24")),
                "renta_joven_estimada_25_34": to_float(base.get("renta_joven_estimada_25_34")),
                "ratio_fiscal_18_34": to_float(base.get("ratio_fiscal_18_34")),
                "ratio_fiscal_18_24": to_float(base.get("ratio_fiscal_18_24")),
                "ratio_fiscal_25_34": to_float(base.get("ratio_fiscal_25_34")),
                "flag_ratio_fiscal_18_34": to_str(base.get("flag_ratio_fiscal_18_34")),
                # Esfuerzo: canonico 18-34 + legacy 16-29 (alias, sin romper).
                "esfuerzo_joven_pct": (
                    to_float(base.get("esfuerzo_joven_pct_16_29"))
                    if to_float(base.get("esfuerzo_joven_pct_16_29")) is not None
                    else to_float(base.get("esfuerzo_joven_pct"))
                ),
                "esfuerzo_joven_pct_16_29": (
                    to_float(base.get("esfuerzo_joven_pct_16_29"))
                    if to_float(base.get("esfuerzo_joven_pct_16_29")) is not None
                    else to_float(base.get("esfuerzo_joven_pct"))
                ),
                "esfuerzo_joven_pct_18_34": to_float(base.get("esfuerzo_joven_pct_18_34")),
                "esfuerzo_joven_pct_18_24": to_float(base.get("esfuerzo_joven_pct_18_24")),
                "esfuerzo_joven_pct_25_34": to_float(base.get("esfuerzo_joven_pct_25_34")),
                "renta_familiar_eur": to_float(row.get("renta_familiar_eur")),
                "renta_personal_total_eur": to_float(row.get("renta_personal_total_eur")),
                "renta_personal_disponible_eur": to_float(row.get("renta_personal_disponible_eur")),
                "poblacion_16_24_estimada": to_int(row.get("poblacion_16_24_estimada")),
                # Poblacion 18-34 estimada (silver poblacion_joven_municipal, _est).
                "poblacion_18_34_est": to_int(pob.get("poblacion_18_34_est")),
                "poblacion_18_24_est": to_int(pob.get("poblacion_18_24_est")),
                "poblacion_25_34_est": to_int(pob.get("poblacion_25_34_est")),
                "renta_personal_total_hombres_eur": to_float(row.get("renta_personal_total_hombres_eur")),
                "renta_personal_total_mujeres_eur": to_float(row.get("renta_personal_total_mujeres_eur")),
            },
            "empleo": {
                "tasa_actividad_pct": to_float(row.get("tasa_actividad_pct")),
                "tasa_ocupacion_pct": to_float(row.get("tasa_ocupacion_pct")),
                "tasa_paro_lanbide_pct": to_float(row.get("tasa_paro_lanbide_pct")),
                "tasa_paro_valida": to_bool(row.get("tasa_paro_valida")),
                "tasa_ocupacion_juvenil_16_24_pct": to_float(row.get("tasa_ocupacion_juvenil_16_24_pct")),
                "trabaja_fuera_pct": to_float(row.get("trabaja_fuera_pct")),
                "afiliacion_ss_16_24_pct": to_float(row.get("afiliacion_ss_16_24_pct")),
                "paro_joven_menores_25": to_int(row.get("paro_joven_menores_25")),
                "ocupados_16_24": to_int(row.get("ocupados_16_24")),
                "activos_16_24": to_int(row.get("activos_16_24")),
                "tasa_desempleo_juvenil_real_pct": to_float(row.get("tasa_desempleo_juvenil_real_pct")),
                "tasa_paro_joven_pct": to_float(row.get("tasa_paro_joven_pct")),
            },
            "vivienda_contexto": {
                "superficie_media_m2": to_float(row.get("superficie_media_m2")),
                "antiguedad_media_anyos": to_float(row.get("antiguedad_media_anyos")),
                "dist_bilbao_km": to_float(row.get("dist_bilbao_km")),
                "dist_donostia_km": to_float(row.get("dist_donostia_km")),
                "dist_vitoria_km": to_float(row.get("dist_vitoria_km")),
                "capital_mas_cercana": to_str(row.get("capital_mas_cercana")),
                "dist_centroide_comarca_km": to_float(row.get("dist_centroide_comarca_km")),
                "renta_media_eur_m2_media": to_float(row.get("renta_media_eur_m2_media")),
                "cuantia_media_eur_mes_media": to_float(row.get("cuantia_media_eur_mes_media")),
                "superficie_media_m2_media": to_float(row.get("superficie_media_m2_media")),
                "alquiler_anual": to_float(row.get("alquiler_anual")),
            },
            "demanda_social": {
                "etxebide_solicitudes_por_mil_2024": to_float(row.get("etxebide_solicitudes_por_mil_2024")),
                "tension_demanda_social": to_float(row.get("tension_demanda_social")),
                "tension_categoria": to_str(row.get("tension_categoria")),
            },
            "transporte": {
                "n_paradas": to_int(tr.get("n_paradas")) if tr is not None else None,
                "expediciones_dia": to_int(tr.get("expediciones_dia")) if tr is not None else None,
                "tiene_tren_metro": to_bool(tr.get("tiene_tren_metro")) if tr is not None else None,
                "tiene_transporte_publico": to_bool(tr.get("tiene_transporte_publico")) if tr is not None else None,
                "paradas_por_1000_hab": to_float(tr.get("paradas_por_1000_hab")) if tr is not None else None,
                "operadores": [x.strip() for x in str(tr.get("operadores")).split(";") if x and str(x).strip() and str(x).strip().lower() != "nan"] if tr is not None else [],
            },
            "fuente": "silver dim_municipios_enriquecido + transporte + alquiler + analisis_variables_base (18-34) + poblacion_joven_municipal (18-34 est)",
            "anio_fuente": 2024,
            "fecha_carga": datetime.now(timezone.utc),
        }
        docs.append(doc)
    if not docs:
        return 0
    return replace_collection("municipios", docs)


def load_anuncios() -> int:
    # CARGA-SEGURA-01: staging + <name>__backup + rename atomico via
    # replace_collection (rename con dropTarget=True); nunca drop directo
    # sobre la coleccion original; docs vacios abortan sin tocar origen.
    df = _read_csv("anuncios_unificados.csv")
    geo_by_id = _lookup_fotocasa_geo()
    docs: list[dict] = []
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        if code is None:
            continue
        equip = to_str(row.get("equipamiento"))
        equip_list = [x.strip() for x in equip.split(",") if x.strip()] if equip else []
        portal = to_str(row.get("portal"))
        id_anuncio = to_str(row.get("id_anuncio"))
        coordenadas = geo_by_id.get(id_anuncio) if portal == "fotocasa" and id_anuncio else None
        # M1 OUTLIER-01 (AGREGACION-01): `precio_m2` solo porta el valor valido
        # para la agregacion (precio_m2_calc en [3, 50] y superficie en
        # [10, 500]); fuera de rango -> None (el bruto queda en
        # precio_m2_calc + auditoria). Asi, 0 documentos participan en la
        # agregacion con precio_m2 fuera de [3, 50].
        _pm2 = to_float(row.get("precio_m2_calc"))
        _sup = to_float(row.get("superficie_m2"))
        precio_m2_valido = _pm2 if (_pm2 is not None and 3 <= _pm2 <= 50
                                    and (_sup is None or 10 <= _sup <= 500)) else None
        doc = {
            "portal": to_str(row.get("portal")),
            "id_anuncio": to_str(row.get("id_anuncio")),
            "property_fingerprint": to_str(row.get("property_fingerprint")),
            "modalidad": to_str(row.get("modalidad")),
            "precio_eur": _money(row.get("precio_eur")),
            "superficie_m2": to_float(row.get("superficie_m2")),
            "habitaciones": to_int(row.get("habitaciones")),
            "es_outlier_superficie": to_bool(row.get("es_outlier_superficie")),
            "ubicacion": {
                "codigo_ine": code,
                "municipio": to_str(row.get("municipio")),
                "barrio": None,
                "distrito": None,
                "coordenadas": coordenadas,
            },
            "equipamiento": equip_list,
            "precio_m2_calc": to_float(row.get("precio_m2_calc")),
            "precio_m2": precio_m2_valido,
            "es_outlier_iqr": to_bool(row.get("es_outlier_iqr")),
            "motivo_exclusion": to_str(row.get("motivo_exclusion")),
            "precio_m2_fuera_3_50": to_bool(row.get("precio_m2_fuera_3_50")),
            "superficie_fuera_10_500": to_bool(row.get("superficie_fuera_10_500")),
            "iqr_excluido": to_bool(row.get("iqr_excluido")),
            "auditoria": {
                "es_outlier_iqr": to_bool(row.get("es_outlier_iqr")),
                "precio_m2_calc": to_float(row.get("precio_m2_calc")),
            },
            "historico_precios": [],
            "fuente": "silver anuncios_unificados",
            "anio_fuente": 2026,
            "fecha_carga": datetime.now(timezone.utc),
            "origen_resolucion": to_str(row.get("origen_resolucion")),
            "geo_invalida": to_bool(row.get("geo_invalida")),
        }
        docs.append(doc)
    if not docs:
        return 0
    return replace_collection("anuncios", docs)


def load_alquiler() -> int:
    df = _read_csv("alquiler_municipal_completo.csv")
    docs = []
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        if code is None:
            continue
        docs.append({
            "_id": code,
            "codigo_ine": code,
            "territorio": to_str(row.get("territorio")),
            "municipio": to_str(row.get("municipio")),
            "distrito": to_str(row.get("distrito")),
            "nivel_geografico": to_str(row.get("nivel_geografico")),
            "metodo_imputacion": to_str(row.get("metodo_imputacion")),
            "idw_vecinos": to_str(row.get("idw_vecinos")),
            "renta_media_eur_m2_media": to_float(row.get("renta_media_eur_m2_media")),
            "renta_media_eur_m2_mediana": to_float(row.get("renta_media_eur_m2_mediana")),
            "renta_media_eur_m2_p25": to_float(row.get("renta_media_eur_m2_p25")),
            "renta_media_eur_m2_p75": to_float(row.get("renta_media_eur_m2_p75")),
            "cuantia_media_eur_mes_media": to_float(row.get("cuantia_media_eur_mes_media")),
            "cuantia_media_eur_mes_mediana": to_float(row.get("cuantia_media_eur_mes_mediana")),
            "superficie_media_m2_media": to_float(row.get("superficie_media_m2_media")),
            "superficie_media_m2_mediana": to_float(row.get("superficie_media_m2_mediana")),
            "fuente": "Eustat alquiler municipal + imputacion comarcal/IDW",
            "anio_fuente": 2024,
            "fecha_carga": datetime.now(timezone.utc),
        })
    if not docs:
        return 0
    return replace_collection("alquiler_municipal", docs)


def load_indicadores() -> int:
    df = _read_csv("analisis_variables_base.csv")
    docs = []
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        if code is None:
            continue
        doc = {"_id": code, "codigo_ine": code, "fuente": "silver analisis_variables_base", "anio_fuente": 2024, "fecha_carga": datetime.now(timezone.utc)}
        for col in df.columns:
            if col == "codigo_ine":
                continue
            val = row.get(col)
            if col in {"nombre_canonico", "territorio", "capital_mas_cercana", "tipologia_mercado", "flag_ratio_fiscal_18_34"}:
                doc[col] = to_str(val)
            elif col in {"tiene_alquiler_oficial", "tasa_paro_valida"}:
                doc[col] = to_bool(val)
            else:
                f = to_float(val)
                if f is not None and float(f).is_integer() and col not in {"renta_eustat"}:
                    # keep counts as int when clearly integer-valued
                    pass
                doc[col] = f
        # JOVEN-18-34: alias legacy preservados sin romper (esfuerzo_joven_pct
        # = legacy 16-29; el canonico nuevo es esfuerzo_joven_pct_18_34).
        if doc.get("esfuerzo_joven_pct_16_29") is None and doc.get("esfuerzo_joven_pct") is not None:
            doc["esfuerzo_joven_pct_16_29"] = doc["esfuerzo_joven_pct"]
        if doc.get("esfuerzo_alquiler_pct") is None and doc.get("esfuerzo_joven_pct") is not None:
            doc["esfuerzo_alquiler_pct"] = doc["esfuerzo_joven_pct"]
        docs.append(doc)
    if not docs:
        return 0
    return replace_collection("indicadores", docs)


def _load_json(path: str):
    with open(ROOT / "data" / "procesado" / path, encoding="utf-8") as f:
        return json.load(f)


def _prov_from_loaded(data, default_fuente: str) -> tuple[dict, list]:
    if isinstance(data, dict):
        meta = data.get("metadata", {})
        recs = data.get("datos", [])
        if not isinstance(recs, list):
            recs = []
    else:
        meta, recs = {}, (data if isinstance(data, list) else [])
    return _provenance_from_raw_meta(meta, default_fuente), recs


def load_ecvi() -> int:
    data = _load_json("ecvi_compraventa_limpio.json")
    prov, records = _prov_from_loaded(data, "OVV ECVI compraventa")
    coll = get_collection("ecvi_compraventa")
    docs = []
    for i, row in enumerate(records if records else (data if isinstance(data, list) else [])):
        code = zfill_ine(row.get("codigo_ine"))
        doc = dict(row)
        if code:
            doc["_id"] = f"{code}_{row.get('trimestre', i)}"
        doc.update(prov)
        doc["fecha_carga"] = datetime.now(timezone.utc)
        docs.append(doc)
    if not docs:
        return 0
    return replace_collection("ecvi_compraventa", docs)


def load_udalmap_indicadores() -> int:
    data = _load_json("udalmap_indicadores_adicionales_normalizado.json")
    prov, records = _prov_from_loaded(data, "Eustat Udalmap indicadores")
    docs = []
    for row in records:
        code = zfill_ine(row.get("codigo_ine"))
        doc = dict(row)
        if code:
            doc["_id"] = code
        doc.update(prov)
        doc["fecha_carga"] = datetime.now(timezone.utc)
        docs.append(doc)
    if not docs:
        return 0
    return replace_collection("udalmap_indicadores", docs)


def load_udalmap_empleo() -> int:
    data = _load_json("udalmap_empleo_corregido.json")
    prov, records = _prov_from_loaded(data, "Eustat Udalmap empleo")
    docs = []
    for row in records:
        code = zfill_ine(row.get("codigo_ine"))
        doc = dict(row)
        if code:
            doc["_id"] = code
        doc.update(prov)
        doc["fecha_carga"] = datetime.now(timezone.utc)
        docs.append(doc)
    return replace_collection("udalmap_empleo", docs)


def load_osrm() -> int:
    data = _load_json("osrm_tiempos_capitales_normalizado.json")
    prov, records = _prov_from_loaded(data, "OSRM tiempos a capitales")
    docs = []
    for row in records:
        code = zfill_ine(row.get("codigo_ine"))
        doc = dict(row)
        if code:
            doc["_id"] = code
        doc.update(prov)
        doc["fecha_carga"] = datetime.now(timezone.utc)
        docs.append(doc)
    return replace_collection("osrm_tiempos", docs)


def load_emancipacion() -> int:
    data = _load_json("emancipacion_juventud_resumen_normalizado.json")
    if isinstance(data, dict):
        prov = _provenance_from_raw_meta(data.get("metadata", {}), "Observatorio Juventud emancipacion")
        payload = {k: v for k, v in data.items() if k != "metadata"}
    else:
        prov, payload = _provenance_from_raw_meta({}, "Observatorio Juventud emancipacion"), {"datos": data}
    doc = {"_id": "resumen", **payload, **prov, "fecha_carga": datetime.now(timezone.utc)}
    return replace_collection("emancipacion_juventud", [doc])


def load_etxebide_solicitudes() -> int:
    data = _load_json("etxebide_solicitudes_normalizado.json")
    prov, records = _prov_from_loaded(data, "Etxebide solicitudes")
    docs = []
    for i, row in enumerate(records):
        code = zfill_ine(row.get("codigo_ine"))
        doc = dict(row)
        anio = row.get("anio")
        if code and anio is not None:
            doc["_id"] = f"{code}_{anio}"
        doc.update(prov)
        doc["fecha_carga"] = datetime.now(timezone.utc)
        docs.append(doc)
    return replace_collection("etxebide_solicitudes", docs)


def _provenance_from_raw_meta(meta: dict, default_fuente: str, default_url: str | None = None) -> dict:
    fuente = meta.get("fuente") or default_fuente
    url = meta.get("url") or default_url
    fecha_ext = meta.get("fecha_extraccion")
    anio = None
    if isinstance(fecha_ext, str) and len(fecha_ext) >= 4 and fecha_ext[:4].isdigit():
        anio = int(fecha_ext[:4])
    return {"fuente": fuente, "fuente_url": url, "anio_fuente": anio, "fecha_extraccion": fecha_ext}


def load_udalmap_extendido() -> int:
    with open(ROOT / "data" / "raw" / "udalmap_extendido.json", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("datos", [])
    prov = _provenance_from_raw_meta(data.get("metadata", {}), "Eustat Udalmap (API)", "https://api.euskadi.eus/udalmap/indicators")
    docs = []
    for row in records:
        code = zfill_ine(row.get("codigo_ine"))
        doc = dict(row)
        if code:
            doc["_id"] = code
        doc.update(prov)
        doc["fecha_carga"] = datetime.now(timezone.utc)
        docs.append(doc)
    return replace_collection("udalmap_extendido", docs)


def _codigo_ine_etxebide(row: dict) -> str | None:
    prov = to_str(row.get("Cod_Prov"))
    muni = to_str(row.get("CODMUNI"))
    if prov is None or muni is None:
        return None
    digits_prov = "".join(ch for ch in prov if ch.isdigit())
    digits_muni = "".join(ch for ch in muni if ch.isdigit())
    if not digits_prov or not digits_muni:
        return None
    code = digits_prov.zfill(2) + digits_muni.zfill(3)
    return zfill_ine(code)


def load_etxebide_promociones() -> int:
    with open(ROOT / "data" / "raw" / "etxebide_promociones.json", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("datos", [])
    prov = _provenance_from_raw_meta(data.get("metadata", {}), "Open Data Euskadi - Promociones Etxebide")
    docs = []
    for i, row in enumerate(records):
        doc = dict(row)
        doc["_id"] = f"{row.get('ID_PROM', i)}_{i}"
        doc["codigo_ine"] = _codigo_ine_etxebide(row)
        # NumViviendas viene vacio en el CSV origen (406/406 vacios 2026-11-03): se guarda None y se documenta como sin dato.
        doc["num_viviendas"] = to_int(row.get("NumViviendas"))
        doc["estado_obra"] = to_str(row.get("EstadoObra"))
        doc["tipologia"] = to_str(row.get("Tipologia"))
        doc["reg_acceso"] = to_str(row.get("Reg Acceso"))
        doc.update(prov)
        doc["fecha_carga"] = datetime.now(timezone.utc)
        docs.append(doc)
    return replace_collection("etxebide_promociones", docs)


def load_certificados() -> int:
    df = _read_csv("cert_energetico_municipal_252.csv")
    docs = []
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        if code is None:
            continue
        docs.append({
            "_id": code,
            "codigo_ine": code,
            "municipio": to_str(row.get("municipio")),
            "n_certificados": to_int(row.get("n_certificados")),
            "cert_moda": to_str(row.get("cert_moda")),
            "distribucion": {
                "A": to_int(row.get("cert_A")),
                "B": to_int(row.get("cert_B")),
                "C": to_int(row.get("cert_C")),
                "D": to_int(row.get("cert_D")),
                "E": to_int(row.get("cert_E")),
                "F": to_int(row.get("cert_F")),
                "G": to_int(row.get("cert_G")),
            },
            "fuente": "Open Data Euskadi - Registro de Certificados de Eficiencia Energetica",
            "fuente_url": "https://opendata.euskadi.eus/catalogo/-/registro-de-certificados-de-eficiencia-energetica-de-euskadi/",
            "anio_fuente": 2026,
            "fecha_extraccion": "2026-11-03",
            "fecha_carga": datetime.now(timezone.utc),
        })
    return replace_collection("certificados_energeticos", docs)


def load_vpo_municipal() -> int:
    """VPO terminada en el ultimo quinquenio (Udalmap 73), flujo en por mil."""
    df = _read_csv("vpo_municipal.csv")
    docs = []
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        if code is None:
            continue
        docs.append({
            "_id": code,
            "codigo_ine": code,
            "municipio": to_str(row.get("municipio")),
            "vpo_terminadas_por_mil": to_float(row.get("vpo_terminadas_por_mil")),
            "anio_fuente": to_int(row.get("anio_fuente")),
            "fuente": to_str(row.get("fuente")),
            "fuente_url": to_str(row.get("fuente_url")),
            "fecha_carga": datetime.now(timezone.utc),
        })
    if not docs:
        return 0
    return replace_collection("vpo_municipal", docs)


def load_all() -> dict[str, int]:
    result = {
        "municipios": load_municipios(),
        "anuncios": load_anuncios(),
        "alquiler_municipal": load_alquiler(),
        "indicadores": load_indicadores(),
        "ecvi_compraventa": load_ecvi(),
        "udalmap_indicadores": load_udalmap_indicadores(),
        "udalmap_empleo": load_udalmap_empleo(),
        "osrm_tiempos": load_osrm(),
        "emancipacion_juventud": load_emancipacion(),
        "etxebide_solicitudes": load_etxebide_solicitudes(),
        "udalmap_extendido": load_udalmap_extendido(),
        "etxebide_promociones": load_etxebide_promociones(),
        "certificados_energeticos": load_certificados(),
        "vpo_municipal": load_vpo_municipal(),
    }
    try:
        from analysis.mongo_indexes import ensure_indexes

        ensure_indexes()
    except Exception as exc:
        logger.exception("No se pudieron crear los índices de MongoDB tras la carga")
        raise RuntimeError(
            f"No se pudieron crear los índices de MongoDB tras la carga: {exc}"
        ) from exc
    return result


if __name__ == "__main__":
    from storage.mongo import ping

    if not ping():
        raise SystemExit("MongoDB no responde en localhost:27017")
    print(load_all())