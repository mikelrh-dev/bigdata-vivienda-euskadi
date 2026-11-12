"""Helpers del contrato de comparabilidad (config/comparabilidad.yaml).

Funciones puras, sin I/O ni Mongo, para que los generadores de figuras y los
tests compartan las mismas reglas de capas, unidades y denominadores.
"""
from __future__ import annotations

from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
CONFIG = BASE / "config" / "comparabilidad.yaml"

_cache: dict | None = None


def cargar() -> dict:
    global _cache
    if _cache is None:
        with CONFIG.open(encoding="utf-8") as fh:
            _cache = yaml.safe_load(fh)
    assert _cache is not None
    return _cache


def es_capa(fila: dict, capa: str) -> bool:
    """True si la fila pertenece a la capa indicada (oficial/idw/contexto)."""
    return str(fila.get("metodo_imputacion")) == capa


def filtrar_capa(filas: list[dict], capa: str) -> list[dict]:
    """Devuelve solo las filas de la capa indicada."""
    return [f for f in filas if es_capa(f, capa)]


def etiqueta_vintage(métrica: str) -> str:
    """Vintage declarado de una métrica."""
    return str(cargar()["vintages"].get(métrica, "sin declarar"))


def denominador_de(esfuerzo: str) -> str:
    """Denominador declarado de una variante de esfuerzo."""
    return str(cargar()["denominadores"].get(esfuerzo, "sin declarar"))


def canonico_esfuerzo() -> str:
    """Nombre del esfuerzo canónico."""
    return str(cargar()["canonico"]["esfuerzo"])


def assert_misma_unidad(unidad: str) -> None:
    """Falla si la unidad no está en el contrato."""
    if unidad not in cargar()["unidades"]:
        raise ValueError(f"unidad no declarada en el contrato: {unidad}")


def es_alias_legacy(columna: str) -> bool:
    """True si la columna es un alias legacy declarado."""
    return columna in cargar()["aliases_legacy"]
