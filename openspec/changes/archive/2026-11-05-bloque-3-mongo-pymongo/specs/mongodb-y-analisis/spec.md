# Delta for mongodb-y-analisis

## ADDED Requirements

### Requirement: RESPALDO-01 — Backups y geo en lectura pura

El sistema SHALL garantizar backups de `municipios` e `indicadores` vía
`replace_collection` (staging + `<name>__backup` + rename), SHALL documentar
los 424 Point GeoJSON de 759 anuncios desde silver, y SHALL verificarlo con
el listing de 15 colecciones, sin escrituras en prod.

#### Scenario: Backups, geo y listing

- GIVEN `vivienda_euskadi` con 759 anuncios y 252 municipios
- WHEN se listan las colecciones y se cuentan los Point
- THEN hay 15 colecciones, incluidos `municipios__backup` (252 previos) e `indicadores__backup`
- AND hay 424 Point reales, el resto `None` por falta de silver

### Requirement: RENTA-01 — `validar_renta` o justificación firmada

El sistema SHALL incluir `validar_renta.py` como paso de
`transform/run_all.py` o SHALL firmar su exclusión, y `pytest tests` SHALL
pasar con 130 tests.

#### Scenario: Integración o justificación

- GIVEN `validar_renta.py` en `EXCLUIDOS` de `run_all.py`
- WHEN se revisa el orquestador
- THEN es paso del pipeline o existe justificación firmada
- AND `pytest tests -q` reporta 130 passed

## MODIFIED Requirements

### Requirement: INDICES-01 — Índices y explain()

El sistema SHALL demostrar con `explain("executionStats")`, para
`ubicacion.codigo_ine=48001` + `modalidad=larga_estancia` + `precio_eur $lte
Decimal128(1000)`, la transición COLLSCAN → IXSCAN con `nReturned` y
`totalDocsExamined=1` tras el índice ESR
`{ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}`, y SHALL documentarlo en
`docs/modelo_mongodb.md` junto a geo 2dsphere sparse, multikey
(`equipamiento`) y parcial.
(Previously: ESR/geo/multikey/parcial en SHOULD sin evidencia.)

#### Scenario: Before/after con totalDocsExamined=1

- GIVEN el índice ESR eliminado
- WHEN se ejecutan `explain_before_after()` y `_explain()`
- THEN `before.stage` es `COLLSCAN` y `after.stage` es `IXSCAN`
- AND `after.totalDocsExamined` es 1 con `nReturned` documentado

#### Scenario: Geo, multikey y parcial documentados

- GIVEN `docs/modelo_mongodb.md`
- WHEN se revisan los índices
- THEN constan geo 2dsphere sparse, multikey `equipamiento` y parcial
- AND cada uno cita su consulta real justificativa

### Requirement: MODELO-01 — Modelo justificado y relaciones

El sistema SHALL responder en `docs/modelo_mongodb.md`, literalmente, las 7
preguntas docx §5: ¿qué información se consulta normalmente junta?; ¿qué
información cambia con frecuencia?; ¿qué arrays podrían crecer sin límite?;
¿hay información que se repite pero interesa conservar como fotografía
histórica?; ¿qué relaciones son 1:1, 1:N o N:M?; ¿qué campos se usarán para
relacionar información procedente de fuentes distintas?; ¿qué tipos BSON son
adecuados para fechas, importes, identificadores, booleanos o arrays?
(Previously: las 7 preguntas en SHOULD.)

#### Scenario: Preguntas literales en el doc

- GIVEN `docs/modelo_mongodb.md`
- WHEN se revisa el modelado
- THEN las 7 preguntas aparecen literales con su respuesta
- AND ≥1 decisión embedding/referencing queda justificada

### Requirement: LIMPIEZA-01 — Incompletos, duplicados, incorrectos

El sistema SHALL limpiar con `$unset` explícito y SHALL retornar
`deleted_count`, SHALL exponer una única función canónica
anuncio-por-municipio y SHALL mantener los 759 anuncios tras limpio.
(Previously: `$unset`/`deleted_count` sin función canónica única.)

#### Scenario: Limpieza con contadores

- GIVEN anuncios con campos obsoletos
- WHEN se ejecuta `clean_mongo`
- THEN aplica `$unset` y el resultado incluye `deleted_count`
- AND el recuento sigue en 759

### Requirement: TRANSACCIONES-01 — Atomicidad multidocumento

El sistema SHALL demostrar commit/abort multidocumento en
`vivienda_euskadi_test` o SHALL justificar por READ (docx §11), y MUST NOT
tocar prod por defecto (solo `MONGO_ALLOW_DESTRUCTIVE=1`).
(Previously: solo atomicidad de un documento.)

#### Scenario: Commit/abort en test o READ

- GIVEN `vivienda_euskadi_test` o la decisión documentada
- WHEN se ejecuta la transacción o se revisa la justificación
- THEN el commit persiste, el abort revierte y prod conserva su recuento
- AND si no aplica, la justificación cita docx §11 y el ejemplo plausible

### Requirement: PYMONGO-01 — CRUD con excepciones tipadas

El sistema SHALL sustituir `except Exception` por `except (TypeError,
ValueError)` con log en `_money` (`storage/load_mongo.py`) y en los
`except Exception: pass` de `ensure_indexes`/`explain_*`
(`analysis/mongo_indexes.py`), y SHALL comprobar `matched_count`,
`modified_count` y `deleted_count` en test.
(Previously: excepciones genéricas con `pass` silencioso.)

#### Scenario: Errores no silenciados y CRUD con contadores

- GIVEN un precio no numérico o un CRUD en `vivienda_euskadi_test`
- WHEN se procesa `_money` o se insertan/actualizan/borran documentos
- THEN `_money` devuelve `None` con log y el test comprueba los 3 contadores
- AND `pytest tests` sigue en 130 passed

### Requirement: AGREGACION-01 — Pipelines a CSV canónico

El sistema SHALL emitir CSV canónicos en `data/resultados/` desde
`pipeline_indicadores_municipio` (252 filas),
`pipeline_alquiler_por_municipio` (252), `pipeline_modalidades` (2),
`pipeline_accesibilidad_extendida` y `pipeline_vpo_por_municipio`, con
`$group`/`$lookup`/`$unwind` donde los datos lo permitan.
(Previously: solo 3 CSV canónicos medidos.)

#### Scenario: Cinco CSV canónicos

- GIVEN las 8 pipelines de `analysis/mongo_aggregations.py`
- WHEN se ejecutan las 5 citadas
- THEN cada una escribe su CSV canónico en `data/resultados/`
- AND los recuentos medidos son 252, 252 y 2
