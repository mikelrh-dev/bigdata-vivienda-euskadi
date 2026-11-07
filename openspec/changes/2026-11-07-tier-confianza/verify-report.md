# Verification Report: 2026-11-07-tier-confianza

- Change: `2026-11-07-tier-confianza` (Modo openspec)
- Artifacts read: `proposal.md`, `specs/mongodb-y-analisis/spec.md`, `specs/presentacion-de-resultados/spec.md`, `tasks.md` (10 tareas, 0 marcadas)
- Date of verification: 2026-11-07
- Role: dedicated `sdd-verify` sub-agent (skill `sdd-verify` 3.0; nota: `gentle-ai sdd-verify-validate` no disponible en esta máquina — comando desconocido — por lo que la validación formal del CLI no pudo ejecutarse; se verifica con evidencia runtime directa y se deja constancia)
- Working directory: `C:\Users\mikel\Documents\bigdata-vivienda-euskadi`

## Verdict

**GATE PASS WITH WARNINGS** (sustantivamente PASS — ningún FAIL; dos P1 formales/administrativos no bloquean el GATE funcional)

---

## Gate (1) — Tests

Command: `.venv/Scripts/python -m pytest tests -q`

| Evidence | Value |
|---|---|
| Collected | 175 |
| Passed | 174 |
| Skipped | 1 |
| Failed | 0 |

Literal output (tail):

```
........................................................................ [ 41%]
........................................................................ [ 82%]
........s......................                                          [100%]
174 passed, 1 skipped in 7.98s
EXIT:0
```

Breakdown tier + comparativa:

Command: `.venv/Scripts/python -m pytest tests/test_tier_confianza.py tests/test_mongo_comparativa.py -q -v`

```
tests\test_tier_confianza.py .......                                     [ 77%]
tests\test_mongo_comparativa.py ..                                       [100%]
============================== 9 passed in 0.56s ==============================
```

- `tests/test_tier_confianza.py`: 7 tests (`test_conteos_4_3_57_188_total_252`, `test_tier_a_son_bilbao_donostia_getxo_vitoria`, `test_tier_b_son_sopela_zarautz_santurtzi`, `test_tier_c_d_sin_precio_municipal`, `test_tier_b_temporal_no_igual_larga`, `test_sin_promocion_comarcal_ni_idw`, `test_doble_ejecucion_sha_identico`).
- `tests/test_mongo_comparativa.py`: 2 tests.
- Esperado por el encargo: `174 passed, 1 skipped` — coincide exactamente (166 base + 7 tier + 2 comparativa = 175 colectados).
- Fallo pre-existente: ninguno (0 fallos). La prueba vía diff solicitada para fallos pre-existentes no aplica: `pytest` verde con el árbol sucio de otros cambios (`2026-11-07-pisos-re-resolver-ubicacion`, `muni_resolve.py`, etc.).
- Raw guardrails: `pytest tests/test_raw_guardrails.py tests/test_raw_inmutable.py -q` → `9 passed in 3.98s`.

**Gate 1: PASS**

---

## Gate (2) — Doble ejecución `analysis/run_analisis_mongo.py` + SHA + artefactos

Command (dos veces, mismo comando):

```
.venv/Scripts/python analysis/run_analisis_mongo.py --salida data/resultados
```

Literal output (segunda ejecución):

