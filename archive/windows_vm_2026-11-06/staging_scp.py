"""Copia staging data/raw -> VM ~/staging/raw via scp (Windows).

Objetivo: transferir los bytes de ``data/raw/`` a la VM para que el
uploader VM->HDFS los suba a HDFS. Kafka NO lleva los bytes (solo
manifiestos); ver ``vm/staging_scp.md``.

Uso (Windows, PowerShell o Git-Bash):
    .venv/Scripts/python.exe scripts/staging_scp.py --dry-run
    .venv/Scripts/python.exe scripts/staging_scp.py

- ``--dry-run`` NO copia y NO llama a ``subprocess``; solo imprime
  conteo/bytes locales y el comando scp que ejecutaria.
- Sin ``--dry-run`` ejecuta ``scp -r`` y luego verifica por SSH
  (solo lectura) el conteo/bytes remoto antes y despues.

Seguridad: siempre ``-o BatchMode=yes`` (nunca pide password) con
la clave ``C:/Users/mikel/.ssh/id_vm_hermes``.
No borra nada en local ni en remoto.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC = ROOT / "data" / "raw"
DEFAULT_HOST = "192.168.201.162"
DEFAULT_USER = "mikel"
DEFAULT_KEY = "C:/Users/mikel/.ssh/id_vm_hermes"
DEFAULT_REMOTE_DIR = "~/staging/raw"


def iter_files(src: Path) -> list[Path]:
    return sorted(p for p in Path(src).rglob("*") if p.is_file())


def stats(src: Path) -> tuple[int, int]:
    files = iter_files(src)
    return len(files), sum(p.stat().st_size for p in files)


def build_scp_command(
    src: Path | str,
    user: str = DEFAULT_USER,
    host: str = DEFAULT_HOST,
    remote_dir: str = DEFAULT_REMOTE_DIR,
    key: str = DEFAULT_KEY,
) -> list[str]:
    src_posix = Path(src).as_posix() if isinstance(src, Path) else str(src)
    if not src_posix.endswith("/"):
        src_posix += "/"
    target = f"{user}@{host}:{remote_dir}/"
    return ["scp", "-i", key, "-o", "BatchMode=yes", "-r", src_posix, target]


def remote_stats_snippet(remote_dir: str = DEFAULT_REMOTE_DIR) -> str:
    # Se ejecuta en la VM via ssh; solo lectura. Imprime "<n> <bytes>".
    return (
        "python3 -c \"from pathlib import Path; "
        f"p=Path('{remote_dir}').expanduser(); "
        "fs=[x for x in p.rglob('*') if x.is_file()] if p.exists() else []; "
        "print(len(fs), sum(x.stat().st_size for x in fs))\""
    )


def build_ssh_stats_command(
    user: str = DEFAULT_USER,
    host: str = DEFAULT_HOST,
    remote_dir: str = DEFAULT_REMOTE_DIR,
    key: str = DEFAULT_KEY,
) -> list[str]:
    return [
        "ssh",
        "-i",
        key,
        "-o",
        "BatchMode=yes",
        f"{user}@{host}",
        remote_stats_snippet(remote_dir),
    ]


def remote_stats(
    user: str = DEFAULT_USER,
    host: str = DEFAULT_HOST,
    remote_dir: str = DEFAULT_REMOTE_DIR,
    key: str = DEFAULT_KEY,
    timeout: int = 60,
) -> tuple[int, int] | None:
    """Lee conteo/bytes remoto via ssh (solo lectura). None si falla."""
    cmd = build_ssh_stats_command(
        user=user, host=host, remote_dir=remote_dir, key=key
    )
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        return None
    parts = proc.stdout.strip().split()
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def run_scp(
    src: Path | str,
    user: str = DEFAULT_USER,
    host: str = DEFAULT_HOST,
    remote_dir: str = DEFAULT_REMOTE_DIR,
    key: str = DEFAULT_KEY,
    timeout: int | None = None,
) -> subprocess.CompletedProcess:
    cmd = build_scp_command(
        src, user=user, host=host, remote_dir=remote_dir, key=key
    )
    print("SCP_CMD " + " ".join(cmd))
    return subprocess.run(cmd, text=True, timeout=timeout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--src", default=str(DEFAULT_SRC), help="Origen local (data/raw)."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="VM host.")
    parser.add_argument("--user", default=DEFAULT_USER, help="Usuario SSH.")
    parser.add_argument(
        "--key", default=DEFAULT_KEY, help="Clave SSH privada (BatchMode)."
    )
    parser.add_argument(
        "--remote-dir",
        default=DEFAULT_REMOTE_DIR,
        help="Destino remoto (~/staging/raw).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Imprime conteo/bytes y comando sin copiar ni llamar a subprocess.",
    )
    args = parser.parse_args(argv)
    src = Path(args.src)
    if not src.exists() or not src.is_dir():
        print(f"NO existe directorio origen: {src}")
        return 2
    n_local, b_local = stats(src)
    print(f"STAGING_LOCAL n={n_local} bytes={b_local} src={src.as_posix()}")
    scp_cmd = build_scp_command(
        src, user=args.user, host=args.host, remote_dir=args.remote_dir, key=args.key
    )
    print("SCP_CMD " + " ".join(scp_cmd))
    if args.dry_run:
        # No se toca la VM: ni ssh ni scp.
        print("STAGING_REMOTE_BEFORE SKIPPED (dry-run, cero llamadas)")
        print("DRY_RUN_OK CERO_COPIAS NO_COPIADO")
        return 0
    # --- real: verifica remoto antes (solo lectura) ---
    before = remote_stats(
        user=args.user, host=args.host, remote_dir=args.remote_dir, key=args.key
    )
    if before is None:
        print("STAGING_REMOTE_BEFORE UNKNOWN (ssh fallo; se continua con scp)")
    else:
        print(f"STAGING_REMOTE_BEFORE n={before[0]} bytes={before[1]}")
    # --- copia ---
    proc = run_scp(
        src, user=args.user, host=args.host, remote_dir=args.remote_dir, key=args.key
    )
    print(f"SCP_EXIT {proc.returncode}")
    if proc.returncode != 0:
        print("SCP_FALLO")
        return 1
    # --- verifica remoto despues (solo lectura) ---
    after = remote_stats(
        user=args.user, host=args.host, remote_dir=args.remote_dir, key=args.key
    )
    if after is None:
        print("STAGING_REMOTE_AFTER UNKNOWN (ssh fallo)")
        return 1
    print(f"STAGING_REMOTE_AFTER n={after[0]} bytes={after[1]}")
    if after != (n_local, b_local):
        print(
            f"STAGING_MISMATCH local n={n_local} bytes={b_local} "
            f"remoto n={after[0]} bytes={after[1]}"
        )
        return 1
    print("STAGING_VERIFIED OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
