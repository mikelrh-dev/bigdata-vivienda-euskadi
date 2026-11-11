"""Contrato de ``paths.py``: única fuente de rutas del pipeline."""

from __future__ import annotations

from pathlib import Path

from conftest import ROOT, load_module


def _paths(monkeypatch, data_dir: str) -> object:
    monkeypatch.setenv("DATA_DIR", data_dir)
    return load_module("paths_under_test", "paths.py")


def test_data_dir_por_defecto_fuera_del_repositorio(monkeypatch) -> None:
    monkeypatch.delenv("DATA_DIR", raising=False)
    mod = load_module("paths_default", "paths.py")
    assert mod.DEFAULT_DATA_DIR == "../data_nuevo"
    assert mod.DATA_DIR == (ROOT.parent / "data_nuevo").resolve()


def test_data_dir_relativo_se_resuelve_contra_la_raiz(monkeypatch) -> None:
    mod = _paths(monkeypatch, "datos_de_prueba")
    assert mod.DATA_DIR == (ROOT / "datos_de_prueba").resolve()


def test_data_dir_absoluto_se_respeta(monkeypatch, tmp_path: Path) -> None:
    mod = _paths(monkeypatch, str(tmp_path))
    assert mod.DATA_DIR == tmp_path.resolve()
    assert mod.RAW_DIR == tmp_path.resolve() / "raw"
    assert mod.PROCESADO_DIR == tmp_path.resolve() / "procesado"
    assert mod.RESULTADOS_DIR == tmp_path.resolve() / "resultados"


def test_variable_de_entorno_prevalece_sobre_env(monkeypatch, tmp_path: Path) -> None:
    mod = _paths(monkeypatch, str(tmp_path / "elegido"))
    assert mod.DATA_DIR == (tmp_path / "elegido").resolve()


def test_importar_no_crea_directorios(monkeypatch, tmp_path: Path) -> None:
    destino = tmp_path / "todavia_no_existe"
    _paths(monkeypatch, str(destino))
    assert not destino.exists()


def test_ensure_dirs_crea_las_tres_capas(monkeypatch, tmp_path: Path) -> None:
    destino = tmp_path / "datos"
    mod = _paths(monkeypatch, str(destino))
    mod.ensure_dirs()
    assert mod.RAW_DIR.is_dir()
    assert mod.PROCESADO_DIR.is_dir()
    assert mod.RESULTADOS_DIR.is_dir()
