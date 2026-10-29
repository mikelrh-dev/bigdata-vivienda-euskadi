"""Desglosa Eustat Renta y Población en dataset demográfico limpio por municipio (252 filas)."""
from __future__ import annotations
import json, os, unicodedata
import pandas as pd

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

def norm(s):
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s

def main():
    os.makedirs(OUT, exist_ok=True)
    # dim municipios para mapeo nombre -> codigo_ine
    dim = pd.read_csv(os.path.join(RAW, "dim_municipios.csv"))
    dim["key"] = dim["nombre_canonico"].apply(norm)
    name2code = dict(zip(dim["key"], dim["codigo_ine"].astype(str).str.zfill(5)))

    # Renta
    renta = pd.read_csv(os.path.join(RAW, "eustat_renta_municipal.csv"), low_memory=False)
    renta["key"] = renta["ámbitos territoriales__etiqueta"].apply(norm)
    renta["codigo_ine"] = renta["key"].map(name2code)
    renta = renta[renta["codigo_ine"].notna()].copy()
    renta["municipio"] = renta["ámbitos territoriales__etiqueta"].astype(str).str.strip()
    last_year = int(renta["periodo"].max())
    renta = renta[renta["periodo"] == last_year]

    def pivot_renta(tipo):
        sub = renta[renta["tipo de renta__etiqueta"] == tipo]
        piv = sub.pivot_table(
            index=["codigo_ine", "municipio"],
            columns="sexo__etiqueta",
            values="Renta personal media de la C.A. de Euskadi (euros)",
            aggfunc="first",
        ).reset_index()
        piv.columns.name = None
        return piv

    rt = pivot_renta("Renta total")
    rd = pivot_renta("Renta disponible")
    df = rt[["codigo_ine", "municipio", "Total", "Hombres", "Mujeres"]].copy()
    df = df.rename(columns={"Total": "renta_personal_total_ambos_eur",
                            "Hombres": "renta_personal_total_hombres_eur",
                            "Mujeres": "renta_personal_total_mujeres_eur"})
    rd2 = rd[["codigo_ine", "Total"]].rename(columns={"Total": "renta_disponible_ambos_eur"})
    df = df.merge(rd2, on="codigo_ine", how="left")
    df["anio_renta"] = last_year

    # Población total (último año, grupo Total)
    pob = pd.read_csv(os.path.join(RAW, "eustat_poblacion_edad.csv"), low_memory=False)
    pob["key"] = pob["ámbitos territoriales__etiqueta"].apply(norm)
    pob["codigo_ine"] = pob["key"].map(name2code)
    pob = pob[pob["codigo_ine"].notna()].copy()
    pob["anio"] = pob["periodo"].astype(str).str[:4].astype(int)
    last_pob_year = int(pob["anio"].max())
    pob = pob[(pob["anio"] == last_pob_year) & (pob["grandes grupos de edad cumplida__etiqueta"] == "Total")]
    pob_total = pob.groupby("codigo_ine")["Población de la C.A. de Euskadi"].sum().reset_index()
    pob_total = pob_total.rename(columns={"Población de la C.A. de Euskadi": "poblacion_total"})
    df = df.merge(pob_total, on="codigo_ine", how="left")
    df["poblacion_joven_15_29"] = None

    cols = ["codigo_ine", "municipio", "anio_renta",
            "renta_personal_total_ambos_eur", "renta_personal_total_hombres_eur",
            "renta_personal_total_mujeres_eur", "renta_disponible_ambos_eur",
            "poblacion_total", "poblacion_joven_15_29"]
    df = df[cols]
    df.to_json(os.path.join(OUT, "eustat_demografia_renta_252.json"), orient="records", force_ascii=False, indent=2)
    df.to_csv(os.path.join(OUT, "eustat_demografia_renta_252.csv"), index=False)
    print("Demografia renta:", len(df), "filas")

if __name__ == "__main__":
    main()
