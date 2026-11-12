"""Genera y verifica manifests SHA-256 de integridad (WP-08).

- Manifest canonico de raw: data/raw/manifest_sha256.txt (solo verificación aquí).
- Manifest de silver: data/procesado/manifest_sha256.txt (versionado, datos no).

Uso:
    python transform/quality/generar_manifest.py --write    # regenera manifiesto Silver
    python transform/quality/generar_manifest.py --verify   # exit 0 si todo coincide

--verify falla (exit 1) si falta algun fichero, sobra alguno no listado
o algun hash no coincide. Excluye .FROZEN, .gitkeep, ingestion_manifest.json
y el propio manifest (auto-referencial).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from paths import PROCESADO_DIR, RAW_DIR  # noqa: E402

PROC_DIR = PROCESADO_DIR
CANONICAL = RAW_DIR / "manifest_sha256.txt"
SILVER = PROC_DIR / "manifest_sha256.txt"

EXCLUIDOS = {".FROZEN", ".gitkeep", "ingestion_manifest.json", "manifest_sha256.txt"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _inventario(root: Path) -> dict[str, Path]:
    return {str(p.relative_to(root)).replace("\\", "/"): p
            for p in sorted(root.rglob("*"))
            if p.is_file() and p.name not in EXCLUIDOS}


def _leer_manifest(path: Path) -> dict[str, str]:
    man = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            h, n = ln.split(None, 1)
            man[n.lstrip("* ").strip()] = h
    return man


def _escribir(path: Path, root: Path) -> int:
    inv = _inventario(root)
    lineas = [f"{_sha256(p)}  {rel}" for rel, p in inv.items()]
    path.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"OK: {path} ({len(lineas)} entradas)")
    return 0


def _verificar(path: Path, root: Path) -> int:
    if not path.exists():
        print(f"FALTA manifest: {path}")
        return 1
    man = _leer_manifest(path)
    inv = _inventario(root)
    errores = []
    for rel in sorted(set(man) - set(inv)):
        errores.append(f"sobra en manifest (no existe): {rel}")
    for rel in sorted(set(inv) - set(man)):
        errores.append(f"falta en manifest: {rel}")
    for rel in sorted(set(man) & set(inv)):
        if _sha256(inv[rel]) != man[rel]:
            errores.append(f"hash distinto: {rel}")
    if errores:
        print(f"FALLA {path} ({len(errores)} errores):")
        for e in errores[:15]:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} ({len(man)} entradas, 0 errores)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Verifica Raw y Silver; escribe solo el manifiesto Silver.")
    ap.add_argument("--write", action="store_true", help="Regenerar solo el manifiesto Silver; no modifica Raw.")
    ap.add_argument("--verify", action="store_true", help="Verificar ambos manifests (solo lectura).")
    args = ap.parse_args()
    if args.write:
        _escribir(SILVER, PROC_DIR)
        return 0
    if args.verify:
        rc = _verificar(CANONICAL, RAW_DIR)
        rc |= _verificar(SILVER, PROC_DIR)
        return rc
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
