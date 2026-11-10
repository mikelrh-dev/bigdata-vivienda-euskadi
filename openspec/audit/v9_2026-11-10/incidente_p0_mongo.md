# Incidente P0 — índices de `anuncios` ausentes tras la Ronda 4

**Fecha:** 2026-11-10
**Estado:** restaurado 2026-11-10 con `ensure_indexes()` (cambio `2026-11-10-defensa-v9-p0`); 4 índices de `anuncios` y 24 en 16 vivas.
**Severidad:** P0 para la evidencia de C13; la base productiva quedó degradada (sin pérdida de datos)

## Qué pasó

Durante la Ronda 4, el subagente W3.1 ejecutó la suite `pytest tests -q`. El test
`tests/test_mongo_geo.py:13` llamaba `load_anuncios()` real (sin mongomock ni `skipif`),
que ejecuta `replace_collection("anuncios", docs)`. Esa función deja la colección viva
sin índices (el staging se crea con solo `_id_`) y **no** llama a `ensure_indexes()`:
eso solo lo hace `load_all()`.

`tests/test_load_mongo.py` **no** es el mutador: usa `mongomock` vía el fixture
`mongo_tmp` (`tests/test_load_mongo.py:37-43`), que parchea `storage.mongo.get_db`;
`replace_collection` resuelve `get_db` en tiempo de llamada, así que nunca tocó prod.

Resultado: `anuncios` se quedó con solo `_id_`; los 4 índices documentados
(`idx_anuncios_ine_modalidad_precio`, `idx_anuncios_geo`, `idx_anuncios_portal_id`,
`idx_anuncios_equipamiento`) desaparecieron.

## Evidencia

- `mongod.log`: `renameCollectionForCommand` sobre `vivienda_euskadi.anuncios__staging`
  → `anuncios` a 08:58:45 y 08:59:48 (conn497 y conn521); 18 `CMD: drop` entre 08:58 y 09:02.
- No hay ningún `createIndexes` en el log después de 07:22:02 (cuando se crearon los
  índices originales).
- Sonda actual: `anuncios` 594 docs, `list_indexes()` → `['_id_']`.
- `anuncios__backup` 594 docs, también sin índices (el `$out` no copia índices).
- Corrección de la Ronda 4: el informe de W3.1 afirmó que `etxbide_promociones` y su
  backup desaparecieron. **Es incorrecto**: están presentes con 406 docs cada uno. El
  daño real es solo la pérdida de los 4 índices de `anuncios`.

## Estado actual (verificado)

- 30 colecciones, conteos íntegros: anuncios 594, municipios 252, vpo_municipal 252,
  etxbide_promociones 406, etx_solicitudes 5040, etc.
- Datos íntegros: 594 docs con `ubicacion.codigo_ine`, `portal`, `id_anuncio`;
  0 duplicados `(portal, id_anuncio)`.
- Índices totales: 34 (30 `_id_` + 4 de negocio: alquiler, certificados, etx, municipios).
  Faltan los 4 de `anuncios`.
- No hay pérdida de datos.
- **Resolución 2026-11-10:** `ensure_indexes()` restauró los 4 índices de `anuncios`
  (idempotente); verificado `list_indexes()` → 4 en `anuncios`, 24 en 16 vivas, 594 docs íntegros.

## Causa raíz

`replace_collection()` (`storage/mongo.py:152-164`) deja la colección viva sin índices.
`load_all()` los recrea con `ensure_indexes()`, pero `load_anuncios()` directo no.
Los tests llaman `load_anuncios()` directo.

## Impacto

- C13 (índices) ya no es reproducible: el `explain` da COLLSCAN 594.
- El baseline v9 (07:29) registraba los índices presentes; la evidencia de la Ronda 3
  (IXSCAN 8/8) ya no es reproducible.
- La defensa pierde la prueba de índices.

## Opciones

1. **Restaurar los índices** ejecutando `ensure_indexes()` (idempotente: `create_index`
   con el mismo nombre y spec no hace nada si ya existe). Requiere autorización
   (escritura en Mongo).
2. **Dejarlo así** y documentar; C13 queda sin evidencia reproducible.
3. **Restaurar desde `__backup`**: no sirve, el backup tampoco tiene los índices.

## Recomendación

Opción 1. Es segura (no toca datos), devuelve el estado al baseline y permite repetir
la evidencia de C13.

## Nota de proceso

El plan v9 permitía `pytest tests -q` como lectura, pero la suite no era hermética
(H-T1) y había tests que mutaban producción (`test_mongo_geo.py` y los tests de
`explain`). Con el cambio `2026-11-10-defensa-v9-p0` el explain es read-only y
`test_mongo_geo.py` se aísla con `get_test_db()`; la suite queda verde sin
deseleccionar y sin mutar prod (235 passed + 2 skipped).
