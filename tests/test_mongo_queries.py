"""Consultas del reto: cada una debe devolver filas reales.

Cubre RA3 «Consultas» (≥5 útiles, una con campos anidados o arrays y otra
combinando 2+ condiciones) y cierra la regresión detectada en la auditoría
del 2026-11-06: `anuncios_con_equipamiento("ascensor")` devolvía 0 filas
porque el vocabulario real de `equipamiento` es
exterior/balcon/interior/parking (679 de 759 anuncios lo tienen vacío).

Solo lectura: no escribe en MongoDB ni en `data/`.
"""

from __future__ import annotations

import pytest

from analysis import mongo_queries as mq
from storage.mongo import ping

# Bilbao: 173 anuncios en la carga del 2026-11-06.
MUNICIPIO = "48020"


@pytest.fixture(scope="module", autouse=True)
def _mongo_vivo() -> None:
    assert ping() is True, "MongoDB no responde en localhost:27017"


def test_consulta_por_municipio_devuelve_filas() -> None:
    filas = mq.anuncios_por_municipio(MUNICIPIO)
    assert filas, f"sin anuncios para {MUNICIPIO}"
    assert all(f["ubicacion"]["codigo_ine"] == MUNICIPIO for f in filas)


def test_consulta_dos_condiciones_devuelve_filas() -> None:
    filas = mq.anuncios_por_municipio(
        MUNICIPIO, modalidad="larga_estancia", precio_max=1500
    )
    assert filas, "la consulta de 2 condiciones no devuelve nada"
    assert all(f["modalidad"] == "larga_estancia" for f in filas)


def test_consulta_campo_anidado_dot_notation() -> None:
    filas = mq.dot_notation_municipio(MUNICIPIO)
    assert filas, "dot notation sobre ubicacion.codigo_ine no devuelve nada"
    assert filas[0]["ubicacion"]["codigo_ine"] == MUNICIPIO


def test_consulta_array_equipamiento_devuelve_filas() -> None:
    """El array tiene vocabulario cerrado: usar un valor que exista."""
    filas = mq.anuncios_con_equipamiento("exterior")
    assert filas, "ningún anuncio con equipamiento='exterior': revisa el vocabulario real"
    assert all("exterior" in (f.get("equipamiento") or []) for f in filas)


def test_consulta_regex_y_orden_limite() -> None:
    assert mq.anuncios_regex("ubicacion.municipio", "vitoria"), "regex sin resultados"
    assert len(mq.anuncios_ordenar_limitar("precio_eur", limit=5)) == 5


def test_demo_no_tiene_consultas_vacias() -> None:
    """Cualquier consulta de la demo que devuelva 0 es una regresión."""
    res = mq.busqueda_avanzada_demo()
    vacias = [clave for clave, valor in res.items() if valor == 0]
    assert not vacias, f"consultas de la demo sin resultados: {vacias}"
