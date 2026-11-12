# mongodb-y-analisis — Delta

## MODIFIED Requirements

### Requirement: AGREGACION-01 — Pipeline con mediana winsorizada y exclusión IQR (M1)

La pipeline `pipeline_indicadores_municipio` SHALL calcular la mediana de `precio_m2` con winsorización al percentil 1–99 (los valores extremos se recortan antes de la mediana, no se imputan) y SHALL excluir de la media/preciomedio los valores fuera del rango intercuartílico. Solo entran anuncios con `precio_m2` en [3, 50] y `superficie_m2` en [10, 500] y `habitaciones` entero (ya garantizado por OUTLIER-01 en extracción). `pipeline_tier_por_municipio` SHALL mantener 252 filas con `n_anuncios`, `n_precio`, `min_precio`, `max_precio`, `min_precio_temporal`, `max_precio_temporal`, `mediana_precio_temporal`, `min_precio_larga`, `max_precio_larga`, `mediana_precio_larga`, `n_precio_temporal`, `n_precio_larga` y `esfuerzo_joven_pct_18_34` (nombres canónicos `mediana_precio_temporal` / `mediana_precio_larga`); `analysis/run_analisis_mongo.py` SHALL volcarlos en `mongo_tier_confianza.csv` (252 filas) y `mongo_esfuerzo_por_municipio.csv` sin recomputar ni teclear valores. El ranking de esfuerzo SHALL limitarse a `n_anuncios >= 30` (4 Tier A); `n < 30` SHALL etiquetarse `n_insuficiente` sin ordenación. Temporal y larga SHALL NOT promediarse. El `n` sigue siendo propio de Mongo, nunca de HDFS. La mediana winsorizada se SHALL publicar como `mediana_precio_m2_winsorizada` y la mediana cruda no se SHALL usar para conclusiones. Las figuras A1/A2 y F SHALL usar solo la capa oficial (`metodo_imputacion=oficial`) o etiquetar la IDW; la figura P SHALL declarar que la cuantía oficial 2024 y el precio de anuncio 2026 no son comparables (ratio 1,96; Spearman 0,18).
(Previously: sin requisito de capas en las figuras.)

#### Scenario: Capas no mezcladas en A1/A2 y F

- GIVEN `mongo_esfuerzo_por_municipio.csv` (252 filas: 159 oficial + 93 idw)
- WHEN se generan A1/A2 y F
- THEN el denominador es 159 oficiales o la IDW va etiquetada
- AND la mediana oficial no se mezcla con la IDW en la misma barra

#### Scenario: P declara la no comparabilidad

- GIVEN la cuantía oficial 2024 y el precio de anuncio 2026
- WHEN se dibuja P
- THEN cada serie declara fuente y vintage
- AND la nota «no comparable» está presente con ratio 1,96 y Spearman 0,18

#### Scenario: Mediana winsorizada con exclusión IQR

- GIVEN anuncios con `precio_m2` extremos dentro de [3, 50] pero fuera de IQR
- WHEN corre `python analysis/run_analisis_mongo.py`
- THEN `mongo_indicadores_municipio.csv` tiene 252 filas y `mediana_precio_m2_winsorizada` no nula donde `n_precio≥1`
- AND la salida del análisis: `28+8 PNG + 8 CSV`, doble ejecución con SHA idéntico en los 8 `mongo_*.csv`

#### Scenario: Ningún outlier contamina la agregación

- GIVEN la colección `anuncios` cargada tras OUTLIER-01 y DEDUP-01
- WHEN se ejecuta la pipeline
- THEN 0 documentos con `precio_m2` fuera de [3, 50] o `superficie_m2` fuera de [10, 500] participan en la agregación
- AND `python -c "import pymongo; c=pymongo.MongoClient().vivienda_euskadi.anuncios; print(c.count_documents({'precio_m2':{'$gt':50}}))"` → salida: `0`

#### Scenario: Cinco CSV canónicos

- GIVEN las pipelines de `analysis/mongo_aggregations.py`
- WHEN se ejecutan las citadas
- THEN cada una escribe su CSV canónico en `data/resultados/`
- AND los recuentos medidos son 252, 252 y 2

#### Scenario: tier_por_municipio completo

- GIVEN los anuncios cargados en `vivienda_euskadi`
- WHEN corre `python analysis/run_analisis_mongo.py`
- THEN `data/resultados/mongo_tier_confianza.csv` tiene 252 filas
- AND salida: 4 Tier A / 3 B / 57 C / 188 D, doble ejecución con SHA idéntico

#### Scenario: Tier B expone rango y medianas por modalidad (2026-11-07)

- GIVEN `vivienda_euskadi` cargada
- WHEN corre `python analysis/run_analisis_mongo.py`
- THEN `mongo_tier_confianza.csv` tiene 252 filas con min/max/mediana temporal y larga para Sopela, Zarautz y Santurtzi
- AND doble ejecución da SHA idéntico

#### Scenario: Tier A expone esfuerzo rankeable (2026-11-07)

