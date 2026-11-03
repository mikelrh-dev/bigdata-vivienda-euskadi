# Tasks: Fase MongoDB

## 1. Preparación

- [x] 1.1 Verificar conexión a MongoDB local (`localhost:27017`) y crear BD `vivienda_euskadi`.
  - Aceptación: `db.list_collection_names()` responde sin error.
- [x] 1.2 Canonicalizar `codigo_ine` a string de 5 dígitos en todos los loaders.
  - Aceptación: no hay `None` ni longitud != 5 en colecciones municipales.

## 2. Modelado

- [x] 2.1 Crear `docs/modelo_mongodb.md` con colecciones, embedding/referencing, BSON, índices, shard, transacciones.
  - Aceptación: documento revisado y coherente con `design.md`.

## 3. Carga

- [x] 3.1 Crear `storage/mongo.py` con `MongoClient` reutilizable y URI desde `.env`.
  - Aceptación: conexión singleton y manejo de errores.
- [x] 3.2 Crear `storage/load_mongo.py` con upserts idempotentes para `municipios`, `anuncios`, `alquiler_oficial`, `indicadores`.
  - Aceptación: re-ejecutar no duplica; conteos esperados (252, 759, 252/1569, 252).
- [x] 3.3 Verificar conteos y claves con `tests/test_mongo.py`.
  - Aceptación: tests en verde.

## 4. Limpieza PyMongo

- [x] 4.1 Implementar `storage/clean_mongo.py` con `update_many`, `$set`, `$unset`, `$convert`, contadores.
  - Aceptación: nulos marcados, no interpretados como cero; duplicados resueltos.

## 5. Consultas

- [x] 5.1 Implementar `analysis/mongo_queries.py` con filtros, dot notation, arrays, `$exists`, `$type`, regex, proyecciones, sort, limit.
  - Aceptación: cada consulta devuelve resultados coherentes y documentados.

## 6. Aggregation

- [x] 6.1 Implementar `analysis/mongo_aggregations.py` con ≥1 pipeline de ≥4 etapas e indicador por municipio.
  - Aceptación: pipeline ejecutable y resultado interpretable.

## 7. Índices

- [x] 7.1 Implementar `analysis/mongo_indexes.py` con `explain("executionStats")` before/after.
  - Aceptación: mejora demostrable (IXSCAN vs COLLSCAN).

## 8. Transacciones

- [x] 8.1 Documentar decisión de transacciones en `docs/modelo_mongodb.md`.
  - Aceptación: decisión razonada (atomicidad documental suficiente o transacción implementada).

## 9. Verificación

- [x] 9.1 Ejecutar `pytest tests/test_mongo.py -q`.
- [x] 9.2 Actualizar README con pasos de Mongo.
- [x] 9.3 Preparar demo (comandos + explicación).
"""