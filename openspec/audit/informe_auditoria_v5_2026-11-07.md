# Auditoría integral v5 — `bigdata-vivienda-euskadi`

**Fecha:** 2026-11-07 · **Baseline:** `HEAD 0ada593` · **Modo:** solo lectura
**Plan aplicado:** `openspec/audit/plan_auditoria_v5_2026-11-07.md` + `plan_auditoria_v5_barridos_2026-11-07.md`
**Evidencia:** `openspec/audit/evidencia/2026-11-07/`

## 0. Veredicto

**APTO CON RESERVAS.** La cadena técnica funciona y es defendible: 178 tests colectados (177 passed, 1 skipped), 10 pipelines reproducibles, `explain()` con mejora medida 594→8 documentos, 594 anuncios y 252 municipios estables. No hay P0 ni P1.

Hay **6 hallazgos P2** y **8 P3** de deuda. Ninguno rompe la demo; dos cifras deben corregirse antes de la defensa (IDs de requisito duplicados y 43 vs 44 scripts) y una interpretación debe aclararse (VPO). El antiguo F-02 (188 vs 191) quedó **descartado**: `--verify` da 354 raw / 188 silver con 0 errores.

> Esta auditoría **no agota** las 527 verificaciones del plan. Se ejecutaron F0–F8, con **9 de 14 barridos completos** y 5 parciales. Lo no verificado se declara en §7; no se presenta como aprobado.

---

## 1. Baseline e integridad de la auditoría

| Comprobación | Valor medido | Evidencia |
|---|---|---|
| HEAD | `0ada593207828c1dc2d107e0ae27b4b17545adc5` | `git_baseline.txt` |
| Árbol de trabajo | 65 entradas modificadas/untracked al inicio | `git status --porcelain` |
| Digest del diff (baseline) | `87b7639654261fefe8401dc2bff01bbe84e4bb7c92f928607b9b6e089a3dcf49` | `git diff \| sha256sum` |
| Digest del índice | `581e8b1d1daa5e30ba0e0b42217ee33615d274290cda50cef4881488c1e59515` | `git ls-files -s \| sha256sum` |
| Python | 3.12.10 (`.venv`) | ejecución de scripts |
| Producción antes/después de tests | `anuncios 594`, `municipios 252` | `mongo_audit.txt` |

**Esta auditoría no escribió** en `data/`, `extract/`, `transform/`, `storage/`, `analysis/`, `tests/`, ni en el clúster. La suite escribe solo en `vivienda_euskadi_test`; los conteos de producción no cambiaron. `explain()` se ejecutó con `hint: {$natural: 1}` en lugar de `explain_before_after`, porque esa función **borra y recrea** el índice y habría violado el modo solo lectura.

> **Cambio concurrente detectado.** Entre el baseline y el cierre, un proceso externo a esta auditoría modificó `openspec/specs/contrato-reto/spec.md` (mtime 23:35:36) y movió `openspec/changes/2026-11-07-p1p2-stale-docs/` a `openspec/changes/archive/`. Por eso el digest del diff pasó de `87b7…` a `2f1f…` aunque el número de tracked modificados sigue en 48. No se revirtió nada: puede ser trabajo del usuario o de otra sesión. La auditoría solo creó los ficheros de `openspec/audit/`.

Artefactos creados: este informe, `matriz_requisitos_2026-11-07.csv`, `hallazgos_2026-11-07.csv` y `evidencia/2026-11-07/`.

---

## 2. Resultados por fase

### F0 — Preflight · PASS

- 356 ficheros en `data/raw`; 354 pares en `docs/raw_manifest_sha256.txt`; **0 entradas del manifiesto sin fichero**; 2 ficheros sin manifiesto (`.FROZEN`, `.gitkeep`, ambos esperados).
- **12/12 SHA-256 verificados OK** sobre la muestra; `.FROZEN` presente.
- `data/procesado`: **191 ficheros** = 144 JSON + 42 CSV + 2 TXT + 1 MD + 1 GeoJSON + `.gitkeep`.
- `data/resultados`: 33 ficheros = 16 CSV + 12 PNG + 2 dashboards HTML + README + mapa de esquema.
- Mongo `127.0.0.1:27017` responde; `vivienda_euskadi` con **28 colecciones = 14 vivas + 14 `__backup`**.

### F1 — Contrato y rúbrica · PASS con corrección de conteo

