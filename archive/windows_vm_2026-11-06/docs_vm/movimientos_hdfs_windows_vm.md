# Movimientos HDFS Windows->VM->Hadoop (bitácora + explicaciones)

Fecha: 2026-11-06 · Change: `2026-11-06-hdfs-windows-vm-kafka`
Flujo que marca la profesora: solo `data/raw` (sin silver), Kafka broker solo en la VM, Mongo solo en local Windows.

## Movimientos (en orden)

1. Borrar contenido de HDFS `raw` sin borrar la carpeta (Windows, WebHDFS directo).
   - Borrados 200/200 OK, `list /data/raw` vacío, `childrenNum=0`.
2. Archivar lo anterior (Windows): `storage/kafka_producer.py`, `storage/kafka_consumer.py`, `scripts/publish_adapter.py`, `scripts/gate_bloque2.py`, `tests/test_kafka.py` -> `archive/kafka_2026-11-06/`. Apuntado en `AGENT.md` como ignorar y regenerar.
3. Borrar topic `anuncios_inmobiliarios` en la VM y vaciar `vivienda_euskadi.anuncios` en Mongo (759>0). Restaurado productor `storage/kafka_producer.py`.
4. Env en la VM sin sudo: `get-pip.py --user` (pip 26.3), luego `~/.local/bin/pip install --user hdfs==2.7.3 kafka-python==2.2.3 requests==2.32.3 python-dotenv==1.0.1` (sin `python3-venv` por falta de `ensurepip` + sin `python3-pip` del sistema).
5. Copia mínima a la VM: `storage/hdfs_utils.py`, `kafka_raw_producer.py`, `kafka_hdfs_uploader.py`, `kafka_producer.py` a `~/bigdata_hdfs_vm/`; `mkdir -p ~/staging/raw`.
6. Bytes por scp: subset 10 (532K) y luego full `data/raw/` (861M, 356 ficheros) a `~/staging/raw/`. Kafka transporta solo manifiesto JSON (ficheros hasta 114M exceden `max.message.bytes=1048588`).
7. Topic recreado en la VM: `kafka-topics --create --topic anuncios_inmobiliarios --partitions 3`.
8. Manifiestos Windows>Kafka: 10 (offsets 0-3) y full 352 (offsets 115-123). Total 362 mensajes.
9. VM consume con grupo `hdfs_vm` (LAG 0, offsets 124/121/117): subset 10/10 y luego bulk full 352 con SHA y `read_file_sha256`.
10. HDFS final: `/data/raw` 201 top-level `childrenNum=201`, `fileId=2850772`, `alquiler_municipal.json` length 154205 SHA `6f5af1b3...` = local.

## Explicaciones

- Por qué Kafka no lleva bytes: un fichero de 114M no cabe en un mensaje Kafka (1M). Kafka orquesta (quién sube qué, con SHA); `scp` lleva los bytes. La VM es el intermediario físico que exige la profe.
- Por qué solo raw: raw es inmutable y registrable con SHA; silver es regenerable y no se sube por decisión firmada 2026-11-05.
- Por qué Mongo no entra en este flujo: Mongo es local Windows para análisis (PDF objetivo 5 queda fuera del change); el sink aquí es HDFS.
- Por qué `~/.local --user` y no venv: la VM no tiene `python3-pip`/`python3-venv` (sin `ensurepip`) y `sudo` pide contraseña. La vía `--user` instala los mismos pines sin apt.
