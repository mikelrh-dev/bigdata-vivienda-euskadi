# Tasks: mongo-geojson-real

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 70-90 (load_mongo 26, test nuevo 45, docs 1, artefactos SDD fuera del presupuesto de revisión) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR (sin commit en esta sesión por instrucción) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | GeoJSON Point real en `load_anuncios` + test dedicado | PR único | `.venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py -q` | Mongo vivo `localhost:27017`, `anuncios` 759 con 424 Point | Revertir `storage/load_mongo.py` y `tests/test_mongo_geo.py`, recargar |

## Phase 1: Implementación del loader

- [x] 1.1 Implementar `_geo_point(lat_raw, lon_raw)` en `storage/load_mongo.py` con validación `to_float`, finito y rango `[-90,90]`/`[-180,180]`, retorno `{"type":"Point","coordinates":[lon,lat]}`. Aceptación: Point válidos tienen lon/lat finitos en rango, inválidos retornan `None`.
- [x] 1.2 Implementar `_lookup_fotocasa_geo()` en `storage/load_mongo.py` leyendo `data/procesado/anuncios_fotocasa_enriquecido.csv` por `id_anuncio`. Aceptación: mapa con 471 claves, 424 con Point válido tras cruce con unificados.
- [x] 1.3 Cablear `load_anuncios()` en `storage/load_mongo.py` para usar el mapa solo si `portal == "fotocasa"` y guardar `None` en el resto. Aceptación: `anuncios.ubicacion.coordenadas` es Point o `None`, sin valores inventados.

## Phase 2: Test dedicado

- [x] 2.1 Crear `tests/test_mongo_geo.py` con `test_anuncios_geojson_real` que ejecuta `load_anuncios()`, cuenta Point válidos y exige `puntos > 0` e `invalid == 0`. Aceptación: `.venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py -q` exit 0.

## Phase 3: Documentación y verificación

- [x] 3.1 Actualizar `docs/modelo_mongodb.md:40` solo si el test de la fase 2 pasa, con conteo vivo 424 de 759, fuente silver y `None` por falta de silver. Aceptación: línea 40 coincide con `count_documents({"ubicacion.coordenadas.type":"Point"})`.
- [x] 3.2 Verificar sin regresión con `.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q` y Mongo vivo (13 colecciones principales, `anuncios` 759). Aceptación: exit 0, 25 passed, `idx_anuncios_geo` 2dsphere sparse presente. Cambios sin commitear.