```
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

- Huella primera ejecución: `0c3985a17a1238fe5f632246aaad92ed0a7b8d35efc3b6fbf1523333479e6eb7`
- Huella segunda ejecución: `0c3985a17a1238fe5f632246aaad92ed0a7b8d35efc3b6fbf1523333479e6eb7`
- Doble SHA idéntico: **SÍ** (coincide con el esperado)
- PNG: **13** (`A1_distribucion_esfuerzo_por_TH.png`, `A2_pct_inasequibles_por_TH.png`, `B_paro_vs_precio.png`, `C_vpo_antiguedad_por_TH.png`, `D_distancia_vs_precio.png`, `E_demografia_edad.png`, `F_comparativa_th.png`, `g1_esfuerzo_por_territorio.png`, `g2_renta_vs_alquiler.png`, `g3_top10_precio_medio.png`, `g4_distribucion_anuncios.png`, `g5_esfuerzo_robustos.png`, `G_gaps_limitaciones.png`)
- `mongo_*.csv`: **7 total** (`mongo_accesibilidad_extendida.csv`, `mongo_alquiler_por_municipio.csv`, `mongo_esfuerzo_por_municipio.csv`, `mongo_modalidades.csv`, `mongo_tier_confianza.csv`, `mongo_vpo_por_municipio.csv`, `mongo_vpo_terminadas_por_municipio.csv`)

| Expected | Observed | |
|---|---|---|
| 6 CSV canónicos incl. tier | tier ✓ (252 filas) | PASS |
| + vpo terminadas adicional | `mongo_vpo_terminadas_por_municipio.csv` (7º) | PASS (ver P2) |

- `mongo_tier_confianza.csv`: **252 filas** (Tier counts: `{'D': 188, 'C': 57, 'A': 4, 'B': 3}`)
- Dim: `data/procesado/dim_municipios.csv` lleva `tier,tier_etiqueta` (cabecera: `codigo_ine,nombre_canonico,territorio,nombre_normalizado,variantes,tiene_alquiler_oficial,tiene_fianzas_emal,tipologia_mercado,n_anuncios_raw,n_anuncios,tier,tier_etiqueta`)

**Gate 2: PASS**

---

## Gate (3) — Conteos Mongo

Mongo: `mongodb://localhost:27017/vivienda_euskadi`

| Colección / métrica | Expected | Observed (literal) | |
|---|---|---|---|
| `anuncios` | 594 | `anuncios 594` (también `coll anuncios 594`; backup `anuncios__backup 594`) | PASS |
| `municipios` | 252 | `municipios 252` | PASS |
| `indicadores` | 252 | `indicadores 252` (backup `indicadores__backup 252`) | PASS |
| `alquiler` (alquiler_municipal) | 252 | `coll alquiler_municipal 252` | PASS |
| `tasa_paro` (Lanbide) | 249 | `indicadores tasa_paro_lanbide nonnull 249` + `tasa_paro_valida true 249` + `tasa_paro nonnull 249` en `mongo_esfuerzo_por_municipio.csv` | PASS |
| Tier A | 4 (204/126/50/39) | 4 — `Bilbao 204, Donostia / San Sebastián 126, Getxo 50, Vitoria-Gasteiz 39` (CSV + test) | PASS |
| Tier B | 3 (19/15/11) | 3 — `Sopela 19, Zarautz 15, Santurtzi 11` | PASS |
| Tier C | 57 | 57 | PASS |
| Tier D | 188 | 188 | PASS |
| Nivel (tipologia_mercado) | 4/54/194 | `{'Nivel2_Mercado_Regulado': 54, 'Nivel3_Mercado_Rural_Cerrado': 194, 'Nivel1_Mercado_Dinamico': 4}` | PASS |
| precio | 62/252 | `precio_medio nonnull 62` (`mongo_esfuerzo_por_municipio.csv`, `pipeline_indicadores_municipio`) | PASS |
| sin precio en C | C: n_precio=0, min/max nulos | `Tier C n_precio max 0` + test `test_tier_c_d_sin_precio_municipal` | PASS |

Notes:
- Tier B detail literal (CSV): `Zarautz 15 (temporal 9 / larga 6)`, `Santurtzi 11 (5/4)`, `Sopela 19 (9/8)` — `n_precio_temporal != n_precio_larga` en los 3 ✓. Con `min_precio=900.0` y `max_precio` declarado + `mediana_precio`/`mediana_temporal`/`mediana_larga` (B siempre con min-max + mediana + `n_precio` ✓).
- `n_precio>0` en el CSV tier = 7 (los 7 son Tier A+B con precio municipal robusto; Tier C/D fuerzan `n_precio=0` por diseño para no afirmar precio con n=1-9/0) — **no contradice** 62/252: 62/252 es `precio_medio_eur` observable (`pipeline_indicadores_municipio`); 7 es el count con precio municipal robusto tras suprimir C y D. Ver P2.
- `tiene_alquiler_oficial 159` — coherente con "252 contextual sobre 159".
- Esfuerzo: `esfuerzo nonnull 252`.

