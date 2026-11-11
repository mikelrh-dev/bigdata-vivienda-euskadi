"""Contrato del orquestador de extracción."""

from __future__ import annotations

from pathlib import Path
import csv

import pytest

from conftest import ROOT, load_module


@pytest.fixture
def ra():
    return load_module("extract_run_all_test", "extract/run_all.py")


def _script_path(paso) -> Path:
    if "/" in paso.script:
        return ROOT / paso.script
    return ROOT / "extract" / paso.script


def test_registro_sin_ids_duplicados(ra) -> None:
    ids = [paso.id for paso in ra.PASOS]
    assert len(ids) == len(set(ids))
    assert len(ra.PASOS) == 34


def test_cada_paso_declara_salidas(ra) -> None:
    assert all(paso.salidas for paso in ra.PASOS)


def test_todos_los_scripts_declarados_existen(ra) -> None:
    faltan = [paso.script for paso in ra.PASOS if not _script_path(paso).exists()]
    assert faltan == []


def test_inventario_cubre_todos_los_extractores_registrados(ra) -> None:
    ruta = ROOT / "extract" / "inventario_extractores.csv"
    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        filas = list(csv.DictReader(fh))
    columnas = {
        "script", "salidas_actuales", "formato_canonico", "consumidores",
        "red_credenciales", "lento_manual_obsoleto", "menu",
    }
    assert columnas <= set(filas[0])
    scripts = {fila["script"] for fila in filas}
    assert all(p.script.split("/")[-1] in scripts for p in ra.PASOS if not p.script.startswith("transform/"))


def test_anuncios_se_guardan_solo_en_json(ra) -> None:
    for paso in ra.PASOS:
        for salida in paso.salidas:
            if salida.startswith("anuncios_"):
                assert salida.endswith(".json"), (paso.id, salida)


def test_solo_el_catalogo_escribe_en_procesado(ra) -> None:
    for paso in ra.PASOS:
        for salida in paso.salidas:
            if salida.startswith("procesado/"):
                assert salida == "procesado/dim_municipios.json", (paso.id, salida)


def test_coincidencias_resuelve_prefijo_procesado(ra, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ra, "RAW_DIR", tmp_path / "raw")
    (tmp_path / "procesado").mkdir()
    objetivo = tmp_path / "procesado" / "dim_municipios.json"
    objetivo.write_text("{}", encoding="utf-8")
    assert ra._coincidencias("procesado/dim_municipios.json") == [objetivo]


def test_estado_completo_parcial_y_pendiente(ra, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ra, "RAW_DIR", tmp_path / "raw")
    paso = ra.Paso("x", "x.py", ("a.csv", "b.csv"))
    assert ra.estado(paso) == ("pendiente", 0, 2)
    (tmp_path / "raw").mkdir()
    (tmp_path / "raw" / "a.csv").write_text("", encoding="utf-8")
    assert ra.estado(paso) == ("parcial", 1, 2)
    (tmp_path / "raw" / "b.csv").write_text("", encoding="utf-8")
    assert ra.estado(paso) == ("completo", 2, 2)


def _fake_registry(ra, monkeypatch):
    pasos = (
        ra.Paso("a", "a.py", ("a.csv",)),
        ra.Paso("b", "b.py", ("b.csv",)),
    )
    monkeypatch.setattr(ra, "PASOS", pasos)
    monkeypatch.setattr(ra, "POR_ID", {p.id: p for p in pasos})
    return pasos


def test_seleccionar_only_respeta_orden_del_registro(ra, monkeypatch) -> None:
    _fake_registry(ra, monkeypatch)
    assert [p.id for p in ra.seleccionar("b,a", missing=False, force=False)] == ["a", "b"]


def test_seleccionar_only_desconocido_aborta(ra, monkeypatch) -> None:
    _fake_registry(ra, monkeypatch)
    with pytest.raises(SystemExit, match="desconocido"):
        ra.seleccionar("no-existe", missing=False, force=False)


def test_seleccionar_force_devuelve_todo(ra, monkeypatch) -> None:
    pasos = _fake_registry(ra, monkeypatch)
    assert ra.seleccionar(None, missing=False, force=True) == list(pasos)


def test_seleccionar_missing_excluye_completos(ra, monkeypatch) -> None:
    _fake_registry(ra, monkeypatch)
    monkeypatch.setattr(
        ra,
        "estado",
        lambda paso: ("completo", 1, 1) if paso.id == "a" else ("pendiente", 0, 1),
    )
    assert [p.id for p in ra.seleccionar(None, missing=True, force=False)] == ["b"]


