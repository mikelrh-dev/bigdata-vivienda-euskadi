# Auditoría v12 vs rúbrica — 2026-11-15

**Alcance:** rúbrica v2 (`brief/RETO 1Evaluacion SBD-BDAv2.pdf`, 19 criterios) + Tema 8
(`brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` §16, 7 criterios) + prohibiciones P-01…P-08
+ invariantes del contrato, contrastados contra el repositorio en su estado actual.

**Naturaleza:** solo análisis. No se modificó código, datos, `data/raw`, `data/procesado`, Mongo,
HDFS ni Kafka. Las únicas escrituras son este informe y ficheros temporales en el scratch de
Hermes (el gold se regeneró dos veces en `C:/tmp/gold1` y `C:/tmp/gold2`).

**Entorno:** Windows 11, `.venv` Python 3.12.10, Mongo local operativo. HDFS centro
(`10.22.87.215:50070`) y Kafka centro (`10.22.87.215:9092`) **no alcanzables hoy**: TCP timeout
a ambas IP y DNS de `hadoop-master1/worker1/worker2.tartangalh.eus` no resuelve. Se trata como
excepción de entorno y se contrasta con la evidencia histórica fechada
(`openspec/audit/v8_2026-11-09/evidencia/vivo/`, `openspec/audit/v11_2026-11-12/evidencia/vivo_2026-11-12.json`).

**Base previa:** `openspec/audit/v11_2026-11-12/auditoria_completa_v11.md`. Este informe repite la
verificación con ejecución real y añade los deltas del 2026-11-13/14 (deck 24+8, gold 55, capa 2026).

---

## 1. Veredicto ejecutivo

| Bloque | Criterios | Nota 10 | Puntos |
|---|---|---:|---:|
| BDA RA1 (el PDF no declara peso) | 4 | 3 | **34/40 (85,0 %)** |
| SBD RA1 (46,7 %) | 4 | 4 | **40/40** |
| SBD RA3 (13,3 %) | 6 | 6 | **60/60** |
| SBD RA4 (40 %) | 5 | 5 | **50/50** |
| **Total rúbrica** | **19** | **17** | **184/190 (96,8 %)** |
| **SBD ponderado** | | | **100,0 %** |
| Tema 8 §16 (ponderado aparte) | 7 | 5 | **9,40/10** |

- **Dos criterios por debajo de 10:** C2 (HDFS) y C4 (integración). Ninguno por código: C2 por
  entorno (DNS/red) y C4 porque el gate vivo no verifica nada.
- **SBD impecable:** 150/150. Mongo responde, los 11 pipelines se ejecutan, el explain es real y
  el gold es reproducible byte a byte.
- **El PDF no pondera BDA RA1**, así que no existe porcentaje global único. Lo defendible es:
  «SBD ponderado 100 %; BDA 34/40; Tema 8 9,40/10».
- **0 P0.** 9 P1 (6 documentales/defensa y 3 de entorno/gate), 9 P2 y 3 P3.

---

## 2. Estado verificado hoy (ejecución real)

| Check | Comando | Resultado |
|---|---|---|
| Suite | `pytest tests` | **293 passed, 2 skipped** (rc 0) |
| Gobernanza | `scripts/verificar_gobernanza.py` | **TODO OK**: 53 cabeceras / 49 IDs, 47 scripts / 40 DAG, 183 silver, 0 env sin declarar, 11 pipelines |
| Gate offline | `scripts/gate_extremo_a_extremo.py --offline` | **OK** (355 SHA, 183 silver, 15 colecciones, 0 duplicados, lag 0); `PENDA-01` por centro no alcanzable |
| DAG | `transform/run_all.py --check` | **rc 1**: falta `data/resultados/auditoria_lagunas_silver.csv` |
| Pipeline | `scripts/run_pipeline.py --check` | **rc 0**: 355 raw + 183 silver, 0 errores |
| Fase de datos | `scripts/verificar_fase_datos.py` | **rc 1**: solo `FAIL 07` conocido (Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26) |
| Deck | `scripts/verificar_cifras_deck.py` | **115/115** comprobaciones |
| Vintage fig. | `scripts/verificar_vintage_figuras.py` | **56 figuras** declaradas |
| Gold | `analysis/run_analisis_mongo.py --salida …` (dos pasadas) | **rc 0**, huella `983fa53f…668b9e` idéntica; 8 CSV canónicos byte-idénticos a `data/resultados` |
| Explain | `analysis.mongo_indexes.explain_before_after()` | **COLLSCAN 594 docs / 0 claves → IXSCAN 1 doc / 1 clave** (`20069`) |
| HDFS | WebHDFS + TCP | **TCP timeout** a `10.22.87.215:50070`; DNS de `hadoop-*.tartangalh.eus` no resuelve |
| Kafka | TCP + admin/offsets | **TCP timeout** a `10.22.87.215:9092` |
| Mongo | PyMongo | **17 vivas + 15 `__backup` = 32**; anuncios 594; municipios 252; Tier 4/3/57/188; 25 índices (8 de trabajo) |

