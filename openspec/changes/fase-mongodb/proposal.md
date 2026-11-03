# Proposal: Fase MongoDB — modelado, PyMongo y análisis

## Intent

Cerrar el bloque SBD-RA3 del reto: base de datos MongoDB con modelo justificado,
operaciones PyMongo automatizadas y comprobadas, consultas avanzadas, Aggregation
Pipeline, índices con `explain()`, decisión de transacciones y PyMongo profesional.
La capa silver (`data/procesado/`) ya está lista y será la fuente de carga.

## Scope

### In Scope

- `storage/mongo.py`: `MongoClient` reutilizable, URI desde `.env`, helpers.
- `storage/load_mongo.py`: carga idempotente desde silver a colecciones.
- `storage/clean_mongo.py`: limpieza/transformación con operaciones PyMongo.
- `analysis/mongo_queries.py`: consultas avanzadas.
- `analysis/mongo_aggregations.py`: pipelines con ≥4 etapas.
- `analysis/mongo_indexes.py`: `explain("executionStats")` before/after.
- `docs/modelo_mongodb.md`: justificación de modelo, BSON, índices, shard, transacciones.
- `tests/test_mongo.py`: verificación de conteos, consultas, agregación.

### Out of Scope

- Kafka e integración end-to-end (fase posterior).
- HDFS (ya accesible; se implementa aparte).
- Cambios en `data/raw/` o `data/procesado/`.

## Capabilities

### New Capabilities

- `mongodb-modelado-pymongo`: modelo documental + operaciones + consultas + aggregation + índices.

### Modified Capabilities

- `mongodb-y-analisis`: pasa de Pendiente a parcial/implementado.

## Approach

Usar la instancia local de MongoDB (`localhost:27017`, BD `vivienda_euskadi`), cargar
silver mediante upserts idempotentes por `codigo_ine`/`id_anuncio`, y demostrar cada
criterio con código y tests. No forzar transacciones artificiales; justificar
atomicidad documental.

## Risks

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| `codigo_ine` no string en algún artefacto | Med | canonicalizar en loader |
| Campos sparse (coordenadas, barrio) | Med | marcar nulos, no imputar |
| Índice sin mejora real | Bajo | medir con explain antes/después |
| Sobrecargar `municipios` | Med | generar indicadores en aggregation, no denormalizar |

## Success Criteria

- [ ] 4+ colecciones cargadas con conteos esperados.
- [ ] CRUD/limpieza con contadores verificados.
- [ ] Consultas con anidados/arrays/$exists/$type/regex.
- [ ] ≥1 pipeline con ≥4 etapas y indicador por municipio.
- [ ] ≥1 índice con mejora demostrable en explain.
- [ ] Decisión de transacciones documentada.
- [ ] `pytest` en verde.
- [ ] README actualizado con pasos de Mongo.
"""