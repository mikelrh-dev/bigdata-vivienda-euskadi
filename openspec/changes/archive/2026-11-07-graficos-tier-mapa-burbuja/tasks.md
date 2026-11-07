# Tasks: Gráficos Tier B / Mapa / Burbuja esfuerzo-n

Change: `2026-11-07-graficos-tier-mapa-burbuja` · Specs: `mongodb-y-analisis`, `presentacion-de-resultados`.
Rutas reales (verificadas): `analysis/mongo_aggregations.py`, `analysis/run_analisis_mongo.py`,
`docs/presentacion/build_presentacion.py`, `docs/presentacion/index.template.html`,
`data/procesado/municipios_euskadi_252.geojson`, `data/resultados/mongo_tier_confianza.csv`.

Prohibiciones transversales (todas las tareas): sin Docker; HDFS solo raw inmutable
(`data/raw` y raw HDFS intactos); Kafka → HDFS, nunca a Mongo; sin imputación de precios;
sin teclear/inventar valores (todo sale de CSV Mongo); n<30 nunca rankea.

## 1. Pipeline Tier expone min/max/mediana por modalidad + esfuerzo Tier A

Archivos: `analysis/mongo_aggregations.py` (`pipeline_tier_por_municipio`), `analysis/run_analisis_mongo.py`.

- [x] 1.1 `analysis/mongo_aggregations.py`: añadir a `pipeline_tier_por_municipio` los campos
  `min_precio_temporal`, `max_precio_temporal`, `min_precio_larga`, `max_precio_larga`
  (min/max por modalidad con `$filter`/`$min`/`$max` sobre `precio_eur` no nulo, condicionados
  a Tier A/B igual que el resto de estadísticas; C/D nulos como hoy).
- [x] 1.2 Alinear nombres con la spec: `mediana_precio_temporal` / `mediana_precio_larga`
  (hoy en código `mediana_temporal` / `mediana_larga`; exponer el nombre canónico en
  `$project` sin romper `tests/test_tier_confianza.py`, que debe seguir verde).
- [x] 1.3 `analysis/run_analisis_mongo.py`: volcar los campos nuevos en
  `data/resultados/mongo_tier_confianza.csv` (252 filas) y `mongo_esfuerzo_por_municipio.csv`
  sin recomputar en el exportador (solo `pipeline_tier_por_municipio` + pipeline de esfuerzo).
- [x] 1.4 Tier A: `mongo_esfuerzo_por_municipio.csv` lleva `esfuerzo_joven_pct_18_34`
  junto a `n_anuncios`/`n_precio` solo para los 4 Tier A (Bilbao 204, Donostia 126,
  Getxo 50, Vitoria-Gasteiz 39); `n_anuncios < 30` → `n_insuficiente`, sin ordenación.
- [x] 1.5 Verificación: `python analysis/run_analisis_mongo.py` dos veces → SHA idéntico
  de `mongo_tier_confianza.csv`; Sopela/Zarautz/Santurtzi con min/max/mediana por modalidad.

## 2. `chart_tierB_range` en `build_presentacion.py` + placeholders en la plantilla

Archivos: `docs/presentacion/build_presentacion.py`, `docs/presentacion/index.template.html`.

- [x] 2.1 `build_presentacion.py`: función `chart_tierB_range()` — 3 barras
  (Sopela 19, Zarautz 15, Santurtzi 11) desde `mongo_tier_confianza.csv` (columna `nombre`/`n_anuncios`),
  cada una con `min_precio`–`max_precio` y mediana temporal vs larga por separado
  (`mediana_precio_temporal`/`mediana_precio_larga` + su `n_precio_temporal`/`n_precio_larga`
  visible junto a cada mediana). Nunca promediar temporal+larga.
- [x] 2.2 Etiqueta `indicativo` en el gráfico y en su sección (no ranking firme: los 3 Tier B
  no se ordenan como firmes, solo se representan en barras de rango).
- [x] 2.3 `index.template.html`: placeholders para el gráfico (SVGs/PNG según el patrón actual
  del build) y su texto de pie con n de cada mediana; inyectar en `index.html` al regenerar.

## 3. `chart_mapa_tier`: SVG coroplético 4 niveles + capas 159/93/252

Archivos: `docs/presentacion/build_presentacion.py`, `index.template.html`.
Fuente: `data/procesado/municipios_euskadi_252.geojson` (252 features) + `mongo_tier_confianza.csv`.

- [x] 3.1 `build_presentacion.py`: función `chart_mapa_tier()` — parseo manual del GeoJSON a SVG
  (sin librería de mapas; proyección equirectangular simple como el resto del build).
- [x] 3.2 Join estricto por `codigo_ine` GeoJSON ↔ CSV; 4 cromas A/B/C/D; 252/252 municipios
  clasificados; `codigo_ine` sin match → nulo (sin geometría ni precio inventados).
- [x] 3.3 Capas por `metodo_imputacion`/`is_imputed` del GeoJSON: oficial 159 / IDW 93 / contexto 252,
  dibujadas como capas distinguibles (croma o tramado).
- [x] 3.4 Texto literal `252 contextual sobre 159` dentro del SVG; placeholder + leyenda en
  `index.template.html`.

## 4. `chart_effort_vs_n`: burbuja solo 4 Tier A + banda `n_insuficiente`

Archivos: `docs/presentacion/build_presentacion.py`, `index.template.html`.
Fuente: `data/resultados/mongo_esfuerzo_por_municipio.csv`.

- [x] 4.1 `build_presentacion.py`: función `chart_effort_vs_n()` — X `n_anuncios`,
  Y `esfuerzo_joven_pct_18_34`, tamaño de burbuja `n_precio`; exactamente 4 puntos
  (solo Tier A con `n_anuncios >= 30`: Bilbao, Donostia, Getxo, Vitoria-Gasteiz).
- [x] 4.2 Banda vertical `n_insuficiente` para `n < 30` sin puntos ni ordenación dentro de ella;
  nada de ranking 1-16; sin imputación de esfuerzo.
- [x] 4.3 Placeholder + leyenda (`n_insuficiente` = muestra insuficiente, no ranking) en
  `index.template.html`.

## 5. Regeneración completa + tests + doble SHA

- [x] 5.1 Regenerar con `python docs/presentacion/build_presentacion.py`: los 13 PNG existentes
  + 3 SVG nuevos (`chart_tierB_range`, `chart_mapa_tier`, `chart_effort_vs_n`) + `index.html`
  + `presentacion.pdf` (los 3 gráficos visibles en el PDF).
- [x] 5.2 `pytest tests -q` verde, en concreto `tests/test_tier_confianza.py`
  (conteos 4/3/57/188 = 252, sin ranking de n<30) + grep de literales tecleados en las
  3 funciones nuevas (ningún precio/esfuerzo hardcodeado).
- [x] 5.3 Doble SHA: ejecutar `run_analisis_mongo.py` dos veces seguidas y comprobar
  SHA-256 idéntico de `mongo_tier_confianza.csv` (y `mongo_esfuerzo_por_municipio.csv`).
- [x] 5.4 Comprobación de libertad: `git status` sin cambios en `data/raw`, sin Dockerfile
  tocado ni servicio Docker levantado; Kafka no escribe en Mongo.
