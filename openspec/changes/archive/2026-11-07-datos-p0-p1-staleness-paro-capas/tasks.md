# Tasks: 2026-11-07-datos-p0-p1-staleness-paro-capas

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 400–550 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 M1+M6 (extracción) → PR2 M5+M7 (paro+capas Mongo) → PR3 M2/M3/M4 (ranking+docs) + gates |
| Delivery strategy | single-pr |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No — orden secuencial fijo abajo.
Chained PRs recommended: Yes (se pueden colapsar a un solo PR si se acepta >400 líneas).
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | M1 outliers + M6 dedup en extracción (`filtrar_outliers`/`generar_anuncios_residencial_filtrado`/`unificar_anuncios`) + mediana winsorizada en pipeline | PR1 (base `main`) | `pytest tests/test_mongo_pipeline.py tests/test_indicadores.py -q` | `python transform/generar_anuncios_residencial_filtrado.py && python transform/unificar_anuncios.py` | revertir `transform/` sin tocar `data/raw` |
| 2 | M5 paro 252 + M7 capas 159/93/252 (extract 18/21 → `corregir_empleo` → `load_mongo` staging+backup → `run_analisis`) | PR2 (base PR1) | `pytest tests/test_mongo_pipeline.py -q` | `python -m storage.load_mongo && python analysis/run_analisis_mongo.py` | rename desde `<name>__backup` en Mongo; `git checkout -- transform/ analysis/` |
| 3 | M2/M3/M4 ranking `n>=30` + 62 vs 7 + sync 759→594 (4 docs) + gates finales | PR3 (base PR2) | `pytest tests -q` (174 passed + 1 skipped) | doble `python analysis/run_analisis_mongo.py` con SHA idéntico (13 PNG + 7 CSV) | revertir `data/resultados/` + `docs/` |

Secuencia obligatoria: Fase 1 → Fase 2 → Fase 3 + Fase 4 (ambas deben terminar antes de `load_mongo`) → Fase 5 → Fase 6. Sin Docker; HDFS solo para raw (`storage/hdfs_utils.py` con 0 changes); Kafka → HDFS, nunca Kafka → Mongo; sin tocar `data/raw` (solo re-extract 18/21 que escribe raw Lanbide vía `extract/`).

## Phase 1: M1 — Outliers y mediana winsorizada (OUTLIER-01 + AGREGACION-01)

- [x] 1.1 En `transform/filtrar_outliers.py`: filtrar `precio_m2` al rango [3, 50] €/m² y `superficie_m2` al rango [10, 500] m². Fuera de rango → descarte con motivo (`precio_m2_fuera_3_50` / `superficie_fuera_10_500`), nunca recorte ni winsorice en esta capa. Contar exclusiones por motivo en el log de filtrado.
- [x] 1.2 En `transform/generar_anuncios_residencial_filtrado.py`: excluir del `precio_medio` los valores dentro de [3, 50] pero fuera del IQR (Q3+1,5·IQR), contados como `iqr_excluido`. Castear `habitaciones` a entero (`2,5` → `2`). Verificación: anuncio con `precio_m2=0,16` → motivo `precio_m2_fuera_3_50`; con `83,33` → excluido; salida: `excluidos_precio_m2=2, excluidos_superficie=0, excluidos_iqr_precio_medio=N, habitaciones_int=100%`.
- [x] 1.3 En `transform/unificar_anuncios.py` (parche correlaciones anotadas): propagar las columnas de anotación de filtrado (`motivo_exclusion`, `iqr_excluido`, `precio_m2_fuera_3_50`) a la salida unificada sin reintroducir valores fuera de rango. Generar de nuevo `data/procesado/anuncios_unificados.csv` vía `.venv/Scripts/python.exe transform/generar_anuncios_residencial_filtrado.py` + `.venv/Scripts/python.exe transform/unificar_anuncios.py`.
- [x] 1.4 En `analysis/mongo_aggregations.py` (`pipeline_indicadores_municipio` / pipeline de indicadores): calcular `mediana_precio_m2_winsorizada` con winsorización a percentil 1–99 (recorte antes de la mediana, no imputación) y exclusión IQR de la media. Solo entran anuncios con `precio_m2` en [3, 50], `superficie_m2` en [10, 500] y `habitaciones` entero (garantizado aguas arriba en 1.1–1.3). Publicar `mediana_precio_m2_winsorizada` (la mediana cruda no se usa para conclusiones). Verificación: 0 documentos con `precio_m2` fuera de [3, 50] participan en la agregación (`count_documents({'precio_m2':{'$gt':50}})` → `0`); `mongo_indicadores_municipio.csv` con 252 filas y mediana winsorizada no nula donde `n_precio≥1`.

## Phase 2: M6 — Dedup dura por `property_fingerprint` (DEDUP-01)

- [x] 2.1 En `transform/unificar_anuncios.py`: deduplicar por `property_fingerprint` (generado en `transform/generar_fingerprint.py`). El primer anuncio de cada huella conserva; el resto se descarta con motivo `duplicado_fingerprint`, contado en el log. SHAL NOT sobrevivir ningún duplicado cross-portal en la salida unificada ni en Mongo.
- [x] 2.2 Verificar dedup: `python -c "import pandas as pd; d=pd.read_csv('data/procesado/anuncios_unificados.csv'); print(d['property_fingerprint'].duplicated().sum())"` → `0`; tras la carga, sin dos documentos de `anuncios` con el mismo fingerprint.
- [x] 2.3 Test no-regresión: añadir/actualizar test de dedup (p. ej. en `tests/test_fase_datos.py` o `tests/test_mongo_pipeline.py`) que genere dos anuncios cross-portal con idéntico fingerprint y afirme 1 sola fila en la salida unificada. Gate: `pytest tests -q` en verde con el test incluido, sin regresión en el conteo previo.

