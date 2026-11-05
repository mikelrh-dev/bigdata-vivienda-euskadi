"""Descarga el indicador municipal de VPO terminadas (Udalmap 73).

Fuente: Open Data Euskadi, "Indicadores municipales de sostenibilidad:
Viviendas protegidas (VPO) terminadas en el último quinquenio (‰ habitantes)".
Serie 2004-2024, con bloques de territorio, comarca y municipio.

Flujo seguro:
  1. Descarga a ``data/staging/vpo/indicator.csv`` (no toca el bronce).
  2. Valida que haya 252 municipios con código de 5 dígitos y valor 2024
     dentro de rango.
  3. Solo con ``--promote`` copia a ``data/raw/`` con ``assert_raw_writable``.

Uso:
    python extract/26_vpo_terminadas.py
    python extract/26_vpo_terminadas.py --promote
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parents[1]
STAGING_DIR = BASE / "data" / "staging" / "vpo"
STAGING_CSV = STAGING_DIR / "indicator.csv"
RAW_CSV = BASE / "data" / "raw" / "udalmap_vpo_terminadas.csv"

URL = (
    "https://opendata.euskadi.eus/contenidos/estadistica/"
    "udalmap_indicador_73/es_def/adjuntos/indicator.csv"
)
ANIO = "2024"
MIN_MUNICIPIOS = 252  # el origen incluye ademas municipios disueltos (272 codigos)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _leer_filas(path: Path) -> list[list[str]]:
    with path.open(encoding="latin-1", newline="") as fh:
        return list(csv.reader(fh, delimiter=";"))


def validar(path: Path) -> tuple[int, float, float]:
    """Devuelve (n municipios, mínimo, máximo) del año de referencia."""
    filas = _leer_filas(path)
    cabecera = next((f for f in filas if f and f[0].strip().lower() == "entidad"), None)
    if cabecera is None:
        raise ValueError("falta la cabecera 'Entidad'")
    try:
        idx = cabecera.index(ANIO)
    except ValueError as exc:
        raise ValueError(f"falta la columna {ANIO}") from exc

    valores: list[float] = []
    codigos: set[str] = set()
    for fila in filas:
        if not fila or not fila[0].strip().isdigit() or len(fila[0].strip()) != 5:
            continue
        codigos.add(fila[0].strip())
        crudo = fila[idx].strip()
        if not crudo:
            continue
        valores.append(float(crudo.replace(".", "").replace(",", ".")))

    if len(codigos) < MIN_MUNICIPIOS:
        raise ValueError(f"esperados al menos {MIN_MUNICIPIOS} municipios, encontrados {len(codigos)}")
    if len(valores) < MIN_MUNICIPIOS:
        raise ValueError(f"esperados al menos {MIN_MUNICIPIOS} valores {ANIO}, encontrados {len(valores)}")
    if min(valores) < 0 or max(valores) > 100:
        raise ValueError(f"valor fuera de rango: {min(valores)}..{max(valores)}")
    return len(codigos), min(valores), max(valores)


def descargar() -> Path:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.get(URL, timeout=90)
    resp.raise_for_status()
    STAGING_CSV.write_bytes(resp.content)
    return STAGING_CSV


def promover(origen: Path) -> Path:
    sys.path.insert(0, str(BASE))
    from transform._raw_guard import assert_raw_writable

    assert_raw_writable(
        "append autorizado 2026-11-05: indicador 73 VPO terminadas, "
        "fuente oficial Open Data Euskadi, validado en staging"
    )
    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origen, RAW_CSV)
    return RAW_CSV


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Indicador 73 VPO terminadas")
    parser.add_argument("--promote", action="store_true", help="copiar a data/raw")
    parser.add_argument("--sin-descargar", action="store_true", help="usar el staging existente")
    args = parser.parse_args(argv)

    origen = STAGING_CSV if args.sin_descargar else descargar()
    n, vmin, vmax = validar(origen)
    print(f"staging OK: {origen} ({n} municipios, {ANIO} {vmin:.2f}-{vmax:.2f} ‰)")
    print("el parser filtra a los 252 de dim_municipios")
    print(f"sha256 staging: {_sha256(origen)}")
    if args.promote:
        destino = promover(origen)
        print(f"raw: {destino} ({destino.stat().st_size} bytes)")
        print(f"sha256 raw: {_sha256(destino)}")
        print(f"promovido: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    else:
        print("sin --promote: data/raw no se ha tocado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
