"""Materializa la seleccion de municipios del scraping dirigido de Pisos.com (F4c).

La lista NO se inventa aqui: es una decision de estudio versionada en
``config/f4_pisos_objetivo.yaml`` (62 municipios). Este paso solo la valida
contra dim_municipios y la emite como artefacto silver, de modo que un rebuild
limpio reproduce exactamente la misma seleccion que uso el scraper.

Antes (hasta 2026-11-11) el script generaba una lista alternativa cuando el
fichero no existia, avisando de que podia diferir de la original: eso hacia que
el artefacto no fuese reproducible ni comparable entre ejecuciones.
"""
from __future__ import annotations

import json
import os

import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(BASE, "config", "f4_pisos_objetivo.yaml")
PROC = os.path.join(BASE, "data", "procesado")
RAW = os.path.join(BASE, "data", "raw")


def _validar(obj, nombres) -> list[str]:
    errores = []
    if not isinstance(obj, list):
        errores.append("no es una lista")
        return errores
    if not all(isinstance(x, str) for x in obj):
        errores.append("no todos los elementos son strings")
    desconocidos = [c for c in obj if c not in nombres]
    if desconocidos:
        errores.append(f"{len(desconocidos)} codigos no estan en dim_municipios: {desconocidos[:5]}")
    if len(obj) != len(set(obj)):
        errores.append("contiene duplicados")
    return errores


def _cargar_config() -> list[str]:
    if not os.path.exists(CONFIG):
        raise FileNotFoundError(CONFIG)
    datos = yaml.safe_load(open(CONFIG, encoding="utf-8")) or {}
    municipios = datos.get("municipios")
    if not isinstance(municipios, list) or not municipios:
        raise ValueError(f"{CONFIG}: falta la lista 'municipios' o esta vacia")
    return [str(c).zfill(5) for c in municipios]


def main() -> int:
    dim_path = os.path.join(RAW, "dim_municipios.json")
    if not os.path.exists(dim_path):
        print(f"[ERROR] No existe {dim_path}")
        return 1
    dim = json.loads(open(dim_path, encoding="utf-8").read())
    regs = dim.get("datos", dim) if isinstance(dim, dict) else dim
    nombres = {r["codigo_ine"]: r["nombre_canonico"] for r in regs}

    try:
        seleccion = _cargar_config()
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] Seleccion no reproducible: {exc}")
        return 1

    errores = _validar(seleccion, nombres)
    if errores:
        print("[ERROR] config/f4_pisos_objetivo.yaml invalido:", "; ".join(errores))
        return 1

    out_path = os.path.join(PROC, "f4_pisos_objetivo.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(seleccion, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"[OK] {out_path}: {len(seleccion)} codigos desde config (validados contra dim_municipios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
