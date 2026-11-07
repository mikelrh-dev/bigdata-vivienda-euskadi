# Tasks: 2026-11-07-habitaciones-medianas

## 1. Pipeline `pipeline_habitaciones_por_municipio` — mediana municipal de habitaciones

- [x] Inspeccionar `analysis/mongo_aggregations.py` (patrón de `pipeline_tier_por_municipio` y `pipeline_alquiler_por_municipio`) y la colección `anuncios_habitaciones_unificados` en `vivienda_euskadi` (201 anuncios).
- [x] Añadir `pipeline_habitaciones_por_municipio` en `analysis/mongo_aggregations.py`: `$group` por `codigo_ine` normalizado (no por texto de municipio) sobre `anuncios_habitaciones_unificados_bigdata`/`anuncios_habitaciones_unificados`, calculando `codigo_ine`, `municipio`, `n`, `n_precio`, `min_precio_eur`, `max_precio_eur`, `mediana_precio_eur` (mediana cruda, sin winsorizar ni imputar comarcal/IDW).
- [x] Exponer como función pública en `analysis/mongo_aggregations.py` (importable como las demás `pipeline_*`); añadir alias en `__all__` si existe.
- [x] Verificar en `analysis/mongo_aggregations.py` que no se modifica ninguna función existente (Tier A/B/C/D, precio 62/252 intactos).
- [x] Validación unitaria: ejecutar la pipeline contra Mongo local y comprobar 9 municipios con `n_precio` 96/66/12/11/8/3/2/2/1 (=201): Bilbao 96, Donostia-San Sebastián 66, Vitoria-Gasteiz 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 2, Eibar 1; cada fila con `n`, `n_precio`, min, max y mediana.

## 2. Export `mongo_habitaciones_por_municipio.csv` — pipeline nº 11

- [x] En `analysis/run_analisis_mongo.py`: registrar `pipeline_habitaciones_por_municipio` como pipeline nº 11 (sin tocar ni reordenar los 10 actuales: `pipeline_indicadores_municipio`, `pipeline_alquiler_por_municipio`, `pipeline_modalidades`, `pipeline_top_municipios_por_esfuerzo`, `pipeline_esfuerzo_por_sexo`, `pipeline_accesibilidad_extendida`, `pipeline_udalmap_extendido_osrm`, `pipeline_vpo_por_municipio`, `pipeline_vpo_terminadas`, `pipeline_tier_por_municipio`).
- [x] Añadir a `CSV_POR_PIPELINE`/`EXPORTS` el par `("mongo_habitaciones_por_municipio.csv", "pipeline_habitaciones_por_municipio")` y resolver la escritura en `data/resultados/mongo_habitaciones_por_municipio.csv` (sin recomputar ni teclear valores a mano; todo desde Mongo vía la pipeline).
- [x] Ejecutar `python analysis/run_analisis_mongo.py` y verificar: CSV con 9 filas, suma `n_precio` = 201, columnas `codigo_ine`, `municipio`, `n`, `n_precio`, `min_precio_eur`, `max_precio_eur`, `mediana_precio_eur`.

## 3. Gráfico `chart_habitaciones_medianas` — residencia vs habitaciones

- [x] En `docs/presentacion/build_presentacion.py`: añadir `chart_habitaciones_medianas(habitaciones, tier)` que lea `data/resultados/mongo_habitaciones_por_municipio.csv` y `mongo_tier_confianza.csv` (valores Mongo, nunca tecleados) y genere `docs/presentacion/assets/chart_habitaciones_medianas.svg`.
- [x] Dibujar 3 series nunca agregadas ni promediadas: residencia temporal, residencia larga y habitaciones (una barra por municipio y serie; residencia temporal y larga siempre por separado).
- [x] Cada barra de habitaciones muestra `mediana_precio_eur` con min-max (`min_precio_eur`/`max_precio_eur`) y `n_precio` visible.
- [x] Etiquetar Bilbao (96) y Donostia (66) como comparación firme (`n>=30`); Vitoria (12), Barakaldo (11), Getxo (8), Irun (3), Errenteria (2), Durango (2), Eibar (1) como `indicativo`/`n_insuficiente`, sin ranking ni imputación comarcal/IDW.
- [x] En `docs/presentacion/index.template.html`: añadir placeholder `<img src="assets/chart_habitaciones_medianas.svg" alt="...">` en la sección de comparación residencia vs habitaciones (mismo patrón que `chart_tierB_range`/`chart_mapa_tier`); no tocar los gráficos existentes.
- [x] Ejecutar `python docs/presentacion/build_presentacion.py` y comprobar que el SVG se genera y que `index.html`/PDF incluyen `chart_habitaciones_medianas` con las 3 series y `n_precio`.

## 4. Regeneración completa + validación (doble SHA, pytest, Tier 252)

- [x] Regenerar `data/resultados/mongo_habitaciones_por_municipio.csv` (vía `python analysis/run_analisis_mongo.py`) y `chart_habitaciones_medianas.svg` + `index.html` + PDF (vía `python docs/presentacion/build_presentacion.py`).
- [x] Doble SHA: ejecutar `run_analisis_mongo.py` dos veces y comparar SHA256 de `mongo_habitaciones_por_municipio.csv` (idéntico); repetir para el SVG si aplica (doble ejecución de `build_presentacion.py`).
- [x] `pytest tests -q` (vía `uv run python -m pytest tests -q`): esperado 177 passed, 1 skipped (actual confirmado 2026-11-08); verde sin regresiones.
- [x] Verificar Tier intacto: `mongo_tier_confianza.csv` mantiene 252 filas y precio observable 62/252, Tier A/B/C/D sin cambios (diff contra la versión previa).
- [x] Comprobación final de arquitectura: sin Docker (sin `docker-compose` ni `Dockerfile` nuevos); HDFS solo raw (352 ficheros); Kafka → HDFS, nunca Kafka → Mongo (no se añade ningún conector Kafka→Mongo).