- GIVEN los 4 Tier A (`n >= 30`: Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39)
- WHEN se exporta `mongo_esfuerzo_por_municipio.csv`
- THEN cada Tier A lleva `esfuerzo_joven_pct_18_34` junto a `n_anuncios` y `n_precio`

#### Scenario: Edge n<30 sin ranking (2026-11-07)

- GIVEN un municipio con `n_anuncios < 30`
- WHEN corre la pipeline
- THEN figura `n_insuficiente`, sin posición de ranking y sin imputación
- AND `pytest tests -q` sigue verde

#### Scenario: Edge n_precio=0 en Tier C/D

- GIVEN municipio con `n_anuncios` 1-9 o 0
- WHEN corre la pipeline
- THEN `n_precio`=0, min/max nulos, tier C/D, sin imputación comarcal/IDW
- AND `pytest tests -q` sigue verde

### Requirement: PISOS-03 — Conteos honestos, sin imputación

`n_anuncios` y `n_anuncios_raw` SHALL ser conteos reales de anuncios tras re-resolución (excluidos cuarentena). Precio/superficie SHALL calcularse solo donde hay anuncio; SHALL NOT imputar por IDW ni comarcal. Valores reales post 2026-11-07: suma `n_anuncios=594`, `n_anuncios_raw=843`, 64 municipios con anuncio, L1 4 (Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39), L2 3 (Sopela 19, Zarautz 15, Santurtzi 11), zeros 188, precio observable en 60/252 (7 con `n_precio` en A+B).
(Previously: precio observable en 62/252.)

| Regla | Conducta |
|---|---|
| `n_anuncios` | count real por `codigo_ine` en `dim_municipios` |
| `n_anuncios_raw` | count pre-limpieza, sin filtrar cuarentena |
| Sin anuncio | precio/superficie `None`, sin IDW/comarcal |

#### Scenario: Municipio sin anuncios no inventa precio

- GIVEN municipio con `n_anuncios=0`
- WHEN se agregan indicadores
- THEN precio/superficie = `None` y `metodo_imputacion=ninguno` (para precio de anuncios)
- AND `python analysis/run_analisis_mongo.py` regenera 28+8 PNG + 8 CSV sin valores imputados

#### Scenario: Conteos vigentes 64/252 y 60/252

- GIVEN `mongo_esfuerzo_por_municipio.csv` regenerado
- WHEN se cuentan municipios con `n_anuncios>0` y con `precio_medio_eur` no nulo
- THEN son 64 y 60 respectivamente
- AND `grep -rn "83/252" README.md docs/` → 0 coincidencias

### Requirement: CAPAS-01 — Capas de precio visibles y etiquetadas (M7)

El sistema SHALL publicar tres capas de precio municipal en `data/resultados/` y en el mapa: (1) capa titular oficial Eustat, 159 municipios con precio observable real; (2) capa de sensibilidad IDW, 93 municipios estimados e interpolados; (3) capa de contexto, 252 municipios con el contexto oficial completado vía `transform/completar_alquiler_comarca.py` + `load_mongo` + `run_analisis` (mapa). Cada capa SHALL llevar `metodo_imputacion` (`oficial`/`idw`/`contexto`) e `is_imputed` (`false` solo en la titular). La capa IDW y la de contexto SHALL NOT presentarse nunca como precio municipal real ni mezclarse en la titular. La capa titular SHALL respaldar las conclusiones de precio; la IDW es solo sensibilidad y la de contexto solo contexto. Las figuras N1/N2 SHALL dibujar la titular con croma y la IDW con trama o leyenda; el mapa SHALL declarar 159 oficial + 93 IDW + gris sin dato.
(Previously: sin requisito de etiquetado en las figuras.)

| Capa | Municipios | `metodo_imputacion` | `is_imputed` | Uso |
|---|---|---|---|---|
| Oficial Eustat | 159 | `oficial` | `false` | titular, conclusiones |
| IDW sensibilidad | 93 | `idw` | `true` | sensibilidad, nunca conclusiones |
| Contexto | 252 | `contexto` | `true` | contexto, nunca precio municipal |

#### Scenario: Tres capas etiquetadas en resultados y mapa

- GIVEN `completar_alquiler_comarca` + `load_mongo` + `run_analisis` ejecutados
- WHEN se corre `python analysis/run_analisis_mongo.py`
- THEN existen los 3 ficheros de capas (oficial 159, IDW 93, contexto 252) con `metodo_imputacion` e `is_imputed` por fila
- AND el mapa dibuja la titular como capa principal y la IDW con trama o leyenda, declarando 159 oficial + 93 IDW

#### Scenario: La IDW no contamina la capa oficial

- GIVEN un municipio sin precio oficial pero con estimación IDW
- WHEN se calculan indicadores
- THEN la capa oficial figura «sin dato» (`None`, `metodo_imputacion=ninguno`) y la estimación solo vive en la capa IDW con `is_imputed=true`
- AND `python -c "import pandas as pd; d=pd.read_csv('data/resultados/capa_oficial.csv'); print(d['is_imputed'].sum())"` → salida: `0`
