"""Extracción de la API JSON del INE (wstempus).

URL:
  https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tabla}

Es una API abierta, sin registro, documentada en ine.es/dyngs/DAB
(incluye un wstempus.yaml con la especificación OpenAPI).

Tablas usadas:
  69301  Población residente por municipio
  69302  Hogares y viviendas
  69303  Tasa de actividad y desempleo
  69323  Indicadores Urbanos - vivienda
  69330  Indicadores Urbanos completo

LIMITACIÓN VERIFICADA: el alquiler por municipio viene a null en
Euskadi (INE no lo publica en régimen foral). Esta fuente sirve para
población, hogares y precios de compraventa.

Uso:
  python extract/06_ine_api.py
  python extract/06_ine_api.py --tabla 69301
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("ine_api")

BASE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA"

TABLAS = {
    "69301": "Población residente por municipio",
    "69302": "Hogares y viviendas",
    "69303": "Tasa de actividad y desempleo",
    "69323": "Indicadores Urbanos - vivienda",
    "69330": "Indicadores Urbanos completo",
}


def extraer_tabla(cliente: Cliente, tabla: str) -> list[dict]:
    url = f"{BASE_URL}/{tabla}"
    resp = cliente.get(url)
    series = resp.json()
    log.info("Tabla %s → %d series", tabla, len(series))
    return series


def _ultimo_valor(serie: dict) -> tuple[int | None, float | None]:
    """Último año con valor no nulo y no secreto."""
    mejor: tuple[int | None, float | None] = (None, None)
    for punto in serie.get("Data", []):
        if punto.get("Valor") is None or punto.get("Secreto"):
            continue
        anyo = punto.get("Anyo")
        if anyo and (mejor[0] is None or anyo > mejor[0]):
            mejor = (anyo, punto["Valor"])
    return mejor


def serie_a_registro(serie: dict) -> dict:
    nombre = serie.get("Nombre", "")
    partes = nombre.split(".")
    ambito = partes[0].strip()
    indicador = partes[1].strip() if len(partes) > 1 else nombre
    segmento = partes[2].strip() if len(partes) > 2 else "Total"

    anyo, valor = _ultimo_valor(serie)
    return {
        "ambito": ambito,
        "indicador": indicador,
        "segmento": segmento,
        "anyo": anyo,
        "valor": valor,
        "codigo_serie": serie.get("COD"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extracción de la API INE")
    parser.add_argument(
        "--tabla",
        choices=list(TABLAS) + ["todas"],
        default="todas",
    )
    args = parser.parse_args()

    cliente = Cliente("ine_api", delay=0.8)
    tablas = list(TABLAS) if args.tabla == "todas" else [args.tabla]

    for tabla in tablas:
        try:
            series = extraer_tabla(cliente, tabla)
        except Exception as exc:  # noqa: BLE001
            log.error("Tabla %s: %s", tabla, exc)
            continue

        registros = [serie_a_registro(s) for s in series]

        guardar_json(
            RAW_DIR / f"ine_{tabla}.json",
            {
                "tabla": tabla,
                "descripcion": TABLAS[tabla],
                "n_series": len(series),
                "n_registros": len(registros),
                "registros": registros,
                "payload_original": series,
            },
            metadata={
                "fuente": "INE wstempus API",
                "url": f"{BASE_URL}/{tabla}",
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "n_series": len(series),
                "n_registros": len(registros),
            },
        )

        # Payload original (respuesta cruda de la API) guardado aparte
        guardar_json(
            RAW_DIR / f"ine_{tabla}_raw.json",
            series,
            metadata={
                "fuente": "INE wstempus API (payload original)",
                "url": f"{BASE_URL}/{tabla}",
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "n_series": len(series),
                "n_registros": len(series),
            },
        )

        # CSV con todos los registros de la tabla
        destino_csv = RAW_DIR / f"ine_{tabla}.csv"
        with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
            columnas = ["ambito", "indicador", "segmento", "anyo", "valor", "codigo_serie"]
            escritor = csv.DictWriter(fh, fieldnames=columnas)
            escritor.writeheader()
            escritor.writerows(registros)
        log.info("CSV → %s (%d registros)", destino_csv.name, len(registros))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