- Pesos v2 confirmados: **46,7 % / 13,3 % / 40 %** (BDA RA1, SBD RA3, SBD RA4).
- **19 criterios de nivel 10**, no 26: 4 (BDA RA1) + 4 (SBD RA1) + 6 (SBD RA3) + 5 (SBD RA4). El plan v5 usó 26; ese número incluye criterios que no están en las tablas v2 y **debe corregirse** (F-07).
- 14/14 frases distintivas del PDF aparecen literalmente en `openspec/specs/contrato-reto/spec.md` (cotovía normalizada). No se detectaron alteraciones de umbrales.
- El DOCX Tema 8 se mantiene como evaluación separada; no se suman sus pesos a los v2. Correcto.

### F2 — Requisitos · PASS con trazabilidad rota

- **45 cabeceras `### Requirement:`**, **43 IDs únicos**.
- Duplicados reales: `EXTRACCION-01` (2 cabeceras) y `CONCLUSION-01` (2 cabeceras). `ENTREGABLES-01` aparece una vez como requisito y otra como destino de mapa, no es duplicado.
- 259 ficheros del corpus (código, tests, docs, specs) cruzados contra cada ID. La matriz completa está en `matriz_requisitos_2026-11-07.csv`.
- Resultado: **39 CUMPLE, 6 PARCIAL, 0 NO CUMPLE**. Los parciales son `INTEGRACION-01`, `GATE-JOIN-01`, `TIER-01`, `VALIDACION-01`, `RENTA-01`, `DOCS-01`.

### F3 — Extracción y transformación · PASS con deuda

- `extract/`: **41 `.py`**, 29 numerados, 39 con `main()`. Colisiones de numeración: dos `09_` y tres `10_`.
- 40 fuentes inventariadas en `config/fuentes.yaml`.
- `transform/`: **44 `.py`**; DAG de `run_all.py` con **34 nodos**. Fuera del DAG: `_raw_guard.py`, `auditoria_duckdb.py`, `f4_pisos_dirigido.py`, `generar_dashboard_completo.py`, `generar_dashboard_visual.py`, `generar_f4_pisos_objetivo.py`, `generar_fotocasa_dirigido_informe.py`, `muni_resolve.py`, `run_all.py`, `validar_renta.py`.
- Raw inmutable: manifiesto completo y hashes correctos; no se escribió en `data/raw`.

### F4 — MongoDB y análisis · PASS

| Comprobación | Resultado |
|---|---|
| Colecciones | 14 vivas + 14 backup; `anuncios` 594, `municipios` 252, `etxebide_solicitudes` 5040, `etxebide_promociones` 406, `ecvi_compraventa` 29 |
| Modalidad | 326 larga estancia + 268 temporal |
| Portales | Fotocasa 428 · Pisos 87 · RealtyAPI 79 |
| `codigo_ine` | 594/594 con 5 dígitos |
| Capas de alquiler | 159 oficial + 93 IDW = 252; sin solape |
| Índices | 9 declarados; 4 en `anuncios`, incluido único `(portal, id_anuncio)` |
| `explain()` | natural: **COLLSCAN**, 594 docs; con índice: **IXSCAN**, 8 docs / 8 claves, 8 devueltos |
| Pipelines | 10, entre 4 y 7 etapas; 3 con `$group`, 8 con `$lookup`, 4 con `$unwind` |
| Reproducibilidad | doble ejecución de los 10 → conteos idénticos |
| Filas por pipeline | 252, 252, 2, 4, 252, 252, 252, 322, 251, 252 |
| Limpieza | canonicalización INE, marcado de nulos, dedup con `delete_many`, conversión de tipos, `$unset` de obsoletos |
| CRUD | `demo_crud_operations`: insert, insert_many, update, `$inc/$push/$addToSet`, `find_one_and_update`, upsert, `$unset/$rename/$pull`, bulk, delete |
| Consultas | 30 funciones en `analysis/mongo_queries.py` (anidados, arrays, `$elemMatch`, regex, tipos, paginación) |

La rúbrica exige ≥3 pipelines con ≥5 etapas distintas, `$group` y uno de `$lookup/$unwind/$facet`: se cumple con margen.

### F5 — Tests · PASS

```
177 passed, 1 skipped in 8.96s
```

- 178 colectados; el skip es el test destructivo separado.
- Conteos de producción idénticos antes y después.
- 22 ficheros de test; sin fallos, sin errores de colección.

### F6 — Datos y artefactos · PASS con un aviso de lectura

