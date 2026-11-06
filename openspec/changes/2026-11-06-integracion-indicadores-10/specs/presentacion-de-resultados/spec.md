# Delta: presentacion-de-resultados (INDICADORES-01)

## MODIFIED Requirements

### Requirement: INDICADORES-01 — Cinco indicadores distintos non-legacy

El sistema SHALL calcular 5 indicadores distintos (non-legacy) de 2 o más fuentes, con pipeline Mongo verdadero o silver justificado documentado. `esfuerzo_16_29` se archiva como legacy y MUST NOT contar como indicador independiente en el conteo. Los CSV canónicos con huella SHALL ser 253/253 filas y regenerables; cualquier cambio de huella SHALL regenerarse desde MongoDB, nunca teclearse. Tensión social y paro Lanbide SHALL declarar si el cálculo es Mongo o silver con `metodo_imputacion` preservado y flag `is_imputed`.

#### Scenario: Cinco indicadores distintos

- GIVEN los indicadores documentados en `docs/matriz_indicadores.md`
- WHEN se listan los non-legacy de 2+ fuentes
- THEN hay exactamente 5: (1) esfuerzo 18-34, (2) tensión social, (3) paro Lanbide, (4) precio €/m2 oficial, (5) VPO terminadas ‰ (Open Data Euskadi indicador 73 + población `dim_municipios`, campo común `codigo_ine`)
- AND `esfuerzo_16_29` no aparece en el conteo

#### Scenario: VPO como 5º indicador

- GIVEN la colección `vpo_municipal` (252 municipios, rango 0-50 ‰) y `dim_municipios` (252)
- WHEN se ejecuta `pipeline_vpo_por_municipio` (con `$group/$lookup/$unwind`)
- THEN el indicador VPO está calculado desde 2 fuentes por `codigo_ine` y citado en la matriz
- AND ningún valor está tecleado a mano

#### Scenario: Huella regenerada

- GIVEN los CSV canónicos `mongo_esfuerzo_por_municipio`, `mongo_alquiler_por_municipio`, `mongo_modalidades`
- WHEN se regeneran desde MongoDB con `analysis/run_analisis_mongo.py`
- THEN su SHA-256 figura en `docs/matriz_indicadores.md` y coincide con el fichero calculado
- AND el conjunto de huellas se verifica sin teclear valores
