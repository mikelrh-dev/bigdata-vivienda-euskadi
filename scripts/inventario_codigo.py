"""Inventario del código: qué hace cada .py, carpeta por carpeta.

Lee la primera línea del docstring de cada módulo con `ast`, sin importarlo, así
que funciona con los scripts que ejecutan al importar. No versiona el resultado:
se regenera cuando haga falta, de modo que nunca queda una tabla obsoleta.

Uso:
    python scripts/inventario_codigo.py
    python scripts/inventario_codigo.py --salida inventario.md
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Orden del pipeline, no alfabético: el inventario se lee como se ejecuta.
CARPETAS = (
    ("extract", "descarga y normaliza hacia data/raw (inmutable)"),
    ("transform", "raw → data/procesado (silver y gold)"),
    ("storage", "Kafka, HDFS y carga batch a MongoDB"),
    ("analysis", "gold → data/resultados y consultas sobre Mongo"),
    ("scripts", "entry points y verificadores del contrato"),
    ("visuals", "figuras y assets de la memoria y del deck"),
    ("tests", "pytest: el contrato se comprueba aquí"),
    ("config", "parámetros y fuentes (YAML)"),
)


def docstring_de(ruta: Path) -> tuple[str, str]:
    """(primera línea del docstring, sí/no con guard) sin ejecutar el módulo."""
    try:
        tree = ast.parse(ruta.read_text(encoding="utf-8-sig"))
    except SyntaxError as exc:
        return f"ERROR de sintaxis: {exc.msg}", "?"
    doc = (ast.get_docstring(tree) or "").strip()
    primera = doc.splitlines()[0] if doc else ""
    guard = any(
        isinstance(nodo, ast.If) and "__main__" in ast.dump(nodo.test)
        for nodo in tree.body
    )
    return primera or "(sin docstring)", "sí" if guard else "no"


def tabla(nombre: str, descripcion: str) -> list[str]:
    carpeta = ROOT / nombre
    if not carpeta.is_dir():
        return []
    filas = [f"## `{nombre}/` — {descripcion}", "", "| Fichero | Qué hace | `__main__` |", "|---|---|---|"]
    for py in sorted(carpeta.glob("*.py")):
        texto, guard = docstring_de(py)
        texto = texto.replace("|", "\\|")[:110]
        filas.append(f"| `{py.name}` | {texto} | {guard} |")
    filas.append("")
    return filas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--salida", type=Path, help="escribe la tabla en este fichero en vez de stdout")
    args = parser.parse_args()

    lineas = [
        "# Inventario de código — BigData Vivienda Euskadi",
        "",
        "Generado por `scripts/inventario_codigo.py`. No editar a mano:",
        "regenerar con `python scripts/inventario_codigo.py`.",
        "",
    ]
    for nombre, descripcion in CARPETAS:
        lineas += tabla(nombre, descripcion)

    texto = "\n".join(lineas)
    if args.salida:
        args.salida.write_text(texto + "\n", encoding="utf-8")
        print(f"escrito {args.salida} ({len(lineas)} líneas)")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
