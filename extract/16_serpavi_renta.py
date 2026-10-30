"""F16: SERPAVI (MIVAU) - renta de alquiler municipal por codigo INE.

Descarga el XLSX oficial del Sistema Estatal de Referencia del Precio del
Alquiler de Vivienda (SERPAVI/MIVAU) y extrae, para los 252 municipios
vascos, la renta mediana por m2 y el numero de declaraciones del ultimo
año disponible (2024), con fallback LOCF a años anteriores y marca del
metodo usado.

Metodo: descarga programatica (urllib) de XLSX (~68 MB) + pandas.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("serpavi_renta")
URL = ("https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/"
       "2026-03_09_bd_SERPAVI_2011-2024%20-%20DEFINITIVO%20WEB_v2.xlsx")


def main() -> int:
    import urllib.request

    import pandas as pd

    destino = RAW_DIR / "serpavi_renta_municipal.xlsx"
    if not destino.exists():
        log.info("Descargando SERPAVI (~68 MB)...")
        urllib.request.urlretrieve(URL, destino)
        log.info("Guardado %s", destino.name)

    df = pd.read_excel(destino, sheet_name="Municipios", dtype={"CUMUN": str, "CPRO": str})
    basque = df[df["CPRO"].isin(["01", "20", "48"])].copy()
    basque["codigo_ine"] = basque["CUMUN"].astype(str).str.zfill(5)

    years = list(range(11, 25))
    cols_renta = ["ALQM2_LV_M_VC_%02d" % y for y in years]
    cols_n = ["BI_ALVHEPCO_TVC_%02d" % y for y in years]

    filas = []
    for _, r in basque.iterrows():
        # LOCF: ultimo año con dato no nulo
        renta = None
        anio_renta = None
        n_decl = None
        for y in reversed(years):
            v = r.get("ALQM2_LV_M_VC_%02d" % y)
            if pd.notna(v):
                renta = float(v)
                anio_renta = 2000 + y
                n_decl = r.get("BI_ALVHEPCO_TVC_%02d" % y)
                n_decl = int(n_decl) if pd.notna(n_decl) else None
                break
        if anio_renta == 2024:
            metodo = "declaraciones_2024"
        elif anio_renta is not None:
            metodo = "locf_%d" % anio_renta
        else:
            metodo = "sin_dato"
        filas.append({
            "codigo_ine": r["codigo_ine"],
            "municipio": r["NMUN"],
            "provincia_codigo": r["CPRO"],
            "renta_m2_mes_eur": renta,
            "anio_renta": anio_renta,
            "n_declaraciones": n_decl,
            "metodo": metodo,
            "renta_m2_p25": (float(r["ALQM2_LV_25_VC_%02d" % (anio_renta - 2000)]) if anio_renta and pd.notna(r.get("ALQM2_LV_25_VC_%02d" % (anio_renta - 2000))) else None),
            "renta_m2_p75": (float(r["ALQM2_LV_75_VC_%02d" % (anio_renta - 2000)]) if anio_renta and pd.notna(r.get("ALQM2_LV_75_VC_%02d" % (anio_renta - 2000))) else None),
        })

    out_df = pd.DataFrame(filas)
    csv_path = RAW_DIR / "serpavi_renta_municipal.csv"
    out_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    log.info("CSV -> %s (%d)", csv_path.name, len(out_df))

    regs = out_df.to_dict(orient="records")
    guardar_json(RAW_DIR / "serpavi_renta_municipal.json", regs,
                metadata={"fuente": "SERPAVI/MIVAU (Modelo 100, datos tributarios)",
                          "url": URL,
                          "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                          "periodo": "2011-2024 (LOCF)",
                          "n_municipios": len(out_df),
                          "n_registros": len(out_df),
                          "nota": "Renta fiscal (declaraciones), no precio de mercado. "
                                  "Cubre solo municipios con declaraciones."})
    log.info("JSON -> serpavi_renta_municipal.json")
    print(out_df["metodo"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())