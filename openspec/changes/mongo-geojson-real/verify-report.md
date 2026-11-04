# Verification Report: mongo-geojson-real

**Change**: mongo-geojson-real
**Mode**: Standard (strict_tdd: false en openspec/config.yaml)
**Verdict**: PASS

## Completeness

| Task | Status |
|------|--------|
| 1.1 `_geo_point` con validación y orden [lon,lat] | [x] |
| 1.2 `_lookup_fotocasa_geo` por id_anuncio | [x] |
| 1.3 `load_anuncios` cableado solo fotocasa, resto None | [x] |
| 2.1 `test_anuncios_geojson_real` con puntos > 0 e invalid == 0 | [x] |
| 3.1 `docs/modelo_mongodb.md:40` solo si pasa el test | [x] |
| 3.2 Sin regresión en test_mongo y Mongo vivo 13 colecciones | [x] |

## Evidence

- `.venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py -q`: 1 passed in 1.20s, EXIT_GEO:0.
- `.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q`: 25 passed in 0.64s, EXIT_MONGO:0.
- Mongo vivo `localhost:27017`, base `vivienda_euskadi`: ping True, 15 colecciones con backups, 13 principales (`alquiler_municipal`, `anuncios`, `certificados_energeticos`, `ecvi_compraventa`, `emancipacion_juventud`, `etxebide_promociones`, `etxebide_solicitudes`, `indicadores`, `municipios`, `osrm_tiempos`, `udalmap_empleo`, `udalmap_extendido`, `udalmap_indicadores`).
- Conteo vivo `anuncios`: 759 total, 424 con `ubicacion.coordenadas.type = Point`, 335 con `ubicacion.coordenadas = None`. El test recarga con `load_anuncios()` antes de contar, por lo que el conteo es post-recarga y no un estado heredado.
- Índice vivo: `idx_anuncios_geo` sobre `ubicacion.coordenadas: 2dsphere` sparse, más `idx_anuncios_portal_id`, `idx_anuncios_equipamiento` e `idx_anuncios_ine_modalidad_precio`.
- Cruce silver verificado: `anuncios_unificados.csv` 759 filas con 428 `fotocasa`; `anuncios_fotocasa_enriquecido.csv` 471 filas con 471 `id_anuncio` únicos; intersección 424. Los 4 fotocasa sin silver son 182812522, 191125846, 191234371 y 191247657, más 247 `pisos` y 84 `realtyapi` sustentan los 335 `None`.

## Spec Compliance

| Requirement | Evidence | Status |
|-------------|----------|--------|
| GEOJSON-01 Point real [lon,lat] desde silver por id_anuncio | `storage/load_mongo.py` `_geo_point` y `_lookup_fotocasa_geo`, vivo 424 Point | PASS |
| Solo fotocasa, resto None sin inventar | `load_anuncios` condiciona por `portal == "fotocasa"`, 335 None documentados | PASS |
| Inválidos a None, cero inválidos en base | Test exige `invalid == 0` y pasa; validación finito + rango | PASS |
| Test dedicado con conteo > 0 | `tests/test_mongo_geo.py` `test_anuncios_geojson_real`, 1 passed exit 0 | PASS |
| Indice 2dsphere sparse sin error | `idx_anuncios_geo` vivo, carga sin error | PASS |

## Correctness / Design Coherence

La implementación coincide con `design.md`: orden GeoJSON lon primero, solo `fotocasa`, sin fallback de centroide, índice sparse existente sin cambios en `analysis/mongo_indexes.py`. Alcance respetado: no se tocaron `tests/test_mongo.py`, `storage/clean_mongo.py` ni `analysis/*`. `docs/modelo_mongodb.md:40` ya decía 424 de 759 con fuente silver por `id_anuncio`, que coincide con el conteo vivo; no requirió reescritura en esta pasada porque el test pasa.

Nota de estado: la implementación de los tres ficheros ya estaba en HEAD (commit 6b3b109); `git diff` de esos tres ficheros está vacío en esta sesión y los artefactos SDD de `openspec/changes/mongo-geojson-real/` quedan sin commitear como entrega del loop. Cambios sin commitear por instrucción.

## Issues

CRITICAL: none
WARNING: none
SUGGESTION: none
