# Proposal: mongo-hardening

## Intent
Endurecer capa datos+Mongo sin infra: integridad BSON (NaN/zfill), loads idempotentes, RA3 a 10 y provenance completa. Raw inmutable.

## Scope
### In Scope
- `storage/mongo.py`: `to_float("nan")` -> None.
- `storage/clean_mongo.py`: canonicalize con zfill real, clean_all 13 colecciones.
- `storage/load_mongo.py`: patron sin ventana vacia, provenance en base.
- `analysis/mongo_aggregations.py`: top/indicador con $sort/$limit en Mongo.
- Tests/docs higiene.
### Out of Scope
- HDFS, Kafka, RA4 graficos, matriz 252x252, Padron joven, Udalmap 10-15.

## Approach
Scripts Python + PyMongo, raw solo lectura, verify con pytest y explain.

## Risks
- NaN existentes requieren migracion una vez.
- Cambio canonicalize toca 8 colecciones.

## Rollback
Revert commit; recargar Mongo desde silver.

## Success Criteria
- [ ] pytest 108+ verde, NaN=0, codigo_ine 5 digitos 13/13.
- [ ] clean_all keys 13, pipelines con $sort/$limit en Mongo.
- [ ] provenance en base, git status limpio, docs actualizados.
