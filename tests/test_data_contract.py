"""Invariantes del pipeline entre capas y formatos."""

from __future__ import annotations

import re

from conftest import ROOT, load_module

CODIGO_DIRS = ("extract", "transform", "analysis")


def _pasos_extract():
    return load_module("contrato_extract", "extract/run_all.py").PASOS


def _pasos_transform():
    return load_module("contrato_transform", "transform/run_all.py").PASOS


def test_raw_tiene_un_solo_formato_por_tabla() -> None:
    for paso in _pasos_extract():
        formatos: dict[str, set[str]] = {}
        for salida in paso.salidas:
            if salida.startswith("procesado/"):
                continue
            if "." not in salida:
                continue
            base, extension = salida.rsplit(".", 1)
            if extension in {"csv", "json"}:
                formatos.setdefault(base, set()).add(extension)
        dobles = {base: exts for base, exts in formatos.items() if len(exts) > 1}
        assert dobles == {}, (paso.id, dobles)


def test_los_anuncios_crudos_son_json() -> None:
    for paso in _pasos_extract():
        for salida in paso.salidas:
            if salida.startswith("anuncios_"):
                assert salida.endswith(".json"), (paso.id, salida)


def test_extract_escribe_solo_en_raw_y_el_catalogo() -> None:
    for paso in _pasos_extract():
        for salida in paso.salidas:
            assert not salida.startswith(("/", "..")), (paso.id, salida)
            assert "/resultados/" not in salida, (paso.id, salida)


def test_transform_escribe_solo_en_procesado() -> None:
    for paso in _pasos_transform():
        for salida in paso.salidas:
            assert "/" not in salida and "\\" not in salida, (paso.id, salida)


def test_solo_paths_lee_data_dir_del_entorno() -> None:
    patron = re.compile(r"getenv\(\s*[\"']DATA_DIR[\"']|environ\[[\"']DATA_DIR[\"']\]")
    infractores = []
    for carpeta in CODIGO_DIRS:
        for ruta in sorted((ROOT / carpeta).glob("*.py")):
            if patron.search(ruta.read_text(encoding="utf-8", errors="ignore")):
                infractores.append(str(ruta.relative_to(ROOT)))
    assert infractores == []


def test_ningun_script_compone_rutas_data_antiguas() -> None:
    prohibidos = [
        re.compile(r"os\.path\.join\(\s*[\"']data[\"']"),
        re.compile(r"Path\(\s*[\"']data[\"']"),
        re.compile(r"[\"']data[\"']\s*/\s*[\"'](?:raw|procesado|resultados)[\"']"),
    ]
    infractores = []
    for carpeta in CODIGO_DIRS:
        for ruta in sorted((ROOT / carpeta).glob("*.py")):
            texto = ruta.read_text(encoding="utf-8", errors="ignore")
            if any(patron.search(texto) for patron in prohibidos):
                infractores.append(str(ruta.relative_to(ROOT)))
    assert infractores == []
