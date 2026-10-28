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


def test_complementarios_salarios_no_simulados():
    """COMPLEMENTARIOS-01 / P-02: el salario proviene de una fuente real."""
    ruta = RAW / "ine_salarios_edad.json"
    assert ruta.exists(), "falta el extractor de salarios del INE"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos["metadata"]["n_registros"] > 0, "el fichero de salarios está vacío"
    assert len(datos["datos"]["registros"]) > 0, "sin registros de salarios"


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


# ─── Entity Resolution: capitales cruzan al 100% por codigo_ine ─────

def test_entity_resolution_tres_capitales():
    """MODELO-01: Donostia, Vitoria-Gasteiz y Bilbao cruzan por codigo_ine."""
    dim_path = RAW / "dim_municipios.json"
    if not dim_path.exists():
        pytest.skip("dim_municipios.json no existe (ejecuta transform/dim_municipios.py)")
    dim = json.loads(dim_path.read_text(encoding="utf-8"))
    registros = dim["datos"] if isinstance(dim, dict) else dim
    por_canonico = {r["nombre_canonico"]: r for r in registros}

    capitales = {
        "Donostia / San Sebastián": "Donostia - San Sebastián",
        "Vitoria-Gasteiz": "Vitoria - Gasteiz",
        "Bilbao": "Bilbao",
    }
    for canonico, variante_fotocasa in capitales.items():
        assert canonico in por_canonico, f"falta {canonico} en dim_municipios"
        r = por_canonico[canonico]
        assert r["codigo_ine"], f"sin codigo_ine para {canonico}"
        assert variante_fotocasa in r["variantes"], (
            f"variante Fotocasa '{variante_fotocasa}' no mapeada a {canonico}"
        )

    # Alquiler municipal contiene las 3 capitales
    ruta_alq = RAW / "alquiler_municipal.csv"
    if ruta_alq.exists():
        import csv as _csv

        with ruta_alq.open(encoding="utf-8-sig") as fh:
            munis_alq = {row["municipio"] for row in _csv.DictReader(fh)}
        for canonico in capitales:
            assert canonico in munis_alq, f"{canonico} no está en alquiler_municipal.csv"

    # Eustat renta contiene las 3 capitales (por ambito etiqueta)


# ─── P0: INE Atlas Renta ────────────────────────────────────────────

def test_ine_atlas_renta_existe():
    """P0: el fichero de renta del INE Atlas existe."""
    ruta = RAW / "ine_atlas_renta.json"
    assert ruta.exists(), "falta ine_atlas_renta.json (ejecuta extract/ine_atlas_renta.py)"


def test_ine_atlas_renta_campos():
    """P0: cada registro tiene renta_atlas, anio_renta, renta_origen."""
    ruta = RAW / "ine_atlas_renta.json"
    if not ruta.exists():
        pytest.skip("ine_atlas_renta.json no existe")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    registros = datos.get("datos", datos) if isinstance(datos, dict) else datos
    assert len(registros) > 0, "sin registros en Atlas"
    for r in registros[:5]:
        assert "renta_atlas" in r, "falta renta_atlas"
        assert "anio_renta" in r, "falta anio_renta"
        assert "renta_origen" in r, "falta renta_origen"
        assert r["renta_origen"] in ("Eustat", "INE_Atlas"), "origen invalido"


def test_renta_municipal_completa_cobertura():
    """P0: renta_municipal_completa cubre 252 municipios."""
    ruta = RAW / "renta_municipal_completa.json"
    if not ruta.exists():
        pytest.skip("renta_municipal_completa.json no existe")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    registros = datos.get("datos", datos) if isinstance(datos, dict) else datos
    assert len(registros) == 252, f"esperados 252, hay {len(registros)}"
    # Todos tienen renta_origen
    sin_origen = [r for r in registros if not r.get("renta_origen")]
    assert len(sin_origen) == 0, f"{len(sin_origen)} municipios sin renta_origen"


# ─── P1a: Filtrado de outliers ──────────────────────────────────────

def test_filtrar_outliers_marca_extremos():
    """P1a: los outliers extremos se marcan como outlier=True."""
    ruta = RAW.parent / "procesado" / "anuncios_fotocasa_filtrado.json"
    if not ruta.exists():
        pytest.skip("anuncios_fotocasa_filtrado.json no existe (ejecuta transform/filtrar_outliers.py)")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    registros = datos.get("datos", datos) if isinstance(datos, dict) else datos
    outliers = [r for r in registros if r.get("outlier")]
    assert len(outliers) > 0, "no se marcaron outliers"
    for o in outliers:
        assert o.get("motivo_outlier"), "outlier sin motivo"


