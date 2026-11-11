"""Informe 1x1 del scraping dirigido de Pisos.com (F4c), derivado del raw.

Genera ``data/procesado/f4_pisos_informe.csv`` con una fila por municipio
objetivo (``codigo_ine, municipio, estado``), contando los anuncios de los
lotes ``data/raw/anuncios_pisos_dirigido_*.json``.

El informe historico lo escribia el propio scraper con el resultado de cada
intento (OK/FALLO y total del portal), asi que no era reproducible desde raw.
Este paso lo sustituye por una derivacion determinista: usa la misma
convencion que el informe de Fotocasa (``n=0`` cuando no hay lote) y deja el
log de intentos donde corresponde, en la metadata del lote de raw.

Nada del pipeline lee este CSV: es evidencia de cobertura del scraping.
"""
from __future__ import annotations

import csv
import glob
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "procesado")
RAW = os.path.join(BASE, "data", "raw")


def _objetivos() -> list[str]:
    path = os.path.join(PROC, "f4_pisos_objetivo.json")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return [str(c).zfill(5) for c in json.loads(open(path, encoding="utf-8").read())]


def _conteo_por_municipio() -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in sorted(glob.glob(os.path.join(RAW, "anuncios_pisos_dirigido_*.json"))):
        try:
            data = json.loads(open(path, encoding="utf-8").read())
        except Exception:
            continue
        anuncios = data.get("datos", data) if isinstance(data, dict) else data
        if not isinstance(anuncios, list):
            continue
        for a in anuncios:
            if not isinstance(a, dict):
                continue
            cod = a.get("codigo_ine_forzado") or a.get("codigo_ine")
            if cod:
                cod = str(cod).zfill(5)
                counts[cod] = counts.get(cod, 0) + 1
    return counts


def _nombres() -> dict[str, str]:
    dim_path = os.path.join(RAW, "dim_municipios.json")
    if not os.path.exists(dim_path):
        return {}
    dim = json.loads(open(dim_path, encoding="utf-8").read())
    regs = dim.get("datos", dim) if isinstance(dim, dict) else dim
    return {r["codigo_ine"]: r["nombre_canonico"] for r in regs}


def main() -> int:
    try:
        objetivos = _objetivos()
    except FileNotFoundError as exc:
        print(f"[ERROR] No existe {exc}. Ejecuta antes generar_f4_pisos_objetivo.py.")
        return 1

    counts = _conteo_por_municipio()
    nombres = _nombres()
    filas = []
    for cod in sorted(objetivos):
        n = counts.get(cod, 0)
        estado = f"OK n={n}" if n else "sin_anuncios"
        filas.append({"codigo_ine": cod, "municipio": nombres.get(cod, cod), "estado": estado})

    out_path = os.path.join(PROC, "f4_pisos_informe.csv")
    with open(out_path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["codigo_ine", "municipio", "estado"])
        w.writeheader()
        w.writerows(filas)
    con_datos = sum(1 for f in filas if not f["estado"].startswith("sin_"))
    print(f"[OK] {out_path}: {len(filas)} objetivos ({con_datos} con anuncios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
