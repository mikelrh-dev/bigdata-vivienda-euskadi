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

# Poblacion 16-24 estimada (T3 desempleo juvenil)
pop = pd.read_csv(RAW / "eustat_poblacion_edad.csv", dtype=str, encoding="utf-8-sig")
pop = pop[(pop["sexo__etiqueta"] == "Total") & (pop["periodo"] == pop["periodo"].max())]
pop0 = pop[pop["grandes grupos de edad cumplida__etiqueta"] == "0 - 19"][["ámbitos territoriales", "Población de la C.A. de Euskadi"]].rename(columns={"Población de la C.A. de Euskadi": "pob_0_19"})
pop1 = pop[pop["grandes grupos de edad cumplida__etiqueta"] == "20 - 64"][["ámbitos territoriales", "Población de la C.A. de Euskadi"]].rename(columns={"Población de la C.A. de Euskadi": "pob_20_64"})
popm = pop0.merge(pop1, on="ámbitos territoriales")
popm["codigo_ine"] = popm["ámbitos territoriales"].astype(str).str.zfill(5)
popm = popm[popm["codigo_ine"].str.len() == 5]
popm["pob_0_19"] = pd.to_numeric(popm["pob_0_19"], errors="coerce")
popm["pob_20_64"] = pd.to_numeric(popm["pob_20_64"], errors="coerce")
popm["poblacion_16_24_estimada"] = popm["pob_0_19"] * (4 / 20) + popm["pob_20_64"] * (5 / 45)
popm = popm[["codigo_ine", "poblacion_16_24_estimada"]]

# Lanbide paro joven
paro_j = pd.read_csv(RAW / "lanbide_paro_juvenil.csv", dtype=str, encoding="utf-8-sig")
paro_j["codigo_ine"] = paro_j["codigo_ine"].astype(str).str.zfill(5)
paro_j["paro_joven_menores_25"] = pd.to_numeric(paro_j["paro_joven_menores_25"], errors="coerce")
paro_j = paro_j[["codigo_ine", "paro_joven_menores_25"]]

base = base.merge(popm, on="codigo_ine", how="left")
base = base.merge(paro_j, on="codigo_ine", how="left")
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
            "cuantia_media_eur_mes_media", "superficie_media_m2_media",
            "poblacion_16_24_estimada", "paro_joven_menores_25"]
for c in num_cols:
    if c in base.columns:
        base[c] = pd.to_numeric(base[c], errors="coerce")

# alquiler anual y esfuerzo
base["alquiler_anual"] = base["cuantia_media_eur_mes_media"] * 12
base["esfuerzo_renta_hogar"] = base["alquiler_anual"] / base["renta_hogar"]
base["esfuerzo_renta_eustat"] = base["alquiler_anual"] / base["renta_eustat"]
base["esfuerzo_renta_joven"] = base["alquiler_anual"] / base["renta_joven_estimada_16_29"]

# T3 desempleo juvenil real con mitigaciones
base["ocupados_16_24"] = base["poblacion_16_24_estimada"] * (base["tasa_ocupacion_juvenil_16_24_pct"] / 100.0)
base["activos_16_24"] = base["ocupados_16_24"] + base["paro_joven_menores_25"]
base["tasa_desempleo_juvenil_real_pct"] = None
mask = base["activos_16_24"] >= 20
base.loc[mask, "tasa_desempleo_juvenil_real_pct"] = (
    base.loc[mask, "paro_joven_menores_25"] / base.loc[mask, "activos_16_24"] * 100.0
)
base["tasa_desempleo_juvenil_real_pct"] = base["tasa_desempleo_juvenil_real_pct"].clip(0, 100)
# sanity: no mayor que 4x paro lanbide
if "tasa_paro_lanbide_pct" in base.columns:
    cap = base["tasa_paro_lanbide_pct"] * 4
    m = base["tasa_desempleo_juvenil_real_pct"].notna() & cap.notna()
    base.loc[m, "tasa_desempleo_juvenil_real_pct"] = base.loc[m, "tasa_desempleo_juvenil_real_pct"].clip(upper=cap[m])
cols = ["codigo_ine", "nombre_canonico", "territorio", "tipologia_mercado", "n_anuncios",
        "tiene_alquiler_oficial", "renta_eustat", "renta_hogar", "renta_atlas",
        "renta_joven_estimada_16_29", "tasa_actividad_pct", "tasa_ocupacion_pct",
        "tasa_paro_lanbide_pct", "tasa_ocupacion_juvenil_16_24_pct", "trabaja_fuera_pct",
        "afiliacion_ss_16_24_pct", "renta_familiar_eur", "renta_personal_total_eur",
        "renta_personal_disponible_eur", "superficie_media_m2", "antiguedad_media_anyos",
        "dist_bilbao_km", "dist_donostia_km", "dist_vitoria_km", "capital_mas_cercana",
        "dist_centroide_comarca_km", "renta_media_eur_m2_media", "cuantia_media_eur_mes_media",
        "superficie_media_m2_media", "alquiler_anual", "esfuerzo_renta_hogar",
        "esfuerzo_renta_eustat", "esfuerzo_renta_joven",
        "poblacion_16_24_estimada", "paro_joven_menores_25", "ocupados_16_24",
        "activos_16_24", "tasa_desempleo_juvenil_real_pct"]
base = base[cols]

dest = PROC / "analisis_variables_base.csv"
base.to_csv(dest, index=False, encoding="utf-8-sig")
print("Generado " + str(dest) + ": " + str(len(base)) + " filas, " + str(len(base.columns)) + " cols")
