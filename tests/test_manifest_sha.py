"""Manifest SHA-256 con tmp_path (transform/quality/generar_manifest.py).

Genera un arbol raw sintetico en tmp_path con .FROZEN y
ingestion_manifest.json, ejecuta _escribir/_verificar del modulo y
aserta: sha256 correcto, excluidos fuera del manifiesto y que
_verificar detecta un cambio de contenido (mismatch).
Sin tocar data/raw ni data/resultados reales.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "generar_manifest", ROOT / "transform" / "quality" / "generar_manifest.py")
assert _spec is not None and _spec.loader is not None
gm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gm)


def _arbol(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "a.csv").write_bytes(b"col1,col2\n1,2\n")
    (raw / "b.json").write_bytes(b'{"k": 1}')
    (raw / ".FROZEN").write_bytes(b"")
    (raw / ".gitkeep").write_bytes(b"")
    (raw / "ingestion_manifest.json").write_bytes(b"{}")
    (raw / "manifest_sha256.txt").write_bytes(b"legacy")
    return raw


def test_sha256_correcto(tmp_path):
    """_sha256 coincide con hashlib.sha256 del contenido."""
    raw = _arbol(tmp_path)
    esperado = hashlib.sha256(b"col1,col2\n1,2\n").hexdigest()
    assert gm._sha256(raw / "a.csv") == esperado


def test_generar_y_verificar_ok(tmp_path):
    """_escribir genera manifiesto y _verificar retorna 0."""
    raw = _arbol(tmp_path)
    manifiesto = tmp_path / "manifest_sha256.txt"
    assert gm._escribir(manifiesto, raw) == 0
    assert gm._verificar(manifiesto, raw) == 0
    # El manifiesto contiene el sha correcto de a.csv
    texto = manifiesto.read_text(encoding="utf-8")
    sha_a = hashlib.sha256(b"col1,col2\n1,2\n").hexdigest()
    assert f"{sha_a}  a.csv" in texto or f"{sha_a}  a.csv\r" in texto


def test_excluidos_fuera(tmp_path):
    """Excluidos (.FROZEN, .gitkeep, ingestion_manifest.json, manifest_sha256.txt) no aparecen."""
    raw = _arbol(tmp_path)
    manifiesto = tmp_path / "manifest_sha256.txt"
    gm._escribir(manifiesto, raw)
    texto = manifiesto.read_text(encoding="utf-8")
    for nombre in (".FROZEN", ".gitkeep", "ingestion_manifest.json",
                   "manifest_sha256.txt"):
        assert nombre not in texto, nombre
    # Solo a.csv y b.json
    lineas = [ln for ln in texto.splitlines() if ln.strip()]
    assert len(lineas) == 2


def test_mismatch_detecta_cambio(tmp_path):
    """Tras modificar un fichero, _verificar retorna 1."""
    raw = _arbol(tmp_path)
    manifiesto = tmp_path / "manifest_sha256.txt"
    gm._escribir(manifiesto, raw)
    assert gm._verificar(manifiesto, raw) == 0
    (raw / "a.csv").write_bytes(b"col1,col2\n9,9\n")
    assert gm._verificar(manifiesto, raw) == 1


def test_verificar_sobra_y_falta(tmp_path):
    """Fichero nuevo no listado o borrado tambien fallan (exit 1)."""
    raw = _arbol(tmp_path)
    manifiesto = tmp_path / "manifest_sha256.txt"
    gm._escribir(manifiesto, raw)
    (raw / "nuevo.csv").write_bytes(b"x\n")
    assert gm._verificar(manifiesto, raw) == 1
    (raw / "nuevo.csv").unlink()
    (raw / "b.json").unlink()
    assert gm._verificar(manifiesto, raw) == 1
    # Manifiesto inexistente -> 1
    assert gm._verificar(tmp_path / "no_existe.txt", raw) == 1
