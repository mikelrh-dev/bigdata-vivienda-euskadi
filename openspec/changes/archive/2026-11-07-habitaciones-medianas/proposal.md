# Proposal: 2026-11-07-habitaciones-medianas

## Intent

El alquiler por habitaciones (compartir vivienda) hoy no tiene vista propia: 201 anuncios en 9 municipios, disponibles solo en `data/procesado/anuncios_habitaciones_unificados.csv`, sin mediana municipal comparable. Se propone vista separada, sin mezclar con el precio municipal de residencia (62/252) ni con los tiers A/B/C/D, para responder: ¿cuánto cuesta una habitación por municipio frente a una vivienda entera?

## Scope

### In Scope

- Normalizar los 9 municipios por `codigo_ine` (Bilbao 96, Donostia-San Sebastián 66, Vitoria-Gasteiz 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 2, Eibar 1; suma 201).
- Pipeline `pipeline_habitaciones_por_municipio` en `analysis/mongo_aggregations.py`: mediana, mínimo, máximo y `n_precio` por municipio desde anuncios de habitaciones.
- Exportar `mongo_habitaciones_por_municipio.csv` en `analysis/run_analisis_mongo.py` (pipeline nº 11, sin tocar los 10 actuales).
- Gráfico `chart_habitaciones_medianas` en `docs/presentacion/build_presentacion.py`: barras residencia vs habitaciones con `n_precio`, temporal y larga estancia nunca mezclados.

### Out of Scope

- Sin Docker; HDFS solo raw (352 ficheros); Kafka → HDFS, nunca Kafka → Mongo.
- Sin ranking con n<30 (solo Bilbao y Donostia lo superan; el resto, solo indicativo con min-max+mediana+`n_precio`, sin imputar comarcal).
- Sin tocar Tier A/B/C/D ni el precio municipal 62/252; sin nuevas fuentes ni cambio de modelo de datos.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `mongodb-y-analisis`: pipeline y CSV propios de habitaciones por municipio.
- `presentacion-de-resultados`: gráfico de comparación residencia vs habitaciones con `n_precio`.

## Approach

1. Pipeline que agrupa anuncios de habitaciones por `codigo_ine` normalizado y calcula mediana/min/max/`n_precio` (sin winsorizar ni imputar).
2. Orquestador añade el pipeline nº 11 y exporta `data/resultados/mongo_habitaciones_por_municipio.csv`.
3. `build_presentacion.py` genera `chart_habitaciones_medianas`: residencia (temporal y larga por separado) frente a habitaciones, con `n_precio` visible y etiqueta "indicativo" si n<30.
4. Validación: 9 filas, suma `n_precio`=201, doble ejecución con SHA idéntico, `pytest tests -q` verde.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Variantes de nombre inflan municipios | High | Normalizar por `codigo_ine`, no por texto |
| n<30 leído como firme | Med | "Indicativo" en gráfico; sin ranking |
| Mezcla residencia con habitaciones | Med | CSV y gráfico separados; modalidades nunca agregadas |

## Rollback Plan

- Retirar pipeline nº 11, CSV y gráfico; Mongo y los 10 pipelines quedan intactos.

## Success Criteria

- [ ] `mongo_habitaciones_por_municipio.csv` con 9 municipios, mediana/min/max/`n_precio`, suma 201.
- [ ] Solo Bilbao y Donostia sostienen comparación firme; n<30 sin ranking.
- [ ] Gráfico con residencia (temporal/larga separados) vs habitaciones y `n_precio`.
- [ ] Precio municipal 62/252 y tiers A/B/C/D sin cambios.