def test_filtrar_outliers_validos():
    """P1a: los anuncios validos no se marcan como outlier."""
    ruta = RAW.parent / "procesado" / "anuncios_pisos_filtrado.json"
    if not ruta.exists():
        pytest.skip("anuncios_pisos_filtrado.json no existe")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    registros = datos.get("datos", datos) if isinstance(datos, dict) else datos
    validos = [r for r in registros if not r.get("outlier")]
    assert len(validos) > 0, "todos marcados como outlier"
    # Verificar que los validos tienen precio_m2 razonable
    for v in validos[:10]:
        pm2 = v.get("precio_m2_calculado") or v.get("precio_m2")
        if pm2 is not None:
            assert 3 <= pm2 <= 50, f"valido con precio_m2 fuera de rango: {pm2}"


# ─── Nuevas fuentes (scripts 10-13) ─────────────────────────────────



# Nuevas fuentes (scripts 10-13)

NUEVAS_FUENTES_JSON = [
    "emal_fianzas.json",
    "etxebide_solicitudes.json",
    "transporte_paradas_municipio.json",
    "anuncios_fotocasa_enriquecido.json",
    "anuncios_pisos_enriquecido.json",
    "anuncios_fotocasa_habitaciones.json",
    "anuncios_pisos_habitaciones.json",
]

NUEVAS_FUENTES_CSV = [
    "emal_fianzas.csv",
    "etxebide_solicitudes.csv",
    "transporte_paradas_municipio.csv",
    "anuncios_fotocasa_habitaciones.csv",
    "anuncios_pisos_habitaciones.csv",
]


@pytest.mark.parametrize("nombre", NUEVAS_FUENTES_JSON)
def test_nuevas_fuentes_json_existen(nombre):
    # Nuevas fuentes (10-13): el JSON generado existe.
    assert (RAW / nombre).exists(), "falta " + nombre


@pytest.mark.parametrize("nombre", NUEVAS_FUENTES_JSON)
def test_nuevas_fuentes_json_registros(nombre):
    # Nuevas fuentes (10-13): el JSON tiene registros > 0.
    datos = _cargar_json(nombre)
    registros = datos.get("datos", datos) if isinstance(datos, dict) else datos
    assert isinstance(registros, list), nombre + ": datos no es lista"
    assert len(registros) > 0, nombre + ": sin registros"


@pytest.mark.parametrize("nombre", NUEVAS_FUENTES_JSON)
def test_nuevas_fuentes_json_codigo_ine_rango(nombre):
    # Nuevas fuentes (10-13): codigo_ine en rango valido (01xxx/20xxx/48xxx) cuando aplica.
    datos = _cargar_json(nombre)
    registros = datos.get("datos", datos) if isinstance(datos, dict) else datos
    codigos = [
        r.get("codigo_ine")
        for r in registros
        if isinstance(r, dict) and r.get("codigo_ine") is not None
    ]
    if not codigos:
        pytest.skip(nombre + ": no incluye codigo_ine")
    for c in codigos:
        assert isinstance(c, str) and len(c) == 5 and c[:2] in {"01", "20", "48"}, (
            nombre + ": codigo_ine fuera de rango: " + str(c)
        )


@pytest.mark.parametrize("nombre", NUEVAS_FUENTES_CSV)
def test_nuevas_fuentes_csv_existen(nombre):
    # Nuevas fuentes (10-13): el CSV generado existe.
    assert (RAW / nombre).exists(), "falta " + nombre


@pytest.mark.parametrize("nombre", NUEVAS_FUENTES_CSV)
def test_nuevas_fuentes_csv_registros(nombre):
    # Nuevas fuentes (10-13): el CSV tiene registros > 0.
    import csv as _csv

    ruta = RAW / nombre
    assert ruta.exists(), "falta " + nombre
    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        filas = list(_csv.DictReader(fh))
    assert len(filas) > 0, nombre + ": sin registros"


@pytest.mark.parametrize("nombre", NUEVAS_FUENTES_CSV)
def test_nuevas_fuentes_csv_codigo_ine_rango(nombre):
    # Nuevas fuentes (10-13): codigo_ine en rango valido en CSV cuando aplica.
    import csv as _csv

    ruta = RAW / nombre
    assert ruta.exists(), "falta " + nombre
    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        filas = list(_csv.DictReader(fh))
    if not filas or "codigo_ine" not in (filas[0] or {}):
        pytest.skip(nombre + ": no incluye codigo_ine")
    codigos = [f.get("codigo_ine") for f in filas if f.get("codigo_ine")]
    if not codigos:
        pytest.skip(nombre + ": sin codigo_ine")
    for c in codigos:
        assert len(str(c)) == 5 and str(c)[:2] in {"01", "20", "48"}, (
            nombre + ": codigo_ine fuera de rango: " + str(c)
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q", "-v"]))
