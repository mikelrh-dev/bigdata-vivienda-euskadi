# Proposal: mongo-limpieza-crud-test

## Intent

test_clean_mongo y test_crud_demo están skipped sin MONGO_ALLOW_DESTRUCTIVE=1, así que las 4 operaciones de limpieza con nulos, duplicados, tipos y formato (RA1) y el CRUD con comprobación por código (RA3) no se prueban en la suite estándar.

## Scope

### In Scope
- Reescribir solo test_clean_mongo y test_crud_demo en tests/test_mongo.py para correr sobre la base de test vivienda_euskadi_test, con colección temporal y limpieza en finally.
- Insertar 3 documentos: código sin zfill, duplicado portal e id_anuncio, y precio string.
- Ejecutar canonicalize_codigo_ine, mark_nulls, resolve_duplicates, convert_types y demo_crud_operations solo sobre la temporal, con patch de clean_mongo.get_collection.
- Asertar matched_count, modified_count, deleted_count, códigos canonizados y conteo productivo intacto.

### Out of Scope
- Tocar storage/clean_mongo.py, storage/load_mongo.py, docs/modelo_mongodb.md, tests/test_mongo_geo.py y analysis/.
- Cambiar operaciones de producción o crear base de test nueva: MONGO_TEST_DB y get_test_db ya existen.

## Capabilities

### New Capabilities
- Ninguna.

### Modified Capabilities
- mongodb-y-analisis: PYMONGO-01 deja de exigir skipped; exige prueba no destructiva en base de test. LIMPIEZA-01 y TRANSFORM-01 ganan prueba con contadores.

## Approach

Patch temporal de clean_mongo.get_collection hacia get_test_db, datos sintéticos mínimos, aserciones estrictas de contadores y borrado de colecciones temporales al terminar. Sin skip y sin tocar producción.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| tests/test_mongo.py | Modified | Dos tests reescritos, helper de contexto temporal |
| openspec/changes/mongo-limpieza-crud-test/ | New | proposal, delta spec, design, tasks, verify-report |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Funciones de clean_mongo tocan producción | Low | Patch de get_collection limitado al contexto; verificación de conteo productivo antes y después |
| Contadores frágiles por orden de duplicado | Low | Ambos duplicados con precio string; fingerprints distintos |
| Base de test con restos de otra ejecución | Low | Drop de colecciones temporales antes y en finally |

## Rollback Plan

Revertir tests/test_mongo.py y eliminar la carpeta del cambio. La base de test es desechable; producción no se toca.

## Dependencies

- MongoDB local en marcha. Base vivienda_euskadi_test creada al primer acceso.

## Success Criteria

- [ ] .venv/Scripts/python.exe -m pytest tests/test_mongo.py -q reporta 25 passed y 0 skipped.
- [ ] Limpieza y CRUD dejan colección temporal eliminada y producción intacta.
