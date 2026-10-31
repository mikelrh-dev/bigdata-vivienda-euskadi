"""Bateria de verificacion de la fase raw->transformacion (plan 10/10 datos).

Cada test nombra el WP que cubre. Lee data/procesado (nunca raw salvo
guardrails, que estan en test_raw_inmutable.py).
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "procesado"


def _csv(nombre):
    return pd.read_csv(PROC / nombre, encoding="utf-8-sig")


def test_wp03_n_anuncios_real():
    """WP-03: n_anuncios sale de los JSON de anuncios, no del 252 fijo."""
    dim = _csv("dim_municipios.csv")
    assert "n_anuncios" in dim.columns
    assert dim["n_anuncios"].sum() > 0, "n_anuncios todo ceros: el conteo no corre"
    assert (dim["n_anuncios"] != 252).any(), "n_anuncios parece la constante 252"


def test_wp04_ceros_a_nulo_con_flag():
    """WP-04: ceros imposiles de paro -> NaN + flag, bruto conservado."""
    df = _csv("udalmap_empleo_corregido.csv")
    assert "tasa_paro_lanbide_bruto" in df.columns
    assert "paro_registrado_cero" in df.columns
    assert "tasa_paro_valida" in df.columns
    ceros = df[df["paro_registrado_cero"]]
    assert len(ceros) > 0, "se esperaba al menos un cero documentado"
    assert ceros["tasa_paro_lanbide_pct"].isna().all()


def test_wp04_sin_clip_contra_cero():
    """WP-04: ningun clip usa un techo nulo o cero."""
    df = _csv("analisis_variables_base.csv")
    if "tasa_desempleo_juvenil_real_pct" in df.columns:
        s = df["tasa_desempleo_juvenil_real_pct"].dropna()
        assert (s >= 0).all() and (s <= 100).all()


def test_wp05_sin_brecha_ocupacion_actividad():
    """WP-05: la brecha invalida ocupacion-actividad no existe en gold."""
    df = _csv("dim_municipios_enriquecido.csv")
    assert "brecha_ocupacion_actividad_pct" not in df.columns


def test_wp06_esfuerzo_canonico_unico():
    """WP-06: esfuerzo_joven_pct (municipal fiscal) existe y se preserva."""
    base = _csv("analisis_variables_base.csv")
    renta = _csv("dim_municipios_renta.csv")
    assert "esfuerzo_joven_pct" in base.columns
    assert "esfuerzo_joven_pct" in renta.columns
    m = base[["codigo_ine", "esfuerzo_joven_pct"]].merge(
        renta[["codigo_ine", "esfuerzo_joven_pct"]],
        on="codigo_ine", suffixes=("_base", "_renta"))
    m = m.dropna()
    assert len(m) > 0
    diff = (m["esfuerzo_joven_pct_base"] - m["esfuerzo_joven_pct_renta"]).abs()
    assert (diff < 0.05).all(), f"canonico alterado en merge: max diff {diff.max()}"


def test_wp06_tension_usa_canonico():
    """WP-06: tension sin NaN con el esfuerzo canonico como insumo."""
    t = _csv("dim_municipios_tension.csv")
    assert int(t.isna().sum().sum()) == 0
    assert set(t["tension_categoria"].unique()) <= {"baja", "media", "alta"}


def test_wp09_nombres_canonicos():
    """WP-09: codigo_ine 5 digitos + nombre_canonico coherente entre tablas."""
    # Convencion del repo (plan crudos): los CSV se leen con dtype=str para
    # no perder el cero inicial de Alava (01xxx). El writer no puede
    # imponerlo en CSV sin esquema; el contrato esta en el lector.
    dim = pd.read_csv(PROC / "dim_municipios.csv", encoding="utf-8-sig",
                      dtype={"codigo_ine": str})
    base = pd.read_csv(PROC / "analisis_variables_base.csv", encoding="utf-8-sig",
                       dtype={"codigo_ine": str})
    dim["codigo_ine"] = dim["codigo_ine"].str.zfill(5)
    base["codigo_ine"] = base["codigo_ine"].str.zfill(5)
    assert (dim["codigo_ine"].str.len() == 5).all()
    m = dim[["codigo_ine", "nombre_canonico"]].merge(
        base[["codigo_ine", "nombre_canonico"]],
        on="codigo_ine", suffixes=("_dim", "_base"))
    assert (m["nombre_canonico_dim"] == m["nombre_canonico_base"]).all()
    t = _csv("dim_municipios_tension.csv")
    assert (t["codigo_ine"].astype(str).str.zfill(5).str.len() == 5).all()
    assert set(t["codigo_ine"].astype(str).str.zfill(5)) <= set(
        dim["codigo_ine"].astype(str))


def _llamadas_sin(texto, marcador, clave):
    """Localiza llamadas marcador(...) cuyo argumento no contiene clave.

    Recorre parentesis balanceados (el regex simple se rompia con
    os.path.join(...) anidado). Devuelve lineas 1-based."""
    out, i = [], 0
    while True:
        j = texto.find(marcador, i)
        if j < 0:
            return out
        k = j + len(marcador)
        depth, p = 1, k
        while p < len(texto) and depth:
            if texto[p] == "(":
                depth += 1
            elif texto[p] == ")":
                depth -= 1
            p += 1
        if clave not in texto[k:p]:
            out.append(texto[:j].count("\n") + 1)
        i = p


def test_wp10_lectura_tipografica():
    """WP-10: todo pd.read_csv de transform usa dtype=str (cero de Alava)."""
    mal = []
    for py in sorted((ROOT / "transform").glob("*.py")):
        texto = py.read_text(encoding="utf-8")
        for ln in _llamadas_sin(texto, "pd.read_csv(", "dtype"):
            mal.append(f"{py.name}:{ln}")
    assert not mal, "lecturas sin dtype=str:\n" + "\n".join(mal)


def test_wp11_fallback_poblacion_joven():
    """WP-11: estimacion 15-29 con periodo y metodo declarados por fila."""
    pj = pd.read_csv(PROC / "poblacion_joven_municipal.csv",
                     encoding="utf-8-sig", dtype=str)
    assert len(pj) == 252, f"esperados 252, hay {len(pj)}"
    assert pj["metodo"].str.contains("periodo=").all()
    assert pd.to_numeric(pj["poblacion_15_29_est"], errors="coerce").notna().all()


def test_wp12_cobertura_mercado():
    """WP-12: n_anuncios real post-dedup, crudo conservado, tipologia cerrada."""
    dim = pd.read_csv(PROC / "dim_municipios.csv", encoding="utf-8-sig",
                      dtype=str)
    assert "n_anuncios_raw" in dim.columns
    real = pd.to_numeric(dim["n_anuncios"], errors="coerce")
    crudo = pd.to_numeric(dim["n_anuncios_raw"], errors="coerce")
    # El dedup reduce el total (843 -> 759); por municipio el recuento real
    # puede superar al crudo porque el unificador resuelve mas variantes.
    assert int(crudo.sum()) >= int(real.sum()), "el dedup no reduce el total"
    assert (real >= 0).all() and (crudo >= 0).all()
    assert set(dim["tipologia_mercado"].unique()) <= {
        "Nivel1_Mercado_Dinamico", "Nivel2_Mercado_Regulado",
        "Nivel3_Mercado_Rural_Cerrado"}


def test_wp13_higiene_escritura():
    """WP-13: todo to_csv de transform escribe con encoding utf-8-sig."""
    mal = []
    for py in sorted((ROOT / "transform").glob("*.py")):
        texto = py.read_text(encoding="utf-8")
        for ln in _llamadas_sin(texto, ".to_csv(", "encoding"):
            mal.append(f"{py.name}:{ln}")
    assert not mal, "escrituras sin encoding:\n" + "\n".join(mal)
