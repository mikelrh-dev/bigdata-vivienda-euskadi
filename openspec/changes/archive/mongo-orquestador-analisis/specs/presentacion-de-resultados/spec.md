# Delta for presentacion-de-resultados

## ADDED Requirements

### Requirement: AUTOMATIZACION-ANALISIS-01 — Orquestador de los 8 pipelines

El sistema SHALL proveer `analysis/run_analisis_mongo.py` con `run_all_estandar` que importe y ejecute en orden fijo los 8 pipelines de `analysis/mongo_aggregations.py`: `pipeline_indicadores_municipio`, `pipeline_alquiler_por_municipio`, `pipeline_modalidades`, `pipeline_top_municipios_por_esfuerzo`, `pipeline_esfuerzo_por_sexo`, `pipeline_accesibilidad_extendida`, `pipeline_udalmap_extendido_osrm` y `pipeline_vpo_por_municipio`. El orquestador SHALL comparar la huella de dos ejecuciones y SHALL fallar si difieren.

#### Scenario: Los 8 pipelines se ejecutan en orden fijo

- GIVEN MongoDB con la base cargada
- WHEN se llama a `run_all_estandar`
- THEN se ejecutan los 8 pipelines en el orden fijo
- AND el resultado es un dict con las 8 claves y sus filas

#### Scenario: Dos ejecuciones reproducen la misma huella

- GIVEN los resultados de la primera ejecucion
- WHEN se ejecuta de nuevo `run_all_estandar` y se calcula la huella
- THEN ambas huellas coinciden
- AND los conteos por pipeline coinciden

### Requirement: PREPARACION-VISUALIZACION-01 — Tres CSV desde PyMongo

El sistema SHALL exportar automaticamente desde PyMongo, sin valores tecleados, 3 conjuntos preparados para representar: `data/resultados/mongo_esfuerzo_por_municipio.csv` (252 filas), `data/resultados/mongo_alquiler_por_municipio.csv` (252 filas) y `data/resultados/mongo_modalidades.csv` (2 filas). Cada CSV SHALL tener cabecera utilizable directamente para representar y SHALL coincidir con los pipelines en memoria.

#### Scenario: Exportacion de tres conjuntos

- GIVEN los resultados en memoria de los pipelines
- WHEN el orquestador exporta los CSV
- THEN existen los 3 ficheros con cabecera y filas no vacias
- AND ningun valor procede de un numero escrito a mano

#### Scenario: Los CSV coinciden con los pipelines en memoria

- GIVEN los CSV exportados en un directorio temporal
- WHEN se leen con `csv.DictReader`
- THEN cabeceras y conteos coinciden con los pipelines en memoria
- AND regenerar reproduce los mismos conteos

## MODIFIED Requirements

Ninguno. No se altera el comportamiento de los pipelines existentes.

## REMOVED Requirements

Ninguno.

## RENAMED Requirements

Ninguno.
