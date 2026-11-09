"""Verificación byte a byte de un fichero de data/raw contra HDFS (Windows, sin VM).

Uso:
    .venv/Scripts/python.exe scripts/hdfs_verify.py
    .venv/Scripts/python.exe scripts/hdfs_verify.py alquiler_municipal.json
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage.hdfs_utils import get_client, read_file_sha256

FILE = sys.argv[1] if len(sys.argv) > 1 else "alquiler_municipal.json"

local_sha = hashlib.sha256((ROOT / "data" / "raw" / FILE).read_bytes()).hexdigest()
remoto = read_file_sha256(get_client(), f"/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/{FILE}")

print(local_sha)
print(remoto)
print("Igual?", local_sha == remoto)
