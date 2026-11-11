"""Contrato de rutas de los scripts de análisis."""

from __future__ import annotations

import re
import sys
import types
from pathlib import Path

import pytest

from conftest import ROOT, load_module

ANALYSIS_DIR = ROOT / "analysis"
SIN_RUTAS = {"__init__.py", "_common.py", "mongo_aggregations.py", "mongo_indexes.py", "mongo_queries.py"}


def _fake_modules(tmp_path: Path, monkeypatch):
    proc = tmp_path / "procesado"
    res = tmp_path / "resultados"
    raw = tmp_path / "raw"
    paths = types.ModuleType("paths")
    paths.DATA_DIR = tmp_path
    paths.RAW_DIR = raw
    paths.PROCESADO_DIR = proc
    paths.RESULTADOS_DIR = res
    paths.ensure_dirs = lambda: None
    common = types.ModuleType("_common")
    common.PROJECT_ROOT = ROOT
    common.DATA_DIR = tmp_path
    common.RAW_DIR = raw
    common.PROCESADO_DIR = proc
    common.RESULTADOS_DIR = res
    common.ensure_dirs = lambda: None
    monkeypatch.setitem(sys.modules, "paths", paths)
    monkeypatch.setitem(sys.modules, "_common", common)
    return proc, res


@pytest.mark.parametrize(
    ("nombre", "modulo"),
    [
        ("dashboard_completo_test", "analysis/generar_dashboard_completo.py"),
        ("dashboard_visual_test", "analysis/generar_dashboard_visual.py"),
    ],
)
def test_q_sustituye_la_ruta_logica(nombre, modulo, tmp_path: Path, monkeypatch) -> None:
    proc, res = _fake_modules(tmp_path, monkeypatch)
    proc.mkdir()
    (proc / "prueba.csv").write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    dashboard = load_module(nombre, modulo)

    assert dashboard.PROC == proc
    assert dashboard.OUT == res

    df = dashboard._q("SELECT SUM(a) AS s FROM read_csv('data/procesado/prueba.csv')")
    assert int(df.loc[0, "s"]) == 4


def test_analysis_common_reexporta_las_rutas(tmp_path: Path, monkeypatch) -> None:
    proc, res = _fake_modules(tmp_path, monkeypatch)
    common = load_module("analysis_common_test", "analysis/_common.py")
    assert common.DATA_DIR == tmp_path
    assert common.PROCESADO_DIR == proc
    assert common.RESULTADOS_DIR == res


def test_analysis_no_compone_rutas_data_a_mano() -> None:
    prohibidos = [
        re.compile(r"os\.path\.join\(\s*[\"']data[\"']"),
        re.compile(r"Path\(\s*[\"']data[\"']"),
        re.compile(r"[\"']data[\"']\s*/\s*[\"']"),
    ]
    infractores = []
    for ruta in sorted(ANALYSIS_DIR.glob("*.py")):
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for patron in prohibidos:
            if patron.search(texto):
                infractores.append(ruta.name)
                break
    assert infractores == []


def test_analysis_no_escribe_en_procesado() -> None:
    patrones = [
        re.compile(r"to_csv\(\s*PROC\b"),
        re.compile(r"PROC\s*/\s*[^\n]*\.write_text"),
        re.compile(r"PROC\s*/\s*[^\n]*\.savefig"),
    ]
    infractores = []
    for ruta in sorted(ANALYSIS_DIR.glob("*.py")):
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for patron in patrones:
            if patron.search(texto):
                infractores.append(ruta.name)
                break
    assert infractores == []


def test_todos_los_scripts_de_analysis_usan_paths() -> None:
    sin_rutas = []
    for ruta in sorted(ANALYSIS_DIR.glob("*.py")):
        if ruta.name in SIN_RUTAS:
            continue
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        if "from _common import" not in texto and "from paths import" not in texto:
            sin_rutas.append(ruta.name)
    assert sin_rutas == []
