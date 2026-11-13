# Auditoría completa v11 — rúbrica v2 (19) + Tema 8 (7)

**Fecha:** 2026-11-12 · **Modo:** solo lectura · **HEAD:** `b29c6ac` (con 6 ficheros modificados sin commit)
**Rúbrica:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (transcrita en `openspec/specs/contrato-reto/spec.md`) y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` §16.
**Entorno:** Windows 11, `.venv` Python 3.12.10, HDFS/Kafka centro `10.22.87.215` y Mongo local **alcanzables por IP/TCP**.
**Naturaleza:** no se modificó código, datos, `data/raw`, `data/procesado`, Mongo, HDFS ni Kafka. Se escribieron únicamente este informe, el CSV de hallazgos y un JSON de evidencia; el gold se regeneró en un directorio temporal.

---

## 1. Veredicto ejecutivo

| Bloque | Criterios | Cubiertos a 10 | Puntos |
|---|---|---:|---:|
| BDA RA1 (el PDF no declara peso) | 4 | 2 | **34/40 (85,0 %)** |
| SBD RA1 (46,7 %) | 4 | 4 | **40/40** |
| SBD RA3 (13,3 %) | 6 | 6 | **60/60** |
| SBD RA4 (40 %) | 5 | 5 | **50/50** |
| **Total bruto** | **19** | **17** | **184/190 (96,8 %)** |
| SBD ponderado | — | — | **100,0 %** |
| Tema 8 ponderado | 7 | 5 | **9,40/10 (94,0 %)** |

- **C2 baja a 7 y C4 se mantiene en 7.** C2 no por el waiver de procesados (declarado y legítimo), sino porque **hoy la recuperación de un fichero no se puede completar**: el redirect WebHDFS apunta a `hadoop-worker*.tartangalh.eus` y ese nombre **no resuelve** desde esta máquina. C4 sigue en 7 porque no existe un comando único que demuestre extracción → Mongo → análisis; el gate «vivo» solo hace TCP.
- **C3 se sostiene en 10 con evidencia histórica**, no con la de hoy: Kafka acepta TCP pero no entrega metadata (`NodeNotReadyError`), muy probablemente por el mismo DNS de los brokers anunciados. La evidencia v8 (`end=352`, `committed=352`, lag 0) y los tests offline siguen siendo válidos.
- **SBD está impecable**: 150/150. Mongo responde, los 11 pipelines se ejecutan, el explain es real y las cifras canónicas cuadran.
- **17 hallazgos**: 0 P0, 2 P1 (ambos de defensa HDFS/Kafka), 8 P2 y 7 P3.

---

## 2. Lo que se ejecutó (evidencia real de hoy)

| Check | Comando | Resultado |
|---|---|---|
| Suite | `pytest tests` | **285 passed, 2 skipped** (287 collected), rc 0 |
| Gobernanza | `scripts/verificar_gobernanza.py` | **TODO OK**: 53 cabeceras / 49 IDs, 47 scripts / 40 DAG, 183 silver, 0 env sin declarar, 11 pipelines |
| Gate offline | `scripts/gate_extremo_a_extremo.py --offline` | rc 0: 355 SHA, 183 silver, «15 colecciones», «lag 0», «0 duplicados» |
| DAG | `transform/run_all.py --check` | **rc 1**: falta `data/resultados/auditoria_lagunas_silver.csv` |
| Pipeline | `scripts/run_pipeline.py --check` | rc 0: 355 raw + 183 silver, 0 errores |
| Fase de datos | `scripts/verificar_fase_datos.py` | rc 1: **solo FAIL 07** conocido (Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26); huella `596e7e11…e443` |
| Gold on-demand | `analysis/run_analisis_mongo.py --salida /tmp/...` | rc 0: 11/11 pipelines, 13 CSV + 33 PNG, huella `d158780a…090a`, dos pasadas idénticas |
| Explain | `analysis.mongo_indexes.explain_before_after()` | **COLLSCAN 594 docs → IXSCAN 1 doc**, `totalKeysExamined` 0→1 |
| HDFS | WebHDFS `GETCONTENTSUMMARY` / `LISTSTATUS` / `GETFILESTATUS` | **353 ficheros**, 895.597.901 B, 202 hijos en raw; `data/procesado` → **404** |
| HDFS recuperación | `scripts/hdfs_recuperacion_un_fichero.py` | **rc 2** por DNS del datanode (ver §4) |
| Kafka | `KafkaAdminClient.list_topics` / offsets | **NodeNotReadyError**; TCP 9092 OK |
| Mongo | PyMongo (conteos, índices, agregados) | 17 vivas + 15 backup = 32; 594 anuncios; 252 municipios; 4/3/57/188 |

### Baseline de cifras (las que hay que defender)

| Magnitud | Valor verificado hoy | Documento que la cita |
|---|---:|---|
| Raw local | 357 ficheros | README ✅ |
| Manifest raw | 355 SHA | README ✅ |
| Raw en HDFS | **353** | README ✅ |
| Silver | **183** (manifest 183) | README ✅ |
| Anuncios | **594** = 326 larga + 268 temporal | README ✅ |
| Municipios con anuncio | **64** | README ✅ |
| Municipios con precio medio | **60** | README ✅ |
| Tier A/B/C/D | **4 / 3 / 57 / 188** | README ✅ |
| Alquiler oficial + IDW | **159 + 93 = 252** | README ✅ |
| Colecciones vivas | **17** (+15 backup = 32) | README dice **16 (+14 = 30)** ❌ |
| Tests | 285 passed / 2 skipped | README ✅ |

---

## 3. Matriz de la rúbrica PDF (19 criterios)

| # | Criterio (nivel 10) | Nota | Evidencia verificada hoy | Hueco |
|---|---|---:|---|---|
| C1 | Automatiza **API y scraping** | **10** | 41 scripts en `extract/`; 15 usan `_common.Cliente` (requests.Session con timeout/retry); scrapers Fotocasa/Pisos parsean el JSON/HTML embebido; `main_ingest` orquesta | Nada. El scraping no usa BeautifulSoup, pero no es requisito |
| C2 | HDFS: originales **y procesados** y **demuestra recuperación** | **7** | 353 raw + 202 hijos; organización correcta; `data/procesado` 404 por waiver; **recuperación no demostrable hoy** (DNS) | Resolver DNS del datanode y guardar la salida SHA |
| C3 | Productor y consumidor Python funcionan y procesan | **10** | Código correcto: `send(key=rel)` + `add_callback/add_errback`; commit manual con `offset+1` (confirmado contra la doc de kafka-python); evidencia v8 end=352/committed=352/lag 0; tests offline | Hoy no revalidable en vivo; la diapositiva que afirma lo contrario no tiene evidencia |
| C4 | Flujo completo **hasta MongoDB** | **7** | Cadena por partes funciona (extract → silver → load → clean → 11 pipelines → 13 CSV); gate offline OK pero no toca Mongo; gate vivo solo TCP | Un comando único E2E real o un gate vivo que verifique datos |
| C5 | 2+ fuentes con **campo común** | **10** | 17 colecciones; `$lookup` `anuncios.ubicacion.codigo_ine → municipios._id`; 594 anuncios / 252 municipios; anuncios 594/594 con `ubicacion.codigo_ine` | `municipios` no expone `codigo_ine` (0/252): la relación es por `_id`. Reserva de lectura |
| C6 | 2+ colecciones con relación/embedding/referencia | **10** | `anuncios.ubicacion{}` anidado, `equipamiento[]`, `historico_precios[]`; referencing por código en alquiler/indicadores/etxebide | Duplicado habitaciones 201/201 (P3) |
| C7 | Limpieza: nulos, duplicados, tipos +1 | **10** | `clean_mongo`: canonicalize, `mark_nulls`, `resolve_duplicates` (3 claves), `convert_types` ($convert), `clean_obsolete_fields`, `clean_null_markers` | Nada |
| C8 | Automatización carga+limpieza+transformación | **10** | `scripts/run_mongo_pipeline.py` (load_all → clean_all → ensure_indexes → pipeline); `run_pipeline.py --fase mongo`; staging + `__backup` + rename | Nada |
| C9 | Modelado + decisión embedding/referencing justificada | **10** | `modelo_mongodb.md` §Embedding vs referencing, tipos BSON, índices, shard key, transacciones, 7 preguntas del docx | Nada |
| C10 | CRUD 4 ops + comprobación por código | **10** | `demo_crud_operations`: insert_one/many, find, update_one, `$inc/$push/$addToSet`, upsert, `$unset/$rename/$pull`, bulk_write, delete_one/many; tests con contadores | Assert tautológico en `test_mongo.py:132` (P3) |
| C11 | 5+ consultas + anidados/arrays + 2 condiciones | **10** | `analysis/mongo_queries.py`: 30 funciones con dot notation, `$elemMatch`, `$all`, `$size`, `$and/$or`, proyección, sort, skip/limit, `$regex`, `$type`, `$exists` | Nada |
| C12 | 3+ pipelines, 5 etapas, `$group` + lookup/unwind/facet | **10** | 11 pipelines; `$match` 20, `$group` 6, `$lookup` 22, `$unwind` 5, `$addFields` 38, `$project` 14, `$sort` 20, `$limit` 15 | `$facet` no se usa (la rúbrica admite lookup/unwind) |
| C13 | explain antes/después + COLLSCAN/IXSCAN + docsExamined | **10** | **Ejecutado hoy**: before COLLSCAN 594/0 claves; after IXSCAN 1/1 clave; índice ESR `{ubicacion.codigo_ine, modalidad, precio_eur}`; 5 índices en `anuncios` | Nada |
| C14 | Transacción o atómica justificada | **10** | `marcar_calidad_municipio` con `find_one_and_update` + `ReturnDocument.AFTER`; justificación standalone en `modelo_mongodb.md`; test de consistencia | Nada |
| C15 | Datos heterogéneos adaptados con Python/PyMongo | **10** | 7 formatos: CSV 130, HTML 101, JSON 61, ZIP 49, XLSX 6, GeoJSON 2, SHP; normalización común, `_geo_point`, `ubicacion` | Nada |
| C16 | Script que ejecuta **todos** los análisis | **10** | `run_analisis_mongo.py`: 11/11 pipelines, huella estable, 8 CSV canónicos + 5 extras + 33 PNG | Nada |
| C17 | 5+ indicadores con 2+ fuentes | **10** | Esfuerzo 18-34, esfuerzo por sexo, tensión social, paro Lanbide, precio/m² winsorizado, VPO terminadas, accesibilidad, habitaciones; 159 oficiales + 93 IDW | Nada |
| C18 | 3+ municipios comparados con indicador Mongo | **10** | 4 Tier A: Bilbao 204, Donostia 126, Getxo 50, Vitoria 39; `comparativa_3_municipios_mongo.csv` con esfuerzo/paro/precio | Getxo vs Vitoria es margen de 11 anuncios (ya advertido) |
| C19 | 3+ conjuntos automáticos para representar | **10** | **8 CSV `mongo_*`** + 33 PNG generados desde Mongo en directorio temporal; 5 CSV extra de análisis; deck desde CSV | 4 PNG del directorio real vienen de la capa 2026, no de `run_analisis_mongo` (P3) |

**BDA RA1 = 10 + 7 + 10 + 7 = 34/40.**  
**SBD = 40 + 60 + 50 = 150/150.**  
**Total bruto = 184/190 (96,8 %).** El PDF no pondera BDA RA1, así que no existe un porcentaje global único.

---

## 4. HDFS y Kafka en vivo (lo que el centro permite hoy)

### HDFS — sí, con un matasellos

| Comprobación | Resultado |
|---|---|
| `GETCONTENTSUMMARY /data/raw` | 200 · **353 ficheros** · 6 directorios · 895.597.901 B |
| `LISTSTATUS /data` | 200 · solo `raw` (procesado no existe, como se declara) |
| `GETFILESTATUS /data/procesado` | **404 FileNotFoundException** (waiver de la profesora) |
| `GETFILESTATUS /data/raw` | 200 · `childrenNum = 202` |
| `OPEN` de un fichero | **falla**: redirige a `hadoop-worker1/2.tartangalh.eus:50075`, nombre que **no resuelve** |
| `scripts/hdfs_recuperacion_un_fichero.py` | **rc 2** en el fichero por defecto y en `udalmap_vpo_terminadas.csv` |

La organización de originales está acreditada y el conteo es correcto (353). Lo que no está acreditado hoy es **la recuperación**. El script está bien escrito (valida ruta, compara tamaño y SHA, solo lectura, 6 tests offline), pero en esta máquina el `OPEN` de WebHDFS no puede seguir el redirect. El mensaje del script («revisa HDFS_URL/HDFS_USER y la red del centro») despista: la red y la IP funcionan; falla el DNS del datanode.

**Consecuencia:** C2 = 7 hoy. Con el DNS resuelto (o descargando contra la IP del worker) el mismo script devuelve 0 y C2 pasa a 10. **No es un problema de código, es de entorno**, y así debe declararse.

### Kafka — TCP sí, metadata no

- `socket.connect(10.22.87.215:9092)` → OK.
- `KafkaAdminClient.list_topics()` → **`NodeNotReadyError`** en 3 intentos.
- `KafkaConsumer(...).end_offsets()` → `KafkaTimeoutError`.
- Causa más probable: los brokers anunciados usan `hadoop-*.tartangalh.eus`, que no resuelve (los tres nombres fallan con `[Errno 11001]`).

No se produjo ni consumió nada. La evidencia válida sigue siendo `openspec/audit/v8_2026-11-09/evidencia/vivo/kafka_retry2.json`: topic `vivienda_euskadi`, 1 partición, `end=352`, `committed=352`, **lag 0**. El código del productor/consumidor es correcto y el patrón de commit (`offset+1`) coincide con la documentación oficial de kafka-python.

---

## 5. Tema 8 (evaluación separada)

| # | Criterio | Peso | Nota | Evidencia | Hueco |
|---|---|---:|---:|---|---|
| T1 | Modelado documental | 15 % | **10** | 17 colecciones, embedding/referencing justificado, tipos BSON, 7 preguntas | Mantener cifras |
| T2 | CRUD, limpieza y consultas | 15 % | **10** | 4+ ops CRUD, 6 limpiezas, 30 consultas, tests con asserts | Assert tautológico (P3) |
| T3 | Aggregation | 20 % | **10** | 11 pipelines, 8 etapas, huella reproducible | Nada |
| T4 | Índices y rendimiento | 15 % | **10** | ESR + 2dsphere + unique + multikey; explain 594→1 | Nada |
| T5 | Transacciones y consistencia | 10 % | **10** | Atómica documental + justificación standalone | Nada |
| T6 | PyMongo profesional | 15 % | **8** | Cliente único, `MONGO_URI`, `Decimal128`, cursores, staging→rename, errores tipados | `lru_cache` contradice el docstring; CI usa mongomock |
| T7 | Defensa técnica | 10 % | **7** | Deck 21+9, guion, PDF, mapa de rúbrica | El deck afirma verificaciones de hoy que no se reproducen; 6 ficheros sin commit |

**Tema 8 ponderado = (15×10 + 15×10 + 20×10 + 15×10 + 10×10 + 15×8 + 10×7) / 100 = 9,40/10.**

---

## 6. Hallazgos (detalle en `hallazgos_v11.csv`)

**0 P0 · 2 P1 · 8 P2 · 7 P3.**

### P1 — afectan a la defensa

1. **V11-01 · Recuperación HDFS no reproducible.** El redirect WebHDFS a `hadoop-worker*.tartangalh.eus` no resuelve. El script devuelve rc 2. C2 queda en 7 hasta que se arregle el DNS.
2. **V11-02 · El deck afirma evidencia que no existe.** `docs/presentacion_v2/index.html` dice «Verificado en vivo (2026-11-12): 353 ficheros… 353 committed, lag 0» y «corrida real OK 2026-11-12». No hay JSON fechado hoy y Kafka no responde. Es el hallazgo más peligroso: se puede convertir en un P-08 delante del tribunal.

### P2 — incoherencias que un evaluador puede ver

3. **V11-03 · El gate vivo es un no-op.** `run_vivo()` está vacío y `--vivo` solo hace tres sondas TCP; `check_lag()` y `check_duplicados()` son tautológicos. C4 no tiene gate real.
4. **V11-04 · El consumidor no «descarta por SHA».** Siempre hace `client.write(..., overwrite=True)`. El README describe otra cosa.
5. **V11-05 · `run_all.py --check` en rojo.** Falta `data/resultados/auditoria_lagunas_silver.csv`, que README y `data/resultados/README.md` listan.
6. **V11-06 · `n_precio` contradice `precio_medio_eur`.** 60 filas con precio medio, solo 7 con `n_precio>0`; 53 municipios con precio quedan con `n_precio=0` por el gating de Tier C/D.
7. **V11-07 · `municipios` no tiene `codigo_ine`.** 0/252. La relación con anuncios va por `_id`; C5 se defiende, pero no se «ve».
8. **V11-08 · `openspec/config.yaml` sigue diciendo Docker.** Contradice la invariante del contrato.
9. **V11-09 · Cifras de documentación desincronizadas.** 354 vs 355 raw; gold 53/53 vs 63 artefactos; 16 vivas vs 17 reales; 29+8 PNG atribuidos al script cuando 4 son de la capa 2026.
10. **V11-10 · Habitaciones duplicadas 201/201.**

### P3 — deuda

11. `get_client()` con `lru_cache` frente a un docstring que promete releer `MONGO_URI`.
12. `tests/test_mongo.py:132` con `assert "_id" not in d or True` (tautología).
13. `verificar_gobernanza.py` fija 47/40 como literales.
14. El gate offline espera 15 colecciones y hay 17 vivas.
15. La cabecera de `almacenamiento-y-streaming/spec.md` dice que no hay gate único.
16. El deck y los 6 arreglos están sin commit.
17. El CI corre mongomock, no Mongo real.

---

## 7. Riesgos de defensa y respuesta recomendada

| Pregunta probable | Respuesta sólida | Estado |
|---|---|---|
| «Demuéstrame la recuperación HDFS» | `CONTENTSUMMARY` 353 + `GETFILESTATUS` OK; el `OPEN` falla por DNS del datanode, no por el proyecto | **Hoy no se puede cerrar en vivo**; arreglar hosts o descargar por IP |
| «¿Dónde están los procesados?» | Waiver de la profesora; originales + organización + recuperación (cuando el DNS funcione) | Defendible |
| «Demuéstrame Kafka en vivo» | Evidencia v8 (352/352, lag 0) + tests offline; hoy el broker no da metadata por DNS | Defendible si no se afirma que se ha revalidado hoy |
| «¿Por qué C4 no es 10?» | Existe la cadena por partes, pero no un comando único hasta Mongo; el gate offline no toca Mongo | Honesto |
| «¿Cuántos municipios tienen precio?» | 60 con `precio_medio_eur`, 7 con `n_precio>0` (gating Tier C/D) | **Hay que explicarlo antes de que lo pregunten** |
| «¿Cuántas colecciones?» | 17 vivas + 15 backup = 32 | Corregir el README |
| «¿Los gráficos son automáticos?» | 8 CSV + 33 PNG desde Mongo en una corrida; los 4 PNG de 2026 salen de `regenerar_capa_2026.py` | Defendible con matiz |

---

## 8. Plan de cierre recomendado (por coste/impacto)

1. **DNS del clúster (P1, 5 min).** Añadir `hadoop-master1/worker1/worker2.tartangalh.eus` al `hosts` del aula o usar la IP del datanode; ejecutar `scripts/hdfs_recuperacion_un_fichero.py` y guardar la salida como `evidencia/vivo_2026-11-12.json`. Esto sube C2 a 10 y cierra V11-01.
2. **Alinear el deck con la evidencia (P1, 10 min).** O se versiona la evidencia real de hoy, o la diapositiva B5 vuelve a la evidencia v8 (352, lag 0) y se retira «corrida real OK 2026-11-12». Cierra V11-02.
3. **Regenerar `auditoria_lagunas_silver.csv` (P2, 1 min).** Deja el DAG en verde y elimina una cita falsa.
4. **Corregir `n_precio` o documentarlo (P2).** Es la incoherencia numérica más visible.
5. **Actualizar cifras y Docker (P2, 15 min).** 17/15/32, 355, gold real, `openspec/config.yaml`.
6. **Commit local (P3, 2 min).** Sin push, según la convención del repo.

---

## 9. Anexo — comandos ejecutados

```bash
.venv/Scripts/python.exe -m pytest tests                     # 285 passed, 2 skipped
.venv/Scripts/python.exe scripts/verificar_gobernanza.py     # TODO OK
.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline  # OK
.venv/Scripts/python.exe transform/run_all.py --check        # rc 1: falta auditoria_lagunas_silver.csv
.venv/Scripts/python.exe scripts/run_pipeline.py --check     # rc 0
.venv/Scripts/python.exe scripts/verificar_fase_datos.py     # rc 1: solo FAIL 07
.venv/Scripts/python.exe analysis/run_analisis_mongo.py --salida /tmp/audit_v11_gold  # 11 pipelines, 13 CSV, 33 PNG
.venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py           # rc 2 (DNS)
.venv/Scripts/python.exe scripts/hdfs_recuperacion_un_fichero.py udalmap_vpo_terminadas.csv  # rc 2 (DNS)
# WebHDFS GETCONTENTSUMMARY / LISTSTATUS / GETFILESTATUS (read-only)
# KafkaAdminClient.list_topics + KafkaConsumer offsets (read-only, NodeNotReadyError)
# PyMongo: count_documents, distinct, aggregate, list_indexes, explain_before_after
```

**Ficheros leídos:** PDF/docx de la rúbrica, `contrato-reto/spec.md`, `almacenamiento-y-streaming/spec.md`, `README.md`, `AGENT.md`, `docs/README.md`, `data/resultados/README.md`, `analysis/mongo_indexes.py`, `analysis/mongo_aggregations.py`, `analysis/run_analisis_mongo.py`, `storage/*.py`, `scripts/*.py`, `tests/test_hdfs_recuperacion.py`, `tests/test_kafka_*.py`, `.github/workflows/quality-gate.yml`, auditorías v7-v10 y evidencia v8.

**Límites:** no se ejecutó `load_all`/`clean_all`, no se escribió en Mongo/HDFS/Kafka, no se lanzó el productor ni el consumidor reales, no se hizo commit ni push.
