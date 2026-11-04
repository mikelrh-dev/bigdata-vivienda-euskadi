# Genera data/procesado/analisis_variables_base.csv
# Merge de dim_municipios + renta + empleo + distancias + alquiler.
# Basado en scratchpad/analysis.py, adaptado para leer de raw/procesado.
# Regla bronce: solo lectura; escribe en procesado.

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "procesado"


def _ratios_18_34_desde_eustat() -> tuple[dict, str]:
    """Ratios 18-34 ponderados por anchura desde eustat_renta_edad.csv (CAE 2024).

    Espejo de transform/calcular_renta_joven.py (misma fuente, mismo fallback).
    Retorna (dict ratio_18_34/ratio_18_24/ratio_25_34, flag calculado|fallback).
    """
    df = pd.read_csv(RAW / "eustat_renta_edad.csv", dtype=str, encoding="utf-8-sig")
    d = df[(df["sexo__etiqueta"] == "Total") & (df["tipo de renta__etiqueta"] == "Renta total")]
    d = d[d["periodo"].astype(str) == "2024"]
    tramos: dict = {}
    for _, row in d.iterrows():
        etiqueta = str(row["edad__etiqueta"]).strip()
        valor = row["Renta personal media de la C.A. de Euskadi (euros)"]
        tramos[etiqueta] = valor

    def _get(*claves: str):
        for k in claves:
            if k in tramos and tramos[k] is not None and str(tramos[k]).strip() != "":
                return tramos[k]
        return None

    r18_19 = _get("18 - 19 años", "De 18 a 19 años", "18 a 19 años")
    r20_24 = _get("20 - 24 años", "De 20 a 24 años", "20 a 24 años")
    r25_29 = _get("25 - 29 años", "De 25 a 29 años", "25 a 29 años")
    r30_34 = _get("30 - 34 años", "De 30 a 34 años", "30 a 34 años")
    rtotal = _get("Total", "Total (todas las edades)")
    vals = (r18_19, r20_24, r25_29, r30_34, rtotal)
    if any(v is None for v in vals):
        v = (1599.0, 8156.0, 20109.0, 25609.0, 28170.0)
        return {
            "ratio_18_34": (2 * v[0] + 5 * v[1] + 5 * v[2] + 5 * v[3]) / 17 / v[4],
            "ratio_18_24": (2 * v[0] + 5 * v[1]) / 7 / v[4],
            "ratio_25_34": (5 * v[2] + 5 * v[3]) / 10 / v[4],
        }, "fallback"
    try:
        n = [float(str(x).replace(".", "").replace(",", ".")) for x in vals]
    except (TypeError, ValueError):
        v = (1599.0, 8156.0, 20109.0, 25609.0, 28170.0)
        return {
            "ratio_18_34": (2 * v[0] + 5 * v[1] + 5 * v[2] + 5 * v[3]) / 17 / v[4],
            "ratio_18_24": (2 * v[0] + 5 * v[1]) / 7 / v[4],
            "ratio_25_34": (5 * v[2] + 5 * v[3]) / 10 / v[4],
        }, "fallback"
    return {
        "ratio_18_34": (2 * n[0] + 5 * n[1] + 5 * n[2] + 5 * n[3]) / 17 / n[4],
        "ratio_18_24": (2 * n[0] + 5 * n[1]) / 7 / n[4],
        "ratio_25_34": (5 * n[2] + 5 * n[3]) / 10 / n[4],
    }, "calculado"

def loadcsv(path):
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig")

dim = loadcsv(PROC / "dim_municipios.csv")
rc = loadcsv(RAW / "renta_municipal_completa.csv")
alq = loadcsv(PROC / "alquiler_municipal_completo.csv")
dc = loadcsv(RAW / "distancias_capitales_252.csv")
# WP-04/C-03: se lee la copia de PROCESADO, no el duplicado congelado de raw.
ud = loadcsv(PROC / "udalmap_empleo_corregido.csv")

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
                      "tasa_paro_lanbide_pct", "tasa_paro_valida",
                      "tasa_ocupacion_juvenil_16_24_pct",
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

