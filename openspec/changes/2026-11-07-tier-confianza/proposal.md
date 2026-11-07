# Proposal: 2026-11-07-tier-confianza

## Intent

Sustituir los niveles L1/L2/L3 ambiguos por tiers explícitos (A/B/C/D) derivados solo de `n_anuncios` real, para que nada indicativo se lea como firme. Hoy la cobertura se comunica dispersa (precio 62/252, esfuerzo 252 sobre 159) sin lenguaje uniforme de confianza.

## Scope

### In Scope

- Definir Tier A (n≥30, 4 municipios: Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39): comparación fuerte.
- Tier B (10–29, 3: Sopela 19, Zarautz 15, Santurtzi 11): solo indicativo, con min-max + mediana + `n_precio`, separando temporal vs larga estancia.
- Tier C (1–9, 57): sin precio municipal, sin ranking.
- Tier D (0, 188): sin dato; solo contexto oficial cuando exista.
- Calcular tiers desde Mongo vía Aggregation Pipeline y exponerlos en CSV/PNG. Sin imputar.
- Mantener separado el contexto oficial: esfuerzo 252 contextual sobre 159 (Eustat 252/252), Lanbide 249/252, precio observable 62/252.

### Out of Scope

- Sin Docker; HDFS solo raw (352 ficheros); Kafka → HDFS, nunca Kafka → Mongo.
- Sin imputación comarcal/IDW para subir municipios a n≥30; `n<30` no se disfraza.
- Sin nuevas fuentes ni cambio de modelo de datos.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `presentacion-de-resultados`: lenguaje A/B/C/D en informe y gráficos; B siempre con min-max+mediana+`n_precio`.
- `mongodb-y-analisis`: `mongo_tier_confianza.csv` con tier derivado de `n_anuncios` y `n_precio` por modalidad.

## Approach

1. Pipeline PyMongo que clasifica los 252 municipios en A/B/C/D (≥30 / 10–29 / 1–9 / 0) y genera `mongo_tier_confianza.csv`.
2. Informe y gráficos leen el tier: A compara, B es rango indicativo, C/D sin precio municipal con etiqueta de confianza.
3. Validación: conteos 4/3/57/188 = 252; doble ejecución con SHA reproducible.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Umbrales leídos como arbitrarios | Med | Justificar n≥30 como robustez; B/C/D siempre etiquetados |
| B promedia temporal+larga | Med | `n_precio` y mediana por separado; prohibido agregar modalidades |
| D interpretado como "barato" | High | D = "sin dato", sin conclusión de precio |
| Regresión 252/159/249 | Low | staging+backup; verificar Eustat 252/252, Lanbide 249/252 |

## Rollback Plan

- Retirar `mongo_tier_confianza.csv` y la columna tier; el informe vuelve a L1/L2/L3. Mongo intacto.

## Success Criteria

- [ ] Los 252 municipios pertenecen a un único tier A/B/C/D (4/3/57/188) verificado desde Mongo.
- [ ] Solo Tier A sustenta ranking firme; B muestra min-max+mediana+`n_precio`; C/D sin precio municipal.
- [ ] Esfuerzo y contexto oficial citados como "252 contextual sobre 159" y Lanbide 249/252, sin lectura oficial donde n<30.
- [ ] `pytest tests -q` verde y doble ejecución de `run_analisis_mongo.py` con SHA idéntico.
