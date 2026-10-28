"""Enriquece los JSON de anuncios con campos anidados 'ubicacion' y 'equipamiento'.

Lee data/raw/anuncios_fotocasa.json y anuncios_pisos.json SIN modificarlos y
genera data/raw/anuncios_fotocasa_enriquecido.json y
anuncios_pisos_enriquecido.json.

Uso:
  python extract/12_enriquecer_json_anidado.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("enriquecer_json_anidado")

CAMPOS_EQUIPAMIENTO = [
    "calefaccion",
    "parking",
    "ascensor",
    "terraza",
    "trastero",
    "jardin",
    "exterior",
    "alquiler_temporal",
]

PROVINCIA_POR_PREFIJO = {
    "01": "Araba/Álava",
    "20": "Gipuzkoa",
    "48": "Bizkaia",
}


def _ubicacion_fotocasa(reg: dict) -> dict:
    return {
        "coords": {
            "lat": reg.get("latitud"),
            "lon": reg.get("longitud"),
        },
        "barrio": reg.get("barrio"),
        "distrito": reg.get("distrito"),
        "comarca": reg.get("comarca"),
        "codigo_postal": reg.get("codigo_postal"),
        "municipio": reg.get("municipio"),
        "provincia": reg.get("provincia"),
        "codigo_ine": reg.get("codigo_ine"),
        "nombre_canonico": reg.get("nombre_canonico"),
    }


def _ubicacion_pisos(reg: dict) -> dict:
    codigo_ine = reg.get("codigo_ine")
    provincia = None
    if codigo_ine and len(str(codigo_ine)) >= 2:
        provincia = PROVINCIA_POR_PREFIJO.get(str(codigo_ine)[:2])
    municipio = reg.get("nombre_canonico_resuelto") or reg.get("municipio_busqueda")
    nombre_canonico = reg.get("nombre_canonico") or reg.get("nombre_canonico_resuelto")
    return {
        "coords": {"lat": None, "lon": None},
        "barrio": None,
        "distrito": None,
        "comarca": None,
        "codigo_postal": None,
        "municipio": municipio,
        "provincia": provincia,
        "codigo_ine": codigo_ine,
        "nombre_canonico": nombre_canonico,
    }


def _equipamiento(reg: dict) -> list[str]:
    return [c for c in CAMPOS_EQUIPAMIENTO if reg.get(c) is not None]


def _procesar(entrada: Path, salida: Path, ubicacion_fn) -> int:
    data = json.loads(entrada.read_text(encoding="utf-8"))
    meta = data.get("metadata", {}) if isinstance(data, dict) else {}
    regs = data.get("datos", data) if isinstance(data, dict) else data
    if not isinstance(regs, list):
        raise ValueError(f"{entrada}: 'datos' no es una lista")
    for reg in regs:
        reg["ubicacion"] = ubicacion_fn(reg)
        reg["equipamiento"] = _equipamiento(reg)
    meta = {**meta, "enriquecido_anidado": True}
    guardar_json(salida, regs, metadata=meta)
    log.info("%s: %d anuncios -> %s", entrada.name, len(regs), salida.name)
    return len(regs)


def main() -> int:
    _procesar(
        RAW_DIR / "anuncios_fotocasa.json",
        RAW_DIR / "anuncios_fotocasa_enriquecido.json",
        _ubicacion_fotocasa,
    )
    _procesar(
        RAW_DIR / "anuncios_pisos.json",
        RAW_DIR / "anuncios_pisos_enriquecido.json",
        _ubicacion_pisos,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
