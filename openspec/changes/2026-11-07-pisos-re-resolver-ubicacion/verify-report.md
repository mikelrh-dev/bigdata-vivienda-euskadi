# Verification Report — 2026-11-07-pisos-re-resolver-ubicacion

**Change:** `2026-11-07-pisos-re-resolver-ubicacion` (Modo openspec)
**Mode:** openspec-file (sin Engram)
**Fecha:** 2026-11-07 (verificación local, branch `master`, repo `C:\Users\mikel\Documents\bigdata-vivienda-euskadi`)
**Alcance verificado:** proposal.md + 3 delta specs (9 requirements, 12 scenarios) + tasks.md (6 tareas, 27 acceptance checkboxes)
**Artefactos leídos:**
- `openspec/changes/2026-11-07-pisos-re-resolver-ubicacion/proposal.md:1-79` (Intent L5-L6, Approach L37-L39, Success Criteria L72-L75)
- `openspec/changes/2026-11-07-pisos-re-resolver-ubicacion/tasks.md:1-155` (T1 L18-L38, T2 L41-L62, T3 L65-L87, T4 L90-L110, T5 L113-L131, T6 L134-L155)
- `openspec/changes/2026-11-07-pisos-re-resolver-ubicacion/specs/extraccion-datos/spec.md:1-53` (EXTRACCION-01, PISOS-01, PISOS-02)
- `openspec/changes/2026-11-07-pisos-re-resolver-ubicacion/specs/mongodb-y-analisis/spec.md:1-58` (CARGA-SEGURA-01, LIMPIEZA/TRANSFORM-01, PISOS-03, PISOS-04)
- `openspec/changes/2026-11-07-pisos-re-resolver-ubicacion/specs/presentacion-de-resultados/spec.md:1-50` (CONCLUSION-01, PISOS-05)
- Sin `design.md` en el change (verificación spec/correctness + runtime; coherencia de diseño omitida por ausencia, no por defecto).

## Final verdict: GATE PASS WITH WARNINGS (P1 abiertos)

Los 5 gates delegados **pasan en fuente primaria** (pytest 166/1, doble SHA, conteos dim/esfuerzo/Mongo-anuncios, manifests, no-Docker/Kafka→HDFS). Hay **P1 abiertos no cubiertos por test** que deben resolverse antes de `sdd-archive`: (1) `indicadores` en Mongo sin refrescar (suma 759 vs 594) por `dim_municipios_enriquecido.csv` stale de 2026-11-05; (2) 27 checkboxes de `tasks.md` sin marcar pese a evidencia de implementación. No se declara FAIL porque ningún gate delegado falla; se declara PASS WITH WARNINGS y la decisión de archivar con P1 corresponde al orquestador/usuario.

## 1. Completeness (tasks.md)

> `tasks.md:18-155` define 6 tareas. Todos los checkboxes aparecen como `- [ ]` (27 sin marcar, 0 marcados). La evidencia de runtime siguiente prueba implementación completa; el estado del checkbox es administrativo (P1-2), no falta de código.

