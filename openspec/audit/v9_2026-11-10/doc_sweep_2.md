# Barrido documental 2 (W4.2) — 2026-11-10

**Unidad:** W4.2 (doc sweep 2), ronda 4 del plan v9.
**Entrada barrida:** `docs/informe_final.md`, `docs/preguntas_analisis_profesional.md`, `docs/guion_defensa_12min.md`, `docs/guion_defensa.md`.
**Cifras vigentes:** `openspec/audit/v9_2026-11-10/00_baseline_v9.md` (congelada).
**Naturaleza:** SOLO LECTURA. No se modificó código, datos, Mongo, HDFS ni Kafka; no hubo commit/push; no se instalaron dependencias. No se ejecutó `load_all`, `clean_all`, `run_analisis_mongo`, el productor Kafka ni ningún gate.

---

## 1. Criterios cubiertos

| Criterio | Contenido | Estado |
|---|---|---|
| **C12** | Cadena raw→silver→Mongo→pipelines; número de pipelines | Cubierto (H-04) |
| **C13** | Índices/explain (performance) | Cubierto (H-03) + hallazgo nuevo P1 |
| **C16** | CSV `mongo_*` / artefactos de resultados | Cubierto (H-04) |
| **C18** | Comparativa Bilbao/Donostia/Getxo/Vitoria | Cubierto (H-05) |

Hallazgos barbados: **H-03** (IXSCAN 1), **H-04** (10/9 pipelines, 4/5/6 CSV, 14+13), **H-05** (comparativa 173/113/40).

---

## 2. Ejecutado vs solo leído

**Ejecutado (comandos read-only, con salida real):**
- `ls -1 data/resultados/` + `wc -l data/resultados/*.csv` + `ls -1 data/resultados/mongo_*.csv`.
- `ls -1 data/resultados/*.png | wc -l` (28) y `ls -1 data/resultados/anexo/*.png | wc -l` (8).
- `cat data/resultados/comparativa_3_municipios_mongo.csv` (4 filas de datos + cabecera).
- pymongo read-only sobre `localhost:27017` / `vivienda_euskadi`: `list_collection_names`, `estimated_document_count`, `index_information`, `listIndexes`, `explain()` (sin `drop`/`create`).
- `grep -n` de cifras en los 4 ficheros; `grep` de `ensure_indexes`, `PIPELINE_ORDER`, `huella`.
- `read_file` de `analysis/mongo_indexes.py` y `storage/load_mongo.py` (parcial).

**Solo leído (sin ejecutar):** los 4 ficheros de entrada; `00_baseline_v9.md`; `plan_ejecucion_v9_rondas_2026-11-10.md`; `AGENT.md`; `docs/modelo_mongodb.md`; los `.py` (no se ejecutó ni `compileall`).

**No ejecutado (guardrails):** `pytest`, `run_analisis_mongo`, `load_all`, `clean_all`, gates, productor Kafka, commit/push, instalación.

---

## 3. Hallazgos

### 3.1 P0/P1 — hallazgo nuevo (detener y reportar, no arreglar)

| ID | Sev | Fichero:línea | Cita literal | Cifra/estado correcto | Impacto |
|---|---|---|---|---|---|
| **DS2-01** | **P1** | `docs/guion_defensa.md:10,33,51`; `docs/guion_defensa_12min.md:36,175` (afirman IXSCAN) | «pasa de COLLSCAN (594 examinados) a IXSCAN (1 examinado) con indice compuesto ESR» / «explain COLLSCAN 594→IXSCAN 1» | **Medido ahora:** los 4 índices de `anuncios` (`idx_anuncios_ine_modalidad_precio`, `idx_anuncios_geo`, `idx_anuncios_portal_id`, `idx_anuncios_equipamiento`) **no existen**; `explain()` de la consulta documentada devuelve `COLLSCAN` con `totalDocsExamined=594`, `totalKeysExamined=0`. | El criterio C13 (performance/índices, 15 % de Tema 8) **no se sostiene**: la defensa no puede mostrar IXSCAN. Contradice además la sección 3 del baseline («Índices `anuncios` … `index_information()`» y «índices presentes»). **No se tocó nada; corrección = reejecutar `ensure_indexes()` (fuera de este barrido).** |

**Evidencia del hallazgo P1 (comandos reales):**
- `db['anuncios'].index_information()` → `{'_id_': …}` (1 índice).
- `db.command('listIndexes','anuncios')['cursor']['firstBatch']` → `[{'key': {'_id': 1}, 'name': '_id_'}]`.
- `explain('executionStats')` sobre `{ubicacion.codigo_ine:'48020', modalidad:'larga_estancia', precio_eur:{$lte:1000}}` → `stage=COLLSCAN`, `nReturned=8`, `totalDocsExamined=594`, `totalKeysExamined=0`.
- Los 4 índices de negocio que sí existen son los de `municipios`, `alquiler_municipal`, `etxebide_promociones` y `certificados_energeticos` (20 índices totales en 16 vivas, no 24).
- `analysis/mongo_indexes.py:62 ensure_indexes()` crea los 8 (4 en `anuncios`); `storage/load_mongo.py:610` la llama tras la carga. Su ausencia indica que el último estado de `anuncios` no pasó por `ensure_indexes()` o que los índices fueron borrados.

