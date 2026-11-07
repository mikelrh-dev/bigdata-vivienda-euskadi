# mongodb-y-analisis — Delta

## Purpose

Vista separada de habitaciones por municipio (201 anuncios, 9 municipios), sin alterar precio municipal 62/252 ni Tier A/B/C/D.

## ADDED Requirements

### Requirement HAB-01 — `pipeline_habitaciones_por_municipio`

El sistema SHALL añadir `pipeline_habitaciones_por_municipio` en `analysis/mongo_aggregations.py`: `$group` por `codigo_ine` normalizado sobre `anuncios_habitaciones_unificados` (201 anuncios; Bilbao 96, Donostia 66, Vitoria 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 2, Eibar 1). Cada fila SHALL exponer `codigo_ine`, `municipio`, `n`, `n_precio`, `min_precio_eur`, `max_precio_eur`, `mediana_precio_eur` (mediana cruda, sin winsorizar ni imputar). `analysis/run_analisis_mongo.py` SHALL registrarlo como pipeline nº 11 y exportar `data/resultados/mongo_habitaciones_por_municipio.csv` (9 filas) sin recomputar ni teclear valores. SHALL NOT tocar `pipeline_tier_por_municipio`, Tier A/B/C/D ni precio 62/252. Guardarraíles: sin Docker; HDFS solo raw (352 ficheros); Kafka → HDFS, nunca Kafka → Mongo.

#### Scenario: Nueve filas con suma 201

- GIVEN `anuncios_habitaciones_unificados` cargados en `vivienda_euskadi`
- WHEN corre `python analysis/run_analisis_mongo.py`
- THEN `mongo_habitaciones_por_municipio.csv` tiene 9 filas y suma `n_precio` = 201 (Bilbao 96, Donostia 66, Vitoria 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 2, Eibar 1)
- AND cada fila expone `n`, `n_precio`, min, max y mediana

#### Scenario: Doble ejecución idéntica

- GIVEN Mongo recargado
- WHEN corre `run_analisis_mongo.py` dos veces
- THEN SHA256 de `mongo_habitaciones_por_municipio.csv` coincide entre ejecuciones

#### Scenario: n<30 sin ranking ni imputación

- GIVEN municipio con `n_precio < 30` (p. ej. Eibar 1)
- WHEN corre la pipeline
- THEN figura `n_insuficiente`, sin posición de ranking y sin imputación comarcal/IDW
- AND `pytest tests -q` sigue verde

#### Scenario: Tier y precio intactos

- GIVEN el orquestador con 11 pipelines
- WHEN se regeneran los resultados
- THEN `mongo_tier_confianza.csv` mantiene 252 filas y precio observable 62/252, sin cambios
