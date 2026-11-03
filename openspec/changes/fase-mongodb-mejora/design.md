# Design: fase-mongodb-mejora

## Approach
- Refactor `load_mongo.py` para upserts con `_id=codigo_ine`.
- Añadir loaders para JSON huérfanos normalizados (ECVI, Udalmap, OSRM, emancipación).
- Extender `clean_mongo.py` con marcado de nulos y tipos.
- Actualizar `mongo_aggregations.py` para joins por `codigo_ine`.
- Añadir índices compuestos en colecciones nuevas.
- Tests en `tests/test_mongo.py`.
