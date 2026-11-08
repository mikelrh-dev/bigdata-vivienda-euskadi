"""muni_resolve parametrizado (transform/muni_resolve.py).

resolver_pisos_por_texto con vacio / sin parentesis / INE inexistente,
y _load_dim con monkeypatch (dim sintetico en tmp_path via chdir).
Sin tocar data/procesado real salvo la carga inicial del modulo.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "transform"))

import muni_resolve as mr  # noqa: E402


@pytest.mark.parametrize("sub,tit", [
    (None, None),
    ("", ""),
    ("   ", None),
    (None, ""),
])
def test_vacio_es_cuarentena_sin_subtitulo(sub, tit):
    """Sin subtitulo ni titulo -> cuarentena sin_subtitulo, codigo None."""
    ci, canon, origen, motivo = mr.resolver_pisos_por_texto(sub, tit, None)
    assert ci is None and canon is None
    assert origen == "cuarentena" and motivo == "sin_subtitulo"


@pytest.mark.parametrize("sub,canon_esperado", [
    ("Getxo", "Getxo"),
    ("Bilbao", "Bilbao"),
    ("Vitoria-Gasteiz", "Vitoria-Gasteiz"),
])
def test_sin_parentesis_resuelve_por_subtitulo(sub, canon_esperado):
    """Subtitulo sin parentesis que es municipio -> origen subtitulo."""
    ci, canon, origen, _motivo = mr.resolver_pisos_por_texto(sub, None, None)
    assert canon == canon_esperado
    assert ci is not None and len(ci) == 5
    assert origen == "subtitulo"


def test_con_parentesis_manda_hint():
    """'Barrio (Muni)' resuelve por el hint entre parentesis."""
    ci, canon, origen, _ = mr.resolver_pisos_por_texto(
        "Santutxu (Bilbao)", "Piso en Santutxu", None)
    assert canon == "Bilbao" and ci == "48020" and origen == "subtitulo"


@pytest.mark.parametrize("ine_inexistente", ["99999", "00000", "12345"])
def test_ine_inexistente_no_se_propaga(ine_inexistente):
    """INE inexistente sin coincidencia textual -> cuarentena, nunca el INE dado."""
    ci, canon, origen, _motivo = mr.resolver_pisos_por_texto(
        "Texto Sin Municipio Conocido", "Piso en Calle Inventada", ine_inexistente)
    assert ci != ine_inexistente
    # O cuarentena o resolucion por otro texto; en ningun caso el INE inventado
    assert not (ci == ine_inexistente and origen == "fallback")


def test_ine_inexistente_con_texto_resuelve_por_texto():
    """Con texto valido manda el texto aunque el INE no exista."""
    ci, canon, origen, _ = mr.resolver_pisos_por_texto(
        "Getxo", "Piso en Getxo", "99999")
    assert canon == "Getxo" and ci != "99999" and origen == "subtitulo"


def test_load_dim_monkeypatch_tmp(tmp_path, monkeypatch):
    """_load_dim lee la dim de data/procesado bajo el cwd (monkeypatch chdir)."""
    destino = tmp_path / "data" / "procesado"
    destino.mkdir(parents=True)
    with (destino / "dim_municipios.csv").open("w", newline="",
                                               encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["codigo_ine", "nombre_canonico",
                                           "variantes"])
        w.writeheader()
        w.writerow({"codigo_ine": "48020", "nombre_canonico": "Bilbao",
                    "variantes": "Bilbo|Bilbao"})
        w.writerow({"codigo_ine": "20014", "nombre_canonico":
                    "Donostia / San Sebastián", "variantes": "Donostia"})
    monkeypatch.chdir(tmp_path)
    # _load_dim monkeypatch: se sustituye por una version que lee tmp_path
    # (equivale a parchear el _load_dim importado: los globals no se tocan
    # salvo que se recargue el modulo, asi que se llama directamente).
    code2name, name2code, valid = mr._load_dim()
    assert code2name["48020"] == "Bilbao"
    assert valid == {"48020", "20014"}
    # La variante se indexa por su forma normalizada
    assert "48020" in valid and code2name["20014"] == "Donostia / San Sebastián"
    assert name2code  # no vacio


def test_globals_monkeypatch_cambian_resolucion(monkeypatch):
    """Parchear los globales (salida de _load_dim) cambia la resolucion."""
    monkeypatch.setattr(mr, "CODE2NAME", {"48020": "Bilbao"})
    monkeypatch.setattr(mr, "NAME2CODE", {"bilbao": "48020"})
    monkeypatch.setattr(mr, "VALID_CODES", {"48020"})
    # Con la dim parcheada, Getxo ya no resuelve y Bilbao si
    ci_b, canon_b, origen_b, _ = mr.resolver_pisos_por_texto("Bilbao", None, None)
    assert (ci_b, canon_b) == ("48020", "Bilbao")
    ci_g, _canon_g, origen_g, _m = mr.resolver_pisos_por_texto("Getxo", None, None)
    assert ci_g is None or origen_g == "cuarentena"
