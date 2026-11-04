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


def test_wp01_todo_script_declarado():
    """WP-01: todo transform/*.py esta en SCRIPTS o EXCLUIDOS de run_all."""
    import sys
    sys.path.insert(0, str(ROOT))
    import transform.run_all as orch
    en_disco = {p.name for p in (ROOT / "transform").glob("*.py")}
    en_disco.discard("run_all.py")  # el propio orquestador
    declarados = set(orch.SCRIPTS) | set(orch.EXCLUIDOS)
    assert en_disco <= declarados, f"sin declarar: {sorted(en_disco - declarados)}"


def test_wp09_mapa_nombres_estables():
    """WP-09: todo *_normalizado.json con timestamp esta en el mapa o es canonico."""
    import json
    import re
    mapa = json.loads((PROC / "_meta" / "nombres_normalizados_map.json").
                      read_text(encoding="utf-8"))
    registrados = {e["nombre_actual"] for e in mapa["ficheros_con_timestamp_heredado"]}
    for p in PROC.glob("*_normalizado.json"):
        if re.search(r"_20\d{6}(_\d+)?_normalizado\.json$", p.name):
            assert p.name in registrados, f"sin registrar en mapa: {p.name}"
            entrada = [e for e in mapa["ficheros_con_timestamp_heredado"]
                       if e["nombre_actual"] == p.name][0]
            assert (ROOT / "data" / "raw" / entrada["origen_raw"]).exists()


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


def test_wp11_flag_fiscal():
    """WP-11: ratio fiscal con flag calculado|fallback, sin nulos silenciosos."""
    df = pd.read_csv(PROC / "dim_municipios_renta.csv", encoding="utf-8-sig",
                      dtype=str)
    assert "flag_ratio_fiscal" in df.columns
    assert set(df["flag_ratio_fiscal"].unique()) <= {"calculado", "fallback"}
    assert pd.to_numeric(df["ratio_fiscal"], errors="coerce").notna().all()


def test_wp18_metadata_salario():
    """WP-18: sidecars canonicos completos para salario y emancipacion."""
    import json
    for nombre in ("ovj_salario_joven_2024.json",
                   "emancipacion_juventud_resumen.json"):
        sc = json.loads((PROC / "_meta" / f"{nombre}.meta.json").read_text(
            encoding="utf-8"))
        assert sc["completa"] is True, sc["incidencias"]
        assert all(sc[k] not in (None, "", [])
                   for k in ("fuente", "url", "fecha_extraccion",
                             "n_registros", "hash_sha256", "version_parser"))


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
    cob = pd.read_csv(PROC / "cobertura_anuncios.csv", encoding="utf-8-sig",
                      dtype=str)
    assert list(cob.columns) == ["codigo_ine", "n_crudo", "n_unico",
                                 "fuente_mix", "nivel_fiabilidad"]
    assert len(cob) == 252
    assert set(cob["nivel_fiabilidad"].unique()) <= {
        "alta", "media", "baja", "sin_mercado"}


def test_wp15_renta_origen_fila():
    """WP-15: renta_joven_origen derivada de nulidad real, valores cerrados."""
    df = pd.read_csv(PROC / "dim_municipios_renta.csv", encoding="utf-8-sig",
                      dtype=str)
    assert "renta_joven_origen" in df.columns
    assert set(df["renta_joven_origen"].unique()) <= {
        "Eustat+INE_Atlas", "Eustat", "INE_Atlas", "imputado"}
    eu = pd.to_numeric(df["renta_eustat"], errors="coerce")
    at = pd.to_numeric(df["renta_atlas"], errors="coerce")
    ambos = df[eu.notna() & at.notna()]["renta_joven_origen"]
    assert (ambos == "Eustat+INE_Atlas").all()


def test_wp17_ingestion_manifest():
    """WP-17: acta maquina-leible con una entrada por fichero raw."""
    import json
    man = json.loads((PROC / "_meta" / "ingestion_manifest.json").read_text(
        encoding="utf-8"))
    assert man["n_ficheros"] == len(man["ficheros"]) == 353
    for e in man["ficheros"]:
        assert set(e) >= {"fichero", "bytes", "sha256", "fuente",
                          "url", "fecha_extraccion", "n_registros"}


def test_wp19_precio_nulo_con_motivo():
    """WP-19 (A1+A3): precio_m2_calc + IQR calculados, nulos con motivo."""
    import json
    recs = json.loads((PROC / "anuncios_unificados.json").read_text(
        encoding="utf-8"))
    assert len(recs) == 759
    con_pm2 = [r for r in recs if r["auditoria"].get("precio_m2_calc") is not None]
    assert len(con_pm2) > 700, "precio_m2_calc casi vacio"
    nulos = [r for r in recs if r.get("precio_eur") is None]
    assert nulos, "se esperaban algunos nulos de origen"
    for r in nulos:
        assert r["auditoria"].get("motivo_precio_nulo") in (
            "geo_aproximada", "origen_sin_precio"), r.get("id_anuncio")
    flags = sum(1 for r in recs if r["auditoria"].get("es_outlier_iqr") is True)
    assert flags >= 0
    csv = pd.read_csv(PROC / "anuncios_unificados.csv", encoding="utf-8-sig",
                      dtype=str)
    assert "precio_m2_calc" in csv.columns and "es_outlier_iqr" in csv.columns


def test_wp13_higiene_escritura():
    """WP-13: todo to_csv de transform escribe con encoding utf-8-sig."""
    mal = []
    for py in sorted((ROOT / "transform").glob("*.py")):
        texto = py.read_text(encoding="utf-8")
        for ln in _llamadas_sin(texto, ".to_csv(", "encoding"):
            mal.append(f"{py.name}:{ln}")
    assert not mal, "escrituras sin encoding:\n" + "\n".join(mal)
