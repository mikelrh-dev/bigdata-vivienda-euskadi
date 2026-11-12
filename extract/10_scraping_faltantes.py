"""Scraping dirigido a municipios con baja cobertura (n < 30 anuncios).

Append-only: guarda lotes en data/raw/anuncios_faltantes_batch*.json.
No sobrescribe archivos existentes.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402
from _slugs import slug_fotocasa  # noqa: E402
from entity_resolution import cargar_dim, resolver_municipio  # noqa: E402

import importlib.util

spec_fc = importlib.util.spec_from_file_location(
    "fotocasa_mod", Path(__file__).resolve().parent / "05_fotocasa_scraper.py"
)
fotocasa_mod = importlib.util.module_from_spec(spec_fc)
spec_fc.loader.exec_module(fotocasa_mod)

spec_pisos = importlib.util.spec_from_file_location(
    "pisos_mod", Path(__file__).resolve().parent / "08_pisos_scraper.py"
)
pisos_mod = importlib.util.module_from_spec(spec_pisos)
spec_pisos.loader.exec_module(pisos_mod)

log = get_logger("faltantes")
def _slug(nombre: str) -> str:
    return slug_fotocasa(nombre)


def _municipios_faltantes(umbral: int) -> list[tuple[str, str]]:
    """Identifica municipios con pocos anuncios usando solo entradas raw.

    Este extractor corre antes de Transform; por eso no puede depender de
    anuncios_unificados.csv. Los IDs/URLs deduplican repeticiones entre feeds.
    """
    dim = cargar_dim()
    regs = dim.to_dict(orient="records")
    nombres = {str(r["codigo_ine"]).zfill(5): r["nombre_canonico"] for r in regs}
    ids_por_codigo: dict[str, set[str]] = {}
    fuentes = [
        RAW_DIR / "anuncios_fotocasa.json",
        RAW_DIR / "anuncios_pisos.json",
        RAW_DIR / "anuncios_realtyapi.json",
        *sorted(RAW_DIR.glob("anuncios_fotocasa_dirigido_*.json")),
    ]
    for ruta in fuentes:
        if not ruta.exists():
            continue
        payload = json.loads(ruta.read_text(encoding="utf-8"))
        anuncios = payload.get("datos", payload) if isinstance(payload, dict) else payload
        for idx, anuncio in enumerate(anuncios):
            codigo = anuncio.get("codigo_ine") or anuncio.get("codigo_ine_forzado")
            if not codigo:
                codigo, _ = resolver_municipio(
                    anuncio.get("municipio_busqueda") or anuncio.get("municipio")
                )
            if not codigo:
                continue
            codigo = str(codigo).zfill(5)
            identidad = anuncio.get("url_detalle") or anuncio.get("url") or anuncio.get("id_anuncio")
            if not identidad:
                identidad = f"{ruta.name}:{idx}"
            ids_por_codigo.setdefault(codigo, set()).add(str(identidad))
    counts = {codigo: len(ids) for codigo, ids in ids_por_codigo.items()}
    faltantes = []
    for cod, nombre in nombres.items():
        n = counts.get(cod, 0)
        if n < umbral:
            faltantes.append((cod, nombre))
    # ordenar por población desc (si disponible)
    pobl = {r["codigo_ine"]: r.get("poblacion_total", 0) for r in regs}
    faltantes.sort(key=lambda x: pobl.get(x[0], 0), reverse=True)
    return faltantes


def main() -> int:
    parser = argparse.ArgumentParser(description="Scraping dirigido a faltantes")
    parser.add_argument("--umbral", type=int, default=30)
    parser.add_argument("--max-municipios", type=int, default=10)
    parser.add_argument("--max-paginas", type=int, default=2)
    parser.add_argument("--codigos", nargs="+", help="Limitar a códigos INE concretos")
    args = parser.parse_args()

    faltantes = _municipios_faltantes(args.umbral)
    if args.codigos:
        dim = cargar_dim()
        nombres = {
            str(fila["codigo_ine"]).zfill(5): fila["nombre_canonico"]
            for fila in dim.to_dict(orient="records")
        }
        pedidos = list(dict.fromkeys(args.codigos))
        desconocidos = sorted(set(pedidos) - set(nombres))
        if desconocidos:
            parser.error(f"Códigos INE desconocidos: {', '.join(desconocidos)}")
        seleccion = [(codigo, nombres[codigo]) for codigo in pedidos]
    else:
        seleccion = faltantes[: args.max_municipios]
    log.info("Faltantes totales: %d | seleccionados: %d", len(faltantes), len(seleccion))

    cliente_fc = Cliente("faltantes_fc", delay=2.0, reintentos=2)
    cliente_pisos = Cliente("faltantes_pisos", delay=3.0, reintentos=2)

    todos_fc = []
    todos_pisos = []
    for cod, nombre in seleccion:
        # Fotocasa
        slug = _slug(nombre)
        url_base = f"https://www.fotocasa.es/es/alquiler/viviendas/{slug}/todas-las-zonas/l"
        for pagina in range(1, args.max_paginas + 1):
            url = url_base if pagina == 1 else f"{url_base}/{pagina}"
            try:
                html = cliente_fc.get(url).text
            except Exception as exc:
                log.warning("Fotocasa %s p%d: %s", nombre, pagina, exc)
                break
            datos = fotocasa_mod._extraer_json(html)
            if not datos:
                break
            try:
                resultado = datos["initialSearch"]["result"]
                lote = [fotocasa_mod._normalizar(a) for a in resultado.get("realEstates", [])]
            except (KeyError, TypeError) as exc:
                log.warning("Fotocasa %s p%d: %s", nombre, pagina, exc)
                break
            for an in lote:
                an["municipio_busqueda"] = nombre
                an["codigo_ine_forzado"] = cod
                an["provincia_origen"] = "faltantes"
            todos_fc.extend(lote)
            paginas = fotocasa_mod._paginas_totales(resultado)
            if pagina >= paginas or not lote:
                break

        # Pisos
        try:
            lote_p = pisos_mod.scrapear_municipio(cliente_pisos, nombre, args.max_paginas)
            for an in lote_p:
                an["municipio_busqueda"] = nombre
                an["codigo_ine_forzado"] = cod
            todos_pisos.extend(lote_p)
        except Exception as exc:
            log.warning("Pisos %s: %s", nombre, exc)

        log.info("%s [%s]: fc=%d pisos=%d", nombre, cod, len(todos_fc), len(todos_pisos))

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_num = len(list(RAW_DIR.glob("anuncios_faltantes_*_batch*.json"))) + 1
    if todos_fc:
        fc_path = RAW_DIR / f"anuncios_faltantes_fotocasa_batch{batch_num}_{fecha}.json"
        guardar_json(fc_path, todos_fc, metadata={
            "fuente": "Scraping dirigido a faltantes (Fotocasa)",
            "url": "https://www.fotocasa.es/es/alquiler/viviendas",
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_anuncios": len(todos_fc),
            "municipios_objetivo": len(seleccion),
            "umbral": args.umbral,
        })
        log.info("Lote Fotocasa guardado: %s (%d)", fc_path.name, len(todos_fc))
    if todos_pisos:
        pisos_path = RAW_DIR / f"anuncios_faltantes_pisos_batch{batch_num}_{fecha}.json"
        guardar_json(pisos_path, todos_pisos, metadata={
            "fuente": "Scraping dirigido a faltantes (Pisos)",
            "url": "https://www.pisos.com/alquiler/",
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_anuncios": len(todos_pisos),
            "municipios_objetivo": len(seleccion),
            "umbral": args.umbral,
        })
        log.info("Lote Pisos guardado: %s (%d)", pisos_path.name, len(todos_pisos))
    return 0 if (todos_fc or todos_pisos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
