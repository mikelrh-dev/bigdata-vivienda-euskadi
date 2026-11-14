"""Regresiones del sello de vintage en las figuras.

El proyecto declara en `config/comparabilidad.yaml` que hay que declarar el
vintage de cada cifra. Estos tests impiden que un generador publique una
figura sin entrada en `config/vintage_figuras.yaml` y que el sello se rompa.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis import vintage_figuras as vf  # noqa: E402

GENERADORES = (
    ROOT / "analysis" / "run_analisis_mongo.py",
    ROOT / "transform" / "generar_figuras_N.py",
    ROOT / "visuals" / "mapa_esfuerzo_mercado_2026.py",
    ROOT / "visuals" / "graficos_esfuerzo_mercado_2026.py",
    ROOT / "visuals" / "assets_presentacion_esfuerzo_mercado_2026.py",
)

PNG_RE = re.compile(r'"([A-Za-z0-9_]+\.png)"')

CODIGOS_VALIDOS = {"2024", "2026", "mixto", "flujo", "acumulado", "sin-fecha"}


def test_toda_figura_declarada_tiene_codigo_valido():
    declaradas = vf.figuras()
    assert len(declaradas) >= 45, len(declaradas)
    for nombre, entrada in declaradas.items():
        assert str(entrada.get("vintage")) in CODIGOS_VALIDOS, (nombre, entrada)
        assert entrada.get("fuentes"), f"{nombre} sin fuentes declaradas"


def test_cada_codigo_tiene_etiqueta():
    etiquetas = vf._config().get("codigos") or {}
    for codigo in CODIGOS_VALIDOS:
        assert str(etiquetas.get(codigo, "")).strip(), codigo


def test_generadores_no_publican_figuras_sin_declarar():
    """Si se anade una figura nueva, tiene que entrar en el YAML."""
    declaradas = set(vf.figuras())
    faltan: dict[str, set[str]] = {}
    for ruta in GENERADORES:
        texto = ruta.read_text(encoding="utf-8")
        nombres = set(PNG_RE.findall(texto))
        sin_declarar = {n for n in nombres if n not in declaradas}
        if sin_declarar:
            faltan[ruta.name] = sin_declarar
    assert not faltan, f"figuras sin vintage declarado: {faltan}"


def test_etiqueta_nunca_vacia():
    for nombre in list(vf.figuras())[:5] + ["no_existe.png"]:
        assert vf.etiqueta(nombre).strip()


def test_figura_sin_declarar_falla_en_codigo():
    with pytest.raises(KeyError):
        vf.codigo("figura_inventada.png")


def test_metadatos_llevan_el_vintage():
    nombre = "H1_ranking_esfuerzo_18_34.png"
    meta = vf.metadatos(nombre)
    assert meta["Vintage"] == "2024"
    assert meta["Figura"] == nombre
    assert meta["Description"] == f"Vintage: {vf.etiqueta(nombre)}"


def test_anotar_pinta_la_etiqueta():
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, _ax = plt.subplots(figsize=(3, 2))
    antes = len(fig.texts)
    vf.anotar(fig, "P_oficial_vs_anuncios_por_TH.png")
    assert len(fig.texts) == antes + 1
    texto = fig.texts[-1].get_text()
    assert "2024" in texto and "2026" in texto and "no comparable" in texto
    plt.close(fig)


def test_sincronizacion_apunta_a_figuras_declaradas():
    cfg = vf._config().get("sincronizacion") or {}
    declaradas = set(vf.figuras())
    for nombre in cfg.get("deck") or []:
        assert nombre in declaradas, nombre
    for destino, origen in (cfg.get("memoria") or {}).items():
        assert destino.endswith(".png"), destino
        assert str(origen).endswith(".png"), origen
        assert Path(str(origen)).name in declaradas, origen