# alquiler anual y esfuerzo (WP-06: todo en % de la renta anual; el canonico
# 18-34 es esfuerzo_joven_pct_18_34, de base municipal. El legacy 16-29
# esfuerzo_joven_pct se conserva. El salario OVJ es referencia, no ranking.)
base["alquiler_anual"] = base["cuantia_media_eur_mes_media"] * 12
base["esfuerzo_hogar_pct"] = (base["alquiler_anual"] / base["renta_hogar"] * 100).round(1)
base["esfuerzo_eustat_pct"] = (base["alquiler_anual"] / base["renta_eustat"] * 100).round(1)
base["esfuerzo_joven_pct"] = (base["alquiler_anual"] / base["renta_joven_estimada_16_29"] * 100).round(1)
# JOVEN-18-34: ponderada por anchura, escalares CAE sobre renta_hogar (misma base
# municipal que el legacy, para comparabilidad). Subgrupos CAE, no municipales.
_ratios, _flag_18_34 = _ratios_18_34_desde_eustat()
base["renta_joven_estimada_18_34"] = (base["renta_hogar"] * _ratios["ratio_18_34"]).round(1)
base["renta_joven_estimada_18_24"] = (base["renta_hogar"] * _ratios["ratio_18_24"]).round(1)
base["renta_joven_estimada_25_34"] = (base["renta_hogar"] * _ratios["ratio_25_34"]).round(1)
base["esfuerzo_joven_pct_18_34"] = (base["alquiler_anual"] / base["renta_joven_estimada_18_34"] * 100).round(1)
base["esfuerzo_joven_pct_18_24"] = (base["alquiler_anual"] / base["renta_joven_estimada_18_24"] * 100).round(1)
base["esfuerzo_joven_pct_25_34"] = (base["alquiler_anual"] / base["renta_joven_estimada_25_34"] * 100).round(1)
base["esfuerzo_joven_pct_16_29"] = base["esfuerzo_joven_pct"]
base["ratio_fiscal_18_34"] = _ratios["ratio_18_34"]
base["ratio_fiscal_18_24"] = _ratios["ratio_18_24"]
base["ratio_fiscal_25_34"] = _ratios["ratio_25_34"]
base["flag_ratio_fiscal_18_34"] = _flag_18_34

# T3 desempleo juvenil real con mitigaciones
base["ocupados_16_24"] = base["poblacion_16_24_estimada"] * (base["tasa_ocupacion_juvenil_16_24_pct"] / 100.0)
base["activos_16_24"] = base["ocupados_16_24"] + base["paro_joven_menores_25"]
base["tasa_desempleo_juvenil_real_pct"] = None
mask = base["activos_16_24"] >= 20
base.loc[mask, "tasa_desempleo_juvenil_real_pct"] = (
    base.loc[mask, "paro_joven_menores_25"] / base.loc[mask, "activos_16_24"] * 100.0
)
base["tasa_desempleo_juvenil_real_pct"] = base["tasa_desempleo_juvenil_real_pct"].clip(0, 100)
# sanity: no mayor que 4x paro lanbide. WP-04: nunca recortar contra un cap
# nulo o cero (un techo de 0 anularia un valor calculado correctamente).
if "tasa_paro_lanbide_pct" in base.columns:
    cap = base["tasa_paro_lanbide_pct"] * 4
    m = base["tasa_desempleo_juvenil_real_pct"].notna() & cap.gt(0)
    base.loc[m, "tasa_desempleo_juvenil_real_pct"] = base.loc[m, "tasa_desempleo_juvenil_real_pct"].clip(upper=cap[m])
cols = ["codigo_ine", "nombre_canonico", "territorio", "tipologia_mercado", "n_anuncios",
        "tiene_alquiler_oficial", "renta_eustat", "renta_hogar", "renta_atlas",
        "renta_joven_estimada_16_29", "renta_joven_estimada_18_34",
        "renta_joven_estimada_18_24", "renta_joven_estimada_25_34",
        "ratio_fiscal_18_34", "ratio_fiscal_18_24", "ratio_fiscal_25_34",
        "flag_ratio_fiscal_18_34", "tasa_actividad_pct", "tasa_ocupacion_pct",
        "tasa_paro_lanbide_pct", "tasa_paro_valida",
        "tasa_ocupacion_juvenil_16_24_pct", "trabaja_fuera_pct",
        "afiliacion_ss_16_24_pct", "renta_familiar_eur", "renta_personal_total_eur",
        "renta_personal_disponible_eur", "superficie_media_m2", "antiguedad_media_anyos",
        "dist_bilbao_km", "dist_donostia_km", "dist_vitoria_km", "capital_mas_cercana",
        "dist_centroide_comarca_km", "renta_media_eur_m2_media", "cuantia_media_eur_mes_media",
        "superficie_media_m2_media", "alquiler_anual", "esfuerzo_hogar_pct",
        "esfuerzo_eustat_pct", "esfuerzo_joven_pct", "esfuerzo_joven_pct_16_29",
        "esfuerzo_joven_pct_18_34", "esfuerzo_joven_pct_18_24", "esfuerzo_joven_pct_25_34",
        "poblacion_16_24_estimada", "paro_joven_menores_25", "ocupados_16_24",
        "activos_16_24", "tasa_desempleo_juvenil_real_pct"]
base = base[cols]

dest = PROC / "analisis_variables_base.csv"
base.to_csv(dest, index=False, encoding="utf-8-sig")
print("Generado " + str(dest) + ": " + str(len(base)) + " filas, " + str(len(base.columns)) + " cols")
