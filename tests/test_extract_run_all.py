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
    return ROOT / "extract" / paso.script


def test_registro_sin_ids_duplicados(ra) -> None:
    ids = [paso.id for paso in ra.PASOS]
    assert len(ids) == len(set(ids))
    assert len(ra.PASOS) == 33


def test_cada_paso_declara_salidas(ra) -> None:
    assert all(paso.salidas for paso in ra.PASOS)


def test_todos_los_scripts_declarados_existen(ra) -> None:
    faltan = [paso.script for paso in ra.PASOS if not _script_path(paso).exists()]
    assert faltan == []
    assert all(Path(paso.script).name == paso.script for paso in ra.PASOS)


def test_slugs_portales_usan_aliases_actuales() -> None:
    from conftest import load_module

    pisos = load_module("pisos_scraper_slug_test", "extract/08_pisos_scraper.py")
    assert pisos._slug("Gernika-Lumo") == "gernika_lumo"
    assert pisos._slug("Donostia / San Sebastián") == "donostia_san_sebastian"
    assert pisos._slug("Alegría-Dulantzi") == "alegria_dulantzi"
    assert pisos._slug("Iruña Oka/Iruña de Oca") == "iruna_oka_iruna_de_oca"
    assert pisos._slug("Urduña/Orduña") == "urduna_orduna"
    assert pisos._slug("Ribera Baja/Erriberabeitia") == "ribera_baja_erriberabeitia"
    assert pisos._slug("Karrantza Harana/Valle de Carranza") == "karrantza_harana"

    from _slugs import slug_fotocasa

    assert slug_fotocasa("Agurain/Salvatierra") == "salvatierra-agurain"
    assert slug_fotocasa("Campezo/Kanpezu") == "campezo-kampezu"
    assert (
        slug_fotocasa("Soraluze-Placencia de las Armas")
        == "soraluze-plasencia-de-las-armas"
    )


def test_cliente_no_reintenta_error_404() -> None:
    from conftest import load_module

    common = load_module("extract_common_404_test", "extract/_common.py")
    cliente = common.Cliente("test_404", reintentos=4, delay=0)
    llamadas = []

    class Response:
        status_code = 404

    cliente.session.request = lambda *args, **kwargs: llamadas.append(args) or Response()
    with pytest.raises(RuntimeError, match="no se reintenta"):
        cliente.get("https://example.invalid/not-found")
    assert len(llamadas) == 1


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
    assert all(Path(p.script).name in scripts for p in ra.PASOS)


def test_entity_resolution_funciona_desde_raw_sin_transform(tmp_path: Path) -> None:
    import pandas as pd

    from conftest import load_module

    module = load_module("entity_resolution_raw_only", "extract/entity_resolution.py")
    raw = tmp_path / "raw"
    raw.mkdir()
    pd.DataFrame(
        [
            {"ámbitos territoriales": "01001", "ámbitos territoriales__etiqueta": "Alegría-Dulantzi"},
            {"ámbitos territoriales": "20001", "ámbitos territoriales__etiqueta": "Abaltzisketa"},
            {"ámbitos territoriales": "20065", "ámbitos territoriales__etiqueta": "Soraluze-Placencia de las Armas"},
            {"ámbitos territoriales": "48001", "ámbitos territoriales__etiqueta": "Abadiño"},
            {"ámbitos territoriales": "00001", "ámbitos territoriales__etiqueta": "CAE"},
        ]
    ).to_csv(raw / "eustat_renta_municipal.csv", index=False, encoding="utf-8-sig")
    module.RAW_DIR = raw
    module.cargar_dim.cache_clear()
    module._mapa.cache_clear()

    assert module.resolver_municipio("Abadiño") == ("48001", "Abadiño")
    assert module.resolver_municipio("Soraluze / Plasencia de las Armas") == (
        "20065", "Soraluze-Placencia de las Armas"
    )
    assert not (tmp_path / "procesado").exists()


def test_anuncios_se_guardan_solo_en_json(ra) -> None:
    for paso in ra.PASOS:
        for salida in paso.salidas:
            if salida.startswith("anuncios_"):
                assert salida.endswith(".json"), (paso.id, salida)


def test_extract_no_declara_salidas_fuera_de_raw(ra) -> None:
    for paso in ra.PASOS:
        for salida in paso.salidas:
                assert not salida.startswith(("procesado/", "resultados/")), (paso.id, salida)
    for script in (ROOT / "extract").glob("*.py"):
        contenido = script.read_text(encoding="utf-8")
        assert "PROCESADO_DIR" not in contenido, script.name
        assert "RESULTADOS_DIR" not in contenido, script.name


def test_orquestador_extract_no_crea_ni_escribe_fuera_de_raw(ra, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ra, "RAW_DIR", tmp_path / "data" / "raw")
    monkeypatch.setattr(ra, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(ra, "_ejecutar", lambda paso, log: True)
    monkeypatch.setattr(ra, "PASOS", (ra.Paso("x", "x.py", ("x.csv",)),))

    assert ra.ejecutar(list(ra.PASOS)) == 0
    assert (tmp_path / "data" / "raw").is_dir()
    assert not (tmp_path / "data" / "procesado").exists()
    assert not (tmp_path / "data" / "resultados").exists()


def test_coincidencias_solo_resuelve_dentro_de_raw(ra, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ra, "RAW_DIR", tmp_path / "raw")
    (tmp_path / "raw").mkdir()
    objetivo = tmp_path / "raw" / "dim_municipios.json"
    objetivo.write_text("{}", encoding="utf-8")
    assert ra._coincidencias("dim_municipios.json") == [objetivo]
    assert ra._coincidencias("../procesado/dim_municipios.json") == []


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

    monkeypatch.setattr(ra, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(ra, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(ra, "_ejecutar", fake_ejecutar)

    codigo = ra.ejecutar(list(pasos))

    assert codigo == 1
    assert llamados == ["a", "b"]
    log = next((tmp_path / "logs").glob("extract_*.log"))
    assert "Fallidos: a" in log.read_text(encoding="utf-8")


def test_ejecutar_devuelve_cero_si_todo_va_bien(ra, tmp_path: Path, monkeypatch) -> None:
    pasos = (ra.Paso("a", "a.py", ("a.csv",)),)
    monkeypatch.setattr(ra, "RAW_DIR", tmp_path / "raw")
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
    assert "eustat" in salida and "euskadi-geo" in salida
    assert "dim-municipios" not in salida


def test_main_missing_sin_pendientes_no_ejecuta(ra, monkeypatch, capsys) -> None:
    monkeypatch.setattr(ra, "seleccionar", lambda *a, **k: [])
    monkeypatch.setattr(ra, "ejecutar", lambda pasos: pytest.fail("no debe ejecutar"))
    assert ra.main(["--missing"]) == 0
    assert "No hay nada pendiente" in capsys.readouterr().out
