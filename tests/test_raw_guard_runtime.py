"""_raw_guard runtime con tmp_path (transform/_raw_guard.py).

assert_raw_writable: sin marcador .FROZEN lanza RawFrozenMissing,
con .FROZEN y reason no vacio pasa, y la intencion queda en el
audit_log (en tmp_path, nunca en logs/ real). Reason vacio lanza
ValueError. Sin tocar data/raw real.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "_raw_guard", ROOT / "transform" / "_raw_guard.py")
assert _spec is not None and _spec.loader is not None
rg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rg)


@pytest.fixture()
def guard_tmp(tmp_path, monkeypatch):
    """Apunta FROZEN_MARKER y TODOS los audit logs a tmp_path."""
    raw = tmp_path / "raw"
    raw.mkdir()
    audit = tmp_path / "audit.log"
    for nombre in ("AUDIT_LOG", "AUDIT_LOG_PATH", "AUDIT_LOG_FILE",
                   "LOG_PATH", "LOG_FILE", "AUDIT_FILE"):
        monkeypatch.setattr(rg, nombre, audit)
    monkeypatch.setattr(rg, "AUDIT_LOG_PATHS", [audit])
    monkeypatch.setattr(rg, "FROZEN_MARKER", raw / ".FROZEN")
    monkeypatch.setattr(rg, "RAW_DIR", raw)
    monkeypatch.setenv("RAW_GUARD_AUDIT_LOG", str(audit))
    return raw, audit


def test_sin_frozen_lanza(guard_tmp):
    """Sin .FROZEN (tmp) -> RawFrozenMissing aunque haya reason."""
    _raw, _audit = guard_tmp
    with pytest.raises(rg.RawFrozenMissing):
        rg.assert_raw_writable("intento sin congelar")


def test_con_frozen_ok(guard_tmp):
    """Con .FROZEN y reason no vacio -> no lanza."""
    raw, _audit = guard_tmp
    (raw / ".FROZEN").write_bytes(b"")
    rg.assert_raw_writable("razon valida de escritura raw")  # no debe lanzar


def test_audit_log_se_escribe(guard_tmp):
    """La intencion queda registrada en el audit_log de tmp_path."""
    raw, audit = guard_tmp
    (raw / ".FROZEN").write_bytes(b"")
    rg.assert_raw_writable("auditar esta escritura concreta 123")
    assert audit.exists()
    texto = audit.read_text(encoding="utf-8")
    assert "auditar esta escritura concreta 123" in texto
    assert "raw_guard" in texto


@pytest.mark.parametrize("reason", ["", "   ", None, 123])
def test_reason_vacio_lanza_valueerror(guard_tmp, reason):
    """Reason vacio/no-string -> ValueError (antes de mirar .FROZEN)."""
    raw, _audit = guard_tmp
    (raw / ".FROZEN").write_bytes(b"")
    with pytest.raises(ValueError):
        rg.assert_raw_writable(reason)
