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

# also update CSV
import pandas as pd
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
df.to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False)
print("RealtyAPI enriquecidos:", changed)
print("Total anuncios:", len(data))