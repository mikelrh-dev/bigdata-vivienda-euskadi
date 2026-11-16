"""Bloqueos fase crudos: padding, temporal/larga, renta transparente.

Los recuentos que antes vivían en el script manual `verificacion_crudos.py` se
portaron aquí el 2026-11-16, cuando el script se archivó: así se comprueban en
cada `pytest` en vez de depender de acordarse de ejecutarlo.
"""
from pathlib import Path
import pandas as pd
import pytest
RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

def _leer(n):
    """Lee un crudo; si no esta en el clon, skip (los crudos no se versionan)."""
    p = RAW / n
    if not p.exists():
        pytest.skip(f"data/raw/{n} no esta en este clon: crudos no versionados")
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig", low_memory=False)

def test_codigo_ine_5_digitos():
    for f in ["dim_municipios.csv","alquiler_municipal.csv","anuncios_fotocasa.csv",
              "anuncios_pisos.csv","anuncios_realtyapi.csv","renta_municipal_completa.csv",
              "udalmap_empleo_corregido.csv","emal_fianzas_ampliado.csv"]:
        p = RAW/f
        if not p.exists():
            continue
        df = _leer(f)
        if "codigo_ine" not in df.columns:
            continue
        c = df["codigo_ine"].dropna().astype(str).str.strip().str.zfill(5)
        assert (c.str.len()==5).all(), f"{f} len!=5"
        assert c.str[:2].isin(["01","20","48"]).all(), f"{f} prefijo malo"

def test_temporal_larga_no_mezclados():
    larga = _leer("anuncios_fotocasa_larga.csv")
    temp = _leer("anuncios_fotocasa_temporal.csv")
    assert len(larga)==167 and len(temp)==304
    assert not set(larga["id_anuncio"]).intersection(set(temp["id_anuncio"]))

def test_renta_origen_transparente():
    rc = _leer("renta_municipal_completa.csv")
    assert len(rc)==252
    assert set(rc["renta_origen"].unique())=={"Eustat+INE_Atlas"}


def test_dim_252_municipios():
    assert len(_leer("dim_municipios.csv")) == 252


def test_alquiler_159_municipios():
    """Eustat publica alquiler de 159 municipios; el resto no tiene serie."""
    assert _leer("alquiler_municipal.csv")["municipio"].nunique() == 159


def test_emal_73_municipios_con_muestra():
    em = _leer("emal_fianzas_ampliado.csv")
    assert em["codigo_ine"].nunique() == 73
    assert {"n_muestral", "tipo_fuente"} <= set(em.columns)


def test_pisos_columnas_de_ambito():
    """Sin estas dos columnas no se puede separar municipio verificado de area."""
    pi = _leer("anuncios_pisos_busqueda.csv")
    assert {"ambito_busqueda", "es_municipio_verificado"} <= set(pi.columns)


def test_realtyapi_tres_capitales():
    """RealtyAPI es el techo sin creditos: solo las tres capitales."""
    assert _leer("anuncios_realtyapi.csv")["municipio"].nunique() == 3


@pytest.mark.parametrize("fichero,filas", [
    ("transporte_paradas_municipio.csv", 252),
    ("osrm_tiempos_capitales.csv", 252),
    ("distancias_haversine_252.csv", 252 * 252),
])
def test_recuentos_de_matrices(fichero, filas):
    """252 es el universo; 63.504 son los pares ordenados de 252 municipios."""
    assert len(_leer(fichero)) == filas
