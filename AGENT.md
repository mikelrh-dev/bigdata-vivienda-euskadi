# AGENT.md — bigdata-vivienda-euskadi

## Stack
- Python 3.12 (`.venv`); extracción `requests`/`beautifulsoup4`/`lxml`; almacenamiento HDFS centro `http://10.22.87.215:50070` `iabd-user15` (352 ficheros raw canónicos en `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw`; manifest local 354 SHA con 2 alias legacy), streaming Kafka clúster centro `10.22.87.215:9092` topic vigente `vivienda_euskadi` 1 partición RF 1 (grupo `hdfs_centro`; topic viejo `anuncios_inmobiliarios` eliminado 2026-11-06), BD MongoDB local (HDFS centro + Mongo local sin Docker Compose en repo) + PyMongo (16 vivas + 14 `__backup` = 30 totales); análisis Aggregation Pipeline (11 pipelines en `analysis/run_analisis_mongo.py` `PIPELINE_ORDER`, antes 10) con `explain()` COLLSCAN 594 → IXSCAN 1 (índice ESR en `analysis/mongo_indexes.py`); viz matplotlib/seaborn; contrato `pdf v2` más `docx Tema 8` como evaluación separada según `brief/RETO 1Evaluacion SBD-BDAv2.pdf` y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`.
- Detalle, layout, fuentes y estado por fase: `openspec/project.md`.

## Key facts
- Objetivo: qué municipios de Euskadi ofrecen mejor emancipación juvenil, con datos reales.
- Raw inmutable congelado (352 en HDFS, manifest local 354 SHA), silver 188, 238 tests colectados (236 passed, 2 skipped). Gobernanza `scripts/verificar_gobernanza.py` TODO OK: 46 requisitos con ID, 45 scripts en `transform/` con 34 en el DAG, 11 pipelines, 0 env sin declarar (`KAFKA_NUM_PARTITIONS`/`KAFKA_REPLICATION_FACTOR` declaradas en `.env.example`). Anuncios vigentes 594 (843 raw → 594 tras dedup + cuarentena 45; 759 histórico pre-v5). Artefactos: 8 CSV `mongo_*` + 28+8 PNG (28 resultados + 8 anexo). CI en rama `master` (`.github/workflows/quality-gate.yml`; gate vivo solo manual `GATE_LIVE=1`). FAIL 07 conocido en `verificar_fase_datos.py` (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26) documentado sin enmascarar: no tocar datos para forzarlo.
- Estado pesado, fases, preferencias y descubrimientos: Engram proyecto "bigdata-vivienda-euskadi" (obs 2988).

## Conventions
- Commits no deben identificar al agente en el mensaje.
- Otro agente trabaja en paralelo en el mismo repo → integrar con `git pull --rebase` y resolver conflictos.
- Preferencia: datos crudos/reales, sin valores simulados, con proxy de renta e imputación comarcal declarados según README y contrato; documentar avances en `openspec/audit`.
- `openspec/specs/contrato-reto/spec.md` es la verdad: si código y contrato discrepan, manda el contrato.
- Commits local-only; never `git push` sin orden explícita.
- Archivado Kafka 2026-11-06: `archive/kafka_2026-11-06/` (storage_kafka_*, scripts_publish_adapter/gate_bloque2, tests_test_kafka) — ignorar: la cadena vigente es Windows>Kafka centro>Hadoop (`storage/kafka_raw_producer.py` → `storage/kafka_hdfs_uploader.py`). Datos Kafka borrados: topic `anuncios_inmobiliarios` eliminado, colección `vivienda_euskadi.anuncios` vaciada (759>0, cifra histórica pre-v5; vigente 594/843).

## References
- Project spec: `openspec/project.md`
- Contrato: `openspec/specs/contrato-reto/spec.md`
- Fuentes profesora: `brief/RETO 1Evaluacion SBD-BDAv2.pdf` y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, mapa trazable docx en `openspec/specs/contrato-reto/spec.md` líneas 199-269
- Memory: Engram project "bigdata-vivienda-euskadi". Este archivo = solo punteros.
", "path">
C:/Users/mikel/Documents/bigdata-vivienda-euskadi/AGENT.md