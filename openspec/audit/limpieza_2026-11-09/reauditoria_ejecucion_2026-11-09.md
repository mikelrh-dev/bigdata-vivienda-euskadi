# Reauditoría tras limpieza — 2026-11-09

## Alcance ejecutado

Se conservaron, por indicación expresa:

- `graphify-out/` — **67 archivos** de caché, intactos.
- `notebooks/Kafka_Ejercicio.ipynb` — intacto.

Se retiraron **59 archivos**:

- **48 borrados**: 30 renders de demo, 7 one-offs de `scratchpad`, 7 archivos DuckDB/código, 1 log y 3 metadatos locales (`.atl/` y `.freebuff/project-id`).
- **11 archivados**: 10 backups de `scratchpad/` y 1 documento resuelto de DuckDB → PyMongo.

No se retiraron los 9 archivos de edición/revisión (README, `run_all.py`, documentación y referencias históricas).

## Destinos del archivo

- `archive/scratchpad/backup_t3prev/` — 5 archivos.
- `archive/scratchpad/p1-1_backup_2026-11-07/` — 5 archivos.
- `docs/archive/2026-11/pendiente_duckdb_pymongo_2026-11-05.md` — 1 archivo.

El detalle previo está en `plan_retirada.md`; esta ejecución excluye Graphify y el notebook y añade los 3 metadatos opcionales.

## Ajustes de referencias

- `README.md`: retirado el paso 5 de los dashboards DuckDB; ahora apunta a `analysis/run_analisis_mongo.py`.
- `transform/run_all.py`: eliminadas las 3 entradas de `EXCLUIDOS` de los scripts borrados.
- `scripts/verificar_gobernanza.py`: el conteo canónico de `transform/` pasa de 45 a **42 scripts** (34 en el DAG).
- `AGENT.md`, `README.md`, `docs/arquitectura_datos.md`, `docs/guion_defensa.md`: actualizados los conteos a **235 passed / 237 collected / 42 scripts**.
- `docs/README.md`, `docs/analisis_vault_vs_rubrica.md` y `docs/auditoria_10_10_SDD_2026-11-05.md`: retiradas las referencias activas a los generadores DuckDB borrados.
- `.gitignore`: eliminadas las reglas específicas de `launch_duckdb_ui.py` y `scratchpad/auditoria_duckdb.md`.

## Verificación

| Check | Resultado |
|---|---|
| `pytest tests -q` | **235 passed, 2 skipped**; 237 collected; exit 0 |
| `scripts/verificar_gobernanza.py` | **TODO OK**: 46 requisitos, 42 scripts, 34 DAG, 188 silver, 0 env sin declarar, 11 pipelines; exit 0 |
| `transform/run_all.py --check` | **34/34 OK**; exit 0 |
| `scripts/gate_extremo_a_extremo.py --offline` | **OK**: 354 SHA raw, 188 silver, 14 colecciones, 0 duplicados, lag 0; exit 0 |
| `scripts/verificar_fase_datos.py` | 17 PASS + **FAIL 07 conocido** (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26); exit 1. No es una regresión de la limpieza y no se tocó `data/` para forzarlo |
| `git diff --check` | Sin errores |
| Referencias activas a lo retirado | Ninguna en código, tests, scripts o documentación activa |

## Límites de la verificación

- El gate vivo de HDFS/Kafka no se ejecutó: el gate offline lo deja declarado como `PENDA-01`; la comprobación viva requiere el clúster del centro.
- `pytest` se ejecutó en el entorno local con los dobles/mocks habituales; no sustituye una prueba contra MongoDB, HDFS o Kafka reales.
- El `FAIL 07` de `verificar_fase_datos.py` es preexistente y está documentado; la limpieza no modificó datos ni imputaciones.

## Estado del árbol

No se ha hecho commit ni push. Permanecen cambios previos no relacionados con esta limpieza (`extract/26_vpo_terminadas.py`, cambios de `openspec/changes/...` y artefactos de auditoría), que no se tocaron.
