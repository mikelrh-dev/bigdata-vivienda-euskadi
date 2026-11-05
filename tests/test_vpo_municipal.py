"""Contrato del indicador municipal de VPO terminadas (Udalmap 73)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

RAW = BASE / "data" / "raw" / "udalmap_vpo_terminadas.csv"
PROC = BASE / "data" / "procesado" / "vpo_municipal.csv"


@pytest.fixture(scope="module")
def vpo() -> pd.DataFrame:
    if not PROC.exists():
        pytest.skip("vpo_municipal.csv no generado")
    return pd.read_csv(PROC, dtype={"codigo_ine": str})


def test_252_municipios_unicos(vpo: pd.DataFrame) -> None:
    assert len(vpo) == 252
    assert vpo["codigo_ine"].is_unique
    assert vpo["codigo_ine"].str.len().eq(5).all()


def test_valores_en_rango(vpo: pd.DataFrame) -> None:
    valores = vpo["vpo_terminadas_por_mil"].dropna()
    assert valores.between(0, 100).all()


def test_sin_dato_declarado_no_imputado(vpo: pd.DataFrame) -> None:
    """Usansolo (48916, segregado en 2023) aun no tiene VPO publicada."""
    sin_dato = vpo[vpo["vpo_terminadas_por_mil"].isna()]["codigo_ine"].tolist()
    assert sin_dato == ["48916"]


def test_anio_y_fuente_declarados(vpo: pd.DataFrame) -> None:
    assert (vpo["anio_fuente"] == 2024).all()
    assert vpo["fuente"].str.contains("Udalmap", case=False).all()
    assert vpo["fuente_url"].str.startswith("https://").all()


def test_municipios_robustos_presentes(vpo: pd.DataFrame) -> None:
    por_codigo = vpo.set_index("codigo_ine")["vpo_terminadas_por_mil"]
    for codigo in ("48020", "20069", "48044", "01059"):
        assert codigo in por_codigo.index


def test_es_flujo_no_stock(vpo: pd.DataFrame) -> None:
    # El origen no publica NumViviendas: la columna de stock no debe existir.
    assert "viviendas" not in vpo.columns
    assert "num_viviendas" not in vpo.columns