### 3.2 P2 — H-03 (explain IXSCAN)

| ID | Sev | Fichero:línea | Cita literal | Cifra correcta |
|---|---|---|---|---|
| DS2-02 | P2 | `docs/guion_defensa.md:10` | «a IXSCAN (1 examinado) con indice compuesto ESR» | IXSCAN **68/68** (baseline; depende del filtro). La realidad medida es COLLSCAN 594 (DS2-01). |
| DS2-03 | P2 | `docs/guion_defensa.md:33` | «COLLSCAN 594 -> IXSCAN 1 en `test_indexes_explain` con ESR» | IXSCAN **68/68**. |
| DS2-04 | P2 | `docs/guion_defensa.md:51` | «explain COLLSCAN 594→IXSCAN 1» | IXSCAN **68/68**. |
| DS2-05 | P2 | `docs/guion_defensa_12min.md:36` | «Pruebas: explain 594→1, 177 tests» | IXSCAN **68/68**; tests **235 passed + 2 skipped**. |
| DS2-06 | P2 | `docs/guion_defensa_12min.md:175` | «de **COLLSCAN 594 examinados** a **IXSCAN 1**» | IXSCAN **68/68**. |

### 3.3 P2 — H-04 (pipelines / CSV / colecciones / tests)

| ID | Sev | Fichero:línea | Cita literal | Cifra correcta |
|---|---|---|---|---|
| DS2-07 | P2 | `docs/informe_final.md:26` | «Mongo 14 colecciones → 10 aggregation pipelines» | **30 colecciones** (16 vivas + 14 `__backup`) y **11 pipelines** (`PIPELINE_ORDER`). |
| DS2-08 | P2 | `docs/informe_final.md:27` | «5 CSV canónicos + comparativa + VPO + sensibilidad» | **8 CSV `mongo_*`** (`ls data/resultados/mongo_*.csv`). |
| DS2-09 | P2 | `docs/informe_final.md:142` | `# 177 passed + 1 skipped` | **235 passed + 2 skipped** (237 colectados). |
| DS2-10 | P2 | `docs/informe_final.md:144` | `# 14 colecciones` | **30** (16 vivas + 14 `__backup`). |
| DS2-11 | P2 | `docs/informe_final.md:145` | `# 10 pipelines + huella` | **11 pipelines**. |
| DS2-12 | P2 | `docs/preguntas_analisis_profesional.md:99` | «Mongo hoy hecho con 14 colecciones (+13 `__backup`) y 10 pipelines» | **30** (16 vivas + **14** `__backup`) y **11 pipelines**. |
| DS2-13 | P2 | `docs/preguntas_analisis_profesional.md:120` | «14 colecciones + 13 `__backup`, 10 pipelines» | **30** (16 + 14) y **11**. |
| DS2-14 | P2 | `docs/guion_defensa_12min.md:35` | «fuentes → raw → silver → Mongo → 10 pipelines» | **11 pipelines**. |
| DS2-15 | P2 | `docs/guion_defensa_12min.md:143` | «Mongo **14 colecciones** → **10 pipelines** → 6 CSV + 12 PNG únicos de 13 emitidos» | **30 colecciones**, **11 pipelines**, **8 CSV**, **28+8 PNG**. |
| DS2-16 | P2 | `docs/guion_defensa_12min.md:170` | «pytest \| **177 passed + 1 skipped**» | **235 passed + 2 skipped**. |
| DS2-17 | P2 | `docs/guion_defensa_12min.md:171` | «**10 pipelines**, 6 CSV, **12 PNG únicos de 13 emitidos**» | **11 pipelines**, **8 CSV**, **28+8 PNG**. |
| DS2-18 | P2 | `docs/guion_defensa_12min.md:222` | «¿Por qué 14 colecciones? … los 13 `__backup` no cuentan.» | **30** (16 vivas + **14** `__backup`). La frase es además internamente incoherente (14 totales no pueden tener 13 `__backup`). |
| DS2-19 | P2 | `docs/guion_defensa_12min.md:249` | «CSV y 12 PNG únicos de 13 emitidos en `data/resultados`» | **8 CSV** y **28+8 PNG** (28 en `data/resultados` + 8 en `anexo/`). |

### 3.4 P2 — H-05 (comparativa 173/113/40)

| ID | Sev | Fichero:línea | Cita literal | Cifra correcta |
|---|---|---|---|---|
| DS2-20 | P2 | `docs/preguntas_analisis_profesional.md:84` | «Bilbao 48020 n 173, Donostia 20069 n 113, Getxo 48044 n 40, Vitoria-Gasteiz 01059 n 39» | **Bilbao 204, Donostia 126, Getxo 50**, Vitoria-Gasteiz 39. |
| DS2-21 | P2 | `docs/preguntas_analisis_profesional.md:91` | «solo 4 (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39)» | **204 / 126 / 50 / 39**. |
| DS2-22 | P2 | `docs/preguntas_analisis_profesional.md:120` | «Bilbao 48020 n 173, Donostia 20069 n 113, Getxo 48044 n 40…» | **204 / 126 / 50 / 39**. |

