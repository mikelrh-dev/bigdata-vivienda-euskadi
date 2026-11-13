"""Recuperacion HDFS de un fichero raw: descarga y cotejo SHA-256 (solo lectura).

Descarga a memoria un fichero publicado en HDFS, compara tamano y SHA-256 con
la copia local de `data/raw` y devuelve un codigo de salida. No escribe en HDFS,
no crea carpetas y no toca `data/raw`.

Uso:
    .venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py
    .venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py alquiler_distrito_seccion_original.csv
    .venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py --file X --timeout 5

Codigos: 0 = SHA y tamano iguales; 1 = difiere o el local no existe;
2 = HDFS no alcanzable o argumento invalido.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import BinaryIO, cast

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_REL = "alquiler_distrito_seccion_original.csv"
HDFS_RAW = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw"
DEFAULT_HDFS_URL = "http://10.22.87.215:50070"
DEFAULT_HDFS_USER = "iabd-user15"
DEFAULT_TIMEOUT_S = 10


def get_hdfs_url() -> str:
    return os.getenv("HDFS_URL") or DEFAULT_HDFS_URL


def get_hdfs_user() -> str:
    return os.getenv("HDFS_USER") or DEFAULT_HDFS_USER


def rel_valida(rel: str) -> bool:
    """Solo rutas relativas dentro de data/raw, sin `..` ni ficheros legacy."""
    if not rel:
        return False
    if ".." in Path(rel).parts:
        return False
    if Path(rel).is_absolute() or rel.startswith(("/", "\\")):
        return False
    if "legacy_obsoleto_no_usar" in rel:
        return False
    return True


def sha_local(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def recuperar(
    rel: str,
    raw_dir: Path | str | None = None,
    timeout: int = DEFAULT_TIMEOUT_S,
    client: object | None = None,
) -> tuple[int, dict[str, object]]:
    """Coteja un fichero. Devuelve (codigo_salida, detalle).

    `client` permite inyectar un doble en tests sin red; si es None se crea un
    InsecureClient con HDFS_URL/HDFS_USER.
    """
    info: dict[str, object] = {"rel": rel, "hdfs_path": f"{HDFS_RAW}/{rel}"}
    if not rel_valida(rel):
        info["error"] = "REL_INVALIDA"
        return 2, info

    local = Path(raw_dir) / rel if raw_dir is not None else ROOT / "data" / "raw" / rel
    if not local.is_file():
        info["error"] = "LOCAL_NO_EXISTE"
        info["local"] = str(local)
        return 1, info

    local_size = local.stat().st_size
    local_sha = sha_local(local)

    try:
        if client is None:
            from hdfs import InsecureClient

            client = InsecureClient(get_hdfs_url(), user=get_hdfs_user(), timeout=timeout)
        status = client.status(info["hdfs_path"])  # type: ignore[attr-defined]
        with client.read(info["hdfs_path"]) as reader:  # type: ignore[attr-defined]
            remote = cast(BinaryIO, reader).read()
    except Exception as exc:  # noqa: BLE001
        info["error"] = f"HDFS_NO_ALCANZABLE ({type(exc).__name__}: {exc})"
        return 2, info

    remote_size = len(remote)
    remote_sha = hashlib.sha256(remote).hexdigest()
    info.update(
        {
            "local_size": local_size,
            "local_sha": local_sha,
            "remote_size": remote_size,
            "remote_sha": remote_sha,
            "remote_status_length": (status or {}).get("length"),
        }
    )
    if local_size == remote_size and local_sha == remote_sha:
        return 0, info
    return 1, info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file_pos", nargs="?", default=None, help="Ruta relativa dentro de data/raw.")
    parser.add_argument("--file", default=None, help="Ruta relativa dentro de data/raw.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S, help="Timeout HDFS en segundos.")
    parser.add_argument("--raw-dir", default=None, help="Directorio raw alternativo (tests).")
    args = parser.parse_args(argv)

    rel = args.file or args.file_pos or DEFAULT_REL
    code, info = recuperar(rel, raw_dir=args.raw_dir, timeout=args.timeout)

    print(f"FICHERO {rel}")
    print(f"HDFS_PATH {info['hdfs_path']}")
    if "error" in info:
        print(f"HDFS_REC FAIL {info['error']}")
        if code == 2 and "NO_ALCANZABLE" in str(info["error"]):
            print("HDFS_REC PISTA revisa HDFS_URL/HDFS_USER y la red del centro (VPN o aula)")
        return code

    print(f"LOCAL_SIZE {info['local_size']} SHA {info['local_sha']}")
    print(f"REMOTE_SIZE {info['remote_size']} SHA {info['remote_sha']}")
    if code == 0:
        print("HDFS_REC OK SHA_TAMANO_IGUALES")
        print("HDFS_REC CERO_ESCRITURAS NO_CARPETA_NUEVA")
        return 0
    print("HDFS_REC DIFIERE")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
