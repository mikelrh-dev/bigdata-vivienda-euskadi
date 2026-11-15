#!/usr/bin/env python3
"""Verifica que la cadena raw -> silver -> Mongo -> gold sigue siendo reproducible.

No reconstruye nada ni escribe fuera de un temporal: comprueba lo que ya existe
y compara el gold contra un baseline versionado. Cuatro bloques:

  1. raw       355 SHA contra docs/raw_manifest_sha256.txt
  2. DAG       toda entrada y salida data/procesado tiene productor declarado
               en transform/run_all.py (nada hecho a mano)
  3. colecciones  las vivas de Mongo son exactamente las que carga load_all
  4. gold      dos pasadas de run_analisis_mongo.py en un temporal dan la misma
               huella y coinciden byte a byte con el baseline y data/resultados

Uso:
    python scripts/verificar_reproducibilidad.py
    python scripts/verificar_reproducibilidad.py --sin-gold
    python scripts/verificar_reproducibilidad.py --actualizar-baseline

Codigos: 0 OK, 1 fallo, 2 no verificable (sin Mongo o sin raw).
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "data" / "raw"
RAW_MANIFEST = ROOT / "docs" / "raw_manifest_sha256.txt"
PROC_DIR = ROOT / "data" / "procesado"
RES_DIR = ROOT / "data" / "resultados"
SILVER_MANIFEST = PROC_DIR / "manifest_sha256.txt"
BASELINE = ROOT / "docs" / "baseline_gold_sha256.json"
ANALISIS = ROOT / "analysis" / "run_analisis_mongo.py"

OK, FALLO, NO_VERIFICABLE = "OK", "FALLO", "NO_VERIFICABLE"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def leer_manifest(path: Path) -> dict[str, str]:
    """Manifest 'sha  nombre' -> {nombre: sha}."""
    out: dict[str, str] = {}
    for linea in path.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea:
            continue
        partes = linea.split(None, 1)
        if len(partes) == 2:
            out[partes[1].lstrip("*").strip()] = partes[0]
    return out


def check_raw() -> tuple[str, str]:
    if not RAW_DIR.is_dir():
        return NO_VERIFICABLE, "no existe data/raw"
    if not RAW_MANIFEST.exists():
        return NO_VERIFICABLE, f"no existe {RAW_MANIFEST.relative_to(ROOT)}"
    esperado = leer_manifest(RAW_MANIFEST)
    malos = [n for n, sha in esperado.items()
             if not (RAW_DIR / n).is_file() or sha256_of(RAW_DIR / n) != sha]
    if malos:
        return FALLO, f"{len(malos)} ficheros raw no coinciden (p.ej. {malos[0]})"
    return OK, f"{len(esperado)} SHA de raw OK"


def check_dag() -> tuple[str, str]:
    try:
        import transform.run_all as ra
    except Exception as exc:  # noqa: BLE001
        return NO_VERIFICABLE, f"no se pudo importar el DAG ({exc!r})"
    if not SILVER_MANIFEST.exists():
        return NO_VERIFICABLE, "no existe data/procesado/manifest_sha256.txt"

    prod: set[str] = set()
    for script in ra.SCRIPTS:
        for ruta in ra._salidas(script):
            try:
                prod.add(ruta.resolve().relative_to(PROC_DIR.resolve()).as_posix())
            except ValueError:
                pass

    manifest = set(leer_manifest(SILVER_MANIFEST))
    # Los sidecars _meta/ los escribe la fase quality (normalizar_metadata).
    datos = {n for n in manifest if not n.startswith("_meta/")}
    huerfanos = sorted(n for n in datos if n not in prod)
    if huerfanos:
        return FALLO, (f"{len(huerfanos)} ficheros de silver sin productor "
                       f"(p.ej. {huerfanos[0]})")

    sin_productor: set[str] = set()
    for cfg in ra.SCRIPTS.values():
        for ref in cfg.get("in", []):
            base, _, patron = ref.partition(":")
            if base != "proc" or any(c in patron for c in "*?["):
                continue
            if patron not in prod:
                sin_productor.add(patron)
    if sin_productor:
        return FALLO, ("entradas del DAG sin productor: "
                       + ", ".join(sorted(sin_productor)[:3]))

    return OK, (f"{len(ra.SCRIPTS)} scripts, {len(datos)} datos de silver y "
                f"{len(prod)} salidas con productor")


def colecciones_cargadas() -> list[str]:
    """Claves del dict literal de load_all (evita ejecutar la carga)."""
    from storage import load_mongo

    fuente = inspect.getsource(load_mongo.load_all)
    return re.findall(r'"(\w+)":\s*load_\w+\(', fuente)


def check_colecciones() -> tuple[str, str]:
    try:
        from storage.mongo import get_db, ping
    except Exception as exc:  # noqa: BLE001
        return NO_VERIFICABLE, f"no se pudo importar storage.mongo ({exc!r})"
    if not ping():
        return NO_VERIFICABLE, "MongoDB no responde (ping fallido)"
    db = get_db()
    vivas = {n for n in db.list_collection_names()
             if not n.endswith("__backup") and not n.endswith("__staging")}
    cargadas = set(colecciones_cargadas())
    faltan = sorted(vivas - cargadas)
    sobran = sorted(cargadas - vivas)
    if faltan:
        return FALLO, f"colecciones vivas sin loader: {', '.join(faltan)}"
    if sobran:
        return FALLO, f"load_all declara colecciones inexistentes: {', '.join(sobran)}"
    return OK, f"{len(vivas)} colecciones vivas, todas con loader"


def _pasada_gold(destino: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ANALISIS), "--salida", str(destino), "--sin-sync-deck"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    huella = ""
    for linea in (proc.stdout or "").splitlines():
        if linea.startswith("huella: "):
            huella = linea.split(": ", 1)[1].strip()
    return proc.returncode, huella


def check_gold(actualizar_baseline: bool) -> tuple[str, str]:
    from storage.mongo import ping

    if not ping():
        return NO_VERIFICABLE, "MongoDB no responde: el gold no se puede recalcular"
    if not BASELINE.exists() and not actualizar_baseline:
        return NO_VERIFICABLE, f"no existe {BASELINE.relative_to(ROOT)}"

    with tempfile.TemporaryDirectory(prefix="repro_gold_") as tmp:
        tmp1 = Path(tmp) / "pasada1"
        tmp2 = Path(tmp) / "pasada2"
        rc1, huella1 = _pasada_gold(tmp1)
        if rc1 != 0 or not huella1:
            return FALLO, f"pasada 1 del analisis fallo (rc={rc1})"
        rc2, huella2 = _pasada_gold(tmp2)
        if rc2 != 0 or not huella2:
            return FALLO, f"pasada 2 del analisis fallo (rc={rc2})"
        if huella1 != huella2:
            return FALLO, f"huella inestable: {huella1[:12]} != {huella2[:12]}"

        csvs = sorted(p.name for p in tmp1.glob("mongo_*.csv"))
        shas = {n: sha256_of(tmp1 / n) for n in csvs}
        if actualizar_baseline:
            BASELINE.write_text(
                json.dumps({"_nota": "Baseline de reproducibilidad del gold. "
                                     "Regenerar con --actualizar-baseline.",
                            "fecha": _hoy(), "huella_gold": huella1,
                            "csv": shas},
                           indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return OK, (f"baseline escrito: huella {huella1[:12]}…, "
                        f"{len(shas)} CSV")

        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        if base.get("huella_gold") != huella1:
            return FALLO, (f"huella {huella1[:12]}… != baseline "
                           f"{str(base.get('huella_gold'))[:12]}…")
        distintos = [n for n, sha in base.get("csv", {}).items()
                     if shas.get(n) != sha]
        if distintos:
            return FALLO, f"CSV distintos del baseline: {', '.join(distintos[:3])}"
        divergentes = [n for n, sha in shas.items()
                       if (RES_DIR / n).is_file() and sha256_of(RES_DIR / n) != sha]
        if divergentes:
            return FALLO, (f"CSV recalculados != data/resultados: "
                           f"{', '.join(divergentes[:3])}")
        return OK, (f"huella {huella1[:12]}… identica en dos pasadas y "
                    f"{len(shas)} CSV iguales a baseline y gold")


def _hoy() -> str:
    from datetime import date

    return date.today().isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifica la reproducibilidad raw -> silver -> Mongo -> gold")
    parser.add_argument("--sin-gold", action="store_true",
                        help="Omite el recalculo del gold (rapido, sin Mongo)")
    parser.add_argument("--actualizar-baseline", action="store_true",
                        help="Regenera docs/baseline_gold_sha256.json con el gold actual")
    args = parser.parse_args(argv)

    checks = [("raw", check_raw()), ("DAG", check_dag()),
              ("colecciones", check_colecciones())]
    if not args.sin_gold:
        checks.append(("gold", check_gold(args.actualizar_baseline)))

    print("=== REPRODUCIBILIDAD ===")
    for nombre, (estado, detalle) in checks:
        print(f"  [{estado:<14}] {nombre:<12} {detalle}")

    if any(e == NO_VERIFICABLE for _, (e, _) in checks):
        print("\nRESULTADO: NO VERIFICABLE (falta una dependencia)")
        return 2
    if any(e == FALLO for _, (e, _) in checks):
        print("\nRESULTADO: FALLO")
        return 1
    print("\nRESULTADO: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
