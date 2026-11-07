# Proposal: mongo-geojson-real

## Intent

El modelo anuncia GeoJSON Point con índice 2dsphere en `anuncios.ubicacion.coordenadas`, pero el estado previo medido era `None` en 759 de 759 anuncios. Sin coordenadas reales no hay consultas espaciales ni defensa de índices útil. El cambio usa latitud y longitud reales de `data/procesado/anuncios_fotocasa_enriquecido.csv` sin inventar valores.

Alineación: rúbrica v2 `brief/RETO 1Evaluacion SBD-BDAv2.pdf` RA1 46,7 % (integración de fuentes y construcción del conjunto) y RA3 13,3 % (modelado e índices con explain); Tema 8 tabla de pesos Modelado 15 % e Índices 15 % con respaldo en `openspec/specs/contrato-reto/spec.md` y `openspec/specs/mongodb-y-analisis/spec.md`.

## Scope

### In Scope
- `storage/load_mongo.py` en `load_anuncios`: construir `{"type":"Point","coordinates":[lon,lat]}` desde silver por `id_anuncio` solo para `portal == "fotocasa"`.
- `tests/test_mongo_geo.py` con `test_anuncios_geojson_real`: recargar anuncios y contar Point válidos mayor que 0, con 0 inválidos.
- `docs/modelo_mongodb.md:40`: actualizar solo si el test pasa, con conteo medido real (esperado 424 de 759).

### Out of Scope
- Tocar `tests/test_mongo.py`, `storage/clean_mongo.py` o `analysis/*`.
- Inventar coordenadas, centroides municipales o fallback geográfico.
- Cambiar colecciones, índices o pipelines.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `mongodb-y-analisis`: el documento `anuncios` pasa a almacenar GeoJSON Point real en `ubicacion.coordenadas` con validación y test dedicado.

## Approach

Leer silver `anuncios_fotocasa_enriquecido.csv`, mapear `id_anuncio -> Point` con orden GeoJSON `[lon, lat]`, validar finito y rango con `to_float` más chequeo `-90..90` y `-180..180`. En `load_anuncios`, usar el mapa por `id_anuncio` y dejar `None` al resto (sparse 2dsphere ya existente en `analysis/mongo_indexes.py`). El test recarga con `load_anuncios()` y verifica conteo en Mongo vivo.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `storage/load_mongo.py` | Modified | `_geo_point` y `_lookup_fotocasa_geo` alimentan `ubicacion.coordenadas` en `load_anuncios` |
| `tests/test_mongo_geo.py` | Create | `test_anuncios_geojson_real` con conteo de Point válidos |
| `docs/modelo_mongodb.md` | Modified | Línea 40 con conteo medido y fuente silver |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `latitud`/`longitud` vacías o inválidas | Low | `to_float` retorna `None`; `_geo_point` retorna `None` si falta o es inválida |
| `id_anuncio` sin coincidencia | Medium | 4 fotocasa de 428 sin silver quedan `None`; resto `pisos`/`realtyapi` también `None` por diseño |
| Desvío de conteo documental | Low | No tocar la línea 40 hasta que el test pasa con conteo vivo |

## Rollback Plan

Revertir los tres ficheros de alcance y recargar con `.venv/Scripts/python.exe storage/load_mongo.py`. Los artefactos SDD de este cambio quedan sin commitear hasta decisión del orquestador.

## Dependencies

- Silver `data/procesado/anuncios_fotocasa_enriquecido.csv` (471 filas, columnas `id_anuncio`, `latitud`, `longitud`).
- Silver `data/procesado/anuncios_unificados.csv` (759 filas, 428 `fotocasa`).
- Mongo vivo `localhost:27017`, base `vivienda_euskadi`, 13 colecciones principales.

## Success Criteria

- [ ] `.venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py -q` con exit 0 y Point válidos mayor que 0.
- [ ] `.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q` con exit 0.
- [ ] Mongo vivo: 13 colecciones principales, `anuncios` 759, Point 424, `None` 335, índice `idx_anuncios_geo` 2dsphere sparse.
- [ ] `docs/modelo_mongodb.md:40` coincide con el conteo vivo.
