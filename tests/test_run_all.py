"""Orquestador run_all con tmp_path (transform/run_all.py).

_orden_topologico respeta el DAG productor->consumidor,
_salidas/_entradas resuelven prefijos proc:/raw: contra tmp_path y
_estado marca OK cuando la salida es fresca (skip) y DESACTUALIZADO/
FALTA/SIN-DECLARAR en los demas casos. Sin subprocess real.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "transform_run_all", ROOT / "transform" / "run_all.py")
assert _spec is not None and _spec.loader is not None
ra = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ra)


@pytest.fixture()
def dag(tmp_path, monkeypatch):
    """DAG sintetico a -> b -> c sobre tmp_path (sin tocar data/procesado)."""
    proc = tmp_path / "proc"
    raw = tmp_path / "raw"
    proc.mkdir()
    raw.mkdir()
    monkeypatch.setattr(ra, "BASES", {"raw": raw, "proc": proc,
                                       "res": tmp_path / "res"})
    monkeypatch.setattr(ra, "PROCESADO_DIR", proc)
    monkeypatch.setattr(ra, "SCRIPTS", {
        "a.py": {"group": "g", "in": ["raw:x.csv"],
                 "out": ["proc:a.csv"], "out_glob": []},
        "b.py": {"group": "g", "in": ["proc:a.csv"],
                 "out": ["proc:b.csv"], "out_glob": []},
        "c.py": {"group": "g", "in": ["proc:b.csv"],
                 "out": ["proc:c.csv"], "out_glob": []},
        "sin_salida.py": {"group": "g", "in": [], "out": [], "out_glob": []},
    })
    return proc, raw


def _tocar(path: Path, mtime: float) -> None:
    path.write_bytes(b"x")
    os.utime(path, (mtime, mtime))


def test_orden_topologico_respeta_dag(dag):
    """Aunque se pase en orden inverso, el orden sale a,b,c (sin_salida al final relativo)."""
    orden = ra._orden_topologico(["c.py", "b.py", "a.py"])
    assert orden == ["a.py", "b.py", "c.py"]
    # b escribe lo que consume c, a lo que consume b: indices crecientes
    assert orden.index("a.py") < orden.index("b.py") < orden.index("c.py")


def test_salidas_y_entradas_resuelven_prefijos(dag):
    proc, raw = dag
    assert ra._salidas("b.py") == [proc / "b.csv"]
    assert ra._entradas("b.py") == [proc / "a.csv"]
    assert ra._entradas("a.py") == [raw / "x.csv"]
    assert ra._salidas("sin_salida.py") == []


def test_estado_ok_cuando_salida_fresca(dag):
    """Salida mas nueva que la entrada -> OK (skip: no hay que re-ejecutar)."""
    proc, raw = dag
    ahora = time.time()
    _tocar(raw / "x.csv", ahora - 100)
    _tocar(proc / "a.csv", ahora - 10)
    estado, _detalle = ra._estado("a.py")
    assert estado == "OK"


def test_estado_desactualizado_cuando_entrada_mas_nueva(dag):
    """Entrada mas nueva que la salida -> DESACTUALIZADO."""
    proc, raw = dag
    ahora = time.time()
    _tocar(proc / "a.csv", ahora - 100)
    _tocar(raw / "x.csv", ahora - 10)
    estado, detalle = ra._estado("a.py")
    assert estado == "DESACTUALIZADO"
    assert "x.csv" in detalle


def test_estado_falta_y_sin_declarar(dag):
    """Sin salida en disco -> FALTA; sin salidas declaradas -> SIN-DECLARAR."""
    estado, detalle = ra._estado("b.py")
    assert estado == "FALTA"
    assert "b.csv" in detalle
    estado2, _ = ra._estado("sin_salida.py")
    assert estado2 == "SIN-DECLARAR"


def test_estado_entrada_inexistente_no_da_falso_ok(dag):
    """Una entrada declarada que falta no puede reportarse como OK.

    Protege el caso de un arbol sin data/raw (clon o entrega a terceros):
    `_resolver` devuelve la ruta aunque no exista, asi que el chequeo debe
    mirar `.exists()` o daría por buena una salida que no se puede reproducir.
    """
    proc, raw = dag
    ahora = time.time()
    _tocar(proc / "a.csv", ahora - 10)  # salida presente y fresca
    assert not (raw / "x.csv").exists()  # falta la entrada declarada
    estado, detalle = ra._estado("a.py")
    assert estado == "DESACTUALIZADO"
    assert "x.csv" in detalle
