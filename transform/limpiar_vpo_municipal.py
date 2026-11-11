"""Convierte el indicador 73 (VPO terminadas) en tabla municipal limpia.

Entrada:  data/raw/udalmap_vpo_terminadas.csv (latin-1, ';', bloques mixtos)
Salida:   data/procesado/vpo_municipal.csv (utf-8-sig)

El CSV oficial mezcla filas de territorio, comarca y municipio. Solo se
conservan las filas con código de 5 dígitos (municipio) y se toma el año de
referencia del indicador. El valor es un FLUJO quinquenal en ‰ habitantes,
no un stock de viviendas.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR, RAW_DIR  # noqa: E402

RAW = RAW_DIR / "udalmap_vpo_terminadas.csv"
DIM = PROCESADO_DIR / "dim_municipios.csv"
PROC = PROCESADO_DIR / "vpo_municipal.csv"

ANIO = "2024"
FUENTE = "Open Data Euskadi - Udalmap indicador 73 (VPO terminadas ultimo quinquenio)"
FUENTE_URL = (
    "https://opendata.euskadi.eus/contenidos/estadistica/"
    "udalmap_indicador_73/es_def/adjuntos/indicator.csv"
)


def _numero(crudo: str) -> float | None:
    texto = (crudo or "").strip()
    if not texto:
        return None
    return float(texto.replace(".", "").replace(",", "."))


def parsear(path: Path = RAW) -> pd.DataFrame:
    with path.open(encoding="latin-1", newline="") as fh:
        filas = list(csv.reader(fh, delimiter=";"))

    cabecera = next((f for f in filas if f and f[0].strip().lower() == "entidad"), None)
    if cabecera is None:
        raise ValueError("falta la cabecera 'Entidad'")
    idx_valor = cabecera.index(ANIO)

    registros = []
    for fila in filas:
        if not fila or len(fila) <= idx_valor:
            continue
        codigo = fila[0].strip()
        if not codigo.isdigit() or len(codigo) != 5:
            continue
        registros.append(
            {
                "codigo_ine": codigo,
                "municipio": fila[1].strip(),
                "vpo_terminadas_por_mil": _numero(fila[idx_valor]),
                "anio_fuente": int(ANIO),
                "fuente": FUENTE,
                "fuente_url": FUENTE_URL,
            }
        )

    df = pd.DataFrame(registros)
    if df.empty:
        raise ValueError("sin filas municipales")

    # El origen mantiene municipios disueltos: se conserva la referencia viva.
    referencia = set(pd.read_csv(DIM, dtype={"codigo_ine": str})["codigo_ine"].str.zfill(5))
    descartados = sorted(set(df["codigo_ine"]) - referencia)
    df = df[df["codigo_ine"].isin(referencia)].copy()

    # Un municipio sin valor (Usansolo, segregado en 2023) se conserva con
    # nulo explicito: "sin dato" no es cero.
    df["vpo_terminadas_por_mil"] = pd.to_numeric(
        df["vpo_terminadas_por_mil"], errors="coerce"
    ).round(2)
    df = df.drop_duplicates("codigo_ine", keep="first").sort_values("codigo_ine")
    print(f"descartados {len(descartados)} codigos sin municipio vivo: {descartados}")
    return df.reset_index(drop=True)


def main() -> int:
    if not RAW.exists():
        raise SystemExit(f"falta {RAW}: ejecuta extract/26_vpo_terminadas.py")
    df = parsear()
    if len(df) != 252:
        raise SystemExit(f"esperados 252 municipios, obtenidos {len(df)}")
    faltan = set(pd.read_csv(DIM, dtype={"codigo_ine": str})["codigo_ine"].str.zfill(5)) - set(df["codigo_ine"])
    if faltan:
        raise SystemExit(f"sin dato VPO 2024 en {len(faltan)} municipios: {sorted(faltan)}")
    valores = df["vpo_terminadas_por_mil"].dropna()
    if not valores.between(0, 100).all():
        raise SystemExit("valores fuera de 0-100 ‰")
    PROC.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROC, index=False, encoding="utf-8-sig")
    print(f"Generado {PROC}: {len(df)} filas, {len(df.columns)} cols")
    print(
        "VPO terminadas "
        f"{ANIO}: mediana {df['vpo_terminadas_por_mil'].median():.2f} ‰, "
        f"max {df['vpo_terminadas_por_mil'].max():.2f} ‰, "
        f"sin dato {int(df['vpo_terminadas_por_mil'].isna().sum())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
