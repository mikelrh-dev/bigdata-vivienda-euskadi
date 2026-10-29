# Genera data/procesado/analisis_variables_base.csv
# Merge de dim_municipios + renta + empleo + distancias + alquiler.
# Basado en scratchpad/analysis.py, adaptado para leer de raw/procesado.
# Regla bronce: solo lectura; escribe en procesado.

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "procesado"

def loadcsv(path):
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig")

dim = loadcsv(PROC / "dim_municipios.csv")
rc = loadcsv(RAW / "renta_municipal_completa.csv")
alq = loadcsv(PROC / "alquiler_municipal_completo.csv")
dc = loadcsv(RAW / "distancias_capitales_252.csv")
ud = loadcsv(RAW / "udalmap_empleo_corregido.csv")

# normalize codes
for df in (dim, rc, dc, ud):
    if "codigo_ine" in df.columns:
        df["codigo_ine"] = df["codigo_ine"].astype(str).str.zfill(5)
alq["codigo_ine"] = alq["codigo_ine"].astype(str).str.zfill(5)

# Merge base
base = dim[["codigo_ine", "nombre_canonico", "territorio", "tipologia_mercado",
            "n_anuncios", "tiene_alquiler_oficial"]].copy()
base = base.merge(rc[["codigo_ine", "renta_eustat", "renta_hogar", "renta_atlas",
                      "renta_joven_estimada_16_29"]],
                  on="codigo_ine", how="left")
base = base.merge(ud[["codigo_ine", "tasa_actividad_pct", "tasa_ocupacion_pct",
                      "tasa_paro_lanbide_pct", "tasa_ocupacion_juvenil_16_24_pct",
                      "trabaja_fuera_pct", "afiliacion_ss_16_24_pct",
                      "renta_familiar_eur", "renta_personal_total_eur",
                      "renta_personal_disponible_eur", "superficie_media_m2",
                      "antiguedad_media_anyos"]],
                  on="codigo_ine", how="left")
base = base.merge(dc[["codigo_ine", "dist_bilbao_km", "dist_donostia_km",
                      "dist_vitoria_km", "capital_mas_cercana",
                      "dist_centroide_comarca_km"]],
                  on="codigo_ine", how="left")

# alquiler municipal: first row per municipio
alq1 = alq.drop_duplicates("codigo_ine", keep="first")
base = base.merge(alq1[["codigo_ine", "renta_media_eur_m2_media",
                        "cuantia_media_eur_mes_media", "superficie_media_m2_media"]],
                  on="codigo_ine", how="left", suffixes=("", "_alq"))

# numeric
num_cols = ["renta_eustat", "renta_hogar", "renta_atlas", "renta_joven_estimada_16_29",
            "tasa_actividad_pct", "tasa_ocupacion_pct", "tasa_paro_lanbide_pct",
            "tasa_ocupacion_juvenil_16_24_pct", "trabaja_fuera_pct",
            "afiliacion_ss_16_24_pct", "renta_familiar_eur", "renta_personal_total_eur",
            "renta_personal_disponible_eur", "superficie_media_m2", "antiguedad_media_anyos",
            "dist_bilbao_km", "dist_donostia_km", "dist_vitoria_km",
            "dist_centroide_comarca_km", "renta_media_eur_m2_media",
            "cuantia_media_eur_mes_media", "superficie_media_m2_media"]
for c in num_cols:
    if c in base.columns:
        base[c] = pd.to_numeric(base[c], errors="coerce")

# alquiler anual y esfuerzo
base["alquiler_anual"] = base["cuantia_media_eur_mes_media"] * 12
base["esfuerzo_renta_hogar"] = base["alquiler_anual"] / base["renta_hogar"]
base["esfuerzo_renta_eustat"] = base["alquiler_anual"] / base["renta_eustat"]
base["esfuerzo_renta_joven"] = base["alquiler_anual"] / base["renta_joven_estimada_16_29"]

# ordenar columnas como pre_silver
cols = ["codigo_ine", "nombre_canonico", "territorio", "tipologia_mercado", "n_anuncios",
        "tiene_alquiler_oficial", "renta_eustat", "renta_hogar", "renta_atlas",
        "renta_joven_estimada_16_29", "tasa_actividad_pct", "tasa_ocupacion_pct",
        "tasa_paro_lanbide_pct", "tasa_ocupacion_juvenil_16_24_pct", "trabaja_fuera_pct",
        "afiliacion_ss_16_24_pct", "renta_familiar_eur", "renta_personal_total_eur",
        "renta_personal_disponible_eur", "superficie_media_m2", "antiguedad_media_anyos",
        "dist_bilbao_km", "dist_donostia_km", "dist_vitoria_km", "capital_mas_cercana",
        "dist_centroide_comarca_km", "renta_media_eur_m2_media", "cuantia_media_eur_mes_media",
        "superficie_media_m2_media", "alquiler_anual", "esfuerzo_renta_hogar",
        "esfuerzo_renta_eustat", "esfuerzo_renta_joven"]
base = base[cols]

dest = PROC / "analisis_variables_base.csv"
base.to_csv(dest, index=False, encoding="utf-8-sig")
print("Generado " + str(dest) + ": " + str(len(base)) + " filas, " + str(len(base.columns)) + " cols")
