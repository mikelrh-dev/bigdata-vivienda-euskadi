"""F18: paro registrado por municipio y edad (Lanbide Open Data).

Descarga el XLSX historico de Lanbide (Dap_Historico.xlsx) y extrae,
para el ultimo periodo disponible, el paro registrado en cada uno de los
252 municipios desglosado por edad (con foco en jovenes <25).

Metodo: descarga programatica (requests) de XLSX + pandas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("lanbide_paro_juvenil")
URL = "https://www.lanbide.euskadi.eus/contenidos/estadistica/paro_historico/es_def/adjuntos/Dap_Historico.xlsx"


def main() -> int:
    import urllib.request

    import pandas as pd

    destino = RAW_DIR / "lanbide_paro_historico.xlsx"
    if not destino.exists():
        log.info("Descargando %s", URL)
        urllib.request.urlretrieve(URL, destino)
        log.info("Guardado %s", destino.name)

    df = pd.read_excel(destino, sheet_name="Hoja DATOS", header=1, dtype={"Cod. Municipio": str})
    latest = int(df["Año"].max())
    tri = int(df[df["Año"] == latest]["Trimestre"].max())
    sub = df[(df["Año"] == latest) & (df["Trimestre"] == tri)].copy()
    log.info("Periodo seleccionado: %d T%d (%d filas)", latest, tri, len(sub))

    sub["codigo_ine"] = sub["Cod. Municipio"].astype(str).str.strip().str.zfill(5)
    sub["paro_joven_menores_25"] = (
        pd.to_numeric(sub["Total <20"], errors="coerce").fillna(0)
        + pd.to_numeric(sub["Total 20-24"], errors="coerce").fillna(0)
    )
    sub["paro_total"] = pd.to_numeric(sub["TOTAL PARADOS"], errors="coerce")
    sub["poblacion"] = pd.to_numeric(sub["Poblacion"], errors="coerce")
    sub["poblacion_activa"] = pd.to_numeric(sub["Pobl. Activa"], errors="coerce")

    cols = ["codigo_ine", "Nombre Municipio", "Año", "Trimestre",
            "paro_total", "paro_joven_menores_25", "poblacion", "poblacion_activa",
            "Total <20", "Total 20-24", "Total 25-29"]
    out = sub[cols].copy()
    out = out.rename(columns={"Nombre Municipio": "municipio", "Año": "anio", "Trimestre": "trimestre",
                             "Total <20": "paro_menores_20", "Total 20-24": "paro_20_24",
                             "Total 25-29": "paro_25_29"})
    out["tasa_paro_joven_pct"] = (out["paro_joven_menores_25"] / out["poblacion_activa"].replace(0, pd.NA) * 100).round(2)

    # CSV
    csv_path = RAW_DIR / "lanbide_paro_juvenil.csv"
    out.to_csv(csv_path, index=False, encoding="utf-8-sig")
    log.info("CSV -> %s (%d)", csv_path.name, len(out))

    # JSON
    regs = out.to_dict(orient="records")
    guardar_json(RAW_DIR / "lanbide_paro_juvenil.json", regs,
                metadata={"fuente": "Lanbide Dap_Historico.xlsx",
                          "periodo": f"{latest} T{tri}",
                          "n_municipios": len(out),
                          "nota": "paro registrado (no tasa de desempleo). Joven = <20 + 20-24."})
    log.info("JSON -> lanbide_paro_juvenil.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY