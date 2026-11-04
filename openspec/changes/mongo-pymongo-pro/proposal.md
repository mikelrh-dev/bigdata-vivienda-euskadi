# Proposal: PyMongo profesional — MONGO_URI configurable y ObjectId

## Intent

Cerrar el requisito PYMONGO-PRO-01 (Tema 8 secciones 12 y 16): el cliente de
MongoDB debe leerse desde MONGO_URI con fallback a MONGO_HOST/MONGO_PORT, y
anuncios debe usar ObjectId con validación reutilizable, en lugar de la
conexión hardcodeada a host/port sin lectura de URI.

## Scope

### In Scope
- `storage/mongo.py`: lectura de MONGO_URI en tiempo de llamada, fallback a
  host/port; import y helpers `is_objectid` / `to_objectid`; mantener
  `lru_cache`, `get_collection` y `ping`.
- `tests/test_mongo_pymongo_pro.py`: test_mongo_uri_configurable con
  monkeypatch de URI falsa y verificación de fallback sin URI; y
  test_anuncios_objectid con ping en vivo, `_id` isinstance ObjectId,
  `is_objectid` y `to_objectid`.

### Out of Scope
- La corrección del except silencioso en `storage/load_mongo.py`: queda para
  la próxima ronda.
- Tocados prohibidos: `storage/load_mongo.py`, `storage/clean_mongo.py`,
  `docs/`, `tests/test_mongo.py`.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `mongodb-y-analisis`: el requisito PYMONGO-PRO-01 pasa de descrito a
  implementado y verificado (MONGO_URI configurable, fallback, ObjectId).

## Approach

get_mongo_uri() lee MONGO_URI del entorno en tiempo de llamada (no cacheada
en import, visible para monkeypatch); get_client() con lru_cache usa la URI
cuando existe y cae a MongoClient(MONGO_HOST, MONGO_PORT) en caso contrario.
is_objectid acepta instancias ObjectId y strings de 24 hex; to_objectid
convierte strings válidos y devuelve None en el resto.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| storage/mongo.py | Modified | get_client + get_mongo_uri + ObjectId helpers |
| tests/test_mongo_pymongo_pro.py | New-style tests | URI configurable + ObjectId en anuncios |
| openspec/changes/mongo-pymongo-pro/ | New | proposal.md, spec.md, design.md, tasks.md |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cache lru_cache oculta monkeypatch | Med | get_client.cache_clear() en tests; URI leída en tiempo de llamada |
| Fallback roto si MONGO_URI vacío | Bajo | get_mongo_uri devuelve None si el env está vacío o en blanco |

## Rollback Plan

Revertir storage/mongo.py a MongoClient(MONGO_HOST, MONGO_PORT) y borrar
tests/test_mongo_pymongo_pro.py; el resto del sistema no depende de estos
helpers.

## Dependencies

Ninguna nueva. PyMongo 4 ya está instalado.

## Success Criteria

- [ ] .venv/Scripts/python.exe -m pytest tests/test_mongo_pymongo_pro.py tests/test_mongo_geo.py -q reporta exit 0.
- [ ] MONGO_URI configurable con fallback verificado por monkeypatch.
- [ ] anuncios con _id ObjectId validado por is_objectid / to_objectid.
