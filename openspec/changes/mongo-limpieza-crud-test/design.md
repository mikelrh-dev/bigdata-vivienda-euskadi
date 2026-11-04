# Design: mongo-limpieza-crud-test

## Technical Approach

Las funciones de storage/clean_mongo.py resuelven colecciones con get_collection importado en su módulo. El test usa patch.object sobre clean_mongo.get_collection para redirigir cualquier nombre hacia get_test_db, sin modificar producción ni el módulo. Dos tests comparten un contexto que vacía las colecciones temporales antes y en finally.

## Architecture Decisions

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| Patch de clean_mongo.get_collection | Las funciones no aceptan base ni colección; el patch es la única vía sin tocar producción | Elegida: patch limitado al bloque with, verificado con conteo productivo antes y después |
| Ejecutar clean_all con MONGO_ALLOW_DESTRUCTIVE=1 | Mutaría producción y seguiría gated | Descartada: limpia solo anuncios sobre temporal con las 4 funciones sueltas |
| Duplicar la lógica de limpieza en el test | No probaría código real | Descartada: se llama a las funciones reales y se asertan sus contadores |
| Fingerprints distintos en los 3 documentos | Evita que resolve_duplicates agrupe nulos de property_fingerprint | Elegida: cada documento lleva property_fingerprint propio |

## Data Flow

    test_clean_mongo -> insert_many (3 docs) -> canonicalize -> mark_nulls -> resolve_duplicates -> convert_types -> drop temporal
    test_crud_demo -> demo_crud_operations (sobre _demo_crud de test) -> asserts de contadores -> drop

## File Changes

| File | Action | Description |
|------|--------|-------------|
| tests/test_mongo.py | Modify | Helper de contexto temporal, test_clean_mongo y test_crud_demo reescritos, sin skip |
| openspec/changes/mongo-limpieza-crud-test/ | Create | proposal, specs, design, tasks, verify-report |

## Interfaces / Contracts

Helper _clean_mongo_on_test_db: contexto que deja get_test_db() en clean_mongo.get_collection, con drop previo y en finally de las colecciones que toca clean_mongo más _demo_crud. Datos: 2 duplicados portal Idealista id_anuncio A1 con precio string y códigos 1001 y 01001; 1 documento Fotocasa con código entero 20069, superficie 65, precio None y habitaciones None.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Integration | canonicalize, mark_nulls, resolve_duplicates, convert_types | Contadores exactos matched/modified/deleted y códigos finales |
| Integration | demo_crud_operations | inserted_id, update_one, upsert, bulk_write, delete_one, delete_many, remaining |
| Safety | Producción intacta | Conteo de anuncios productivo antes y después, igualdad exacta |

## Threat Matrix

N/A — no hay routing, shell, subprocess, VCS/PR automation, clasificación de ejecutables ni process integration.

## Migration / Rollout

No migration required.

## Open Questions

- Ninguna.
