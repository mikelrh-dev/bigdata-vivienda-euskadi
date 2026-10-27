"""Scraping de anuncios de alquiler en Pisos.com (Álava, Bizkaia, Gipuzkoa).

Pisos.com no tiene API pública, pero el HTML de búsqueda incluye los
anuncios como tarjetas `ad-preview` con precio, título, barrio y enlace.

  https://www.pisos.com/alquiler/pisos-{municipio}/
  https://www.pisos.com/alquiler/pisos-{municipio}/2/
  ...

Cada página trae ~30 anuncios. El total aparece en el texto
"30 de 43 resultados".

Es la SEGUNDA fuente de anuncios, independiente de Fotocasa: amplía la
cobertura de municipios y permite contrastar precios entre portales.

Uso:
  python extract/08_pisos_scraper.py
  python extract/08_pisos_scraper.py --max-paginas 2
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("pisos")

BASE = "https://www.pisos.com/alquiler/pisos-{municipio}"
MAX_POR_PAGINA = 30


def _slug(nombre: str) -> str:
    """Convierte 'Donostia / San Sebastián' en 'donostia-san-sebastian'."""
    nombre = nombre.split("/")[0].strip()
    nombre = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", nombre.lower()).strip("-")


def _limpiar(texto: str) -> str:
    import html as html_module

    return html_module.unescape(re.sub(r"<[^>]+>", " ", texto)).strip()


def _parsear_anuncios(html: str) -> list[dict]:
    """Extrae las tarjetas `ad-preview` de una pagina.

    El precio esta en un contenedor previo al titulo, por lo que se itera
    sobre cada span de precio y se extrae el resto desde una ventana de
    ~1500 caracteres a continuacion.
    """
    anuncios = []
    for pm in re.finditer(r'<span class="ad-preview__price">(.*?)</span>', html, re.S):
        segmento = html[pm.start():pm.start() + 1500]

        titulo = re.search(r'class="ad-preview__title"[^>]*>(.*?)</a>', segmento, re.S)
        subtitulo = re.search(r'ad-preview__subtitle">(.*?)</p>', segmento, re.S)
        enlace = re.search(r'href="(/alquilar/[^"]+)"', segmento)
        tipo = re.search(r'ad-preview__type[^>]*>(.*?)</', segmento, re.S)
        superficie = re.search(r'ad-preview__char[^>]*>(\d+)\s*m', segmento, re.S | re.I)
        habitaciones = re.search(r'ad-preview__char[^>]*>(\d+)\s*hab', segmento, re.S | re.I)
        banos = re.search(r'ad-preview__char[^>]*>(\d+)\s*ba', segmento, re.S | re.I)

        precio_texto = _limpiar(pm.group(1)).replace("/mes", "").strip()
        precio = None
        match = re.search(r"(\d[\d\.]*)", precio_texto.replace(".", ""))
        if match:
            try:
                precio = int(match.group(1))
            except ValueError:
                precio = None

        if not titulo and not enlace:
            continue

        id_anuncio = enlace.group(1).rstrip("/").split("/")[-1] if enlace else None

        anuncios.append(
            {
                "id_anuncio": id_anuncio,
                "precio_eur": precio,
                "precio_texto": precio_texto,
                "titulo": _limpiar(titulo.group(1)) if titulo else None,
                "subtitulo": _limpiar(subtitulo.group(1)) if subtitulo else None,
                "tipo_inmueble": _limpiar(tipo.group(1)) if tipo else None,
                "superficie_m2": int(superficie.group(1)) if superficie else None,
                "habitaciones": int(habitaciones.group(1)) if habitaciones else None,
                "banos": int(banos.group(1)) if banos else None,
                "url_detalle": (
                    "https://www.pisos.com" + enlace.group(1)
                    if enlace
                    else None
                ),
            }
        )
    return anuncios


def _total_resultados(html: str) -> int | None:
    """Lee '30 de 43 resultados' → 43."""
    match = re.search(r"(\d+)\s+de\s+(\d+)\s+resultados", html)
    if match:
        return int(match.group(2))
    match = re.search(r'content="(\d+) casas y pisos en alquiler', html)
    return int(match.group(1)) if match else None


def scrapear_municipio(
    cliente: Cliente,
    nombre: str,
    max_paginas: int,
) -> list[dict]:
    municipio = _slug(nombre)
    anuncios: list[dict] = []
    pagina = 1
    total = None

    while pagina <= max_paginas:
        ruta = f"/{pagina}/" if pagina > 1 else "/"
        url = f"{BASE.format(municipio=municipio)}{ruta}"
        try:
            html = cliente.get(url).text
        except RuntimeError as exc:
            log.error("%s página %d: %s", nombre, pagina, exc)
            break

        if pagina == 1:
            total = _total_resultados(html)
            if total is not None:
                paginas_reales = (total + MAX_POR_PAGINA - 1) // MAX_POR_PAGINA
                log.info(
                    "%s → %d resultados (%d páginas)",
                    nombre, total, paginas_reales,
                )
                if paginas_reales < max_paginas:
                    max_paginas = paginas_reales

        lote = _parsear_anuncios(html)
        if not lote:
            break
        anuncios.extend(lote)
        log.info("%s página %d → %d anuncios", nombre, pagina, len(lote))

        if len(lote) < MAX_POR_PAGINA:
            break
        pagina += 1

    for anuncio in anuncios:
        anuncio["municipio_busqueda"] = nombre
        anuncio["total_resultados"] = total
    return anuncios


def main() -> int:
    parser = argparse.ArgumentParser(description="Scraping de Pisos.com")
    parser.add_argument("--max-paginas", type=int, default=5)
    parser.add_argument(
        "--municipios",
        nargs="+",
        help="Lista concreta de municipios (por defecto, los de Eustat)",
    )
    args = parser.parse_args()

    # Si no se pasan municipios, usar los 159 de Eustat
    if args.municipios:
        municipios = args.municipios
    else:
        import csv as csv_module

        ruta_alquiler = RAW_DIR / "alquiler_municipal.csv"
        if not ruta_alquiler.exists():
            log.error(
                "Falta %s. Ejecuta 02_eustat_alquiler.py primero.",
                ruta_alquiler.name,
            )
            return 1
        with ruta_alquiler.open(encoding="utf-8-sig") as fh:
            municipios = [
                r["municipio"]
                for r in csv_module.DictReader(fh)
                if r["distrito"] in ("01", "")
            ]
        # deduplicar conservando orden
        municipios = list(dict.fromkeys(municipios))
        log.info("Municipios a scrapear: %d", len(municipios))

    cliente = Cliente("pisos", delay=1.5, reintentos=4)

    todos: list[dict] = []
    for nombre in municipios:
        try:
            lote = scrapear_municipio(cliente, nombre, args.max_paginas)
            todos.extend(lote)
            log.info("%s: %d anuncios", nombre, len(lote))
        except Exception as exc:  # noqa: BLE001
            log.error("Fallo en %s: %s", nombre, exc)

    # Desduplicar por URL de detalle
    vistos: set = set()
    unicos = []
    for anuncio in todos:
        clave = anuncio.get("url_detalle") or anuncio.get("titulo")
        if clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(anuncio)

    log.info("Anuncios totales: %d | únicos: %d", len(todos), len(unicos))

    if unicos:
        guardar_json(
            RAW_DIR / "anuncios_pisos.json",
            unicos,
            metadata={
                "fuente": "Pisos.com (scraping HTML, sin API key)",
                "n_municipios": len({a["municipio_busqueda"] for a in unicos}),
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "n_anuncios": len(unicos),
                "n_sin_duplicar": len(todos),
            },
        )

        columnas = [
            "id_anuncio", "precio_eur", "municipio_busqueda", "titulo", "subtitulo",
            "tipo_inmueble", "superficie_m2", "habitaciones", "banos",
            "url_detalle", "total_resultados",
        ]
        destino_csv = RAW_DIR / "anuncios_pisos.csv"
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
