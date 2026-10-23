"""Extracción de la API de Eustat (Banco de Datos / bankupx).

La API funciona así:
  GET  /{ID_PX}        → metadatos (variables y valores)
  POST /{ID_PX}        → datos completos (JSON)

Tablas descargadas (verificadas):
  PX_010154_cepv1_ep06b.px   Población por municipio y grupo de edad
  PX_173402_crpf_rpf_rp11s.px Renta personal media por municipio (€)
  PX_173402_crpf_rpf_rp03.px  Renta personal media por edad y tipo (€)
  PX_170120_cpibmun_pibmun03b.px PIB por municipio
  PX_122404_cemv_viv09a.px   Viviendas por régimen de tenencia

Uso:
  python extract/01_eustat_api.py
  python extract/01_eustat_api.py --tabla renta_municipal
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    RAW_DIR,
    Cliente,
    get_logger,
    guardar_json,
)

log = get_logger("eustat_api")

BASE_URL = "https://www.eustat.eus/bankupx/api/v1/es/DB"

TABLAS = {
    "poblacion_edad": "PX_010154_cepv1_ep06b.px",
    "renta_municipal": "PX_173402_crpf_rpf_rp11s.px",
    "renta_edad": "PX_173402_crpf_rpf_rp03.px",
    "pib_municipal": "PX_170120_cpibmun_pibmun03b.px",
    "tenencia": "PX_122404_cemv_viv09a.px",
}


def obtener_metadatos(cliente: Cliente, tabla_id: str) -> dict:
    """GET → título, variables y valores con sus etiquetas."""
    url = f"{BASE_URL}/{tabla_id}"
    resp = cliente.get(url)
    meta = resp.json()
    log.info("Metadatos de %s: %s", tabla_id, meta.get("title", "")[:70])
    return meta


def obtener_datos(cliente: Cliente, tabla_id: str) -> dict:
    """POST con query vacía → todos los datos de la tabla."""
    url = f"{BASE_URL}/{tabla_id}"
    cuerpo = {"query": [], "response": {"format": "json"}}
    resp = cliente.post(url, json=cuerpo)
    datos = resp.json()
    columnas = datos.get("columns", [])
    filas = datos.get("data", [])
    log.info(
        "%s → %d columnas, %d filas",
        tabla_id, len(columnas), len(filas),
    )
    return datos


def _mapear_valores(meta: dict) -> dict[str, dict[str, str]]:
    """Construye {variable: {codigo: etiqueta}} a partir de los metadatos."""
    mapa: dict[str, dict[str, str]] = {}
    for var in meta.get("variables", []):
        codigos = var.get("values", [])
        etiquetas = var.get("valueTexts", [])
        mapa[var["code"]] = {
            codigo: etiquetas[i] if i < len(etiquetas) else codigo
            for i, codigo in enumerate(codigos)
        }
    return mapa


def tabla_a_filas(meta: dict, datos: dict) -> list[dict]:
    """Convierte la respuesta {key:[], values:[]} en filas de diccionarios
    ya traducidas con las etiquetas de cada variable."""
    columnas = [c["code"] for c in datos.get("columns", [])]
    mapa = _mapear_valores(meta)
    filas = []
    for registro in datos.get("data", []):
        valores = registro.get("key", []) + registro.get("values", [])
        fila = {}
        for columna, valor in zip(columnas, valores):
            fila[columna] = valor
            etiqueta = mapa.get(columna, {}).get(str(valor))
            if etiqueta and etiqueta != valor:
                fila[f"{columna}__etiqueta"] = etiqueta
        filas.append(fila)
    return filas


def guardar_csv(filas: list[dict], destino: Path, columnas: list[str]) -> None:
    if not filas:
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8-sig") as fh:
        escritor = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(filas)
    log.info("CSV → %s (%d filas)", destino.name, len(filas))


def extraer_tabla(cliente: Cliente, clave: str, tabla_id: str) -> dict:
    meta = obtener_metadatos(cliente, tabla_id)
    datos = obtener_datos(cliente, tabla_id)
    filas = tabla_a_filas(meta, datos)

    # JSON con metadatos + datos en bruto + filas traducidas
    salida_json = RAW_DIR / f"eustat_{clave}.json"
    guardar_json(
        salida_json,
        {
            "tabla_id": tabla_id,
            "titulo": meta.get("title"),
            "variables": [
                {
                    "code": v["code"],
                    "text": v.get("text"),
                    "values": v.get("values"),
                    "valueTexts": v.get("valueTexts"),
                }
                for v in meta.get("variables", [])
            ],
            "columnas": datos.get("columns"),
            "filas": filas,
        },
        metadata={
            "fuente": "Eustat bankupx API",
            "url": f"{BASE_URL}/{tabla_id}",
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_filas": len(filas),
        },
    )

    # CSV legible (solo columnas con etiqueta = las categóricas)
    if filas:
        columnas = list(filas[0].keys())
        guardar_csv(filas, RAW_DIR / f"eustat_{clave}.csv", columnas)

    return {"clave": clave, "filas": len(filas), "json": str(salida_json)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Extracción de Eustat")
    parser.add_argument(
        "--tabla",
        choices=list(TABLAS) + ["todas"],
        default="todas",
        help="Tabla a descargar (por defecto: todas)",
    )
    args = parser.parse_args()

    cliente = Cliente("eustat_api", delay=0.6)
    claves = list(TABLAS) if args.tabla == "todas" else [args.tabla]

    resultados = []
    for clave in claves:
        try:
            resultados.append(extraer_tabla(cliente, clave, TABLAS[clave]))
        except Exception as exc:  # noqa: BLE001
            log.error("Fallo en %s: %s", clave, exc)

    log.info("Resumen: %s", json.dumps(resultados, ensure_ascii=False))
    return 0 if resultados else 1


if __name__ == "__main__":
    raise SystemExit(main())
