"""Añade metadatos y huella (fingerprint) a los JSON crudos de anuncios.

Lee los JSON crudos de Fotocasa, Pisos.com, habitaciones y enriquecidos,
y genera copias ``*_meta.json`` con, en cada registro:
  - ``_metadata``: {source_portal, modality, scraped_at, raw_file_hdfs_path, schema_version}
  - ``property_fingerprint``: hash de codigo_ine + superficie (redondeada a 5 m2)
    + habitaciones + precio (redondeado a 50 EUR).

Los originales en data/raw/ no se modifican.

Uso:
    python extract/14_add_metadata_fingerprint.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("metadata_fingerprint")

SCHEMA_VERSION = "1.0"

# Ficheros crudos de entrada -> se genera <stem>_meta.json
ENTRADAS = [
    "anuncios_fotocasa.json",
    "anuncios_pisos.json",
    "anuncios_fotocasa_habitaciones.json",
    "anuncios_pisos_habitaciones.json",
    "anuncios_fotocasa_enriquecido.json",
    "anuncios_pisos_enriquecido.json",
]


def _inferir_portal_modality(nombre: str) -> tuple[str, str]:
    low = nombre.lower()
    portal = "fotocasa" if "fotocasa" in low else "pisos"
    modality = "habitaciones" if "habitaciones" in low else "alquiler"
    return portal, modality


def _redondear_5(valor) -> int | None:
    if valor is None:
        return None
    try:
        return int(round(float(valor) / 5.0) * 5)
    except (TypeError, ValueError):
        return None


def _redondear_50(valor) -> int | None:
    if valor is None:
        return None
    try:
        return int(round(float(valor) / 50.0) * 50)
    except (TypeError, ValueError):
        return None


def _fingerprint(reg: dict) -> str:
    codigo_ine = reg.get("codigo_ine")
    superficie_r = _redondear_5(reg.get("superficie_m2"))
    habitaciones = reg.get("habitaciones")
    precio_r = _redondear_50(reg.get("precio_eur"))
    clave = f"{codigo_ine}|{superficie_r}|{habitaciones}|{precio_r}"
    return hashlib.md5(clave.encode("utf-8")).hexdigest()


def _scraped_at(metadata: dict) -> str | None:
    for clave in ("fecha_extraccion", "fecha", "scraped_at", "fecha_scraping"):
        valor = metadata.get(clave)
        if valor:
            return str(valor)
    return None


def procesar_fichero(nombre: str) -> Path | None:
    origen = RAW_DIR / nombre
    if not origen.exists():
        log.warning("No existe %s, se omite", origen)
        return None

    try:
        crudo = json.loads(origen.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log.error("Error leyendo %s: %s", origen, exc)
        return None

    if isinstance(crudo, list):
        datos = crudo
        metadata = {}
    elif isinstance(crudo, dict):
        datos = crudo.get("datos", [])
        if not isinstance(datos, list):
            datos = []
        metadata = crudo.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
    else:
        log.error("Estructura no soportada en %s", origen)
        return None

    portal, modality = _inferir_portal_modality(nombre)
    scraped_at = _scraped_at(metadata)

    n = 0
    for reg in datos:
        if not isinstance(reg, dict):
            continue
        reg["_metadata"] = {
            "source_portal": reg.get("fuente") or portal,
            "modality": modality,
            "scraped_at": scraped_at,
            "raw_file_hdfs_path": f"/raw/{nombre}",
            "schema_version": SCHEMA_VERSION,
        }
        reg["property_fingerprint"] = _fingerprint(reg)
        n += 1

    destino = RAW_DIR / nombre.replace(".json", "_meta.json")
    guardar_json(destino, datos, metadata=metadata)
    log.info("%s -> %s (%d registros)", nombre, destino.name, n)
    return destino


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Añade _metadata y property_fingerprint a los JSON crudos"
    )
    parser.add_argument(
        "--solo",
        nargs="*",
        default=None,
        help="Nombres de ficheros de entrada a procesar (por defecto todos)",
    )
    args = parser.parse_args()

    entradas = args.solo if args.solo else ENTRADAS
    ok = 0
    for nombre in entradas:
        if procesar_fichero(nombre) is not None:
            ok += 1
    log.info("Procesados %d/%d ficheros", ok, len(entradas))
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
