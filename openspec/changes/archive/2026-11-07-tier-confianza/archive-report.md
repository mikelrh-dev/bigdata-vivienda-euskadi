# Archive report: 2026-11-07-tier-confianza

Archivado: 2026-11-07 (SDD-Archive, Modo openspec, rama `master`, sin commit/push).
Estado: CERRADO. Deltas sincronizados a `openspec/specs/` base sin perder requisitos (ver §5).

## 1. Resolución P1 (verify-report §Issues)

**P1-1 — Silver manifest desactualizado 1/187: RESUELTO**
- Causa: `data/procesado/dim_municipios.csv` evolucionó con columnas `tier`/`tier_etiqueta` (tasks 2.1/2.2), `data/procesado/manifest_sha256.txt` no verificaba (`MISMATCH SILVER dim_municipios.csv`, `silver OK 186 FAIL 1`).
- Fix: `python extract/generar_manifest.py --write` (regenera raw 354 + silver 187). No se tocó raw ni se imputó.
- Verificación post-fix (§2).

**P1-2 — tasks.md 0/10 sin marcar: RESUELTO**
- `tasks.md` 10 × `- [ ]` → 10 × `- [x]` (1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 4.3) solo con la evidencia del Gate 174 passed 1 skipped + doble SHA `0c3985…` (verify-report Gates 1–2 y re-ejecución §2). Sin evidencia no hay tick.

## 2. Gates finales (evidencia literal)

```
$ .venv/Scripts/python extract/generar_manifest.py --write
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\docs\raw_manifest_sha256.txt (354 entradas)
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\data\procesado\manifest_sha256.txt (187 entradas)
EXIT:0
$ .venv/Scripts/python extract/generar_manifest.py --verify
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\docs\raw_manifest_sha256.txt (354 entradas, 0 errores)
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\data\procesado\manifest_sha256.txt (187 entradas, 0 errores)
EXIT:0
wc -l docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt
354 docs/raw_manifest_sha256.txt
187 data/procesado/manifest_sha256.txt
dim_municipios.csv: 252 filas, Counter({'D': 188, 'C': 57, 'A': 4, 'B': 3})
Tier A: Bilbao 204, Donostia / San Sebastián 126, Getxo 50, Vitoria-Gasteiz 39
Tier B: Sopela 19, Zarautz 15, Santurtzi 11

$ .venv/Scripts/python -m pytest tests -q
........................................................................ [ 41%]
........................................................................ [ 82%]
........s......................                                          [100%]
174 passed, 1 skipped in 8.23s
EXIT:0

$ .venv/Scripts/python analysis/run_analisis_mongo.py --salida data/resultados   (×2, mismo comando)
mongo_esfuerzo_por_municipio.csv: 252 filas -> data\resultados\mongo_esfuerzo_por_municipio.csv
mongo_alquiler_por_municipio.csv: 252 filas -> data\resultados\mongo_alquiler_por_municipio.csv
mongo_modalidades.csv: 2 filas -> data\resultados\mongo_modalidades.csv
mongo_accesibilidad_extendida.csv: 252 filas -> data\resultados\mongo_accesibilidad_extendida.csv
mongo_vpo_por_municipio.csv: 322 filas -> data\resultados\mongo_vpo_por_municipio.csv
mongo_tier_confianza.csv: 252 filas -> data\resultados\mongo_tier_confianza.csv
mongo_vpo_terminadas_por_municipio.csv: 251 filas -> data\resultados\mongo_vpo_terminadas_por_municipio.csv
png_mongo: 13 ficheros -> data/resultados
pipelines: ['pipeline_indicadores_municipio', 'pipeline_alquiler_por_municipio', 'pipeline_modalidades', 'pipeline_top_municipios_por_esfuerzo', 'pipeline_esfuerzo_por_sexo', 'pipeline_accesibilidad_extendida', 'pipeline_udalmap_extendido_osrm', 'pipeline_vpo_por_municipio', 'pipeline_vpo_terminadas', 'pipeline_tier_por_municipio']
n={'pipeline_indicadores_municipio': 252, 'pipeline_alquiler_por_municipio': 252, 'pipeline_modalidades': 2, 'pipeline_top_municipios_por_esfuerzo': 10, 'pipeline_esfuerzo_por_sexo': 252, 'pipeline_accesibilidad_extendida': 252, 'pipeline_udalmap_extendido_osrm': 252, 'pipeline_vpo_por_municipio': 322, 'pipeline_vpo_terminadas': 251, 'pipeline_tier_por_municipio': 252}
huella: 0c3985a17a1238fe5f632246aaad92ed0a7b8d35efc3b6fbf1523333479e6eb7
reproducibilidad: ok (dos ejecuciones con la misma huella)
EXIT:0
```

Conteo gates: **174 passed / 1 skipped**, doble SHA idéntico **0c3985a17a1238fe5f632246aaad92ed0a7b8d35efc3b6fbf1523333479e6eb7**, **13 PNG / 7 mongo_*.csv (6 canónicos + 1 adicional)**, manifests **354 + 187 (0 errores)**, tier **4/3/57/188 = 252**.

## 3. Reconciliación P2 (archive)

