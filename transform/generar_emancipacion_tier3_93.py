# Genera data/procesado/emancipacion_tier3_93.csv
# Derivado analitico para los 93 municipios sin mercado de alquiler estructural.
# Regla bronce: solo lectura de raw/procesado; escribe en procesado.

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "procesado"

# 1. Municipios sin alquiler directo
falt = pd.read_csv(PROC / "municipios_faltantes_93.csv", dtype=str, encoding="utf-8-sig")
codes = falt["codigo_ine"].astype(str).str.zfill(5).tolist()

# 2. Fuentes
ud = pd.read_csv(RAW / "udalmap_empleo_corregido.csv", dtype=str, encoding="utf-8-sig")
ud["codigo_ine"] = ud["codigo_ine"].astype(str).str.zfill(5)

rc = pd.read_csv(RAW / "renta_municipal_completa.csv", dtype=str, encoding="utf-8-sig")
rc["codigo_ine"] = rc["codigo_ine"].astype(str).str.zfill(5)

osrm = pd.read_csv(RAW / "osrm_tiempos_capitales.csv", dtype=str, encoding="utf-8-sig")
osrm["codigo_ine"] = osrm["codigo_ine"].astype(str).str.zfill(5)

paradas = pd.read_csv(RAW / "transporte_paradas_municipio.csv", dtype=str, encoding="utf-8-sig")
paradas["codigo_ine"] = paradas["codigo_ine"].astype(str).str.zfill(5)

edu = pd.read_csv(RAW / "educacion_centros.csv", dtype=str, encoding="utf-8-sig")
edu["codigo_ine"] = edu["codigo_ine"].astype(str).str.zfill(5)
edu_set = set(edu["codigo_ine"].unique())

sal = pd.read_csv(RAW / "salud_centros.csv", dtype=str, encoding="utf-8-sig")
sal["codigo_ine"] = sal["codigo_ine"].astype(str).str.zfill(5)
sal_set = set(sal["codigo_ine"].unique())

dim = pd.read_csv(PROC / "dim_municipios.csv", dtype=str, encoding="utf-8-sig")
dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)

# 3. Construir DataFrame
rows = []
for code in codes:
    u = ud[ud["codigo_ine"] == code]
    r = rc[rc["codigo_ine"] == code]
    o = osrm[osrm["codigo_ine"] == code]
    p = paradas[paradas["codigo_ine"] == code]
    d = dim[dim["codigo_ine"] == code]

    paro = float(u["tasa_paro_lanbide_pct"].iloc[0]) if not u.empty and pd.notna(u["tasa_paro_lanbide_pct"].iloc[0]) else None
    osrm_min = None
    if not o.empty:
        vals = [pd.to_numeric(o[c].iloc[0], errors="coerce") for c in ["minutos_Vitoria-Gasteiz", "minutos_Bilbao", "minutos_Donostia-San Sebastian"]]
        osrm_min = min([v for v in vals if pd.notna(v)], default=None)
    n_paradas = int(pd.to_numeric(p["n_paradas"].iloc[0], errors="coerce")) if not p.empty and pd.notna(p["n_paradas"].iloc[0]) else 0
    tiene_edu = 1 if code in edu_set else 0
    tiene_sal = 1 if code in sal_set else 0
    etxebide_pc = float(u["etxebide_solicitudes_por_mil"].iloc[0]) if not u.empty and pd.notna(u["etxebide_solicitudes_por_mil"].iloc[0]) else None
    renta_hogar = float(r["renta_hogar"].iloc[0]) if not r.empty and pd.notna(r["renta_hogar"].iloc[0]) else None
    renta_joven = float(r["renta_joven_estimada_16_29"].iloc[0]) if not r.empty and pd.notna(r["renta_joven_estimada_16_29"].iloc[0]) else None
    nombre = d["nombre_canonico"].iloc[0] if not d.empty else falt[falt["codigo_ine"]==code]["nombre_canonico"].iloc[0]

    # clasificacion
    if n_paradas == 0 and tiene_edu == 0 and tiene_sal == 0:
        clasif = "no_emancipa"
        justif = "sin paradas ni servicios basicos"
    elif osrm_min is not None and osrm_min < 45 and n_paradas >= 2:
        clasif = "compra_commuting"
        justif = "OSRM<45min y >=2 paradas; alquiler 0 estructural, via compra/commuting"
    else:
        clasif = "desierto"
        justif = "resto Tier3 sin mercado alquiler"

    rows.append({
        "codigo_ine": code,
        "nombre_canonico": nombre,
        "paro_lanbide": paro,
        "osrm_min": osrm_min,
        "n_paradas": n_paradas,
        "tiene_educacion": tiene_edu,
        "tiene_salud": tiene_sal,
        "etxebide_pc": etxebide_pc,
        "renta_hogar": renta_hogar,
        "alquiler_eur_m2": None,
        "origen_alquiler": "sin_mercado_estructural_0_oferta",
        "clasificacion": clasif,
        "justificacion": justif,
        "renta_joven_16_29": renta_joven,
        "n_secciones_rescatadas": 0,
    })

out = pd.DataFrame(rows)
out = out.sort_values("codigo_ine").reset_index(drop=True)

# tipos
out["codigo_ine"] = out["codigo_ine"].astype(str).str.zfill(5)
out["paro_lanbide"] = pd.to_numeric(out["paro_lanbide"], errors="coerce")
out["osrm_min"] = pd.to_numeric(out["osrm_min"], errors="coerce")
out["n_paradas"] = pd.to_numeric(out["n_paradas"], errors="coerce").astype("Int64")
out["tiene_educacion"] = pd.to_numeric(out["tiene_educacion"], errors="coerce").astype("Int64")
out["tiene_salud"] = pd.to_numeric(out["tiene_salud"], errors="coerce").astype("Int64")
out["etxebide_pc"] = pd.to_numeric(out["etxebide_pc"], errors="coerce")
out["renta_hogar"] = pd.to_numeric(out["renta_hogar"], errors="coerce")
out["renta_joven_16_29"] = pd.to_numeric(out["renta_joven_16_29"], errors="coerce")

dest = PROC / "emancipacion_tier3_93.csv"
out.to_csv(dest, index=False, encoding="utf-8-sig")
print("Generado " + str(dest) + ": " + str(len(out)) + " filas")
# resumen clasificacion
print(out["clasificacion"].value_counts().to_string())
