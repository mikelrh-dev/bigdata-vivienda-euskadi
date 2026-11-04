"""Entrypoint único del pipeline MongoDB: carga + limpieza + índices + agregación.

Ejecuta, sin intervención manual en MongoDB:
  1. storage.load_mongo.load_all
  2. storage.clean_mongo.clean_all
  3. analysis.mongo_indexes.ensure_indexes
  4. analysis.mongo_aggregations.pipeline_indicadores_municipio

Imprime los conteos de load_all, el total de modified_count, el total de
deleted_count y el número de indicadores.

Uso:
  python scripts/run_mongo_pipeline.py            # pipeline completo (muta prod)
  python scripts/run_mongo_pipeline.py --dry-run  # solo valida imports y ping,
                                                  # no muta producción
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.mongo_aggregations import pipeline_indicadores_municipio
from analysis.mongo_indexes import ensure_indexes
from storage.clean_mongo import clean_all
from storage.load_mongo import load_all
from storage.mongo import ping


def _sum_counter(clean_result: Any, key: str) -> int:
    """Suma recursiva de `key` en un dict anidado (modified/deleted_count)."""
    if isinstance(clean_result, dict):
        total = 0
        for k, v in clean_result.items():
            if k == key and isinstance(v, (int, float)):
                total += int(v)
            else:
                total += _sum_counter(v, key)
        return total
    if isinstance(clean_result, (list, tuple)):
        return sum(_sum_counter(item, key) for item in clean_result)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline MongoDB: carga + limpieza + índices + agregación"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo valida imports y conexión (ping); no muta producción",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.dry_run:
        # Imports ya validados al importar este módulo. Solo ping, sin mutar.
        ok = ping()
        print(f"dry-run: imports ok, ping={ok}, sin mutar producción")
        return 0 if ok else 1
    load_result = load_all()
    clean_result = clean_all()
    index_result = ensure_indexes()
    indicadores = pipeline_indicadores_municipio()
    modified_count = _sum_counter(clean_result, "modified_count")
    deleted_count = _sum_counter(clean_result, "deleted_count")
    print(f"load_all: {load_result}")
    print(f"clean_all modified_count: {modified_count}")
    print(f"clean_all deleted_count: {deleted_count}")
    print(f"ensure_indexes: {index_result}")
    print(f"indicadores: {len(indicadores)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