**Gate 3: PASS**

---

## Gate (4) — Manifests raw (354) + silver (187)

Commands: verificación SHA256 literal contra `docs/raw_manifest_sha256.txt` y `data/procesado/manifest_sha256.txt` + `pytest tests/test_raw_guardrails.py tests/test_raw_inmutable.py -q`

```
wc -l docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt
354 docs/raw_manifest_sha256.txt
187 data/procesado/manifest_sha256.txt

raw OK 354 FAIL 0
silver OK 186 FAIL 1
MISMATCH SILVER dim_municipios.csv

.........  [100%]  9 passed in 3.98s   (raw guardrails + inmutable)
```

| Manifest | Expected | Observed | |
|---|---|---|---|
| raw `docs/raw_manifest_sha256.txt` (354) | 354 OK | `raw OK 354 FAIL 0` | PASS |
| silver `data/procesado/manifest_sha256.txt` (187) | 187 OK | `silver OK 186 FAIL 1` — solo `dim_municipios.csv` (evolución intencional del cambio: columnas `tier`/`tier_etiqueta`) | WARN (P1) |

`ingestion_manifest.json`: `{"n_ficheros": 354, ...}` — coherente con raw 354.

**Gate 4: PASS WITH WARNINGS** — raw íntegro; silver 1/187 desactualizado por la propia evolución del change (no pérdida de datos: el resto, 186/187, verifica byte a byte). Requiere regenerar `data/procesado/manifest_sha256.txt` tras consolidar apply (P1).

---

## Gate (5) — Sin Docker, HDFS solo raw (352), Kafka→HDFS, git sin push

| Check | Evidence literal | |
|---|---|---|
| Sin Docker | `ls: cannot access 'Dockerfile*'` + `cannot access 'docker-compose*'`; `grep docker/Dockerfile` sin resultados fuera de `.venv`/`.git` | PASS |
| HDFS solo raw (352) | `docs/arquitectura_datos.md:4`: "HDFS centro solo-raw hecho (`http://10.22.87.215:50070`, `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw`, 352 ficheros)" ; `docs/trazabilidad_vm.md:1537`: "2026-11-06 HDFS Windows->Kafka->VM->Hadoop raw 352 GATE PASS" ; `docs/guion_defensa.md:37`: "HDFS 352/352 con SHA igual + Kafka lag 0 tras recarga de 352" | PASS (evidencia documental; HDFS remoto no re-consultado en vivo en esta sesión — P2) |
| Kafka→HDFS, nunca Kafka→Mongo | `storage/kafka_hdfs_uploader.py:1`: "Consumer Windows: consume manifiesto Kafka y sube a HDFS (Windows -> Kafka -> HDFS)"; escribe vía `InsecureClient(...)/raw` (`client.write(f"{dest_base}/{rel}", ...)`); `grep MongoClient/insert_many/update_one` en `kafka_hdfs_uploader.py` y `kafka_raw_producer.py` → sin resultados; `docs/arquitectura_datos.md:4`: "Kafka no escribe en Mongo" | PASS |
| Git sin push | `git status -sb`: `## master...origin/master` (ahead 0, behind 0); `git log origin/master..HEAD` vacío; `git status --porcelain` muestra solo trabajo local sin commitear (incl. `?? tests/test_tier_confianza.py`, `?? openspec/changes/2026-11-07-tier-confianza/`); sin commits sin pushear | PASS |

**Gate 5: PASS**

---

## Spec Compliance Matrix

### mongodb-y-analisis — Delta

