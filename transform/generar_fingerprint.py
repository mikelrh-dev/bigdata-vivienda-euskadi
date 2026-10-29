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

# update CSV
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
    "property_fingerprint": r["property_fingerprint"],
} for r in data])
df.to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False)
print("Fingerprints generados:", len(data))
print("Unicos:", len(set(r["property_fingerprint"] for r in data)))