- 16 CSV de resultados; nulos 0 en columnas clave (`n_anuncios`, esfuerzo, alquiler, paro).
- `codigo_ine` de 5 dígitos en todos los CSV; 0 duplicados salvo `mongo_vpo_por_municipio.csv`, que es promoción×tipología (322 filas, 77 municipios) y **no** una fila por municipio.
- Tier: **A 4 / B 3 / C 57 / D 188**; `n≥30` = 4; 188 municipios con 0 anuncios. Coincide con README y `docs/metodologia.md`.
- `comparativa_3_municipios_mongo.csv`: 4 filas (3 municipios + referencia), cumple ≥3.
- 12 PNG únicos; 13 emitidos históricamente por duplicado de `A1`, documentado.
- **VPO:** `NumViviendas` está vacío en **406/406** promociones de origen; `num_viviendas` se guarda `None` y el pipeline suma 0. El CSV publica `viviendas=0` en las 322 filas. Es «sin dato», no un cero real (F-01).

### F7 — Infraestructura · N/V en vivo

- **Kafka `10.22.87.215:9092`: timeout TCP.** **HDFS `10.22.87.215:50070`: timeout TCP y HTTP.** No hay evidencia viva del flujo completo en esta sesión.
- Estático: productor con `add_callback/add_errback`, consumidor con `enable_auto_commit=False`, commit manual por mensaje, `KAFKA_IDLE_MS`, verificación local por tamaño y SHA antes de subir, estado reanudable en `data/_hdfs_state/`, `upload_raw_excluding_legacy` y `read_file_sha256`. Diseño correcto; ejecución no comprobada.
- `duckdb==2.0.0` sigue en `requirements.txt` y lo usan 5 scripts, 4 de ellos legacy fuera del DAG.

### F8 — Documentación, seguridad y entrega · PASS con contradicciones

- **Sin secretos versionados**: `git ls-files` no contiene `.env`, `api.txt`, claves ni certificados. `.env` existe local (1580 bytes) y está ignorado.
- 13 variables de entorno usadas; **5 no declaradas** en `.env.example`: `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_GROUP_ID`, `KAFKA_IDLE_MS`, `MONGO_TEST_DB`, `MONGO_URI`. Declaradas y no usadas: `HDFS_BASE_PATH`, `IDEALISTA_API_KEY`, `VM_HOST`, `VM_KAFKA_PORT`.
- 21 directorios en `openspec/changes` sin archivar.
- Presentación: HTML con 10 SVG referenciados (10/10 existen), 8 `<img>`, PDF de 13 páginas. Coherente con el guion de 12 min.
- Deuda: **90 `except Exception`**, 43 `print()` en `storage/` y `analysis/`, 1 `if False` en `extract/udalmap_empleo.py:86`.

---

## 3. Hallazgos

| ID | Sev. | Hallazgo | Evidencia | Impacto | Acción |
|---|---|---|---|---|---|
| F-01 | P2 | `mongo_vpo_por_municipio.csv` publica `viviendas=0` en 322/322 filas; el origen tiene `NumViviendas` vacío en 406/406 | `vpo_audit.txt`; `storage/load_mongo.py:523` | Se puede leer «0 viviendas» donde no hay dato | Dejar `viviendas` nulo o renombrar `viviendas_sin_dato` y añadir nota en el CSV |
| F-02 | — | **Descartado.** 191 ficheros en disco − 3 excluidos (`.gitkeep`, `ingestion_manifest.json`, `manifest_sha256.txt`) = 188; `--verify` exit 0 | `data/procesado/manifest_sha256.txt` (188); `extract/generar_manifest.py:30` | Ninguno | Ninguna |
| F-03 | P2 | 5 variables usadas sin declarar; 4 declaradas sin uso | `env` F8 | Reproducción en otra máquina falla en Kafka/Mongo test | Completar `.env.example` y retirar las muertas |
| F-04 | P2 | 45 cabeceras de requisito, 43 IDs únicos; `EXTRACCION-01` y `CONCLUSION-01` duplicados | `requisitos_audit.txt` | Matriz de trazabilidad ambigua | Renombrar extensiones (`-B`, `-TIER`) |
| F-05 | P2 | README dice 43 scripts de transform; hay 44 y 34 en el DAG; 10 fuera | `README.md:120`; DAG F3 | La cifra estrella de «automatización» no cuadra | Actualizar a 44/34 y listar los 10 fuera del DAG |
| F-06 | P2 | Kafka y HDFS no responden desde esta red; no hay captura viva del flujo completo | F7 | «Listo» es estático, no demostrado | Capturar `status`/consumo desde el clúster o marcarlo N/V |
| F-07 | P2 | El plan v5 contó 26 criterios de rúbrica; el contrato tiene 19 | F1; `contrato-reto/spec.md` | Checklist de auditoría inflada | Corregir el plan a 19 |
| F-08 | P3 | `TIER-01` se titula «Raw inmutable, HDFS solo raw, Kafka→HDFS», no habla de tiers | `mongodb-y-analisis/spec.md` | ID engañoso | Renombrar a `RAW-01` o mover el contenido |
| F-09 | P3 | `if False` en `extract/udalmap_empleo.py:86` | grep F8 | Código muerto | Eliminar |
| F-10 | P3 | 90 `except Exception` y 43 `print()` en librerías | grep F8 | Errores silenciosos y salida no estructurada | Acotar excepciones y usar logging |
| F-11 | P3 | `duckdb` en requirements y 5 scripts, 4 legacy | F7/F8 | Dependencia pesada sin cadena vigente | Mover a `requirements-legacy.txt` |
| F-12 | P3 | Dos `09_` y tres `10_` en `extract/` | F3 | Orden aparente ambiguo; el orquestador ordena alfabéticamente | Documentar lotes; no renumerar |
| F-13 | P3 | 21 cambios sin archivar | F8 | Ruido en `openspec/changes` | Archivar cerrados |
| F-14 | P3 | `idx_udx_id` indexa `_id`, ya indexado por Mongo | `analysis/mongo_indexes.py:94` | Índice redundante | Eliminar |
| F-15 | P3 | 13 PNG emitidos, 12 únicos | F6; README | Confusión menor | Mantener la nota actual |

