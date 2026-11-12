"""Rutas y utilidades compartidas por los scripts de transformación.

Reexporta las rutas canónicas de ``paths.py`` para que ningún script de
``transform/`` vuelva a componer ``data/raw`` o ``data/procesado`` a mano.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import (  # noqa: E402
    DATA_DIR,
    PROCESADO_DIR,
    RAW_DIR,
)

__all__ = [
    "DATA_DIR",
    "PROCESADO_DIR",
    "RAW_DIR",
    "get_logger",
    "guardar_json",
    "leer_csv_seguro",
]


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def leer_csv_seguro(path, **kwargs):
    """``read_csv`` con dtype=str, utf-8-sig y ``codigo_ine`` a 5 dígitos."""
    import pandas as pd

    kwargs.setdefault("dtype", str)
    kwargs.setdefault("encoding", "utf-8-sig")
    kwargs.setdefault("low_memory", False)
    df = pd.read_csv(Path(path), **kwargs)
    if "codigo_ine" in df.columns:
        df["codigo_ine"] = df["codigo_ine"].astype(str).str.strip().str.zfill(5)
    return df


def guardar_json(destino: Path, datos, metadata: dict | None = None) -> Path:
    """Escribe ``{"metadata": ..., "datos": ...}`` en UTF-8."""
    from datetime import datetime

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    meta = dict(metadata or {})
    if isinstance(datos, list):
        meta.setdefault("n_registros", len(datos))
    meta.setdefault(
        "fecha_extraccion",
        datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    destino.write_text(
        json.dumps({"metadata": meta, "datos": datos}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return destino
