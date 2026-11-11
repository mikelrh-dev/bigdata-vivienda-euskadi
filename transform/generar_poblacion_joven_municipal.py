# Genera data/procesado/poblacion_joven_municipal.csv
# Poblacion municipal total y estimacion de poblacion 15-29 (legacy) y 18-34 (canonico).
# NOTA: Eustat solo publica grandes grupos (0-19, 20-64, >=65) a nivel municipal.
# La poblacion 15-29 se estima de forma transparente:
#   15-19 ~ (0-19) * (5/20)
#   20-29 ~ (20-64) * (10/45)
#   Total 15-29 ~ 0.25*(0-19) + 0.222*(20-64)
# La poblacion 18-34 se estima con ponderacion por anchura (estimacion, no dato real):
#   18-19 ~ (0-19) * (2/20) = 0.10*(0-19)
#   20-34 ~ (20-64) * (15/45) = 0.333*(20-64)
#   Total 18-34 ~ 0.10*(0-19) + 0.333*(20-64)
# Subgrupos (formulas explicitas):
#   18-24 ~ 0.10*(0-19) + (5/45)*(20-64) = 18-19 (2/20) + 20-24 (5/45)
#   25-34 ~ (10/45)*(20-64) = 0.222*(20-64)
#   Verificacion: _18_24_est + _25_34_est = _18_34_est
# Documentado como estimacion, no dato real.
# Regla bronce: solo lectura; escribe en procesado.

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR, RAW_DIR  # noqa: E402

RAW = RAW_DIR
PROC = PROCESADO_DIR

pob = pd.read_csv(RAW / "eustat_poblacion_edad.csv", dtype=str, encoding="utf-8-sig")
# WP-11: fallback explicito de periodo (2025/01/01 -> max disponible).
periodos = sorted(pob["periodo__etiqueta"].dropna().unique())
periodo = "2025/01/01" if "2025/01/01" in periodos else periodos[-1]
print(f"periodo poblacion: {periodo} (disponibles: {periodos[0]}..{periodos[-1]})")
pob = pob[pob["periodo__etiqueta"] == periodo]

# pivot: un row por municipio con columnas por grupo
grupos = pob.pivot_table(
    index="ámbitos territoriales",
    columns="grandes grupos de edad cumplida__etiqueta",
    values="Población de la C.A. de Euskadi",
    aggfunc="first",
).reset_index()
grupos["codigo_ine"] = grupos["ámbitos territoriales"].astype(str).str.zfill(5)

# nombre
nombres = pob[pob["grandes grupos de edad cumplida__etiqueta"] == "Total"][
    ["ámbitos territoriales", "ámbitos territoriales__etiqueta"]
].drop_duplicates()
grupos = grupos.merge(nombres, on="ámbitos territoriales", how="left")

# numeric
for c in ["Total", "0 - 19", "20 - 64", ">= 65"]:
    grupos[c] = pd.to_numeric(grupos[c], errors="coerce")

# estimacion 15-29 (legacy, se conserva)
grupos["poblacion_total"] = grupos["Total"]
grupos["poblacion_15_19_est"] = grupos["0 - 19"] * (5.0 / 20.0)
grupos["poblacion_20_29_est"] = grupos["20 - 64"] * (10.0 / 45.0)
grupos["poblacion_15_29_est"] = grupos["poblacion_15_19_est"] + grupos["poblacion_20_29_est"]
grupos["poblacion_15_29_est"] = grupos["poblacion_15_29_est"].round(0).astype("Int64")

# estimacion 18-34 (canonico): 0.10*(0-19)+0.333*(20-64) -> 2/20 y 15/45 por anchura
grupos["poblacion_18_34_est"] = grupos["0 - 19"] * (2.0 / 20.0) + grupos["20 - 64"] * (15.0 / 45.0)
grupos["poblacion_18_34_est"] = grupos["poblacion_18_34_est"].round(0).astype("Int64")
# subgrupos con formulas explicitas:
#   18-24 = 0.10*(0-19) + (5/45)*(20-64)  [18-19: 2/20, 20-24: 5/45]
grupos["poblacion_18_24_est"] = grupos["0 - 19"] * (2.0 / 20.0) + grupos["20 - 64"] * (5.0 / 45.0)
grupos["poblacion_18_24_est"] = grupos["poblacion_18_24_est"].round(0).astype("Int64")
#   25-34 = (10/45)*(20-64)  [25-34: 10/45, sin componente 18-19]
grupos["poblacion_25_34_est"] = grupos["20 - 64"] * (10.0 / 45.0)
grupos["poblacion_25_34_est"] = grupos["poblacion_25_34_est"].round(0).astype("Int64")

out = grupos[["codigo_ine", "ámbitos territoriales__etiqueta", "poblacion_total",
              "poblacion_15_29_est", "poblacion_18_34_est",
              "poblacion_18_24_est", "poblacion_25_34_est"]].copy()
out = out.rename(columns={"ámbitos territoriales__etiqueta": "nombre"})
out["codigo_ine"] = out["codigo_ine"].astype(str).str.zfill(5)
# filtrar solo municipios (codigos 01xxx, 20xxx, 48xxx de 5 digitos)
out = out[out["codigo_ine"].str[:2].isin(["01", "20", "48"]) & (out["codigo_ine"].str.len() == 5)]
out["metodo"] = f"estimacion 18-34: 0.10*(0-19)+0.333*(20-64) periodo={periodo}; legacy 15-29: 0.25*(0-19)+0.222*(20-64)"
out = out.sort_values("codigo_ine").reset_index(drop=True)

dest = PROC / "poblacion_joven_municipal.csv"
out.to_csv(dest, index=False, encoding="utf-8-sig")
print("Generado " + str(dest) + ": " + str(len(out)) + " filas")
print(out.head(3).to_string(index=False))
