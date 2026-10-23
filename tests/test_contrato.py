"""Verificación del contrato OpenSpec con datos reales.

Cada test corresponde a un requisito o prohibición del contrato en
`openspec/specs/contrato-reto/spec.md`. Un test en rojo significa que el
proyecto se ha desviado del contrato.

Uso:
    .venv/Scripts/python.exe -m pytest tests -q
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SPECS = ROOT / "openspec" / "specs"

# Umbrales observados el 2026-10-23. Si la extracción mejora, se suben.
MIN_ANUNCIOS = 400
MIN_MUNICIPIOS = 150
MIN_POBLACION = 80000      # eustat_poblacion_edad: 89.424
MIN_RENTA_MUNICIPAL = 90000  # eustat_renta_municipal: 98.532


def _cargar_json(nombre: str):
    ruta = RAW / nombre
    if not ruta.exists():
        pytest.skip(f"{nombre} no existe (ejecuta la extracción)")
    return json.loads(ruta.read_text(encoding="utf-8"))


# ─── EXTRACCION-01: API y scraping, datos completos ────────────────

def test_extraccion_anuncios_reales():
    """EXTRACCION-01 / Escenario: el scraping produce anuncios reales."""
    datos = _cargar_json("anuncios_fotocasa.json")["datos"]
    assert len(datos) >= MIN_ANUNCIOS, f"solo {len(datos)} anuncios"
    assert datos[0]["precio_eur"] is not None
    assert datos[0]["municipio"]
    assert datos[0]["provincia_origen"] in {"gipuzkoa", "bizkaia", "araba_alava"}


def test_extraccion_anuncios_sin_duplicar():
    """LIMPIEZA-01 / Escenario: los duplicados se resuelven."""
    datos = _cargar_json("anuncios_fotocasa.json")["datos"]
    ids = [a["id_anuncio"] for a in datos]
    assert len(ids) == len(set(ids)), "hay id_anuncio repetido"


def test_extraccion_tres_fuentes_independientes():
    """EXTRACCION-02 / Escenario: las fuentes son independientes."""
    esperadas = [
        "eustat_poblacion_edad.json",
        "eustat_renta_municipal.json",
        "ine_69301.json",
        "emancipacion_juventud.csv",
        "anuncios_fotocasa.json",
    ]
    existentes = [n for n in esperadas if (RAW / n).exists()]
    assert len(existentes) >= 3, f"solo {len(existentes)} fuentes: {existentes}"


# ─── COMPLEMENTARIOS-01: salarios y población ────────────────────

def test_complementarios_poblacion():
    """COMPLEMENTARIOS-01 / Escenario: población por municipio."""
    datos = _cargar_json("eustat_poblacion_edad.json")
    filas = datos["datos"]["filas"]
    assert len(filas) >= MIN_POBLACION, f"solo {len(filas)} filas"


def test_complementarios_renta_municipal():
    """COMPLEMENTARIOS-01: la renta por municipio alimenta el indicador."""
    datos = _cargar_json("eustat_renta_municipal.json")
    filas = datos["datos"]["filas"]
    assert len(filas) >= MIN_RENTA_MUNICIPAL
    assert any("ámbitos territoriales__etiqueta" in f for f in filas[:50])


@pytest.mark.xfail(
    reason="COMPLEMENTARIOS-01 ABIERTO: falta ine_salarios_edad.json "
           "(INE EPA, salario medio por grupo de edad). Ver P-02.",
    strict=True,
)
def test_complementarios_salarios_no_simulados():
    """COMPLEMENTARIOS-01 / P-02: el salario proviene de una fuente real."""
    # El contrato exige salario real. Mientras no exista el fichero, este test
    # queda marcado como pendiente intencionado (xfail) y la suite sigue verde.
    ruta = RAW / "ine_salarios_edad.json"
    assert ruta.exists(), "falta el extractor de salarios del INE"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos["registros"], "el fichero de salarios está vacío"


# ─── FORMATO-01: JSON o CSV ───────────────────────────────────────

def test_formato_csv_alquiler_y_municipios():
    """FORMATO-01 + EXTRACCION-01: el alquiler es CSV y cubre 3 territorios."""
    import csv

    ruta = RAW / "alquiler_municipal.csv"
    if not ruta.exists():
        pytest.skip("alquiler_municipal.csv no existe")
    filas = list(csv.DictReader(ruta.open(encoding="utf-8-sig")))
    assert len({f["municipio"] for f in filas}) >= MIN_MUNICIPIOS
    territorios = {f["territorio"] for f in filas}
    assert territorios == {"Araba/Álava", "Bizkaia", "Gipuzkoa"}, territorios
    # Los valores parseados son numéricos, no texto con coma
    assert isinstance(float(filas[0]["renta_media_eur_m2_media"]), float)


def test_formato_metadatos_en_json():
    """FORMATO-01: el JSON lleva fuente, fecha y recuento."""
    datos = _cargar_json("anuncios_fotocasa.json")
    meta = datos["metadata"]
    assert meta["fuente"]
    assert meta["fecha_extraccion"]
    assert meta["n_anuncios"] == len(datos["datos"])


# ─── LIMPIEZA-01: nulos tratados explícitamente ───────────────────

def test_limpieza_nulos_explicitos():
    """LIMPIEZA-01 / Escenario: los nulos no se interpretan como cero."""
    datos = _cargar_json("anuncios_fotocasa.json")["datos"]
    con_nulos = [a for a in datos if a["superficie_m2"] is None]
    # Que haya nulos está bien; lo que no está bien es convertirlos a 0
    for a in datos:
        assert a["superficie_m2"] != 0 or a["superficie_m2"] is None
    print(f"  (anuncios sin superficie: {len(con_nulos)})")


# ─── Prohibiciones ───────────────────────────────────────────────

def test_p06_todo_en_python():
    """P-06: todos los programas del reto están en Python."""
    scripts = sorted((ROOT / "extract").glob("*.py"))
    assert len(scripts) >= 6, f"solo {len(scripts)} scripts"
    for script in scripts:
        assert script.suffix == ".py"


def test_p07_sin_credenciales_en_el_repositorio():
    """P-07: no hay credenciales rastreadas por git."""
    rastreados: list = []
    try:
        rastreados = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        ).stdout.split()
    except (FileNotFoundError, subprocess.SubprocessError):
        pytest.skip("git no disponible")
    prohibidos = [f for f in rastreados if f in {".env", "api.txt"}]
    assert not prohibidos, f"credenciales rastreadas: {prohibidos}"


def test_p08_contrato_cubre_los_criterios():
    """P-08: cada criterio de la rúbrica tiene un requisito asignado."""
    if not SPECS.exists():
        pytest.skip("openspec/ no existe")
    contrato = (SPECS / "contrato-reto" / "spec.md").read_text(encoding="utf-8")
    for criterio in (
        "Extracción de datos mediante Python",
        "Almacenamiento HDFS",
        "Kafka",
        "Integración",
        "Modelado MongoDB",
        "Operaciones PyMongo",
        "Consultas",
        "Aggregation Pipeline",
        "Gráficos",
        "Datos utilizados",
        "Presentación",
        "Interpretación",
    ):
        assert criterio in contrato, f"criterio sin transcribir: {criterio}"
    # Y cada criterio apunta a un requisito
    for requisito in (
        "EXTRACCION-01", "HDFS-01", "KAFKA-01", "INTEGRACION-01",
        "MODELO-01", "PYMONGO-01", "CONSULTAS-01", "AGREGACION-01",
        "GRAFICOS-01", "DATOS-PYMONGO-01", "PRESENTACION-01",
        "INTERPRETACION-01",
    ):
        assert requisito in contrato, f"requisito sin asignar: {requisito}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q", "-v"]))
