# Genera data/procesado/poblacion_joven_municipal.csv
# Poblacion municipal total y estimacion de poblacion 15-29.
# NOTA: Eustat solo publica grandes grupos (0-19, 20-64, >=65) a nivel municipal.
# La poblacion 15-29 se estima de forma transparente:
#   15-19 ~ (0-19) * (5/20)
#   20-29 ~ (20-64) * (10/45)
#   Total 15-29 ~ 0.25*(0-19) + 0.222*(20-64)
# Documentado como estimacion, no dato real.
# Regla bronce: solo lectura; escribe en procesado.

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "procesado"

pob = pd.read_csv(RAW / "eustat_poblacion_edad.csv", dtype=str, encoding="utf-8-sig")
pob = pob[pob["periodo__etiqueta"] == "2025/01/01"]

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

# estimacion 15-29
grupos["poblacion_total"] = grupos["Total"]
grupos["poblacion_15_19_est"] = grupos["0 - 19"] * (5.0 / 20.0)
grupos["poblacion_20_29_est"] = grupos["20 - 64"] * (10.0 / 45.0)
grupos["poblacion_15_29_est"] = grupos["poblacion_15_19_est"] + grupos["poblacion_20_29_est"]
grupos["poblacion_15_29_est"] = grupos["poblacion_15_29_est"].round(0).astype("Int64")

out = grupos[["codigo_ine", "ámbitos territoriales__etiqueta", "poblacion_total",
              "poblacion_15_29_est"]].copy()
out = out.rename(columns={"ámbitos territoriales__etiqueta": "nombre"})
out["codigo_ine"] = out["codigo_ine"].astype(str).str.zfill(5)
# filtrar solo municipios (codigos 01xxx, 20xxx, 48xxx de 5 digitos)
out = out[out["codigo_ine"].str[:2].isin(["01", "20", "48"]) & (out["codigo_ine"].str.len() == 5)]
out["metodo"] = "estimacion: 0.25*(0-19)+0.222*(20-64)"
out = out.sort_values("codigo_ine").reset_index(drop=True)

dest = PROC / "poblacion_joven_municipal.csv"
out.to_csv(dest, index=False, encoding="utf-8-sig")
print("Generado " + str(dest) + ": " + str(len(out)) + " filas")
print(out.head(3).to_string(index=False))
