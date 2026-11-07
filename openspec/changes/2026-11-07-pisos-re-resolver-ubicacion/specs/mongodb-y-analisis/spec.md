# mongodb-y-analisis — Delta

## Purpose

Re-cargar Mongo tras la re-resolución de pisos sin perder ni maquillar datos: staging+backup+rename, conteos honestos y precio/superficie solo donde hay anuncio real.

## MODIFIED Requirements

### Requirement: CARGA-SEGURA-01 — Re-carga sin drop

El sistema SHALL re-cargar vía `storage/load_mongo.py` con staging + `<name>__backup` + rename atómico, recreando índices con `ensure_indexes`. SHALL NOT hacer `drop()` directo: si staging está vacío, aborta y la colección original conserva sus documentos (base CARGA-SEGURA-01 vigente).

#### Scenario: Recarga reversible

- GIVEN `anuncios` con 759 documentos
- WHEN se carga silver re-resuelto
- THEN existe `anuncios__backup` con 759 previos
- AND `pytest tests/test_pisos_ubicacion_real.py -q` → backup presente, 0 pérdidos

### Requirement: LIMPIEZA-01 / TRANSFORM-01 — Re-ejecución en orden

El sistema SHALL re-ejecutar `transform/unificar_anuncios.py` → `transform/aplicar_cobertura_mercado.py` (base `dim_municipios` primero, enricher después), con cuarentena fuera-Euskadi en `aplicar_cobertura_mercado`.

#### Scenario: Orden base→enricher

- GIVEN silver con pisos re-resueltos
- WHEN corre `python transform/unificar_anuncios.py && python transform/aplicar_cobertura_mercado.py`
- THEN enricher usa solo municipios de `dim_municipios` y cuarentena queda fuera
- AND `n_anuncios` por municipio = anuncios reales post re-resolución

## ADDED Requirements

### Requirement: PISOS-03 — Conteos honestos, sin imputación

`n_anuncios` y `n_anuncios_raw` SHALL ser conteos reales de anuncios tras re-resolución (excluidos cuarentena). Precio/superficie SHALL calcularse solo donde hay anuncio; SHALL NOT imputar por IDW ni comarcal.

| Regla | Conducta |
|---|---|
| `n_anuncios` | count real por `codigo_ine` en `dim_municipios` |
| `n_anuncios_raw` | count pre-limpieza, sin filtrar cuarentena |
| Sin anuncio | precio/superficie `None`, sin IDW/comarcal |

#### Scenario: Municipio sin anuncios no inventa precio

- GIVEN municipio con `n_anuncios=0`
- WHEN se agregan indicadores
- THEN precio/superficie = `None` y `metodo_imputacion=ninguno`
- AND `python analysis/run_analisis_mongo.py` regenera 13 PNG + 6 CSV sin valores imputados

### Requirement: PISOS-04 — Regresión 252/252 y 249/252

Tras la recarga, Eustat SHALL seguir 252/252 y Lanbide 249/252. Doble ejecución de `run_analisis_mongo.py` SHALL dar SHA idéntico.

#### Scenario: Doble ejecución idéntica

- GIVEN Mongo recargado
- WHEN corre `run_analisis_mongo.py` dos veces
- THEN SHA256 de los 6 `mongo_*.csv` coincide entre ejecuciones
