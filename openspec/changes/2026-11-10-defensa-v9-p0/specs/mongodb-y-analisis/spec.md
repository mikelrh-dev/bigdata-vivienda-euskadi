# Delta for MongoDB y análisis

## MODIFIED Requirements

### Requirement: INDICES-01 — Índices y explain() read-only

El sistema SHALL demostrar con `explain("executionStats")`, para el filtro
canónico `ubicacion.codigo_ine=20069` + `modalidad=larga_estancia` +
`precio_eur $lte Decimal128(1000)` (1 documento; `48020` → 8; `48001` → 0),
la transición COLLSCAN → IXSCAN **en lectura**: el "antes" SHALL forzar
COLLSCAN con `hint: {"$natural": 1}` **sin dropear** el índice, y el
"después" SHALL usar el índice ESR presente
`{ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}` sin recrearlo. El
sistema SHALL NOT dropear ni crear índices en prod desde el demo ni desde
los tests. `analysis/run_analisis_mongo.py` SHALL ejecutar la versión
read-only del explain en `main()`. SHALL documentar en
`docs/modelo_mongodb.md` junto a geo 2dsphere sparse, multikey
(`equipamiento`) y parcial.
(Previously: demo que dropeaba/recreaba el índice ESR y escenario «GIVEN el
índice ESR eliminado» con filtro `48001` y `totalDocsExamined=1`.)

#### Scenario: Before/after read-only con hint $natural

- GIVEN `anuncios` con el índice ESR presente y filtro canónico `20069`
- WHEN se ejecutan `explain_before_after()` y `_explain()`
- THEN `before` usa `hint:{"$natural":1}` y `before.stage` es `COLLSCAN`
- AND `after.stage` es `IXSCAN` con `nReturned` y `totalDocsExamined` documentados
- AND `after.totalDocsExamined` es 1 para `20069`
- AND `list_indexes()` de `anuncios` es idéntico antes y después (sin drop/create)

#### Scenario: Filtros documentados

- GIVEN los filtros `20069`, `48020` y `48001`
- WHEN se ejecuta el explain read-only
- THEN `20069` devuelve 1 documento, `48020` 8 y `48001` 0
- AND el demo usa un filtro con ≥1 documento para que IXSCAN sea demostrable

#### Scenario: Geo, multikey y parcial documentados

- GIVEN `docs/modelo_mongodb.md`
- WHEN se revisan los índices
- THEN constan geo 2dsphere sparse, multikey `equipamiento` y parcial
- AND cada uno cita su consulta real justificativa