### Baseline de cifras (las que hay que defender)

| Magnitud | Valor verificado hoy |
|---|---:|
| Raw en disco / manifest | 357 ficheros / 355 SHA (351 canónicas + 4 legado) |
| Raw en HDFS | **353** objetos = 351 canónicas + `.FROZEN` + `.gitkeep` (histórico) |
| Silver | **183** entradas de manifest (187 ficheros, 65 en `_meta`, 42 CSV) |
| Anuncios | **594** = 326 larga + 268 temporal; 64 municipios con anuncio |
| Precio | **60/252** con `precio_medio_eur`; solo **7** con `n_precio>0` |
| Tier A/B/C/D | **4 / 3 / 57 / 188** |
| Nivel 1/2/3 | **4 / 54 / 194** |
| Colecciones | **17 vivas + 15 `__backup` = 32** |
| Tests | **293 passed, 2 skipped** |
| Gold | **55** (24 CSV + 31 PNG) + 8 PNG en `anexo/` |
| Huella gold | `983fa53fb5c61f37f526f4f27a9ffbc408a633c17c3a0cdf9d17771b00668b9e` |

---

## 3. Matriz de la rúbrica PDF (19 criterios)

| # | Criterio (nivel 10) | Nota | Evidencia verificada hoy |
|---|---|---:|---|
| C1 | Automatiza **API y scraping** | **10** | 41 scripts en `extract/`; `_common.Cliente` con timeout/retry; `main_ingest` orquesta; scrapers Fotocasa/Pisos |
| C2 | HDFS: originales **y procesados** y recuperación | **7** | 353 raw acreditados (histórico); `data/procesado` 404 por waiver; recuperación no demostrable hoy (DNS) |
| C3 | Productor y consumidor Python funcionan | **10** | `kafka_raw_producer.py` + `kafka_hdfs_uploader.py` (commit `offset+1`); evidencia v8 352/352 lag 0; tests offline |
| C4 | Flujo completo **hasta MongoDB** | **7** | Cadena por partes OK; `run_vivo()` vacío y `check_lag`/`check_duplicados` tautológicos; no hay gate E2E real |
| C5 | 2+ fuentes con **campo común** | **10** | 15 loaders, 17 colecciones; `$lookup` por `codigo_ine`/`_id`; 594/594 anuncios con `ubicacion.codigo_ine` |
| C6 | 2+ colecciones con relación/embedding/referencia | **10** | Embedding (`ubicacion`, `equipamiento`, `historico_precios`, `municipios.demografia/empleo/demanda_social`) + referencing por `codigo_ine` |
| C7 | Limpieza: nulos, duplicados, tipos +1 | **10** | `canonicalize_codigo_ine`, `mark_nulls`, `resolve_duplicates`, `convert_types`, `clean_obsolete_fields`, `clean_null_markers` |
| C8 | Automatización carga+limpieza+transformación | **10** | `run_mongo_pipeline.py` (load_all → clean_all → ensure_indexes → pipeline); `run_pipeline --fase mongo`; staging + `__backup` + rename |
| C9 | Modelado + decisión embedding/referencing justificada | **10** | `modelo_mongodb.md` §Embedding vs referencing, tipos BSON, 7 preguntas del docx |
| C10 | CRUD 4 ops + comprobación por código | **10** | `demo_crud_operations` + tests con asserts. Deuda: `tests/test_mongo.py:132` tautológico |
| C11 | 5+ consultas + anidada/array + 2 condiciones | **10** | 30 funciones: dot notation, `$elemMatch`, `$all`, `$size`, `$exists`, `$type`, `$regex`, `$and/$or`, sort/skip/limit |
| C12 | 3+ pipelines, 5 etapas, `$group` + lookup/unwind/facet | **10** | 11 pipelines; `$match` 24, `$group` 6, `$lookup` 23, `$unwind` 5, `$project` 15, `$sort` 22, `$limit` 15, `$addFields` 40 |
| C13 | explain antes/después + COLLSCAN/IXSCAN + docsExamined | **10** | **Ejecutado hoy**: COLLSCAN 594/0 → IXSCAN 1/1, filtro `20069` |
| C14 | Transacción real o atómica justificada | **10** | `find_one_and_update` + índice único; justificación READ en standalone; sonda en `vivienda_euskadi_test` |
| C15 | Datos heterogéneos adaptados con Python/PyMongo | **10** | 7 formatos (CSV, JSON, JSON anidado, XLSX, GeoJSON, ZIP/GTFS, SHP); normalización común |
| C16 | Script que ejecuta **todos** los análisis | **10** | `run_analisis_mongo.py`: 11 pipelines, huella `983fa53f…` en dos pasadas, 8 CSV canónicos byte-idénticos |
| C17 | 5+ indicadores con 2+ fuentes | **10** | Esfuerzo 18-34, tensión, VPO, esfuerzo por sexo, accesibilidad, habitaciones; 159 oficiales + 93 IDW. Matiz: `matriz_indicadores.md` solo lista 5 y 2 son de una fuente |
| C18 | 3+ municipios comparados con indicador Mongo | **10** | 4 Tier A: Bilbao 204, Donostia 126, Getxo 50, Vitoria 39; `comparativa_3_municipios_mongo.csv`. Deuda: `conclusiones_municipios.md` stale |
| C19 | 3+ conjuntos automáticos para representar | **10** | 8 CSV canónicos + 5 derivados + 26 PNG (análisis) + 5 PNG (transform) + 8 anexo, todo desde Mongo |

