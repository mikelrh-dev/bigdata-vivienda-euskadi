"""Genera data/procesado/municipios_faltantes_93.csv a partir de fuentes raw/procesado.

Identifica los 93 municipios sin alquiler directo (nivel_geografico comarcal o
sin dato) y les asigna territorio, poblacion (Eustat 2025) y tipologia de mercado.

Regla bronce: solo lectura de raw/procesado existentes; escribe en procesado.
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "procesado"

# 1. Municipios sin alquiler directo
alq = pd.read_csv(PROC / "alquiler_municipal_completo.csv", dtype=str, encoding="utf-8-sig")
# Sin dato directo = renta_media_eur_m2_media vacio o nivel_geografico != municipal
sin = alq[
    alq["renta_media_eur_m2_media"].isna()
    | (alq["nivel_geografico"].fillna("").str.lower() != "municipal")
].copy()

dim = pd.read_csv(PROC / "dim_municipios.csv", dtype=str, encoding="utf-8-sig")
sin = sin.merge(
    dim[["codigo_ine", "nombre_canonico", "territorio", "tipologia_mercado"]],
    on="codigo_ine", how="left", suffixes=("", "_dim"),
)
# Preferir nombre_canonico de dim si falta
if "nombre_canonico_dim" in sin.columns:
    sin["nombre_canonico"] = sin["nombre_canonico"].fillna(sin["nombre_canonico_dim"])
    sin = sin.drop(columns=["nombre_canonico_dim"])

# 2. Poblacion Eustat 2025 (Total, Total)
pob = pd.read_csv(RAW / "eustat_poblacion_edad.csv", dtype=str, encoding="utf-8-sig")
pob = pob[
    (pob["grandes grupos de edad cumplida__etiqueta"] == "Total")
    & (pob["sexo__etiqueta"] == "Total")
    & (pob["periodo__etiqueta"] == "2024/01/01")
][["ámbitos territoriales", "Población de la C.A. de Euskadi"]].copy()
pob["codigo_ine"] = pob["ámbitos territoriales"].astype(str).str.zfill(5)
pob["poblacion"] = pd.to_numeric(pob["Población de la C.A. de Euskadi"], errors="coerce")
pob = pob[["codigo_ine", "poblacion"]]
sin = sin.merge(pob, on="codigo_ine", how="left")

# 3. Salida ordenada
out = sin[["codigo_ine", "nombre_canonico", "territorio", "poblacion", "tipologia_mercado"]].copy()
out["codigo_ine"] = out["codigo_ine"].astype(str).str.zfill(5)
out["poblacion"] = out["poblacion"].astype("Int64")
out = out.sort_values("codigo_ine").reset_index(drop=True)

dest = PROC / "municipios_faltantes_93.csv"
out.to_csv(dest, index=False, encoding="utf-8-sig")
print(f"Generado {dest}: {len(out)} filas")
print(out.head(3).to_string(index=False))
