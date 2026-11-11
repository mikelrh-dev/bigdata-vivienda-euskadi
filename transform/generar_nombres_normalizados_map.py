"""Genera ``data/procesado/_meta/nombres_normalizados_map.json`` (WP-09).

El mapa registra los lotes raw que conservan timestamp en silver. Antes era un
JSON escrito a mano dentro de ``data/procesado`` (gitignorado): se perdia en
cualquier rebuild y `tests/test_fase_datos.py` dependia de el.

Ahora el motivo y el nombre canonico futuro viven en
``config/lotes_heredados.yaml`` (versionado) y este paso solo deriva
``nombre_actual`` del nombre del raw y comprueba que el lote sigue existiendo.
"""
from __future__ import annotations

import json
import os
import re

import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(BASE, "config", "lotes_heredados.yaml")
PROC = os.path.join(BASE, "data", "procesado")
RAW = os.path.join(BASE, "data", "raw")
META = os.path.join(PROC, "_meta")
TIMESTAMP_RE = r"_20\d{6}(_\d+)?_normalizado\.json$"

NOTA = ("Los timestamps se heredan de los lotes raw congelados (no se renombran en silver "
        "para no romper la correspondencia raw->silver; los dos lotes fotocasa_dirigido "
        "tienen distinto contenido y no son fusionables). Proceso de normalizacion: "
        "transform/normalizar_json_crudos.py (basename + _normalizado).")
POLITICA = ("WP-09: toda ingesta nueva usa nombres canonicos sin timestamp en raw y silver; "
            "este mapa registra la excepcion cerrada de los 5 lotes 2026-10-29.")


def main() -> int:
    if not os.path.exists(CONFIG):
        print(f"[ERROR] No existe {CONFIG}: el mapa no se puede derivar")
        return 1
    datos = yaml.safe_load(open(CONFIG, encoding="utf-8")) or {}
    lotes = datos.get("lotes") or []

    entradas = []
    for lote in lotes:
        origen = lote.get("origen_raw")
        futuro = lote.get("nombre_canonico_futuro")
        motivo = lote.get("motivo")
        if not (origen and futuro and motivo):
            print(f"[ERROR] Entrada incompleta en {CONFIG}: {lote}")
            return 1
        if not os.path.exists(os.path.join(RAW, origen)):
            print(f"[ERROR] El lote declarado no existe en raw: {origen}")
            return 1
        entradas.append({
            "motivo": motivo,
            "nombre_actual": os.path.splitext(origen)[0] + "_normalizado.json",
            "nombre_canonico_futuro": futuro,
            "origen_raw": origen,
        })

    # Los 5 lotes normalizados deben estar ya en silver (los produce
    # normalizar_json_crudos.py): el mapa solo tiene sentido si existen.
    faltan = [e["nombre_actual"] for e in entradas
              if not os.path.exists(os.path.join(PROC, e["nombre_actual"]))]
    if faltan:
        print(f"[ERROR] Faltan normalizados en silver: {faltan[:3]}. "
              "Ejecuta antes transform/normalizar_json_crudos.py.")
        return 1

    registrados = {e["nombre_actual"] for e in entradas}
    sin_registrar = [f for f in sorted(os.listdir(PROC))
                     if re.search(TIMESTAMP_RE, f) and f not in registrados]
    if sin_registrar:
        print(f"[WARN] Normalizados con timestamp no registrados en {CONFIG}: {sin_registrar}")

    os.makedirs(META, exist_ok=True)
    salida = {
        "ficheros_con_timestamp_heredado": entradas,
        "nota": NOTA,
        "politica": POLITICA,
    }
    destino = os.path.join(META, "nombres_normalizados_map.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(salida, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"[OK] {destino}: {len(entradas)} lotes heredados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
