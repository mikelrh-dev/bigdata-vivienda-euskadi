# VM — documentación

Documentación de la VM `192.168.201.162` y del flujo raw, separada por máquina.

## `ubuntu/` — VM (Ubuntu Server)

| Documento | Contenido |
|---|---|
| [`flujo_raw_windows_vm_hdfs.md`](ubuntu/flujo_raw_windows_vm_hdfs.md) | Flujo completo Windows → Kafka → VM → Hadoop (runbook de la VM) |
| [`kafka_consumer.md`](ubuntu/kafka_consumer.md) | Consumidor Kafka (heredoc actual; pendiente de versionar) |
| [`00_verificacion.md`](ubuntu/00_verificacion.md) | Verificación read-only de HDFS desde la VM |
| [`kafka_hdfs_uploader.md`](ubuntu/kafka_hdfs_uploader.md) | Uploader VM → HDFS (con su estado real) |
| [`hdfs_utils.md`](ubuntu/hdfs_utils.md) | Librería HDFS (dormida en la VM) |
| [`hdfs_verify.md`](ubuntu/hdfs_verify.md) | Verificación SHA de un fichero |

## `windows/` — Windows

| Documento | Contenido |
|---|---|
| [`kafka_raw_producer.md`](windows/kafka_raw_producer.md) | Productor de manifiestos (Windows) |

## Ficheros que quedan en la VM

`~/bigdata_hdfs_vm/`:

```text
hdfs_utils.py
hdfs_verify.py
kafka_hdfs_uploader.py
```

## Aviso

`vm/` no está trackeado en git (`git status` → `?? vm/`). Pendiente de añadir.
