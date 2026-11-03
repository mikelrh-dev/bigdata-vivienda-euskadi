# -*- coding: utf-8 -*-
"""Auditoría de solo lectura (2026-10-29). No modifica data/.

Ejecutar desde la raíz: .venv/Scripts/python.exe scratchpad/auditoria_2026_10_29.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "procesado"
RES = ROOT / "data" / "resultados"


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def read(name, base=RAW, **kw):
    return pd.read_csv(base / name, dtype=str, encoding="utf-8-sig", low_memory=False, **kw)


def num(s):
    return pd.to_numeric(s, errors="coerce")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ── 1. Inventario ─────────────────────────────────────────────────
hr("1. INVENTARIO")
for base in (RAW, PROC):
    files = [p for p in base.rglob("*") if p.is_file()]
    by_ext = {}
    for p in files:
        by_ext[p.suffix.lower()] = by_ext.get(p.suffix.lower(), 0) + 1
    size = sum(p.stat().st_size for p in files) / 1e6
    print(f"{base.name}: {len(files)} archivos, {size:.1f} MB, {by_ext}")

dim = read("dim_municipios.csv")
print(f"dim_municipios: {len(dim)} filas, duplicados codigo_ine={dim['codigo_ine'].duplicated().sum()}")
print("territorios:", dim["territorio"].value_counts().to_dict())

# ── 2. Manifest ───────────────────────────────────────────────────
hr("2. MANIFEST E INTEGRIDAD RAW")
manifest_candidates = [ROOT / "docs" / "raw_manifest_sha256.txt",
                       RAW / "manifest_sha256.txt"]
for m in manifest_candidates:
    if not m.exists():
        print(f"FALTA manifest: {m}")
        continue
    lines = [ln.strip() for ln in m.read_text(encoding="utf-8").splitlines() if ln.strip()]
    print(f"\n{m.relative_to(ROOT)}: {len(lines)} entradas")
    missing, bad = [], []
    seen = set()
    for ln in lines:
        parts = ln.split(None, 1)
        if len(parts) != 2:
            bad.append(("malformada", ln[:60]))
            continue
        h, rest = parts
        rel = rest.lstrip("* ").strip()
        seen.add(rel)
        f = RAW / rel
        if not f.exists():
            missing.append(rel)
        elif sha256(f) != h:
            bad.append(("hash", rel))
    disk = {p.relative_to(RAW).as_posix() for p in RAW.rglob("*") if p.is_file()
            and p.name not in {"manifest_sha256.txt", ".FROZEN", "ingestion_manifest.json"}}
    extra = sorted(disk - seen)
    print(f"  faltantes={len(missing)} hash_distinto={len(bad)} en_disco_no_listados={len(extra)}")
    if missing[:8]:
        print("  faltan:", missing[:8])
    if bad[:8]:
        print("  malos:", bad[:8])
    if extra[:8]:
        print("  extra:", extra[:8])

# ── 3. Entity resolution ──────────────────────────────────────────
hr("3. ENTITY RESOLUTION (codigo_ine)")
valid_codes = set(dim["codigo_ine"].astype(str).str.zfill(5))
tables = {
    "raw/alquiler_municipal.csv": read("alquiler_municipal.csv"),
    "raw/renta_municipal_completa.csv": read("renta_municipal_completa.csv"),
    "raw/anuncios_fotocasa.csv": read("anuncios_fotocasa.csv"),
    "raw/anuncios_pisos.csv": read("anuncios_pisos.csv"),
    "raw/anuncios_realtyapi.csv": read("anuncios_realtyapi.csv"),
    "proc/anuncios_unificados.csv": read("anuncios_unificados.csv", PROC),
    "proc/alquiler_municipal_completo.csv": read("alquiler_municipal_completo.csv", PROC),
    "proc/dim_municipios_enriquecido.csv": read("dim_municipios_enriquecido.csv", PROC),
    "raw/udalmap_empleo_corregido.csv": read("udalmap_empleo_corregido.csv"),
    "raw/transporte_paradas_municipio.csv": read("transporte_paradas_municipio.csv"),
    "raw/distancias_capitales.csv": read("distancias_capitales.csv"),
    "raw/areas_funcionales_municipios.csv": read("areas_funcionales_municipios.csv"),
}
for name, df in tables.items():
    if "codigo_ine" not in df.columns:
        print(f"{name}: SIN codigo_ine")
        continue
    c = df["codigo_ine"].astype(str).str.strip()
    c5 = c.str.zfill(5)
    print(f"{name}: filas={len(df)} nulls={c.isna().sum()} len5={int((c5.str.len()==5).sum())} "
          f"prefijo_ok={int(c5.str[:2].isin(['01','20','48']).sum())} "
          f"no_en_dim={int((~c5.isin(valid_codes)).sum())} municipios={c5.nunique()}")

# ── 4. Anuncios ───────────────────────────────────────────────────
hr("4. ANUNCIOS: VOLUMEN, CALIDAD, COBERTURA")
an = read("anuncios_unificados.csv", PROC)
an["precio"] = num(an["precio_eur"])
an["sup"] = num(an["superficie_m2"])
an["hab"] = num(an["habitaciones"])
an["pm2"] = an["precio"] / an["sup"]
print("por portal:\n", an.groupby("portal").size().to_string())
print("por modalidad:\n", an.groupby("modalidad").size().to_string())
print(f"precio nulo/<=0: {(an['precio'].isna() | (an['precio']<=0)).sum()}")
print(f"superficie nula: {an['sup'].isna().sum()}  fuera 10-600: {((an['sup']<10)|(an['sup']>600)).sum()}")
print(f"habitaciones nulas: {an['hab'].isna().sum()}  pm2 calculable: {an['pm2'].notna().sum()}")
print("pm2 describe:\n", an["pm2"].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).round(2).to_string())
print("precio describe:\n", an["precio"].describe(percentiles=[.01,.5,.99]).round(0).to_string())
print("superficie top:", an["sup"].nlargest(5).tolist())

dup_id = an.duplicated(subset=["portal", "id_anuncio"]).sum()
dup_full = an.duplicated(subset=["portal", "codigo_ine", "precio_eur", "superficie_m2", "habitaciones"]).sum()
print(f"duplicados (portal,id)={dup_id}  (portal,ine,precio,sup,hab)={dup_full}")

counts = an.groupby("codigo_ine").size().sort_values(ascending=False)
print(f"municipios con anuncios={len(counts)}/252; n>=30={int((counts>=30).sum())}; "
      f"5-29={int(((counts>=5)&(counts<30)).sum())}; 1-4={int(((counts>=1)&(counts<5)).sum())}; 0={252-len(counts)}")
print("top10:\n", counts.head(10).to_string())
print("n>=30:", counts[counts>=30].to_dict())

# outliers pm2 por portal
for portal, g in an.groupby("portal"):
    q1, q3 = g["pm2"].quantile([.25, .75])
    iqr = q3 - q1
    out = g[(g["pm2"] < q1 - 1.5*iqr) | (g["pm2"] > q3 + 1.5*iqr)]
    print(f"{portal}: n={len(g)} pm2 mediana={g['pm2'].median():.2f} "
          f"limites=({q1-1.5*iqr:.2f},{q3+1.5*iqr:.2f}) outliers={len(out)}")

# temporal vs larga
fot = read("anuncios_fotocasa.csv")
fot["precio"] = num(fot["precio_eur"]); fot["sup"] = num(fot["superficie_m2"])
fot["pm2"] = fot["precio"]/fot["sup"]
fot["temp"] = fot["alquiler_temporal"].astype(str).str.lower().isin(["true","1","yes"])
print("\nFotocasa raw:", len(fot), "temporal:", int(fot["temp"].sum()), "larga:", int((~fot["temp"]).sum()))
print(f"  pm2 temporal mediana={fot.loc[fot['temp'],'pm2'].median():.2f} n={fot.loc[fot['temp'],'pm2'].notna().sum()}")
print(f"  pm2 larga mediana={fot.loc[~fot['temp'],'pm2'].median():.2f} n={fot.loc[~fot['temp'],'pm2'].notna().sum()}")
print("  anio_fuente:", fot["anio_fuente"].value_counts().to_dict())

# ── 5. Alquiler oficial e imputación ──────────────────────────────
hr("5. ALQUILER: OFICIAL, IDW Y CALIDAD")
alq = read("alquiler_municipal.csv")
alq["m2"] = num(alq["renta_media_eur_m2_media"]); alq["mes"] = num(alq["cuantia_media_eur_mes_media"])
print(f"raw filas={len(alq)} municipios={alq['municipio'].nunique()} duplicados_municipio={alq['municipio'].duplicated().sum()}")
print("distritos:", alq["distrito"].value_counts().head(8).to_dict())
print("territorios:", alq["territorio"].value_counts().to_dict())
print("m2 describe:\n", alq["m2"].describe(percentiles=[.05,.5,.95]).round(2).to_string())

comp = read("alquiler_municipal_completo.csv", PROC)
comp["m2"] = num(comp["renta_media_eur_m2_media"]); comp["mes"] = num(comp["cuantia_media_eur_mes_media"])
print("\ncompleto:", len(comp), "municipios", comp["codigo_ine"].nunique())
print(comp["metodo_imputacion"].value_counts().to_dict())
print("nivel_geografico:", comp["nivel_geografico"].value_counts().to_dict())
print("m2 por metodo:\n", comp.groupby("metodo_imputacion")["m2"].describe(percentiles=[.5]).round(2).to_string())
print("mes por metodo:\n", comp.groupby("metodo_imputacion")["mes"].describe(percentiles=[.5]).round(2).to_string())
print("duplicados codigo:", comp["codigo_ine"].duplicated().sum())
print("idw_vecinos ejemplo:", comp.loc[comp["metodo_imputacion"]!="oficial","idw_vecinos"].head(3).tolist())

# ── 6. Renta, esfuerzo, correlación ───────────────────────────────
hr("6. RENTA, ESFUERZO Y CORRELACIÓN")
rc = read("renta_municipal_completa.csv")
print("renta completa:", len(rc), "origen:", rc["renta_origen"].value_counts().to_dict())
for col in ["renta_eustat", "renta_atlas", "renta_joven_estimada_16_29", "renta_hogar"]:
    print(f"  {col}: nulls={num(rc[col]).isna().sum()} min={num(rc[col]).min():.0f} max={num(rc[col]).max():.0f}")
print("anio_renta:", rc["anio_renta"].value_counts().to_dict())

enr = read("dim_municipios_enriquecido.csv", PROC)
numcols = ["renta_personal_total_eur", "cuantia_media_eur_mes_media", "esfuerzo_ovj_individual_pct",
           "esfuerzo_ajustado_pct", "esfuerzo_min_pct", "esfuerzo_max_pct",
           "tasa_paro_lanbide_pct", "tasa_desempleo_juvenil_real_pct",
           "salario_joven_ajustado_local_eur", "brecha_esfuerzo_genero_pp",
           "renta_media_eur_m2_media", "n_anuncios"]
print(f"\nenriquecido: {len(enr)} x {len(enr.columns)}")
for c in numcols:
    if c not in enr.columns:
        print(f"  {c}: NO EXISTE"); continue
    s = num(enr[c])
    print(f"  {c}: nulls={s.isna().sum()} min={s.min():.2f} p50={s.median():.2f} max={s.max():.2f}")

m = pd.DataFrame({"renta": num(enr["renta_personal_total_eur"]),
                  "alq_m2": num(enr["renta_media_eur_m2_media"]),
                  "alq_mes": num(enr["cuantia_media_eur_mes_media"]),
                  "oficial": enr["tiene_alquiler_oficial"].astype(str).str.lower().isin(["true","1"])})
for a, b in [("renta","alq_m2"), ("renta","alq_mes")]:
    print(f"Pearson {a} vs {b}: global={m[[a,b]].corr().iloc[0,1]:.3f} "
          f"oficial={m.loc[m['oficial'],[a,b]].corr().iloc[0,1]:.3f} "
          f"n={m[[a,b]].dropna().shape[0]}")

for c in ["esfuerzo_ovj_individual_pct", "esfuerzo_ajustado_pct", "esfuerzo_min_pct", "esfuerzo_max_pct"]:
    s = num(enr[c])
    print(f"{c}: >100%={int((s>100).sum())} >60%={int((s>60).sum())} <20%={int((s<20).sum())}")

# ── 7. Empleo, paro y coherencia ──────────────────────────────────
hr("7. EMPLEO Y PARO")
ud = read("udalmap_empleo_corregido.csv")
for c in ["tasa_actividad_pct","tasa_ocupacion_pct","tasa_paro_aprox_pct","tasa_paro_lanbide_pct",
          "tasa_ocupacion_juvenil_16_24_pct","renta_personal_total_eur","afiliacion_ss_16_24_pct"]:
    s = num(ud[c])
    print(f"{c}: nulls={s.isna().sum()} min={s.min():.2f} p50={s.median():.2f} max={s.max():.2f} neg={int((s<0).sum())} >100={int((s>100).sum())}")
print("tasa_paro_valida:", ud["tasa_paro_valida"].value_counts().to_dict())
print("nota_metodologica unicas:", ud["nota_metodologica"].nunique())

lan = read("lanbide_paro_juvenil.csv")
print("\nlanbide:", len(lan), "municipios", lan["codigo_ine"].nunique(), "anios", lan["anio"].unique().tolist())
print("tasa_paro_joven:", num(lan["tasa_paro_joven_pct"]).describe().round(2).to_dict())
# coherencia udalmap vs lanbide
lj = lan.copy(); lj["c"] = lj["codigo_ine"].str.zfill(5); lj["t"] = num(lj["tasa_paro_joven_pct"])
u = ud.copy(); u["c"] = u["codigo_ine"].str.zfill(5); u["t"] = num(u["tasa_paro_lanbide_pct"])
j = u[["c","t"]].merge(lj[["c","t"]], on="c", suffixes=("_udal","_lanbide"))
print(f"join udalmap-lanbide n={len(j)} correlacion={j[['t_udal','t_lanbide']].corr().iloc[0,1]:.3f} "
      f"dif_media={ (j['t_udal']-j['t_lanbide']).abs().mean():.2f} pp")

# ── 8. Geo, distancias, GTFS, ECVI, cert ─────────────────────────
hr("8. GEO / DISTANCIAS / GTFS / ECVI / CERT")
dc = read("distancias_capitales.csv")
print("distancias_capitales:", len(dc), "dup_codigo:", dc["codigo_ine"].duplicated().sum(),
      "nulls:", {c:int(dc[c].isna().sum()) for c in ["dist_bilbao_km","dist_donostia_km","dist_vitoria_km"]})
dc252 = read("distancias_capitales_252.csv")
print("distancias_capitales_252:", len(dc252), "dup:", dc252["codigo_ine"].duplicated().sum())

hv = read("distancias_haversine_252.csv")
hv["km"] = num(hv["km_haversine"])
print("haversine:", len(hv), "NaN km:", hv["km"].isna().sum(), "cero:", int((hv["km"]==0).sum()),
      "min/max:", hv["km"].min(), hv["km"].max())

geo = json.loads((RAW / "municipios_euskadi.geojson").read_text(encoding="utf-8"))
feats = geo.get("features", [])
coords = [c for f in feats for c in (f.get("geometry") or {}).get("coordinates", [])]
print("geojson features:", len(feats))

gt = read("transporte_paradas_municipio.csv")
gt["n"] = num(gt["n_paradas"]); gt["op"] = num(gt["n_operadores"])
print("gtfs:", len(gt), "municipios", gt["codigo_ine"].nunique(), "nulls n:", gt["n"].isna().sum(),
      "cero paradas:", int((gt["n"]==0).sum()), "op nulls:", gt["op"].isna().sum())

afm = read("areas_funcionales_municipios.csv")
print("areas_funcionales:", len(afm), "municipios", afm["codigo_ine"].nunique(), "areas", afm["area_funcional"].nunique())
ecvi = read("comparativa_compra_alquiler_af.csv", PROC)
print("comparativa AF:", len(ecvi), "n_municipios suma:", num(ecvi["n_municipios"]).sum())
maf = read("municipio_area_funcional_ecvi.csv", PROC)
print("municipio_area_funcional_ecvi:", len(maf), "con precio:", maf["precio_medio_total_eur"].notna().sum())

cert = read("cert_energetico_municipal_252.csv", PROC)
cert["n"] = num(cert["n_certificados"])
print("cert 252:", len(cert), "nulls n:", cert["n"].isna().sum(), "cero:", int((cert["n"]==0).sum()),
      "total certificados:", cert["n"].sum())

# ── 9. Años y procedencia ─────────────────────────────────────────
hr("9. AÑOS / PROCEDENCIA")
for name, base in [("anuncios_fotocasa.csv", RAW), ("anuncios_pisos.csv", RAW),
                   ("anuncios_realtyapi.csv", RAW), ("dim_municipios_enriquecido.csv", PROC)]:
    d = read(name, base)
    if "anio_fuente" in d.columns:
        print(name, "anio_fuente:", d["anio_fuente"].value_counts(dropna=False).to_dict())
print("anio_renta:", rc["anio_renta"].value_counts().to_dict())
print("anio_fuente udalmap:", ud["anio_fuente"].value_counts(dropna=False).to_dict())
print("certificados sin año; ECVI trimestres en comparativa:", ecvi.head(2).to_dict("records"))

# ── 10. Documentación vs realidad ────────────────────────────────
hr("10. DOCS vs REALIDAD")
import subprocess
tracked = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.splitlines()
print("archivos trackeados:", len(tracked))
for d in ["storage", "analysis", "visualization", "notebooks"]:
    print(f"  {d}/ existe: {(ROOT/d).exists()}")
print("README menciona tests 59:", "59 passed" in (ROOT/"README.md").read_text(encoding="utf-8"))
print("data/raw/ingestion_manifest.json existe:", (RAW/"ingestion_manifest.json").exists())
print("data/raw/.FROZEN existe:", (RAW/".FROZEN").exists())
