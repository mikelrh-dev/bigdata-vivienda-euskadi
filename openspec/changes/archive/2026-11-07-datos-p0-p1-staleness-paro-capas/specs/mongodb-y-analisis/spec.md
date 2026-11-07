# mongodb-y-analisis — Delta

## Purpose

Alinear la capa MongoDB con los huecos P0/P1: (M1) pipeline de indicadores con mediana winsorizada y exclusión IQR del precio medio, para que ningún `precio_m2` fuera de [3, 50] ni superficie fuera de [10, 500] llegue al cálculo; (M5) carga de `udalmap` con el paro Lanbide normalizado 252/252, sin imputar; (M7) capas visibles de precio — Eustat 159 oficial como capa titular, IDW 93 como capa de sensibilidad y contexto 252 — cada una etiquetada con `metodo_imputacion` e `is_imputed`. RESTRICCIONES: sin Docker; HDFS solo para raw; Kafka solo hacia HDFS, nunca hacia Mongo. Estado: propuesta (delta desde base Hecho).

## MODIFIED Requirements

### Requirement: AGREGACION-01 — Pipeline con mediana winsorizada y exclusión IQR (M1)

La pipeline `pipeline_indicadores_municipio` SHALL calcular la mediana de `precio_m2` con winsorización al percentil 1–99 (los valores extremos se recortan antes de la mediana, no se imputan) y SHALL excluir de la media/preciomedio los valores fuera del rango intercuartílico. Solo entran anuncios con `precio_m2` en [3, 50] y `superficie_m2` en [10, 500] y `habitaciones` entero (ya garantizado por OUTLIER-01 en extracción). `pipeline_tier_por_municipio` SHALL mantener 252 filas con `n_anuncios`, `n_precio`, `min_precio`, `max_precio`, `n_precio_temporal`, `n_precio_larga`. El `n` sigue siendo propio de Mongo, nunca de HDFS. La mediana winsorizada se SHALL publicar como `mediana_precio_m2_winsorizada` y la mediana cruda no se SHALL usar para conclusiones.

#### Scenario: Mediana winsorizada con exclusión IQR

- GIVEN anuncios con `precio_m2` extremos dentro de [3, 50] pero fuera de IQR
- WHEN corre `python analysis/run_analisis_mongo.py`
- THEN `mongo_indicadores_municipio.csv` tiene 252 filas y `mediana_precio_m2_winsorizada` no nula donde `n_precio≥1`
- AND la salida del análisis: `13 PNG + 6 CSV`, doble ejecución con SHA idéntico en los 6 `mongo_*.csv`

#### Scenario: Ningún outlier contamina la agregación

- GIVEN la colección `anuncios` cargada tras OUTLIER-01 y DEDUP-01
- WHEN se ejecuta la pipeline
- THEN 0 documentos con `precio_m2` fuera de [3, 50] o `superficie_m2` fuera de [10, 500] participan en la agregación
- AND `python -c "import pymongo; c=pymongo.MongoClient().vivienda_euskadi.anuncios; print(c.count_documents({'precio_m2':{'$gt':50}}))"` → salida: `0`

### Requirement: PISOS-04 — Paro 252/252 desde Lanbide normalizado (M5)

Tras la extracción M5 (extractores 18/21 + `corregir_empleo`), el sistema SHALL cargar `udalmap` con paro oficial en 252/252 municipios: `tasa_paro_lanbide_pct` no nulo, `metodo_imputacion=oficial`, `is_imputed=false`. La carga SHALL ir por staging + `<name>__backup` + rename atómico vía `storage/load_mongo.py` (`python -m storage.load_mongo`). Doble ejecución de `run_analisis_mongo.py` SHALL dar SHA idéntico en los 6 `mongo_*.csv`. Sustituye el 249/252 de la base.

#### Scenario: Paro 252/252 verificado tras la carga

- GIVEN extractores 18/21 ejecutados y `corregir_empleo` aplicado
- WHEN corre `python -m storage.load_mongo` y luego `python analysis/run_analisis_mongo.py`
- THEN `udalmap` tiene 252 documentos con paro oficial y 0 con `is_imputed=true`
- AND `pytest tests -q` en verde, con conteo de paro `252/252` en el log de carga

## ADDED Requirements

### Requirement: CAPAS-01 — Capas de precio visibles y etiquetadas (M7)

El sistema SHALL publicar tres capas de precio municipal en `data/resultados/` y en el mapa: (1) capa titular oficial Eustat, 159 municipios con precio observable real; (2) capa de sensibilidad IDW, 93 municipios estimados e interpolados; (3) capa de contexto, 252 municipios con el contexto oficial completado vía `transform/completar_alquiler_comarca.py` + `load_mongo` + `run_analisis` (mapa). Cada capa SHALL llevar `metodo_imputacion` (`oficial`/`idw`/`contexto`) e `is_imputed` (`false` solo en la titular). La capa IDW y la de contexto SHALL NOT presentarse nunca como precio municipal real ni mezclarse en la titular. La capa titular SHALL respaldar las conclusiones de precio; la IDW es solo sensibilidad y la de contexto solo contexto.

| Capa | Municipios | `metodo_imputacion` | `is_imputed` | Uso |
|---|---|---|---|---|
| Oficial Eustat | 159 | `oficial` | `false` | titular, conclusiones |
| IDW sensibilidad | 93 | `idw` | `true` | sensibilidad, nunca conclusiones |
| Contexto | 252 | `contexto` | `true` | contexto, nunca precio municipal |

#### Scenario: Tres capas etiquetadas en resultados y mapa

- GIVEN `completar_alquiler_comarca` + `load_mongo` + `run_analisis` ejecutados
- WHEN se corre `python analysis/run_analisis_mongo.py`
- THEN existen los 3 ficheros de capas (oficial 159, IDW 93, contexto 252) con `metodo_imputacion` e `is_imputed` por fila
- AND el mapa dibuja la titular como capa principal y las otras como sensibilidad/contexto, con salida: `13 PNG` generados

#### Scenario: La IDW no contamina la capa oficial

- GIVEN un municipio sin precio oficial pero con estimación IDW
- WHEN se calculan indicadores
- THEN la capa oficial figura «sin dato» (`None`, `metodo_imputacion=ninguno`) y la estimación solo vive en la capa IDW con `is_imputed=true`
- AND `python -c "import pandas as pd; d=pd.read_csv('data/resultados/capa_oficial.csv'); print(d['is_imputed'].sum())"` → salida: `0`
