"""Gate de aceptacion de la fase extraccion+transformacion (WP-14).

15 checks. Exit 0 si todo PASS, 1 si algun FAIL. No escribe en data/raw.
Uso: python verificar_fase_datos.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "procesado"

import pandas as pd  # noqa: E402

ok = True


def check(nombre: str, cond: bool, det: str = "") -> None:
    global ok
    print(("PASS" if cond else "FAIL"), nombre, det)
    if not cond:
        ok = False


def main() -> int:
    # 1. Manifest integro
    man = (ROOT / "docs" / "raw_manifest_sha256.txt").read_text(encoding="utf-8")
    malas, n = [], 0
    for ln in man.splitlines():
        if not ln.strip():
            continue
        h, rel = ln.split(None, 1)
        p = RAW / rel.strip()
        n += 1
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
            malas.append(rel)
    check("01 manifest integro", not malas, f"{n} ficheros" + (f" malas={malas[:3]}" if malas else ""))

    # 2. Sin gemelos derivados en raw (WP-08)
    gemelos = [p.name for p in RAW.rglob("*") if "corregido" in p.name]
    check("02 raw sin derivados legacy", not gemelos, f"{gemelos}" if gemelos else "limpio")

    # 3-4. Indices de metadata cubren lo observado
    idx = json.loads((PROC / "_meta" / "index.json").read_text(encoding="utf-8"))
    njson = len(list(RAW.rglob("*.json")))
    check("03 metadata cubre JSON", idx["n_ficheros"] == njson, f"{idx['n_ficheros']}/{njson}")
    cidx = json.loads((PROC / "_meta" / "csvs_index.json").read_text(encoding="utf-8"))
    ncsv = len(list(RAW.rglob("*.csv")))
    check("04 inventario cubre CSV", cidx["n_csvs"] == ncsv, f"{cidx['n_csvs']}/{ncsv}")

    # 5. Dim 252 + codigos
    dim = pd.read_csv(PROC / "dim_municipios.csv", encoding="utf-8-sig", dtype=str)
    dim["codigo_ine"] = dim["codigo_ine"].str.zfill(5)
    check("05 dim 252 + len5", len(dim) == 252 and (dim["codigo_ine"].str.len() == 5).all(), f"{len(dim)}")

    # 6. n_anuncios real post-dedup (verdad v5: 594/843)
    check("06 n_anuncios 594/843", int(pd.to_numeric(dim["n_anuncios"]).sum()) == 594
          and int(pd.to_numeric(dim["n_anuncios_raw"]).sum()) == 843,
          f"real={pd.to_numeric(dim['n_anuncios']).sum()}")

    # 7-8. Ceros y brecha (FAIL conocido, sin enmascarar como PASS)
    emp = pd.read_csv(PROC / "udalmap_empleo_corregido.csv", encoding="utf-8-sig", dtype=str)
    _cero = emp[emp["paro_registrado_cero"] == "True"] if "paro_registrado_cero" in emp.columns else emp.iloc[0:0]
    _con_nulo = _cero[_cero["tasa_paro_lanbide_pct"].astype(str).str.lower().isin(["nan", "none", "", "nat"]) | _cero["tasa_paro_lanbide_pct"].isna()]
    _con_valor = _cero[~_cero.index.isin(_con_nulo.index)]
    _CONOCIDOS = {("Aramaio", "0.28"), ("Gaintza", "1.45"), ("Usansolo", "3.26")}
    _visto = {(str(r["nombre_canonico"]).strip(), str(r["tasa_paro_lanbide_pct"]).strip()) for _, r in _con_valor.iterrows()}
    _desconocidos = sorted(_visto - _CONOCIDOS)
    _nombres_conocidos = "Aramaio 0.28, Gaintza 1.45, Usansolo 3.26"
    if _con_valor.empty:
        check("07 ceros a nulo con flag", "paro_registrado_cero" in emp.columns and _cero["tasa_paro_lanbide_pct"].isna().all(),
              "sin ceros con valor no nulo")
    elif not _desconocidos and _visto == _CONOCIDOS:
        # Casos documentados v5: jamás PASS, jamás imputación comarcal.
        check(f"07 FAIL conocido paro-cero ({_nombres_conocidos})", False,
              f"{len(_con_valor)} ceros documentados con tasa no nula (no enmascarados, sin imputación)")
    else:
        check("07 FAIL ceros no conocidos", False,
              f"desconocidos={_desconocidos} conocidos={sorted(_visto & _CONOCIDOS)}")
    gold = pd.read_csv(PROC / "dim_municipios_enriquecido.csv", encoding="utf-8-sig", dtype=str)
    check("08 sin brecha ocup-activ", "brecha_ocupacion_actividad_pct" not in gold.columns)

    # 9-10. Esfuerzo canonico + tension
    base = pd.read_csv(PROC / "analisis_variables_base.csv", encoding="utf-8-sig", dtype=str)
    renta = pd.read_csv(PROC / "dim_municipios_renta.csv", encoding="utf-8-sig", dtype=str)
    m = base[["codigo_ine", "esfuerzo_joven_pct"]].merge(
        renta[["codigo_ine", "esfuerzo_joven_pct"]], on="codigo_ine",
        suffixes=("_b", "_r")).dropna()
    d = (pd.to_numeric(m["esfuerzo_joven_pct_b"], errors="coerce")
         - pd.to_numeric(m["esfuerzo_joven_pct_r"], errors="coerce")).abs()
    check("09 canonico preservado", len(m) > 0 and (d < 0.05).all(), f"{len(m)} mun")
    ten = pd.read_csv(PROC / "dim_municipios_tension.csv", encoding="utf-8-sig", dtype=str)
    check("10 tension cerrada", int(ten.isna().sum().sum()) == 0
          and set(ten["tension_categoria"].unique()) <= {"baja", "media", "alta"})

    # 11. Pytest bateria fase datos
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_fase_datos.py",
                        "tests/test_raw_inmutable.py", "tests/test_raw_guardrails.py",
                        "-q"], capture_output=True, text=True, cwd=ROOT)
    tail = (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else ""
    check("11 pytest bateria verde", r.returncode == 0, tail)

    # 12. Orquestador declara plan (dry-run)
    r2 = subprocess.run([sys.executable, "transform/run_all.py", "--dry-run"],
                        capture_output=True, text=True, cwd=ROOT)
    check("12 orquestador dry-run", r2.returncode == 0,
          [l for l in r2.stdout.splitlines() if "pasos" in l][:1])

    # 13. Poblacion joven con fallback declarado
    pj = pd.read_csv(PROC / "poblacion_joven_municipal.csv", encoding="utf-8-sig", dtype=str)
    check("13 pob joven 252 + metodo", len(pj) == 252 and pj["metodo"].str.contains("periodo=").all(),
          f"{len(pj)}")

    # 14. Tipologia cerrada
    check("14 tipologia cerrada", set(dim["tipologia_mercado"].unique()) <= {
        "Nivel1_Mercado_Dinamico", "Nivel2_Mercado_Regulado", "Nivel3_Mercado_Rural_Cerrado"})

    # 15. Raw congelado (solo lectura: ningun paso escribe RAW_DIR salvo f4 dirigido)
    import re
    escritores = []
    for py in (ROOT / "transform").glob("*.py"):
        if py.name == "f4_pisos_dirigido.py":
            continue
        txt = py.read_text(encoding="utf-8")
        if re.search(r"(RAW_DIR|RAW)\s*/[^=]*\.(to_csv|write_text|open\([^)]*['\"]w)", txt):
            escritores.append(py.name)
        for mm in re.finditer(r"\.to_csv\((.*?)\)", txt):
            pass  # cubierto por test_wp13
    # chequeo simple: to_csv con destino RAW
    for py in (ROOT / "transform").glob("*.py"):
        if py.name == "f4_pisos_dirigido.py":
            continue
        txt = py.read_text(encoding="utf-8")
        if re.search(r"to_csv\(\s*(RAW_DIR|RAW)\b", txt):
            escritores.append(py.name + ":to_csvRAW")
    check("15 transform no escribe raw", not escritores, f"{escritores}" if escritores else "solo lectura")

    # 16-18. Artefactos de trazabilidad WP-12/17/09 (lo que verifica demo = tests)
    cob = pd.read_csv(PROC / "cobertura_anuncios.csv", encoding="utf-8-sig", dtype=str)
    check("16 cobertura auditable", len(cob) == 252
          and set(cob["nivel_fiabilidad"].unique()) <= {"alta", "media", "baja", "sin_mercado"},
          f"{len(cob)} mun")
    man = json.loads((PROC / "_meta" / "ingestion_manifest.json").read_text(encoding="utf-8"))
    # 354 = ficheros con hash en ingestion_manifest local; distinto de los
    # 352 ficheros raw publicados en HDFS (alias documentado, no se colapsa).
    check("17 ingestion manifest", man["n_ficheros"] == len(man["ficheros"]) == 354,
          f"{man['n_ficheros']} ficheros (354 ingestion local; 352 raw en HDFS)")
    mapa = json.loads((PROC / "_meta" / "nombres_normalizados_map.json").read_text(encoding="utf-8"))
    import re as _re
    con_ts = [p.name for p in PROC.glob("*_normalizado.json")
              if _re.search(r"_20\d{6}(_\d+)?_normalizado\.json$", p.name)]
    reg = {e["nombre_actual"] for e in mapa["ficheros_con_timestamp_heredado"]}
    check("18 nombres estables registrados", set(con_ts) <= reg, f"{len(con_ts)} con ts")

    print("RESULTADO:", "OK 18/18" if ok else "PENDIENTE (ver FAIL)")
    # Huella SHA-256 reproducible de los artefactos comprobados (mismo
    # criterio que check 01 con docs/raw_manifest_sha256.txt). Se emite
    # siempre: con 07 FAIL conocido el resultado sigue siendo PENDIENTE.
    _artefactos = [
        ROOT / "docs" / "raw_manifest_sha256.txt",
        PROC / "dim_municipios.csv",
        PROC / "udalmap_empleo_corregido.csv",
        PROC / "_meta" / "ingestion_manifest.json",
        PROC / "cobertura_anuncios.csv",
    ]
    _h = hashlib.sha256()
    for _p in _artefactos:
        _h.update(_p.read_bytes())
    print("HUELLA SHA-256:", _h.hexdigest())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
