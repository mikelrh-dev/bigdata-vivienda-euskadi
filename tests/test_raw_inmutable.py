"""Integridad e inmutabilidad de data/raw (regla bronce)."""
from pathlib import Path
import hashlib

import pytest

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "docs" / "raw_manifest_sha256.txt"
FROZEN = RAW / ".FROZEN"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_raw_congelado_marker():
    assert FROZEN.exists(), "data/raw no esta congelado (.FROZEN falta)"


def test_raw_hashes_manifest():
    assert MANIFEST.exists(), "Manifest canonical falta: docs/raw_manifest_sha256.txt"
    lines = [ln for ln in MANIFEST.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines, "Manifest vacio"
    errores = []
    for ln in lines:
        # formato: "<hash> *<path>" o "<hash>  <path>"
        parts = ln.split(None, 1)
        if len(parts) != 2:
            errores.append(f"linea malformada: {ln}")
            continue
        esperado, resto = parts
        ruta_rel = resto.lstrip("*").strip()
        # sha256sum puede prefijar con espacio; normalizar
        ruta_rel = ruta_rel.lstrip()
        archivo = RAW / ruta_rel
        if not archivo.exists():
            errores.append(f"falta: {ruta_rel}")
            continue
        real = _sha256(archivo)
        if real != esperado:
            errores.append(f"hash distinto: {ruta_rel}")
    assert not errores, "Integridad raw rota:\n" + "\n".join(errores)
