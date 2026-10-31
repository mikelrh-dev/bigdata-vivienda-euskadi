"""Sondas de estrés de solo lectura sobre el estado real del proyecto.

Uso:
    .venv/Scripts/python.exe openspec/audit/estres/sondas_estres_2026-10-31.py

No modifica nada: abre ficheros en modo lectura y escribe únicamente el JSON de
resultados junto a este script.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "procesado"
RES = ROOT / "data" / "resultados"
OUT = Path(__file__).resolve().parent / "resultados_sondas_2026-10-31.json"

R = {"fecha": "2026-10-31", "root": str(ROOT)}

# ---------------------------------------------------------------- utilidades


def csv(name: str, base: Path = PROC) -> pd.DataFrame:
    """Lee CSV forzando str: evita que 01001 se convierta en 1001."""
    return pd.read_csv(base / name, dtype=str, encoding="utf-8-sig", low_memory=False)


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def add(k: str, v) -> None:
    R[k] = v
    print(f"[{k}] {v}")


# ------------------------------------------------- 1. inventario y congelado
t0 = time.monotonic()
inv = {
    "raw_files": sum(1 for p in RAW.rglob("*") if p.is_file()),
    "proc_files": sum(1 for p in PROC.rglob("*") if p.is_file()),
    "res_files": sum(1 for p in RES.rglob("*") if p.is_file()),
    "raw_mb": round(sum(p.stat().st_size for p in RAW.rglob("*") if p.is_file()) / 1e6, 1),
    "frozen_marker": (RAW / ".FROZEN").exists(),
}
manifests = sorted(RAW.glob("*manifest*")) + sorted(RAW.glob("*MANIFEST*"))
inv["manifest_files"] = [p.name for p in manifests]
if manifests:
    try:
        m = json.loads(manifests[0].read_text(encoding="utf-8"))
        inv["manifest_entries"] = len(m) if hasattr(m, "__len__") else None
    except Exception as exc:  # pragma: no cover
        inv["manifest_entries"] = f"error: {exc}"
add("inventario", inv)

# ------------------------------------- 2. metadata FORMATO-01 en JSON crudos
FECHA_KEYS = {"fecha_extraccion", "fecha_descarga", "fecha_conversion", "fecha", "timestamp"}
FUENTE_KEYS = {"fuente", "source", "origen"}
META_KEYS = {"metadata", "meta", "_metadata"}
json_gaps = []
json_seen = 0
for p in sorted(RAW.glob("*.json")):
    json_seen += 1
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        json_gaps.append({"file": p.name, "issue": f"ilegible: {exc}"})
        continue
    if not isinstance(obj, dict):
        json_gaps.append({"file": p.name, "issue": "raiz no-dict (sin bloque de metadata)"})
        continue
    keys = set(obj)
    meta_blob = {}
    for mk in META_KEYS & keys:
        if isinstance(obj[mk], dict):
            meta_blob = obj[mk]
    allk = keys | set(meta_blob)
    missing = []
    if not (FECHA_KEYS & allk):
        missing.append("fecha")
    if not (FUENTE_KEYS & allk):
        missing.append("fuente")
    if not ({"n_registros", "n_filas", "num_registros", "count"} & allk):
        missing.append("recuento")
    if missing:
        json_gaps.append({"file": p.name, "issue": "falta " + "/".join(missing)})
add("formato01_json", {"json_raiz": json_seen, "con_gaps": len(json_gaps), "gaps": json_gaps})

# ------------------------------------------ 3. encoding de los CSV crudos
enc_issues = []
for p in sorted(RAW.glob("*.csv")):
    raw = p.read_bytes()[:200_000]
    if raw.startswith(b"\xef\xbb\xbf"):
        enc = "utf-8-sig"
    else:
        try:
            raw.decode("utf-8")
            enc = "utf-8"
        except UnicodeDecodeError:
            enc = "no-utf8"
    if enc != "utf-8-sig":
        try:
            txt = p.read_text(encoding=enc if enc != "no-utf8" else "latin-1")
            delim = ";" if txt.split("\n", 1)[0].count(";") > txt.split("\n", 1)[0].count(",") else ","
        except Exception:
            delim = "?"
        enc_issues.append({"file": p.name, "encoding": enc, "delimiter": delim})
add("formato01_encoding_csv", {"csv_raiz": len(list(RAW.glob('*.csv'))), "no_bom": len(enc_issues), "detalle": enc_issues})

# --------------------------------------------- 4. integridad de dim_municipios
dim = csv("dim_municipios.csv")
dim_codes = dim["codigo_ine"].astype(str).str.strip()
dup_codes = dim_codes[dim_codes.duplicated()].tolist()
name_col = "nombre_canonico" if "nombre_canonico" in dim else dim.columns[1]
dup_names = dim[name_col][dim[name_col].duplicated(keep=False)].tolist()
add("dim_municipios", {
    "rows": len(dim),
    "codigos_unicos": dim_codes.nunique(),
    "duplicados_codigo": dup_codes,
    "duplicados_nombre": sorted(set(dup_names)),
    "longitudes": dim_codes.str.len().value_counts().to_dict(),
    "prefijos": dim_codes.str[:2].value_counts().to_dict(),
    "esperado_oficial_euskadi": 251,
    "delta_vs_oficial": len(dim) - 251,
})

# ----------------------------------------- 5. integridad referencial al dim
ref = {}
for name, col in [
    ("alquiler_municipal_completo.csv", "codigo_ine"),
    ("analisis_variables_base.csv", "codigo_ine"),
    ("distancias_capitales_252.csv", "codigo_ine"),
    ("anuncios_unificados.csv", "codigo_ine"),
    ("anuncios_unificados.csv|fingerprint", None),
]:
    f = name.split("|")[0]
    df = csv(f)
    if col and col in df:
        codes = df[col].dropna().astype(str).str.strip()
        huerfanos = sorted(set(codes) - set(dim_codes))
        ref[f] = {
            "rows": len(df),
            "codigos": codes.nunique(),
            "sin_codigo": int(df[col].isna().sum()),
            "huerfanos_vs_dim": len(huerfanos),
            "ejemplos_huerfanos": huerfanos[:5],
            "municipios_del_dim_ausentes": len(set(dim_codes) - set(codes)),
        }
add("integridad_referencial", ref)

# -------------------------------- 6. coherencia de percentiles de alquiler
alq = csv("alquiler_municipal_completo.csv")
pct_cols = [c for c in alq.columns if re.search(r"_p(25|50|75)$|_mediana$", c)]
checks = {}
for base in ["renta_media_eur_m2", "cuantia_media_eur_mes", "superficie_media_m2"]:
    p25, p50, p75 = (num(alq.get(f"{base}_p25")), num(alq.get(f"{base}_mediana")), num(alq.get(f"{base}_p75")))
    if p25 is None or p50 is None or p75 is None:
        continue
    m = p25.notna() & p50.notna() & p75.notna()
    checks[base] = {
        "viola_p25_le_p50": int((p25[m] > p50[m]).sum()),
        "viola_p50_le_p75": int((p50[m] > p75[m]).sum()),
        "negativos": int((pd.concat([p25, p50, p75]) < 0).sum()),
        "ceros": int((pd.concat([p25, p50, p75]) == 0).sum()),
        "nulos": int(pd.concat([p25, p50, p75]).isna().sum()),
        "min": float(pd.concat([p25, p50, p75]).min()),
        "max": float(pd.concat([p25, p50, p75]).max()),
    }
add("alquiler_percentiles", {
    "rows": len(alq),
    "metodo_imputacion": alq["metodo_imputacion"].value_counts().to_dict(),
    "nivel_geografico": alq["nivel_geografico"].value_counts().to_dict() if "nivel_geografico" in alq else {},
    "checks": checks,
})

# ------------------------- 7. centinelas: ceros donde el nulo es lo correcto
ana = csv("analisis_variables_base.csv")
pct_like = [c for c in ana.columns if c.endswith("_pct") or c.startswith("esfuerzo_")]
sentinels = {}
for c in pct_like:
    s = num(ana[c])
    sentinels[c] = {
        "nulos": int(s.isna().sum()),
        "ceros_exactos": int((s == 0).sum()),
        "negativos": int((s < 0).sum()),
        "min": None if s.dropna().empty else round(float(s.min()), 2),
        "max": None if s.dropna().empty else round(float(s.max()), 2),
        "fuera_0_100": int(((s < 0) | (s > 100)).sum()),
    }
add("centinelas_pct", sentinels)

# ------------------------------------------- 8. anuncios: claves y extremos
anu = csv("anuncios_unificados.csv")
unif = {
    "rows": len(anu),
    "por_portal": anu["portal"].value_counts().to_dict(),
    "modalidad": anu["modalidad"].value_counts().to_dict() if "modalidad" in anu else {},
    "dup_portal_id": int(anu.duplicated(subset=["portal", "id_anuncio"]).sum()),
    "dup_fingerprint": int(anu["property_fingerprint"].duplicated().sum()) if "property_fingerprint" in anu else None,
    "precio": {
        "min": float(num(anu["precio_eur"]).min()),
        "max": float(num(anu["precio_eur"]).max()),
        "nulos": int(num(anu["precio_eur"]).isna().sum()),
        "cero_o_neg": int((num(anu["precio_eur"]) <= 0).sum()),
    },
    "superficie": {
        "min": float(num(anu["superficie_m2"]).min()),
        "max": float(num(anu["superficie_m2"]).max()),
        "nulos": int(num(anu["superficie_m2"]).isna().sum()),
        "menor_10m2": int((num(anu["superficie_m2"]) < 10).sum()),
        "mayor_1000m2": int((num(anu["superficie_m2"]) > 1000).sum()),
    },
    "habitaciones_min": float(num(anu["habitaciones"]).min()) if "habitaciones" in anu else None,
    "flags_outlier": anu["es_outlier_superficie"].value_counts().to_dict() if "es_outlier_superficie" in anu else {},
}
add("anuncios", unif)

# ------------------------------------- 9. cobertura: municipios sin soporte
cov = {}
if "n_anuncios" in dim:
    n = num(dim["n_anuncios"])
    cov["dim_n_anuncios_max"] = float(n.max())
    cov["dim_n_anuncios_suma"] = float(n.sum())
cov["anuncios_rows"] = len(anu)
cov["municipios_con_anuncio"] = anu["codigo_ine"].nunique()
cov["municipios_oficial_alquiler"] = int((alq["metodo_imputacion"] == "oficial").sum()) if "metodo_imputacion" in alq else None
cov["municipios_sin_anuncio"] = len(set(dim_codes) - set(anu["codigo_ine"].dropna()))
cov["municipios_imputados"] = int((alq["metodo_imputacion"] != "oficial").sum())
add("cobertura", cov)

# ------------------------------- 10. reproducibilidad / nombres volátiles
vol = [p.name for p in PROC.iterdir() if p.is_file() and re.search(r"_20\d{6}_\d{6}", p.name)]
gold = [p for p in PROC.glob("*unificad*")] + [p for p in PROC.glob("analisis_variables*")]
add("reproducibilidad", {
    "procesado_con_timestamp_en_nombre": vol,
    "n_con_timestamp": len(vol),
    "manifests_transform": [p.name for p in PROC.glob("*manifest*")],
    "gold_hashes": {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in gold if p.is_file()
    },
})

# ------------------------------------------- 11. escala: coste de lectura
t_read = time.monotonic()
_ = [csv(p.name) for p in PROC.glob("*.csv") if p.stat().st_size > 0]
add("escala", {
    "segundos_lectura_todos_los_csv_procesado": round(time.monotonic() - t_read, 2),
    "csv_procesado": len(list(PROC.glob("*.csv"))),
})

R["duracion_total_s"] = round(time.monotonic() - t0, 2)
OUT.write_text(json.dumps(R, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print(f"\nJSON -> {OUT}")
