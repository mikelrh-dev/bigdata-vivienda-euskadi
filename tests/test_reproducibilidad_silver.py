"""Invariante de reproducibilidad de silver.

Regla: cada fichero listado en `data/procesado/manifest_sha256.txt` tiene un
productor declarado (nodo del DAG o paso de la fase quality). Si alguien deja
un artefacto escrito a mano, este test falla antes de que el conteo de
gobernanza se convierta en una foto sin significado.

Este es el guardarrail que evita repetir el bug de los 12 ficheros: el umbral
numerico detecta el cambio, esta invariante detecta la causa.
"""

from __future__ import annotations

import fnmatch
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "ra_reproducibilidad", ROOT / "transform" / "run_all.py")
assert _spec is not None and _spec.loader is not None
ra = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ra
_spec.loader.exec_module(ra)

MANIFEST = ROOT / "data" / "procesado" / "manifest_sha256.txt"

# Artefactos de la fase quality: inventarios y sidecars que no salen de un
# nodo del DAG pero si de un paso declarado en scripts/run_pipeline.py.
QUALITY = (
    "_meta/index.json",
    "_meta/csvs_index.json",
    "_meta/nombres_normalizados_map.json",
    "_meta/*.meta.json",
    "run_manifest.json",  # subproducto del propio run_all
)

# Artefactos de la capa de analisis (gold) que se escriben junto a silver por
# herencia historica. No salen de un nodo del DAG, sino de un script de
# analysis/: se declara el productor y el test comprueba que sigue existiendo.
ANALISIS = {
    "brecha_esfuerzo_2024_2026.csv": "analysis/calcular_brecha_esfuerzo_2024_2026.py",
    "premium_oferta_2026.csv": "analysis/calibrar_premium_oferta.py",
    "comparacion_esfuerzo_2024_2026.csv": "analysis/comparar_esfuerzo_2024_2026_misma_base.py",
    "comparacion_esfuerzo_2024_2026_resumen.csv": "analysis/comparar_esfuerzo_2024_2026_misma_base.py",
    "cobertura_representatividad_2026.csv": "analysis/cobertura_representatividad_2026.py",
    "validacion_alquiler_2024_serpavi.csv": "analysis/validar_alquiler_serpavi.py",
}


def _patrones_dag() -> list[str]:
    """Patrones proc:* declarados por cualquier nodo (out y out_glob)."""
    patrones: list[str] = []
    for cfg in ra.SCRIPTS.values():
        for ref in list(cfg.get("out", [])) + list(cfg.get("out_glob", [])):
            base, _, patron = ref.partition(":")
            if base == "proc":
                patrones.append(patron)
    return patrones


def _entradas_manifest() -> list[str]:
    if not MANIFEST.exists():
        pytest.skip("sin data/procesado/manifest_sha256.txt (clon sin capa silver)")
    nombres = []
    for linea in MANIFEST.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            nombres.append(linea.split("  ", 1)[1].strip())
    return nombres


def test_manifest_silver_solo_tiene_productores_declarados():
    nombres = _entradas_manifest()
    assert nombres, "el manifest silver esta vacio"
    faltan = [p for p in ANALISIS.values() if not (ROOT / p).exists()]
    assert not faltan, f"productores de analisis declarados que no existen: {faltan}"
    patrones = _patrones_dag() + list(QUALITY) + list(ANALISIS)
    sin_productor = [n for n in nombres
                     if not any(fnmatch.fnmatch(n, p) for p in patrones)]
    assert not sin_productor, (
        "ficheros sin productor declarado en el DAG ni en quality: "
        f"{sorted(sin_productor)}"
    )


def test_no_quedan_residuos_legacy_conocidos():
    """Los 6 residuos retirados no deben reaparecer (ni a mano ni por script)."""
    proc = ROOT / "data" / "procesado"
    residuos = [
        "pob_rank.csv",
        "anuncios_pisos_dirigido.csv",
        "anuncios_pisos_dirigido.json",
        "_meta/acta_ingesta.md",
        "_meta/udalmap_empleo_corregido.json.meta.json",
        "udalmap_empleo_corregido_normalizado.json",
    ]
    presentes = [r for r in residuos if (proc / r).exists()]
    assert not presentes, f"residuos legacy presentes: {presentes}"
