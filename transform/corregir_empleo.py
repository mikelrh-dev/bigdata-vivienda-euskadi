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
    df["brecha_ocupacion_actividad_pct"] = (pd.to_numeric(df["tasa_ocupacion_pct"], errors="coerce")
                                            - pd.to_numeric(df["tasa_actividad_pct"], errors="coerce")).round(2)
    df["tasa_paro_valida"] = df["tasa_paro_lanbide_pct"].notna()
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
