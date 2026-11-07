# Proposal: Gráficos Tier B / Mapa / Burbuja esfuerzo-n

## Intent
La presentación actual muestra el ranking agregado pero no visualiza la incertidumbre de muestra: no explica por qué solo 4 municipios son rankeables (Tier A), ni dónde están los "sin dato", ni cómo esfuerzo y muestra se relacionan. Se añaden 3 gráficos automatizados desde CSV Mongo para hacer ese límite visible sin datos inventados.

## Scope
### In Scope
- `chart_tierB_range`: barras Sopela 19, Zarautz 15, Santurtzi 11 (Tier B indicativo, n 10-29) con min-max y mediana temporal vs larga desde `mongo_tier_confianza.csv` (`n_precio_temporal`/`n_precio_larga`).
- `chart_mapa_tier`: SVG coroplético 4 niveles A-D sobre `data/procesado/municipios_euskadi_252.geojson` (join por `codigo_ine`) + capas `metodo_imputacion`/`is_imputed`: oficial 159 / IDW 93 / contexto 252.
- `chart_effort_vs_n`: burbuja X `n_anuncios`, Y `esfuerzo_joven_pct_18_34`, tamaño `n_precio`, solo 4 Tier A rankeables (n≥30); resto en banda "n insuficiente".
- Pipeline: `pipeline_tier_por_municipio` (`analysis/mongo_aggregations.py`) → export `analysis/run_analisis_mongo.py` → funciones nuevas en `docs/presentacion/build_presentacion.py` → `index.html` → `presentacion.pdf`.
### Out of Scope
- Nuevos datos, imputación de precios, ranking de n<30, cambios en extracción/HDFS/Kafka, Docker.

## Capabilities
### New Capabilities
None (sin capacidad nueva).
### Modified Capabilities
- `mongodb-y-analisis`: exporta columnas `min/max/mediana` temporal/larga por Tier B y `esfuerzo` por Tier A desde `pipeline_tier_por_municipio`; contrato añade 3 artefactos consistentes sin recomputar en el exportador.
- `presentacion-de-resultados`: `build_presentacion.py` incorpora 3 funciones nuevas y las inyecta en `index.html`/`presentacion.pdf`.

## Approach
Extender `pipeline_tier_por_municipio`; `run_analisis_mongo.py` escribe los CSV necesarios; `build_presentacion.py` genera los 3 SVG (mapa GeoJSON → SVG manual, barras/burbuja con matplotlib o SVG propio), sin valores tecleados. Join mapa estricto por `codigo_ine`; si falta, nulo sin inventar.

## Affected Areas
| Area | Impact | Descripción |
|------|--------|-------------|
| `analysis/mongo_aggregations.py` | Modified | `pipeline_tier_por_municipio` (min/max/mediana por modalidad) |
| `analysis/run_analisis_mongo.py` | Modified | Export de los 3 CSV usados por la presentación |
| `docs/presentacion/build_presentacion.py` | Modified | 3 funciones nuevas + regenera HTML/PDF |
| `openspec/specs/presentacion-de-resultados` + `mongodb-y-analisis` | Modified | Requisitos y escenarios de los 3 gráficos |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| geojson/CSV desalineados | Low | join estricto por `codigo_ine`; test 252/252 |
| n<30 leído como ranking | Med | etiquetas "indicativo"/banda n_insuficiente; sin orden |
| medianas temporales inestables | Med | mostrar n junto a cada mediana |

## Rollback Plan
Revertir el commit de `build_presentacion.py` y la pipeline; regenerar `index.html`+PDF desde la versión anterior; ningún dato en Mongo/HDFS se toca.

## Dependencies
`mongo_tier_confianza.csv` (252 filas), `mongo_esfuerzo_por_municipio.csv`, `municipios_euskadi_252.geojson` (252 features).

## Success Criteria
- [ ] Los 3 gráficos se generan automatizadamente sin literales; `run_analisis` + `build_presentacion` reproduces SHA idéntico en CSV.
- [ ] Mapa 252/252 clasificada A-D; burbuja solo 4 puntos rankeables n≥30; Tier B medianas temporal/larga por municipio.
- [ ] `pytest -q` verde y PDF incluye los 3 gráficos sin inventar datos.
