# Auditoría exhaustiva — bigdata-vivienda-euskadi (2026-11-06)

Fecha: 2026-11-06. Rama: cierre/suficiencia-auditoria (e76fbcd), pusheada a origin/master.
Método: 3 oleadas de 3 agentes read-only (máx 3 en paralelo) + 2 jueces independientes con sondas propias. No se modificó datos ni código durante la auditoría. Todo número abajo sale de ejecución; lo no verificado se declara como tal.
Skills: data-audit, planning-and-task-breakdown, code-review-and-quality.

## Veredicto global: MIXTO

Datos suficientes para tipología de mercado y análisis comarcal-capital, NO suficientes para ranking municipal de precios. Tests 136/136 pasados (ejecutados en oleada 1C). Manifests reconciliados. Deuda acotada en documentos vivos, artefactos HTML manuales y SHOULD de infra (HDFS procesados / Kafka vivo verificado / gate extremo a extremo re-ejecutable).

## 1. Baseline verificado

| Hecho | Medido | Fuente |
|---|---|---|
| Rama / estado | cierre/suficiencia-auditoria, limpio, 0/0 vs origin/master | git status / rev-list |
| Raw | 356 ficheros find, 354 con hash (356-2 .FROZEN/.gitkeep) | docs/raw_manifest_sha256.txt 354 líneas, diff vacío |
| Silver | 188 ficheros find, 185 con hash (188-3 .gitkeep/_meta/ingestion_manifest/manifest) | data/procesado/manifest_sha256.txt 185 líneas |
| Tests | 136 collected (106 def + parametrización), 136 passed / 0 failed / 0 skipped | pytest tests/ -q 9,09s (oleada 1C). Jueces: solo collect-only (passed = no verificable en modo lectura) |
| PNG resultados | 13, todos posteriores a silver (22:42 vs manifest 22:38) | ls data/resultados/*.png, README coincide |
| 5 CSV EXPORTS_5 | Existen en data/resultados, posteriores a silver | analysis/run_analisis_mongo.py EXPORTS_5 |
| VPO | vpo_municipal.csv 253 líneas = 252 + cabecera | wc -l |

Nota de conteo: el "353/184" vigente en docs vivos es pre-VPO. El +1/+1 es data/raw/udalmap_vpo_terminadas.csv y data/procesado/vpo_municipal.csv. README 356/354 y 188/185 es correcto con find; el conteo recursivo del Juez 2 (354/187) corresponde a otro método de conteo sin dotfiles — la reconciliación find menos exclusiones es el control que manda.

## 2. Cobertura y suficiencia municipal

| Dimensión | Medido | Conclusión |
|---|---|---|
| dim_municipios | 252 filas, 252 códigos únicos zfill 5, prefijos 48:113, 20:88, 01:51, sin 00001 | OK |
| Anuncios unificados | 759 filas, 83 municipios únicos, 0 códigos 4 dígitos | OK, temporal 268 / larga 491 separados |
| n>=30 (con dedup n_anuncios) | 4 municipios (Bilbao 173, Donostia 113, Getxo 40, Vitoria 39) = 1,6% | NO ranking municipal |
| n>=30 (n_anuncios_raw pre-dedup) | 6 (añade Abanto y Ayala 31/30) = 2,38% | La diferencia 4 vs 6 es raw vs filtrado, confirmada por Juez 1 |
| Sin anuncios | 169 (67,5%), 1-29: 79, =0: 169 post-dedup | Sesgo urbano extremo |
| Alquiler oficial Eustat | 159 municipios oficiales / 93 IDW_5_vecinos | 93 NO son municipales, nunca imputar como municipales |
| Esfuerzo 18-34 canónico | med oficial 26,61% (40/159 >30); global 25,37% (47/252); IDW-93 med 23,38% | 25,4% sin universo es ambiguo (ver P1 docs) |
| ECVI | 29 filas, solo 7 con código municipal, 1 trimestre 2026T2 | No municipal completo |
| Comparativa AF | 15 filas área funcional, no municipal | Solo uso comarcal-AF |

Veredicto suficiencia:
- Ranking municipal: NO SUFICIENTE (n>=30 <10%)
- Tipología mercado: SUFICIENTE con cautela (informar n por tipo)
- Comarcal-capital: SUFICIENTE (AF 15, distancias 252x252, 3 capitales)
- Contextual: SUFICIENTE con proxies rotos (ver abajo)

Tensiones 0-10: cobertura anuncios 9, sesgo urbano/rural 9, proxies esfuerzo/VPO/paro 7, robustez 7, años 6, granularidad 6.

Calidad:
- BOM utf-8-sig: CSV procesado 41/41 (100%); JSON 0/77 (0%) — el "BOM 100%" solo vale para CSV (matiz del Juez 2). Raw 109/126 con BOM.
- IQR por segmento: larga med 15,81 Q1 12,00 Q3 20,02 outliers 12; temporal med 18,92 Q1 15,00 Q3 24,08 outliers 9. Sin mezcla temporal/larga.
- VPO: n=252, 251 válidos, med 0,0, 211/251 cero (84%), máx 62,55 — poco discriminativo.
- Paro: tasa_paro_lanbide_pct 249 válidos (3 NaN, med 5,94%); tasa_paro_aprox_pct columna muerta (extract None + drop en corregir_empleo, 252 None).
- Distancias: 252x252 = 63504 pares, 252 únicos origen/destino, 0 NaN — completa.
- Eustat 252: poblacion_joven_15_29 252 NaN (columna muerta).

## 3. Código, infra y seguridad

- extract/: 41 .py (29 numerados 01-26 con duplicados 09_/10_ + 12 AUX). transform/: 44 .py (34 SCRIPTS + 10 EXCLUIDOS, 0 huérfanos). storage/: 7, analysis/: 7, scripts/: 9.
- main_ingest.py: docstring dice 01-13 pero glob ejecuta 01-26 + 7 AUX. leer_csv_seguro (utf-8-sig, zfill) solo usado en 3 sitios; resto lecturas manuales utf-8-sig.
- run_all.py: DAG topológico; 4 escritores in-place sucesivos sobre anuncios_unificados; 3 nodos con out_glob que pueden quedar SIN-DECLARAR.
- Tests por fichero: contrato 54, mongo 25, fase_datos 18, hdfs 6, vpo 6, raw_guardrails 5, raw_inmutable 4, crudos 3, kafka 3, resto 1-2 cada uno. Total 136.
- HDFS: solo sube raw (upload_raw_excluding_legacy), no procesados por diseño. No accesible desde sandbox (timeout).
- Kafka: productor/consumidor completos en código, bootstrap 192.168.201.162:9094, topic anuncios_inmobiliarios. Test kafka híbrido: productor mock, consumidor upsert vivo solo en vivienda_euskadi_test. Socket a 9094 bloqueado por sandbox, vivo no verificable aquí.
- Mongo: vivo localhost:27017, prod vivienda_euskadi 27 colecciones (14 canónicas + 13 __backup), anuncios 759, municipios 252. Test efímera (0 colecciones entre runs). 9 pipelines en analysis/mongo_aggregations.py, 5 CSV canónicos en EXPORTS_5.
- Gate scripts/gate_bloque2.py: PASS exige HDFS ok + 10/10 + total>=759 + lag 0. Produce 10 a Kafka + upserts (escrituras, no ejecutado aquí). Matiz Juez 1: docs/trazabilidad_vm.md registra GATE PASS histórico (VERIFICADOS 10/10, HUELLA_SHA e32c3d3d...faf25, TOTAL 759, LAG 0) — el gate SÍ se ejecutó en el pasado; no re-ejecutable/verificable en esta sesión solo-lectura sin HDFS/Kafka.
- MONGO_ALLOW_DESTRUCTIVE: solo docstring en clean_mongo.py:387 y assert en test_mongo_consistencia.py:104 (env != "1"). Sin gate en código; clean_mongo hace drop/delete_many sin leer env. Protección por convención/test, no por lock.
- Seguridad: .env existe (1580 B) no tracked (gitignore cubre, solo .env.example con placeholders). Sin credenciales hardcodeadas (0 matches de asignación api_key/password/secret/token). IPs internas 10.22.87.215 / 192.168.201.162 hardcodeadas como defaults.
- Git: clean, e76fbcd, master local behind 11 vs origin/master (stale, ignorar).

## 4. Artefactos y honestidad de evidencia

- 13 PNG + EXPORTS_5: posteriores a silver, README coincide (13).
- HTML stale/manuales: dashboard.html 30/10, mapa_esquema_silver.html 01/11 (generado pero stale), dashboard_completo.html 04/11. Ningún .py en transform/ escribe esos HTML; son manuales, no evidencia RA4.
- G_gaps_limitaciones.png: transform/generar_dashboard_completo.py:173 def g_G_gaps() — tabla literal tecleada (93, 169, 406 promociones...), no conteos Mongo. run_all.py:243 lo marca "legacy DuckDB". README:159 ya lo declara como no-auto.
- docs/presentacion/index.html: generado desde CSV data/resultados (build_presentacion.py), no manual. Es presentación, no artefacto data/resultados.
- comparativa_3_municipios_mongo.csv: 4 filas reales (Bilbao, Donostia, Getxo, Vitoria), nombre histórico "3" stale. mtime 19:43, anterior a silver.

## 5. Cascada numérica presentación vs CSV (oleada 2E)

Correctas (confirmadas con cálculo propio): 252/159/93, 169 sin anuncios / 83 con / 759, oficial 26,61% & tramos 54/65/40, IDW-252 25,37% & 47/252, tensión 76/103/73, paro 249, Etxebide 5040, 4 robustos con importes, bootstrap ICs, VPO 251/211/med 0,0, 136/354/185 en index.html y guion.

Stale/refutadas:
- 6 municipios n>=30 (solo archive; hoy n_anuncios=4, n_anuncios_raw=6)
- 25,4% titular sin universo en docs/datos_finales_conclusiones_2026-11-05.md:9,26 — canónico oficial 26,61%
- 43,5% legacy 16-29 en README:147, docs/matriz, docs/guion_defensa — real ~42,9% oficial (desvío 0,6pp)
- r=0,385 sin etiqueta en guion:87 — es correlación de conteos (0,39), no de tasa (0,11/0,04 vs cuantía)
- 2,4% / IQR / óptimo: no están en presentación (sin cifra que auditar)
- informe_final:26 dice 8 pipelines vs :138 y resto 9 — falta 1

## 6. Huecos por prioridad

P1:
- openspec/project.md (353/184/130/355/187, 2026-10-29) y AGENT.md:9 (353/184) stale vs medido 354/185/136/356/188. README sí está actualizado.
- openspec/specs/mongodb-y-analisis/spec.md:344 fija 130 tests.
- SHOULD contrato sin cerrar: HDFS procesados no, Kafka vivo gate no re-verificado, integración extremo a extremo no re-ejecutable aquí, tensión/paro en silver (aprox muerta).
- G_gaps con cifras tecleadas (P-05) — bloquea P-08 para ese artefacto.
- docs/datos_finales 25,4% ambiguo y README 43,5%/7,5 incoherente.

P2:
- D5: comparativa 4 filas con nombre "3" (renombrar rompe ~26 citas).
- D6: 15 changes sin merge de delta en specs/ (archivar perdería requisitos).
- MONGO_ALLOW_DESTRUCTIVE sin gate real.
- main_ingest docstring 01-13 desactualizado; leer_csv_seguro infrausado; IPs hardcodeadas.
- project.md estado por fase superado por el cierre.

P3:
- docs/trazabilidad_vm.md y docs/archive conservan 353/184/130 históricos sin cabecera — no leer como inventario vivo.
- Bootstrap n_larga Donostia 51 vs mongo 55, Vitoria 37 vs 38; Getxo ICinf degenerado.

## 7. Jueces independientes

Juez 1 (sondas: pytest collect-only, wc -l manifests, PNG mtimes, Python n>=30/169/759/159/93/medianas, lectura g_G_gaps/gate/mongo):
- Confirmado: 136 collected, 354/185, 13 PNG, EXPORTS_5, g_G_gaps literal, 169/759/83, 159/93, medianas 26,61/25,37 (18-34), HDFS solo raw, Kafka mock, Mongo 759 vivo, HDFS/Kafka no alcanzables.
- Refutado (2): "6 en dim" es n_anuncios_raw (en n_anuncios son 4) — divergencia raw vs filtrado, no dim vs mongo; "gate no ejecutado" es falso — trazabilidad registra GATE PASS histórico. Corrección incorporada arriba.
- 136 passed: no verificable en solo collect-only (no ejecutada por él).

Juez 2 (sondas: grep docs, wc comparativa, Python dim/distancias/BOM/VPO/paro, lectura clean_mongo/test_consistencia):
- Confirmado: project.md/AGENT.md stale, comparativa 4 filas, 169 vs 93 complementarios, 25,4 mezcla universos (oficial 26,61), r=0,385 conteo no tasa, dim 252 sin 00001, distancias 63504, IQR por segmento, VPO 211/251 med 0,0, paro 249 vs aprox None, mongo 36 tests, HDFS offline, Kafka híbrido, MONGO_ALLOW_DESTRUCTIVE sin gate.
- Refutado (2 con matiz): "README 356/188 veraz" — texto confirmado pero conteo recursivo suyo da 354/187 (método: sin dotfiles; el control find menos exclusiones de arriba manda); "BOM 100% universal" — solo CSV 41/41, JSON 0/77.

Ambos jueces confirman el núcleo (136/354/185, 169/93, 26,61%, 4 robustos, G literal, SHOULD sin cerrar). Las dos refutaciones del Juez 1 quedan incorporadas; las dos del Juez 2 quedan como matiz de conteo y de alcance (CSV).

## 8. Próximos pasos (no ejecutados)

1. Fixes doc-only: project.md y AGENT.md a 354/185/136/356/188; mongodb-y-analisis/spec.md 130->136; datos_finales 25,4% con universo explícito; README 43,5%/7,5 y r=0,385 con etiqueta conteo; informe_final 8->9 pipelines; README comparativa (3,)->(4,).
2. G_gaps: regenerar desde conteos Mongo o retirar como evidencia (P-05).
3. Infra viva: re-ejecutar gate_bloque2.py con HDFS/Kafka alcanzables para PASS fresco; decidir HDFS procesados; añadir gate real MONGO_ALLOW_DESTRUCTIVE=1 en clean_mongo.
4. No tocar raw ni regenerar silver sin orden explícita. Commit local-only con mensaje sin identidad de agente; push solo con tu orden.
