"""Recalcula la cobertura de anuncios por municipio desde datos deduplicados.

SEGUNDO y ultimo escritor autorizado de data/procesado/dim_municipios.csv
(el primero es dim_municipios.py). Motivo: dim_municipios.py corre ANTES de
la unificacion y solo puede contar filas crudas (843); este paso corre
DESPUES y cuenta anuncios unicos post-dedup (759), y recalcula
tipologia_mercado con el mismo umbral (>= 30).

Lee:
- data/procesado/dim_municipios.csv (n_anuncios crudo -> n_anuncios_raw)
- data/procesado/anuncios_unificados.csv (recuento real por codigo_ine)

Escribe:
- data/procesado/dim_municipios.csv (misma tabla + n_anuncios_raw).
- data/procesado/cobertura_anuncios.csv (WP-12: codigo_ine, n_crudo,
  n_unico, fuente_mix, nivel_fiabilidad; 252 filas, una por municipio).
No toca raw.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR  # noqa: E402
from dim_municipios import tier_de_n  # noqa: E402

PROC = PROCESADO_DIR


def _es_verdadero(serie: pd.Series) -> pd.Series:
    return serie.astype(str).str.lower().isin(["true", "1"])


def main() -> int:
    dim = pd.read_csv(PROC / "dim_municipios.csv", dtype=str, encoding="utf-8-sig")
    uni = pd.read_csv(PROC / "anuncios_unificados.csv", dtype=str, encoding="utf-8-sig")
    uni["codigo_ine"] = uni["codigo_ine"].str.zfill(5)
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)

    # PISOS-02/03: cuarentena fuera-Euskadi (geo_invalida=True) queda fuera de
    # n_anuncios y de L1/L2; n_anuncios_raw conserva el conteo pre-limpieza.
    if "geo_invalida" in uni.columns:
        _es_true = uni["geo_invalida"].astype(str).str.lower().isin(["true", "1"])
        if _es_true.any():
            print(f"Cuarentena excluida de cobertura: {int(_es_true.sum())} "
                  "anuncios geo_invalida=True")
            uni = uni.loc[~_es_true].copy()
    # Codigos nulos/vacios (cuarentena sin codigo) nunca cuentan como municipio.
    uni = uni[uni["codigo_ine"].astype(str).str.strip().replace("", "nan") != "nan"].copy()

    # Trazabilidad: conservar el recuento crudo antes de sustituirlo.
    # Idempotente: si ya existe (re-ejecucion), se preserva el original.
    if "n_anuncios_raw" in dim.columns:
        crudo = pd.to_numeric(dim["n_anuncios_raw"], errors="coerce")
        dim = dim.drop(columns=["n_anuncios", "n_anuncios_raw"])
    else:
        crudo = pd.to_numeric(dim["n_anuncios"], errors="coerce")
        dim = dim.drop(columns=["n_anuncios"])
    dim["n_anuncios_raw"] = crudo
    real = uni.groupby("codigo_ine").size().rename("n_anuncios")
    dim = dim.merge(real, on="codigo_ine", how="left")
    dim["n_anuncios"] = dim["n_anuncios"].fillna(0).astype(int)

    con_alquiler = _es_verdadero(dim["tiene_alquiler_oficial"])
    con_fianzas = _es_verdadero(dim["tiene_fianzas_emal"])
    con_mercado = con_alquiler | con_fianzas
    dim["tipologia_mercado"] = np.select(
        [dim["n_anuncios"] >= 30, (dim["n_anuncios"] >= 1) & con_mercado],
        ["Nivel1_Mercado_Dinamico", "Nivel2_Mercado_Regulado"],
        default="Nivel3_Mercado_Rural_Cerrado")

    # CONCLUSION-02: tier definitivo DESPUES del base de dim_municipios.py, con
    # el recuento real post-dedup. Fuente: n_anuncios real (nunca crudo).
    # Ante conflicto de escritura con el tier provisional crudo del base
    # (que corre antes del dedup y puede inflar: 6 A / 10 B en crudo),
    # gana el recuento real; max() se aplica solo entre re-ejecuciones
    # idempotentes de este script (mismo n real -> mismo tier, sin
    # degradar ni promocionar). Sin imputacion comarcal/IDW;
    # tipologia_mercado y n_anuncios_raw intactos.
    _tiers = [tier_de_n(int(v)) for v in dim["n_anuncios"]]
    dim["tier"] = [t for t, _ in _tiers]
    dim["tier_etiqueta"] = [te for _, te in _tiers]

    # WP-12: artefacto auditable de cobertura por municipio.
    uni["portal"] = uni["portal"].fillna("desconocido")
    mix = uni.groupby("codigo_ine")["portal"].agg(
        lambda s: "|".join(sorted(set(s.astype(str))))).rename("fuente_mix")
    cob = dim[["codigo_ine"]].copy()
    cob["n_crudo"] = pd.to_numeric(dim["n_anuncios_raw"], errors="coerce").fillna(0).astype(int)
    cob["n_unico"] = pd.to_numeric(dim["n_anuncios"], errors="coerce").fillna(0).astype(int)
    cob = cob.merge(mix, on="codigo_ine", how="left")
    cob["fuente_mix"] = cob["fuente_mix"].fillna("sin_mercado")
    import numpy as _np
    cob["nivel_fiabilidad"] = _np.select(
        [cob["n_unico"] >= 5, cob["n_unico"] >= 2, cob["n_unico"] >= 1],
        ["alta", "media", "baja"], default="sin_mercado")
    cob.to_csv(PROC / "cobertura_anuncios.csv", index=False, encoding="utf-8-sig")
    print(f"OK: {PROC / 'cobertura_anuncios.csv'} "
          f"({len(cob)} filas, niveles={cob['nivel_fiabilidad'].value_counts().to_dict()})")

    out = PROC / "dim_municipios.csv"
    dim.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"OK: {out} (suma n_anuncios={int(dim['n_anuncios'].sum())}, "
          f"raw={int(dim['n_anuncios_raw'].sum())})")
    print(dim["tipologia_mercado"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
