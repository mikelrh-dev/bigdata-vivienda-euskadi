"""Chequeo rapido fase datos: raw inmutable, silver, cobertura, tipos.

Uso: python framework_auditoria_completo2/diagnostico.py
Solo lectura (no modifica data/). Codigo de salida 0 = OK, 1 = hay P1/P2.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "procesado"

fallos: list[str] = []


def ok(msg: str) -> None:
    print(f"  OK  {msg}")


def mal(msg: str) -> None:
    print(f"  MAL {msg}")
    fallos.append(msg)


def main() -> int:
    print("== RAW ==")
    raw_manifest = ROOT / "docs" / "raw_manifest_sha256.txt"
    if raw_manifest.exists():
        lineas = [l for l in raw_manifest.read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"  manifest docs/raw_manifest_sha256.txt: {len(lineas)} entradas")
    else:
        mal("falta docs/raw_manifest_sha256.txt")
    ing = PROC / "_meta" / "ingestion_manifest.json"
    if ing.exists():
        try:
            d = json.loads(ing.read_text(encoding="utf-8"))
            items = d if isinstance(d, list) else d.get("files", d.get("ficheros", d.get("entries", [])))
            print(f"  manifest _meta/ingestion_manifest.json: {len(items)} entradas")
        except Exception as e:  # noqa: BLE001 - diagnostico rapido
            mal(f"ingestion_manifest ilegible: {e}")
    else:
        print("  (sin _meta/ingestion_manifest.json — lo crea el pipeline)")
    if (RAW / ".FROZEN").exists():
        ok(".FROZEN presente")
    else:
        mal("falta data/raw/.FROZEN")
    html = list((RAW / "html_fotocasa").glob("*.html")) if (RAW / "html_fotocasa").exists() else []
    print(f"  html_fotocasa: {len(html)} paginas")

    print("== SILVER ==")
    if not PROC.exists():
        mal("falta data/procesado/")
        return 1
    print(f"  ficheros silver: {len(list(PROC.iterdir()))}")
    for clave in ["dim_municipios.csv", "anuncios_unificados.csv", "cobertura_anuncios.csv"]:
        p = PROC / clave
        print(f"  {'OK ' if p.exists() else 'FALTA'} {clave}")

    try:
        import pandas as pd

        dim = pd.read_csv(PROC / "dim_municipios.csv", encoding="utf-8-sig", dtype=str)
        print(f"  dim_municipios: {len(dim)} filas, {dim['codigo_ine'].nunique()} ine unicos")
        if len(dim) != 252:
            mal(f"dim_municipios={len(dim)}, esperado 252")
        else:
            ok("dim 252 municipios")
        if (dim["codigo_ine"].str.len() != 5).any():
            mal("codigo_ine no siempre 5 digitos en dim")
        else:
            ok("codigo_ine 5 digitos en dim")
        uni_path = PROC / "anuncios_unificados.csv"
        if uni_path.exists():
            uni = pd.read_csv(uni_path, encoding="utf-8-sig", dtype=str)
            print(f"  unificados: {len(uni)} anuncios, {uni['codigo_ine'].nunique()} municipios")
    except Exception as e:  # noqa: BLE001
        mal(f"pandas check: {e}")

    print("== TIPOS / RUIDO ==")
    sin_dtype = []
    for py in (ROOT / "transform").glob("*.py"):
        txt = py.read_text(encoding="utf-8", errors="replace")
        if "pd.read_csv(" in txt and "dtype" not in txt:
            sin_dtype.append(py.name)
    if sin_dtype:
        mal(f"read_csv sin dtype en: {', '.join(sin_dtype)}")
    else:
        ok("todo pd.read_csv de transform con dtype")
    import subprocess

    r = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT  # noqa: S603
    )
    tracked = r.stdout if r.returncode == 0 else ""
    secretos = [l for l in tracked.splitlines() if l == ".env" or "api.txt" in l.lower()]
    if secretos:
        mal(f"secretos trackeados: {secretos}")
    else:
        ok("sin secretos trackeados (.env/api.txt)")

    print()
    if fallos:
        print(f"RESULTADO: {len(fallos)} problema(s)")
        return 1
    print("RESULTADO: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
