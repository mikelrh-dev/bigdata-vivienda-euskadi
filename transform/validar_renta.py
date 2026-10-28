"""F1: blinda renta_municipal_completa (252/252) con escala explícita.

Genera data/raw/renta_municipal_referencia.csv:
  codigo_ine, nombre_canonico,
  renta_hogar_atlas_eur (hogar, INE Atlas ADRH - usar para esfuerzo),
  renta_personal_eustat_eur (personal, Eustat - secundaria),
  anio_renta, renta_origen, nota_escala
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from _common import RAW_DIR, get_logger  # noqa: E402
log = get_logger("f1_renta")

def main() -> int:
    import pandas as pd
    rc = pd.read_csv(RAW_DIR / "renta_municipal_completa.csv", dtype=str, encoding="utf-8-sig")
    dim = pd.read_csv(RAW_DIR / "dim_municipios.csv", dtype=str, encoding="utf-8-sig")
    assert len(rc) == 252, f"esperados 252, hay {len(rc)}"
    assert rc["renta_origen"].notna().all(), "hay municipios sin origen"
    assert set(rc["codigo_ine"].str.zfill(5)) == set(dim["codigo_ine"].str.zfill(5)), "desajuste con dim"
    out = pd.DataFrame({
        "codigo_ine": rc["codigo_ine"].str.zfill(5),
        "nombre_canonico": rc["nombre_canonico"],
        "renta_hogar_atlas_eur": rc["renta_atlas"],
        "renta_personal_eustat_eur": rc["renta_eustat"],
        "anio_renta": rc["anio_renta"],
        "renta_origen": rc["renta_origen"],
        "nota_escala": "renta_hogar_atlas=hogar (INE Atlas ADRH, usar en esfuerzo); "
                       "renta_personal_eustat=personal (Eustat, secundaria). No mezclar.",
    })
    # esfuerzo usa hogar; si faltara, fallback a personal con factor declarado
    out.to_csv(RAW_DIR / "renta_municipal_referencia.csv", index=False, encoding="utf-8-sig")
    log.info("REFERENCIA: 252/252, hogar media=%.0f, personal media=%.0f",
             out["renta_hogar_atlas_eur"].mean(), out["renta_personal_eustat_eur"].mean())
    log.info("CSV -> renta_municipal_referencia.csv (252)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