def test_missing_excluye_lentos_y_scrapers_por_defecto(ra, monkeypatch) -> None:
    pasos = (
        ra.Paso("rapido", "a.py", ("a.csv",)),
        ra.Paso("lento", "b.py", ("b.csv",), lento=True),
        ra.Paso("scraper", "c.py", ("c.json",), scraper=True),
    )
    monkeypatch.setattr(ra, "PASOS", pasos)
    monkeypatch.setattr(ra, "POR_ID", {p.id: p for p in pasos})
    monkeypatch.setattr(ra, "estado", lambda paso: ("pendiente", 0, 1))
    assert [p.id for p in ra.seleccionar(None, missing=True, force=False)] == ["rapido"]
    assert [p.id for p in ra.seleccionar("scraper", missing=True, force=False)] == ["scraper"]


def test_aliases_check_y_run(ra, monkeypatch, capsys) -> None:
    monkeypatch.setattr(ra, "listar", lambda: print("CHECK_OK"))
    assert ra.main(["--check"]) == 0
    assert "CHECK_OK" in capsys.readouterr().out
    monkeypatch.setattr(ra, "seleccionar", lambda *a, **k: [])
    assert ra.main(["--run"]) == 0


def test_ejecutar_aisla_fallos_y_sigue(ra, tmp_path: Path, monkeypatch) -> None:
    pasos = (ra.Paso("a", "a.py", ("a.csv",)), ra.Paso("b", "b.py", ("b.csv",)))
    llamados: list[str] = []

    def fake_ejecutar(paso, log):
        llamados.append(paso.id)
        return paso.id == "b"

    monkeypatch.setattr(ra, "ensure_dirs", lambda: None)
    monkeypatch.setattr(ra, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(ra, "_ejecutar", fake_ejecutar)

    codigo = ra.ejecutar(list(pasos))

    assert codigo == 1
    assert llamados == ["a", "b"]
    log = next((tmp_path / "logs").glob("extract_*.log"))
    assert "Fallidos: a" in log.read_text(encoding="utf-8")


def test_ejecutar_devuelve_cero_si_todo_va_bien(ra, tmp_path: Path, monkeypatch) -> None:
    pasos = (ra.Paso("a", "a.py", ("a.csv",)),)
    monkeypatch.setattr(ra, "ensure_dirs", lambda: None)
    monkeypatch.setattr(ra, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(ra, "_ejecutar", lambda paso, log: True)
    assert ra.ejecutar(list(pasos)) == 0


def test_ejecutar_paso_sin_script_falla(ra, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ra, "PROJECT_ROOT", tmp_path)
    lineas: list[str] = []
    paso = ra.Paso("fantasma", "no_existe.py", ("x.csv",))
    assert ra._ejecutar(paso, lineas.append) is False
    assert any("no existe" in linea for linea in lineas)


def test_ejecutar_paso_con_salidas_incompletas_falla(ra, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ra, "PROJECT_ROOT", tmp_path)
    (tmp_path / "extract").mkdir()
    (tmp_path / "extract" / "ok.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(ra, "estado", lambda paso: ("parcial", 1, 2))

    class Proceso:
        stdout = iter(["linea\n"])

        def wait(self) -> int:
            return 0

    monkeypatch.setattr(ra.subprocess, "Popen", lambda *a, **k: Proceso())
    lineas: list[str] = []
    paso = ra.Paso("ok", "ok.py", ("a.csv", "b.csv"))
    assert ra._ejecutar(paso, lineas.append) is False
    assert any("faltan salidas" in linea for linea in lineas)


def test_main_list_no_ejecuta(ra, monkeypatch, capsys) -> None:
    def prohibido(*args, **kwargs):
        raise AssertionError("--list no debe ejecutar")

    monkeypatch.setattr(ra, "ejecutar", prohibido)
    assert ra.main(["--list"]) == 0
    salida = capsys.readouterr().out
    assert "eustat" in salida and "dim-municipios" in salida


def test_main_missing_sin_pendientes_no_ejecuta(ra, monkeypatch, capsys) -> None:
    monkeypatch.setattr(ra, "seleccionar", lambda *a, **k: [])
    monkeypatch.setattr(ra, "ejecutar", lambda pasos: pytest.fail("no debe ejecutar"))
    assert ra.main(["--missing"]) == 0
    assert "No hay nada pendiente" in capsys.readouterr().out
