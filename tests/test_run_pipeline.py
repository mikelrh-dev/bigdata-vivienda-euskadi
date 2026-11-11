"""Orquestador de fases (scripts/run_pipeline.py).

Sin subprocess real: _ejecutar y preflight se monkeypatchean. Se valida el
contrato de seguridad (mongo nunca en `all`, fase mongo opt-in), el orden de
las fases y el trato de los avisos de quality.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "scripts_run_pipeline", ROOT / "scripts" / "run_pipeline.py")
assert _spec is not None and _spec.loader is not None
rp = importlib.util.module_from_spec(_spec)
# dataclasses resuelve el modulo via sys.modules durante el decorado
sys.modules[_spec.name] = rp
_spec.loader.exec_module(rp)


@pytest.fixture()
def sin_subprocess(monkeypatch):
    """Cualquier intento de ejecutar un paso real revienta el test."""
    def _boom(paso, silencioso=False):
        raise AssertionError(f"no deberia ejecutarse {paso.nombre}")
    monkeypatch.setattr(rp, "_ejecutar", _boom)


def test_all_no_incluye_mongo():
    """La carga de Mongo es destructiva: `all` nunca la arrastra."""
    nombres = [f.nombre for f in rp.resolver_fases(["all"])]
    assert nombres == ["silver", "quality", "gold"]
    assert "mongo" not in nombres


def test_fases_desconocidas_fallan():
    with pytest.raises(ValueError, match="desconocida"):
        rp.resolver_fases(["oro"])


def test_plan_silver_es_run_all():
    assert [p.nombre for p in rp.FASES["silver"].pasos] == ["run_all"]
    assert rp.FASES["silver"].pasos[0].args == ("transform/run_all.py",)


def test_plan_quality_en_orden():
    pasos = [p.nombre for p in rp.FASES["quality"].pasos]
    assert pasos == ["normalizar_metadata", "nombres_normalizados_map",
                     "generar_ingestion_manifest", "generar_manifest"]
    # el manifest hashea la capa: debe ser el ultimo paso
    assert pasos[-1] == "generar_manifest"
    normalizar = rp.FASES["quality"].pasos[0]
    # rc=1 de normalizar_metadata es aviso de calidad, no fallo de ejecucion
    assert 1 in normalizar.tolerar_rc


def test_plan_gold_respeta_dependencias():
    """Analisis antes de figuras: las figuras leen los CSV generados."""
    pasos = [p.nombre for p in rp.FASES["gold"].pasos]
    assert pasos == ["run_analisis_mongo", "comparativa_mongo",
                     "sensibilidad", "generar_figuras_N"]
    assert pasos.index("run_analisis_mongo") < pasos.index("sensibilidad")


def test_dry_run_no_ejecuta(monkeypatch, capsys, sin_subprocess):
    monkeypatch.setattr(rp, "preflight", lambda verificar_hash: rp.EXIT_OK)
    assert rp.main(["--fase", "all", "--dry-run"]) == rp.EXIT_OK
    salida = capsys.readouterr().out
    assert "PLAN" in salida
    assert "generar_figuras_N" in salida


def test_mongo_sin_flag_aborta(monkeypatch, capsys, sin_subprocess):
    monkeypatch.setattr(rp, "preflight", lambda verificar_hash: rp.EXIT_OK)
    assert rp.main(["--fase", "mongo"]) == rp.EXIT_PREFLIGHT
    assert "--allow-mongo-write" in capsys.readouterr().err


def test_mongo_con_flag_se_ejecuta(monkeypatch):
    ejecutados: list[str] = []
    monkeypatch.setattr(rp, "preflight", lambda verificar_hash: rp.EXIT_OK)
    monkeypatch.setattr(rp, "_ejecutar",
                        lambda paso, silencioso=False: ejecutados.append(paso.nombre) or 0)
    assert rp.main(["--fase", "mongo", "--allow-mongo-write"]) == rp.EXIT_OK
    assert ejecutados == ["run_mongo_pipeline"]


def test_aviso_no_bloquea_sin_strict(monkeypatch, capsys):
    def _falso(paso, silencioso=False):
        return 1 if paso.nombre == "normalizar_metadata" else 0
    monkeypatch.setattr(rp, "preflight", lambda verificar_hash: rp.EXIT_OK)
    monkeypatch.setattr(rp, "_ejecutar", _falso)
    assert rp.main(["--fase", "quality"]) == rp.EXIT_OK
    assert "AVISO" in capsys.readouterr().out


def test_strict_convierte_aviso_en_fallo(monkeypatch):
    def _falso(paso, silencioso=False):
        return 1 if paso.nombre == "normalizar_metadata" else 0
    monkeypatch.setattr(rp, "preflight", lambda verificar_hash: rp.EXIT_OK)
    monkeypatch.setattr(rp, "_ejecutar", _falso)
    assert rp.main(["--fase", "quality", "--strict"]) == rp.EXIT_FALLO


def test_fallo_aborta_la_fase(monkeypatch):
    ejecutados: list[str] = []

    def _falla(paso, silencioso=False):
        ejecutados.append(paso.nombre)
        return 2
    monkeypatch.setattr(rp, "preflight", lambda verificar_hash: rp.EXIT_OK)
    monkeypatch.setattr(rp, "_ejecutar", _falla)
    assert rp.main(["--fase", "gold"]) == rp.EXIT_FALLO
    assert ejecutados == ["run_analisis_mongo"]  # no sigue con comparativa


def test_preflight_no_exige_procesado(tmp_path, monkeypatch):
    """El caso de uso es reconstruir desde cero: procesado puede no existir."""
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "x.csv").write_text("a", encoding="utf-8")
    monkeypatch.setattr(rp, "RAW_DIR", raw)
    monkeypatch.setattr(rp, "PROC_DIR", tmp_path / "procesado")
    assert rp.preflight(verificar_hash=False) == rp.EXIT_OK


def test_preflight_falla_sin_raw(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "RAW_DIR", tmp_path / "no_existe")
    monkeypatch.setattr(rp, "PROC_DIR", tmp_path / "procesado")
    assert rp.preflight(verificar_hash=False) == rp.EXIT_PREFLIGHT


def test_comparativa_mongo_importa_lanzada_como_script():
    """gold la ejecuta como script: sys.path[0]=analysis/ y `analysis.*` debe resolver.

    Regresion detectada al ejecutar la fase: el import fallaba con
    ModuleNotFoundError y gold abortaba en el segundo paso.
    """
    import subprocess
    codigo = ("import sys, runpy; sys.path[0] = 'analysis'; "
              "runpy.run_path('analysis/comparativa_mongo.py', run_name='no_main')")
    proc = subprocess.run([sys.executable, "-c", codigo], cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr


def test_check_solo_hace_preflight(monkeypatch, sin_subprocess):
    llamadas: list[bool] = []
    monkeypatch.setattr(rp, "preflight",
                        lambda verificar_hash: llamadas.append(verificar_hash) or 0)
    assert rp.main(["--check"]) == rp.EXIT_OK
    assert llamadas == [True]
