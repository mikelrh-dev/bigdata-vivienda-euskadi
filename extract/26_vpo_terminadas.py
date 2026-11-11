"""Descarga el indicador municipal de VPO terminadas (Udalmap 73).

Fuente: Open Data Euskadi, "Indicadores municipales de sostenibilidad:
Viviendas protegidas (VPO) terminadas en el último quinquenio (‰ habitantes)".
Serie 2004-2024, con bloques de territorio, comarca y municipio.

Flujo:
  1. Descarga el CSV a memoria (no escribe nada todavía).
  2. Valida que haya 252 municipios con código de 5 dígitos y valor 2024
     dentro de rango.
  3. Solo si la validación pasa, escribe ``raw/udalmap_vpo_terminadas.csv``
     de una vez y de forma atómica. Si algo falla, ``raw`` queda intacto.

Uso:
    python extract/26_vpo_terminadas.py
"""

from __future__ import annotations

import csv
import hashlib
import io
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, guardar_meta, write_raw  # noqa: E402

RAW_CSV = RAW_DIR / "udalmap_vpo_terminadas.csv"

URL = (
    "https://opendata.euskadi.eus/contenidos/estadistica/"
    "udalmap_indicador_73/es_def/adjuntos/indicator.csv"
)
ANIO = "2024"
MIN_MUNICIPIOS = 252  # el origen incluye ademas municipios disueltos (272 codigos)


def _sha256(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def _leer_filas(contenido: bytes) -> list[list[str]]:
    texto = contenido.decode("latin-1")
    return list(csv.reader(io.StringIO(texto, newline=""), delimiter=";"))


def validar(contenido: bytes) -> tuple[int, float, float]:
    """Devuelve (n municipios, mínimo, máximo) del año de referencia."""
    filas = _leer_filas(contenido)
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


def descargar() -> bytes:
    resp = requests.get(URL, timeout=90)
    resp.raise_for_status()
    return resp.content


def escribir_raw(contenido: bytes) -> Path:
    return write_raw(RAW_CSV, contenido)


def main() -> int:
    contenido = descargar()
    n, vmin, vmax = validar(contenido)
    print(f"validado: {n} municipios, {ANIO} {vmin:.2f}-{vmax:.2f} ‰")
    print("el parser filtra a los 252 de dim_municipios")
    print(f"sha256 origen: {_sha256(contenido)}")
    destino = escribir_raw(contenido)
    guardar_meta(destino, {
        "fuente": "Open Data Euskadi - Udalmap indicador 73 (VPO terminadas)",
        "url": URL,
        "n_registros": n,
    })
    print(f"raw: {destino} ({destino.stat().st_size} bytes)")
    print(f"sha256 raw: {_sha256(destino.read_bytes())}")
    print(f"escrito: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
