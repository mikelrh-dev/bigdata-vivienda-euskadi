"""Construye la tabla gold data/procesado/dim_municipios_enriquecido.csv.

UNICO escritor autorizado de ese fichero. Une por codigo_ine:
- dim_municipios.csv (dimensiones y cobertura)
- dim_municipios_renta.csv (renta joven y esfuerzo, de calcular_renta_joven.py)
- dim_municipios_tension.csv (tension social, de calcular_tension_social.py)

El orden de columnas reproduce el historico: dim + columnas solo-renta
(en el orden en que las genera calcular_renta_joven) + columnas de tension.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "procesado"


def main() -> int:
    dim = pd.read_csv(PROC / "dim_municipios.csv", dtype=str, encoding="utf-8-sig")
    renta = pd.read_csv(PROC / "dim_municipios_renta.csv", dtype=str, encoding="utf-8-sig")
    tension = pd.read_csv(PROC / "dim_municipios_tension.csv", dtype=str, encoding="utf-8-sig")
    for df in (dim, renta, tension):
        df["codigo_ine"] = df["codigo_ine"].astype(str).str.zfill(5)

    extra_renta = [c for c in renta.columns if c not in dim.columns]
    extra_tension = [c for c in tension.columns
                     if c not in dim.columns and c not in extra_renta]
    gold = dim.merge(renta[["codigo_ine"] + extra_renta], on="codigo_ine", how="left")
    gold = gold.merge(tension[["codigo_ine"] + extra_tension], on="codigo_ine", how="left")

    assert len(gold) == len(dim) == 252, f"filas inesperadas: {len(gold)}"
    assert gold["codigo_ine"].is_unique, "codigo_ine duplicado en el join"

    out_path = PROC / "dim_municipios_enriquecido.csv"
    gold.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"OK: {out_path} ({len(gold)} filas, {len(gold.columns)} cols)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