### 3.5 P2/P3 — afirmaciones no numéricas

| ID | Sev | Fichero:línea | Cita literal | Corrección | Impacto |
|---|---|---|---|---|---|
| DS2-23 | P2 | `docs/guion_defensa.md:9` | «**Embedding**: cada anuncio se almacena embebido en `municipios` (`ubicacion.codigo_ine`, `demografia`, `empleo`, `demanda_social`) con `alquiler_municipal` por `$lookup`» | El modelo es **referencing por `codigo_ine`**: `anuncios` es colección separada; `municipios` embebe demografía/empleo/demanda social. Contradice `docs/modelo_mongodb.md:26-28,148-149,152` y `docs/guion_defensa_12min.md:144-146`. | Si se lee en defensa, tergiversa el modelo de datos (pregunta literal del docx §5). |
| DS2-24 | P2 | `docs/guion_defensa.md:44` | «24 índices en 16 vivas (16 `_id` + 8 de negocio)» | Medido: **20 índices** en 16 vivas (16 `_id` + **4** de negocio); faltan los 4 de `anuncios` (DS2-01). | Infla el número de índices; se sostiene sobre el mismo error que DS2-01. |
| DS2-25 | P3 | `docs/guion_defensa_12min.md:250` | «Huella `08665d03…c30a` copiada» | Es la huella **histórica de 9 pipelines** (`docs/matriz_indicadores.md:32` la etiqueta como histórica; el 10.º y 11.º no entran). Con 11 pipelines la huella vigente es distinta y no está registrada en el baseline. | El checklist de defensa copia una huella que ya no es la vigente. |
| DS2-26 | P3 | `docs/guion_defensa_12min.md:252` | «`git status` limpio.» | Baseline v9: **38 entradas** (19 staged, 15 modified, 46 untracked). | El checklist pide un estado que no es el de partida; no es un fallo del proyecto, pero no se cumple tal cual. |

---

## 4. Observaciones al baseline (no son hallazgos de los 4 docs)

- **O-1 (P3, baseline interno):** `00_baseline_v9.md:97` lista «CSV `mongo_*` filas | 253 / 253 / 253 / 253 / 3 / 253 / 323 / 252» (cinco 253). Medido con `wc -l`: `mongo_accesibilidad_extendida` 253, `mongo_alquiler_por_municipio` 253, `mongo_esfuerzo_por_municipio` 253, **`mongo_habitaciones_por_municipio` 10**, `mongo_modalidades` 3, `mongo_tier_confianza` 253, `mongo_vpo_por_municipio` 323, `mongo_vpo_terminadas_por_municipio` 252. El recuento de **8 ficheros** es correcto; la fila tiene un 253 donde corresponde un 10.
- **O-2 (P1, relatevo a DS2-01):** `00_baseline_v9.md:98` afirma que `anuncios` tiene 4 índices y la sección 4 dice «índices presentes». Medido: no los tiene. El baseline no cierra en este punto.
- **O-3:** `docs/informe_final.md:154` dice «comparativa_3_municipios_mongo.csv (4 filas)» — **correcto** (4 datos + cabecera, `wc -l` = 5). No es hallazgo.
- **O-4:** `docs/guion_defensa.md:9` «16 vivas (14 negocio + 2 habitaciones 201+201)» — **correcto** (medido: `anuncios_habitaciones_unificados` 201 y `anuncios_habitaciones_unificados_bigdata` 201).

---

## 5. Blockers

1. **DS2-01 (P1):** los 4 índices de `anuncios` no existen y el `explain` real es COLLSCAN 594. Bloquea la verificación del criterio C13 y contradice al baseline. **No se arregla en este barrido** (sería ejecutar `ensure_indexes()`).
2. **DS2-25 (P3):** la huella vigente de 11 pipelines no está registrada en el baseline; no se puede dar la cifra correcta sin ejecutar `run_analisis_mongo.py` (fuera de guardrails).

---

## 6. Conclusión

- Los 4 documentos contienen **26 hallazgos**: 1 P1 nuevo, 23 P2 y 2 P3, más 4 observaciones al baseline (O-1…O-4).
- **H-03 abierto** en 5 líneas (IXSCAN 1); **H-04 abierto** en 13 líneas (10 pipelines, 14/13 colecciones, 5/6 CSV, 177 tests, 12 PNG); **H-05 abierto** en 3 líneas (173/113/40).
- **Hallazgo nuevo P1:** los índices de `anuncios` no están en Mongo y el explain documentado es COLLSCAN 594, no IXSCAN. Es el hallazgo más grave del barrido y requiere decisión del coordinador (reejecutar `ensure_indexes()` o declarar la caída).
- No se modificó ningún documento de entrada; solo se escribió este informe.
