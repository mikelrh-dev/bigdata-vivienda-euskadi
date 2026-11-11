"""Utilidades compartidas por los tests del pipeline."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    """Carga un fichero .py por ruta y lo registra en ``sys.modules``.

    Registrarlo antes de ejecutarlo evita los fallos de ``@dataclass`` cuando
    el módulo no pertenece a un paquete importable.
    """
    path = (ROOT / relative_path).resolve()
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se puede cargar {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
