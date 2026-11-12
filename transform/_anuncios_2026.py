"""Libreria de carga y filtrado unico de los anuncios 2026.

Una sola definicion de que anuncio entra en la capa de esfuerzo de mercado 2026,
para que `calcular_esfuerzo_mercado_2026.py` y `..._por_tipo.py` no puedan
divergir.

Regla de filtrado (explicita, auditable):
  - se descartan las filas sin `precio_eur` (no son anuncio valorable);
  - se descartan las filas con `motivo_exclusion` (las marco el propio pipeline:
    IQR, superficie fuera de rango, precio/m2 fuera de 3-50);
  - se descarta alquiler temporal si la columna existe (no comparable con
    larga estancia: ~24 % mas caro).

NO escribe nada ni toca raw. Solo lectura de `data/procesado`.

Uso:
    from _anuncios_2026 import cargar_anuncios_2026, mediana_con_ic
    df, meta = cargar_anuncios_2026()
    validos = df[df["anuncio_valido"]]
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROC = PROJECT_ROOT / "data" / "procesado"
ANUNCIOS = PROC / "anuncios_vivienda_residencial_filtrado.csv"

NUMERICAS = ("precio_eur", "superficie_m2", "habitaciones")
VERDADEROS = {"true", "1", "si", "sí", "yes"}

REPLICAS_BOOTSTRAP = 2000
SEMILLA_BASE = 20260101


def cargar_anuncios_2026(ruta: Path | None = None) -> tuple[pd.DataFrame, dict[str, int]]:
    """Carga los anuncios 2026 con su marca de validez y contadores de auditoria.

    Devuelve ``(df, meta)``. ``df`` contiene **todas** las filas con precio y una
    columna booleana ``anuncio_valido``; ``meta`` resume cuantas se descartaron
    y por que, para que la exclusion quede registrada y no silenciosa.
    """
    ruta = ruta or ANUNCIOS
    if not ruta.exists():
        raise FileNotFoundError(
            f"Falta {ruta.name}. Ejecuta primero transform/generar_anuncios_residencial_filtrado.py"
        )

    df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    df["codigo_ine"] = df["codigo_ine"].astype(str).str.zfill(5)
    for col in NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    n_filas = len(df)

    # 1) Solo filas valorables.
    sin_precio = df["precio_eur"].isna()
    n_sin_precio = int(sin_precio.sum())
    df = df[~sin_precio].copy()

    # 2) Marca de exclusion de calidad del propio pipeline.
    motivo = df["motivo_exclusion"].astype(str).str.strip()
    excluido = df["motivo_exclusion"].notna() & motivo.ne("") & motivo.ne("nan")

    # 3) Temporal fuera (defensivo: hoy el fichero ya es solo larga estancia).
    if "alquiler_temporal" in df.columns:
        temporal = df["alquiler_temporal"].astype(str).str.strip().str.lower().isin(VERDADEROS)
    else:
        temporal = pd.Series(False, index=df.index)

    df["anuncio_valido"] = ~excluido & ~temporal
    df["precio_m2"] = (df["precio_eur"] / df["superficie_m2"]).where(df["superficie_m2"] > 0)

    meta = {
        "n_filas": n_filas,
        "n_sin_precio": n_sin_precio,
        "n_con_precio": len(df),
        "n_excluidos_calidad": int(excluido.sum()),
        "n_temporal": int(temporal.sum()),
        "n_usados": int(df["anuncio_valido"].sum()),
    }
    return df, meta


def mediana(valores: list[float] | np.ndarray) -> float:
    """Mediana simple; NaN si no hay valores."""
    if valores is None or len(valores) == 0:
        return float("nan")
    return float(np.median(np.asarray(valores, dtype=float)))


def mediana_con_ic(
    valores: list[float] | np.ndarray,
    semilla: int = SEMILLA_BASE,
    replicas: int = REPLICAS_BOOTSTRAP,
) -> dict[str, float]:
    """Mediana con IC95 % bootstrap (percentil), determinista por semilla.

    Con n=1 el IC colapsa al propio valor (no se finge incertidumbre que no se
    puede estimar) y ``amplitud_pct`` queda en 0.
    """
    arr = np.asarray(valores, dtype=float)
    n = len(arr)
    if n == 0:
        return {"mediana": float("nan"), "lo": float("nan"), "hi": float("nan"), "amplitud_pct": float("nan")}
    med = float(np.median(arr))
    if n == 1:
        return {"mediana": med, "lo": med, "hi": med, "amplitud_pct": 0.0}

    rng = np.random.default_rng(int(semilla))
    idx = rng.integers(0, n, size=(replicas, n))
    medianas = np.median(arr[idx], axis=1)
    lo, hi = np.percentile(medianas, [2.5, 97.5])
    amplitud = float((hi - lo) / med * 100) if med else float("nan")
    return {"mediana": med, "lo": float(lo), "hi": float(hi), "amplitud_pct": round(amplitud, 2)}
