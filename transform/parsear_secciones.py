"""V4: parsea secciones censales de alquiler (Bizkaia+Gipuzkoa+Alava, 2024).

Los 3 CSV originales comparten layout: filas de datos con
Municipio|Distrito|Seccion + 12 metricas; el municipio solo aparece en la
primera fila de cada grupo (forward-fill). Sin red.
Genera data/raw/alquiler_seccion.csv (con codigo_ine) y resumen por municipio.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from _common import RAW_DIR, get_logger  # noqa: E402
from entity_resolution import resolver_municipio  # noqa: E402
log = get_logger("v4_secciones")
PROC_DIR = RAW_DIR.parent / "procesado"
PROC_DIR.mkdir(parents=True, exist_ok=True)
METS = ["renta_media_eur_m2_media", "renta_media_eur_m2_mediana", "renta_media_eur_m2_p25",
        "renta_media_eur_m2_p75", "cuantia_media_eur_mes_media", "cuantia_media_eur_mes_mediana",
        "cuantia_media_eur_mes_p25", "cuantia_media_eur_mes_p75", "superficie_media_m2_media",
        "superficie_media_m2_mediana", "superficie_media_m2_p25", "superficie_media_m2_p75"]

def _num(v):
    if v is None: return None
    s = str(v).strip().replace(".", "").replace(",", ".")
    if s in ("", "..", "-"): return None
    try: return float(s)
    except ValueError: return None

def _territorio(cod):
    if cod is None: return ""
    s = str(cod).strip()
    if s.startswith("01"): return "Araba/Álava"
    if s.startswith("20"): return "Gipuzkoa"
    if s.startswith("48"): return "Bizkaia"
    return ""

def _parsear(ruta: Path) -> list[dict]:
    with open(ruta, encoding="utf-8") as fh:
        filas = list(csv.reader(fh, delimiter=";", quotechar='"'))
    regs, muni, dist = [], "", ""
    for f in filas[5:]:
        if len(f) < 4: continue
        c0, c1, c2 = f[0].strip(), f[1].strip(), f[2].strip()
        if c0 and not c1 and not c2 and not any(_num(x) is not None for x in f[3:]):
            continue  # cabecera de territorio
        if c0: muni = c0
        if c1: dist = c1
        if not muni or not c2: continue
        vals = [(_num(f[i]) if i < len(f) else None) for i in range(3, 15)]
        if all(v is None for v in vals): continue
        cod, can = resolver_municipio(muni)
        regs.append({"territorio": _territorio(cod), "municipio": muni, "codigo_ine": cod,
                     "nombre_canonico": can, "distrito": dist, "seccion": c2,
                     **dict(zip(METS, vals)), "anio_fuente": 2024})
    return regs

def main() -> int:
    todos = []
    for nombre in ["alquiler_seccion_a_original.csv", "alquiler_seccion_b_original.csv",
                   "alquiler_distrito_seccion_original.csv"]:
        lote = _parsear(RAW_DIR / nombre)
        log.info("%s: %d secciones", nombre, len(lote))
        todos.extend(lote)
    import pandas as pd
    df = pd.DataFrame(todos)
    df.to_csv(PROC_DIR / "alquiler_seccion.csv", index=False, encoding="utf-8-sig")
    g = df.groupby(["codigo_ine", "municipio"]).agg(
        n_secciones=("seccion", "count"),
        renta_mediana_min=("renta_media_eur_m2_mediana", "min"),
        renta_mediana_max=("renta_media_eur_m2_mediana", "max")).reset_index()
    g["rango_intra_municipal"] = (g["renta_mediana_max"] - g["renta_mediana_min"]).round(2)
    g.to_csv(RAW_DIR.parent / "procesado" / "alquiler_seccion_resumen.csv",
             index=False, encoding="utf-8-sig")
    log.info("V4: %d secciones, %d municipios. Rango medio intra: %.2f eur/m2",
             len(df), df["codigo_ine"].nunique(), g["rango_intra_municipal"].mean())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
