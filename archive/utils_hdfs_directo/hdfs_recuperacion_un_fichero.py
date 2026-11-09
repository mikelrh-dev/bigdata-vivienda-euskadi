"""Recuperación HDFS de un fichero raw solo lectura (Bloque 2, paso 5).

Descarga 1 fichero raw de HDFS y compara SHA-256 + tamaño con el local,
sin escritura en HDFS ni crear carpeta, para cerrar el SHA de 1 fichero.

Uso:
    .venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py alquiler_distrito_seccion_original.csv
    .venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py --file alquiler_distrito_seccion_original.csv

Por defecto usa alquiler_distrito_seccion_original.csv (primer fichero
del manifest). Solo lectura: status/list/read, sin write ni delete ni mkdir.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_FILE = "alquiler_distrito_seccion_original.csv"
HDFS_RAW = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw"


def sha_local(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "file_pos",
        nargs="?",
        default=None,
        help="Ruta relativa dentro de data/raw (p. ej. alquiler_distrito_seccion_original.csv).",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Ruta relativa dentro de data/raw.",
    )
    args = parser.parse_args(argv)
    rel = args.file or args.file_pos or DEFAULT_FILE

    from storage.hdfs_utils import get_client, read_file_sha256

    local = ROOT / "data" / "raw" / rel
    if not local.exists():
        print(f"LOCAL_NO_EXISTE {local}")
        return 1
    hdfs_path = f"{HDFS_RAW}/{rel}"
    local_size = local.stat().st_size
    local_sha = sha_local(local)
    client = get_client()
    try:
        status = client.status(hdfs_path)
        remote_sha = read_file_sha256(client, hdfs_path)
    except Exception as exc:  # noqa: BLE001
        print(f"HDFS_REC FAIL {exc}")
        return 1
    remote_size = status.get("length")
    print(f"FICHERO {rel}")
    print(f"HDFS_PATH {hdfs_path}")
    print(f"LOCAL_SIZE {local_size} SHA {local_sha}")
    print(f"REMOTE_SIZE {remote_size} SHA {remote_sha}")
    if local_size == remote_size and local_sha == remote_sha:
        print("HDFS_REC OK SHA_TAMANO_IGUALES")
        print("HDFS_REC CERO_ESCRITURAS NO_CARPETA_NUEVA")
        return 0
    print("HDFS_REC DIFIERE")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