| Requirement / Scenario | Test / evidence | Status |
|---|---|---|
| AGREGACION-01 — pipeline `pipeline_tier_por_municipio` (`$group` por `codigo_ine`, `n_anuncios`, `n_precio`, `min_precio`, `max_precio`, `n_precio_temporal`, `n_precio_larga`, tier A≥30/B 10–29/C 1–9/D 0, 252 filas) | `run_analisis_mongo.py` (producción literal arriba) + 7 tests tier | **PASS** |
| Scenario: tier_por_municipio completo (252 filas, 4/3/57/188, doble ejecución SHA idéntico) | `mongo_tier_confianza.csv: 252 filas`; huella doble `0c3985…` ✓ | **PASS** |
| Scenario: Edge n_precio=0 en Tier C/D, sin imputación comarcal/IDW | `Tier C n_precio max 0`, `Tier D n_precio max 0`, `test_tier_c_d_sin_precio_municipal`, `test_sin_promocion_comarcal_ni_idw` | **PASS** |
| TIER-01 — raw inmutable, HDFS solo raw 352, Kafka→HDFS (nunca Mongo), staging+`<name>__backup` | `raw OK 354 FAIL 0`; `*_backup` observados (`anuncios__backup 594`, `indicadores__backup 252`, etc.); Kafka→HDFS ver Gate 5 | **PASS** |
| Scenario: Re-carga reversible sin drop (0 documentos perdidos) | Backups con conteos idénticos a activas; `raw OK 354` | **PASS** |

### presentacion-de-resultados — Delta

| Requirement / Scenario | Test / evidence | Status |
|---|---|---|
| CONCLUSION-01 — Tiers A/B/C/D solo de `n_anuncios`; A fuerte; B indicativo con min-max+mediana+`n_precio`, temporal≠larga; C sin precio municipal; D sin dato + contexto oficial; sin ranking 1-16 ni imputación | `test_conteos_4_3_57_188_total_252`, `test_tier_a_*`, `test_tier_b_*`, `test_tier_c_d_*`, `test_tier_b_temporal_no_igual_larga`, `test_sin_promocion_comarcal_ni_idw` | **PASS** |
| Scenario: Ranking firme solo Tier A (salida 13 PNG + 6 CSV canónicos + 1 adicional) | 13 PNG + 7 `mongo_*.csv` literales; Tier A 4 ✓ | **PASS** |
| Scenario: Tier B separa modalidades (min-max + mediana + `n_precio_temporal` y `n_precio_larga`) | Zarautz 9/6, Santurtzi 5/4, Sopela 9/8 ✓ | **PASS** |
| Scenario: Edge Tier C/D sin precio municipal | `n_precio=0`, min/max/mediana nulos + `tier_etiqueta` ("sin precio municipal" / "sin dato (+ contexto oficial)") | **PASS** |
| PISOS-05 — frase literal "252 contextual sobre 159"; nunca lectura oficial donde n<30 | `grep -c "252 contextual sobre 159" docs/conclusiones_municipios.md` → `1` (línea 32, con contexto completo: "Esfuerzo 252 contextual sobre 159 oficiales: los 252 municipios con esfuerzo son contexto, no estimacion oficial donde n<30") | **PASS** |
| Scenario: Frase literal en conclusiones (`grep -c` ≥ 1) | `1` ≥ 1 ✓ | **PASS** |
| Scenario: Edge 0-9 anuncios → "sin dato", sin mediana ni comparativa | C/D verificados; comparativa filtrada a Tier A (`analysis/comparativa_mongo.py`, `test_mongo_comparativa.py` 2 passed) | **PASS** |

**Spec compliance: 100% PASS (12/12 escenarios)**

---

## Issues

### P1 (deben resolverse antes de archivar / PR)

