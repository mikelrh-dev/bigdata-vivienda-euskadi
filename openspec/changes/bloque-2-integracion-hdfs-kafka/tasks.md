# Tasks: bloque-2-integracion-hdfs-kafka

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | Fix Future en `storage/kafka_producer.py` + `tests/test_kafka.py` + design/tasks + trazabilidad (documentado en verify-report) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Una única entrega de solo artefactos; la evidencia viva va en trazabilidad |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|------|------|----------------------|-----------------|-------------------|
| 1 | HDFS dry-run + Kafka 759 + gate 10 | `pytest tests/test_contrato.py -q` | Comandos Kafka/HDFS por tarea | Solo `docs/trazabilidad_vm.md` |

## Phase 1: HDFS procesado listo sin subir (paso 5)

- [x] 1.1 Listar procesado local vs HDFS: inventario local con SHA + LISTSTATUS WebHDFS con `storage/hdfs_utils.py` (`DEFAULT_HDFS_URL` `http://10.22.87.215:50070`, `iabd-user15`). Aceptación: lista local firmada, raw 353 intacto, cero escrituras. Verificación: `get_client().status('/user/iabd-user15/bigdata_reto/vivienda_euskadi/data')`.
- [x] 1.2 Ejecutar `--dry-run` de subida procesado: debe listar lo que subiría (ficheros, bytes, SHA). Aceptación: salida completa, cero escrituras; no subir sin profesora. Verificación: `.venv/Scripts/python.exe scripts/upload_procesado.py --dry-run` + captura en trazabilidad.
- [x] 1.3 Registrar cada comando en `docs/trazabilidad_vm.md` (fecha/objetivo/máquina/comando/salida/conclusión). Aceptación: entradas 1.1–1.2 firmadas. Verificación: `git status --short`.

## Phase 2: Kafka Python con 759 reales (paso 6)

- [x] 2.1 Listar topic, offsets y grupos sobre `192.168.201.162:9094`. Aceptación: `anuncios_inmobiliarios` con 3 particiones. Verificación: `kafka-topics.sh --describe --bootstrap-server 192.168.201.162:9094`.
- [x] 2.2 Ejecutar productor con metadata: `storage/kafka_producer.py` sobre 759 (clave `portal:id_anuncio`). Aceptación: 759 enviados con `topic/partition/offset`. Verificación: `python -m storage.kafka_producer` + `kafka-get-offsets` >= 759.
- [x] 2.3 Ejecutar consumidor con upsert: grupo `anuncios`, commit manual, upsert por `portal`/`id_anuncio`. Aceptación: 759 procesados sin duplicar. Verificación: `python -m storage.kafka_consumer` + `kafka-consumer-groups.sh --group anuncios --describe`.

## Phase 3: Gate extremo a extremo con 10 (paso 7)

- [x] 3.1 Publicar 10 anuncios de prueba (subset determinista) con el productor. Aceptación: 10 con metadata. Verificación: offsets antes/después.
- [x] 3.2 Consumir con upsert sin duplicar. Aceptación: Mongo >= 759 y los 10 recuperables. Verificación: `python -m storage.kafka_consumer` + conteo en `anuncios`.
- [x] 3.3 Verificar en Mongo por `codigo_ine` y huella SHA. Aceptación: 10 consultables por `codigo_ine` con SHA firmado. Verificación: consulta por `codigo_ine` + SHA en trazabilidad.

## Phase 4: Regresión y cierre

- [x] 4.1 Regresión offline: 54 passed + manifest 353/184 sin tocar data/raw. Aceptación: verde y raw intacto. Verificación: `pytest tests/test_contrato.py -q`.
- [x] 4.2 Cierre sin subir procesado y evidencia en trazabilidad. Aceptación: diff solo en `openspec/changes/bloque-2-integracion-hdfs-kafka/*`, `docs/trazabilidad_vm.md`, entrypoints `scripts/upload_procesado.py`/`publish_adapter.py`/`gate_bloque2.py`/`hdfs_recuperacion_un_fichero.py` y fix Future en `storage/kafka_producer.py` + `tests/test_kafka.py` (kafka-python 2.2.3, gate `e32c3d3…faf25`); sin `data/` ni `data/raw`. Verificación: `git status --short` sin `data/`.
