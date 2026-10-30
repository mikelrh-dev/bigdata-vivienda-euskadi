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


EXCLUDED_FROM_MANIFEST = {
    ".FROZEN",
    ".gitkeep",
    "ingestion_manifest.json",
    "manifest_sha256.txt",  # copia legacy del manifiesto (auto-referencial)
}


def test_raw_manifest_complete():
    """Todo fichero de data/raw (salvo excepciones) esta en el manifest."""
    lines = [ln for ln in MANIFEST.read_text(encoding="utf-8").splitlines() if ln.strip()]
    listed = set()
    for ln in lines:
        parts = ln.split(None, 1)
        if len(parts) != 2:
            continue
        ruta_rel = parts[1].lstrip("*").strip().lstrip()
        listed.add(ruta_rel)
    actual = set()
    for p in RAW.rglob("*"):
        if not p.is_file():
            continue
        if p.name in EXCLUDED_FROM_MANIFEST:
            continue
        actual.add(str(p.relative_to(RAW)).replace("\\", "/"))
    missing = actual - listed
    extra = listed - actual
    assert not missing, "ficheros sin listar en manifest:\n" + "\n".join(sorted(missing))
    assert not extra, "ficheros listados que no existen:\n" + "\n".join(sorted(extra))


def test_raw_guard_reason():
    """assert_raw_writable valida el reason (no escribe nada)."""
    import sys
    if str(ROOT / "transform") not in sys.path:
        sys.path.insert(0, str(ROOT / "transform"))
    from _raw_guard import assert_raw_writable
    assert_raw_writable("test ok")
    with pytest.raises(ValueError):
        assert_raw_writable("")
    with pytest.raises(ValueError):
        assert_raw_writable(None)
    with pytest.raises(ValueError):
        assert_raw_writable("   ")
