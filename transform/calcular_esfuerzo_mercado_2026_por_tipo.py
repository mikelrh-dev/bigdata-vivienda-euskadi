"""Calcula esfuerzo de mercado 2026 por municipio y tipo de vivienda.

Combina:
  - precio de anuncio 2026 (desde anuncios_vivienda_residencial_filtrado.csv,
    con la regla unica de filtrado de `_anuncios_2026.py`)
  - salario joven OVJ 2024 ajustado por factor IPC INE 2024->2026

Deriva tipo_de_vivienda de habitaciones:
  "1-2 hab" si habitaciones <= 2, "3 hab" si == 3, "4+ hab" si >= 4.

Esfuerzo = precio_mediana / salario_mensual_ajustado * 100 (misma formula que T-02).

NO toca raw ni esfuerzo canonico 2024.

Guarda:
    data/procesado/esfuerzo_mercado_2026_por_tipo.csv

Uso:
    python transform/calcular_esfuerzo_mercado_2026_por_tipo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _anuncios_2026 import cargar_anuncios_2026, mediana_con_ic  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"

OUT = PROC / "esfuerzo_mercado_2026_por_tipo.csv"
IPC = RAW / "ipc_ine_2024_2026.csv"
SALARIO = RAW / "ovj_salario_joven_2024.json"


def _load_ipc_factor() -> tuple[float, float, float, str]:
    """Carga IPC 2024, IPC 2026 y factor desde raw.

    Retorna (ipc_2024, ipc_2026, factor, flag).
    """
    if not IPC.exists():
        return 107.2, 117.8, 117.8 / 107.2, "fallback"
    df = pd.read_csv(IPC, dtype=str, encoding="utf-8-sig")
    fila_2024 = df[df["ano"].astype(str) == "2024"]
    fila_2026 = df[df["ano"].astype(str) == "2026"]
    fila_factor = df[df["ano"].astype(str) == "factor_2026_2024"]
    ipc_2024 = float(fila_2024["ipc_medio_anual"].iloc[0]) if len(fila_2024) else 107.2
    ipc_2026 = float(fila_2026["ipc_medio_anual"].iloc[0]) if len(fila_2026) else 117.8
    factor_doc = float(fila_factor["ipc_medio_anual"].iloc[0]) if len(fila_factor) else (ipc_2026 / ipc_2024)
    flag = str(fila_2024["flag"].iloc[0]) if len(fila_2024) else "fallback"
    return ipc_2024, ipc_2026, factor_doc, flag


def _load_salario_base() -> dict[str, float]:
    """Carga salario base OVJ 2024 por tramo desde raw."""
    with SALARIO.open(encoding="utf-8") as f:
        datos = json.load(f)
    out: dict[str, float] = {}
    for fila in datos.get("datos", []):
        tramo = str(fila["tramo_edad"])
        out[tramo] = float(fila["salario_neto_mes_eur"])
    return out


def _tipo_de_vivienda(habitaciones: float) -> str:
    """Deriva el tipo de vivienda a partir del numero de habitaciones."""
    if habitaciones <= 2:
        return "1-2 hab"
    if habitaciones == 3:
        return "3 hab"
    return "4+ hab"


def main() -> int:
    ipc_2024, ipc_2026, factor_ipc, flag_ipc = _load_ipc_factor()
    salario_base = _load_salario_base()

    salario_18_34_2024 = salario_base.get("18-34", 1564.0)
    salario_16_29_2024 = salario_base.get("16-29", 1381.0)

    salario_18_34_2026 = salario_18_34_2024 * factor_ipc
    salario_16_29_2026 = salario_16_29_2024 * factor_ipc

    df, meta = cargar_anuncios_2026()
    df = df[df["anuncio_valido"]].dropna(subset=["precio_eur", "habitaciones"]).copy()
    df["tipo_de_vivienda"] = df["habitaciones"].map(_tipo_de_vivienda)

    filas = []
    for (code, tipo), grupo in df.groupby(["codigo_ine", "tipo_de_vivienda"], sort=True):
        precios = grupo["precio_eur"].dropna().tolist()
        n_anuncios = len(precios)
        if n_anuncios == 0:
            continue
        ic = mediana_con_ic(precios, semilla=int(code) + len(tipo))
        esfuerzo_18_34 = ic["mediana"] / salario_18_34_2026 * 100
        esfuerzo_16_29 = ic["mediana"] / salario_16_29_2026 * 100
        esfuerzo_sin_ajuste = ic["mediana"] / salario_18_34_2024 * 100

        filas.append({
            "codigo_ine": code,
            "tipo_de_vivienda": tipo,
            "precio_mediana_eur": round(ic["mediana"], 2),
            "n_anuncios": n_anuncios,
            "salario_joven_2026_ajustado_18_34_eur_mes": round(salario_18_34_2026, 2),
            "salario_joven_2026_ajustado_16_29_eur_mes": round(salario_16_29_2026, 2),
            "esfuerzo_mercado_2026_pct_18_34": round(esfuerzo_18_34, 2),
            "esfuerzo_mercado_2026_pct_16_29": round(esfuerzo_16_29, 2),
            "factor_ipc": round(factor_ipc, 6),
            "vintage_numerador": 2026,
            "vintage_denominador": 2024,
            "esfuerzo_sin_ajuste_pct_18_34": round(esfuerzo_sin_ajuste, 2),
            "ic95_lo_pct_18_34": round(ic["lo"] / salario_18_34_2026 * 100, 2),
            "ic95_hi_pct_18_34": round(ic["hi"] / salario_18_34_2026 * 100, 2),
            "ic95_amplitud_pct_18_34": ic["amplitud_pct"],
            "flag_n_insuficiente": n_anuncios < 5,
            "flag_concluyente": bool(n_anuncios >= 10 and ic["amplitud_pct"] < 30),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out = pd.DataFrame(filas, columns=[
        "codigo_ine", "tipo_de_vivienda", "precio_mediana_eur", "n_anuncios",
        "salario_joven_2026_ajustado_18_34_eur_mes",
        "salario_joven_2026_ajustado_16_29_eur_mes",
        "esfuerzo_mercado_2026_pct_18_34", "esfuerzo_mercado_2026_pct_16_29",
        "factor_ipc", "vintage_numerador", "vintage_denominador",
        "esfuerzo_sin_ajuste_pct_18_34",
        "ic95_lo_pct_18_34", "ic95_hi_pct_18_34", "ic95_amplitud_pct_18_34",
        "flag_n_insuficiente", "flag_concluyente",
    ])
    df_out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(
        f"OK: {OUT.name} ({len(df_out)} grupos, {int(df_out['n_anuncios'].sum())} anuncios, "
        f"factor_ipc={factor_ipc:.6f}, flag_ipc={flag_ipc})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
