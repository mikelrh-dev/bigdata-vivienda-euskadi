"""Descarga el indicador municipal de VPO terminadas (Udalmap 73).

Fuente: Open Data Euskadi, "Indicadores municipales de sostenibilidad:
Viviendas protegidas (VPO) terminadas en el último quinquenio (‰ habitantes)".
Serie 2004-2024, con bloques de territorio, comarca y municipio.

Flujo seguro:
  1. Descarga el CSV en memoria (no escribe staging ni toca el bronce).
  2. Valida que haya al menos 252 códigos de 5 dígitos con valor 2024
     dentro de rango (el origen trae 272, incluidos municipios disueltos).
  3. Solo con ``--promote`` escribe en ``data/raw/`` con
     ``assert_raw_writable``. Si el raw ya existe con el mismo SHA no lo
     reescribe; si existe con otro SHA se niega para preservar la
     inmutabilidad del bronce.
  4. ``--desde-raw`` valida el raw existente sin red (alias histórico:
     ``--sin-descargar``).

Uso:
    python extract/26_vpo_terminadas.py
    python extract/26_vpo_terminadas.py --promote
    python extract/26_vpo_terminadas.py --desde-raw
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parents[1]
RAW_CSV = BASE / "data" / "raw" / "udalmap_vpo_terminadas.csv"

URL = (
    "https://opendata.euskadi.eus/contenidos/estadistica/"
    "udalmap_indicador_73/es_def/adjuntos/indicator.csv"
)
ANIO = "2024"
MIN_MUNICIPIOS = 252  # el origen incluye ademas municipios disueltos (272 codigos)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _leer_filas(payload: bytes) -> list[list[str]]:
    texto = payload.decode("latin-1")
    return list(csv.reader(io.StringIO(texto, newline=""), delimiter=";"))


def validar(payload: bytes) -> tuple[int, float, float]:
    """Devuelve (n códigos de 5 dígitos, mínimo, máximo) del año de referencia."""
    filas = _leer_filas(payload)
    cabecera = next(
        (f for f in filas if f and f[0].strip().lower() == "entidad"),
        None,
    )
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
        if len(fila) <= idx:
            continue
        codigos.add(fila[0].strip())
        crudo = fila[idx].strip()
        if not crudo:
            continue
        valores.append(float(crudo.replace(".", "").replace(",", ".")))

    if len(codigos) < MIN_MUNICIPIOS:
        raise ValueError(
            f"esperados al menos {MIN_MUNICIPIOS} códigos de 5 dígitos, encontrados {len(codigos)}"
        )
    if len(valores) < MIN_MUNICIPIOS:
        raise ValueError(
            f"esperados al menos {MIN_MUNICIPIOS} valores {ANIO}, encontrados {len(valores)}"
        )
    if min(valores) < 0 or max(valores) > 100:
        raise ValueError(f"valor fuera de rango: {min(valores)}..{max(valores)}")
    return len(codigos), min(valores), max(valores)


def descargar() -> bytes:
    resp = requests.get(URL, timeout=90)
    resp.raise_for_status()
    return resp.content


def promover(payload: bytes) -> tuple[Path, bool]:
    """Escribe el payload en raw solo si no existe o si el SHA es idéntico.

    Devuelve ``(ruta, escrito)``. ``escrito=False`` significa que el raw ya
    estaba con el mismo SHA y no se ha tocado. Un SHA distinto se rechaza:
    el bronce es inmutable y no se sobrescribe.
    """
    nuevo = _sha256_bytes(payload)
    if RAW_CSV.exists():
        actual = _sha256(RAW_CSV)
        if actual == nuevo:
            print(f"raw ya existe con el mismo SHA ({nuevo}); no se reescribe")
            return RAW_CSV, False
        raise SystemExit(
            f"raw ya existe con otro SHA ({actual} != {nuevo}); "
            "no se sobrescribe (raw inmutable)"
        )

    sys.path.insert(0, str(BASE))
    from transform._raw_guard import assert_raw_writable

    assert_raw_writable(
        "append autorizado 2026-11-05: indicador 73 VPO terminadas, "
        "fuente oficial Open Data Euskadi, validado en memoria"
    )
    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_CSV.write_bytes(payload)
    return RAW_CSV, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Indicador 73 VPO terminadas")
    parser.add_argument("--promote", action="store_true", help="copiar a data/raw")
    parser.add_argument(
        "--desde-raw",
        "--sin-descargar",
        dest="desde_raw",
        action="store_true",
        help="validar data/raw/udalmap_vpo_terminadas.csv sin descargar",
    )
    args = parser.parse_args(argv)

    if args.desde_raw:
        if not RAW_CSV.exists():
            raise SystemExit(
                f"falta {RAW_CSV}: ejecuta sin --desde-raw para descargar"
            )
        payload = RAW_CSV.read_bytes()
        print(f"origen: raw existente {RAW_CSV}")
    else:
        payload = descargar()
        print(f"origen: descarga {URL}")

    n, vmin, vmax = validar(payload)
    print(
        f"validacion OK: {n} codigos de 5 digitos (>= {MIN_MUNICIPIOS}), "
        f"{ANIO} {vmin:.2f}-{vmax:.2f} por mil"
    )
    print("el parser filtra a los 252 de dim_municipios")
    print(f"sha256 payload: {_sha256_bytes(payload)}")

    if args.promote:
        if args.desde_raw:
            raise SystemExit("--promote no aplica con --desde-raw")
        destino, escrito = promover(payload)
        print(f"raw: {destino} ({destino.stat().st_size} bytes)")
        print(f"sha256 raw: {_sha256(destino)}")
        if escrito:
            print(f"promovido: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
        else:
            print("sin cambios: el raw ya estaba con el mismo SHA")
    else:
        print("sin --promote: data/raw no se ha tocado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
