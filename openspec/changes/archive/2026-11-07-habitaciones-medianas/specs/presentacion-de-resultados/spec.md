# presentacion-de-resultados — Delta

## Purpose

Comparar habitación vs vivienda entera con `n_precio` visible, sin mezclar temporal y larga estancia.

## ADDED Requirements

### Requirement chart_habitaciones_medianas — Barras residencia vs habitaciones

El sistema SHALL generar `chart_habitaciones_medianas` en `docs/presentacion/build_presentacion.py` desde `mongo_habitaciones_por_municipio.csv` + `mongo_tier_confianza.csv` (valores Mongo, nunca tecleados). Por municipio dibujará tres series separadas — residencia temporal, residencia larga, habitaciones — nunca agregadas ni promediadas. Cada barra de habitaciones SHALL mostrar mediana con min-max y `n_precio` visible. Solo Bilbao (96) y Donostia (66) con `n >= 30` sostienen comparación firme; el resto (Vitoria 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 2, Eibar 1) SHALL etiquetarse `indicativo`/`n_insuficiente`, sin ranking ni imputación comarcal/IDW. Sin Docker; HDFS solo raw (352); Kafka → HDFS, nunca Kafka → Mongo.

#### Scenario: Tres series con n_precio visible

- GIVEN `mongo_habitaciones_por_municipio.csv` con 9 filas
- WHEN corre `build_presentacion.py`
- THEN `chart_habitaciones_medianas` aparece en `index.html` y PDF con residencia temporal, larga y habitaciones por separado
- AND cada mediana lleva su `n_precio` y min-max

#### Scenario: Solo Bilbao y Donostia firmes

- GIVEN Bilbao 96 y Donostia 66
- WHEN se lee el gráfico
- THEN la comparación residencia vs habitaciones se presenta como firme
- AND el resto figura `indicativo`, sin ordenación ni ranking

#### Scenario: Eibar indicativo sin imputación

- GIVEN Eibar con `n_precio = 1`
- WHEN se renderiza su barra
- THEN muestra mediana + min-max + `n_precio` con etiqueta `indicativo`
- AND no hay valor imputado ni ranking
