"""Genera comparativa compra vs alquiler agregada por Area Funcional (bottom-up).

Lee:
- data/procesado/municipio_area_funcional_ecvi.csv
- data/procesado/alquiler_municipal_completo.csv
- data/procesado/ecvi_compraventa_limpio.csv

Genera:
- data/procesado/comparativa_compra_alquiler_af.csv
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "procesado"


def _norm_area(name: str) -> str:
    s = str(name).upper().strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"^\d+\s*-\s*A\.F\.\s*DE\s*", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def main() -> int:
    muni_af = pd.read_csv(PROC / "municipio_area_funcional_ecvi.csv")
    alq = pd.read_csv(PROC / "alquiler_municipal_completo.csv")
    ecvi = pd.read_csv(PROC / "ecvi_compraventa_limpio.csv")

    # Join alquiler con area funcional por codigo_ine
    af_map = muni_af[["codigo_ine", "area_funcional"]].copy()
    af_map["area_norm"] = af_map["area_funcional"].map(_norm_area)
    alq2 = alq.merge(af_map[["codigo_ine", "area_funcional", "area_norm"]], on="codigo_ine", how="left")

    agg = alq2.groupby("area_norm", as_index=False).agg(
        n_municipios=("codigo_ine", "nunique"),
        alquiler_eur_m2_mediana=("renta_media_eur_m2_media", "median"),
        alquiler_eur_mes_mediana=("cuantia_media_eur_mes_media", "median"),
    )

    # ECVI areas
    ecvi_af = ecvi[ecvi["ambito_tipo"] == "area_funcional"].copy()
    ecvi_af["area_norm"] = ecvi_af["nombre_ambito"].map(_norm_area)
    ecvi_af = ecvi_af[["area_norm", "precio_medio_total_eur", "precio_m2_libre_eur"]].rename(
        columns={"precio_medio_total_eur": "compraventa_precio_medio_eur",
                 "precio_m2_libre_eur": "compraventa_eur_m2"}
    )

    out = agg.merge(ecvi_af, on="area_norm", how="left")
    out = out.rename(columns={"area_norm": "area_funcional"})
    # ratio compraventa/alquiler (eur/m2)
    out["ratio_compra_alquiler_m2"] = (out["compraventa_eur_m2"] / out["alquiler_eur_m2_mediana"]).round(2)

    out_path = PROC / "comparativa_compra_alquiler_af.csv"
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"OK: {out_path} ({len(out)} filas, {len(out.columns)} cols)")
    print(out[["area_funcional", "n_municipios", "alquiler_eur_m2_mediana", "compraventa_eur_m2", "ratio_compra_alquiler_m2"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
