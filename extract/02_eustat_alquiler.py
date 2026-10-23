"""Extracción del precio del alquiler municipal (Eustat).

Esta tabla NO está en la API JSON de bankupx: solo se descarga por el
endpoint ExtractorBlob, en formato CSV o XLSX.

URL base:
  https://es.eustat.eus/comun/ExtractorBlob.ashx?id=alquiler_vivienda~N/tbl_XXXXXX_c.csv

Contenido (año 2024, cubre Álava, Bizkaia y Gipuzkoa):
  - Renta media (€/m²/mes): media, mediana, percentil 25 y 75
  - Cuantía media del arrendamiento (€/mes)
  - Superficie construida media (m²)

Uso:
  python extract/02_eustat_alquiler.py
"""

from __future__ import annotations

import csv
import io
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("eustat_alquiler")

BASE = "https://es.eustat.eus/comun/ExtractorBlob.ashx"

TABLAS = {
    "territorial": "alquiler_vivienda~1/tbl_0024627_c.csv",
    "municipio": "alquiler_vivienda~2/tbl_0024628_c.csv",
    "distrito_seccion": "alquiler_vivienda~3/tbl_0024629_c.csv",
    "seccion_a": "alquiler_vivienda~3/tbl_0024630_c.csv",
    "seccion_b": "alquiler_vivienda~3/tbl_0024631_c.csv",
}

# Columnas del CSV municipal (estructura de 13 columnas)
COLUMNAS = [
    "municipio",
    "distrito",
    "renta_media_eur_m2_media",
    "renta_media_eur_m2_mediana",
    "renta_media_eur_m2_p25",
    "renta_media_eur_m2_p75",
    "cuantia_media_eur_mes_media",
    "cuantia_media_eur_mes_mediana",
    "cuantia_media_eur_mes_p25",
    "cuantia_media_eur_mes_p75",
    "superficie_media_m2_media",
    "superficie_media_m2_mediana",
    "superficie_media_m2_p25",
    "superficie_media_m2_p75",
]


def _a_numero(valor: str) -> float | None:
    """Convierte '10,6' en 10.6; devuelve None si no es numérico."""
    if valor is None:
        return None
    limpio = valor.strip().replace(".", "").replace(",", ".")
    if limpio in ("", "..", "-"):
        return None
    try:
        return float(limpio)
    except ValueError:
        return None


def parsear_municipal(texto: str) -> list[dict]:
    """Interpreta el CSV municipal.

    Estructura real:
      fila 0  → título de la tabla
      fila 2  → cabeceras de grupo
      fila 3  → Media / Mediana / Percentil 25 / Percentil 75
      fila 4  → 'Municipio' | 'Distrito' | ...
      filas + → datos, con secciones por territorio histórico
    """
    filas = list(csv.reader(io.StringIO(texto), delimiter=";", quotechar='"'))

    registros: list[dict] = []
    territorio = ""
    municipio = ""

    for fila in filas[5:]:
        if len(fila) < 3:
            continue

        col0 = fila[0].strip()
        col1 = fila[1].strip() if len(fila) > 1 else ""

        # Línea de territorio histórico (nombre sin código de distrito)
        if col0 and not col1:
            territorio = col0
            continue

        # Línea de municipio (trae nombre y distrito)
        if col0 and col1:
            municipio = col0
        elif not col0 and not col1:
            continue  # fila vacía

        if not municipio:
            continue

        valores = fila[1:]  # quitamos la columna de nombre
        if len(valores) < 13:
            valores += [""] * (13 - len(valores))

        registro = {
            "territorio": territorio,
            "municipio": municipio,
            "distrito": valores[0].strip(),
        }
        # valores[0] = distrito; valores[1:13] = las 12 métricas
        for nombre, valor in zip(COLUMNAS[2:], valores[1:]):
            registro[nombre] = _a_numero(valor)
        registros.append(registro)

    return registros


def main() -> int:
    cliente = Cliente("eustat_alquiler", delay=0.6)
    resultados = []

    for clave, recurso in TABLAS.items():
        url = f"{BASE}?id={recurso}"
        try:
            resp = cliente.get(url)
            texto = resp.content.decode("utf-8-sig", errors="replace")

            # Guardar siempre el original tal cual
            destino = RAW_DIR / f"alquiler_{clave}_original.csv"
            destino.write_text(texto, encoding="utf-8")
            log.info("Original guardado: %s (%.1f KB)", destino.name, len(texto) / 1024)

            if clave == "municipio":
                registros = parsear_municipal(texto)
                if registros:
                    guardar_json(
                        RAW_DIR / "alquiler_municipal.json",
                        registros,
                        metadata={
                            "fuente": "Eustat ExtractorBlob",
                            "url": url,
                            "anno": 2024,
                            "fecha_extraccion": datetime.now().isoformat(
                                timespec="seconds"
                            ),
                            "n_registros": len(registros),
                        },
                    )
                    columnas = list(registros[0].keys())
                    destino_csv = RAW_DIR / "alquiler_municipal.csv"
                    with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
                        escritor = csv.DictWriter(fh, fieldnames=columnas)
                        escritor.writeheader()
                        escritor.writerows(registros)
                    log.info(
                        "CSV limpio → %s (%d registros)", destino_csv.name, len(registros)
                    )
                    resultados.append({"tabla": clave, "registros": len(registros)})
                else:
                    log.warning("No se parsearon registros de %s", clave)
            else:
                resultados.append({"tabla": clave, "bytes": len(texto)})

        except Exception as exc:  # noqa: BLE001
            log.error("Fallo en %s (%s): %s", clave, url, exc)

    log.info("Resumen: %s", resultados)
    return 0 if resultados else 1


if __name__ == "__main__":
    raise SystemExit(main())