**BDA RA1 = 10 + 7 + 10 + 7 = 34/40.**
**SBD = 40 + 60 + 50 = 150/150.**
**Total bruto = 184/190 (96,8 %).**

---

## 4. Tema 8 §16 (evaluación separada)

| # | Criterio | Peso | Nota | Evidencia |
|---|---|---:|---:|---|
| T1 | Modelado documental | 15 % | **10** | 17 colecciones, embedding/referencing justificado, 7 preguntas |
| T2 | CRUD, limpieza y consultas | 15 % | **10** | 4+ ops CRUD, 6 limpiezas, 30 consultas, tests con asserts |
| T3 | Aggregation | 20 % | **10** | 11 pipelines, 8 etapas, huella reproducible |
| T4 | Índices y rendimiento | 15 % | **10** | ESR + 2dsphere + unique + multikey; explain 594→1 |
| T5 | Transacciones y consistencia | 10 % | **10** | Atómica documental + justificación standalone |
| T6 | PyMongo profesional | 15 % | **8** | `lru_cache` contradice el docstring; CI usa mongomock |
| T7 | Defensa técnica | 10 % | **7** | Figura P con P-05; «845» y «352+1» sin respaldo |

**Tema 8 ponderado = (15×10 + 15×10 + 20×10 + 15×10 + 10×10 + 15×8 + 10×7) / 100 = 9,40/10.**

---

## 5. Prohibiciones e invariantes

| ID | Estado | Evidencia |
|---|---|---|
| P-01 | Cumple | Eje = alquiler Eustat; ECVI solo contraste territorial |
| P-02 | Cumple | Salario OVJ × IPC (1718,65 €), renta INE/Eustat, población Eustat; `test_complementarios_salarios_no_simulados` |
| P-03 | Cumple | Alquiler de Eustat; no se usa alquiler INE para Euskadi |
| P-04 | Cumple | Agregación multi-etapa (`$match`/`$lookup`/`$addFields`/`$group`); 11 pipelines |
| P-05 | **NO cumple (matizado)** | La figura P teclea «ratio 1,96; Spearman 0,18» en `analysis/run_analisis_mongo.py:1479` y `transform/generar_figuras_N.py:445`, y el deck la repite (`index.html:853`, `guion.md:668`). No se reproduce de los CSV |
| P-06 | Cumple | 100 % Python en extract/transform/storage/analysis/scripts |
| P-07 | Cumple | `.env` y `api.txt` ignorados (`.gitignore:1` y `:61`); no versionados |
| P-08 | Cumple con matiz | 293 tests + gobernanza + gate + 115/115 del deck; el test de P-08 solo verifica transcripción |

| Invariante | Estado | Evidencia |
|---|---|---|
| Sin Docker | **No cumple** | `openspec/config.yaml:11` y `.env.example:26` dicen Docker |
| HDFS solo raw | Cumple | `kafka_hdfs_uploader.py` «Solo raw, NO silver»; `/data/procesado` 404 |
| Kafka→HDFS, nunca Kafka→Mongo | Cumple | El consumidor escribe en HDFS; `README.md:106` |
| Sin imputar comarcal/IDW como municipal | Cumple | `metodo_imputacion` + `is_imputed`; sensibilidad separada |
| Nivel y Tier ortogonales | **No consta** | La frase solo está en `openspec/specs`; guion y deck no mencionan Nivel |

