"""Fotocasa dirigido (append-only): scraping por municipio para cabeceras comarcales.

Guarda resultados en data/raw/anuncios_fotocasa_dirigido_YYYYMMDD.json.
No sobrescribe archivos crudos existentes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402
from _slugs import slug_fotocasa  # noqa: E402
from entity_resolution import cargar_dim  # noqa: E402

# Reutilizar normalizador del scraper principal
import importlib.util

spec = importlib.util.spec_from_file_location(
    "fotocasa_mod", Path(__file__).resolve().parent / "05_fotocasa_scraper.py"
)
fotocasa_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fotocasa_mod)

log = get_logger("fotocasa_dirigido")
MAX_PAG = 2


def _slug(nombre: str) -> str:
    return slug_fotocasa(nombre)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fotocasa dirigido por municipio")
    parser.add_argument("--max-municipios", type=int, default=None)
    parser.add_argument("--codigos", nargs="+", help="Limitar a códigos INE concretos")
    parser.add_argument("--max-paginas", type=int, default=MAX_PAG)
    args = parser.parse_args()

    regs = cargar_dim().to_dict(orient="records")
    nombres = {r["codigo_ine"]: r["nombre_canonico"] for r in regs}

    # Optional target list is configuration for this acquisition, kept in raw
    # for compatibility with the existing frozen dataset. Otherwise use all.
    objetivos_path = RAW_DIR / "f4_pisos_objetivo.json"
    if objetivos_path.exists():
        objetivos = json.loads(objetivos_path.read_text(encoding="utf-8"))
    else:
        objetivos = list(nombres.keys())

    if args.codigos:
        desconocidos = [cod for cod in args.codigos if cod not in nombres]
        if desconocidos:
            parser.error(f"Códigos INE desconocidos: {', '.join(desconocidos)}")
        objetivos = list(dict.fromkeys(args.codigos))

    if args.max_municipios:
        objetivos = objetivos[: args.max_municipios]

    cliente = Cliente("fotocasa_dirigido", delay=2.0, reintentos=2)
    todos = []
    informe = []

    for cod in objetivos:
        nombre = nombres.get(cod, cod)
        slug = _slug(nombre)
        url_base = f"https://www.fotocasa.es/es/alquiler/viviendas/{slug}/todas-las-zonas/l"
        lote_total = []
        for pagina in range(1, args.max_paginas + 1):
            url = url_base if pagina == 1 else f"{url_base}/{pagina}"
            try:
                html = cliente.get(url).text
            except Exception as exc:
                log.warning("%s pagina %d: %s", nombre, pagina, exc)
                break
            datos = fotocasa_mod._extraer_json(html)
            if not datos:
                break
            try:
                resultado = datos["initialSearch"]["result"]
                lote = [fotocasa_mod._normalizar(a) for a in resultado.get("realEstates", [])]
            except (KeyError, TypeError) as exc:
                log.warning("%s pagina %d: estructura inesperada (%s)", nombre, pagina, exc)
                break
            for an in lote:
                an["municipio_busqueda"] = nombre
                an["codigo_ine_forzado"] = cod
            lote_total.extend(lote)
            paginas = fotocasa_mod._paginas_totales(resultado)
            if pagina >= paginas or not lote:
                break
        for an in lote_total:
            an["provincia_origen"] = "dirigido"
        todos.extend(lote_total)
        informe.append({"codigo_ine": cod, "municipio": nombre, "n": len(lote_total)})
        log.info("%s [%s]: %d anuncios", nombre, cod, len(lote_total))

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = RAW_DIR / f"anuncios_fotocasa_dirigido_{fecha}.json"
    guardar_json(
        raw_path,
        todos,
        metadata={
            "fuente": "Fotocasa dirigido por municipio (append-only)",
            "url": "https://www.fotocasa.es/es/alquiler/viviendas",
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_anuncios": len(todos),
            "municipios_objetivo": len(objetivos),
        },
    )
    log.info("Lote guardado en raw: %s (%d anuncios)", raw_path.name, len(todos))
    for fila in informe:
        log.info("  %s [%s]: %d", fila["municipio"], fila["codigo_ine"], fila["n"])
    return 0 if todos else 1


if __name__ == "__main__":
    raise SystemExit(main())