| Tarea | Estado por evidencia | Evidencia (fichero:línea + comando) |
|---|---|---|
| T1 Prototipo read-only subtítulo→variantes+gazetteer, resueltos+cuarentena=universo | COMPLETA | `transform/muni_resolve.py:79` `GAZETTEER_RAW`, `:163` `resolver_pisos_por_texto`, `:246-267` pases gazetteer; `tests/test_pisos_ubicacion_real.py:131-151` `test_universo_resueltos_o_cuarentena` (unión ≥230, res≥200, cuar≥20) PASSED |
| T2 Parche `transform_pisos`+`resolver_codigo`, `municipio_busqueda` prohibida, cuarentena | COMPLETA | `transform/unificar_anuncios.py:147` `def transform_pisos`, `:148-154` subtítulo/título manda; `transform/muni_resolve.py:279` `resolver_codigo` (sin texto → `(None,None)`); `extract/08_pisos_scraper.py:166,170` conserva búsqueda como metadata + `es_busqueda_no_ubicacion=True`; `grep -n "municipio_busqueda" transform/unificar_anuncios.py` → solo línea 64 (filtro validez), cero en `transform_pisos` (127+) — ver §Gates |
| T3 Re-ejecución `unificar`→`aplicar_cobertura` + recount L1/L2/L3 + precio | COMPLETA | `transform/aplicar_cobertura_mercado.py:41-63` cuarentena excluida de `n_anuncios`, tipología `n>=30→Nivel1` (`:68-71`); `data/procesado/dim_municipios.csv` 252 filas, suma `n_anuncios=594`, `n_raw=843`; `data/procesado/cuarentena_pisos.csv` 45 filas |
| T4 Recarga Mongo staging+backup+rename + 13 PNG/6 CSV + doble SHA | COMPLETA (con P1-1 en `indicadores`) | `storage/mongo.py:152-163` `replace_collection` staging+`__backup`+rename `dropTarget=True`; `storage/load_mongo.py:233-234` CARGA-SEGURA-01; Mongo `anuncios=594`, `anuncios__backup=594`; `data/resultados` 13 PNG + 6 `mongo_*.csv`, doble `sha256sum` idéntico (ver §Gates) |
| T5 Tests `test_pisos_ubicacion_real.py` + suite (151 base) | COMPLETA | `tests/test_pisos_ubicacion_real.py:47-246` 16 tests (15 passed + 1 skipped destructivo `MONGO_ALLOW_DESTRUCTIVE!=1` en `:239`); suite total `166 passed, 1 skipped` (ver §Gates) |
| T6 Sync docs (Nivel2/3, tipología, guion, precio, manifest) | COMPLETA (con P2-1 spec stale) | `README.md:143-144` Bilbao 204/Donostia 126/Getxo 50/Vitoria 39, Nivel1 4/Nivel2 54/Nivel3 194, L2=3; `docs/conclusiones_municipios.md:29-31` L2 3 con min-max+mediana+`n_precio`, precio 62/252, «252 contextual sobre 159»; `docs/guion_defensa.md:45-47` falsación exterior/no-ascensor + 62/252; `docs/metodologia.md:17` misma tipología |

## 2. Build / Tests / Coverage (evidencia literal)

### Gate 1 — pytest
```
$ .venv/Scripts/python -m pytest tests -q
........................................................................ [ 43%]
........................................................................ [ 86%]
.......s...............                                                  [100%]
166 passed, 1 skipped in 6.57s
EXIT:0
```
```
$ .venv/Scripts/python -m pytest tests --collect-only -q
167 tests collected in 0.58s
$ .venv/Scripts/python -m pytest tests -q -rs
SKIPPED [1] tests\test_pisos_ubicacion_real.py:239: skip separado: MONGO_ALLOW_DESTRUCTIVE!=1
166 passed, 1 skipped in 6.34s
```
```
$ .venv/Scripts/python -m pytest tests/test_pisos_ubicacion_real.py -q
...............s                                                         [100%]
15 passed, 1 skipped in 1.10s
$ .venv/Scripts/python -m pytest tests/test_pisos_ubicacion_real.py --collect-only -q
16 tests collected in 0.44s
```
Colectados/pasados/skipped separados: **167 collected = 166 passed + 1 skipped**. Pisos: **16 collected = 15 passed + 1 skipped**. Base: 151 + 15 pisos = 166 ✓. Esperado `166 passed 1 skipped (151 base +15 pisos)` → **PASS**. Skip único es `tests/test_pisos_ubicacion_real.py:239` (`MONGO_ALLOW_DESTRUCTIVE!=1`, destructivo separado por diseño, no fallo de entorno).

### Gate 2 — Doble SHA `run_analisis_mongo` x2 + PNG 13
```
$ ls data/resultados/*.png | wc -l
13
$ ls data/resultados/mongo_*.csv | wc -l
6
# SHA RUN1 (tras 1ª ejecución)
c2b3b0aca38d52c7f9bedb1c6202c1e4eb7fc8557509b7dcfec0516beaa8ce5e *.../mongo_accesibilidad_extendida.csv
ff39e852d27a754eabb2fe3db76c71c1ac35e8a0cdcd4e799ff9fb7c9798263e *.../mongo_alquiler_por_municipio.csv
2c72d19377e3d3ffea005c0d57079150bf5670236f887227a1c6d1068d48b999 *.../mongo_esfuerzo_por_municipio.csv
67e8120a311666d8cb7d3522766e8a19da468da34fb578c900d702bf2d81bcf0 *.../mongo_modalidades.csv
66e8a674af835c3f60d1b629f119095f16f25e7ae6b2197ab203feb9eff929d7 *.../mongo_vpo_por_municipio.csv
d9a512c82d9c493499b757fbb914b3ee331e0b3e390b59a64c1f4ab6c1f587bb *.../mongo_vpo_terminadas_por_municipio.csv
# SHA RUN2 (tras 2ª ejecución) — idéntico byte a byte:
c2b3b0aca38d52c7f9bedb1c6202c1e4eb7fc8557509b7dcfec0516beaa8ce5e *... (6/6 idénticos)
huella: 32ce4b0d43f114cdb3ce77dbb3d5b2eacfb2458d17cb349153755fa16acaf65c
reproducibilidad: ok (dos ejecuciones con la misma huella)
```
**PASS** (PISOS-04). Además, `tests/test_pisos_ubicacion_real.py:228-236` `test_sha_doble_identico` y `:183-195` `test_resultados_13png_6csv` pasaron.

