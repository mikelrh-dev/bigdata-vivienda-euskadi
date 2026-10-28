"""Extracción de indicadores adicionales de Udalmap (api.euskadi.eus).

Complementa `udalmap_empleo.py` (19 indicadores) con otros de alto valor
para el análisis de emancipación juvenil: vivienda, demografía, migración,
renta por sexo y mercado laboral. Total disponible: 222 indicadores; aquí se
extraen los prioritarios (~28).

Salida: data/raw/udalmap_indicadores_adicionales.json y .csv
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("udalmap_indicadores_adicionales")

BASE = "https://api.euskadi.eus/udalmap/indicators"

# Indicadores prioritarios (id -> etiqueta corta). El nombre oficial se
# obtiene de la API y se guarda en metadata.
INDICADORES = {
    # Vivienda
    "68": "viviendas_desocupadas_pct",
    "69": "viviendas_mas_50_anios_pct",
    "70": "indice_confort",
    "71": "edificios_ruinosos_pct",
    "67": "densidad_viviendas_suelo_residencial",
    "76": "edificios_sin_ascensor_pct",
    "111": "densidad_poblacion",
    "207": "suelo_artificializado_pct",
    # Demografía
    "162": "poblacion_total",
    "40": "variacion_poblacion_periodo",
    "41": "variacion_poblacion_5_anios",
    "42": "indice_envejecimiento",
    "43": "indice_dependencia",
    "44": "indice_sobreenvejecimiento",
    # Migración
    "74": "poblacion_extranjera_pct",
    # Renta por sexo
    "184": "renta_personal_total_mujeres_eur",
    "185": "renta_personal_disponible_mujeres_eur",
    "186": "renta_trabajo_mujeres_pct",
    "187": "renta_personal_total_hombres_eur",
    "188": "renta_personal_disponible_hombres_eur",
    "189": "renta_trabajo_hombres_pct",
    "190": "renta_personal_total_total_eur",
    "191": "renta_personal_disponible_total_eur",
    "166": "renta_familiar_mujeres_eur",
    "167": "renta_familiar_hombres_eur",
    # Mercado laboral
    "181": "afiliacion_ss_total_pct",
    "182": "afiliacion_ss_hombres_pct",
    "183": "afiliacion_ss_mujeres_pct",
    "14": "paro_larga_duracion_pct",
    "169": "paro_hombres_pct",
    "170": "paro_mujeres_pct",
}


def _slug(s: str) -> str:
    s = html.unescape(s or "")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _descargar(indicator_id: str) -> dict:
    import requests

    url = f"{BASE}/{indicator_id}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def _extraer_ultimo(data: dict, dim_codigos: set[str]) -> dict[str, float]:
    resultado = {}
    for ent in data.get("municipalities", data.get("entities", [])):
        codigo = str(ent.get("id", "")).strip().zfill(5)
        if codigo not in dim_codigos:
            continue
        years = ent.get("years", [{}])
        if not years:
            continue
        y = years[0]
        ultimo = None
        for k in sorted(y.keys()):
            if y[k] is not None:
                ultimo = y[k]
        if ultimo is not None:
            resultado[codigo] = ultimo
    return resultado


def main() -> int:
    dim_path = RAW_DIR / "dim_municipios.json"
    if not dim_path.exists():
        log.error("Falta dim_municipios.json.")
        return 1
    dim = json.loads(dim_path.read_text(encoding="utf-8"))
    registros = dim.get("datos", []) if isinstance(dim, dict) else dim
    dim_codigos = {r["codigo_ine"] for r in registros}
    info_por_codigo = {r["codigo_ine"]: r for r in registros}

    datos: dict[str, dict] = {c: {} for c in dim_codigos}
    nombres_oficiales: dict[str, str] = {}

    for ind_id, etiqueta in INDICADORES.items():
        log.info("Descargando indicador %s (%s)...", etiqueta, ind_id)
        try:
            data = _descargar(ind_id)
        except Exception as exc:  # noqa: BLE001
            log.error("Error descargando %s: %s", ind_id, exc)
            continue
        nombres_oficiales[ind_id] = html.unescape(data.get("name", etiqueta))
        valores = _extraer_ultimo(data, dim_codigos)
        log.info("%s: %d municipios", etiqueta, len(valores))
        for codigo, valor in valores.items():
            datos[codigo][etiqueta] = valor

    registros_out = []
    for codigo in sorted(dim_codigos):
        info = info_por_codigo.get(codigo, {})
        fila = {
            "codigo_ine": codigo,
            "nombre_canonico": info.get("nombre_canonico"),
            "territorio": info.get("territorio"),
        }
        for etiqueta in INDICADORES.values():
            fila[etiqueta] = datos[codigo].get(etiqueta)
        registros_out.append(fila)

    guardar_json(
        RAW_DIR / "udalmap_indicadores_adicionales.json",
        registros_out,
        metadata={
            "fuente": "Udalmap (api.euskadi.eus) indicadores adicionales",
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_municipios": len(registros_out),
            "indicadores": {
                ind_id: {
                    "etiqueta": etiqueta,
                    "nombre_oficial": nombres_oficiales.get(ind_id),
                }
                for ind_id, etiqueta in INDICADORES.items()
            },
        },
    )

    columnas = ["codigo_ine", "nombre_canonico", "territorio"] + list(INDICADORES.values())
    destino_csv = RAW_DIR / "udalmap_indicadores_adicionales.csv"
    with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(registros_out)
    log.info("CSV -> %s", destino_csv.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
