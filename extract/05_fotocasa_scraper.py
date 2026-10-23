"""Scraping de anuncios de alquiler en Fotocasa (Álava, Bizkaia, Gipuzkoa).

Fotocasa no tiene API pública, pero las páginas de búsqueda incluyen los
anuncios en un <script type="application/json">:
  initialSearch.result.realEstates[]

Cada anuncio trae: precio, municipio, código postal, barrio, coordenadas,
habitaciones, m², fecha de publicación y descripción.

Robots.txt NO prohíbe /es/alquiler/viviendas/, por lo que el scraping es
legítimo a ritmo razonable (el script ya incluye pausas).

Uso:
  python extract/05_fotocasa_scraper.py
  python extract/05_fotocasa_scraper.py --provincias gipuzkoa
  python extract/05_fotocasa_scraper.py --max-paginas 5
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("fotocasa")

BASE = "https://www.fotocasa.es/es/alquiler/viviendas"

PROVINCIAS = {
    "gipuzkoa": "gipuzkoa-provincia/todas-las-zonas/l",
    "bizkaia": "bizkaia-provincia/todas-las-zonas/l",
    "araba_alava": "araba-alava-provincia/todas-las-zonas/l",
}

PATRON_JSON = re.compile(
    r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', re.S
)


def _extraer_json(html: str) -> dict | None:
    """Busca el bloque JSON que contiene initialSearch."""
    for bloque in PATRON_JSON.finditer(html):
        try:
            datos = json.loads(bloque.group(1))
        except json.JSONDecodeError:
            continue
        if "initialSearch" in datos:
            return datos
    return None


def _extraer_caracteristicas(anuncio: dict) -> dict:
    """Fotocasa mete las características en una lista de {key, value}.

    Las relevantes: surface (m²), rooms, bathrooms. El resto son flags
    (heating, parking, terrace...) cuyo value es un código interno.
    """
    bruto = {}
    for f in anuncio.get("features") or []:
        if isinstance(f, dict) and f.get("key") is not None:
            bruto[f["key"]] = f.get("value")

    extras = anuncio.get("dynamicFeatures") or []
    return {
        "superficie_m2": bruto.get("surface"),
        "habitaciones": bruto.get("rooms"),
        "banos": bruto.get("bathrooms"),
        "calefaccion": bruto.get("heating"),
        "parking": bruto.get("parking"),
        "ascensor": bruto.get("elevator"),
        "terraza": bruto.get("terrace"),
        "trastero": bruto.get("storage_room"),
        "jardin": bruto.get("private_garden"),
        "exterior": "IS_EXTERIOR" in extras,
        "alquiler_temporal": "IS_TEMPORARY" in extras,
        "n_imagenes": len(anuncio.get("multimedia") or []),
    }


def _url_detalle(anuncio: dict) -> str | None:
    """El campo 'detail' es un dict {'es-ES': '/es/alquiler/...'}."""
    for campo in ("detailWithParams", "detail"):
        valor = anuncio.get(campo)
        if isinstance(valor, dict):
            ruta = valor.get("es-ES") or next(iter(valor.values()), None)
        elif isinstance(valor, str):
            ruta = valor
        else:
            ruta = None
        if ruta:
            return "https://www.fotocasa.es" + ruta.split("?")[0]
    return None


def _normalizar(anuncio: dict) -> dict:
    """Deja cada anuncio en una estructura plana y limpia."""
    direccion = anuncio.get("address") or {}
    coordenadas = anuncio.get("coordinates") or {}

    return {
        "id_anuncio": anuncio.get("id") or anuncio.get("realEstateAdId"),
        "uuid_anuncio": anuncio.get("realEstateAdId"),
        "precio_eur": anuncio.get("rawPrice"),
        "precio_reducido_eur": anuncio.get("reducedPrice"),
        "precio_texto": anuncio.get("price"),
        "tipo_inmueble": anuncio.get("buildingType"),
        "subtipo_inmueble": anuncio.get("buildingSubtype"),
        "municipio": (direccion.get("municipality") or "").strip(),
        "provincia": (direccion.get("province") or "").strip(),
        "codigo_postal": direccion.get("zipCode"),
        "barrio": (direccion.get("neighborhood") or "").strip() or None,
        "distrito": (direccion.get("district") or "").strip() or None,
        "comarca": (direccion.get("county") or "").strip() or None,
        "latitud": coordenadas.get("latitude"),
        "longitud": coordenadas.get("longitude"),
        **_extraer_caracteristicas(anuncio),
        "url_detalle": _url_detalle(anuncio),
        "profesional": anuncio.get("clientType"),
        "es_nueva_construccion": anuncio.get("isNewConstruction"),
        "publicado": (
            datetime.fromtimestamp(anuncio["date"]["timestamp"] / 1000).isoformat(
                timespec="seconds"
            )
            if anuncio.get("date", {}).get("timestamp")
            else None
        ),
        "descripcion": (anuncio.get("description") or "").strip()[:500] or None,
    }


def _paginas_totales(resultado: dict) -> int:
    """Calcula cuántas páginas hay a partir de 'count'."""
    total = resultado.get("count")
    if not total:
        return 1
    return (int(total) + 29) // 30  # 30 anuncios por página


def scrapear_provincia(
    cliente: Cliente,
    nombre: str,
    ruta: str,
    max_paginas: int,
) -> list[dict]:
    anuncios: list[dict] = []
    pagina = 1

    while pagina <= max_paginas:
        url = f"{BASE}/{ruta}" if pagina == 1 else f"{BASE}/{ruta}/{pagina}"
        try:
            html = cliente.get(url).text
        except RuntimeError as exc:
            log.error("%s página %d: %s", nombre, pagina, exc)
            break

        datos = _extraer_json(html)
        if not datos:
            log.warning("%s página %d: no se encontró el JSON", nombre, pagina)
            break

        try:
            resultado = datos["initialSearch"]["result"]
            lote = [_normalizar(a) for a in resultado.get("realEstates", [])]
            anuncios.extend(lote)
            total = resultado.get("count")
            paginas = _paginas_totales(resultado)
            log.info(
                "%s página %d/%d → %d anuncios (total portal: %s)",
                nombre, pagina, paginas, len(lote), total,
            )
            if pagina >= paginas or not lote:
                break
        except (KeyError, TypeError) as exc:
            log.error("%s página %d: estructura inesperada (%s)", nombre, pagina, exc)
            break

        pagina += 1

    return anuncios


def main() -> int:
    parser = argparse.ArgumentParser(description="Scraping de Fotocasa")
    parser.add_argument(
        "--provincias",
        nargs="+",
        choices=list(PROVINCIAS),
        default=list(PROVINCIAS),
    )
    parser.add_argument("--max-paginas", type=int, default=20)
    args = parser.parse_args()

    cliente = Cliente("fotocasa", delay=2.0, reintentos=4)

    todos: list[dict] = []
    for nombre in args.provincias:
        log.info("=== %s ===", nombre)
        lote = scrapear_provincia(
            cliente, nombre, PROVINCIAS[nombre], args.max_paginas
        )
        for anuncio in lote:
            anuncio["provincia_origen"] = nombre
        todos.extend(lote)
        log.info("%s: %d anuncios", nombre, len(lote))

    # Desduplicar por id de anuncio
    vistos: set = set()
    unicos = []
    for anuncio in todos:
        clave = anuncio.get("id_anuncio") or json.dumps(
            [anuncio.get("municipio"), anuncio.get("precio_eur"),
             anuncio.get("barrio")], ensure_ascii=False
        )
        if clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(anuncio)

    log.info("Anuncios totales: %d | únicos: %d", len(todos), len(unicos))

    if unicos:
        guardar_json(
            RAW_DIR / "anuncios_fotocasa.json",
            unicos,
            metadata={
                "fuente": "Fotocasa (scraping HTML, sin API key)",
                "provincias": args.provincias,
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "n_anuncios": len(unicos),
                "n_sin_duplicar": len(todos),
            },
        )

        # CSV con los campos principales
        columnas = [
            "id_anuncio", "precio_eur", "precio_reducido_eur",
            "municipio", "provincia", "codigo_postal", "barrio", "comarca",
            "latitud", "longitud", "superficie_m2", "habitaciones", "banos",
            "exterior", "ascensor", "parking", "terraza", "trastero",
            "alquiler_temporal", "tipo_inmueble", "profesional",
            "publicado", "url_detalle",
        ]
        destino_csv = RAW_DIR / "anuncios_fotocasa.csv"
        with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
            escritor = csv.DictWriter(
                fh, fieldnames=columnas, extrasaction="ignore"
            )
            escritor.writeheader()
            escritor.writerows(unicos)
        log.info("CSV → %s", destino_csv.name)

    return 0 if unicos else 1


if __name__ == "__main__":
    raise SystemExit(main())