### Gate 3 — Conteos (dim + anuncios_unificados + Mongo + esfuerzo)
Comandos (Python/pandas sobre silver + pymongo sobre `vivienda_euskadi`):

```
$ python -c "dim=pd.read_csv('data/procesado/dim_municipios.csv')"
filas dim: 252
Nivel3 194 / Nivel2 54 / Nivel1 4
sum n_anuncios: 594 | sum n_anuncios_raw: 843
zeros n_anuncios==0: 188 | L1>=30: 4 | L2 10-29: 3 | L3 1-9: 57
TOP: Bilbao 204, Donostia 126, Getxo 50, Vitoria 39, Sopela 19, Zarautz 15, Santurtzi 11, Leioa 9 ...

$ python -c "u=pd.read_csv('data/procesado/anuncios_unificados.csv')"
filas unificados: 594; portal fotocasa 428 / pisos 87 / realtyapi 79
distintos codigo_ine con precio_eur: 62  (=> precio 62/252)
superficie distintos: 63

$ python -c "e=pd.read_csv('data/resultados/mongo_esfuerzo_por_municipio.csv')"
filas esfuerzo: 252; precio_medio_eur non-null: 62; n_anuncios sum: 594; n==0: 188; L1>=30: 4
tasa_paro non-null esfuerzo: 249

$ mongosh/pymongo (vivienda_euskadi, estimated_document_count)
anuncios 594; indicadores 252; municipios 252; alquiler_municipal 252; anuncios__backup 594
tasa_paro_lanbide_pct non-null en indicadores: 249

$ wc -l data/procesado/dim_municipios.csv data/procesado/anuncios_unificados.csv
253 data/procesado/dim_municipios.csv      # 252 + cabecera
595 data/procesado/anuncios_unificados.csv # 594 + cabecera
$ wc -l data/procesado/cuarentena_pisos.csv
46  # 45 datos + cabecera (fuera_de_euskadi 45)
```

| Valor delegado | Observado | Veredicto |
|---|---|---|
| Mongo anuncios 594 | `anuncios=594`, CSV 594, esfuerzo suma 594 | PASS |
| municipios/indicadores/alquiler 252 (docs) | 252/252/252 | PASS |
| tasa_paro 249 | enriquecido 249, esfuerzo 249, Mongo indicadores 249 | PASS |
| equilibrio n_raw 843 | `dim sum n_raw=843` | PASS |
| L1 4: Bilbao 204 Donostia 126 Getxo 50 Vitoria 39 | dim + esfuerzo exactos | PASS en dim/esfuerzo; **FAIL en `indicadores` (173/113/40/39, suma 759) → P1-1** |
| L2 3: Sopela 19 Zarautz 15 Santurtzi 11 | exacto en dim/esfuerzo | PASS |
| zeros 188 | dim 188, esfuerzo 188 | PASS |
| precio 62/252 | distintos con `precio_eur` 62; esfuerzo `precio_medio` 62 | PASS |
| Nivel2 54 Nivel3 194 | dim exacto; README/docs alineados | PASS |

