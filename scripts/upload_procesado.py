"""Entrypoint de subida de procesado a HDFS con --dry-run (bloque 2, paso 5).

Sin confirmación de la profesora, NO se sube el procesado a HDFS.
Este script solo lista lo que subiría (ficheros, bytes, SHA-256) con
cero escrituras. Sin --dry-run rehúsa y sale con código 2.

Uso:
    .venv/Scripts/python.exe scripts/upload_procesado.py --dry-run

Lee el manifiesto data/procesado/manifest_sha256.txt cuando existe y
verifica que el SHA local coincide para los ficheros incluidos.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESADO_DIR = ROOT / "data" / "procesado"
MANIFEST = PROCESADO_DIR / "manifest_sha256.txt"
DEST_BASE = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/procesado"


def sha_local(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict[str, str]:
    if not MANIFEST.exists():
        return {}
    out: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            out[parts[1].lstrip("*")] = parts[0]
    return out


def iter_files(base: Path) -> list[Path]:
    return sorted(p for p in base.rglob("*") if p.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Lista lo que subiría sin escribir nada en HDFS.",
    )
    args = parser.parse_args(argv)
    if not args.dry_run:
        print("REFUSADO: sin confirmación de la profesora no se sube procesado (usa --dry-run)")
        return 2
    if not PROCESADO_DIR.exists():
        print(f"NO existe {PROCESADO_DIR}")
        return 1
    manifest = load_manifest()
    files = iter_files(PROCESADO_DIR)
    total_bytes = 0
    ok = 0
    falta = 0
    print(f"DESTINO_HDFS {DEST_BASE}")
    print(f"N_FICHEROS {len(files)} MANIFEST {len(manifest)}")
    for f in files:
        rel = f.relative_to(PROCESADO_DIR).as_posix()
        size = f.stat().st_size
        total_bytes += size
        sha = sha_local(f)
        expect = manifest.get(rel)
        if expect is None:
            falta += 1
            print(f"{rel} {size} {sha} SIN_MANIFEST")
        elif expect == sha:
            ok += 1
            print(f"{rel} {size} {sha} OK")
        else:
            print(f"{rel} {size} {sha} EXPECT {expect} DIFIERE")
    print(f"TOTAL_FICHEROS {len(files)} TOTAL_BYTES {total_bytes} OK {ok} SIN_MANIFEST {falta}")
    print("DRY_RUN_OK CERO_ESCRITURAS NO_SUBIDO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
