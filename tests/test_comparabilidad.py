"""Tests del contrato de comparabilidad (config/comparabilidad.yaml)."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from analysis import comparabilidad as cmp

BASE = Path(__file__).resolve().parents[1]


def test_config_carga_y_capas():
    cfg = cmp.cargar()
    assert set(cfg["capas"]) == {"oficial", "idw", "contexto"}
    assert cfg["capas"]["oficial"]["municipios"] == 159
    assert cfg["capas"]["idw"]["municipios"] == 93
    assert cfg["capas"]["oficial"]["is_imputed"] is False
    assert cfg["capas"]["idw"]["is_imputed"] is True


def test_canonico_y_denominador():
    assert cmp.canonico_esfuerzo() == "esfuerzo_joven_pct_18_34"
    assert "INE_Atlas" in cmp.denominador_de("esfuerzo_joven_pct_18_34")


def test_filtrar_capa():
    filas = [
        {"metodo_imputacion": "oficial", "v": 1},
        {"metodo_imputacion": "idw", "v": 2},
        {"metodo_imputacion": "oficial", "v": 3},
    ]
    assert len(cmp.filtrar_capa(filas, "oficial")) == 2
    assert len(cmp.filtrar_capa(filas, "idw")) == 1


def test_unidades_y_vintages():
    cmp.assert_misma_unidad("eur_m2")
    with pytest.raises(ValueError):
        cmp.assert_misma_unidad("eur_hora")
    assert cmp.etiqueta_vintage("alquiler") == "2024"
    assert cmp.etiqueta_vintage("anuncios") == "2026"


def test_alias_legacy():
    assert cmp.es_alias_legacy("esfuerzo_joven_pct")
    assert cmp.es_alias_legacy("esfuerzo_alquiler_pct")
    assert not cmp.es_alias_legacy("esfuerzo_joven_pct_18_34")


def test_matriz_doc_coherente():
    texto = (BASE / "docs" / "matriz-comparabilidad.md").read_text(encoding="utf-8")
    assert "oficial 159" in texto
    assert "IDW 93" in texto
    assert "no comparable" in texto.lower()


def test_parametros_declaran_ine_atlas():
    with (BASE / "config" / "parametros_estudio.yaml").open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    assert "INE Atlas" in cfg["fuentes"]["renta"]
    assert "Udalmap 2024" in cfg["fuentes"]["paro"]
