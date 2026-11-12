"""Calcula esfuerzo de mercado 2026 por municipio (capa paralela al canonico 2024).

Combina:
  - precio de anuncio 2026 (desde anuncios_vivienda_residencial_filtrado.csv,
    ya filtrado por la regla unica de `_anuncios_2026.py`)
  - salario joven OVJ 2024 ajustado por factor IPC INE 2024->2026

NO toca el esfuerzo canonico 2024 (calcular_renta_joven.py,
dim_municipios_enriquecido.csv) ni data/raw.

Anade, sobre las columnas historicas:
  - `n_brutos_2026` / `n_excluidos_2026` (auditoria de la exclusion)
  - `ic95_lo/hi/amplitud_pct_18_34` (bootstrap de la mediana, semilla fija)
  - `flag_n_insuficiente` (n<5) y `flag_concluyente` (n>=10 y amplitud<30)
  - banda de escenarios de denominador: salario 2024, salario+IPC y renta joven
    2024 (esta ultima mide cuanto del salto front al canonico es cambio de
    denominador, no de precio)

Guarda:
    data/procesado/esfuerzo_mercado_2026.csv  (252 filas, 1 por municipio INE zfill5)

Uso:
    python transform/calcular_esfuerzo_mercado_2026.py
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

OUT = PROC / "esfuerzo_mercado_2026.csv"

CAVEAT = (
    "capa de oferta: precio de anuncio 2026 sobre salario OVJ 2024 deflactado; "
    "no comparable con alquiler registrado 2024"
)
FUENTE_NUMERADOR = "fotocasa+pisos+realtyapi larga_estancia 2026 (anuncio publicado)"
FUENTE_DENOMINADOR = "OVJ 2024 salario neto x IPC INE 2024->2026 (valor fallback)"


def _load_ipc_factor() -> tuple[float, float, float, str]:
    """Carga IPC 2024, IPC 2026 y factor desde raw.

    Retorna (ipc_2024, ipc_2026, factor, flag).
    """
    ipc_path = RAW / "ipc_ine_2024_2026.csv"
    if not ipc_path.exists():
        # Fallback documentado si el raw no existe aun.
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
    """Mediana tras winsorizacion al percentil 1-99 (recorte, no imputacion)."""
    if not valores:
        return float("nan")
    s = sorted(valores)
    n = len(s)
    if n == 1:
        return s[0]
    p1_idx = max(0, int(n * 0.01) - 1)
    p99_idx = min(n - 1, int(n * 0.99) - 1)
    recortado = sorted(max(s[p1_idx], min(s[p99_idx], v)) for v in s)
    m = len(recortado)
    if m % 2 == 1:
        return recortado[m // 2]
    return (recortado[m // 2 - 1] + recortado[m // 2]) / 2


def _banda(precio: float | None, salarios: list[float]) -> tuple[float | None, float | None]:
    """Minimo y maximo esfuerzo entre los denominadores disponibles."""
    if precio is None or not salarios:
        return None, None
    esfuerzos = [precio / s * 100 for s in salarios if s and s > 0]
    if not esfuerzos:
        return None, None
    return round(min(esfuerzos), 2), round(max(esfuerzos), 2)


def main() -> int:
    ipc_2024, ipc_2026, factor_ipc, flag_ipc = _load_ipc_factor()
    salario_base = _load_salario_base()

    salario_18_34_2024 = salario_base.get("18-34", 1564.0)
    salario_16_29_2024 = salario_base.get("16-29", 1381.0)

    salario_18_34_2026 = salario_18_34_2024 * factor_ipc
    salario_16_29_2026 = salario_16_29_2024 * factor_ipc

    # Lista maestra de municipios (252) con la renta joven canonica para la banda.
    dim_path = PROC / "dim_municipios_enriquecido.csv"
    dim = pd.read_csv(dim_path, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    dim["renta_joven_mes_18_34"] = pd.to_numeric(
        dim.get("renta_joven_estimada_18_34"), errors="coerce"
    ) / 12

    # Anuncios 2026 con la regla unica de filtrado.
    df_an, meta = cargar_anuncios_2026()
    validos = df_an[df_an["anuncio_valido"]].copy()

    agg: dict[str, dict] = {}
    for code, grupo in df_an.groupby("codigo_ine", sort=True):
        g_validos = grupo[grupo["anuncio_valido"]]
        precios = g_validos["precio_eur"].dropna().tolist()
        if not precios:
            agg[code] = {
                "n_brutos": len(grupo),
                "n_excluidos": int((~grupo["anuncio_valido"]).sum()),
                "precio_medio": None,
                "precio_mediana": None,
                "mediana_m2_w": None,
                "ic": {"mediana": float("nan"), "lo": float("nan"), "hi": float("nan"), "amplitud_pct": float("nan")},
                "n": 0,
            }
            continue

        ic = mediana_con_ic(precios, semilla=int(code))
        sup = g_validos["superficie_m2"].dropna()
        m2_vals = [
            p / s
            for p, s in zip(g_validos["precio_eur"], g_validos["superficie_m2"])
            if pd.notna(p) and pd.notna(s) and s > 0
        ]
        mediana_m2_w = _winsorizar_mediana(m2_vals)

        agg[code] = {
            "n_brutos": len(grupo),
            "n_excluidos": int((~grupo["anuncio_valido"]).sum()),
            "precio_medio": round(float(pd.Series(precios).mean()), 2),
            "precio_mediana": round(float(pd.Series(precios).median()), 2),
            "mediana_m2_w": round(mediana_m2_w, 2) if mediana_m2_w == mediana_m2_w else None,
            "ic": ic,
            "n": len(precios),
        }

    filas = []
    for _, row in dim.iterrows():
        code = str(row["codigo_ine"])
        a = agg.get(code, {
            "n_brutos": 0, "n_excluidos": 0, "precio_medio": None, "precio_mediana": None,
            "mediana_m2_w": None,
            "ic": {"mediana": float("nan"), "lo": float("nan"), "hi": float("nan"), "amplitud_pct": float("nan")},
            "n": 0,
        })
        precio_mediana = a["precio_mediana"]

        if precio_mediana is not None:
            # Esfuerzo = precio mensual / salario mensual x 100 (misma formula que T-02).
            esfuerzo_18_34 = precio_mediana / salario_18_34_2026 * 100
            esfuerzo_16_29 = precio_mediana / salario_16_29_2026 * 100
            esfuerzo_sin_ajuste = precio_mediana / salario_18_34_2024 * 100
            renta_mes = row.get("renta_joven_mes_18_34")
            esfuerzo_renta = (
                precio_mediana / float(renta_mes) * 100
                if pd.notna(renta_mes) and float(renta_mes) > 0 else None
            )
        else:
            esfuerzo_18_34 = esfuerzo_16_29 = esfuerzo_sin_ajuste = esfuerzo_renta = None

        salarios_banda = [salario_18_34_2024, salario_18_34_2026]
        renta_mes = row.get("renta_joven_mes_18_34")
        if pd.notna(renta_mes) and float(renta_mes) > 0:
            salarios_banda.append(float(renta_mes))
        banda_lo, banda_hi = _banda(precio_mediana, salarios_banda)

        n = a["n"]
        ic = a["ic"]
        filas.append({
            # --- columnas historicas (mismos nombres y orden) ---
            "codigo_ine": code,
            "nombre_canonico": row.get("nombre_canonico", ""),
            "territorio": row.get("territorio", ""),
            "n_anuncios_2026": n,
            "n_precio_2026": n,
            "precio_medio_anuncio_2026_eur_mes": a["precio_medio"],
            "precio_mediana_anuncio_2026_eur_mes": a["precio_mediana"],
            "mediana_m2_winsorizada_2026_eur_m2": a["mediana_m2_w"],
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
            # --- columnas nuevas: auditoria, incertidumbre y banda ---
            "n_brutos_2026": a["n_brutos"],
            "n_excluidos_2026": a["n_excluidos"],
            "ic95_lo_pct_18_34": (
                round(ic["lo"] / salario_18_34_2026 * 100, 2)
                if ic["lo"] == ic["lo"] else None
            ),
            "ic95_hi_pct_18_34": (
                round(ic["hi"] / salario_18_34_2026 * 100, 2)
                if ic["hi"] == ic["hi"] else None
            ),
            "ic95_amplitud_pct_18_34": ic["amplitud_pct"] if ic["amplitud_pct"] == ic["amplitud_pct"] else None,
            "metodo_precio": "mediana_anuncios" if n else "sin_dato",
            "metodo_ic": "bootstrap_mediana_2000_semilla_fija" if n > 1 else ("n_1_sin_ic" if n == 1 else "no_aplicable"),
            "flag_n_insuficiente": n < 5,
            "flag_concluyente": bool(n >= 10 and ic["amplitud_pct"] == ic["amplitud_pct"] and ic["amplitud_pct"] < 30),
            "esfuerzo_sin_ajuste_pct_18_34": round(esfuerzo_sin_ajuste, 2) if esfuerzo_sin_ajuste is not None else None,
            "esfuerzo_renta_joven_2024_pct_18_34": round(esfuerzo_renta, 2) if esfuerzo_renta is not None else None,
            "esfuerzo_banda_lo_pct_18_34": banda_lo,
            "esfuerzo_banda_hi_pct_18_34": banda_hi,
            "fuente_numerador": FUENTE_NUMERADOR,
            "fuente_denominador": FUENTE_DENOMINADOR,
            "caveat": CAVEAT,
        })

    df_out = pd.DataFrame(filas)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUT, index=False, encoding="utf-8-sig")

    n_con_dato = int(df_out["esfuerzo_mercado_2026_pct_18_34"].notna().sum())
    n_usados = int(df_out["n_anuncios_2026"].sum())
    n_excluidos = int(df_out["n_excluidos_2026"].sum())
    assert n_usados == meta["n_usados"], f"conciliacion: CSV {n_usados} != filtro {meta['n_usados']}"
    assert n_usados + n_excluidos == meta["n_con_precio"], "conciliacion de anuncios con precio"

    print(
        f"OK: {OUT.name} ({len(df_out)} filas, {n_con_dato} con esfuerzo, "
        f"{n_usados} anuncios usados, {n_excluidos} excluidos, "
        f"{meta['n_sin_precio']} sin precio, flag_ipc={flag_ipc})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
