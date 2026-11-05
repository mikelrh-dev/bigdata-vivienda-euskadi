# Design: bloque-2-integracion-hdfs-kafka

## Technical Approach

Cerrar el bloque 2 del plan `plan/PLAN_10.md` (pasos 5, 6 y 7) sin regresión: dejar HDFS procesado listo en local con `--dry-run` sin subirlo hasta autorización de la profesora, ejecutar productor/consumidor Kafka Python contra el broker vivo de la VM con los 759 anuncios reales, y encadenar un gate extremo a extremo con 10 anuncios de prueba que termina consultable en MongoDB por `codigo_ine`. Todo comando en VM/HDFS queda en `docs/trazabilidad_vm.md`. Sin código nuevo salvo entrypoint `--dry-run` no destructivo (`scripts/upload_procesado.py`, solo lista; cero escrituras).

Limitación dura: el raw congelado de 353 ficheros no se toca; solo se lista y se verifica SHA. El procesado no se sube a HDFS en esta fase.

## Architecture Decisions

| Decision | Options | Tradeoff |
|---|---|---|
| HDFS procesado | Listo en local + `--dry-run` (elegido) vs subir ya a HDFS | Subirlo ahora rompería la restricción (sin confirmación profesora) y el raw es lo único en HDFS; dry-run deja el entrypoint verificable y reversible |
| Kafka vivo | Python con 759 reales (elegido) vs console-producer/consumer | Console solo prueba el transporte; Python demuestra producer/consumer, claves `portal:id_anuncio`, callback con metadata y upsert, que es lo que exige KAFKA-01 |
| Gate e2e | 10 anuncios de prueba con upsert (elegido) vs re-publicar los 759 | 10 basta para demostrar el flujo completo sin duplicar ni cargar la colección; el upsert por `portal`/`id_anuncio` garantiza idempotencia |
| Orden de ejecución | HDFS dry-run → Kafka 759 → gate 10 (elegido) vs gate primero | El gate depende del topic con datos y de MongoDB reachable; verificar por capas evita diagnosticar a ciegas |
| Trazabilidad | Entrada por comando en `docs/trazabilidad_vm.md` (elegido) vs solo log en consola | La rubrica exige trazabilidad total VM; sin entrada en el `.md` la evidencia no existe |

## Data Flow

    data/procesado/anuncios_unificados.csv (759)
        │  storage.kafka_producer (clave portal:id_anuncio, callback metadata)
        ▼
    Topic anuncios_inmobiliarios (3 particiones, VM 192.168.201.162:9094)
        │  storage.kafka_consumer (grupo anuncios, auto-commit manual)
        ▼
    MongoDB anuncios (upsert por portal:id_anuncio)
        │  consulta por codigo_ine → huella SHA
        ▼
    Gate: 10 anuncios de prueba → insertados y consultables

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `docs/trazabilidad_vm.md` | Modify | Una entrada por comando VM/HDFS (fecha/objetivo/máquina/comando/salida/conclusión) |
| `openspec/changes/bloque-2-integracion-hdfs-kafka/design.md` | Create | Este diseño |
| `openspec/changes/bloque-2-integracion-hdfs-kafka/tasks.md` | Create | Tareas 5, 6 y 7 con verificación |
| `storage/hdfs_utils.py` | Use | `DEFAULT_HDFS_URL` + `InsecureClient`; no se modifica en esta fase salvo dry-run |
| `scripts/upload_procesado.py` | Create | Entrypoint `--dry-run`: lista procesado local (ficheros/bytes/SHA) sin subir (cero escrituras); sin `--dry-run` rehúsa (sin profesora) |
| `storage/kafka_producer.py` | Use | Publica 759 con metadata (topic/partition/offset) |
| `storage/kafka_consumer.py` | Use | Upsert en Mongo como grupo `anuncios` |
| `scripts/run_mongo_pipeline.py` | Reference | Entrypoint de carga/limpieza; no se ejecuta completo en el gate de 10 |

## Interfaces / Contracts

- HDFS: centro `http://10.22.87.215:50070`, usuario `iabd-user15`, base `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data`. Raw congelado 353 ficheros, solo lectura y SHA.
- Kafka: `192.168.201.162:9094`, topic `anuncios_inmobiliarios`, 3 particiones, grupo `anuncios`. Clave `portal:id_anuncio`, valor JSON con precio y municipio.
- MongoDB: colección `anuncios`; upsert por `portal` + `id_anuncio`; gate consultable por `codigo_ine`.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| HDFS dry-run | Local vs HDFS sin subir procesado | LISTSTATUS + comparación de ficheros y SHA |
| Kafka 759 | Productor publica con metadata | 759 enviados, offsets ≥ 759, grupo describe |
| Gate 10 | Flujo completo hasta Mongo | 10 insertados consultables por `codigo_ine`, huella SHA |
| Regresión | Sin ruptura offline | `pytest tests/test_contrato.py` 54 passed + manifest 353/184 |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration required. Solo se añade trazabilidad y se ejecuta el flujo vivo; el procesado queda pendiente de subida hasta confirmación de la profesora.

## Open Questions

- Ninguna bloqueante. Pendiente solo la autorización de la profesora para subir el procesado a HDFS.
