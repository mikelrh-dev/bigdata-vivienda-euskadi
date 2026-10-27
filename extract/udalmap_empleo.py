"""Extracción de indicadores de empleo/actividad municipal desde Udalmap (Open Data Euskadi).

Descarga tasa de actividad (id 8) y tasa de ocupación (id 10) para todos
los municipios de la C.A. de Euskadi y calcula la tasa de paro aproximada.

Salida: data/raw/udalmap_empleo.json y .csv
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("udalmap_empleo")

BASE = "https://api.euskadi.eus/udalmap/indicators"
INDICADORES = {
    "actividad": "8",
    "ocupacion": "10",
    # F4d: paro registrado real (Lanbide) + ocupación juvenil (16-24).
    # El cociente actividad/ocupación usa distinta base y daba paro negativo;
    # estos dos indicadores lo sustituyen con fuente oficial municipal.
    "paro_lanbide": "13",
    "ocupacion_juvenil": "50",
    # U1: vivienda, movilidad y renta de contraste (252 munis, 2022-2024).
    "etxebide_solicitudes": "86",
    "etxebide_adjudicadas": "163",
    "vpo_adjudicadas": "108",
    "vpo_terminadas": "73",
    "licencias_nueva": "72",
    "trabaja_fuera": "100",
    "afiliacion_ss": "192",
    "renta_familiar": "206",
    "renta_personal_total": "60",
    "renta_personal_disponible": "61",
    "renta_trabajo_pct": "64",
    "superficie_media": "178",
    "antiguedad_media": "175",
    "cert_energetico": "95",
    "suelo_urbanizable": "77",
}


def _descargar(indicator_id: str) -> dict:
    import requests

    url = f"{BASE}/{indicator_id}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def _extraer_municipios(data: dict, dim_codigos: set[str]) -> dict[str, float]:
    """Devuelve {codigo_ine: valor_2024} para municipios presentes en dim."""
    resultado = {}
    for ent in data.get("municipalities", data.get("entities", [])):
        codigo = str(ent.get("id", "")).strip().zfill(5)
        if codigo not in dim_codigos:
            continue
        years = ent.get("years", [{}])
        if not years:
            continue
        y = years[0]
        # último año disponible
        ultimo = None
        for k in sorted(y.keys()):
            if y[k] is not None:
                ultimo = y[k]
        if ultimo is not None:
            resultado[codigo] = ultimo
    return resultado


def main() -> int:
    # Cargar códigos canónicos
    dim_path = RAW_DIR / "dim_municipios.json"
    if not dim_path.exists():
        log.error("Falta dim_municipios.json. Ejecuta transform/dim_municipios.py primero.")
        return 1
    dim = json.loads(dim_path.read_text(encoding="utf-8"))
    dim_codigos = {r["codigo_ine"] for r in dim["datos"] if isinstance(dim, dict) and "datos" in dim} if False else set()
    # dim_municipios.json es una lista directa (guardar_json envuelve en metadata/datos?)
    if isinstance(dim, dict):
        registros = dim.get("datos", [])
    else:
        registros = dim
    dim_codigos = {r["codigo_ine"] for r in registros}

    datos: dict[str, dict] = {c: {} for c in dim_codigos}

    for nombre, ind_id in INDICADORES.items():
        log.info("Descargando indicador %s (%s)...", nombre, ind_id)
        try:
            data = _descargar(ind_id)
        except Exception as exc:  # noqa: BLE001
            log.error("Error descargando %s: %s", nombre, exc)
            continue
        valores = _extraer_municipios(data, dim_codigos)
        log.info("%s: %d municipios", nombre, len(valores))
        for codigo, valor in valores.items():
            datos[codigo][nombre] = valor

    # F2/F4d: NO derivar tasa de paro del cociente actividad/ocupacion
    # (distinta base; ocu>act en ~248/252 y salía negativo). Paro real =
    # indicador 13 Lanbide; ocupación juvenil = indicador 50.
    registros_out = []
    for codigo in sorted(dim_codigos):
        info = next((r for r in registros if r["codigo_ine"] == codigo), {})
        act = datos[codigo].get("actividad")
        ocu = datos[codigo].get("ocupacion")
        paro = datos[codigo].get("paro_lanbide")  # F4d: Lanbide oficial
        ocu_juv = datos[codigo].get("ocupacion_juvenil")  # F4d: 16-24 años
        registros_out.append(
            {
                "codigo_ine": codigo,
                "nombre_canonico": info.get("nombre_canonico"),
                "territorio": info.get("territorio"),
                "tasa_actividad_pct": act,
                "tasa_ocupacion_pct": ocu,
                "tasa_paro_aprox_pct": None,
                "tasa_paro_lanbide_pct": paro,
                "tasa_ocupacion_juvenil_16_24_pct": ocu_juv,
                "etxebide_solicitudes_por_mil": datos[codigo].get("etxebide_solicitudes"),
                "etxebide_adjudicadas_por_100": datos[codigo].get("etxebide_adjudicadas"),
                "vpo_adjudicadas_por_mil": datos[codigo].get("vpo_adjudicadas"),
                "vpo_terminadas_por_mil": datos[codigo].get("vpo_terminadas"),
                "licencias_nueva_por_mil": datos[codigo].get("licencias_nueva"),
                "trabaja_fuera_pct": datos[codigo].get("trabaja_fuera"),
                "afiliacion_ss_16_24_pct": datos[codigo].get("afiliacion_ss"),
                "renta_familiar_eur": datos[codigo].get("renta_familiar"),
                "renta_personal_total_eur": datos[codigo].get("renta_personal_total"),
                "renta_personal_disponible_eur": datos[codigo].get("renta_personal_disponible"),
                "renta_trabajo_pct": datos[codigo].get("renta_trabajo_pct"),
                "superficie_media_m2": datos[codigo].get("superficie_media"),
                "antiguedad_media_anyos": datos[codigo].get("antiguedad_media"),
                "cert_energetico_por_mil": datos[codigo].get("cert_energetico"),
                "suelo_urbanizable_pct": datos[codigo].get("suelo_urbanizable"),
                "anio_fuente": 2024,
            }
        )

    guardar_json(
        RAW_DIR / "udalmap_empleo.json",
        registros_out,
        metadata={
            "fuente": "Udalmap (api.euskadi.eus) indicadores 8, 10, 13 (paro Lanbide) y 50 (ocupacion juvenil)",
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_municipios": len(registros_out),
            "n_con_datos": sum(1 for r in registros_out if r["tasa_actividad_pct"] is not None),
        },
    )

    columnas = ["codigo_ine", "nombre_canonico", "territorio", "tasa_actividad_pct", "tasa_ocupacion_pct",
                "tasa_paro_aprox_pct", "tasa_paro_lanbide_pct", "tasa_ocupacion_juvenil_16_24_pct",
                "etxebide_solicitudes_por_mil", "etxebide_adjudicadas_por_100",
                "vpo_adjudicadas_por_mil", "vpo_terminadas_por_mil", "licencias_nueva_por_mil",
                "trabaja_fuera_pct", "afiliacion_ss_16_24_pct",
                "renta_familiar_eur", "renta_personal_total_eur", "renta_personal_disponible_eur",
                "renta_trabajo_pct", "superficie_media_m2", "antiguedad_media_anyos",
                "cert_energetico_por_mil", "suelo_urbanizable_pct", "anio_fuente"]
    destino_csv = RAW_DIR / "udalmap_empleo.csv"
    with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(registros_out)
    log.info("CSV -> %s", destino_csv.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())