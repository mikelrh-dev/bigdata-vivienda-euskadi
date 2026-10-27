"""Extracción de anuncios de alquiler de Idealista vía RealtyAPI.io.

Fuente OPCIONAL y no oficial: wrapper de Idealista con autenticación por
API key. Complementa a Fotocasa; no es imprescindible para el contrato.

Uso:
  python extract/09_realtyapi.py                       # municipios de prueba
  python extract/09_realtyapi.py --municipios Bilbao "Donostia / San Sebastián"
  python extract/09_realtyapi.py --todos --max-paginas 2
  python extract/09_realtyapi.py --max-municipios 5
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("realtyapi")

BASE_URL = "https://idealista.realtyapi.io"
MUNICIPIOS_PRUEBA = ["Bilbao", "Donostia / San Sebastián", "Vitoria-Gasteiz"]


def _cargar_env() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_cargar_env()


def _obtener_key() -> str:
    key = os.getenv("REALTYAPI_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Falta REALTYAPI_KEY en .env. Es una fuente opcional; "
            "déjala vacía si no quieres usarla."
        )
    return key


def _slug_busqueda(nombre: str) -> str:
    return nombre.split("/")[0].strip()


def _autocompletar(cliente: Cliente, nombre: str) -> str | None:
    """Devuelve el locationId más adecuado para el municipio."""
    buscado = _slug_busqueda(nombre).lower()
    try:
        resp = cliente.get(
            f"{BASE_URL}/autocomplete",
            params={"input": buscado, "country": "es"},
        )
    except RuntimeError as exc:
        log.error("Autocomplete %s: %s", nombre, exc)
        return None
    data = resp.json()
    resultados = data.get("searchResults", [])
    if not resultados:
        log.warning("Sin resultados de autocomplete para %s", nombre)
        return None

    # Preferir coincidencia exacta por nombre de municipio.
    for r in resultados:
        if str(r.get("name", "")).lower().startswith(buscado):
            return r.get("locationId")
    return resultados[0].get("locationId")


def _normalizar(anuncio: dict, municipio_busqueda: str, location_id: str) -> dict:
    return {
        "id_anuncio": anuncio.get("propertyCode"),
        "url": anuncio.get("url"),
        "precio_eur": anuncio.get("price"),
        "moneda": anuncio.get("currency"),
        "operacion": anuncio.get("operation"),
        "tipo_inmueble": anuncio.get("propertyType"),
        "tipo_extendido": anuncio.get("extendedPropertyType"),
        "superficie_m2": anuncio.get("size"),
        "habitaciones": anuncio.get("rooms"),
        "banos": anuncio.get("bathrooms"),
        "planta": anuncio.get("floor"),
        "exterior": anuncio.get("exterior"),
        "direccion": anuncio.get("address"),
        "provincia": anuncio.get("province"),
        "municipio": anuncio.get("municipality"),
        "distrito": anuncio.get("district"),
        "barrio": anuncio.get("neighborhood"),
        "latitud": anuncio.get("latitude"),
        "longitud": anuncio.get("longitude"),
        "descripcion": anuncio.get("description"),
        "municipio_busqueda": municipio_busqueda,
        "location_id": location_id,
    }


def scrapear_municipio(
    cliente: Cliente,
    nombre: str,
    max_paginas: int,
) -> list[dict]:
    location_id = _autocompletar(cliente, nombre)
    if not location_id:
        return []

    anuncios: list[dict] = []
    pagina = 1
    total_paginas = 1

    while pagina <= max_paginas and pagina <= total_paginas:
        try:
            resp = cliente.get(
                f"{BASE_URL}/search/bylocation",
                params={
                    "locationId": location_id,
                    "country": "es",
                    "searchType": "For_Rent",
                    "propertyType": "homes",
                    "resultCount": 50,
                    "page": pagina,
                },
            )
        except RuntimeError as exc:
            log.error("%s página %d: %s", nombre, pagina, exc)
            break

        data = resp.json()
        total_paginas = int(data.get("totalPages") or 1)
        lote = data.get("searchResults", [])
        if not lote:
            break

        for anuncio in lote:
            anuncios.append(_normalizar(anuncio, nombre, location_id))
        log.info(
            "%s página %d/%d → %d anuncios (total %s)",
            nombre, pagina, total_paginas, len(lote), data.get("total"),
        )

        if pagina >= total_paginas:
            break
        pagina += 1

    return anuncios


def _municipios_desde_alquiler() -> list[str]:
    ruta = RAW_DIR / "alquiler_municipal.csv"
    if not ruta.exists():
        log.error("Falta %s. Ejecuta 02_eustat_alquiler.py primero.", ruta.name)
        return []
    import csv as csv_module

    vistos: set[str] = set()
    resultado: list[str] = []
    with ruta.open(encoding="utf-8-sig") as fh:
        for fila in csv_module.DictReader(fh):
            if fila.get("distrito") not in ("01", ""):
                continue
            nombre = fila.get("municipio", "").strip()
            if nombre and nombre not in vistos:
                vistos.add(nombre)
                resultado.append(nombre)
    return resultado


def main() -> int:
    parser = argparse.ArgumentParser(description="Extracción RealtyAPI (Idealista)")
    parser.add_argument(
        "--municipios", nargs="+", help="Lista concreta de municipios"
    )
    parser.add_argument(
        "--todos", action="store_true",
        help="Usar los municipios de alquiler_municipal.csv (gasta créditos)",
    )
    parser.add_argument("--max-municipios", type=int, default=None)
    parser.add_argument("--max-paginas", type=int, default=1)
    args = parser.parse_args()

    if args.municipios:
        municipios = args.municipios
    elif args.todos:
        municipios = _municipios_desde_alquiler()
    else:
        municipios = MUNICIPIOS_PRUEBA

    if args.max_municipios is not None:
        municipios = municipios[: args.max_municipios]

    if not municipios:
        log.error("No hay municipios que procesar.")
        return 1

    log.info("Municipios a procesar: %d", len(municipios))

    key = _obtener_key()
    cliente = Cliente("realtyapi", delay=1.2, reintentos=3, headers={
        "x-realtyapi-key": key,
    })

    todos: list[dict] = []
    for nombre in municipios:
        try:
            lote = scrapear_municipio(cliente, nombre, args.max_paginas)
            todos.extend(lote)
            log.info("%s: %d anuncios", nombre, len(lote))
        except Exception as exc:  # noqa: BLE001
            log.error("Fallo en %s: %s", nombre, exc)

    # Desduplicar por id_anuncio
    vistos: set = set()
    unicos: list[dict] = []
    for anuncio in todos:
        clave = anuncio.get("id_anuncio") or anuncio.get("url")
        if clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(anuncio)

    log.info("Anuncios totales: %d | únicos: %d", len(todos), len(unicos))

    if not unicos:
        return 1

    guardar_json(
        RAW_DIR / "anuncios_realtyapi.json",
        unicos,
        metadata={
            "fuente": "RealtyAPI.io (Idealista, no oficial)",
            "n_municipios": len({a["municipio_busqueda"] for a in unicos}),
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_anuncios": len(unicos),
            "n_sin_duplicar": len(todos),
        },
    )

    columnas = [
        "id_anuncio", "precio_eur", "municipio_busqueda", "municipio",
        "provincia", "distrito", "barrio", "tipo_inmueble", "superficie_m2",
        "habitaciones", "banos", "planta", "exterior", "url",
    ]
    destino_csv = RAW_DIR / "anuncios_realtyapi.csv"
    with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        escritor = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(unicos)
    log.info("CSV → %s", destino_csv.name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY