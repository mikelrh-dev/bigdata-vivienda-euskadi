# hdfs_verify.py

- **Nombre:** `hdfs_verify.py`
- **Ruta en VM:** `/home/mikel/bigdata_hdfs_vm/hdfs_verify.py`
- **Alcance:** verifica **un** fichero (`alquiler_municipal.json`), no los 352. Para el gate completo hace falta LISTSTATUS + SHA de muestras.
- **Host VM:** `192.168.201.162` (SSH `mikel@192.168.201.162`, clave `C:/Users/mikel/.ssh/id_vm_hermes`)
- **Tamaño:** 505 bytes
- **Líneas:** 10
- **Modificación (stat VM):** 2026-11-06 17:42:43 +0000
- **SHA256 (`sha256sum` en VM):** `530ea11632a4e54ff57f00cc22d4a3941f4832fdf3a1dea023e227d858b109ff`
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
import hashlib
from pathlib import Path
from hdfs import InsecureClient
c=InsecureClient('http://10.22.87.215:50070', user='iabd-user15')
local=(Path.home()/'staging'/'raw'/'alquiler_municipal.json').read_bytes()
with c.read('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/alquiler_municipal.json') as r:
    remote=r.read()
print(hashlib.sha256(local).hexdigest())
print(hashlib.sha256(remote).hexdigest())
print('Igual?', hashlib.sha256(local).hexdigest()==hashlib.sha256(remote).hexdigest())
```