---

## 6. Hallazgos

**P0 = 0 · P1 = 9 · P2 = 9 · P3 = 3.**

### P1 — afectan a la defensa

1. **P-05 violado en la figura P.** «ratio 1,96; Spearman 0,18» tecleado en dos generadores y en el
   deck; no reproducible de los CSV.
2. **«De 845 anuncios crudos a 287 válidos»** (`index.html:280`, `guion.md:212`) sin respaldo:
   `data/procesado/dedup_report.json` dice total 1828, únicos 639.
3. **«352 canónicos + 1 manifiesto»** (`index.html:806`, `guion.md:139`,
   `docs/presentacion_v2/README.md:24`) es falso: 353 raw = 351 canónicas + `.FROZEN` + `.gitkeep`;
   no hay manifiesto en HDFS.
4. **«352 canónicos + 3 legado»** (`guion.md:12`, `index.html:806`) es falso: 351 canónicas + 4 legado.
5. **`conclusiones_municipios.md` obsoleto** (doc de `RESPUESTA-01`): 1716,69 / 2465,32 / 1536,04 /
   1406,13 y 62/252; el gold vigente trae 1704,96 / 2247,82 / 1578,21 / 1408,08 y 60/252.
6. **`AGENT.md:4`** dice 16 vivas + 14 backup = 30 (real 17 + 15 = 32).
7. **`README.md:212`** gold 54 (real 55) y **`README.md:248`** 63/63 (real 115/115).
8. **`data/resultados/README.md:24/50`** gold 54/30 PNG (real 55/31).
9. **C2/C4 de entorno y gate:** recuperación HDFS no demostrable hoy (DNS); gate vivo no-op.

### P2 — incoherencias visibles

10. `openspec/config.yaml:11` y `.env.example:26` con Docker.
11. `n_precio`: 60 municipios con `precio_medio_eur` pero solo 7 con `n_precio>0` (gating Tier C/D).
12. Tres SHA de `matriz_indicadores.md` no coinciden (esfuerzo, alquiler, modalidades).
13. Guion: «53 artefactos» (55), SERPAVI 0,976/0,979 (deck 0,977/0,988), «52→50» sin verificar.
14. `README.md:300` y `docs/README.md:9` deck «22+9 / 22+8» (real 24+8); vintage 52/54 figuras (real 56).
15. Gate offline esperando 15 colecciones (hay 17); gobernanza con literales 47/40.
16. `storage/mongo.py:53` `lru_cache` contra docstring; `tests/test_mongo.py:132` assert tautológico.
17. Sin loader de `anuncios_habitaciones_unificados` (P3-06).
18. Nivel/Tier ortogonal no explicado en guion/deck.

### P3 — deuda

19. `anuncios_habitaciones_unificados` y `_bigdata` duplican 201/201.
20. `FAIL 07` de `verificar_fase_datos` (dato real, no enmascarado).
21. El CI corre mongomock, no Mongo real.

---

## 7. Riesgos de defensa

| Pregunta probable | Respuesta sólida | Estado |
|---|---|---|
| «¿Dónde están los procesados?» | Waiver firmada; originales y organización acreditados | Defendible |
| «Demuéstrame Kafka/HDFS en vivo» | Hoy no hay red; evidencia v8 (352/352, lag 0); el deck declara «No se afirma como revalidado hoy» | Defendible |
| «¿El ratio 1,96?» | **Punto más débil:** está tecleado y no se reproduce | Corregir antes |
| «¿845 crudos?» | No aparece en ningún artefacto; el embudo real es 1828/639 | Corregir antes |
| «¿353 objetos?» | Son 351 canónicas + `.FROZEN` + `.gitkeep` | Corregir antes |
| «¿Cuántas colecciones?» | 17 vivas + 15 backup = 32 | Corregir AGENT |
| «¿Los gráficos son automáticos?» | Sí, pero la figura P lleva una anotación manual | Corregir antes |

---

## 8. Correcciones aplicadas (2026-11-15)

Con la autorización del usuario se corrigieron las especificaciones y las cifras del deck.

**Specs**
- `contrato-reto`, `extraccion-datos`, `mongodb-y-analisis`, `presentacion-de-resultados`:
  «HDFS solo raw 352» → «353» (composición: 351 canónicas + `.FROZEN` + `.gitkeep`).
