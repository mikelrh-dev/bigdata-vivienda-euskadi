# presentacion-de-resultados — Delta

## Purpose

Corregir bootstrap, cifra 759→594, frase Nivel/Tier y mapa Tier en presentación. Estado: propuesta (delta desde base Hecho).

## ADDED Requirements

### Requirement: BOOTSTRAP-01 — `n_larga_solo_vivienda` ≠ Tier

El sistema SHALL documentar que el bootstrap usa `n_larga_solo_vivienda` 67/60/39/37 (Bilbao/Donostia/Getxo/Vitoria-Gasteiz), distinto del `n_anuncios` Tier 204/126/50/39. SHALL constar IC95 Bilbao 33.75–40.95 y Getxo 27.54–31.77. Los dos `n` SHALL NOT intercambiarse en textos ni gráficos.

#### Scenario: Bootstrap con su propio n

- GIVEN `data/resultados/bootstrap_robustos.csv`
- WHEN se lee
- THEN `n_anuncios_larga_vivienda` es 67/60/39/37, IC95 Bilbao 33.75–40.95 y Getxo 27.54–31.77
- AND el texto distingue ese `n` del Tier 204/126/50/39

### Requirement: DOCS-01 — 759→594 y frase ortogonal

El sistema SHALL corregir 759→594 en el docstring de `decor_trama` (`docs/presentacion/build_presentacion.py:218`) y en `docs/presentacion/README.md:62` (trama). SHALL constar la frase ortogonal: Nivel es tipología (`4/54/194`) y Tier es confianza por `n_anuncios` (`4/3/57/188`); son ejes ortogonales, no intercambiables.

#### Scenario: Textos en 594

- GIVEN ambos ficheros
- WHEN se verifican con `grep`
- THEN `grep -c "594"` ≥ 1 en cada uno y 759 no figura como cifra vigente
- AND consta la frase ortogonal Nivel 4/54/194 vs Tier 4/3/57/188

## MODIFIED Requirements

### Requirement: chart_mapa_tier — Aligerar sin tocar los 13 tubos

El sistema SHALL aligerar `chart_mapa_tier.svg` con utilidades de simplificación hasta <2 MB, SHALL eliminar el duplicado g1/A1 y SHALL NOT cambiar los 13 tubos ni la clasificación 252/252 A/B/C/D. Guardarraíles: sin Docker; HDFS solo raw 352; Kafka→HDFS, no Mongo; sin imputar comarcal.
(Previously: SVG ~5.9 MB sin límite de peso ni dedupe.)

#### Scenario: Mapa <2 MB sin duplicado

- GIVEN el SVG regenerado
- WHEN se mide y se busca `id="g1"`/`id="A1"`
- THEN tamaño <2 MB, un solo g1/A1 y 13 tubos intactos con 252/252