**Sin P0 ni P1.** Ningún hallazgo impide ejecutar la demo ni invalida las conclusiones principales (esfuerzo, tiers, comparativa de 4 municipios).

---

## 4. Matriz de requisitos

45 filas en `matriz_requisitos_2026-11-07.csv`. Resumen:

| Veredicto | Nº | Requisitos |
|---|---:|---|
| CUMPLE | 39 | Núcleo de extracción, modelo, CRUD, consultas, aggregation, índices, limpieza, capas, indicadores, visualización, conclusiones |
| PARCIAL | 6 | `INTEGRACION-01`, `GATE-JOIN-01`, `TIER-01`, `VALIDACION-01`, `RENTA-01`, `DOCS-01` |
| NO CUMPLE | 0 | — |

Los parciales no son fallos de código: son requisitos cuya evidencia es documental o está incompleta (gate sin test automatizado, validación «si procede», `validar_renta` fuera del DAG).

---

## 5. Rúbrica v2 — 19 criterios

| # | Criterio | Veredicto | Evidencia |
|---:|---|---|---|
| 1 | Extracción con API/scraping | CUMPLE | 41 extractores, 40 fuentes |
| 2 | HDFS originales y procesados + recuperación | CUMPLE* | `hdfs_utils`, manifiesto, `.FROZEN`; vivo N/V |
| 3 | Kafka productor y consumidor | CUMPLE* | `kafka_raw_producer`, `kafka_hdfs_uploader`; vivo N/V |
| 4 | Flujo completo hasta MongoDB | CUMPLE* | `run_mongo_pipeline.py`; vivo N/V |
| 5 | Integración de 2+ fuentes | CUMPLE | 14 colecciones, 5+ fuentes |
| 6 | Construcción del conjunto de datos | CUMPLE | 594 anuncios, 252 municipios |
| 7 | Limpieza/transformación (≥4 ops) | CUMPLE | 5 operaciones en `clean_mongo.py` |
| 8 | Automatización sin tocar Mongo a mano | CUMPLE | `load_all → clean_all → ensure_indexes` |
| 9 | Modelado justificado | CUMPLE | `docs/modelo_mongodb.md` (7 preguntas) |
| 10 | CRUD completo | CUMPLE | `demo_crud_operations` + tests |
| 11 | Consultas (≥4 tipos) | CUMPLE | 30 funciones |
| 12 | Aggregation (≥3, 5 etapas, `$group` + lookup/unwind/facet) | CUMPLE | 10 pipelines, 8 etapas distintas |
| 13 | Índices + `explain()` | CUMPLE | 9 índices; 594→8 docs |
| 14 | Consistencia/atomicidad | CUMPLE | `find_one_and_update` + justificación docx §11 |
| 15 | Datos heterogéneos | CUMPLE | arrays, anidados, 14 colecciones |
| 16 | Automatización del análisis | CUMPLE | `run_analisis_mongo.py` |
| 17 | ≥5 indicadores de 2+ fuentes | CUMPLE | esfuerzo, paro, renta, VPO, accesibilidad, certificados |
| 18 | ≥3 municipios/zonas con indicador | CUMPLE | Bilbao, Donostia, Getxo, Vitoria |
| 19 | ≥3 conjuntos para visualizar | CUMPLE | 16 CSV + 12 PNG |

