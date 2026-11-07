# presentacion-de-resultados — Delta

## Purpose

Hacer visible la incertidumbre de muestra con 3 gráficos generados desde CSV Mongo, sin valores tecleados.

## ADDED Requirements

### Requirement 1: chart_tierB_range — Barras Tier B con min-max y mediana

El sistema MUST generar `chart_tierB_range` en `build_presentacion.py` con 3 barras —Sopela 19, Zarautz 15, Santurtzi 11— leyendo `mongo_tier_confianza.csv`. Cada barra MUST mostrar min-max y la mediana temporal vs larga por separado, con `n_precio_temporal` y `n_precio_larga` visibles, y la etiqueta `indicativo` (no ranking firme). MUST NOT promediar temporal + larga.

#### Scenario: Tres barras con rango y doble mediana

- GIVEN `mongo_tier_confianza.csv` con 252 filas
- WHEN corre `build_presentacion.py`
- THEN `index.html` y `presentacion.pdf` contienen 3 barras (19/15/11) con min-max y mediana temporal vs larga
- AND cada mediana va acompañada de su `n_precio`

### Requirement 2: chart_mapa_tier — Coroplético 4 niveles y capas

El sistema MUST generar `chart_mapa_tier` como SVG desde `municipios_euskadi_252.geojson`, con join estricto por `codigo_ine` y 4 cromas A/B/C/D. MUST dibujar las capas oficial 159 / IDW 93 / contexto 252 con `metodo_imputacion` e `is_imputed`, y el texto literal `252 contextual sobre 159`. Si falta un `codigo_ine`, el municipio MUST quedar nulo, sin inventar geometría ni precio.

#### Scenario: Mapa 252/252 con capas etiquetadas

- GIVEN `municipios_euskadi_252.geojson` con 252 features
- WHEN corre `build_presentacion.py`
- THEN el SVG colorea 252/252 municipios A/B/C/D con capas 159/93/252
- AND consta el texto `252 contextual sobre 159`

### Requirement 3: chart_effort_vs_n — Burbuja solo Tier A

El sistema MUST generar `chart_effort_vs_n` (X `n_anuncios`, Y `esfuerzo_joven_pct_18_34`, tamaño `n_precio`) con solo los 4 Tier A (`n >= 30`). El resto MUST aparecer en banda `n_insuficiente` sin ordenación. MUST NOT mostrar ranking 1-16, MUST NOT imputar precios ni tocar Docker/HDFS/Kafka.

#### Scenario: Burbuja con 4 puntos y banda insuficiente

- GIVEN `mongo_esfuerzo_por_municipio.csv`
- WHEN corre `build_presentacion.py`
- THEN la burbuja contiene exactamente 4 puntos Tier A con ejes X/Y y tamaño `n_precio`
- AND `n < 30` figura en banda `n_insuficiente` sin ranking

#### Scenario: Sin valores inventados

- GIVEN los CSV generados por `run_analisis_mongo.py`
- WHEN se regenera la presentación
- THEN ningún gráfico usa literales y `pytest tests -q` sigue verde
