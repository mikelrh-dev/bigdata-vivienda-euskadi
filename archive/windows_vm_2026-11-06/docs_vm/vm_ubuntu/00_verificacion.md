# 00 — Verificación HDFS desde la VM

**Flujo completo:** [`flujo_raw_windows_vm_hdfs.md`](flujo_raw_windows_vm_hdfs.md) · **Consumidor:** [`kafka_consumer.md`](kafka_consumer.md) · **Staging scp:** [`staging_scp.md`](../staging_scp.md)

Documentación verificable de la VM `192.168.201.162` y del clúster HDFS `10.22.87.215:50070`.
Todos los comandos son **solo lectura** (`ls`, `cat`, `sha256sum`, `LISTSTATUS`, `python3 hdfs_verify.py`).
La VM quedó con **3 `.py`** (`hdfs_utils.py`, `hdfs_verify.py`, `kafka_hdfs_uploader.py`). Se eliminaron las copias muertas `kafka_producer.py` y `kafka_raw_producer.py`; el productor real vive en Windows (`storage/kafka_raw_producer.py`).

## Parámetros

| Concepto | Valor |
|---|---|
| VM (SSH) | `mikel@192.168.201.162` |
| Clave SSH local | `C:/Users/mikel/.ssh/id_vm_hermes` |
| Directorio en VM | `/home/mikel/bigdata_hdfs_vm/` (a partir de `~/bigdata_hdfs_vm/`) |
| NameNode WebHDFS | `http://10.22.87.215:50070` |
| Usuario HDFS | `iabd-user15` |
| Ruta base HDFS | `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data` |
| Ruta raw HDFS | `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw` |
| Fichero de contraste SHA | `alquiler_municipal.json` (local `~/staging/raw/alquiler_municipal.json` ↔ HDFS `.../data/raw/alquiler_municipal.json`) |
| SHA256 esperado | `6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b` |

> Nota: en la VM no existe la CLI `hadoop`/`hdfs` (`which hdfs hadoop` → vacío,
> `hadoop: command not found`). La verificación se hace con WebHDFS (`curl`)
> y con `hdfs.InsecureClient` desde Python, que es lo que usa `hdfs_utils.py` y `hdfs_verify.py`.

## 1) Listado de los `.py` de la VM

Comando exacto (desde Windows, PowerShell o Git-Bash):

```bash
ssh -i C:/Users/mikel/.ssh/id_vm_hermes mikel@192.168.201.162 "ls -l ~/bigdata_hdfs_vm/"
```

Salida esperada (verificada el 2026-11-06):

```text
-rw-r--r-- 1 mikel mikel 6136 nov  6 17:01 hdfs_utils.py
-rw-rw-r-- 1 mikel mikel  505 nov  6 17:42 hdfs_verify.py
-rw-r--r-- 1 mikel mikel 2503 nov  6 17:01 kafka_hdfs_uploader.py
```

```bash
ssh -i C:/Users/mikel/.ssh/id_vm_hermes mikel@192.168.201.162 "ls -1 ~/bigdata_hdfs_vm/"
```

Salida esperada:

```text
hdfs_utils.py
hdfs_verify.py
kafka_hdfs_uploader.py
```

## 2) HDFS responde por WebHDFS (curl LISTSTATUS)

Comando exacto (dentro de la VM):

```bash
curl -s 'http://10.22.87.215:50070/webhdfs/v1/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw?op=LISTSTATUS&user.name=iabd-user15' | head -c 2000
```

Salida esperada (primeros bytes):

```json
{"FileStatuses":{"FileStatus":[
{"accessTime":1793984881279,"blockSize":134217728,"childrenNum":0,"fileId":2855278,"group":"iabd","length":0,"modificationTime":1793984881283,"owner":"iabd-user15","pathSuffix":".FROZEN","permission":"644","replication":3,"storagePolicy":0,"type":"FILE"},
{"accessTime":1793984881315,"blockSize":134217728,"childrenNum":0,"fileId":2855279,"group":"iabd","length":0,"modificationTime":1793984881317,"owner":"iabd-user15","pathSuffix":".gitkeep","permission":"644","replication":3,"storagePolicy":0,"type":"FILE"},
{"accessTime":1793984881348,"blockSize":134217728,"childrenNum":0,"fileId":2855280,"group":"iabd","length":405698,"modificationTime":1793984881394,"owner":"iabd-user15","pathSuffix":"ECVI_cifras_interanuales_es_2025T4.xlsx","permission":"644","replication":3,"storagePolicy":0,"type":"FILE"},
```

Comprobación de código HTTP:

```bash
curl -s -o /dev/null -w '%{http_code} %{url_effective}\n' 'http://10.22.87.215:50070/webhdfs/v1/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw?op=LISTSTATUS&user.name=iabd-user15'
```

Salida esperada:

```text
200 http://10.22.87.215:50070/webhdfs/v1/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw?op=LISTSTATUS&user.name=iabd-user15
```

Conteo vía curl + python3:

```bash
curl -s 'http://10.22.87.215:50070/webhdfs/v1/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw?op=LISTSTATUS&user.name=iabd-user15' | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d["FileStatuses"]["FileStatus"]))'
```

Salida esperada:

```text
201
```

## 3) Listar 201 entradas con InsecureClient

Comando exacto (dentro de la VM, sin `hadoop`):

```bash
cd ~/bigdata_hdfs_vm && python3 -c "
from hdfs import InsecureClient
c = InsecureClient('http://10.22.87.215:50070', user='iabd-user15')
lst = c.list('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw')
print('len=', len(lst))
print(lst[:5])
print(lst[-3:])
"
```

Salida esperada:

```text
len= 201
['.FROZEN', '.gitkeep', 'ECVI_cifras_interanuales_es_2025T4.xlsx', 'ECVI_es_2026T2.xlsx', 'ECVI_otros_inmuebles_2025T4.xlsx']
['udalmap_indicadores_adicionales.csv', 'udalmap_indicadores_adicionales.json', 'udalmap_vpo_terminadas.csv']
```

Equivalente en una sola línea (mismo resultado):

```bash
ssh -i C:/Users/mikel/.ssh/id_vm_hermes mikel@192.168.201.162 "python3 -c \"from hdfs import InsecureClient; c=InsecureClient('http://10.22.87.215:50070', user='iabd-user15'); print(len(c.list('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw')))\""
```

Salida esperada: `201`

## 4) childrenNum del directorio raw (y del padre data)

Comando exacto:

```bash
python3 -c "
from hdfs import InsecureClient
c = InsecureClient('http://10.22.87.215:50070', user='iabd-user15')
print(c.status('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw'))
"
```

Salida esperada (verificada):

```python
{'accessTime': 0, 'blockSize': 0, 'childrenNum': 201, 'fileId': 2850772, 'group': 'iabd', 'length': 0, 'modificationTime': 1793984973775, 'owner': 'iabd-user15', 'pathSuffix': '', 'permission': '755', 'replication': 0, 'storagePolicy': 0, 'type': 'DIRECTORY'}
```

Lectura:

- `childrenNum: 201` → el directorio `raw` contiene exactamente 201 hijos (coincide con `len(c.list(...))` y con el conteo `curl`).
- `type: DIRECTORY`, `permission: 755`, `owner: iabd-user15`.

Padre `data` (para distinguir):

```bash
python3 -c "
from hdfs import InsecureClient
c = InsecureClient('http://10.22.87.215:50070', user='iabd-user15')
print(c.list('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data'))
print(c.status('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data'))
"
```

Salida esperada:

```python
['raw']
{'accessTime': 0, 'blockSize': 0, 'childrenNum': 1, 'fileId': 2850393, 'group': 'iabd', 'length': 0, 'modificationTime': 1793819308659, 'owner': 'iabd-user15', 'pathSuffix': '', 'permission': '755', 'replication': 0, 'storagePolicy': 0, 'type': 'DIRECTORY'}
```

## 5) SHA byte a byte con hdfs_verify.py → Igual? True

Contenido de `~/bigdata_hdfs_vm/hdfs_verify.py` (ver `hdfs_verify.md`):

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

Comando exacto (dentro de la VM):

```bash
cd ~/bigdata_hdfs_vm && python3 hdfs_verify.py
```

Salida esperada (verificada el 2026-11-06):

```text
6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b
6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b
Igual? True
```

Los dos SHA son idénticos byte a byte: local `~/staging/raw/alquiler_municipal.json`
vs. HDFS `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/alquiler_municipal.json`.

Contraste adicional del fichero local (misma hash):

```bash
ls -l ~/staging/raw/alquiler_municipal.json
sha256sum ~/staging/raw/alquiler_municipal.json
```

Salida esperada:

```text
-r--r--r-- 1 mikel mikel 154205 nov  6 17:02 /home/mikel/staging/raw/alquiler_municipal.json
6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b  /home/mikel/staging/raw/alquiler_municipal.json
```

## 6) Secuencia completa de verificación (una sola sesión SSH)

```bash
ssh -i C:/Users/mikel/.ssh/id_vm_hermes mikel@192.168.201.162
# Dentro de la VM:
cd ~/bigdata_hdfs_vm
ls -l
python3 -c "
from hdfs import InsecureClient
c=InsecureClient('http://10.22.87.215:50070', user='iabd-user15')
lst=c.list('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw')
print('len=', len(lst))
print(c.status('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw'))
"
python3 hdfs_verify.py
ls -l ~/staging/raw/alquiler_municipal.json
sha256sum ~/staging/raw/alquiler_municipal.json
curl -s -o /dev/null -w '%{http_code}\n' 'http://10.22.87.215:50070/webhdfs/v1/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw?op=LISTSTATUS&user.name=iabd-user15'
exit
```

Resultados esperados juntos:

```text
len= 201
{'accessTime': 0, 'blockSize': 0, 'childrenNum': 201, 'fileId': 2850772, ... 'type': 'DIRECTORY'}
6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b
6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b
Igual? True
200
```

## Criterio de aceptación

- `len(c.list(.../data/raw)) == 201`
- `c.status(.../data/raw)['childrenNum'] == 201`
- `curl LISTSTATUS` devuelve 201 `FileStatus` y HTTP `200`
- `python3 hdfs_verify.py` imprime dos veces `6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b` e `Igual? True`

Si lo anterior se da, HDFS funciona correctamente desde la VM.

## 7) Verificación Windows sin VM (2026-11-06, Kafka centro)

El mismo HDFS queda verificado sin VM desde Windows:

- Broker centro `10.22.87.215:9092`, grupo `hdfs_centro`, topic `anuncios_inmobiliarios`.
- Consumer: `storage/kafka_hdfs_uploader.py` (antes `hdfs_vm`/staging, ahora `hdfs_centro` + `data/raw` local + `InsecureClient('http://10.22.87.215:50070')`).
- Offsets consumidos `0:153-0:353` (201 de esta corrida; 352 raw_manifest en total), grupo offset `354` LAG 0.
- LISTSTATUS `/user/.../data/raw`: `childrenNum=201`, LIST 201 top-level.
- SHA `alquiler_municipal.json`: `6f5af1b35deaf01f9cc264589284fcc29f5b3aadefd55381eb118a9dcf79574b` local==remoto.
- Detalle en `docs/trazabilidad_vm.md` sección `2026-11-06 Kafka centro Windows>Kafka>HDFS sin VM`.