## Phase 3: M5 — Paro Lanbide 249→252 (COMPLEMENTARIOS-01 + PISOS-04)

- [x] 3.1 Ejecutar extractores reales (nombres en repo, no `18_lanbide.py`/`21_lanbide.py` de la spec): `.venv/Scripts/python.exe extract/18_lanbide_paro_juvenil.py && .venv/Scripts/python.exe extract/21_lanbide_historico_paro_joven.py && .venv/Scripts/python.exe transform/corregir_empleo.py`. Objetivo: 01003/20037/48916 con `tasa_paro_lanbide_pct` no nulo.
- [x] 3.2 Sin imputación: paro municipal SHALL NOT usar valores comarcales ni IDW. Fila sin fuente oficial → `tasa_paro_lanbide_pct=None`, `metodo_imputacion=ninguno`, `is_imputed=false`. Verificación: `grep -c "is_imputed.*true" data/resultados/udalmap_paro.csv` → `0`.
- [x] 3.3 Recargar vía `storage/load_mongo.py` (staging + `<name>__backup` + rename atómico): `.venv/Scripts/python.exe -m storage.load_mongo`. Salida esperada: `252 filas, 252 oficiales, 0 imputadas`; `udalmap` con 252 documentos, `metodo_imputacion=oficial`, `is_imputed=false` en el 100 % de paro. Sustituye el 249/252 de la base.

## Phase 4: M7 — Capas de precio visibles 159/93/252 (CAPAS-01)

- [x] 4.1 Ejecutar la cadena de capas: `.venv/Scripts/python.exe transform/completar_alquiler_comarca.py` + `.venv/Scripts/python.exe -m storage.load_mongo` + `.venv/Scripts/python.exe analysis/run_analisis_mongo.py`. Publicar tres capas en `data/resultados/` con `metodo_imputacion` e `is_imputed` por fila: (1) oficial Eustat 159 (`oficial`/`false`, titular, conclusiones), (2) IDW sensibilidad 93 (`idw`/`true`, nunca conclusiones), (3) contexto 252 (`contexto`/`true`, nunca precio municipal).
- [x] 4.2 Mapa y sensibilidad: el mapa (A1/A2) dibuja la titular oficial como capa principal y IDW/contexto como sensibilidad/contexto; `data/resultados/sensibilidad_idw.csv` documenta la sensibilidad. Verificación: municipio sin precio oficial pero con IDW → capa oficial «sin dato» (`None`, `metodo_imputacion=ninguno`), estimación solo en capa IDW con `is_imputed=true`; `python -c "import pandas as pd; d=pd.read_csv('data/resultados/capa_oficial.csv'); print(d['is_imputed'].sum())"` → `0`.

## Phase 5: M2/M3/M4 — Ranking, conciliación 62 vs 7 y sync 759→594 (CONCLUSION-01 + RESPUESTA-01)

- [x] 5.1 Ranking bloqueado `n>=30`: en `analysis/run_analisis_mongo.py` (y su pipeline de ranking/esfuerzo) MUST NOT ranking con `n_anuncios<30`. Barakaldo (`n=6`) figura como «n insuficiente» con su `n` visible, nunca ordenado por encima de Donostia (`n=126`) ni de ningún Tier A; top-10 con `n>=30` exclusivamente. Verificación: `python -c "import pandas as pd; d=pd.read_csv('data/resultados/ranking_esfuerzo.csv'); print(d['n_anuncios'].min())"` → `>= 30`.
- [x] 5.2 Reconciliar 62 vs 7 en `data/resultados/README.md`: tabla con «62/252 con precio observable real» y «`n_precio=7` = A+B robusto (4 Tier A + 3 Tier B); C/D suprimidas que no se publican». Misma explicación en conclusiones (`docs/datos_finales_conclusiones_2026-11-05.md`). Verificación: `grep -n "62/252" data/resultados/README.md` ≥ 1 línea; `grep -n "n_precio=7" data/resultados/README.md` ≥ 1 línea.
- [x] 5.3 Sync 759→594/188/204 en los cuatro documentos (ruta real de presentación: `docs/presentacion/index.html`, no `presentacion/index.html`): `docs/datos_finales_conclusiones_2026-11-05.md`, `docs/informe_final.md`, `data/resultados/README.md` y `docs/presentacion/index.html` (regenerar con `.venv/Scripts/python.exe docs/presentacion/build_presentacion.py`). Cifras unidas en cada uno: 594 anuncios post re-resolución + cuarentena, 188 municipios Tier D en cero, Bilbao 204 máximo, con nota «759 era el pre-change». Verificación: `grep -c "594" <doc>` ≥ 1 en los 4 docs; `grep -c "759" docs/informe_final.md` → `0` salvo la nota histórica.

## Phase 6: Re-ejecución completa y gates (env gates)

- [x] 6.1 Ejecución completa y re-ejecutable 2×: `.venv/Scripts/python.exe transform/run_all.py` → `.venv/Scripts/python.exe -m storage.load_mongo` → `.venv/Scripts/python.exe analysis/run_analisis_mongo.py` (dos veces). Artefactos: 13 PNG + 7 CSV en `data/resultados/` y SHA idéntico en los CSV `mongo_*.csv` entre ambas ejecuciones (doble SHA).
- [x] 6.2 Gates finales: `pytest tests -q` → 174 passed + 1 skipped (sin regresión en tests previos); `.venv/Scripts/python.exe extract/generar_manifest.py --verify` → manifests raw 354 + procesados 187, 0 errores. Sin Docker; `storage/hdfs_utils.py` con 0 changes (HDFS solo raw); Kafka → HDFS, nunca Kafka → Mongo; `data/raw` intacto salvo re-extract 18/21.
