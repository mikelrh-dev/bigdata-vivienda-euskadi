"""Load silver data into MongoDB (idempotent)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from bson.decimal128 import Decimal128

from storage.mongo import (
    get_collection,
    to_bool,
    to_float,
    to_int,
    to_str,
    zfill_ine,
)

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "procesado"


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROC / name, encoding="utf-8-sig", dtype=str)


def _money(value):
    text = (value if value is None else str(value)).strip()
    if text == "" or text.lower() == "nan":
        return None
    try:
        return Decimal128(text)
    except Exception:
        return None


def load_municipios() -> int:
    dim = _read_csv("dim_municipios_enriquecido.csv")
    trans = _read_csv("transporte_paradas_municipio_enriquecido.csv")
    trans_by_code = {zfill_ine(r["codigo_ine"]): r for _, r in trans.iterrows()}

    coll = get_collection("municipios")
    n = 0
    for _, row in dim.iterrows():
        code = zfill_ine(row["codigo_ine"])
        if code is None:
            continue
        tr = trans_by_code.get(code)
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
            "tiene_alquiler_oficial": to_bool(row.get("tiene_alquiler_oficial")),
            "tiene_fianzas_emal": to_bool(row.get("tiene_fianzas_emal")),
            "demografia": {
                "renta_eustat": to_float(row.get("renta_eustat")),
                "renta_hogar": to_float(row.get("renta_hogar")),
                "renta_atlas": to_float(row.get("renta_atlas")),
                "renta_joven_estimada_16_29": to_float(row.get("renta_joven_estimada_16_29")),
                "renta_familiar_eur": to_float(row.get("renta_familiar_eur")),
                "renta_personal_total_eur": to_float(row.get("renta_personal_total_eur")),
                "renta_personal_disponible_eur": to_float(row.get("renta_personal_disponible_eur")),
                "poblacion_16_24_estimada": to_int(row.get("poblacion_16_24_estimada")),
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
            "fecha_carga": datetime.now(timezone.utc),
        }
        coll.replace_one({"_id": code}, doc, upsert=True)
        n += 1
    return n


def load_anuncios() -> int:
    df = _read_csv("anuncios_unificados.csv")
    coll = get_collection("anuncios")
    n = 0
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        equip = to_str(row.get("equipamiento"))
        equip_list = [x.strip() for x in equip.split(",") if x.strip()] if equip else []
        doc = {
            "portal": to_str(row.get("portal")),
            "id_anuncio": to_str(row.get("id_anuncio")),
            "property_fingerprint": to_str(row.get("property_fingerprint")),
            "modalidad": to_str(row.get("modalidad")),
            "precio_eur": _money(row.get("precio_eur")),
            "superficie_m2": to_float(row.get("superficie_m2")),
            "habitaciones": to_float(row.get("habitaciones")),
            "es_outlier_superficie": to_bool(row.get("es_outlier_superficie")),
            "ubicacion": {
                "codigo_ine": code,
                "municipio": to_str(row.get("municipio")),
                "barrio": None,
                "distrito": None,
                "coordenadas": None,
            },
            "equipamiento": equip_list,
            "precio_m2_calc": to_float(row.get("precio_m2_calc")),
            "es_outlier_iqr": to_bool(row.get("es_outlier_iqr")),
            "auditoria": {
                "es_outlier_iqr": to_bool(row.get("es_outlier_iqr")),
                "precio_m2_calc": to_float(row.get("precio_m2_calc")),
            },
            "historico_precios": [],
            "fecha_carga": datetime.now(timezone.utc),
        }
        coll.update_one(
            {"portal": doc["portal"], "id_anuncio": doc["id_anuncio"]},
            {"$set": doc},
            upsert=True,
        )
        n += 1
    return n


def load_alquiler() -> int:
    df = _read_csv("alquiler_municipal_completo.csv")
    coll = get_collection("alquiler_municipal")
    n = 0
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        doc = {
            "codigo_ine": code,
            "territorio": to_str(row.get("territorio")),
            "municipio": to_str(row.get("municipio")),
            "distrito": to_str(row.get("distrito")),
            "nivel_geografico": to_str(row.get("nivel_geografico")),
            "metodo_imputacion": to_str(row.get("metodo_imputacion")),
            "idw_vecinos": to_int(row.get("idw_vecinos")),
            "renta_media_eur_m2_media": to_float(row.get("renta_media_eur_m2_media")),
            "renta_media_eur_m2_mediana": to_float(row.get("renta_media_eur_m2_mediana")),
            "renta_media_eur_m2_p25": to_float(row.get("renta_media_eur_m2_p25")),
            "renta_media_eur_m2_p75": to_float(row.get("renta_media_eur_m2_p75")),
            "cuantia_media_eur_mes_media": to_float(row.get("cuantia_media_eur_mes_media")),
            "cuantia_media_eur_mes_mediana": to_float(row.get("cuantia_media_eur_mes_mediana")),
            "superficie_media_m2_media": to_float(row.get("superficie_media_m2_media")),
            "superficie_media_m2_mediana": to_float(row.get("superficie_media_m2_mediana")),
            "fecha_carga": datetime.now(timezone.utc),
        }
        coll.update_one({"codigo_ine": code}, {"$set": doc}, upsert=True)
        n += 1
    return n


def load_indicadores() -> int:
    df = _read_csv("analisis_variables_base.csv")
    coll = get_collection("indicadores")
    n = 0
    for _, row in df.iterrows():
        code = zfill_ine(row.get("codigo_ine"))
        doc = {"codigo_ine": code}
        for col in df.columns:
            if col == "codigo_ine":
                continue
            val = row.get(col)
            if col in {"nombre_canonico", "territorio", "capital_mas_cercana", "tipologia_mercado"}:
                doc[col] = to_str(val)
            elif col in {"tiene_alquiler_oficial", "tasa_paro_valida"}:
                doc[col] = to_bool(val)
            else:
                f = to_float(val)
                if f is not None and float(f).is_integer() and col not in {"renta_eustat"}:
                    # keep counts as int when clearly integer-valued
                    pass
                doc[col] = f
        coll.update_one({"codigo_ine": code}, {"$set": doc}, upsert=True)
        n += 1
    return n


def load_all() -> dict[str, int]:
    return {
        "municipios": load_municipios(),
        "anuncios": load_anuncios(),
        "alquiler_municipal": load_alquiler(),
        "indicadores": load_indicadores(),
    }


if __name__ == "__main__":
    from storage.mongo import ping

    if not ping():
        raise SystemExit("MongoDB no responde en localhost:27017")
    print(load_all())