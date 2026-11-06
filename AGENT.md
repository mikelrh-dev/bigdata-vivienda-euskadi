# AGENT.md — bigdata-vivienda-euskadi

## Stack
- Python 3.12 (`.venv`); extracción `requests`/`beautifulsoup4`/`lxml`; almacenamiento HDFS centro `http://10.22.87.215:50070` `iabd-user15`, streaming Kafka VM `192.168.201.162:9094` broker 4.3.1 KRaft topic 3 particiones, BD MongoDB (Docker) + PyMongo; análisis Aggregation Pipeline (9 pipelines); viz matplotlib/seaborn; contrato `pdf v2` más `docx Tema 8` como evaluación separada según `brief/RETO 1Evaluacion SBD-BDAv2.pdf` y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`.
- Detalle, layout, fuentes y estado por fase: `openspec/project.md`.

## Key facts
- Objetivo: qué municipios de Euskadi ofrecen mejor emancipación juvenil, con datos reales.
- Raw inmutable congelado (manifest 354), silver regenerado (manifest 185), 136 tests colectados (136 passed).
- Estado pesado, fases, preferencias y descubrimientos: Engram proyecto "bigdata-vivienda-euskadi" (obs 2988).

## Conventions
- Commits no deben identificar al agente en el mensaje.
- Otro agente trabaja en paralelo en el mismo repo → integrar con `git pull --rebase` y resolver conflictos.
- Preferencia: datos crudos/reales, sin valores simulados, con proxy de renta e imputación comarcal declarados según README y contrato; documentar avances en `openspec/audit`.
- `openspec/specs/contrato-reto/spec.md` es la verdad: si código y contrato discrepan, manda el contrato.
- Commits local-only; never `git push` sin orden explícita.
- Archivado Kafka 2026-11-06: `archive/kafka_2026-11-06/` (storage_kafka_*, scripts_publish_adapter/gate_bloque2, tests_test_kafka) — ignorar de momento, regenerar con la nueva estructura Windows>VM>Hadoop. Datos Kafka borrados: topic `anuncios_inmobiliarios` eliminado, colección `vivienda_euskadi.anuncios` vaciada (759>0).

## References
- Project spec: `openspec/project.md`
- Contrato: `openspec/specs/contrato-reto/spec.md`
- Fuentes profesora: `brief/RETO 1Evaluacion SBD-BDAv2.pdf` y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, mapa trazable docx en `openspec/specs/contrato-reto/spec.md` líneas 199-269
- Memory: Engram project "bigdata-vivienda-euskadi". Este archivo = solo punteros.
", "path">
C:/Users/mikel/Documents/bigdata-vivienda-euskadi/AGENT.md