1. **Silver manifest desactualizado 1/187** — `data/procesado/manifest_sha256.txt` NO verifica `data/procesado/dim_municipios.csv` (`MISMATCH SILVER dim_municipios.csv`; `silver OK 186 FAIL 1`). Causa: la propia evolución del change (columnas `tier`/`tier_etiqueta` del enricher post-catálogo, tasks 2.1/2.2). Acción: regenerar `data/procesado/manifest_sha256.txt` (187/187) tras consolidar apply. Sin impacto en resultados (raw 354/354 intacto; 186/187 silver OK byte a byte).
2. **tasks.md 1.1–4.3 sin marcar (0/9)** — el flujo OpenSpec nativo exige tareas completadas para cerrar la verificación; en esta sesión no se tocaron tasks (orden: "no tocar código", solo aviso). Acción: marcar las 9 tras resolver el P1-1, o archivar el change con el estado real documentado.

### P2 (menores / polish)

3. **HDFS remoto no re-verificado en vivo** — Gate 5 se verificó con evidencia documental (`docs/arquitectura_datos.md`, `docs/trazabilidad_vm.md` 352 GATE PASS 2026-11-06, `docs/guion_defensa.md` "HDFS 352/352 con SHA igual + Kafka lag 0") y la ausencia de Docker. Si se exige prueba runtime fresca: `scripts/hdfs_verify.py` contra `http://10.22.87.215:50070`.
4. **Precio 62/252 vs `n_precio` del tier = 7** — dos métricas ≠: 62/252 es `precio_medio_eur` observable (`pipeline_indicadores_municipio`); 7 es el count con precio municipal robusto (Tier A+B) tras suprimir C/D por diseño (`n_precio=0`). Genuino, sin contradicción, pero debe quedar explícito en informe/guión para evitar lectura errónea ("solo 7 municipios con precio" sería falso).
5. **7º `mongo_*.csv` no contabilizado en la proposal** — la proposal define "6 CSV"; el 7º es `mongo_vpo_terminadas_por_municipio.csv` (pipeline `pipeline_vpo_terminadas` 251 filas, preexistente). Sin conflicto funcional; documentar como "6 canónicos + 1 adicional" en la proposal/specs.
6. **`gentle-ai sdd-verify-validate` no disponible** — comando desconocido en el CLI instalado (gentle-ai 4.0.0); la validación formal del artefacto no pudo ejecutarse. La verificación se sustenta en evidencia runtime literal (tests, Mongo, CSV, manifests, git).

---

## Task completion

| Phase | Tasks | Completed (verificado por evidencia) | tasks.md checkbox |
|---|---|---|---|
| 1 — Pipeline Mongo (AGREGACION-01) | 1.1, 1.2, 1.3 | 3/3 (funciones presentes en `analysis/mongo_aggregations.py`, `run_analisis_mongo.py`, `comparativa_mongo.py`; CSV tier 252; comparativa Tier A) | 0/3 marcados |
| 2 — dim_municipios (TIER-01) | 2.1, 2.2 | 2/2 (`tier_de_n` + `tier`/`tier_etiqueta` en `dim_municipios.py`; aplicación post-base con `max()` en `aplicar_cobertura_mercado.py`) | 0/2 marcados |
| 3 — Tests (CONCLUSION-01, PISOS-05) | 3.1, 3.2 | 2/2 (7 tests tier + 2 comparativa = 9 verdes ↑ Gate 1) | 0/2 marcados |
| 4 — Artefactos y docs (env gates) | 4.1, 4.2, 4.3 | 3/3 funcionales (13 PNG + 7 CSV + huella doble ✓; "252 contextual sobre 159" grep 1 ✓; manifests raw 354 ✓; silver 186/187 WARN P1) | 0/3 marcados |

**Completitud funcional: 10/10 evidenciada. Checkboxes en tasks.md: 0/10 (P1-2).**

---

## Design Coherence

Not a separate `design.md` exists for this change (proposal + 2 delta specs + tasks only). No design coherence dimension to verify. Recorded as skipped-by-absence.

## Coverage

No configured coverage threshold in the repo root was found for this session; coverage tooling was not invoked. Test evidence above (175 tests, 0 failures) is the runtime proof. Instructed by encargo: report collected/passed/skipped separately — done in Gate (1).
