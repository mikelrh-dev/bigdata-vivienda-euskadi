# AGENT.md — bigdata-vivienda-euskadi

## Stack
- Python 3.12 (`.venv`); extracción `requests`/`beautifulsoup4`/`lxml`; almacenamiento HDFS (Docker), streaming Kafka (VM KRaft), BD MongoDB (Docker) + PyMongo; análisis Aggregation Pipeline; viz matplotlib/seaborn; contrato OpenSpec.
- Detalle, layout, fuentes y estado por fase: `openspec/project.md`.

## Key facts
- Objetivo: qué municipios de Euskadi ofrecen mejor emancipación juvenil, con datos reales.
- Raw inmutable congelado (manifest 353), silver regenerado (manifest 184), 130 tests colectados (130 passed).
- Estado pesado, fases, preferencias y descubrimientos: Engram proyecto "bigdata-vivienda-euskadi" (obs 2988).

## Conventions
- Commits no deben identificar al agente en el mensaje.
- Otro agente trabaja en paralelo en el mismo repo → integrar con `git pull --rebase` y resolver conflictos.
- Preferencia: datos crudos/reales, sin proxies ni imputaciones; documentar avances en `openspec/audit` y `plan_mejora`.
- `specs/contrato-reto/spec.md` es la verdad: si código y contrato discrepan, manda el contrato.
- Commits local-only; never `git push` sin orden explícita.

## References
- Project spec: `openspec/project.md`
- Contrato: `openspec/specs/contrato-reto/spec.md`
- Memory: Engram project "bigdata-vivienda-euskadi". Este archivo = solo punteros.
", "path">
C:/Users/mikel/Documents/bigdata-vivienda-euskadi/AGENT.md