# Proposal: mongo-safe-load

## Intent

Eliminar la ventana vacía y el borrado irreversible de las 11 cargas con drop() en storage/load_mongo.py, sin tocar HDFS ni Kafka. Raw inmutable.

## Scope

### In Scope

- `storage/mongo.py`: zfill_ine con int(float(x)) para floats como 20069.0; constante MONGO_TEST_DB.
- `storage/load_mongo.py`: patrón staging + backup + rename para las 11 colecciones con drop; si docs está vacío, no se toca la original.
- `tests/test_mongo.py`: test_clean_mongo y test_crud_demo solo con MONGO_ALLOW_DESTRUCTIVE=1; nuevo test de zfill con float.
- `analysis/mongo_indexes.py`: recreación documentada de índices tras el swap, sin cambio de conducta.

### Out of Scope

- HDFS, Kafka, RA4 gráficos, cobertura municipal (169 sin anuncios, 4 con n>=30), temporal diluido, manifests, docs de estado.
- Índice y validación JSON Schema añadidos; decisión justificada en la spec.

## Capabilities

### New Capabilities

- `mongo-safe-load`: carga no destructiva con staging, backup y aborto sin borrado.

### Modified Capabilities

- `mongodb-y-analisis`: PYMONGO-01 y LIMPIEZA-01 endurecidos (idempotencia sin ventana vacía, borrado seguro).

## Approach

Helper `_swap_collection` en `storage/mongo.py`: inserta en `<name>__staging`, clona la original a `<name>__backup` con $out, hace rename atómico. Los 2 loaders idempotentes (municipios, anuncios) no cambian. Tests destructivos con guarda explícita.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `storage/mongo.py` | Modified | zfill float, MONGO_TEST_DB, helper swap |
| `storage/load_mongo.py` | Modified | 11 loaders con staging, 2 loaders sin cambio |
| `tests/test_mongo.py` | Modified | Guarda destructiva, test zfill |
| `openspec/specs/mongodb-y-analisis/spec.md` | Modified | Delta de PYMONGO-01 y LIMPIEZA-01 |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Rename pierde índices | Med | ensure_indexes tras load_all; documentado |
| Backup duplica volumen | Low | Una colección de respaldo por colección |
| Guarda de tests oculta regresión | Low | Skipped explícito, no falso verde |

## Rollback Plan

Revertir el commit. La colección `__backup` conserva la última carga buena hasta la siguiente; recargar desde silver si hace falta.

## Dependencies

- MongoDB local en marcha para verify en vivo.

## Success Criteria

- [ ] zfill_ine(1001.0) y zfill_ine("1001.0") devuelven "01001".
- [ ] Carga con docs vacío no borra la colección original.
- [ ] Suite pytest sin mutar prod por defecto; 108 collected.
- [ ] Los 13 conteos de Mongo se mantienen tras una carga de prueba.
