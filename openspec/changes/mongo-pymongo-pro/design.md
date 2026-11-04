# Design: PyMongo profesional — MONGO_URI y ObjectId

## Technical Approach

storage/mongo.py expone get_mongo_uri() que lee MONGO_URI del entorno en
tiempo de llamada. get_client() mantiene el lru_cache(maxsize=1) existente:
si hay URI devuelve MongoClient(uri, serverSelectionTimeoutMS=5000); si no,
devuelve MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000).
Se importa ObjectId de bson y se añaden dos helpers puros: is_objectid(value)
y to_objectid(value). get_collection y ping no cambian.

## Architecture Decisions

| Opción | Compromiso | Decisión |
|--------|------------|----------|
| URI cacheada en import vs leída en llamada | Import es más simple, pero impide monkeypatch | Leer en llamada: get_mongo_uri() sin cache |
| Solo test de URI o también fallback | El fallback es el comportamiento por defecto en local | Testear ambos ramas: URI falsa con mock y delenv con verificación host/port |
| Validación inline en tests vs helper reutilizable | Inline menos código | Helper is_objectid/to_objectid en storage/mongo.py para reuso en analysis |

## Data Flow

    env MONGO_URI ──→ get_mongo_uri() ──→ get_client() (lru_cache)
                                              │
                        MONGO_HOST/MONGO_PORT ┘  (fallback si no hay URI)
                                              ▼
                                   MongoClient ──→ get_db() ──→ get_collection()
                                              ▼
                                      ping() / queries

    _id de anuncios ──→ is_objectid() / to_objectid() (bson.ObjectId)

## File Changes

| File | Action | Description |
|------|--------|-------------|
| storage/mongo.py | Modify | MONGO_URI + fallback en get_client; ObjectId helpers; conserva lru_cache, get_collection, ping |
| tests/test_mongo_pymongo_pro.py | Create-tests | test_mongo_uri_configurable + test_anuncios_objectid |
| openspec/changes/mongo-pymongo-pro/ | New | proposal/spec/design/tasks/verify-report |

## Interfaces / Contracts

- get_mongo_uri() -> str | None: devuelve MONGO_URI sin espacios si está
  definida y no vacía; None en caso contrario.
- is_objectid(value) -> bool: True para instancia ObjectId o string válido
  de 24 hex (tras strip); False para None u otros tipos.
- to_objectid(value) -> ObjectId | None: convierte string válido a ObjectId;
  devuelve la instancia si ya es ObjectId; None si no es convertible.
- get_client() -> MongoClient: singleton con lru_cache(maxsize=1),
  serverSelectionTimeoutMS=5000 en ambas ramas.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Rama URI con mock de MongoClient | monkeypatch.setenv + patch, cache_clear antes/después |
| Unit | Rama fallback host/port | monkeypatch.delenv + patch, assert de args host/port |
| Integration | anuncios con _id ObjectId en vivo | ping + find_one + isinstance + helpers + límite de 5 |

## Threat Matrix

N/A — no hay routing, shell, subprocess, VCS/PR automation ni process
integration en este cambio.

## Migration / Rollout

No migration required. La URI es opcional; sin MONGO_URI el comportamiento
es el anterior (localhost:27017, vivienda_euskadi).

## Open Questions

Ninguna.
