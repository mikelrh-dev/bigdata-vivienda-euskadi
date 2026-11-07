# mongodb-y-analisis — Delta

## Purpose

Derivar el Tier A/B/C/D solo de `n_anuncios` real vía pipeline `$group` por `codigo_ine`, sin mutar raw ni imputar.

## MODIFIED Requirements

### Requirement 1: AGREGACION-01 — Pipeline tier_por_municipio

El sistema SHALL emitir CSV canónicos en `data/resultados/` desde `pipeline_indicadores_municipio` (252 filas), `pipeline_alquiler_por_municipio` (252), `pipeline_modalidades` (2), `pipeline_accesibilidad_extendida`, `pipeline_vpo_por_municipio` y `pipeline_tier_por_municipio` (252) con `$group` por `codigo_ine` que calcule `n_anuncios`, `n_precio`, `min_precio`, `max_precio`, `n_precio_temporal` y `n_precio_larga`; el tier deriva de `n_anuncios` (A ≥30, B 10-29, C 1-9, D 0). El `n` es propio de Mongo, nunca de HDFS.
(Previously: 5 CSV canónicos sin tier.)

#### Scenario: tier_por_municipio completo

- GIVEN los anuncios cargados en `vivienda_euskadi`
- WHEN corre `python analysis/run_analisis_mongo.py`
- THEN `data/resultados/mongo_tier_confianza.csv` tiene 252 filas
- AND salida: 4 Tier A / 3 B / 57 C / 188 D, doble ejecución con SHA idéntico

#### Scenario: Edge n_precio=0 en Tier C/D

- GIVEN municipio con `n_anuncios` 1-9 o 0
- WHEN corre la pipeline
- THEN `n_precio`=0, min/max nulos, tier C/D, sin imputación comarcal/IDW
- AND `pytest tests -q` sigue verde

## ADDED Requirements

### Requirement 2: TIER-01 — Raw inmutable, HDFS solo raw, Kafka→HDFS

El sistema SHALL tratar `data/raw` y HDFS raw (352 ficheros) como inmutables, SHALL NOT usar Docker, SHALL mantener Kafka → HDFS (nunca Kafka → Mongo), y SHALL re-cargar vía staging + `<name>__backup` + rename atómico con `ensure_indexes`.

#### Scenario: Re-carga reversible sin drop

- GIVEN `indicadores` cargada
- WHEN se regenera el Tier desde Mongo con `python -m storage.load_mongo`
- THEN existe `indicadores__backup` y la colección activa conserva 252 filas
- AND salida: 0 documentos perdidos
