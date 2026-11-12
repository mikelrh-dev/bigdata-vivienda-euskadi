# Comparabilidad — Especificación

## Purpose

Congelar las reglas de comparabilidad del proyecto: capas de precio, unidades,
vintages y denominadores. Evita que figuras y conclusiones mezclen magnitudes
no comparables.

## Requirements

### Requirement: COMPARABILIDAD-01 — Capas no mezcladas

El sistema SHALL publicar y dibujar las capas de precio separadas: oficial
Eustat 2024 (159 municipios, `metodo_imputacion=oficial`, `is_imputed=false`),
IDW comarcal (93, `idw`, `true`) y contexto (252, `contexto`, `true`). Las
figuras N1/N2/A1/A2/F/P SHALL usar solo la capa oficial o etiquetar
explícitamente la IDW; ninguna mediana SHALL mezclar capas sin etiqueta.

#### Scenario: Mapa e histograma con capas separadas

- GIVEN `mongo_esfuerzo_por_municipio.csv` (252 filas: 159 oficial + 93 idw)
- WHEN se generan N1/N2/A1/A2
- THEN las figuras usan solo `metodo_imputacion=oficial` o etiquetan la IDW
- AND el mapa declara 159 oficial + 93 IDW

### Requirement: COMPARABILIDAD-02 — Unidades y vintages etiquetados

El sistema SHALL etiquetar la unidad (€/mes, €/m², €/habitación) y el vintage
(alquiler 2024, anuncios 2026, paro 2024, renta 2024) en cada figura y columna.
Las figuras que comparen modalidades SHALL usar €/m² (H8b); H6 SHALL declarar
€/habitación; H10 SHALL declarar el rango de edad de su esfuerzo.

#### Scenario: Figuras con unidad y vintage

- GIVEN las figuras N1/N2/A1/A2/F/P/H6/H8/H8b/H10/I
- WHEN se generan
- THEN cada una declara unidad y vintage
- AND H8b usa €/m² y H6 usa €/habitación

### Requirement: COMPARABILIDAD-03 — Denominadores declarados

El sistema SHALL declarar el denominador de cada variante de esfuerzo. El
canónico `esfuerzo_joven_pct_18_34` usa `renta_hogar` INE Atlas 2024; las
variantes fiscal/OVJ/hombres/mujeres SHALL declarar su denominador y no
presentarse como esfuerzo joven 18-34.

#### Scenario: Denominador canónico declarado

- GIVEN `data/procesado/analisis_variables_base.csv`
- WHEN se lee el denominador de `esfuerzo_joven_pct_18_34`
- THEN la base es `renta_hogar` INE Atlas 2024 (Bilbao 47.550), no Eustat RPF (28.521)