- **P2-3 HDFS remoto no re-verificado en vivo:** Gate 5 verify con evidencia documental (`arquitectura_datos.md` HDFS solo-raw 352, `trazabilidad_vm.md` 2026-11-06 GATE PASS, `guion_defensa.md` "HDFS 352/352 con SHA igual + Kafka lag 0") + ausencia Docker. No se re-consultó `http://10.22.87.215:50070` en esta sesión. Sigue documentado como documental, sin afirmación runtime fresca.
- **P2-4 Precio 62/252 vs `n_precio` tier = 7:** métricas distintas — 62/252 es `precio_medio_eur` observable (`pipeline_indicadores_municipio`); 7 es el count con precio municipal robusto (Tier A+B) tras suprimir C/D por diseño (`n_precio=0`, sin precio municipal con n=1-9/0). Genuino, sin contradicción. Debe leerse 62/252 como universo con precio, 7 como robusto (A+B).
- **P2-5 7º `mongo_*.csv` no contabilizado en proposal:** proposal define "6 CSV canónicos incl. tier"; el 7º es `mongo_vpo_terminadas_por_municipio.csv` (251 filas, preexistente). Documentado como **6 canónicos + 1 adicional** en Spec Compliance (§2, verify-report) y specs base (§5).
- **P2-6 `gentle-ai sdd-verify-validate` no disponible:** comando desconocido en CLI instalado (gentle-ai 4.0.0); validación formal no ejecutable. Verificación sustentada en evidencia runtime literal (tests, Mongo, CSV, manifests, git).
- **Tasks 4.3 166 → 174:** `tasks.md:47` citaba `pytest` → 166 passed + 1 skipped (base pre-tier). Observado 174 passed + 1 skipped = 166 base + 7 `test_tier_confianza.py` + 2 `test_mongo_comparativa.py` (175 colectados). El tick 4.3 cubre la variante real; sin cambio de código.

## 4. Tareas y Success Criteria

`tasks.md` 10 × `- [ ]` → 10 × `- [x]`, solo con evidencia §2 (174 passed 1 skipped, doble SHA `0c3985…`, 13 PNG / 6+1 CSV, manifests 354+187, tier 4/3/57/188). Sin pendientes. Nota honesta: el texto de 4.3 esperaba 166; el real es 174 por los 9 tests tier/comparativa añadidos — queda reconciliado en §3.

## 5. Sincronización delta → specs base (sin perder requisitos)

- `openspec/specs/presentacion-de-resultados/spec.md`: bloque `CONCLUSION-01 — Niveles L1/L2/L3` sustituido por `CONCLUSION-01 — Tiers A/B/C/D, sin ranking 1-16` (A/B/C/D 4/3/57/188, Bilbao 204/Donostia 126/Getxo 50/Vitoria-Gasteiz 39, Sopela 19/Zarautz 15/Santurtzi 11, B con min-max+mediana+`n_precio` temporal≠larga, sin imputación comarcal/IDW) con escenarios *Ranking firme solo Tier A*, *Tier B separa modalidades*, *Edge Tier C/D sin precio municipal*; `PISOS-05` actualizado a frase literal «252 contextual sobre 159» (`grep -c "252 contextual sobre 159"` ≥1) y escenario *Frase literal en conclusiones* + *Edge 0-9*. `DATOS-HETEROGENEOS-01`, `AUTOMATIZACION-ANALISIS-01`, `INDICADORES-01`, `PREPARACION-VISUALIZACION-01`, guion `CONCLUSION-01` original y `RESPUESTA-01` (4 robustos 204/126/50/39) intactos.
- `openspec/specs/mongodb-y-analisis/spec.md`: `AGREGACION-01` actualizado a 6 CSV canónicos incl. `pipeline_tier_por_municipio` (252, `$group` por `codigo_ine`, `n_anuncios`/`n_precio`/`min_precio`/`max_precio`/`n_precio_temporal`/`n_precio_larga`, tier A≥30/B 10-29/C 1-9/D 0, `n` de Mongo nunca HDFS) con escenarios *Cinco CSV canónicos* (conservado), *tier_por_municipio completo*, *Edge n_precio=0 en Tier C/D*; añadido `TIER-01 — Raw inmutable, HDFS solo raw, Kafka→HDFS` (352 ficheros, sin Docker, staging+`<name>__backup`+rename, escenario *Re-carga reversible sin drop*). `MODELO-01`…`PISOS-04` y mapa Tema 1–8 intactos (759 histórico conservado como baseline).

## 6. Diff stat (tracked) y artefactos no tracked

```
25 files changed, 901 insertions(+), 148 deletions(-)
tier-relevantes: analysis/mongo_aggregations.py (+98), analysis/run_analisis_mongo.py (+40),
analysis/comparativa_mongo.py (+69), transform/dim_municipios.py (+40),
transform/aplicar_cobertura_mercado.py (+27), tests/test_mongo_comparativa.py (+26),
openspec/specs/presentacion-de-resultados/spec.md (+66),
openspec/specs/mongodb-y-analisis/spec.md (+81), docs/conclusiones_municipios.md,
docs/guion_defensa.md, docs/guion_defensa_12min.md, docs/metodologia.md, README.md
+ untracked: openspec/changes/2026-11-07-tier-confianza/ (proposal+2 deltas+tasks+verify-report),
  este archive-report.md, tests/test_tier_confianza.py
nota: el diff tracked mezcla 2026-11-07-pisos-re-resolver-ubicacion (muni_resolve, unificar, load_mongo,
tests/test_pisos_ubicacion_real.py, specs/extraccion-datos) — ambos changes comparten rama master
sin commit; el tier-relevante queda identificado arriba.
```
Silver `data/procesado/*` está gitignored: `dim_municipios.csv` (tier 4/3/57/188) y `manifest_sha256.txt` (187) regenerados en disco verifican 187/187 pero no entran en el diff. Manifest raw `docs/raw_manifest_sha256.txt` (354) regenerado sin cambio de conteo.

## 7. Restricciones cumplidas

Sin Docker (sin Dockerfile/compose), HDFS solo raw (`data/raw`, 352 ficheros HDFS), Kafka→HDFS nunca Kafka→Mongo (topología intacta, sin `MongoClient` en uploader), sin commit ni push (`master...origin/master` sin ahead).