**P1-1 (indicadores stale):** `storage/load_mongo.py:98,317-348` `load_indicadores()` lee `dim_municipios_enriquecido.csv`, que **no fue regenerado** (`ls -l`: enriquecido 2026-11-05 22:32 vs dim/anuncios 2026-11-07 15:23; no tracked en git). Suma `indicadores.n_anuncios=759` (Bilbao 173) vs `anuncios=594` (Bilbao 204). El pipeline `run_analisis_mongo` agrega en vivo desde `anuncios` (por eso esfuerzo/CSV sí dan 204), pero la colección `indicadores` queda con el baseline pre re-resolución. Fix: `python transform/construir_dim_gold.py` (y cadena renta/tensión si aplica) + `python storage/load_mongo.py`, luego re-verificar suma 594 y L1 204/126/50/39 en `indicadores`. Ningún test actual detecta este drift (ver §3).

### Gate 4 — Manifests raw+silver
```
$ .venv/Scripts/python extract/generar_manifest.py --verify
OK: ...\docs\raw_manifest_sha256.txt (354 entradas, 0 errores)
OK: ...\data\procesado\manifest_sha256.txt (187 entradas, 0 errores)
EXIT:0
```
**PASS** (354 OK + 187 OK).

### Gate 5 — Sin Docker, HDFS solo raw, Kafka→HDFS, git sin push
```
$ git status --porcelain
 M README.md, docs/conclusiones_municipios.md, docs/guion_defensa.md, docs/guion_defensa_12min.md, docs/metodologia.md
 M extract/08_pisos_scraper.py, storage/load_mongo.py
 M tests/test_fase_datos.py, tests/test_mongo.py, tests/test_mongo_consistencia.py, tests/test_mongo_geo.py, tests/test_mongo_pymongo_pro.py, tests/test_raw_guardrails.py
 M transform/aplicar_cobertura_mercado.py, transform/muni_resolve.py, transform/unificar_anuncios.py
?? openspec/audit/plan_auditoria_v4_2026-11-07.md
?? openspec/changes/2026-11-07-pisos-re-resolver-ubicacion/
?? scratchpad/
?? tests/test_pisos_ubicacion_real.py
$ git status -sb
## master...origin/master   # sin ahead (sin push)
$ git diff --name-only | grep -i docker   # (vacío)
$ ls docker* Dockerfile*                  # No such file or directory
```
- Sin Docker (sin Dockerfile/compose en repo; `README.md:24,100` solo mención narrativa). Sin cambios de topología en el diff.
- HDFS solo raw: `storage/hdfs_utils.py:42` `DEFAULT_HDFS_RAW=.../data/raw`, `:127-128` «destino .../data/raw, separado de procesado. No toca data/procesado»; `upload_raw_excluding_legacy` itera `data/raw` (sin `procesado`); guardrails `tests/test_raw_guardrails.py:128-143` PASSED (ningún transform escribe `data/raw` fuera de lista blanca). Sin evidencia de procesados subidos.
- Kafka→HDFS, no Kafka→Mongo: `storage/kafka_raw_producer.py:1-7,46-68` publica `{type:raw_manifest, rel, size, sha256}` de `data/raw` a Kafka; `storage/kafka_hdfs_uploader.py:1-14,37,92-183` consume y hace `client.write(.../data/raw)` vía WebHDFS. `grep -n "Mongo|mongo" storage/kafka_hdfs_uploader.py storage/kafka_raw_producer.py` → vacío (sin Mongo). Nótese: `archive/kafka_2026-11-06/` contiene un flujo histórico Kafka→Mongo archivado; no está en `storage/` activo y no se modificó.
**PASS**.

## 3. Spec compliance matrix (9 requirements, 12 scenarios)

