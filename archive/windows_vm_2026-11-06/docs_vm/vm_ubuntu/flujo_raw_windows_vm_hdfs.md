# Flujo raw: Windows → Kafka → VM → Hadoop

**Fecha:** 2026-11-06
**Alcance:** `data/raw` (352 ficheros sin legacy). Mongo **no** participa en este flujo.
**Estado:** demostrado (352/352, SHA 3/3, LAG 0); queda cerrar la reproducibilidad (consumidor versionado y uploader con validaciones).

## Diagrama

```text
Windows
  data/raw/ (356; 352 sin legacy)
    ├─ storage/kafka_raw_producer.py ──manifiestos JSON──▶ Kafka
    └─ scp -r data/raw/ ────────────────────────────────▶ VM:~/staging/raw/ (356)

Kafka (VM, 3 particiones)
  topic anuncios_inmobiliarios · grupo hdfs_vm
    └─ consumidor Python (hoy heredoc) ──lee, filtra y commit──▶ (no sube)

VM
  ~/staging/raw/ (356)
    └─ kafka_hdfs_uploader.py ──WebHDFS put──▶ HDFS:.../data/raw (352)

HDFS
  /user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw
```

## 1. Windows: productor de manifiestos

Fichero: `storage/kafka_raw_producer.py`.

```bash
.venv/Scripts/python.exe storage/kafka_raw_producer.py
```

- Recorre `data/raw` y excluye `legacy_obsoleto_no_usar`.
- Por cada fichero publica en `anuncios_inmobiliarios` (`192.168.201.162:9094`) un JSON:

  ```json
  {"type":"raw_manifest","rel":"alquiler_municipal.json","size":154205,"sha256":"6f5af1b3...574b"}
  ```

- Clave del mensaje: `rel`. Valor: el JSON. **No envía los bytes.**
- 352 manifiestos (356 locales − 4 legacy).
- `produce(limit)` permite un subset: `... 10`.

## 2. Windows → VM: bytes por scp

```bash
scp -r data/raw/ mikel@192.168.201.162:~/staging/raw/
```

- 356 ficheros, ~861 MB.
- Kafka no lleva bytes: un CSV de 118 MB no cabe en `max.message.bytes=1048588`.
- Kafka decide **qué** subir y con qué SHA; `scp` lleva el **contenido**.
- En la VM: `~/staging/raw/` (356).

## 3. VM: consumidor Kafka

Estado actual: **heredoc**, no hay `.py`. Ver [`kafka_consumer.md`](kafka_consumer.md).

```bash
cd ~/bigdata_hdfs_vm && python3 - <<'PY'
import json
from kafka import KafkaConsumer

cons = KafkaConsumer(
    'anuncios_inmobiliarios',
    bootstrap_servers='192.168.201.162:9094',
    group_id='hdfs_vm',
    auto_offset_reset='earliest',
    enable_auto_commit=False,
)
n = 0
for msg in cons:
    m = json.loads(msg.value.decode())
    if m.get('type') == 'raw_manifest':
        n += 1
        cons.commit()
        if n % 50 == 0:
            print(f'manifests consumidos {n}')
print(f'TOTAL_MANIFESTS {n}')
cons.close()
PY
```

- Grupo `hdfs_vm`, `enable_auto_commit=False`.
- Filtra `type == "raw_manifest"` y hace `commit()` por mensaje.
- Evidencia: 362 mensajes, offsets 124/121/117, **LAG 0**.
- **No sube a HDFS**: solo cuenta y confirma.

## 4. VM → Hadoop: subida

Fichero: `~/bigdata_hdfs_vm/kafka_hdfs_uploader.py`.

```bash
cd ~/bigdata_hdfs_vm && python3 kafka_hdfs_uploader.py
```

Comportamiento **real**:

- `upload()` recorre `~/staging/raw` y hace `client.write()` a `/data/raw`.
- **No consume Kafka.**
- El bloque `if False` desactiva `upload_raw_excluding_legacy` (dedupe, estado y filtro legacy).
- `is_valid_rel` y `verify_staging` no se llaman; no comprueba SHA.
- Sube los 356 de staging, incluidos los 4 legacy, si se ejecuta tal cual.

Destino: `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw`.

## 5. Verificación

```bash
cd ~/bigdata_hdfs_vm && python3 hdfs_verify.py
```

- Compara `~/staging/raw/alquiler_municipal.json` con HDFS.
- Salida: `6f5af1b3...574b` dos veces + `Igual? True`.
- LISTSTATUS: 201 hijos top-level; 352 ficheros recursivos.
- Bytes: 895.596.949 en local y HDFS.

## Mapa de ficheros

| Lado | Ruta | Papel | Estado |
|---|---|---|---|
| Windows | `storage/kafka_raw_producer.py` | productor de manifiestos | activo |
| Windows | `data/raw/` | origen (356; 352 sin legacy) | activo |
| Windows | `storage/kafka_hdfs_uploader.py` | fuente del uploader | activo (fuente) |
| Windows | `storage/hdfs_utils.py` | librería HDFS; tests/recuperación | activo |
| VM | `~/staging/raw/` | bytes recibidos por scp | activo |
| VM | consumidor (heredoc) | lee manifiestos y commit | activo, **sin fichero** |
| VM | `~/bigdata_hdfs_vm/kafka_hdfs_uploader.py` | subida a HDFS | activo |
| VM | `~/bigdata_hdfs_vm/hdfs_verify.py` | verificación SHA | activo |
| VM | `~/bigdata_hdfs_vm/hdfs_utils.py` | librería con estado/SHA | **dormido** |
| HDFS | `.../data/raw` | destino | 352 ficheros |

## Evidencia

| Comprobación | Resultado |
|---|---|
| HDFS raw | 352/352, 0 missing/extra/mismatch |
| Bytes | 895.596.949 == 895.596.949 |
| SHA 3 muestras | `.FROZEN` 0 B, GTFS 347.791 B, CSV 118.793.174 B: 3/3 |
| Topic | 3 particiones, 362 mensajes |
| Grupo `hdfs_vm` | LAG 0 (124/121/117) |
| `hdfs_verify.py` | `6f5af1b3...574b` local == remoto |

## Huecos conocidos

1. El consumidor no está versionado: vive en un heredoc.
2. El uploader no consume Kafka y no valida SHA/rel; sube todo staging.
3. `hdfs_utils.py` está dormido: el `if False` impide usarlo.
4. No hay gate re-ejecutable que imprima offsets + LISTSTATUS + SHA.
5. `vm/` no está trackeado en git.

## Entorno VM

- `hdfs==2.7.3`, `kafka-python==2.2.3`, `python-dotenv`, `requests`, instalados con `pip --user`.
- No hay `.env` en `~/bigdata_hdfs_vm`; el código usa defaults.
- No hay CLI `hadoop`/`hdfs`; todo va por WebHDFS.

## Referencias

- `docs/trazabilidad_vm.md` (1537-1551).
- `docs/movimientos_hdfs_windows_vm.md`.
- [`kafka_consumer.md`](kafka_consumer.md), [`00_verificacion.md`](00_verificacion.md).
