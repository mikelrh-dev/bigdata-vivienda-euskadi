"""Contrato de la capa 2026: estructura, conciliacion y coherencia de flags.

No comprueba cifras concretas (cambiarian con cada regeneracion): comprueba que
el CSV es internamente consistente y que la exclusion de anuncios queda declarada.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "transform"))

from _anuncios_2026 import cargar_anuncios_2026  # noqa: E402

PROC = ROOT / "data" / "procesado"
CSV = PROC / "esfuerzo_mercado_2026.csv"
CSV_TIPO = PROC / "esfuerzo_mercado_2026_por_tipo.csv"
CSV_BRECHA = PROC / "brecha_esfuerzo_2024_2026.csv"
RES = ROOT / "data" / "resultados"
CSV_PREMIUM = RES / "premium_oferta_2026.csv"
CSV_COMP = RES / "comparacion_esfuerzo_2024_2026.csv"
CSV_COB = RES / "cobertura_representatividad_2026.csv"

LEGACY = {
    "codigo_ine", "nombre_canonico", "territorio", "n_anuncios_2026",
    "precio_mediana_anuncio_2026_eur_mes", "esfuerzo_mercado_2026_pct_18_34",
    "esfuerzo_mercado_2026_pct_16_29", "flag_ipc", "flag_no_comparable",
    "vintage_numerador", "vintage_denominador",
}


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    if not CSV.exists():
        pytest.skip("falta esfuerzo_mercado_2026.csv")
    d = pd.read_csv(CSV, dtype=str, encoding="utf-8-sig")
    for c in ("n_anuncios_2026", "n_brutos_2026", "n_excluidos_2026",
              "esfuerzo_mercado_2026_pct_18_34", "ic95_lo_pct_18_34",
              "ic95_hi_pct_18_34", "ic95_amplitud_pct_18_34",
              "esfuerzo_banda_lo_pct_18_34", "esfuerzo_banda_hi_pct_18_34"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d


def test_estructura_y_columnas_legacy(df: pd.DataFrame) -> None:
    assert len(df) == 252
    assert df["codigo_ine"].is_unique
    assert LEGACY <= set(df.columns)
    assert (df["vintage_numerador"] == "2026").all()
    assert (df["vintage_denominador"] == "2024").all()


def test_conciliacion_con_la_fuente(df: pd.DataFrame) -> None:
    """Los contadores del CSV cuadran con la regla unica de filtrado."""
    _, meta = cargar_anuncios_2026()
    assert int(df["n_anuncios_2026"].sum()) == meta["n_usados"]
    assert int(df["n_excluidos_2026"].sum()) == meta["n_excluidos_calidad"]


def test_ningun_municipio_con_anuncio_invalido(df: pd.DataFrame) -> None:
    """Un municipio sin anuncios validos no puede tener esfuerzo."""
    sin_dato = df[df["n_anuncios_2026"] == 0]
    assert sin_dato["esfuerzo_mercado_2026_pct_18_34"].isna().all()
    con_dato = df[df["n_anuncios_2026"] > 0]
    assert con_dato["esfuerzo_mercado_2026_pct_18_34"].notna().all()


def test_intervalos_ordenados(df: pd.DataFrame) -> None:
    con_ic = df.dropna(subset=["ic95_lo_pct_18_34", "ic95_hi_pct_18_34",
                               "esfuerzo_mercado_2026_pct_18_34"])
    assert len(con_ic) > 0
    assert (con_ic["ic95_lo_pct_18_34"] <= con_ic["esfuerzo_mercado_2026_pct_18_34"]).all()
    assert (con_ic["esfuerzo_mercado_2026_pct_18_34"] <= con_ic["ic95_hi_pct_18_34"]).all()


def test_flags_coherentes(df: pd.DataFrame) -> None:
    d = df[df["flag_n_insuficiente"].astype(str).str.lower() == "true"]
    assert (d["n_anuncios_2026"] < 5).all()
    c = df[df["flag_concluyente"].astype(str).str.lower() == "true"]
    assert (c["n_anuncios_2026"] >= 10).all()
    assert (c["ic95_amplitud_pct_18_34"] < 30).all()


def test_banda_de_escenarios(df: pd.DataFrame) -> None:
    d = df.dropna(subset=["esfuerzo_banda_lo_pct_18_34", "esfuerzo_banda_hi_pct_18_34",
                          "esfuerzo_mercado_2026_pct_18_34"])
    assert (d["esfuerzo_banda_lo_pct_18_34"] <= d["esfuerzo_mercado_2026_pct_18_34"]).all()
    assert (d["esfuerzo_mercado_2026_pct_18_34"] <= d["esfuerzo_banda_hi_pct_18_34"]).all()


def test_por_tipo_no_mezcla_excluidos() -> None:
    if not CSV_TIPO.exists():
        pytest.skip("falta esfuerzo_mercado_2026_por_tipo.csv")
    d = pd.read_csv(CSV_TIPO, dtype=str, encoding="utf-8-sig")
    _, meta = cargar_anuncios_2026()
    n = pd.to_numeric(d["n_anuncios"], errors="coerce")
    # Puede quedar por debajo del total si algun anuncio no tiene habitaciones.
    assert 0 < int(n.sum()) <= meta["n_usados"]
    assert {"ic95_lo_pct_18_34", "flag_n_insuficiente"} <= set(d.columns)


def test_calibracion_y_comparacion() -> None:
    if not CSV_PREMIUM.exists() or not CSV_COMP.exists():
        pytest.skip("faltan premium o comparacion")
    prem = pd.read_csv(CSV_PREMIUM, dtype=str, encoding="utf-8-sig")
    assert {"k_aplicado", "origen_k"} <= set(prem.columns)
    assert set(prem["origen_k"].dropna()) <= {"municipal", "area_loo", "no_aplicable"}
    comp = pd.read_csv(CSV_COMP, dtype=str, encoding="utf-8-sig")
    assert {"esfuerzo_2024_base_salario_pct_18_34",
            "esfuerzo_2026_base_salario_pct_18_34"} <= set(comp.columns)
    # La misma base exige la misma muestra en ambos lados.
    assert comp["esfuerzo_2024_base_salario_pct_18_34"].notna().sum() == len(comp)
    assert comp["esfuerzo_2026_base_salario_pct_18_34"].notna().sum() == len(comp)


def test_brecha_declara_que_no_es_variacion_temporal() -> None:
    if not CSV_BRECHA.exists():
        pytest.skip("falta brecha_esfuerzo_2024_2026.csv")
    d = pd.read_csv(CSV_BRECHA, dtype=str, encoding="utf-8-sig")
    assert {"brecha_pp_18_34", "tipo_diferencia", "caveat"} <= set(d.columns)
    assert (d["tipo_diferencia"] == "nivel_oferta_vs_registrado").all()
    assert d["caveat"].str.contains("no es una variacion temporal").all()


def test_cobertura_en_poblacion_no_solo_municipios() -> None:
    if not CSV_COB.exists():
        pytest.skip("falta cobertura_representatividad_2026.csv")
    d = pd.read_csv(CSV_COB, dtype=str, encoding="utf-8-sig")
    valor = pd.to_numeric(
        d.loc[d["metrica"] == "pct_poblacion_18_34_cubierta", "valor"], errors="coerce")
    assert len(valor) == 1 and 0 < float(valor.iloc[0]) <= 100
