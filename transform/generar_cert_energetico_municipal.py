#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
transform/generar_cert_energetico_municipal.py
Genera cert_energetico_municipal_252.csv a partir de los 3 CSVs de certificados
de eficiencia energética de Open Data Euskadi (raw).

Lee: data/raw/certificados_energeticos_{araba,bizkaia,gipuzkoa}_completo.csv
Escribe: data/procesado/cert_energetico_municipal_252.csv

Filtrado: solo Tipo edificio que contenga 'Vivienda'.
Agregación: moda de Calificación energética + distribución A-G por municipio.
"""
import os
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "procesado")

TERRITORIOS = ["araba", "bizkaia", "gipuzkoa", "bilbao", "donostia", "vitoria"]

def main():
    frames = []
    for t in TERRITORIOS:
        path = os.path.join(RAW, f"certificados_energeticos_{t}_completo.csv")
        if not os.path.exists(path):
            print(f"[WARN] No existe {path}, saltando")
            continue
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig", low_memory=False)
        frames.append(df)
        print(f"[LOAD] {t}: {len(df)} filas, {df['Municipio'].nunique()} municipios")

    if not frames:
        print("[ERROR] No se cargó ningún archivo")
        return

    df = pd.concat(frames, ignore_index=True)
    print(f"[TOTAL] {len(df)} filas, {df['Municipio'].nunique()} municipios")

    # Filtrar solo viviendas
    vivienda_mask = df["Tipo edificio"].astype(str).str.contains("Vivienda", case=False, na=False)
    df_viv = df[vivienda_mask].copy()
    print(f"[FILTRO] Viviendas: {len(df_viv)} de {len(df)} ({len(df_viv)/len(df)*100:.1f}%)")

    # Mapeo municipio -> codigo INE (desde dim_municipios.csv)
    dim_path = os.path.join(PROC, "dim_municipios.csv")
    if os.path.exists(dim_path):
        dim = pd.read_csv(dim_path, dtype=str)
        # Normalizar nombres para join
        dim["nombre_norm"] = dim["nombre_canonico"].str.strip().str.lower()
        df_viv["muni_norm"] = df_viv["Municipio"].str.strip().str.lower()
        # Mapeo general (nombre normalizado)
        name_map = {}
        for _, row in dim.iterrows():
            name_map[row["nombre_norm"]] = row["codigo_ine"]
        df_viv["codigo_ine"] = df_viv["muni_norm"].map(name_map)
        n_sin = df_viv["codigo_ine"].isna().sum()
        print(f"[MAP] Sin codigo_ine (antes manual): {n_sin} de {len(df_viv)}")

        # Aplicar mapeo manual a los que siguen sin codigo (substring matching)
        for idx, row in df_viv[df_viv["codigo_ine"].isna()].iterrows():
            muni_lower = str(row["muni_norm"]).lower()
            for idx2, row2 in dim.iterrows():
                dim_lower = str(row2["nombre_canonico"]).lower()
                if "arrasate" in muni_lower and "arrasate" in dim_lower:
                    df_viv.loc[idx, "codigo_ine"] = row2["codigo_ine"]
                    break
                if muni_lower == "bilbao" and dim_lower == "bilbao":
                    df_viv.loc[idx, "codigo_ine"] = row2["codigo_ine"]
                    break
                if "donostia" in muni_lower and "donostia" in dim_lower:
                    df_viv.loc[idx, "codigo_ine"] = row2["codigo_ine"]
                    break
                if ("vitoria" in muni_lower or "gasteiz" in muni_lower) and ("vitoria" in dim_lower or "gasteiz" in dim_lower):
                    df_viv.loc[idx, "codigo_ine"] = row2["codigo_ine"]
                    break
        n_sin2 = df_viv["codigo_ine"].isna().sum()
        print(f"[MAP] Sin codigo_ine (despues manual): {n_sin2} de {len(df_viv)}")
    else:
        print("[WARN] dim_municipios.csv no encontrado, sin mapeo INE")
        df_viv["codigo_ine"] = None

    # Agregar por municipio
    agg_rows = []
    for muni, g in df_viv.groupby("Municipio"):
        calif = g["Calificación energética"].astype(str).str.strip().str.upper()
        calif = calif[calif.isin(list("ABCDEFG"))]
        n = len(calif)
        if n == 0:
            moda = None
            dist = {l: 0 for l in "ABCDEFG"}
        else:
            moda = calif.mode().iloc[0] if not calif.mode().empty else None
            dist = {l: int((calif == l).sum()) for l in "ABCDEFG"}
        codigo = g["codigo_ine"].dropna().iloc[0] if g["codigo_ine"].notna().any() else None
        agg_rows.append({
            "municipio": muni,
            "codigo_ine": codigo,
            "n_certificados": n,
            "cert_moda": moda,
            "cert_A": dist["A"], "cert_B": dist["B"], "cert_C": dist["C"],
            "cert_D": dist["D"], "cert_E": dist["E"], "cert_F": dist["F"],
            "cert_G": dist["G"],
        })

    result = pd.DataFrame(agg_rows)
    result = result.sort_values("municipio").reset_index(drop=True)

    # Asegurar 252 municipios: reindexar con dim_municipios
    if os.path.exists(dim_path):
        dim = pd.read_csv(dim_path, dtype=str)
        all_munis = dim[["codigo_ine", "nombre_canonico"]].copy()
        all_munis["muni_norm"] = all_munis["nombre_canonico"].str.strip().str.lower()
        all_munis = all_munis.rename(columns={"nombre_canonico": "municipio"})
        result["muni_norm"] = result["municipio"].str.strip().str.lower()
        # Normalizar nombres para merge (quitar espacios alrededor de /)
        result["muni_norm"] = result["muni_norm"].str.replace(" / ", "/", regex=False).str.replace(" /", "/", regex=False).str.replace("/ ", "/", regex=False)
        all_munis["muni_norm"] = all_munis["muni_norm"].str.replace(" / ", "/", regex=False).str.replace(" /", "/", regex=False).str.replace("/ ", "/", regex=False)
        merged = all_munis.merge(result, on="muni_norm", how="left", suffixes=("", "_cert"))
        # Usar nombre de dim_municipios
        merged["municipio"] = merged["municipio"]
        # Rellenar nulos
        for col in ["n_certificados", "cert_A", "cert_B", "cert_C", "cert_D", "cert_E", "cert_F", "cert_G"]:
            merged[col] = merged[col].fillna(0).astype(int)
        merged["cert_moda"] = merged["cert_moda"].fillna(None)
        # Seleccionar columnas finales
        out_cols = ["codigo_ine", "municipio", "n_certificados", "cert_moda",
                    "cert_A", "cert_B", "cert_C", "cert_D", "cert_E", "cert_F", "cert_G"]
        out = merged[out_cols].copy()
    else:
        out = result

    out_path = os.path.join(PROC, "cert_energetico_municipal_252.csv")
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\n[OK] Guardado: {out_path}")
    print(f"  Municipios: {len(out)}")
    print(f"  Con certificados: {(out['n_certificados'] > 0).sum()}")
    print(f"  Sin certificados: {(out['n_certificados'] == 0).sum()}")
    print(f"  Moda distribution:")
    print(out["cert_moda"].value_counts().to_dict())

if __name__ == "__main__":
    main()
