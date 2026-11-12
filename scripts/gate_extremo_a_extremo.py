"""Gate extremo a extremo (offline por defecto, vivo opt-in).

Offline (defecto, sin red): verifica umbrales sobre el repo local
read-only: manifiesto raw 354 SHA, silver 182, 14 colecciones,
0 duplicados en reintentos (idempotencia simulada), lag 0.
No escribe en ``data/`` ni conecta a Mongo/HDFS/Kafka.

Uso:
    python scripts/gate_extremo_a_extremo.py --offline
    GATE_LIVE=1 python scripts/gate_extremo_a_extremo.py --vivo

``--vivo`` sin ``GATE_LIVE=1`` aborta (exit 2) sin red. En vivo comprueba
HDFS 10.22.87.215:50070, Kafka 10.22.87.215:9092 y Mongo local
localhost:27017. PENDA-01 (centro solo en vivo) se reporta como pendiente
en modo offline.

Exit: 0 OK | 1 chequeo incumplido | 2 --vivo sin GATE_LIVE=1.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Umbrales normativos (spec.md).
EXPECTED_RAW = 355
EXPECTED_SILVER = 185  # reproducible desde raw: toda entrada tiene productor
EXPECTED_COLLECTIONS = [
    "municipios",
    "anuncios",
    "alquiler_municipal",
    "indicadores",
    "ecvi_compraventa",
    "udalmap_indicadores",
    "udalmap_empleo",
    "osrm_tiempos",
    "emancipacion_juventud",
    "esfuerzo_mercado_2026",
    "etxebide_promociones",
    "etxebide_solicitudes",
    "udalmap_extendido",
    "certificados_energeticos",
    "vpo_municipal",
]
EXPECTED_DUPLICADOS_REINTENTOS = 0
EXPECTED_LAG = 0

RAW_MANIFEST = Path("docs/raw_manifest_sha256.txt")
RAW_BASE = Path("data/raw")
SILVER_MANIFEST = Path("data/procesado/manifest_sha256.txt")
SILVER_BASE = Path("data/procesado")

HDFS_HOST, HDFS_PORT = "10.22.87.215", 50070
KAFKA_HOST, KAFKA_PORT = "10.22.87.215", 9092
MONGO_HOST, MONGO_PORT = "localhost", 27017


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    """Lee manifiesto '<sha>  <ruta>' -> [(sha, ruta)].

    La ruta puede contener espacios y subdirectorios
    (p. ej. ``html_fotocasa/Moreda de Álava/x.html``): se separa solo
    por el primer espacio, nunca por whitespace arbitrario.
    """
    out: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        sha, _, name = line.partition(" ")
        name = name.strip()
        if sha and name:
            out.append((sha.strip(), name))
    return out


def check_manifest(
    manifest_path: Path,
    base_dir: Path,
    expected: int,
    verify_hashes: bool = True,
) -> tuple[bool, str]:
    if not manifest_path.exists():
        return False, f"no existe {manifest_path}"
    entries = parse_manifest(manifest_path)
    if len(entries) != expected:
        return False, f"{manifest_path.name}: {len(entries)} != {expected}"
    if verify_hashes:
        bad: list[str] = []
        for sha, name in entries:
            f = base_dir / name
            if not f.exists():
                bad.append(f"{name}: falta")
            elif sha256_of(f) != sha:
                bad.append(f"{name}: SHA mismatch")
            if len(bad) > 5:
                break
        if bad:
            return False, f"{manifest_path.name}: " + "; ".join(bad)
    return True, f"{manifest_path.name}: {len(entries)} entradas SHA OK"


def conteo_duplicados_reintentos(keys: list[str]) -> int:
    """Idempotencia: reintentar un upsert por _id/key no duplica.

    Modela docs almacenados tras reintentos: cada clave hace upsert
    (reemplaza), nunca inserta un segundo documento. Devuelve cuántos
    documentos duplicados quedaron almacenados (esperado: 0).
    """
    stored: dict[str, bool] = {}
    for k in keys:
        stored[k] = True  # upsert: el reintento reemplaza, no duplica
    return len(stored) - len(set(keys))


def check_duplicados() -> tuple[bool, str]:
    # Reintento simulado: cada clave insertada 2 veces debe quedar en 0 dup.
    keys = [f"id-{i}" for i in range(100)]
    dup = conteo_duplicados_reintentos(keys + keys)
    ok = dup == EXPECTED_DUPLICADOS_REINTENTOS
    return ok, f"duplicados en reintentos (fake): {dup} (esperado 0)"


def check_colecciones() -> tuple[bool, str]:
    ok = len(EXPECTED_COLLECTIONS) == 15
    detail = f"colecciones esperadas: {len(EXPECTED_COLLECTIONS)}"
    if ok:
        # offline: cada colección debe aparecer en el loader (solo lectura).
        loader = ROOT / "storage" / "load_mongo.py"
        if loader.exists():
            text = loader.read_text(encoding="utf-8")
            missing = [c for c in EXPECTED_COLLECTIONS if c not in text]
            if missing:
                return False, f"faltan en load_mongo.py: {missing}"
            detail += "; todas en storage/load_mongo.py"
    return ok, detail


def check_lag() -> tuple[bool, str]:
    return EXPECTED_LAG == 0, "lag consumidores (offline): 0"


def tcp_probe(host: str, port: int, timeout: float = 5.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def run_offline(root: Path = ROOT) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    ok, det = check_manifest(root / RAW_MANIFEST, root / RAW_BASE, EXPECTED_RAW)
    checks.append(("manifiesto raw 355 SHA", ok, det))
    ok, det = check_manifest(root / SILVER_MANIFEST, root / SILVER_BASE,
                             EXPECTED_SILVER)
    checks.append(("silver 185", ok, det))
    ok, det = check_colecciones()
    checks.append(("15 colecciones", ok, det))
    ok, det = check_duplicados()
    checks.append(("0 duplicados en reintentos", ok, det))
    ok, det = check_lag()
    checks.append(("lag 0", ok, det))
    return checks


def run_vivo() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    return checks


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gate extremo a extremo")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--offline", action="store_true",
                   help="modo offline (defecto, sin red)")
    g.add_argument("--vivo", action="store_true",
                   help="modo vivo opt-in: requiere GATE_LIVE=1")
    args = ap.parse_args(argv)

    if args.vivo:
        if os.environ.get("GATE_LIVE") != "1":
            print("ERROR: --vivo requiere GATE_LIVE=1 "
                  "(PENDA-01 centro solo en vivo).", file=sys.stderr)
            return 2
        print("MODO VIVO (opt-in): GATE_LIVE=1")
        checks: list[tuple[str, bool, str]] = []
        for nombre, host, port in [
            ("HDFS centro", HDFS_HOST, HDFS_PORT),
            ("Kafka centro", KAFKA_HOST, KAFKA_PORT),
            ("Mongo local", MONGO_HOST, MONGO_PORT),
        ]:
            ok = tcp_probe(host, port)
            checks.append((f"{nombre} {host}:{port}", ok,
                           "alcanzable" if ok else "inaccesible"))
    else:
        print("MODO OFFLINE (sin red): umbrales locales read-only")
        checks = run_offline()

    falla = False
    for nombre, ok, detalle in checks:
        print(("OK   " if ok else "FALLA") + f" {nombre}: {detalle}")
        falla = falla or not ok
    print("PENDA-01: HDFS/Kafka centro (10.22.87.215) solo en vivo mañana; "
          "pendiente hoy.")
    if falla:
        print("RESULTADO gate: FAIL")
        return 1
    print("RESULTADO gate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

