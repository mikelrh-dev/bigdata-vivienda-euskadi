"""Deduplica data/procesado/alquiler_municipal_enriquecido.csv (253 -> 252).

Elimina filas duplicadas por (codigo_ine, renta_media_eur_m2_media,
cuantia_media_eur_mes_media, superficie_media_m2_media), conservando la
primera ocurrencia. Actualiza tambien el JSON equivalente.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "procesado"
CSV_PATH = PROC / "alquiler_municipal_enriquecido.csv"
JSON_PATH = PROC / "alquiler_municipal_enriquecido.json"


def _clave(fila: dict) -> tuple:
    return (
        fila.get("codigo_ine"),
        fila.get("renta_media_eur_m2_media"),
        fila.get("cuantia_media_eur_mes_media"),
        fila.get("superficie_media_m2_media"),
    )


def deduplicar_filas(filas: list[dict]) -> list[dict]:
    vistas: set = set()
    resultado: list[dict] = []
    for f in filas:
        k = _clave(f)
        if k in vistas:
            continue
        vistas.add(k)
        resultado.append(f)
    return resultado


def main() -> int:
    # CSV
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        filas = list(reader)
    antes = len(filas)
    filas = deduplicar_filas(filas)
    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    print(f"CSV: {antes} -> {len(filas)}")

    # JSON
    if JSON_PATH.exists():
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        datos = data.get("datos", [])
        antes_j = len(datos)
        datos = deduplicar_filas(datos)
        data["datos"] = datos
        if isinstance(data.get("metadata"), dict):
            data["metadata"]["n_registros"] = len(datos)
            data["metadata"]["n_municipios"] = len({d.get("codigo_ine") for d in datos})
        JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON: {antes_j} -> {len(datos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())