| Req (spec) | Scenarios | Evidencia / test runtime | Estado |
|---|---|---|---|
| EXTRACCION-01 (extraccion-datos/spec.md:9-23) | 2 (Santutxu→Bilbao, código sin texto) | `transform_pisos` + `resolver_codigo(None,'48020')==(None,None)`; `test_subtitulo_real_santutxu_bilbao`, `test_codigo_sin_texto_no_se_propaga` PASSED | COMPLIANT |
| PISOS-01 (spec.md:27-36) | 1 (orden + 245 passed) | Orden subtítulo→título→gazetteer→fallback→cuarentena en `muni_resolve.py:163-267`; `test_orden_subtitulo_antes_que_titulo`, `test_subtitulo_solo_barrio_via_gazetteer`, `test_titulo_como_evidencia…` PASSED. Nota: spec dice «245 passed», real 15 passed + universo unión 263 (ver P2-2) | COMPLIANT (conteo spec desactualizado) |
| PISOS-02 (spec.md:38-53) | 1 (Madrid→cuarentena) | `cuarentena_pisos.csv` 45 `fuera_de_euskadi`, `geo_invalida=True`; `test_fuera_euskadi_cuarentena`, `test_cuarentena_excluida_de_dim_y_conteos` PASSED; `grep geo_invalida` en unificados 0 (cuarentena fuera) | COMPLIANT |
| CARGA-SEGURA-01 (mongodb/spec.md:9-18) | 1 (backup 759) | `mongo.py:152-163` staging+backup+rename; Mongo `anuncios__backup=594` presente; `test_backup_presente_sin_perdidas` PASSED (acepta 594 actual, 759 antes). Spec aún dice «759 previos»; real backup 594 post-recarga (P2-3) | COMPLIANT |
| LIMPIEZA/TRANSFORM-01 (spec.md:20-29) | 1 (orden base→enricher) | `unificar_anuncios.py` → `aplicar_cobertura_mercado.py` ejecutados; `n_anuncios` en dim = reales (594). Agujero: `dim_enriquecido` no re-ejecutado → `indicadores` stale (P1-1) | PARTIAL (dim OK, gold OK no) |
| PISOS-03 (spec.md:33-48) | 1 (n=0 sin precio) | `mongo_esfuerzo`: n=0 → `precio_medio_eur` vacío; `test_municipio_n0_sin_precio_sin_imputacion` PASSED; sin IDW/comarcal para precio de anuncios (docs confirman). `metodo_imputacion` en esfuerzo es oficial/IDW solo para esfuerzo oficial (159/93), no para precio de anuncios | COMPLIANT |
| PISOS-04 (spec.md:50-58) | 1 (doble SHA) | Doble `run_analisis_mongo` SHA 6/6 idéntico + huella; `test_sha_doble_identico` PASSED; 252/252 y 249/252 intactos | COMPLIANT |
| CONCLUSION-01 (presentacion/spec.md:9-31) | 2 (sin ranking 1-16; L2 temporal≠larga) | `docs/conclusiones_municipios.md:29-31` sin ranking, L2 3 con min-max+mediana+`n_precio` separados; Getxo 50 vs Vitoria 39 diferencia 11 (ya no 1) — spec L11 aún 40/39 stale (P2-1). 13 PNG/6 CSV desde Mongo PASS | COMPLIANT |
| PISOS-05 (presentacion/spec.md:35-50) | 2 (252 contextual/159; edge 0-9) | `conclusiones:31` «252 contextual sobre 159», `grep contextual` ≥1; L3 «sin dato» fuera de mediana; `guion:47` 62/252 | COMPLIANT |

**Cobertura de tests:** 12/12 scenarios tienen al menos un test runtime PASSED que los cubre, salvo el agujero P1-1 (ningún test suma `indicadores.n_anuncios` contra `anuncios`). Ningún scenario está `UNTESTED` por ausencia total; P1-1 es `UNTESTED` parcial (fuente `indicadores`).

## 4. Correctness table (verificado por ejecución, no por lectura)

| Invariante | Fuente | Comando (literal) | Salida |
|---|---|---|---|
| 0 pisos por `municipio_busqueda` | silver | `grep -n municipio_busqueda transform/unificar_anuncios.py` | solo L64; cero en `transform_pisos` L127+ |
| 245 re-resueltos o cuarentena | test universo | `pytest tests/test_pisos_ubicacion_real.py -q` | `test_universo…` PASSED (unión 263, res≥200, cuar≥20). Silver unificados 87 pisos + cuarentena 45 = 132 (dedup/filtros posteriores; ver P2-2) |
| Fuera-Euskadi contada y reversible | cuarentena | `wc -l cuarentena_pisos.csv` + pandas `motivo` | 45 `fuera_de_euskadi`, `geo_invalida=True` |
| `n_anuncios` real, `n_raw` pre-limpieza | dim | pandas suma | 594 / 843 |
| Precio/superficie `None` si n=0, sin IDW/comarcal | esfuerzo | `test_municipio_n0…` | PASSED |
| 13 PNG + 6 CSV, doble SHA | resultados | `ls *.png\|wc`, `sha256sum` | 13 / 6 idénticos |
| 252/252 y 249/252 | Mongo + CSVs | pymongo counts, esfuerzo | anuncios 594, ind/mun/alq 252, paro 249 |
| `git status` sin push | git | `git status -sb` | `master...origin/master` sin ahead; diff solo change + `scratchpad/` + `test_pisos_…` |

