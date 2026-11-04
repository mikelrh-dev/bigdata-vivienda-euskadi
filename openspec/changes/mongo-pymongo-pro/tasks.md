# Tasks: PyMongo profesional — MONGO_URI y ObjectId

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~80 (storage/mongo.py helpers + 2 tests) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | MONGO_URI + fallback + ObjectId helpers + tests | PR 1 | .venv/Scripts/python.exe -m pytest tests/test_mongo_pymongo_pro.py tests/test_mongo_geo.py -q | ping en vivo contra MongoDB local en test_anuncios_objectid | storage/mongo.py + tests/test_mongo_pymongo_pro.py |

## Phase 1: Implementación

- [x] 1.1 Añadir lectura de MONGO_URI con fallback a MONGO_HOST/MONGO_PORT en get_client() de storage/mongo.py, manteniendo lru_cache, get_collection y ping.
  - Aceptación: get_mongo_uri() visible a monkeypatch; rama URI y rama fallback verificadas por mock.
- [x] 1.2 Importar ObjectId y añadir helpers is_objectid / to_objectid reutilizables en storage/mongo.py.
  - Aceptación: is_objectid acepta instancia y string de 24 hex; to_objectid convierte o devuelve None.

## Phase 2: Testing

- [x] 2.1 Crear tests/test_mongo_pymongo_pro.py::test_mongo_uri_configurable con monkeypatch de URI falsa y verificación de fallback sin URI.
  - Aceptación: MongoClient invocado con URI en una rama y con host/port en la otra (serverSelectionTimeoutMS=5000).
- [x] 2.2 Crear tests/test_mongo_pymongo_pro.py::test_anuncios_objectid con ping en vivo, find_one con isinstance ObjectId, is_objectid y to_objectid.
  - Aceptación: _id es ObjectId; helpers validan instancia, string y rechazan valores inválidos.

## Phase 3: Verificación

- [x] 3.1 Ejecutar .venv/Scripts/python.exe -m pytest tests/test_mongo_pymongo_pro.py tests/test_mongo_geo.py -q y confirmar exit 0.
  - Aceptación: comando de verificación en verde, sin commit.
