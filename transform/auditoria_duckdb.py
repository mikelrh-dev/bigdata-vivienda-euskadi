"""Auditoria de datos con DuckDB sobre data/procesado/.

Genera scratchpad/auditoria_duckdb.md con:
- Filas/columnas por archivo
- Nulos por columna (top)
- Duplicados por clave
- Rangos min/max de variables numericas
- Consistencia entre archivos (joins por codigo_ine)
- Outliers (>3 sigma)

Uso: python transform/auditoria_duckdb.py
"""
from __future__ import annotations

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "procesado"
OUT = PROJECT_ROOT / "scratchpad" / "auditoria_duckdb.md"

lines = []
lines.append("# Auditoria de datos con DuckDB\n")
lines.append(f"**Fecha:** generada automaticamente\n")
lines.append(f"**Directorio:** data/procesado/\n\n")


def q(sql):
    return duckdb.query(sql).df()


# 1. Inventario
lines.append("## 1. Inventario de archivos\n")
lines.append("| Archivo | Filas | Columnas |\n|---|---|---|\n")
csvs = sorted(PROC.glob("*.csv"))
for p in csvs:
    try:
        df = q(f"SELECT * FROM read_csv_auto('{p.as_posix()}')")
        lines.append(f"| {p.name} | {len(df)} | {len(df.columns)} |\n")
    except Exception as e:
        lines.append(f"| {p.name} | ERROR | {e} |\n")
lines.append(f"\nTotal: {len(csvs)} archivos\n\n")

# 2. Nulos por archivo (top 5 columnas con mas nulos)
lines.append("## 2. Nulos por archivo (columnas con nulos)\n")
for p in csvs:
    try:
        df = q(f"SELECT * FROM read_csv_auto('{p.as_posix()}')")
        nulls = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().sum() > 0}
        if nulls:
            lines.append(f"### {p.name}\n")
            for c, n in sorted(nulls.items(), key=lambda x: -x[1])[:10]:
                lines.append(f"- `{c}`: {n} nulos\n")
            lines.append("\n")
    except Exception:
        pass

# 3. Duplicados por clave
lines.append("## 3. Duplicados por clave\n")
for p in csvs:
    try:
        df = q(f"SELECT * FROM read_csv_auto('{p.as_posix()}')")
        for key in ["codigo_ine", "id_anuncio", "municipio"]:
            if key in df.columns:
                dup = int(df[key].duplicated().sum())
                if dup > 0:
                    lines.append(f"- `{p.name}` / `{key}`: {dup} duplicados\n")
    except Exception:
        pass
lines.append("\n")

# 4. Rangos de variables clave
lines.append("## 4. Rangos de variables clave\n")
lines.append("| Archivo | Columna | Min | Max | Media |\n|---|---|---|---|---|\n")
vars_clave = ["precio_eur", "superficie_m2", "renta_personal_total_eur",
              "cuantia_media_eur_mes_media", "esfuerzo_min_pct", "esfuerzo_max_pct",
              "n_paradas", "paradas_por_1000_hab", "dist_centroide_comarca_km"]
for p in csvs:
    try:
        df = q(f"SELECT * FROM read_csv_auto('{p.as_posix()}')")
        for v in vars_clave:
            if v in df.columns:
                mn = df[v].min()
                mx = df[v].max()
                mean = round(df[v].mean(), 2)
                lines.append(f"| {p.name} | {v} | {mn} | {mx} | {mean} |\n")
    except Exception:
        pass
lines.append("\n")

# 5. Consistencia entre archivos (joins por codigo_ine)
lines.append("## 5. Consistencia entre archivos (joins por codigo_ine)\n")
base = "analisis_variables_base.csv"
base_path = (PROC / base).as_posix()
try:
    base_df = q(f"SELECT codigo_ine FROM read_csv_auto('{base_path}')")
    n_base = len(base_df)
    lines.append(f"Base: `{base}` = {n_base} municipios\n\n")
    for p in csvs:
        if p.name == base:
            continue
        try:
            df = q(f"SELECT * FROM read_csv_auto('{p.as_posix()}')")
            if "codigo_ine" in df.columns:
                common = len(set(base_df["codigo_ine"]) & set(df["codigo_ine"]))
                lines.append(f"- `{p.name}`: {common}/{n_base} municipios coinciden ({len(df)} filas)\n")
        except Exception:
            pass
except Exception as e:
    lines.append(f"Error: {e}\n")
lines.append("\n")

# 6. Outliers (>3 sigma) en variables clave
lines.append("## 6. Outliers (>3 sigma) en variables clave\n")
for p in csvs:
    try:
        df = q(f"SELECT * FROM read_csv_auto('{p.as_posix()}')")
        for v in vars_clave:
            if v in df.columns and df[v].dtype in ("float64", "int64", "float32", "int32"):
                mean = df[v].mean()
                std = df[v].std()
                if std and std > 0:
                    outliers = df[(df[v] > mean + 3 * std) | (df[v] < mean - 3 * std)]
                    if len(outliers) > 0:
                        lines.append(f"- `{p.name}` / `{v}`: {len(outliers)} outliers (min={df[v].min()}, max={df[v].max()})\n")
    except Exception:
        pass
lines.append("\n")

# 7. Resumen
lines.append("## 7. Resumen\n")
lines.append(f"- Archivos auditados: {len(csvs)}\n")
lines.append(f"- Generado con DuckDB (sin cargar en RAM)\n")
lines.append(f"- Regenerable: `python transform/auditoria_duckdb.py`\n")

OUT.write_text("".join(lines), encoding="utf-8")
print(f"OK: {OUT}")
print(f"Archivos auditados: {len(csvs)}")
