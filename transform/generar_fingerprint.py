"""Genera property_fingerprint (sha256) en anuncios_unificados.json."""
from __future__ import annotations
import hashlib, json, os

OUT = os.path.join("data", "procesado")
path = os.path.join(OUT, "anuncios_unificados.json")

with open(path, encoding="utf-8") as f:
    data = json.load(f)

def fingerprint(rec):
    ci = rec.get("ubicacion", {}).get("codigo_ine") or ""
    sup = rec.get("superficie_m2")
    hab = rec.get("habitaciones")
    precio = rec.get("precio_eur")
    # round superficie to 5, precio to 50
    sup_r = round(sup / 5) * 5 if sup is not None else 0
    precio_r = round(precio / 50) * 50 if precio is not None else 0
    hab_r = hab if hab is not None else 0
    key = f"{ci}|{sup_r}|{hab_r}|{precio_r}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

for rec in data:
    rec["property_fingerprint"] = fingerprint(rec)

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# update CSV (additive: preserve existing columns)
import pandas as pd
csv_path = os.path.join(OUT, "anuncios_unificados.csv")
prev = None
if os.path.exists(csv_path):
    try:
        # dtype=str: preservar codigo_ine con 5 digitos (no perder el "0" de Alava)
        prev = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig")
    except Exception:
        prev = None
df = pd.DataFrame([{
    "id_anuncio": r["id_anuncio"],
    "portal": r["portal"],
    "modalidad": r["modalidad"],
    "precio_eur": r["precio_eur"],
    "superficie_m2": r["superficie_m2"],
    "codigo_ine": r["ubicacion"]["codigo_ine"],
    "municipio": r["ubicacion"]["municipio"],
    "equipamiento": ",".join(r["equipamiento"]),
    "property_fingerprint": r["property_fingerprint"],
} for r in data])
df["codigo_ine"] = df["codigo_ine"].astype(str).str.strip().str.zfill(5)
# preserve any previous columns not in df
if prev is not None:
    for col in prev.columns:
        if col in df.columns:
            continue
        if "id_anuncio" in prev.columns and "id_anuncio" in df.columns:
            mapping = dict(zip(prev["id_anuncio"].astype(str), prev[col]))
            df[col] = df["id_anuncio"].astype(str).map(mapping)
        else:
            df[col] = pd.NA
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print("Fingerprints generados:", len(data))
print("Unicos:", len(set(r["property_fingerprint"] for r in data)))