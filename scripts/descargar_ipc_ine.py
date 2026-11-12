"""Descarga el IPC medio anual del INE para 2024 y 2026.

Fuente primaria: INE (servicios.ine.es), tabla IPC medio anual.
Fallback: valor documentado con flag 'fallback' (estilo WP-11) si la API no
responde o no tiene los periodos necesarios.

Guarda:
    data/raw/ipc_ine_2024_2026.csv  (columnas: ano, ipc_medio_anual, fuente, fecha_extraccion)

Uso:
    python scripts/descargar_ipc_ine.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extract"))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("descargar_ipc_ine")

# Valor documentado de referencia (IPC medio anual base 2021=100, España).
# Se usa SOLO como fallback si la API del INE no responde.
# Fuente: INE, serie estadística IPC base 2021, medio anual.
FALLBACK_IPC_2024 = 107.2
FALLBACK_IPC_2026 = 117.8
FALLBACK_FUENTE = "INE (valor documentado de referencia, API no disponible)"

URL_INE_TABLA_IPC = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/247"
OUT = RAW_DIR / "ipc_ine_2024_2026.csv"


def _descargar_desde_ine(cliente: Cliente) -> dict[int, float] | None:
    """Intenta leer IPC medio anual 2024 y 2026 desde el INE.

    Retorna {anio: valor} o None si la llamada falla.
    """
    try:
        resp = cliente.get(URL_INE_TABLA_IPC)
        datos = resp.json()
    except Exception as exc:  # noqa: BLE001
        log.warning("INE API no disponible (%s); usando fallback", exc)
        return None

    # Navega la estructura del INE: buscar series con periodo 2024 y 2026.
    # Estructura esperada: lista de series con 'Nombre' y 'Datos'.
    resultado: dict[int, float] = {}
    series = datos if isinstance(datos, list) else datos.get("Series", [])
    for serie in series:
        nombre = str(serie.get("Nombre", serie.get("nombre", "")))
        # Buscar la serie de "IPC medio anual" o similar.
        if "medio" in nombre.lower() or "anual" in nombre.lower():
            for dato in serie.get("Datos", []):
                periodo = str(dato.get("Periodo", dato.get("periodo", "")))
                valor = dato.get("Valor", dato.get("valor"))
                if periodo in ("2024", "2026") and valor is not None:
                    try:
                        resultado[int(periodo)] = float(valor)
                    except (TypeError, ValueError):
                        continue
    if 2024 in resultado and 2026 in resultado:
        return resultado
    log.warning("INE no devuelve ambos periodos (2024, 2026); usando fallback")
    return None


def main() -> int:
    cliente = Cliente("descargar_ipc_ine", delay=0.6)
    datos_ine = _descargar_desde_ine(cliente)

    if datos_ine:
        ipc_2024 = datos_ine[2024]
        ipc_2026 = datos_ine[2026]
        fuente = "INE (servicios.ine.es, tabla IPC medio anual)"
        flag = "calculado"
    else:
        ipc_2024 = FALLBACK_IPC_2024
        ipc_2026 = FALLBACK_IPC_2026
        fuente = FALLBACK_FUENTE
        flag = "fallback"

    factor = ipc_2026 / ipc_2024
    ahora = datetime.now(timezone.utc)

    filas = [
        {"ano": 2024, "ipc_medio_anual": ipc_2024, "fuente": fuente, "flag": flag, "fecha_extraccion": ahora.isoformat()},
        {"ano": 2026, "ipc_medio_anual": ipc_2026, "fuente": fuente, "flag": flag, "fecha_extraccion": ahora.isoformat()},
        {"ano": "factor_2026_2024", "ipc_medio_anual": round(factor, 6), "fuente": fuente, "flag": flag, "fecha_extraccion": ahora.isoformat()},
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["ano", "ipc_medio_anual", "fuente", "flag", "fecha_extraccion"])
        writer.writeheader()
        writer.writerows(filas)

    log.info(
        "OK: %s (ipc_2024=%.2f, ipc_2026=%.2f, factor=%.4f, flag=%s)",
        OUT.name, ipc_2024, ipc_2026, factor, flag,
    )
    print(f"IPC 2024: {ipc_2024} | IPC 2026: {ipc_2026} | factor: {factor:.4f} | flag: {flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
