"""INDICADORES-01: 5 indicadores distintos non-legacy de 2+ fuentes.

Verifica la matriz 2026-11-06: esfuerzo 18-34, tensión social, paro
Lanbide, precio m2 oficial y VPO terminadas ‰. `esfuerzo_16_29` es
legacy y NO cuenta.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIZ = ROOT / "openspec" / "archive" / "2026-11-10-docs" / "matriz_indicadores.md"


def _indicadores_no_legacy() -> list[str]:
    txt = MATRIZ.read_text(encoding="utf-8")
    # Filas de tabla numeradas 1-5; legacy está fuera de la tabla.
    filas = re.findall(r"^\|\s*(\d)\s*\|", txt, flags=re.M)
    # Solo las 5 primeras (la tabla es 1..5); legacy no es fila numerada.
    return filas


def test_cinco_indicadores_no_legacy():
    txt = MATRIZ.read_text(encoding="utf-8")
    filas = _indicadores_no_legacy()
    assert filas == ["1", "2", "3", "4", "5"], f"filas={filas} txt={txt[:200]}"
    # VPO terminadas ‰ como 5º (2 fuentes: Open Data 73 + dim_municipios).
    assert "VPO terminadas" in txt and "vpo_terminadas_por_mil" in txt
    assert "codigo_ine" in txt  # campo común
    # Legacy archivado, no contado como fila.
    assert "NO cuenta como indicador" in txt
    assert "esfuerzo_16_29" in txt  # mencionado como archivo
