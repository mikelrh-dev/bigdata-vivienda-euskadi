"""Rutas y utilidades compartidas por los scripts de análisis.

Reexporta las rutas canónicas de ``paths.py`` para que ningún script de
``analysis/`` vuelva a componer ``data/procesado`` o ``data/resultados`` a mano.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import (  # noqa: E402
    DATA_DIR,
    PROCESADO_DIR,
    RAW_DIR,
    RESULTADOS_DIR,
    ensure_dirs,
)

__all__ = [
    "DATA_DIR",
    "PROCESADO_DIR",
    "PROJECT_ROOT",
    "RAW_DIR",
    "RESULTADOS_DIR",
    "ensure_dirs",
]
