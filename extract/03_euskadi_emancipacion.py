"""Descarga del CSV de indicadores de emancipación juvenil (Gobierno Vasco).

Fuente:
  https://www.euskadi.eus/contenidos/estadistica/gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv

Contenido (867 filas, datos hasta 2024):
  - Tasa de emancipación y edad media de emancipación
  - Coste de acceso a la vivienda libre en alquiler y en propiedad,
    por grupo de edad (18-24, 25-29, 30-34) y territorio histórico
  - Sobreesfuerzo económico (hipoteca/renta)
  - Jóvenes inscritos en Etxebide

Uso:
  python extract/03_euskadi_emancipacion.py
"""

from __future__ import annotations

import csv
import io
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("euskadi_emancipacion")

URL = (
    "https://www.euskadi.eus/contenidos/estadistica/"
    "gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv"
)


def main() -> int:
    cliente = Cliente("euskadi_emancipacion")

    resp = cliente.get(URL)
    texto = resp.content.decode("utf-8-sig", errors="replace")

    destino = RAW_DIR / "emancipacion_juventud.csv"
    destino.write_text(texto, encoding="utf-8")
    log.info("Guardado %s (%.1f KB)", destino.name, len(texto) / 1024)

    # Resumen de los indicadores disponibles
    filas = list(csv.reader(io.StringIO(texto), delimiter=";", quotechar='"'))
    indicadores = Counter(
        fila[0].strip() for fila in filas[1:] if fila and fila[0].strip()
    )
    annos = sorted(
        {fila[1].strip() for fila in filas[1:] if len(fila) > 1 and fila[1].strip()}
    )

    log.info("Indicadores distintos: %d", len(indicadores))
    for nombre, cuenta in indicadores.most_common():
        log.info("  [%3d] %s", cuenta, nombre[:80])
    log.info("Años: %s", annos)

    guardar_json(
        RAW_DIR / "emancipacion_juventud_resumen.json",
        {
            "url": URL,
            "n_filas": len(filas) - 1,
            "anno_min": annos[0] if annos else None,
            "anno_max": annos[-1] if annos else None,
            "indicadores": dict(indicadores),
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