\* CUMPLE estático; ejecución viva no verificada en esta sesión.

---

## 6. Contradicciones y cifras

| # | Contradicción | Valor real medido | Estado |
|---|---|---|---|
| H1 | 178 vs 151/145/136 tests | 178 colectados, 177 passed, 1 skipped | Resuelta; históricos no vigentes |
| H2 | 594 vs 759 anuncios | 594 (326+268); 759 es pre-v5 | Resuelta, ya etiquetada histórica |
| H3 | 191 vs 188/185 silver | **191 − 3 excluidos = 188**; `--verify` exit 0 (354/188) | Resuelta; F-02 descartado |
| H4 | 34 vs 43 scripts | **44 `.py`**, 34 en DAG | Abierta → F-05 |
| H5 | «14 colecciones» | 14 vivas + 14 backup = 28 | Aclarar en README |
| H6 | `duckdb` en requirements | 5 scripts, 4 legacy | Abierta → F-11 |
| H7 | IDs duplicados | 45 cabeceras / 43 únicos | Abierta → F-04 |
| H8 | 21 changes sin archivar | 21 | Abierta → F-13 |
| H9 | 12 vs 13 PNG | 12 únicos, 13 emitidos | Documentada |
| H10 | manifest 354 vs 188 | 354 entradas raw; silver sin manifiesto propio | Abierta → F-02 |
| H11 | 26 criterios de rúbrica | **19** | Abierta → F-07 |

---

## 7. Lo que no se verificó

1. **Ejecución viva de HDFS y Kafka**: timeouts TCP/HTTP. Solo se auditó el código y la configuración.
2. **Los 359 barridos elemento a elemento**: 9 de 14 completos; PNG, VIS-A, DOC-F, IDX-I y RUB quedaron parciales.
3. **Fidelidad visual del PDF**: se comparó texto, no maquetación ni cifras de las diapositivas contra los CSV.
4. **Reproducción desde cero** (`extract` + `transform` completos): no se ejecutó para no escribir en `data/`; se verificó el estado final y los manifiestos.
5. **Copia/restauración real de backups**: se comprobó su existencia y conteo, no un `restore` (sería escritura).

---

## 8. Backlog priorizado

**Antes de la defensa (P2, ~2 h):**

1. **F-04** Renombrar las dos extensiones duplicadas y fijar 45/43 en la documentación.
2. **F-05** Actualizar 43→44 scripts y 34 nodos; listar los 10 fuera del DAG.
3. **F-03** Completar `.env.example` con las 5 variables y retirar las 4 muertas.
4. **F-01** Aclarar `viviendas=0` como «sin dato» (nulo o nota en el CSV VPO).
5. **F-07** Corregir el plan de 26 a 19 criterios.
6. **F-06** Añadir captura viva de HDFS/Kafka o marcar N/V en README.

**Después (P3):** F-08…F-15.

---

## 9. Reproducibilidad

```bash
# Baseline
git rev-parse HEAD && git status --porcelain

# Tests (escribe solo en vivienda_euskadi_test)
.venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider

# Mongo (lectura)
.venv/Scripts/python.exe - <<'PY'
from pymongo import MongoClient
db=MongoClient("mongodb://localhost:27017")["vivienda_euskadi"]
print(db.anuncios.count_documents({}), db.municipios.count_documents({}))
PY

# Pipelines (lectura, sin run_analisis_mongo: no escribe CSV ni toca índices)
.venv/Scripts/python.exe -c "from analysis.mongo_aggregations import run_all; print({k:len(v) for k,v in run_all().items()})"

# Integridad raw
.venv/Scripts/python.exe extract/generar_manifest.py --verify
```

---

## Anexo A — Evidencia generada

