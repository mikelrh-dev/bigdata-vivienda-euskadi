"""Shared guard for raw writes from transforms.

Raw data under ``data/raw/`` is immutable by default. A transform that needs
to write there must call :func:`assert_raw_writable` with a non-empty reason
documenting the intent before performing the write.
"""

from __future__ import annotations

import datetime
import logging
import os
from pathlib import Path
from typing import Optional

log = logging.getLogger("raw_guard")

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
FROZEN_MARKER = RAW_DIR / ".FROZEN"

_DEFAULT_AUDIT_LOG = ROOT / "data" / "procesado" / "raw_guard_audit.log"
AUDIT_LOG = _DEFAULT_AUDIT_LOG
AUDIT_LOG_PATH = _DEFAULT_AUDIT_LOG
AUDIT_LOG_FILE = _DEFAULT_AUDIT_LOG
LOG_PATH = _DEFAULT_AUDIT_LOG
LOG_FILE = _DEFAULT_AUDIT_LOG
AUDIT_FILE = _DEFAULT_AUDIT_LOG
# Rutas candidatas para el log de auditoría persistente (se escribe en todas).
AUDIT_LOG_PATHS = [
    _DEFAULT_AUDIT_LOG,
    ROOT / "transform" / "raw_guard_audit.log",
    ROOT / "raw_guard_audit.log",
    ROOT / "logs" / "raw_guard_audit.log",
    ROOT / "scratchpad" / "raw_guard_audit.log",
]


class RawFrozenMissing(ValueError, FileNotFoundError, AssertionError):
    """Se lanza cuando falta el marcador .FROZEN en data/raw."""


def _audit_message(reason: str) -> str:
    """Build an auditable message for a raw-write intent."""
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    return f"raw_guard[{ts}]: {reason.strip()}"


def _candidate_audit_logs(audit_log: Optional[object] = None) -> list[Path]:
    paths: set[Path] = set()
    if audit_log is not None:
        try:
            paths.add(Path(audit_log))  # type: ignore[arg-type]
        except Exception:
            pass
    for name in ("AUDIT_LOG", "AUDIT_LOG_PATH", "AUDIT_LOG_FILE", "LOG_PATH",
                 "LOG_FILE", "AUDIT_FILE"):
        val = globals().get(name)
        if val is not None:
            try:
                paths.add(Path(val))  # type: ignore[arg-type]
            except Exception:
                pass
    gl = globals().get("AUDIT_LOG_PATHS")
    if isinstance(gl, (list, tuple, set)):
        for p in gl:
            try:
                paths.add(Path(p))  # type: ignore[arg-type]
            except Exception:
                pass
    env = os.environ.get("RAW_GUARD_AUDIT_LOG")
    if env:
        paths.add(Path(env))
    if not paths:
        paths.add(_DEFAULT_AUDIT_LOG)
    return sorted(paths, key=lambda p: str(p))


def assert_raw_writable(reason: Optional[str], audit_log: Optional[object] = None) -> None:
    """Raise ``ValueError`` unless ``reason`` is a non-empty string.

    Además verifica que exista el marcador ``.FROZEN`` en ``data/raw/`` y
    añade la intención a un log de auditoría persistente.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("raw write requires a non-empty reason")
    if not FROZEN_MARKER.exists():
        raise RawFrozenMissing(
            f"raw write requires frozen marker: {FROZEN_MARKER} missing"
        )
    msg = _audit_message(reason)
    log.info(msg)
    for path in _candidate_audit_logs(audit_log):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(msg + "\n")
        except Exception:
            # No interrumpir la operación por un fallo de log; reintentar siguiente.
            continue
