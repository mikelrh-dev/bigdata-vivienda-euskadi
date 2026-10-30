"""Enriquece equipamiento de anuncios RealtyAPI en anuncios_unificados.json (post-proceso)."""
from __future__ import annotations
import json, os, re

OUT = os.path.join("data", "procesado")
path = os.path.join(OUT, "anuncios_unificados.json")
with open(path, encoding="utf-8") as f:
    data = json.load(f)

keywords = ["ascensor", "terraza", "parking", "garaje", "balcon", "balcón",
            "jardin", "jardín", "piscina", "trastero", "calefaccion", "calefacción",
            "aire acondicionado", "amueblado", "exterior", "interior", "dúplex", "duplex", "ático", "atico"]

# load realtyapi raw for descripcion/exterior
raw_path = os.path.join("data", "raw", "anuncios_realtyapi.json")
with open(raw_path, encoding="utf-8") as f:
    raw = json.load(f)["datos"]
raw_map = {str(r.get("id_anuncio")): r for r in raw}

changed = 0
for rec in data:
    if rec.get("portal") != "realtyapi":
        continue
    rid = str(rec.get("id_anuncio"))
    r = raw_map.get(rid, {})
    eq = set(rec.get("equipamiento") or [])
    # exterior
    ext = r.get("exterior")
    if ext is True or str(ext).lower() == "true":
        eq.add("exterior")
    elif ext is False or str(ext).lower() == "false":
        eq.add("interior")
    # planta
    planta = r.get("planta")
    if planta is not None and str(planta).lower() in ("bj", "bajo"):
        eq.add("planta_baja")
    # descripcion NLP
    desc = str(r.get("descripcion") or "").lower()
    for kw in keywords:
        if kw in desc:
            # normalize
            norm = kw.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            eq.add(norm)
    rec["equipamiento"] = sorted(eq)
    changed += 1

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# also update CSV (additive: preserve existing columns)
import pandas as pd
csv_path = os.path.join(OUT, "anuncios_unificados.csv")
prev = None
if os.path.exists(csv_path):
    try:
        # dtype=str: preservar codigo_ine con 5 digitos (no perder el "0" de Alava)
        prev = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig")
    except Exception:
        prev = None
if prev is not None:
    # update equipamiento column from JSON
    eq_map = {}
    for r in data:
        eq_map[(str(r.get("portal")), str(r.get("id_anuncio")))] = ",".join(r.get("equipamiento") or [])
    if "equipamiento" in prev.columns:
        def _upd(row):
            key = (str(row.get("portal")), str(row.get("id_anuncio")))
            return eq_map.get(key, row.get("equipamiento"))
        prev["equipamiento"] = prev.apply(_upd, axis=1)
    # ensure superset: add any missing base columns empty
    base_cols = ["id_anuncio", "portal", "modalidad", "precio_eur", "superficie_m2", "habitaciones",
                 "es_outlier_superficie", "codigo_ine", "municipio", "titulo", "subtitulo", "equipamiento"]
    for col in base_cols:
        if col not in prev.columns:
            prev[col] = pd.NA
    if "codigo_ine" in prev.columns:
        prev["codigo_ine"] = prev["codigo_ine"].astype(str).str.strip().str.zfill(5)
    prev.to_csv(csv_path, index=False, encoding="utf-8-sig")
else:
    df = pd.DataFrame([{
        "id_anuncio": r["id_anuncio"],
        "portal": r["portal"],
        "modalidad": r["modalidad"],
        "precio_eur": r["precio_eur"],
        "superficie_m2": r["superficie_m2"],
        "codigo_ine": r["ubicacion"]["codigo_ine"],
        "municipio": r["ubicacion"]["municipio"],
        "equipamiento": ",".join(r["equipamiento"]),
    } for r in data])
    df["codigo_ine"] = df["codigo_ine"].astype(str).str.strip().str.zfill(5)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print("RealtyAPI enriquecidos:", changed)
print("Total anuncios:", len(data))