"""Bloqueos fase crudos: padding, temporal/larga, renta transparente."""
from pathlib import Path
import pandas as pd
RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

def _leer(n):
    return pd.read_csv(RAW/n, dtype=str, encoding="utf-8-sig", low_memory=False)

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
