# kafka_hdfs_uploader.py

- **Nombre:** `kafka_hdfs_uploader.py`
- **Ruta en VM:** `/home/mikel/bigdata_hdfs_vm/kafka_hdfs_uploader.py`
- **Estado real:** **no consume Kafka**. `upload()` recorre `~/staging/raw` y sube todo con `client.write`. El `if False` desactiva `upload_raw_excluding_legacy`; `is_valid_rel` y `verify_staging` no se llaman; no verifica SHA ni excluye legacy. El docstring de abajo describe el diseño, no el comportamiento actual.
- **Host VM:** `192.168.201.162` (SSH `mikel@192.168.201.162`, clave `C:/Users/mikel/.ssh/id_vm_hermes`)
- **Tamaño:** 2503 bytes
- **Líneas:** 76
- **Modificación (stat VM):** 2026-11-06 17:01:49 +0000
- **SHA256 (`sha256sum` en VM):** `863837944f1befde59e33b2a10f086a1282ebb68beeb9285174d9d21ba3f427f`
- **Verificación local:** SHA256 calculado en copia descargada por `scp` coincide con el de VM.

## Listado VM (histórico — hoy quedan 3)

```bash
$ ssh -i C:/Users/mikel/.ssh/id_vm_hermes mikel@192.168.201.162 "ls -l ~/bigdata_hdfs_vm/"
total 28
-rw-r--r-- 1 mikel mikel 6136 nov  6 17:01 hdfs_utils.py
-rw-rw-r-- 1 mikel mikel  505 nov  6 17:42 hdfs_verify.py
-rw-r--r-- 1 mikel mikel 2503 nov  6 17:01 kafka_hdfs_uploader.py
```

## Código completo

```python
"""Uploader VM: consume manifiesto Kafka y sube a HDFS (VM -> Hadoop).

Grupo hdfs_vm, topic anuncios_inmobiliarios. Descarta mensajes sin
type raw_manifest, valida rel (sin .. / absoluta), comprueba SHA+size
de ~/staging/raw contra manifiesto y hace UN put bulk con
upload_raw_excluding_legacy + verificacion read_file_sha256.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_TOPIC = "anuncios_inmobiliarios"
DEFAULT_GROUP = "hdfs_vm"
DEFAULT_STAGING = Path.home() / "staging" / "raw"
DEFAULT_BOOTSTRAP = "192.168.201.162:9094"


def get_bootstrap() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP


def is_valid_rel(rel: str) -> bool:
    if not rel or ".." in Path(rel).parts:
        return False
    if Path(rel).is_absolute():
        return False
    if "legacy_obsoleto_no_usar" in rel:
        return False
    return True


def verify_staging(staging: Path, rel: str, size: int, sha: str) -> bool:
    p = Path(staging) / rel
    if not p.exists():
        return False
    data = p.read_bytes()
    return len(data) == size and hashlib.sha256(data).hexdigest() == sha


def upload() -> dict:
    from hdfs import InsecureClient

    url = os.getenv("HDFS_URL", "http://10.22.87.215:50070")
    user = os.getenv("HDFS_USER", "iabd-user15")
    staging = Path(os.getenv("STAGING_RAW", str(DEFAULT_STAGING)))
    client = InsecureClient(url, user=user)
    dest = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw"
    # Estado del bulk en la VM (reanudable)
    res = __import__("storage.hdfs_utils", fromlist=["upload_raw_excluding_legacy"]).upload_raw_excluding_legacy(
        client=client, raw_dir=staging, hdfs_path=dest,
        state_dir=Path.home() / "bigdata_hdfs_vm" / "data" / "_hdfs_state",
    ) if False else {"uploaded": 0, "deduped": 0}
    # Implementacion directa sin importar storage (VM copia minima):
    uploaded = deduped = 0
    for f in sorted(p for p in staging.rglob("*") if p.is_file()):
        rel = f.relative_to(staging).as_posix()
        with f.open("rb") as fp:
            client.write(f"{dest}/{rel}", data=fp.read(), overwrite=True)
        uploaded += 1
    # Verificacion SHA de 1 fichero de muestra
    sample = next(staging.rglob("*"))
    res = {"uploaded": uploaded, "deduped": deduped}
    print(f"HDFS_VM_UPLOADED {uploaded} a {dest}")
    return res


if __name__ == "__main__":
    print(upload())
```
