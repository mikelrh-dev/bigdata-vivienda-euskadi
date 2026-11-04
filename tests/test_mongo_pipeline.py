"""Tests del entrypoint único del pipeline MongoDB (sin tocar producción).

El módulo scripts/run_mongo_pipeline.py no es un paquete; se carga por ruta
con importlib y las cuatro funciones se sustituyen por espías con monkeypatch.
Ningún test de este fichero llama a load_all/clean_all reales ni muta la
base productiva.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "run_mongo_pipeline.py"


def _load_module() -> ModuleType:
    assert SCRIPT.exists(), "no existe scripts/run_mongo_pipeline.py"
    spec = importlib.util.spec_from_file_location("run_mongo_pipeline", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("run_mongo_pipeline", module)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _prod_count() -> int | None:
    try:
        from storage.mongo import get_collection, ping

        if not ping():
            return None
        return get_collection("anuncios").count_documents({})
    except Exception:
        return None


def _install_spies(module: ModuleType, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []

    def fake_load_all() -> dict[str, int]:
        calls.append("load_all")
        return {"municipios": 252, "anuncios": 700}

    def fake_clean_all() -> dict[str, Any]:
        calls.append("clean_all")
        return {
            "anuncios": {
                "canonicalize": {"modified_count": 2, "deleted_count": 0},
                "duplicates": {"deleted": 1, "modified_count": 0, "deleted_count": 1},
            }
        }

    def fake_ensure_indexes() -> dict[str, str]:
        calls.append("ensure_indexes")
        return {"anuncios_compound": "idx_anuncios_ine_modalidad_precio"}

    def fake_pipeline() -> list[dict[str, Any]]:
        calls.append("pipeline_indicadores_municipio")
        return [{"_id": "48001"}, {"_id": "48002"}]

    monkeypatch.setattr(module, "load_all", fake_load_all)
    monkeypatch.setattr(module, "clean_all", fake_clean_all)
    monkeypatch.setattr(module, "ensure_indexes", fake_ensure_indexes)
    monkeypatch.setattr(
        module, "pipeline_indicadores_municipio", fake_pipeline
    )
    return calls


def test_pipeline_entrypoint_existe(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """El entrypoint existe y main llama a load_all primero, sin tocar prod."""
    module = _load_module()
    assert hasattr(module, "main")
    prod_before = _prod_count()
    calls = _install_spies(module, monkeypatch)
    exit_code = module.main([])
    assert exit_code == 0
    assert calls == [
        "load_all",
        "clean_all",
        "ensure_indexes",
        "pipeline_indicadores_municipio",
    ]
    out = capsys.readouterr().out
    assert "load_all" in out
    assert "modified_count: 2" in out
    assert "deleted_count: 1" in out
    assert "indicadores: 2" in out
    prod_after = _prod_count()
    if prod_before is not None:
        assert prod_after == prod_before


def test_dry_run_no_muta_prod(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """--dry-run solo valida imports y ping; no llama a las funciones de carga."""
    module = _load_module()
    calls = _install_spies(module, monkeypatch)
    monkeypatch.setattr(module, "ping", lambda: True)
    prod_before = _prod_count()
    assert module.main(["--dry-run"]) == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "dry-run" in out and "ping=True" in out
    prod_after = _prod_count()
    if prod_before is not None:
        assert prod_after == prod_before
