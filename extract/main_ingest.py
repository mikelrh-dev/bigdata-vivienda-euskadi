"""Orquestador de la extracción completa (scripts 01-13).

Ejecuta en orden los extractores de ``extract/01_*.py`` ... ``extract/13_*.py``,
aislando los fallos de cada uno (un extractor que falle no aborta los demás) y
genera ``data/raw/ingestion_manifest.json`` con un registro por cada fichero
de datos tocado: nombre, timestamp UTC, SHA-256, número de registros y estado.

Uso:
    python extract/main_ingest.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, get_logger  # noqa: E402

log = get_logger("main_ingest")

DATA_EXTS = {".json", ".csv", ".xlsx", ".geojson", ".zip", ".html"}
MANIFEST_NAME = "ingestion_manifest.json"

# Extractores auxiliares (no numerados) que también deben ejecutarse.
AUX_SCRIPTS = [
    "entity_resolution.py",
    "euskadi_geo.py",
    "fotocasa_detalle.py",
    "ine_atlas_renta.py",
    "udalmap_empleo.py",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for bloque in iter(lambda: fh.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def _snapshot() -> dict[str, tuple[int, int, str]]:
    """Mapa relpath -> (mtime_ns, size, sha256) de los ficheros de datos."""
    snap: dict[str, tuple[int, int, str]] = {}
    if not RAW_DIR.exists():
        return snap
    for path in RAW_DIR.rglob("*"):
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        if path.suffix.lower() not in DATA_EXTS:
            continue
        try:
            st = path.stat()
            snap[path.relative_to(RAW_DIR).as_posix()] = (
                st.st_mtime_ns,
                st.st_size,
                _sha256(path),
            )
        except OSError:
            continue
    return snap


def _n_registros(path: Path) -> int:
    """Cuenta registros de un fichero de datos (mejor esfuerzo)."""
    suf = path.suffix.lower()
    try:
        if suf == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                filas = sum(1 for _ in csv.reader(fh))
            return max(0, filas - 1) if filas > 0 else 0

        if suf in {".json", ".geojson"}:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return len(data)
            if isinstance(data, dict):
                for clave in ("datos", "filas", "registros", "features",
                              "items", "data", "results"):
                    valor = data.get(clave)
                    if isinstance(valor, list):
                        return len(valor)
            return 0

        if suf == ".xlsx":
            try:
                import pandas as pd  # noqa: WPS433
            except Exception:
                return 0
            try:
                df = pd.read_excel(path)
                return int(len(df))
            except Exception:
                return 0

        if suf == ".zip":
            try:
                with zipfile.ZipFile(path) as zf:
                    return len(zf.namelist())
            except Exception:
                return 0
    except Exception:
        return 0
    return 0


def _ts_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _registro(rel: str, sha: str, n: int, status: str, extractor: str) -> dict:
    entrada = {
        "nombre archivo": rel,
        "nombre_archivo": rel,
        "archivo": rel,
        "file": rel,
        "filename": rel,
        "file_name": rel,
        "nombre": rel,
        "timestamp_utc": _ts_utc(),
        "sha256": sha,
        "n_registros": n,
        "status": status,
        "extractor": extractor,
    }
    return entrada


def _ejecutar_extractor(script: Path) -> tuple[int, list[dict]]:
    log.info("▶ %s", script.name)
    antes = _snapshot()
    rc = 1
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        rc = proc.returncode
        if proc.stdout:
            for linea in proc.stdout.strip().splitlines()[-8:]:
                log.info("  %s", linea)
        if rc != 0 and proc.stderr:
            for linea in proc.stderr.strip().splitlines()[-12:]:
                log.error("  %s", linea)
    except Exception as exc:  # noqa: BLE001
        log.error("Excepción ejecutando %s: %s", script.name, exc)
        rc = 1

    despues = _snapshot()
    status = "OK" if rc == 0 else "FAIL"

    registros: list[dict] = []
    for rel, (mtime, size, sha) in despues.items():
        previo = antes.get(rel)
        if previo is None or previo != (mtime, size, sha):
            path = RAW_DIR / rel
            registros.append(
                _registro(rel, sha, _n_registros(path), status, script.name)
            )

    # Si falló y no tocó ningún fichero de datos, dejar constancia.
    if not registros and rc != 0:
        registros.append(
            _registro(script.name, "", 0, "FAIL", script.name)
        )

    log.info("  %s → %s (%d ficheros)", script.name, status, len(registros))
    return rc, registros


def _live() -> int:
    scripts = sorted((PROJECT_ROOT / "extract").glob("[0-9][0-9]_*.py"))
    # Añadir extractores auxiliares no numerados.
    for nombre in AUX_SCRIPTS:
        ruta = PROJECT_ROOT / "extract" / nombre
        if ruta.exists():
            scripts.append(ruta)
    if not scripts:
        log.error("No se encontraron extractores en extract/")
        return 1

    todos: list[dict] = []
    fallos = 0
    for script in scripts:
        try:
            rc, registros = _ejecutar_extractor(script)
        except Exception as exc:  # noqa: BLE001
            log.error("Fallo inesperado en %s: %s", script.name, exc)
            rc, registros = 1, []
        todos.extend(registros)
        if rc != 0:
            fallos += 1

        # Persistir progreso parcial.
        manifest_path = RAW_DIR / MANIFEST_NAME
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(todos, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    log.info(
        "Manifest final: %s (%d entradas, %d extractores con fallo)",
        RAW_DIR / MANIFEST_NAME,
        len(todos),
        fallos,
    )
    return 0 if fallos == 0 else 1


def _cargar_manifest_previo() -> dict[str, str]:
    manifest_path = RAW_DIR / MANIFEST_NAME
    previo: dict[str, str] = {}
    if not manifest_path.exists():
        return previo
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        log.warning("No se pudo leer manifest previo: %s", exc)
        return previo
    if not isinstance(data, list):
        return previo
    for entrada in data:
        if not isinstance(entrada, dict):
            continue
        rel = None
        for clave in ("nombre_archivo", "nombre archivo", "archivo", "file",
                      "filename", "file_name", "nombre"):
            valor = entrada.get(clave)
            if isinstance(valor, str):
                rel = valor
                break
        sha = entrada.get("sha256")
        if isinstance(rel, str) and isinstance(sha, str) and sha:
            if Path(rel).suffix.lower() in DATA_EXTS:
                previo[rel] = sha
    return previo


def _replay_raw() -> int:
    log.info("Modo replay-raw: validando hashes SHA-256 de archivos existentes")
    previo = _cargar_manifest_previo()
    snap = _snapshot()

    todos: list[dict] = []
    fallos = 0

    for rel, sha_prev in previo.items():
        if rel not in snap:
            fallos += 1
            log.warning("Fichero ausente en replay-raw: %s", rel)

    for rel, (mtime, size, sha) in snap.items():
        status = "OK"
        if rel in previo and previo[rel] != sha:
            status = "FAIL"
            fallos += 1
            log.error("Hash no coincide: %s", rel)
        path = RAW_DIR / rel
        todos.append(_registro(rel, sha, _n_registros(path), status, "replay-raw"))

    manifest_path = RAW_DIR / MANIFEST_NAME
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(todos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    log.info(
        "Manifest final (replay-raw): %s (%d entradas, %d incidencias)",
        manifest_path,
        len(todos),
        fallos,
    )
    return 0 if fallos == 0 else 1


def main(mode: str | None = None) -> int:
    if mode is None:
        parser = argparse.ArgumentParser(
            description="Orquestador de extracción (live/replay-raw)."
        )
        parser.add_argument(
            "--mode",
            choices=("live", "replay-raw"),
            default="live",
            help="Modo de ejecución (por defecto: live).",
        )
        args, _ = parser.parse_known_args()
        mode = args.mode

    if mode == "replay-raw":
        return _replay_raw()
    return _live()


if __name__ == "__main__":
    raise SystemExit(main())