## 5. Design coherence

Sin `design.md` en el change. Coherencia juzgada contra `proposal.md:35-39` (Approach 3 pasos) y `tasks.md` (orden base→enricher, staging+backup+rename, Kafka→HDFS): implemented conforme salvo P1-1 (paso gold intermedio no re-ejecutado). Decisiones de riesgo (gazetteer incompleto→cuarentena, n≥30 sin imputación) verificadas en código/tests.

## 6. Issues

### CRITICAL
- Ninguno que rompa el gate delegado (tests/manifests/SHA/conteos primarios en verde; ningún fallo pre-existente por stash: suite 166/1 sin fallos, no se requirió stash).

### WARNING / P1 (antes de archive)
- **P1-1 Indicadores stale:** `indicadores` suma 759 (Bilbao 173) vs real 594 (Bilbao 204). Causa: `dim_municipios_enriquecido.csv` (2026-11-05, no tracked) no regenerado tras T3; `load_indicadores` (`storage/load_mongo.py:317-348`) lo consume. Fix: regenerar gold (`construir_dim_gold` + cadena renta/tensión según `transform/run_all.py:191-200`) y recargar Mongo; añadir aserto `sum(indicadores.n_anuncios)==sum(anuncios)` para que no recurra.
- **P1-2 Checkboxes sin marcar:** `tasks.md` 27×`- [ ]`, 0×`- [x]`; `proposal.md:72-75` 4×`- [ ]`. La implementación está verificada (ver §1), pero `sdd-archive` puede exigir el tick + Success Criteria. Marcar solo tras resolver P1-1 (o documentar la excepción).

### SUGGESTION / P2
- **P2-1 Spec stale vs docs reales:** `presentacion/spec.md:11` aún Bilbao 173/Donostia 113/Getxo 40/Vitoria 39 y L2=16; real 204/126/50/39 y L2=3 (docs sí sincronizados). Sincronizar spec o anotar «valores reales post T3» en archive.
- **P2-2 Universo 245 vs 263/132:** proposal/spec hablan de 245; unión dirigido+enriquecido dedup = 263 (`test:134-135`); silver unificados solo 87 pisos (el resto se pierde en dedup/filtros/fingerprint 129 + cuarentena 45 → 132 trazables). Reconciliar número canónico en archive (245 pitch vs 263 unión vs 87 silver) para que la defensa no invoque 245 como silver.
- **P2-3 Backup 759 vs 594:** spec CARGA-SEGURA dice «759 previos»; backup real es 594 (post-recarga). Actualizar texto archive: 759 era pre-change, 594 es post re-resolución+cuarentena.
- **P2-4 Error menor docs:** `README.md:136` «356 (354 con hash)» vs manifest 354 verificado; aclarar 356 en disco vs 354 con hash en archive.

## 7. Comandos ejecutados (resumen para reproducción)

```
.venv/Scripts/python -m pytest tests -q
.venv/Scripts/python -m pytest tests --collect-only -q
.venv/Scripts/python -m pytest tests/test_pisos_ubicacion_real.py -q -rs
.venv/Scripts/python analysis/run_analisis_mongo.py && sha256sum data/resultados/mongo_*.csv   # x2
ls data/resultados/*.png | wc -l ; ls data/resultados/mongo_*.csv | wc -l
.venv/Scripts/python extract/generar_manifest.py --verify
git status --porcelain ; git status -sb ; git diff --name-only
grep -n "municipio_busqueda" transform/unificar_anuncios.py
# + lecturas pandas/pymongo §Gates 3 (dim, unificados, cuarentena, esfuerzo, Mongo vivienda_euskadi)
```

**Pre-existencia:** sin fallos de test no aplica stash. Suite verde en primer pase (166/1). La discrepancia P1-1 se probó por **diff** (`dim` 594 vs `enriquecido` 759 + fechas `ls -l` + `load_indicadores` lee enriquecido), no por stash clean-tree (árbol ocupacionalmente sucio por el propio change: 17 ficheros M + 4 untracked, según `verification-gate` no se hace stash en ese estado).
