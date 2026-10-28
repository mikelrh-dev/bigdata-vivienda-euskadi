"""Añade el campo GeoJSON 'location' (Point) a los *_meta.json.

Lee los JSON crudos enriquecidos con metadatos (``*_meta.json``) y genera
copias ``*_geo.json`` en las que cada registro con latitud/longitud recibe:

    "location": {"type": "Point", "coordinates": [lon, lat]}

siguiendo RFC 7946 (longitud, latitud). Los originales no se modifican.

Uso:
    python extract/15_add_geojson.py
    python extract/15_add_geojson.py --solo anuncios_fotocasa_meta.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("add_geojson")

# Pares (lat, lon) aceptados para extraer coordenadas de un registro.
_LAT_KEYS = ("latitud", "latitude", "lat")
_LON_KEYS = ("longitud", "longitude", "lon", "lng")


def _extraer_coordenadas(reg: dict):
    """Devuelve (lat, lon) válidos o None si el registro no tiene coordenadas."""
    lat = None
    lon = None

    # 1) Claves directas en el registro.
    for kl in _LAT_KEYS:
        if kl in reg and reg.get(kl) is not None:
            lat = reg.get(kl)
            break
    for kl in _LON_KEYS:
        if kl in reg and reg.get(kl) is not None:
            lon = reg.get(kl)
            break

    # 2) Coordenadas anidadas (p. ej. enriquecido: ubicacion.coords).
    if lat is None or lon is None:
        ub = reg.get("ubicacion")
        if isinstance(ub, dict):
            coords = ub.get("coords") or ub.get("coordenadas")
            if isinstance(coords, dict):
                if lat is None:
                    for kl in _LAT_KEYS:
                        if coords.get(kl) is not None:
                            lat = coords.get(kl)
                            break
                if lon is None:
                    for kl in _LON_KEYS:
                        if coords.get(kl) is not None:
                            lon = coords.get(kl)
                            break

    if lat is None or lon is None:
        return None
    try:
        lat_f = float(lat)  # type: ignore[arg-type]
        lon_f = float(lon)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None

    # Validación básica de rangos WGS84.
    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
        return None
    return lat_f, lon_f


def _nombre_salida(nombre: str) -> str:
    if nombre.endswith("_meta.json"):
        return nombre[: -len("_meta.json")] + "_geo.json"
    if nombre.endswith(".json"):
        return nombre[: -len(".json")] + "_geo.json"
    return nombre + "_geo.json"


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

    n_total = 0
    n_geo = 0
    for reg in datos:
        if not isinstance(reg, dict):
            continue
        n_total += 1
        coords = _extraer_coordenadas(reg)
        if coords is not None:
            lat, lon = coords
            reg["location"] = {"type": "Point", "coordinates": [lon, lat]}
            n_geo += 1

    destino = RAW_DIR / _nombre_salida(nombre)
    guardar_json(destino, datos, metadata=metadata)
    log.info("%s -> %s (%d/%d registros con location)", nombre, destino.name, n_geo, n_total)
    return destino


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Añade campo GeoJSON 'location' a los *_meta.json"
    )
    parser.add_argument(
        "--solo",
        nargs="*",
        default=None,
        help="Nombres de ficheros de entrada a procesar (por defecto todos *_meta.json)",
    )
    args = parser.parse_args()

    if args.solo:
        entradas = args.solo
    else:
        entradas = sorted(p.name for p in RAW_DIR.glob("*_meta.json"))

    ok = 0
    for nombre in entradas:
        if procesar_fichero(nombre) is not None:
            ok += 1
    log.info("Procesados %d/%d ficheros", ok, len(entradas))
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
