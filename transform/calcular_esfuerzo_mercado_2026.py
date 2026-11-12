"""Calcula esfuerzo de mercado 2026 por municipio (capa paralela al canónico 2024).

Combina:
  - precio de anuncio 2026 (desde anuncios_vivienda_residencial_filtrado.csv)
  - salario joven OVJ 2024 ajustado por factor IPC INE 2024→2026

NO toca el esfuerzo canónico 2024 (calcular_renta_joven.py, mongo_aggregations.py
pipeline_indicadores_municipio, dim_municipios_enriquecido.csv).

Guarda:
    data/procesado/esfuerzo_mercado_2026.csv  (252 filas, 1 por municipio INE zfill5)

Uso:
    python transform/calcular_esfuerzo_mercado_2026.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"

OUT = PROC / "esfuerzo_mercado_2026.csv"


def _load_ipc_factor() -> tuple[float, float, float, str]:
    """Carga IPC 2024, IPC 2026 y factor desde raw.

    Retorna (ipc_2024, ipc_2026, factor, flag).
    """
    ipc_path = RAW / "ipc_ine_2024_2026.csv"
    if not ipc_path.exists():
        # Fallback documentado si el raw no existe aún.
        return 107.2, 117.8, 117.8 / 107.2, "fallback"
    df = pd.read_csv(ipc_path, dtype=str, encoding="utf-8-sig")
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
    salario_path = RAW / "ovj_salario_joven_2024.json"
    with salario_path.open(encoding="utf-8") as f:
        datos = json.load(f)
    out: dict[str, float] = {}
    for fila in datos.get("datos", []):
        tramo = str(fila["tramo_edad"])
        out[tramo] = float(fila["salario_neto_mes_eur"])
    return out


def _winsorizar_mediana(valores: list[float]) -> float:
    """Mediana tras winsorización al percentil 1-99 (recorte, no imputación)."""
    if not valores:
        return float("nan")
    s = sorted(valores)
    n = len(s)
    if n == 1:
        return s[0]
    p1_idx = max(0, math.floor(n * 0.01) - 1)
    p99_idx = min(n - 1, math.ceil(n * 0.99) - 1)
    recortado = [max(s[p1_idx], min(s[p99_idx], v)) for v in s]
    recortado.sort()
    m = len(recortado)
    if m % 2 == 1:
        return recortado[m // 2]
    return (recortado[m // 2 - 1] + recortado[m // 2]) / 2


def main() -> int:
    ipc_2024, ipc_2026, factor_ipc, flag_ipc = _load_ipc_factor()
    salario_base = _load_salario_base()

    salario_18_34_2024 = salario_base.get("18-34", 1564.0)
    salario_16_29_2024 = salario_base.get("16-29", 1381.0)

    salario_18_34_2026 = salario_18_34_2024 * factor_ipc
    salario_16_29_2026 = salario_16_29_2024 * factor_ipc

    # Lista maestra de municipios (252).
    dim_path = PROC / "dim_municipios.csv"
    dim = pd.read_csv(dim_path, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)

    # Anuncios 2026 filtrados.
    anuncio_path = PROC / "anuncios_vivienda_residencial_filtrado.csv"
    if not anuncio_path.exists():
        log.error("Falta %s. Ejecuta primero generar_anuncios_residencial_filtrado.py", anuncio_path.name)
        return 1
    df_an = pd.read_csv(anuncio_path, dtype=str, encoding="utf-8-sig")
    df_an["codigo_ine"] = df_an["codigo_ine"].astype(str).str.zfill(5)
    df_an["precio_eur"] = pd.to_numeric(df_an["precio_eur"], errors="coerce")

    # Agregar por municipio: precio medio, mediana, mediana_m2_winsorizada, n_anuncios, n_precio.
    agg = {}
    for code, grupo in df_an.groupby("codigo_ine"):
        precios = grupo["precio_eur"].dropna().tolist()
        if not precios:
            continue
        precios_sorted = sorted(precios)
        n = len(precios_sorted)
        media = sum(precios_sorted) / n
        mediana = precios_sorted[n // 2] if n % 2 == 1 else (precios_sorted[n // 2 - 1] + precios_sorted[n // 2]) / 2
        # Mediana m2 winsorizada (replicar M1 AGREGACION-01).
        sup = pd.to_numeric(grupo["superficie_m2"], errors="coerce").dropna().tolist()
        m2_vals = [p / s for p, s in zip(precios_sorted, sup) if s and s > 0]
        mediana_m2_w = _winsorizar_mediana(m2_vals)
        agg[code] = {
            "precio_medio_eur": round(media, 2),
            "precio_mediana_eur": round(mediana, 2),
            "mediana_m2_winsorizada": round(mediana_m2_w, 2) if not math.isnan(mediana_m2_w) else None,
            "n_anuncios": n,
            "n_precio": n,
        }

    filas = []
    for _, row in dim.iterrows():
        code = str(row["codigo_ine"])
        a = agg.get(code, {
            "precio_medio_eur": None,
            "precio_mediana_eur": None,
            "mediana_m2_winsorizada": None,
            "n_anuncios": 0,
            "n_precio": 0,
        })
        precio_mediana = a["precio_mediana_eur"]
        if precio_mediana is not None:
            # Esfuerzo = precio mensual / salario mensual × 100.
            # Salario OVJ ya es mensual (1.564 €/mes 18-34; 1.381 €/mes 16-29),
            # NO se multiplica por 12 (eso sería para renta anual).
            esfuerzo_18_34 = precio_mediana / salario_18_34_2026 * 100
            esfuerzo_16_29 = precio_mediana / salario_16_29_2026 * 100
        else:
            esfuerzo_18_34 = None
            esfuerzo_16_29 = None

        filas.append({
            "codigo_ine": code,
            "nombre_canonico": row.get("nombre_canonico", ""),
            "territorio": row.get("territorio", ""),
            "n_anuncios_2026": a["n_anuncios"],
            "n_precio_2026": a["n_precio"],
            "precio_medio_anuncio_2026_eur_mes": a["precio_medio_eur"],
            "precio_mediana_anuncio_2026_eur_mes": a["precio_mediana_eur"],
            "mediana_m2_winsorizada_2026_eur_m2": a["mediana_m2_winsorizada"],
            "salario_joven_2024_base_18_34_eur_mes": salario_18_34_2024,
            "salario_joven_2024_base_16_29_eur_mes": salario_16_29_2024,
            "ipc_2024": ipc_2024,
            "ipc_2026": ipc_2026,
            "factor_ipc_2026_2024": round(factor_ipc, 6),
            "salario_joven_2026_ajustado_18_34_eur_mes": round(salario_18_34_2026, 2),
            "salario_joven_2026_ajustado_16_29_eur_mes": round(salario_16_29_2026, 2),
            "esfuerzo_mercado_2026_pct_18_34": round(esfuerzo_18_34, 2) if esfuerzo_18_34 is not None else None,
            "esfuerzo_mercado_2026_pct_16_29": round(esfuerzo_16_29, 2) if esfuerzo_16_29 is not None else None,
            "vintage_numerador": 2026,
            "vintage_denominador": 2024,
            "flag_no_comparable": True,
            "flag_ipc": flag_ipc,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out = pd.DataFrame(filas)
    df_out.to_csv(OUT, index=False, encoding="utf-8-sig")
    n_con_dato = sum(1 for f in filas if f["esfuerzo_mercado_2026_pct_18_34"] is not None)
    print(f"OK: {OUT.name} ({len(filas)} filas, {n_con_dato} con esfuerzo calculado, flag_ipc={flag_ipc})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
