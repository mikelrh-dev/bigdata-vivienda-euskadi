"""Genera el acta maquina-leible de ingesta (WP-17).

NO toca data/raw (congelado). Lee el inventario de raw + los sidecars
de data/procesado/_meta/ y escribe
data/procesado/_meta/ingestion_manifest.json con una entrada por
fichero: nombre, bytes, sha256, fuente, url, fecha_extraccion,
n_registros (los 4 ultimos desde el sidecar cuando existe).

Uso:
    python transform/quality/generar_ingestion_manifest.py
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
META_DIR = PROJECT_ROOT / "data" / "procesado" / "_meta"
OUT = META_DIR / "ingestion_manifest.json"

EXCLUIDOS = {".FROZEN", ".gitkeep", "manifest_sha256.txt"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    META_DIR.mkdir(parents=True, exist_ok=True)
    entradas = []
    for ruta in sorted(RAW_DIR.rglob("*")):
        if not ruta.is_file() or ruta.name in EXCLUIDOS:
            continue
        rel = ruta.relative_to(RAW_DIR).as_posix()
        meta = {}
        sidecar = META_DIR / f"{ruta.name}.meta.json"
        if sidecar.exists():
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                meta = {}
        entradas.append({
            "fichero": rel,
            "bytes": ruta.stat().st_size,
            "sha256": _sha256(ruta),
            "fuente": meta.get("fuente"),
            "url": meta.get("url"),
            "fecha_extraccion": meta.get("fecha_extraccion"),
            "n_registros": meta.get("n_registros"),
        })
    OUT.write_text(json.dumps({
        "generado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generado_por": "transform/quality/generar_ingestion_manifest.py",
        "fuentes_config": "config/fuentes.yaml",
        "n_ficheros": len(entradas),
        "ficheros": entradas,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {OUT} ({len(entradas)} ficheros)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
