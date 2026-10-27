"""Extracción de salarios (INE, Encuesta de Población Activa).

Tablas usadas (API abierta, sin registro):
  66239  Salarios medios por tipo de jornada, grupo de edad y decil
  66252  Salarios medios y límite inferior de cada decil

MATIZ IMPORTANTE: el INE publica estos datos a nivel **nacional**, sin
desglose por comunidad autónoma. Para el territorio se apoya en:
  - Renta personal media por edad de Eustat (Comunidad Autónoma)
  - Dato oficial del Observatorio Vasco de la Juventud (1.564 EUR/mes
    netos para 18-34 en 2024)

Uso:
  python extract/07_ine_salarios.py
  python extract/07_ine_salarios.py --tabla 66239
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("ine_salarios")

BASE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA"

TABLAS = {
    "66239": (
        "Salarios medios por tipo de jornada, grupo de edad y decil (EPA)"
    ),
    "66252": (
        "Salarios medios y límite inferior de cada decil (EPA)"
    ),
}

# Nombre del fichero de salida por tabla
SALIDA = {
    "66239": "ine_salarios_edad.json",
    "66252": "ine_salarios_decil.json",
}


def extraer_tabla(cliente: Cliente, tabla: str) -> list[dict]:
    url = f"{BASE_URL}/{tabla}"
    series = cliente.get(url).json()
    log.info("Tabla %s → %d series", tabla, len(series))
    return series


def serie_a_registro(serie: dict) -> dict:
    """El nombre de la serie es "Ambito. Subambito. Dato. Ámbito geográfico.
    Indicador. Tipo. Grupo de edad/decil." Se parte por puntos."""
    nombre = serie.get("Nombre", "")
    partes = [p.strip() for p in nombre.split(".")]
    ambito = partes[0] if partes else ""
    subambito = partes[1] if len(partes) > 1 else ""
    indicador = ""
    grupo = ""
    for p in partes:
        if p.lower().startswith("salario"):
            indicador = p
        if "años" in p.lower() or p.isdigit():
            grupo = p

    # Último punto con valor no nulo y no secreto
    mejor = (None, None)
    for punto in serie.get("Data", []):
        if punto.get("Valor") is None or punto.get("Secreto"):
            continue
        anyo = punto.get("Anyo")
        if anyo and (mejor[0] is None or anyo > mejor[0]):
            mejor = (anyo, punto["Valor"])

    return {
        "ambito": ambito,
        "subambito": subambito,
        "indicador": indicador,
        "grupo_edad_o_decil": grupo,
        "anyo": mejor[0],
        "valor_eur": mejor[1],
        "codigo_serie": serie.get("COD"),
        "nombre_serie": nombre,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extracción de salarios INE")
    parser.add_argument(
        "--tabla",
        choices=list(TABLAS) + ["todas"],
        default="todas",
    )
    args = parser.parse_args()

    cliente = Cliente("ine_salarios", delay=0.8)
    tablas = list(TABLAS) if args.tabla == "todas" else [args.tabla]

    for tabla in tablas:
        try:
            series = extraer_tabla(cliente, tabla)
        except Exception as exc:  # noqa: BLE001
            log.error("Tabla %s: %s", tabla, exc)
            continue

        registros = [serie_a_registro(s) for s in series]

        guardar_json(
            RAW_DIR / SALIDA[tabla],
            {
                "tabla": tabla,
                "descripcion": TABLAS[tabla],
                "n_series": len(series),
                "n_registros": len(registros),
                "ambito_geografico": "Total Nacional (sin desglose por CCAA)",
                "registros": registros,
            },
            metadata={
                "fuente": "INE wstempus API (EPA)",
                "url": f"{BASE_URL}/{tabla}",
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "n_registros": len(registros),
            },
        )

        # CSV con los registros
        destino_csv = RAW_DIR / SALIDA[tabla].replace(".json", ".csv")
        columnas = [
            "ambito", "subambito", "indicador",
            "grupo_edad_o_decil", "anyo", "valor_eur", "codigo_serie",
        ]
        with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
            escritor = csv.DictWriter(
                fh, fieldnames=columnas, extrasaction="ignore"
            )
            escritor.writeheader()
            escritor.writerows(registros)
        log.info(
            "Guardado %s (%d registros)", destino_csv.name, len(registros)
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
