# Aislamiento de tests — Especificación

## Purpose

Garantizar que la suite de tests y las demos de análisis no muten la base
productiva `vivienda_euskadi`: los tests que cargan o consultan Mongo SHALL
ejecutarse contra `mongomock`/`mongo_tmp`, `get_test_db()` o
`skipif(not ping())`, y ningún test ni demo SHALL dropear o crear índices en
prod. La evidencia de C13/T4 SHALL ser reproducible en lectura pura.

## Requirements

### Requirement: AISLAMIENTO-01 — Tests de carga y consulta aislados

Los tests que cargan o consultan `vivienda_euskadi` SHALL usar `mongomock`
(fixture `mongo_tmp`), `get_test_db()` o `skipif(not ping())`; SHALL NOT
llamar `load_anuncios()` ni `replace_collection()` sobre prod. Los tests que
necesiten Mongo real y no puedan aislarse SHALL declararse con `skipif` y
NO ejecutarse por defecto en CI.

#### Scenario: Test de carga con mongomock

- GIVEN un test que carga anuncios
- WHEN se ejecuta con `mongo_tmp` o `get_test_db()`
- THEN el test no toca prod
- AND `list_indexes()` de prod es idéntico antes y después

#### Scenario: Mongo no disponible

- GIVEN `ping()` es `False`
- WHEN se ejecuta la suite
- THEN los tests que necesitan Mongo se saltan (`skipif`)
- AND ningún test escribe en prod

#### Scenario: Prohibido load_anuncios en prod

- GIVEN un test que invoca `load_anuncios()` sin aislar
- WHEN se ejecuta la suite
- THEN el test NO está permitido (SHALL fallar o estar aislado con `mongo_tmp`)
- AND prod conserva sus 4 índices de `anuncios`

### Requirement: AISLAMIENTO-02 — Demo explain read-only

El demo de `explain` (`explain_before_after`, `explain_promo_before_after`,
`index_report`) SHALL ser read-only: el "antes" SHALL forzar COLLSCAN con
`hint: {"$natural": 1}` y el "después" SHALL usar el índice presente, sin
`drop_index` ni `create_index` en prod. Los tests de explain SHALL llamar a
la versión read-only y SHALL NOT crear índices en su cuerpo.

#### Scenario: Explain sin mutar prod

- GIVEN `anuncios` con el índice ESR presente
- WHEN se ejecuta `explain_before_after()`
- THEN el "antes" usa `hint:{"$natural":1}` y reporta `COLLSCAN`
- AND el "después" reporta `IXSCAN`
- AND `list_indexes()` de `anuncios` no cambia

#### Scenario: Filtro sin resultados

- GIVEN el filtro `48001` que devuelve 0 documentos
- WHEN se ejecuta el explain read-only
- THEN el test aserta los stages, no un `totalDocsExamined` concreto
- AND no dropea ni crea índices

### Requirement: AISLAMIENTO-03 — Suite verde sin deseleccionar y sin mutación

`pytest tests -q` SHALL pasar verde sin deseleccionar tests de Mongo y SHALL
dejar prod intacta: `list_indexes()` de `anuncios` y los recuentos de
colecciones SHALL ser idénticos antes y después de la suite. La evidencia de
C13/T4 (COLLSCAN/IXSCAN con `totalDocsExamined`) SHALL ser reproducible en
lectura pura.

#### Scenario: Suite hermética

- GIVEN prod con 4 índices en `anuncios`
- WHEN se ejecuta `pytest tests -q`
- THEN la suite es verde sin `-k`/`--deselect`
- AND `list_indexes()` y los recuentos son idénticos antes y después