- `mongodb-y-analisis`: «precio observable 62/252» → «60/252».
- `openspec/project.md`: estado al día (355 SHA, 183 silver, 293 passed / 2 skipped).
- `almacenamiento-y-streaming`: el gate único es `scripts/gate_extremo_a_extremo.py`.
- `openspec/config.yaml` y `.env.example`: eliminada la mención a Docker.

**Deck y guion**
- Figura P: eliminado el literal «ratio 1,96; Spearman 0,18» en `analysis/run_analisis_mongo.py`,
  `transform/generar_figuras_N.py`, el deck y el guion; figura regenerada y sincronizada.
- «845 crudos» → «1.828 registros crudos → 639 únicos tras dedup → 594 vigentes».
- «352 canónicos + 1 manifiesto» → «351 canónicas + `.FROZEN` + `.gitkeep`».
- «352 canónicos + 3 legado» → «351 canónicos + 4 legado».
- «53 artefactos (24 CSV + 29 PNG)» → «55 (24 CSV + 31 PNG)».
- `scripts/verificar_cifras_deck.py`: check de 351 canónicos y nuevas prohibiciones; **120/120**.
- PDF reexportado: **32 páginas**, contiene los números nuevos y ninguno de los prohibidos.

**Verificación tras los cambios**
- Suite **293 passed, 2 skipped**; gobernanza **TODO OK**; gate offline **OK**;
  `run_pipeline --check` **OK**; DAG rc 1 (`auditoria_lagunas_silver.csv`, conocido);
  `verificar_fase_datos` rc 1 (solo `FAIL 07`, conocido); deck **120/120**; vintage **56 figuras**;
  huella gold `983fa53f…` sin cambios.

Quedan por aplicar (no incluidas en esta tanda): `README.md`, `AGENT.md`,
`data/resultados/README.md`, `docs/README.md`, `docs/presentacion_v2/README.md` y los tres SHA de
`matriz_indicadores.md`.

---

## 9. Anexo — comandos ejecutados

```bash
.venv/Scripts/python.exe -m pytest tests                          # 293 passed, 2 skipped
.venv/Scripts/python.exe scripts/verificar_gobernanza.py          # TODO OK
.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline   # OK + PENDA-01
.venv/Scripts/python.exe transform/run_all.py --check             # rc 1 (auditoria_lagunas_silver.csv)
.venv/Scripts/python.exe scripts/run_pipeline.py --check          # 355 raw / 183 silver, 0 errores
.venv/Scripts/python.exe scripts/verificar_fase_datos.py          # rc 1, solo FAIL 07
.venv/Scripts/python.exe scripts/verificar_cifras_deck.py         # 115/115
.venv/Scripts/python.exe scripts/verificar_vintage_figuras.py     # 56 figuras
.venv/Scripts/python.exe analysis/run_analisis_mongo.py --salida <tmp>  # huella 983fa53f… (x2)
.venv/Scripts/python.exe - <<'PY'  # explain_before_after()      # COLLSCAN 594/0 -> IXSCAN 1/1
# WebHDFS GETCONTENTSUMMARY/LISTSTATUS/GETFILESTATUS + TCP 50070/9092 (timeout)
# PyMongo: counts, index_information, distinct, aggregate
# sha256sum de los CSV canónicos; grep de literales y cifras en docs
```

**Ficheros leídos para el cotejo:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf`,
`brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, `openspec/specs/contrato-reto/spec.md` y las
cuatro specs detalladas, `README.md`, `AGENT.md`, `docs/README.md`, `data/resultados/README.md`,
`docs/presentacion_v2/{index.html,guion.md,README.md}`, `docs/memoria/memoria.md`,
`openspec/archive/2026-11-10-docs/{matriz_indicadores,conclusiones_municipios,modelo_mongodb}.md`,
`analysis/{mongo_aggregations,mongo_queries,mongo_indexes,run_analisis_mongo}.py`,
`storage/{load_mongo,clean_mongo,mongo,kafka_raw_producer,kafka_hdfs_uploader}.py`,
`scripts/{gate_extremo_a_extremo,verificar_gobernanza,verificar_cifras_deck,verificar_fase_datos}.py`,
`transform/{run_all,generar_figuras_N}.py`, `tests/*`, `.github/workflows/quality-gate.yml`,
`openspec/audit/v11_2026-11-12/*`.

**Guardarraíles respetados:** sin escrituras en `data/`, Mongo, HDFS ni Kafka; sin `load_all`/
`clean_all`; sin productor/consumidor reales; sin commits ni push. `git status` final: solo
`?? .hermes/`.
