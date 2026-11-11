"""E2E gate extremo a extremo offline (hermético, sin red).

Usa tmp_path + fakes para no tocar data/raw ni servicios externos.
Verifica: integridad de manifiestos, guarda --vivo (GATE_LIVE=1)
y que el modo offline nunca intenta red.
"""

from __future__ import annotations

import hashlib
import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.gate_extremo_a_extremo import (
    EXPECTED_COLLECTIONS,
    check_manifest,
    conteo_duplicados_reintentos,
    main,
    run_offline,
)


def _manifest_tmp(base: Path, n: int) -> tuple[Path, Path]:
    """Crea n ficheros fake + manifiesto sha correcto en base."""
    base.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i in range(n):
        f = base / f"fake_{i:03d}.csv"
        f.write_bytes(f"contenido,{i}\n".encode())
        sha = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{sha}  fake_{i:03d}.csv")
    man = base / "manifest.txt"
    man.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return man, base


def test_umbrales_normativos() -> None:
    assert len(EXPECTED_COLLECTIONS) == 14


def test_manifiesto_fake_ok(tmp_path: Path) -> None:
    man, base = _manifest_tmp(tmp_path / "raw", 12)
    ok, detalle = check_manifest(man, base, 12)
    assert ok, detalle


def test_manifiesto_fake_tamper_falla(tmp_path: Path) -> None:
    man, base = _manifest_tmp(tmp_path / "raw", 5)
    (base / "fake_000.csv").write_bytes(b"adulterado")
    ok, detalle = check_manifest(man, base, 5)
    assert not ok, detalle


def test_manifiesto_conteo_incorrecto_falla(tmp_path: Path) -> None:
    man, base = _manifest_tmp(tmp_path / "raw", 4)
    ok, detalle = check_manifest(man, base, 999)
    assert not ok, detalle


def test_dedup_reintentos_cero() -> None:
    keys = [f"id-{i}" for i in range(50)]
    assert conteo_duplicados_reintentos(keys + keys) == 0


def test_vivo_sin_gate_live_aborta(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GATE_LIVE", raising=False)
    assert main(["--vivo"]) == 2


def test_offline_no_red(monkeypatch: pytest.MonkeyPatch,
                        tmp_path: Path) -> None:
    """El modo offline no debe intentar ninguna conexión de red."""
    def _prohibido(*args: object, **kwargs: object) -> object:
        raise AssertionError("offline no debe usar red")

    monkeypatch.setattr(socket, "create_connection", _prohibido)
    checks = run_offline(ROOT)
    assert checks, "sin checks"
    # Solo afirmamos hermeticidad (no red); el OK de umbrales se
    # verifica con el script --offline en VERIFY.