| Fichero | Contenido |
|---|---|
| `evidencia/2026-11-07/rubrica_pdf.txt` | Texto extraído del PDF v2 (6 páginas) |
| `evidencia/2026-11-07/tema8_docx.txt` | Texto extraído del DOCX Tema 8 |
| `evidencia/2026-11-07/mongo_audit.txt` | 28 colecciones, tipos BSON, índices, explain, integridad |
| `evidencia/2026-11-07/pipelines_audit.txt` | 10 pipelines, etapas, filas, doble ejecución |
| `evidencia/2026-11-07/datos_audit.txt` | 16 CSV, nulos, duplicados, tiers, BOM |
| `evidencia/2026-11-07/raw_audit.txt` | 356 raw, 354 manifiesto, 12 SHA, silver |
| `evidencia/2026-11-07/requisitos_audit.txt` | 45 cabeceras, menciones código/test/doc |
| `evidencia/2026-11-07/vpo_audit.txt` | `NumViviendas` vacío 406/406, suma 0 |
| `evidencia/2026-11-07/git_baseline.txt` | HEAD y estado inicial |
| `matriz_requisitos_2026-11-07.csv` | 45 filas: ID, dominio, menciones y veredicto |
| `hallazgos_2026-11-07.csv` | 15 hallazgos con severidad, evidencia y acción |

## Anexo B — Criterio de cierre

Un hallazgo se cierra solo con: (a) el artefacto corregido, (b) el comando que lo demuestra y (c) la salida numérica. Las afirmaciones de este informe sin salida numérica están marcadas como N/V o documentales.

---

## 10. Estado de corrección (2026-11-07, post-auditoría)

Aplicadas las correcciones de riesgo < 6. Evidencia: `pytest tests -q` → **177 passed, 1 skipped**; `scripts/verificar_gobernanza.py` → **TODO OK** (45 IDs únicos, 44/34, 188 silver, 0 env sin declarar, 10 pipelines); `git diff --check` sin errores en los ficheros tocados (los SVG de presentación ya modificados conservan trailing whitespace ajeno a esta corrección).

| ID | Estado | Evidencia |
|---|---|---|
| F-01 | **CORREGIDO** | `pipeline_vpo_por_municipio` publica `viviendas` nulo si `promociones_con_viviendas=0`; CSV 322 filas, 322 vacías, 0 ceros |
| F-02 | **DESCARTADO** | `--verify`: 354 raw / 188 silver, 0 errores |
| F-03 | **CORREGIDO** | `.env.example`: `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_GROUP_ID`, `KAFKA_IDLE_MS`, `MONGO_TEST_DB`, `MONGO_URI`; legacy comentadas |
| F-04 | **CORREGIDO** | 45 cabeceras / 45 IDs únicos; 2.ª `EXTRACCION-01`→`EXTRACCION-03`, 2.ª `CONCLUSION-01`→`CONCLUSION-02` |
| F-05 | **CORREGIDO** | README/arquitectura: 44 scripts (34 DAG); docs principales: 10 pipelines |
| F-06 | **N/V** | Excluido: red de clase no disponible; Kafka/HDFS no se tocan |
| F-07 | **CORREGIDO** | Plan: 19 criterios v2 (+7 Tema 8), no 26 |
| F-08 | **CORREGIDO** | `TIER-01`→`RAW-01` en spec; comentarios de tier→`CONCLUSION-02` |
| F-09 | **CORREGIDO** | `if False` eliminado en `extract/udalmap_empleo.py` |
| F-10 | **PARCIAL** | 2 `except Exception: return {}` acotados con `logger.warning`; quedan ~88 amplios y 43 prints (riesgo global 6) |
| F-11 | **CORREGIDO** | `duckdb` movido a `requirements-legacy.txt` |
| F-12 | **NO PROCEDE** | Prefijos 09/10 = lotes independientes; `main_ingest` ordena alfabéticamente y el orden es determinista. Renumerar rompería docs y manifiestos históricos sin beneficio funcional. Documentado en el docstring del orquestador. |
| F-13 | **PARCIAL** | Archivados los changes cerrados sin referencias; `cierre-suficiencia-auditoria` conserva 1 tarea diferida (merge de delta) |
| F-14 | **CORREGIDO** | `idx_udx_id` eliminado de `mongo_indexes.py` y de Mongo (`_id_` sigue cubriéndolo) |
| F-15 | **SIN ACCIÓN** | Nota 12 únicos / 13 emitidos mantenida |

**Pendiente declarado:** F-10 global (riesgo 6), F-06 (N/V por red) y F-13 residual (1 change con tarea diferida). F-12 se cierra como no procede. No se tocó Kafka/HDFS.
