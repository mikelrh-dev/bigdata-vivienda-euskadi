# mongodb-y-analisis — Delta

## Purpose

Asegurar que `pipeline_tier_por_municipio` expone el contrato completo que consumen los 3 gráficos, sin recomputar en el exportador.

## MODIFIED Requirements

### Requirement 1: AGREGACION-01 — pipeline_tier_por_municipio expone min/max/mediana/esfuerzo

El sistema MUST extender `pipeline_tier_por_municipio` (`analysis/mongo_aggregations.py`) para exponer por municipio: `n_anuncios`, `n_precio`, `min_precio`, `max_precio`, `min_precio_temporal`, `max_precio_temporal`, `mediana_precio_temporal`, `min_precio_larga`, `max_precio_larga`, `mediana_precio_larga`, `n_precio_temporal`, `n_precio_larga` y `esfuerzo_joven_pct_18_34`. `analysis/run_analisis_mongo.py` MUST escribirlos en `mongo_tier_confianza.csv` (252 filas) y `mongo_esfuerzo_por_municipio.csv` sin recomputar ni teclear valores. El ranking de esfuerzo MUST limitarse a `n_anuncios >= 30` (4 Tier A); `n < 30` MUST etiquetarse `n_insuficiente` sin ordenación. El sistema MUST NOT tocar Docker, HDFS (salvo raw inmutable) ni Kafka→Mongo; `data/raw` y raw HDFS quedan inmutables.

| Campo | Fuente |
|---|---|
| `n_anuncios`, `n_precio` | `$group` por `codigo_ine` |
| min/max/mediana temporal/larga | misma pipeline, por modalidad, nunca promediadas |
| `esfuerzo_joven_pct_18_34` | pipeline de esfuerzo, solo Tier A rankea |

#### Scenario: Tier B expone rango y medianas por modalidad

- GIVEN `vivienda_euskadi` cargada
- WHEN corre `python analysis/run_analisis_mongo.py`
- THEN `mongo_tier_confianza.csv` tiene 252 filas con min/max/mediana temporal y larga para Sopela, Zarautz y Santurtzi
- AND doble ejecución da SHA idéntico

#### Scenario: Tier A expone esfuerzo rankeable

- GIVEN los 4 Tier A (`n >= 30`: Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39)
- WHEN se exporta `mongo_esfuerzo_por_municipio.csv`
- THEN cada Tier A lleva `esfuerzo_joven_pct_18_34` junto a `n_anuncios` y `n_precio`

#### Scenario: Edge n<30 sin ranking

- GIVEN un municipio con `n_anuncios < 30`
- WHEN corre la pipeline
- THEN figura `n_insuficiente`, sin posición de ranking y sin imputación
- AND `pytest tests -q` sigue verde
