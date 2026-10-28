"""Scraping de anuncios de alquiler de HABITACIONES (pisos compartidos).

Fuentes:
  - Fotocasa: https://www.fotocasa.es/es/compartir/pisos
  - Pisos.com: https://www.pisos.com/alquiler/habitaciones-{municipio}

Municipios (capitales y cabeceras de comarca, lista corta):
  Bilbao, Donostia / San Sebastián, Vitoria-Gasteiz, Barakaldo, Getxo,
  Irun, Errenteria, Eibar, Durango, Gernika-Lumo.

Maximo 2 paginas por municipio y fuente. Salida:
  data/raw/anuncios_fotocasa_habitaciones.json/.csv
  data/raw/anuncios_pisos_habitaciones.json/.csv

Uso:
  python extract/13_scraping_habitaciones.py
  python extract/13_scraping_habitaciones.py --max-paginas 2
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("habitaciones")

MUNICIPIOS = [
    "Bilbao",
    "Donostia / San Sebastián",
    "Vitoria-Gasteiz",
    "Barakaldo",
    "Getxo",
    "Irun",
    "Errenteria",
    "Eibar",
    "Durango",
    "Gernika-Lumo",
]

MAX_POR_PAGINA_PISOS = 30


# ───────────────────── Fotocasa ─────────────────────
FOTOCASA_BASE = "https://www.fotocasa.es/es/compartir/pisos"
PATRON_JSON = re.compile(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', re.S)


def _slug_fotocasa(nombre: str) -> str:
    texto = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()


def _extraer_json(html: str) -> dict | None:
    for bloque in PATRON_JSON.finditer(html):
        try:
            datos = json.loads(bloque.group(1))
        except json.JSONDecodeError:
            continue
        if "initialSearch" in datos:
            return datos
    return None


def _extraer_caracteristicas(anuncio: dict) -> dict:
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


def _url_detalle_fc(anuncio: dict) -> str | None:
    for campo in ("detailWithParams", "detail"):
        valor = anuncio.get(campo)
        if isinstance(valor, dict):
            ruta = valor.get("es-ES") or next(iter(valor.values()), None)
        elif isinstance(valor, str):
            ruta = valor
        else:
            ruta = None
        if ruta:
            return "https://www.fotocasa.es" + str(ruta).split("?")[0]
    return None


def _normalizar_fc(anuncio: dict, municipio_busqueda: str) -> dict:
    direccion = anuncio.get("address") or {}
    coordenadas = anuncio.get("coordinates") or {}
    try:
        from entity_resolution import resolver_municipio as _resolver
        _cod, _can = _resolver((direccion.get("municipality") or municipio_busqueda).strip())
    except Exception:  # noqa: BLE001
        _cod, _can = None, None
    return {
        "codigo_ine": _cod,
        "nombre_canonico": _can,
        "anio_fuente": 2026,
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
        "url_detalle": _url_detalle_fc(anuncio),
        "profesional": anuncio.get("clientType"),
        "es_nueva_construccion": anuncio.get("isNewConstruction"),
        "municipio_busqueda": municipio_busqueda,
        "fuente": "fotocasa",
    }


def _paginas_totales_fc(resultado: dict) -> int:
    total = resultado.get("count")
    if not total:
        return 1
    return (int(total) + 29) // 30


def scrapear_fotocasa_municipio(
    cliente: Cliente, nombre: str, max_paginas: int
) -> list[dict]:
    slug = _slug_fotocasa(nombre)
    ruta = f"{slug}/todas-las-zonas/l"
    anuncios: list[dict] = []
    pagina = 1
    while pagina <= max_paginas:
        url = f"{FOTOCASA_BASE}/{ruta}" if pagina == 1 else f"{FOTOCASA_BASE}/{ruta}/{pagina}"
        try:
            html = cliente.get(url).text
        except RuntimeError as exc:
            log.error("fotocasa %s p%d: %s", nombre, pagina, exc)
            break
        datos = _extraer_json(html)
        if not datos:
            log.warning("fotocasa %s p%d: sin JSON", nombre, pagina)
            break
        try:
            resultado = datos["initialSearch"]["result"]
            lote = [_normalizar_fc(a, nombre) for a in resultado.get("realEstates", [])]
            anuncios.extend(lote)
            paginas = _paginas_totales_fc(resultado)
            log.info(
                "fotocasa %s p%d/%d -> %d (total portal: %s)",
                nombre, pagina, paginas, len(lote), resultado.get("count"),
            )
            if pagina >= paginas or not lote:
                break
        except (KeyError, TypeError) as exc:
            log.error("fotocasa %s p%d: estructura inesperada (%s)", nombre, pagina, exc)
            break
        pagina += 1
    return anuncios


# ───────────────────── Pisos.com ─────────────────────
PISOS_BASE = "https://www.pisos.com/alquiler/habitaciones-{municipio}"

PISOS_SLUGS = {
    "Bilbao": "bilbao",
    "Donostia / San Sebastián": "san_sebastian_donostia",
    "Vitoria-Gasteiz": "vitoria_gasteiz",
    "Barakaldo": "barakaldo",
    "Getxo": "getxo",
    "Irun": "irun",
    "Errenteria": "errenteria",
    "Eibar": "eibar",
    "Durango": "durango",
    "Gernika-Lumo": "gernika_lumo",
}


def _limpiar_pisos(texto: str) -> str:
    import html as html_module

    return html_module.unescape(re.sub(r"<[^>]+>", " ", texto)).strip()


def _parsear_pisos(html: str) -> list[dict]:
    anuncios = []
    for pm in re.finditer(r'<span class="ad-preview__price">(.*?)</span>', html, re.S):
        segmento = html[pm.start() : pm.start() + 1500]
        titulo = re.search(r'class="ad-preview__title"[^>]*>(.*?)</a>', segmento, re.S)
        subtitulo = re.search(r'ad-preview__subtitle">(.*?)</p>', segmento, re.S)
        enlace = re.search(r'href="(/alquilar/[^"]+)"', segmento)
        tipo = re.search(r'ad-preview__type[^>]*>(.*?)</', segmento, re.S)
        superficie = re.search(r'ad-preview__char[^>]*>(\d+)\s*m', segmento, re.S | re.I)
        habitaciones = re.search(r'ad-preview__char[^>]*>(\d+)\s*hab', segmento, re.S | re.I)
        banos = re.search(r'ad-preview__char[^>]*>(\d+)\s*ba', segmento, re.S | re.I)

        precio_texto = _limpiar_pisos(pm.group(1)).replace("/mes", "").strip()
        precio = None
        match = re.search(r"(\d[\d\.]*)", precio_texto.replace(".", ""))
        if match:
            try:
                precio = int(match.group(1))
            except ValueError:
                precio = None

        if not titulo and not enlace:
            continue

        id_anuncio = (
            enlace.group(1).rstrip("/").split("/")[-1] if enlace else None
        )
        anuncios.append(
            {
                "id_anuncio": id_anuncio,
                "precio_eur": precio,
                "precio_texto": precio_texto,
                "titulo": _limpiar_pisos(titulo.group(1)) if titulo else None,
                "subtitulo": _limpiar_pisos(subtitulo.group(1)) if subtitulo else None,
                "tipo_inmueble": _limpiar_pisos(tipo.group(1)) if tipo else None,
                "superficie_m2": int(superficie.group(1)) if superficie else None,
                "habitaciones": int(habitaciones.group(1)) if habitaciones else None,
                "banos": int(banos.group(1)) if banos else None,
                "url_detalle": (
                    "https://www.pisos.com" + enlace.group(1) if enlace else None
                ),
            }
        )
    return anuncios


def _total_resultados_pisos(html: str) -> int | None:
    match = re.search(r"(\d+)\s+de\s+(\d+)\s+resultados", html)
    if match:
        return int(match.group(2))
    match = re.search(r"(\d+)\s+resultados", html)
    if match:
        return int(match.group(1))
    match = re.search(r'content="(\d+) casas y pisos en alquiler', html)
    return int(match.group(1)) if match else None


def scrapear_pisos_municipio(
    cliente: Cliente, nombre: str, max_paginas: int
) -> list[dict]:
    slug = PISOS_SLUGS.get(nombre, nombre.lower().replace(" ", "_"))
    anuncios: list[dict] = []
    pagina = 1
    total = None
    max_paginas_local = max_paginas
    while pagina <= max_paginas_local:
        ruta = f"/{pagina}/" if pagina > 1 else "/"
        url = PISOS_BASE.format(municipio=slug) + ruta
        try:
            html = cliente.get(url).text
        except RuntimeError as exc:
            log.error("pisos %s p%d: %s", nombre, pagina, exc)
            break
        if pagina == 1:
            total = _total_resultados_pisos(html)
            if total is not None:
                paginas_reales = (total + MAX_POR_PAGINA_PISOS - 1) // MAX_POR_PAGINA_PISOS
                if paginas_reales < max_paginas_local:
                    max_paginas_local = paginas_reales
                log.info("%s (pisos) -> %d resultados (%d paginas)", nombre, total, paginas_reales)
        lote = _parsear_pisos(html)
        if not lote:
            break
        anuncios.extend(lote)
        log.info("pisos %s p%d -> %d anuncios", nombre, pagina, len(lote))
        if len(lote) < MAX_POR_PAGINA_PISOS:
            break
        pagina += 1

    try:
        from entity_resolution import resolver_municipio as _resolver

        _cod, _can = _resolver(nombre)
    except Exception:  # noqa: BLE001
        _cod, _can = None, None
    for a in anuncios:
        a["municipio_busqueda"] = nombre
        a.setdefault("codigo_ine", _cod)
        a.setdefault("nombre_canonico", _can)
        a.setdefault("anio_fuente", 2026)
        a.setdefault("es_busqueda_no_ubicacion", True)
        a["total_resultados"] = total
        a["fuente"] = "pisos"
    return anuncios


# ───────────────────── Main ─────────────────────
def _dedup(items: list[dict], clave_func) -> list[dict]:
    vistos: set = set()
    unicos = []
    for it in items:
        clave = clave_func(it)
        if clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(it)
    return unicos


def main() -> int:
    parser = argparse.ArgumentParser(description="Scraping de habitaciones (Fotocasa + Pisos.com)")
    parser.add_argument("--max-paginas", type=int, default=2)
    args = parser.parse_args()
    max_paginas = max(1, args.max_paginas)

    # ── Fotocasa ──
    cliente_fc = Cliente("fotocasa", delay=2.0, reintentos=4)
    todos_fc: list[dict] = []
    for nombre in MUNICIPIOS:
        log.info("=== fotocasa: %s ===", nombre)
        try:
            lote = scrapear_fotocasa_municipio(cliente_fc, nombre, max_paginas)
            todos_fc.extend(lote)
            log.info("fotocasa %s: %d anuncios", nombre, len(lote))
        except Exception as exc:  # noqa: BLE001
            log.error("fallo fotocasa %s: %s", nombre, exc)

    unicos_fc = _dedup(
        todos_fc,
        lambda a: a.get("id_anuncio") or a.get("url_detalle")
        or json.dumps([a.get("municipio"), a.get("precio_eur")], ensure_ascii=False),
    )
    log.info("Fotocasa habitaciones: total=%d unicos=%d", len(todos_fc), len(unicos_fc))

    if unicos_fc:
        guardar_json(
            RAW_DIR / "anuncios_fotocasa_habitaciones.json",
            unicos_fc,
            metadata={
                "fuente": "Fotocasa (scraping HTML, sin API key) - habitaciones",
                "municipios": MUNICIPIOS,
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "n_anuncios": len(unicos_fc),
                "n_sin_duplicar": len(todos_fc),
                "max_paginas": max_paginas,
            },
        )
        columnas_fc = [
            "codigo_ine", "nombre_canonico", "anio_fuente",
            "id_anuncio", "precio_eur", "precio_reducido_eur",
            "municipio", "provincia", "codigo_postal", "barrio", "comarca",
            "latitud", "longitud", "superficie_m2", "habitaciones", "banos",
            "municipio_busqueda", "fuente", "url_detalle",
        ]
        destino_csv = RAW_DIR / "anuncios_fotocasa_habitaciones.csv"
        with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
            escritor = csv.DictWriter(fh, fieldnames=columnas_fc, extrasaction="ignore")
            escritor.writeheader()
            escritor.writerows(unicos_fc)
        log.info("CSV fotocasa -> %s", destino_csv.name)

    # ── Pisos.com ──
    cliente_pisos = Cliente("pisos", delay=1.5, reintentos=4)
    todos_pisos: list[dict] = []
    for nombre in MUNICIPIOS:
        log.info("=== pisos: %s ===", nombre)
        try:
            lote = scrapear_pisos_municipio(cliente_pisos, nombre, max_paginas)
            todos_pisos.extend(lote)
            log.info("pisos %s: %d anuncios", nombre, len(lote))
        except Exception as exc:  # noqa: BLE001
            log.error("fallo pisos %s: %s", nombre, exc)

    unicos_pisos = _dedup(
        todos_pisos,
        lambda a: a.get("url_detalle") or a.get("titulo") or a.get("id_anuncio"),
    )
    log.info("Pisos habitaciones: total=%d unicos=%d", len(todos_pisos), len(unicos_pisos))

    if unicos_pisos:
        guardar_json(
            RAW_DIR / "anuncios_pisos_habitaciones.json",
            unicos_pisos,
            metadata={
                "fuente": "Pisos.com (scraping HTML, sin API key) - habitaciones",
                "n_municipios": len({a["municipio_busqueda"] for a in unicos_pisos}),
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "n_anuncios": len(unicos_pisos),
                "n_sin_duplicar": len(todos_pisos),
                "max_paginas": max_paginas,
            },
        )
        columnas_pisos = [
            "codigo_ine", "nombre_canonico", "anio_fuente",
            "id_anuncio", "precio_eur", "municipio_busqueda", "titulo", "subtitulo",
            "tipo_inmueble", "superficie_m2", "habitaciones", "banos",
            "url_detalle", "total_resultados", "es_busqueda_no_ubicacion", "fuente",
        ]
        destino_csv = RAW_DIR / "anuncios_pisos_habitaciones.csv"
        with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
            escritor = csv.DictWriter(fh, fieldnames=columnas_pisos, extrasaction="ignore")
            escritor.writeheader()
            escritor.writerows(unicos_pisos)
        log.info("CSV pisos -> %s", destino_csv.name)

    return 0 if (unicos_fc or unicos_pisos) else 1


if __name__ == "__main__":
    raise SystemExit(main())