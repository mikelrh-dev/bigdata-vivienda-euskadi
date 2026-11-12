"""Slugs de búsqueda verificados para portales inmobiliarios."""

from __future__ import annotations

import re
import unicodedata


def _ascii(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def slug_pisos(nombre: str) -> str:
    """Pisos.com representa separadores, incluidos guiones, con ``_``.

    La barra suele separar alias; conserva el primer nombre por defecto y
    declara explícitamente los casos cuyo slug del portal incluye ambos.
    """
    normalizado = _ascii(nombre).lower()
    clave = re.sub(r"[^a-z0-9]+", " ", normalizado).strip()
    aliases = {
        "campezo kanpezu": "campezo_kanpezu",
        "iruna oka iruna de oca": "iruna_oka_iruna_de_oca",
        "ribera baja erriberabeitia": "ribera_baja_erriberabeitia",
        "urduna orduna": "urduna_orduna",
        "donostia san sebastian": "donostia_san_sebastian",
    }
    if clave in aliases:
        return aliases[clave]
    # En alias bilingües, el portal normalmente identifica la búsqueda por
    # el nombre anterior a la barra (p. ej. Karrantza Harana/Valle de Carranza).
    nombre_busqueda = nombre.split("/")[0].strip()
    normalizado = _ascii(nombre_busqueda).lower()
    return re.sub(r"[^a-z0-9]+", "_", normalizado).strip("_")


def slug_fotocasa(nombre: str) -> str:
    """Slugs de Fotocasa y alias oficiales observados en sus URLs actuales."""
    normalizado = _ascii(nombre).lower()
    clave = re.sub(r"[^a-z0-9]+", " ", normalizado).strip()
    aliases = {
        "agurain salvatierra": "salvatierra-agurain",
        "campezo kanpezu": "campezo-kampezu",
        "soraluze placencia de las armas": "soraluze-plasencia-de-las-armas",
    }
    return aliases.get(clave, re.sub(r"[^a-z0-9]+", "-", normalizado).strip("-"))
