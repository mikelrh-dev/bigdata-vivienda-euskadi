"""Contrato del orquestador de transformaciones."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import ROOT, load_module


@pytest.fixture
def tr():
    return load_module("transform_run_all_test", "transform/run_all.py")


def test_registro_sin_ids_duplicados(tr) -> None:
    ids = [paso.id for paso in tr.PASOS]
    assert len(ids) == len(set(ids))
    assert len(tr.PASOS) == 31


def test_cada_paso_declara_salidas(tr) -> None:
    assert all(paso.salidas for paso in tr.PASOS)


def test_todos_los_scripts_declarados_existen(tr) -> None:
    faltan = [p.script for p in tr.PASOS if not (ROOT / "transform" / p.script).exists()]
    assert faltan == []


def test_salidas_son_nombres_planos_en_procesado(tr) -> None:
    for paso in tr.PASOS:
        for salida in paso.salidas:
            assert "/" not in salida and "\\" not in salida, (paso.id, salida)


def test_dim_municipios_va_primero(tr) -> None:
    assert tr.PASOS[0].id == "dim-municipios"


def test_poblacion_joven_antes_que_eustat_demografia(tr) -> None:
    ids = [paso.id for paso in tr.PASOS]
    assert ids.index("poblacion-joven") < ids.index("eustat-demografia")


def test_estado_completo_parcial_y_pendiente(tr, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(tr, "PROCESADO_DIR", tmp_path)
    paso = tr.Paso("x", "x.py", ("a.csv", "b.csv"))
    assert tr.estado(paso) == ("pendiente", 0, 2)
    (tmp_path / "a.csv").write_text("", encoding="utf-8")
    assert tr.estado(paso) == ("parcial", 1, 2)
    (tmp_path / "b.csv").write_text("", encoding="utf-8")
    assert tr.estado(paso) == ("completo", 2, 2)


def test_estado_admite_globs(tr, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(tr, "PROCESADO_DIR", tmp_path)
    (tmp_path / "salida_2026.csv").write_text("", encoding="utf-8")
    paso = tr.Paso("x", "x.py", ("salida_*.csv",))
    assert tr.estado(paso) == ("completo", 1, 1)


def _fake_registry(tr, monkeypatch):
    pasos = (
        tr.Paso("a", "a.py", ("a.csv",)),
        tr.Paso("b", "b.py", ("b.csv",)),
    )
    monkeypatch.setattr(tr, "PASOS", pasos)
    monkeypatch.setattr(tr, "POR_ID", {p.id: p for p in pasos})
    return pasos


def test_seleccionar_only_respeta_orden_del_registro(tr, monkeypatch) -> None:
    _fake_registry(tr, monkeypatch)
    assert [p.id for p in tr.seleccionar("b,a", missing=False, force=False)] == ["a", "b"]


def test_seleccionar_only_desconocido_aborta(tr, monkeypatch) -> None:
    _fake_registry(tr, monkeypatch)
    with pytest.raises(SystemExit, match="desconocido"):
        tr.seleccionar("no-existe", missing=False, force=False)


def test_seleccionar_force_devuelve_todo(tr, monkeypatch) -> None:
    pasos = _fake_registry(tr, monkeypatch)
    assert tr.seleccionar(None, missing=False, force=True) == list(pasos)


def test_seleccionar_missing_excluye_completos(tr, monkeypatch) -> None:
    _fake_registry(tr, monkeypatch)
    monkeypatch.setattr(
        tr,
        "estado",
        lambda paso: ("completo", 1, 1) if paso.id == "a" else ("pendiente", 0, 1),
    )
    assert [p.id for p in tr.seleccionar(None, missing=True, force=False)] == ["b"]


def test_ejecutar_aisla_fallos_y_sigue(tr, tmp_path: Path, monkeypatch) -> None:
    pasos = (tr.Paso("a", "a.py", ("a.csv",)), tr.Paso("b", "b.py", ("b.csv",)))
    llamados: list[str] = []

    def fake_ejecutar(paso, log):
        llamados.append(paso.id)
        return paso.id == "b"

    monkeypatch.setattr(tr, "ensure_dirs", lambda: None)
    monkeypatch.setattr(tr, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(tr, "_ejecutar", fake_ejecutar)

    assert tr.ejecutar(list(pasos)) == 1
    assert llamados == ["a", "b"]
    log = next((tmp_path / "logs").glob("transform_*.log"))
    assert "Fallidos: a" in log.read_text(encoding="utf-8")


def test_ejecutar_devuelve_cero_si_todo_va_bien(tr, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(tr, "ensure_dirs", lambda: None)
    monkeypatch.setattr(tr, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(tr, "_ejecutar", lambda paso, log: True)
    assert tr.ejecutar([tr.Paso("a", "a.py", ("a.csv",))]) == 0


def test_main_list_no_ejecuta(tr, monkeypatch, capsys) -> None:
    def prohibido(*args, **kwargs):
        raise AssertionError("--list no debe ejecutar")

    monkeypatch.setattr(tr, "ejecutar", prohibido)
    assert tr.main(["--list"]) == 0
    salida = capsys.readouterr().out
    assert "dim-municipios" in salida and "unificar" in salida


def test_main_missing_sin_pendientes_no_ejecuta(tr, monkeypatch, capsys) -> None:
    monkeypatch.setattr(tr, "seleccionar", lambda *a, **k: [])
    monkeypatch.setattr(tr, "ejecutar", lambda pasos: pytest.fail("no debe ejecutar"))
    assert tr.main(["--missing"]) == 0
    assert "No hay nada pendiente" in capsys.readouterr().out


def test_orquestador_sin_guardrails_de_manifest(tr) -> None:
    fuente = (ROOT / "transform" / "run_all.py").read_text(encoding="utf-8").lower()
    for prohibido in ("sha256", "run_manifest", "staleness"):
        assert prohibido not in fuente
