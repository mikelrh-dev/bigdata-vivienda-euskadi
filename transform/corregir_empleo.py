"""F2/F4d/U1: corrige y valida udalmap_empleo (local, sin proxy).

- tasa_paro_aprox_pct (cociente, distinta base) -> dropped in memory (no se escribe).
- tasa_paro_lanbide_pct (ind.13) + ocupacion juvenil (50) -> validas 0-100.
- U1: valida nuevos bloques (porcentaje 0-100, por-mil >=0, euros >0).
Genera data/raw/udalmap_empleo_corregido.csv/.json.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402
log = get_logger("f2_empleo")
NOTA = ("tasa_paro_aprox_pct invalidada (cociente con distinta base). Usar "
        "tasa_paro_lanbide_pct (ind.13 Udalmap, paro registrado 16-64). "
        "U1: vivienda/movilidad/renta de contraste (Etxebide, VPO, commuting).")
PROC_DIR = RAW_DIR.parent / "procesado"
PROC_DIR.mkdir(parents=True, exist_ok=True)
PCT_100 = ["tasa_actividad_pct", "tasa_ocupacion_pct", "tasa_paro_lanbide_pct",
           "tasa_ocupacion_juvenil_16_24_pct", "trabaja_fuera_pct",
           "afiliacion_ss_16_24_pct", "renta_trabajo_pct", "suelo_urbanizable_pct",
           "etxebide_adjudicadas_por_100"]
POR_MIL = ["etxebide_solicitudes_por_mil", "vpo_adjudicadas_por_mil",
           "vpo_terminadas_por_mil", "licencias_nueva_por_mil", "cert_energetico_por_mil"]
EUROS = ["renta_familiar_eur", "renta_personal_total_eur", "renta_personal_disponible_eur",
         "superficie_media_m2", "antiguedad_media_anyos"]

def main() -> int:
    import pandas as pd
    # Nota Latin-1: udalmap_empleo.csv se lee en UTF-8-sig (ya saneado).
    # La fuente etxebide original (Latin-1) se sanea en la capa silver.
    df = pd.read_csv(RAW_DIR / "udalmap_empleo.csv", dtype=str, encoding="utf-8-sig")
    df["codigo_ine"] = df["codigo_ine"].str.zfill(5)
    assert len(df) == 252, f"esperados 252, hay {len(df)}"
    for c in PCT_100:
        if c in df.columns:
            num = pd.to_numeric(df[c], errors="coerce")
            bad = df[~df[c].isna() & ~num.between(0, 100)]
            assert len(bad) == 0, f"{c} fuera de 0-100: {bad[['codigo_ine', c]].head()}"
    for c in POR_MIL + EUROS:
        if c in df.columns:
            num = pd.to_numeric(df[c], errors="coerce")
            bad = df[~df[c].isna() & ~(num >= 0)]
            assert len(bad) == 0, f"{c} negativo: {bad[['codigo_ine', c]].head()}"
    # Drop in memory before writing processed outputs (raw untouched).
    if "tasa_paro_aprox_pct" in df.columns:
        df = df.drop(columns=["tasa_paro_aprox_pct"])
    # NOTA WP-05: no se calcula brecha_ocupacion_actividad_pct. Las tasas de
    # ocupacion y actividad de Udalmap no comparten base (248/252 dan
    # ocupacion > actividad, imposible por definicion), asi que la resta no
    # mide ninguna brecha. Ver openspec/archive/2026-11-10-docs/reglas_limpieza.md.
    # WP-04: un 0,00 exacto con muy pocos activos es artefacto, no medicion.
    # Se conserva el valor publicado y la tasa de trabajo queda en NaN.
    p = pd.to_numeric(df["tasa_paro_lanbide_pct"], errors="coerce")
    df["tasa_paro_lanbide_bruto"] = p
    df["paro_registrado_cero"] = p.eq(0)
    df["tasa_paro_valida"] = p.notna() & p.gt(0)
    df["tasa_paro_lanbide_pct"] = p.mask(p.le(0))
    # M5 COMPLEMENTARIOS-01: 249 -> 252 con extractores 18/21 (Lanbide
    # directo, fuente OFICIAL, sin imputacion comarcal/IDW). Para los
    # municipios sin tasa Udalmap (01003/20037/48916) se calcula
    # paro_total/poblacion_activa*100 desde `lanbide_paro_juvenil.csv`
    # (extract 18). El bruto Udalmap se conserva para trazabilidad.
    df["tasa_paro_fuente"] = "udalmap"
    lanb_path = RAW_DIR / "lanbide_paro_juvenil.csv"
    if lanb_path.exists():
        lb = pd.read_csv(lanb_path, dtype=str, encoding="utf-8-sig")
        lb["codigo_ine"] = lb["codigo_ine"].str.zfill(5)
        _pt = pd.to_numeric(lb["paro_total"], errors="coerce")
        _pa = pd.to_numeric(lb["poblacion_activa"], errors="coerce")
        tasa_lb = (_pt / _pa * 100).round(2)
        tasa_lb = tasa_lb.mask((_pa.notna() & (_pa <= 0)) | tasa_lb.isna())
        lb = lb.assign(tasa_lanbide_directa=tasa_lb)
        lb = lb.drop_duplicates(subset=["codigo_ine"])[["codigo_ine", "tasa_lanbide_directa"]]
    else:
        lb = pd.DataFrame(columns=["codigo_ine", "tasa_lanbide_directa"])
    df = df.merge(lb, on="codigo_ine", how="left")
    faltan = df["tasa_paro_lanbide_pct"].isna() & df["tasa_lanbide_directa"].notna()
    df.loc[faltan, "tasa_paro_lanbide_pct"] = df.loc[faltan, "tasa_lanbide_directa"]
    df.loc[faltan, "tasa_paro_fuente"] = "lanbide_directo"
    df.loc[faltan, "tasa_paro_valida"] = True
    df = df.drop(columns=["tasa_lanbide_directa"])
    # M5 COMPLEMENTARIOS-01: paro oficial en el 100% (sin imputacion).
    # Fila sin fuente oficial -> metodo 'ninguno' + is_imputed=false (nunca
    # comarcal/IDW). Tras 18/21 + este merge debe ser 0 filas.
    df["metodo_imputacion"] = "oficial"
    df.loc[df["tasa_paro_lanbide_pct"].isna(), "metodo_imputacion"] = "ninguno"
    df["is_imputed"] = False
    n_paro_ok = int(df["tasa_paro_lanbide_pct"].notna().sum())
    log.info("M5 paro Lanbide: %d/252 oficiales, 0 imputadas (%d lanbide_directo)",
             n_paro_ok, int((df["tasa_paro_fuente"] == "lanbide_directo").sum()))
    assert df["tasa_paro_lanbide_pct"].between(0, 100).sum() == n_paro_ok
    df["nota_metodologica"] = NOTA
    df.to_csv(PROC_DIR / "udalmap_empleo_corregido.csv", index=False, encoding="utf-8-sig")
    guardar_json(PROC_DIR / "udalmap_empleo_corregido.json", df.to_dict(orient="records"),
                 metadata={"fuente": "Udalmap corregido F2/F4d/U1 (local)",
                           "n_municipios": len(df), "nota": NOTA,
                           "cobertura": {c: int(df[c].notna().sum()) for c in df.columns
                                          if c not in ("codigo_ine", "nombre_canonico", "nota_metodologica")}})
    cov = {c: int(df[c].notna().sum()) for c in
           ["tasa_paro_lanbide_pct", "etxebide_solicitudes_por_mil", "trabaja_fuera_pct",
            "renta_familiar_eur", "superficie_media_m2"]}
    log.info("U1: 252 munis validados. Cobertura clave: %s", cov)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
