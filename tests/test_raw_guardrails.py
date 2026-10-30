"""Guardrails de inmutabilidad de data/raw (cambio raw-immutability-hardening).

Sustituyen a la convención: la protección real es código + tests.
"""
from __future__ import annotations

import ast
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TRANSFORM_DIR = ROOT / "transform"
EXTRACT_DIR = ROOT / "extract"
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "procesado"

RAW_WRITE_ALLOWLIST = {
    "enriquecer_codigo_ine.py",  # solo con --write-raw --reason
    "f4_pisos_dirigido.py",      # lot dirigido append-only
}

WRITE_METHODS = {"to_csv", "to_json", "write_text", "write_bytes"}
WRITE_FUNCS = {"guardar_json", "open"}

RAW_MARKER = re.compile(
    r"""
    \bRAW_DIR\b
  | \bRAW\b
  | raw_path
  | raw_dir
  | data[/\\]raw
  | ["']data["']\s*[,/]\s*["']raw["']
    """,
    re.VERBOSE,
)


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tainted_names(tree: ast.AST) -> set[str]:
    tainted: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            if value is None:
                continue
            text = ast.unparse(value)
            raw_hit = bool(RAW_MARKER.search(text)) and not re.search(r"RAW(?:_DIR)?\.parent", text) and "procesado" not in text.lower()
            tainted_hit = any(
                isinstance(t, ast.Name) and t.id in tainted
                for t in ast.walk(value)
            )
            if not (raw_hit or tainted_hit):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tgt in targets:
                for name in ast.walk(tgt):
                    if isinstance(name, ast.Name) and name.id not in tainted:
                        tainted.add(name.id)
                        changed = True
    return tainted


def _raw_write_calls(path: Path) -> list[str]:
    src = _src(path)
    tree = ast.parse(src)
    tainted = _tainted_names(tree)
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            name = func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        else:
            continue
        if name not in WRITE_METHODS and name not in WRITE_FUNCS:
            continue
        if name == "open":
            mode = None
            if len(node.args) >= 2:
                mode = ast.unparse(node.args[1])
            for kw in node.keywords:
                if kw.arg == "mode":
                    mode = ast.unparse(kw.value)
            if not mode or not re.search(r"[wax]", mode):
                continue
        # Destino efectivo de la escritura:
        # - write_text/write_bytes -> el receptor (Path.write_text)
        # - to_csv/to_json -> el argumento filename (o el receptor si no se pasa)
        # - guardar_json/open -> el primer argumento
        targets: list[str] = []
        if name in {"write_text", "write_bytes"}:
            targets.append(ast.unparse(func.value))
        elif name in {"to_csv", "to_json"}:
            if node.args:
                targets.append(ast.unparse(node.args[0]))
        else:
            if node.args:
                targets.append(ast.unparse(node.args[0]))
        raw_tainted = False
        for target_text in targets:
            if RAW_MARKER.search(target_text) and not re.search(r"RAW(?:_DIR)?\.parent", target_text) and "procesado" not in target_text.lower():
                raw_tainted = True
                break
            if any(re.search(rf"\b{re.escape(n)}\b", target_text) for n in tainted):
                raw_tainted = True
                break
        if raw_tainted:
            shown = " | ".join(targets) if targets else "?"
            hits.append(f"linea {node.lineno}: {name} -> {shown}")
    return hits


def test_no_transform_writes_raw():
    """Ningún transform escribe en data/raw salvo lista blanca + guard."""
    offenders = []
    for path in sorted(TRANSFORM_DIR.glob("*.py")):
        if path.name.startswith("_"):
            continue
        hits = _raw_write_calls(path)
        if not hits:
            continue
        if path.name in RAW_WRITE_ALLOWLIST:
            src = _src(path)
            if "assert_raw_writable" not in src:
                offenders.append(f"{path.name}: escribe en raw sin guard: {hits}")
        else:
            offenders.append(f"{path.name}: escribe en raw sin estar en la lista blanca: {hits}")
    assert not offenders, "Transforms que escriben en data/raw:\n" + "\n".join(offenders)


def test_f4_filename_unique():
    """_nombre_lote devuelve nombre con 14 digitos + token, y dos llamadas difieren."""
    if str(TRANSFORM_DIR) not in sys.path:
        sys.path.insert(0, str(TRANSFORM_DIR))
    if str(EXTRACT_DIR) not in sys.path:
        sys.path.insert(0, str(EXTRACT_DIR))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import f4_pisos_dirigido
    p1 = f4_pisos_dirigido._nombre_lote(RAW_DIR)
    p2 = f4_pisos_dirigido._nombre_lote(RAW_DIR)
    assert p1 != p2
    assert re.match(
        r"anuncios_pisos_dirigido_\d{14}_[0-9a-f]{8}\.json", p1.name
    ), p1.name
    assert re.match(
        r"anuncios_pisos_dirigido_\d{14}_[0-9a-f]{8}\.json", p2.name
    ), p2.name


def test_geo_temp_not_tmp_root():
    """22_geo_areas_funcionales no usa /tmp y crea el temp dir."""
    src = _src(EXTRACT_DIR / "22_geo_areas_funcionales.py")
    assert "/tmp" not in src, "literal /tmp encontrado"
    spec = importlib.util.spec_from_file_location(
        "geo_areas_funcionales", EXTRACT_DIR / "22_geo_areas_funcionales.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Asegurar que extract esta en sys.path para imports internos
    if str(EXTRACT_DIR) not in sys.path:
        sys.path.insert(0, str(EXTRACT_DIR))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec.loader.exec_module(mod)
    tmp = mod.TMP
    assert tmp != Path("/tmp")
    assert tmp == Path(tempfile.gettempdir()) / "geo_areas"
    assert tmp.exists()


def test_muni_resolve_accented_slash():
    """resolver_codigo resuelve variantes con acentos/barras sin fallback difuso."""
    if str(EXTRACT_DIR) not in sys.path:
        sys.path.insert(0, str(EXTRACT_DIR))
    if str(TRANSFORM_DIR) not in sys.path:
        sys.path.insert(0, str(TRANSFORM_DIR))
    import muni_resolve

    # Fuerza el fallo del fallback difuso: si se usara, esto lanzaria.
    import difflib as _real_difflib
    class _Boom:
        def ratio(self):
            raise AssertionError("fuzzy fallback used for an exact key")
    import muni_resolve as _mr
    _mr.difflib.SequenceMatcher = lambda *a, **k: _Boom()

    code, name = muni_resolve.resolver_codigo("Donostia/San Sebastián", None)
    assert code == "20069", (code, name)
    code2, name2 = muni_resolve.resolver_codigo("Arrasate/Mondragón", None)
    assert code2 == "20055", (code2, name2)
    # El key normalizado debe existir en NAME2CODE (camino exacto).
    assert "donostia san sebastian" in muni_resolve.NAME2CODE
    assert "arrasate mondragon" in muni_resolve.NAME2CODE


def test_unificados_columns_superset():
    """Los CSV derivados del canonico conservan las 12 columnas base."""
    canonical_path = PROC_DIR / "anuncios_unificados.csv"
    assert canonical_path.exists(), "canonico ausente"
    base = list(__import__("pandas").read_csv(canonical_path, nrows=0).columns)
    assert len(base) == 13, base
    for path in PROC_DIR.glob("anuncios_unificados*.csv"):
        cols = list(__import__("pandas").read_csv(path, nrows=0).columns)
        missing = [c for c in base if c not in cols]
        assert not missing, f"{path.name} falta {missing}"
