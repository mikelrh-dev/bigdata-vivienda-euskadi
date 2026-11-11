"""Normaliza la hoja 'Hoja DATOS' del histórico de Lanbide (paro registrado)
para extraer paro joven por municipio y periodo.

Entrada: raw/lanbide_paro_historico.xlsx (ya descargado).
Salida: raw/lanbide_paro_historico_joven.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_meta  # noqa: E402

log = get_logger("lanbide_historico_paro_joven")

SRC = RAW_DIR / "lanbide_paro_historico.xlsx"
OUT_CSV = RAW_DIR / "lanbide_paro_historico_joven.csv"
URL = "https://www.lanbide.euskadi.eus/contenidos/estadistica/paro_historico/es_def/adjuntos/Dap_Historico.xlsx"


def main() -> int:
    if not SRC.exists():
        log.error("Falta %s", SRC)
        return 1

    import pandas as pd

    df = pd.read_excel(SRC, sheet_name="Hoja DATOS", header=1)
    # Filtrar filas válidas: codigo municipio no nulo y numérico
    df = df[df["Cod. Municipio"].notna()].copy()
    df["Cod. Municipio"] = df["Cod. Municipio"].astype(str).str.strip().str.zfill(5)
    # Eliminar filas de totales/encabezados residuales
    df = df[df["Cod. Municipio"].str.match(r"^\d{5}$", na=False)]

    columnas = {
        "Año": "anio",
        "Trimestre": "trimestre",
        "Cod. Municipio": "codigo_ine",
        "Nombre Municipio": "municipio",
        "Poblacion": "poblacion",
        "Pobl. Activa": "poblacion_activa",
        "TOTAL PARADOS": "paro_total",
        "Varones <20": "paro_varones_menores_20",
        "Varones 20-24": "paro_varones_20_24",
        "Varones 25-29": "paro_varones_25_29",
        "Mujeres <20": "paro_mujeres_menores_20",
        "Mujeres 20-24": "paro_mujeres_20_24",
        "Mujeres 25-29": "paro_mujeres_25_29",
        "Total <20": "paro_total_menores_20",
        "Total 20-24": "paro_total_20_24",
        "Total 25-29": "paro_total_25_29",
    }
    # Seleccionar solo las que existan
    cols_presentes = {k: v for k, v in columnas.items() if k in df.columns}
    out = df[list(cols_presentes.keys())].rename(columns=cols_presentes).copy()
    # Paro joven total (<25) = <20 + 20-24
    if "paro_total_menores_20" in out.columns and "paro_total_20_24" in out.columns:
        out["paro_joven_menores_25"] = (
            out["paro_total_menores_20"].fillna(0) + out["paro_total_20_24"].fillna(0)
        )
    # Tasa ratio (paro joven / poblacion activa) si disponible
    if "poblacion_activa" in out.columns:
        out["tasa_paro_joven_ratio_pct"] = (
            out["paro_joven_menores_25"] / out["poblacion_activa"] * 100
        ).round(4)

    # Limpiar NaN en columnas numéricas
    for c in out.columns:
        if c not in ("codigo_ine", "municipio"):
            out[c] = pd.to_numeric(out[c], errors="coerce")

    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    log.info("Guardado %s (%d filas)", OUT_CSV.name, len(out))
    guardar_meta(OUT_CSV, {
        "fuente": "Lanbide histórico (Dap_Historico.xlsx, Hoja DATOS)",
        "url": URL,
        "n_registros": len(out),
    })
    log.info("Periodos: %s", sorted({(r.get("anio"), r.get("trimestre")) for r in out.to_dict("records")})[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
