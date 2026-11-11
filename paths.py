"""Rutas canónicas del proyecto.

Único lugar que resuelve ``DATA_DIR``. El valor de ``.env`` se interpreta
siempre relativo a la raíz del proyecto, nunca al directorio desde el que se
lanza el script, para que ``python extract/foo.py`` y ``python -m extract.foo``
apunten al mismo sitio.

Por defecto los datos viven fuera del repositorio, en ``../data_nuevo``.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_DATA_DIR = "../data_nuevo"


def _load_env() -> None:
    """Carga ``.env`` sin depender de python-dotenv."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_env()


def _resolve_data_dir() -> Path:
    raw = os.getenv("DATA_DIR") or DEFAULT_DATA_DIR
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


DATA_DIR = _resolve_data_dir()
RAW_DIR = DATA_DIR / "raw"
PROCESADO_DIR = DATA_DIR / "procesado"
RESULTADOS_DIR = DATA_DIR / "resultados"


def ensure_dirs() -> None:
    """Crea las tres capas. Solo lo llama el comando que va a escribir."""
    for directorio in (RAW_DIR, PROCESADO_DIR, RESULTADOS_DIR):
        directorio.mkdir(parents=True, exist_ok=True)
