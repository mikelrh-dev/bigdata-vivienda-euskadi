# Proposal: fase-mongodb-mejora

## Intent
Mejorar la capa MongoDB sin Kafka/HDFS: homogeneizar claves, corregir tipos/flags, cargar datos huérfanos ya disponibles y ampliar pipelines/indices/tests.

## Scope
### In Scope
- Refactor `storage/load_mongo.py`: `_id=codigo_ine` en `alquiler_municipal` e `indicadores`; `idw_vecinos` como texto; `tiene_alquiler_oficial` derivado.
- Cargar colecciones huérfanas disponibles (ECVI, Udalmap indicadores/empleo, OSRM, emancipación resumen).
- Extender `clean_mongo.py` y pipelines/índices.
- Tests Mongo actualizados.

### Out of Scope
- Kafka, HDFS, Docker, nuevas extracciones externas.

## Capabilities
### New Capabilities
- `mongo-refactor-y-huerfanos`: carga y limpieza Mongo homogénea.

### Modified Capabilities
- `mongodb-y-analisis`: joins por `codigo_ine`, datos huérfanos.

## Approach
Refactor loaders, añadir loaders idempotentes para JSON/CSV huérfanos, recalcular joins, ampliar tests.

## Risks
- Rotura de tests/agregaciones por cambio de `_id`.
- Esquemas heterogéneos en datos huérfanos.
- Volumen de datos.

## Rollback Plan
Revertir commit; recargar Mongo desde silver original.

## Success Criteria
- [ ] `pytest tests/test_mongo.py` pasa.
- [ ] Colecciones nuevas cargadas con `_id` homogéneo cuando aplique.
- [ ] Pipelines/índices documentados con explain.
