# Plan de auditoría v5 — auditoría integral del proyecto

**Fecha:** 2026-11-07
**Estado:** PLAN. No se ejecuta en esta sesión. No se modifica `data/`, `extract/`, `transform/`, `storage/`, `analysis/`, `tests/`, MongoDB ni el clúster.
**Sustituye a:** `plan_auditoria_v4_2026-11-07.md` como plan vigente. v3 y v4 quedan como baseline histórico y fuente de hipótesis, nunca como evidencia.
**Objetivo:** verificar **todo** el proyecto —contrato, datos, código, infraestructura, tests, documentación y entrega— con evidencia re-ejecutada, y producir un veredicto defendible criterio por criterio.

---

## 0. Qué significa "auditar todo" en este proyecto

La auditoría cubre 18 dominios con **168 puntos de método** más **359 verificaciones de barrido elemento a elemento** (anexo `plan_auditoria_v5_barridos_2026-11-07.md`). **Total: 527 verificaciones** con ID estable. Cada una declara: qué se audita, cómo se comprueba, qué evidencia se exige y qué severidad tiene un fallo.

| Dominio | Prefijo | Puntos | Qué cubre |
|---|---|---:|---|
| Gobernanza y preflight | `PRE` | 10 | baseline, digest, entorno, acceso, inventario, alcance |
| Contrato y rúbrica | `CTR` | 8 | fidelidad PDF/DOCX, pesos, umbrales, enmiendas |
| Cobertura de requisitos | `REQ` | 7 | 44 cabeceras de requisito de las 5 specs (barrido `RQS`) |
| Extracción | `EXT` | 12 | API, scraping, sidecars, raw inmutable, dedup, outliers, cuarentena |
| Transformación y silver | `TRF` | 12 | DAG, orden, idempotencia, encoding, `codigo_ine`, imputación |
| Modelo Mongo y CRUD | `MON` | 12 | colecciones, tipos BSON, embedding/referencing, CRUD, carga segura, atomicidad |
| Índices y rendimiento | `IDX` | 6 | `explain()` before/after, tipos de índice, justificación |
| Agregaciones e indicadores | `AGG` | 12 | 10 pipelines, etapas, IQR/winsor, tiers, capas, indicadores |
| Reproducibilidad y artefactos | `REP` | 8 | doble ejecución, huellas, mtimes, CSV/PNG canónicos |
| Calidad y suficiencia del dato | `DAT` | 14 | cobertura 252, n≥30, sesgos, proxies, años, granularidad |
| Tests | `TST` | 10 | 178 tests, requisito→test, asserts triviales, skips, aislamiento |
| HDFS, Kafka e integración | `INF` | 10 | originales/procesados, recuperación, productor/consumidor, waiver |
| Visualización y presentación | `VIS` | 10 | PNG desde Mongo, SVG/HTML/PDF, valores vs CSV, staleness |
| Documentación | `DOC` | 9 | contradicciones numéricas, links, índice, docs obsoletas |
| Seguridad y configuración | `SEC` | 7 | secretos, `.env`, IPs, destructivos, permisos |
| Código y arquitectura | `COD` | 9 | duplicación, errores silenciados, dead code, acoplamiento |
| Repositorio y git | `GIT` | 6 | árbol sucio, untracked, cambios sin archivar, convenciones |
| Defensa y entregables | `DEF` | 6 | informe, guion, demo, matriz O1–O4, rúbrica final |
| **Subtotal método** | | **168** | |
| **Barridos (anexo)** | `SRC…ENV` | **359** | 40 fuentes, 41 extractores, 44 transforms, 28 colecciones, 10 pipelines, 44 requisitos, 26 filas de rúbrica (19 v2 + 7 Tema 8), 22 tests, 9 índices, 16 CSV, 12 PNG, 24 assets, 30 docs, 13 variables |
| **Total auditoría** | | **527** | |

---

## 1. Baseline medido (preflight de esta planificación)

Estos datos se midieron el 2026-11-07 para dimensionar el plan. **No son veredictos**: la auditoría debe re-medirlos y confirmarlos o refutarlos.

| Hecho medido | Valor | Fuente del dato |
|---|---:|---|
| Commit HEAD | `0ada593` | `git log -1` |
| Árbol de trabajo | **49 modificados + 3 untracked** | `git status --short` |
| Python | 3.12.10 | `.venv/Scripts/python.exe --version` |
| Tests colectados | **178** | `pytest tests --collect-only -q` |
| Funciones `test_` | 148 | `grep -c "def test_"` |
| Referencias a skip/xfail | 25 | `grep -rn` |
| `data/raw` | 356 ficheros | `find` |
| Manifest raw | 354 líneas | `docs/raw_manifest_sha256.txt` |
| `data/procesado` | 191 ficheros (42 CSV raíz, 78 JSON, 67 en `_meta`) | `find` |
| `ingestion_manifest` | 354 fichas | `data/procesado/_meta/ingestion_manifest.json` |
| Nodos del DAG | 34 | `transform/run_all.py:SCRIPTS` |
| `data/resultados` | 32 ficheros + README = 33 | `ls` |
| CSV de resultados | 16 (252/159/93/… filas) | `wc -l` |
| PNG en resultados | 12 | `ls data/resultados/*.png` |
| Mongo `vivienda_euskadi` | **28 colecciones = 14 vivas + 14 `__backup`** | `list_collection_names()` |
| `anuncios` | 594 | `estimated_document_count()` |
| `municipios` | 252 | idem |
| `ecvi_compraventa` | 29 | idem |
| Scripts `extract/NN_*` | 29 | `ls extract/[0-9][0-9]_*.py` |
| Scripts con `main()` | 39 | `grep -rl "def main("` |
| Sidecars en `data/raw` | 0 | `find -name '*.meta.json'` |
| `except Exception` | 90 | `grep -rn` |
| `if False` | 1 | `grep -rn` |
| Cambios openspec sin archivar | 21 | `ls -d openspec/changes/*/` |
| Secretos versionados | 0 | `git ls-files` |

### 1.1 Contradicciones ya visibles (hipótesis, no hallazgos)

La auditoría debe resolverlas; aquí solo se registran para que no se hereden:

| # | Dato A | Dato B | Dónde |
|---|---|---|---|
| H1 | 178 tests colectados | v4 plan decía 151; docs dicen 136/145/177 | plan v4, README, AGENT, docs |
| H2 | 14 colecciones vivas + 14 backups | docs hablan de "14 colecciones" sin aclarar backups | README, Mongo |
| H3 | `anuncios` = 594 | docs antiguos y 54 ficheros activos citan 759 | Mongo vs `.md` |
| H4 | `data/procesado` = 191 ficheros | docs dicen manifest 185/188 | README/AGENT vs disco |
| H5 | `ingestion_manifest` = 354 fichas | README dice "manifest 188" para silver | README |
| H6 | 34 nodos en el DAG | README dice "43 scripts" en `transform/` | README vs `run_all.py` |
| H7 | 12 PNG emitidos | README dice "12 PNG únicos (13 emitidos)" | README vs disco |
| H8 | `requirements.txt` incluye `duckdb==2.0.0` | README dice que DuckDB es legacy, sin dependencia | requirements vs README |
| H9 | IDs de requisito duplicados: `EXTRACCION-01` (2 veces), `CONCLUSION-01` (2 veces) | Se asume que son extensiones, no colisión | specs |
| H10 | 21 changes sin archivar | AGENT dice que el archivo está cerrado | `openspec/changes/` |

**Regla:** ninguna de estas filas se da por buena sin comando y número. Si un dato del baseline no se reproduce, el informe lo corrige y anota la desincronización.

---

## 2. Reglas de la auditoría

1. **Solo lectura.** Única escritura permitida: los `.md` de auditoría en `openspec/audit/` y logs en `openspec/audit/evidencia/` (gitignored o declarado). Nada de `data/`, código, Mongo (`insert/update/delete/drop`), HDFS ni Kafka.
2. **Evidencia triple.** Cada punto exige: (a) comando ejecutado, (b) salida numérica o literal, (c) `fichero:línea` del código/dato que lo produce. Sin las tres, el veredicto máximo es `NO VERIFICABLE`.
3. **La documentación no es evidencia.** Un README que dice "9 pipelines" no puntúa; puntúan los pipelines contados y ejecutados. La documentación solo se audita **como documentación** (`DOC`).
4. **Umbral literal.** Para la rúbrica, 10 solo si se cumple la columna del 10 palabra por palabra. "Casi" = 7. Nunca se redondea al alza.
5. **No verificable ≠ 10.** Se marca `PENDIENTE` con la lista exacta de lo que falta.
6. **Falsación obligatoria.** Cada `CUMPLE` frágil anota qué observación lo convertiría en `NO CUMPLE`.
7. **Comparativa, no memoria.** Toda métrica se compara con v3/v4 y con el baseline de §1: antes / hoy / delta / veredicto.
8. **Un fallo, una severidad.** P0 tumba una entrega; P1 tumba un criterio de rúbrica; P2 degrada calidad; P3 es deuda.
9. **Sin arreglos.** La auditoría detecta y documenta; las reparaciones van a `backlog_v5`, con triaje de riesgo y autorización aparte.
10. **Baseline pineado.** Como el árbol tiene 49 cambios sin commitear, el informe fija commit + `git diff | sha256sum` + digest de ficheros. Sin baseline pineado no hay auditoría reproducible.

### 2.1 Escala de veredicto por punto

| Veredicto | Significado |
|---|---|
| `CUMPLE` | Evidencia triple completa y umbral literal satisfecho |
| `CUMPLE CON SALVEDAD` | Se cumple, pero con una excepción declarada y acotada (waiver, límite de acceso) |
| `NO CUMPLE` | La evidencia contradice el umbral |
| `NO VERIFICABLE` | Falta acceso, dato o ejecución; se detalla qué falta |
| `N/A` | El punto no aplica al estado actual, con justificación |

### 2.2 Escala de severidad

| Sev. | Definición | Efecto |
|---|---|---|
| **P0** | Integridad rota, dato falso, secreto expuesto, entrega imposible | Bloquea la entrega |
| **P1** | Criterio de rúbrica por debajo de 10, requisito SHALL incumplido | Baja nota |
| **P2** | Deuda que degrada calidad o defensa, sin romper requisito | Afecta P2/P3 del informe |
| **P3** | Estilo, duplicación, higiene | Backlog |

---

## 3. Dominios y puntos de control

### PRE — Gobernanza y preflight (10)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| PRE-01 | Baseline git pineado | `git rev-parse HEAD`, `git status --porcelain`, `git diff \| sha256sum` | commit + conteo M/?? + hash del diff | P1 |
| PRE-02 | Digest del árbol antes/después | `git ls-files -s \| sha256sum` al abrir y cerrar | dos hashes idénticos | P1 |
| PRE-03 | Entorno reproducible | `python --version`, `pip freeze \| sha256sum`, `requirements.txt` vs imports reales | versión + hash + diff de dependencias | P2 |
| PRE-04 | Acceso a Mongo | ping 27017, `list_database_names()`, `count_documents` por colección | salida literal | P1 (degrada MON/AGG) |
| PRE-05 | Acceso a HDFS/Kafka | `LISTSTATUS`, `kafka-topics --describe` o declaración de no acceso | salida o `SIN ACCESO` fechado | P2 |
| PRE-06 | Inventario de datos | conteo por directorio y extensión, tamaños, mtimes | tabla completa | P2 |
| PRE-07 | Suite colectable | `pytest --collect-only -q`, errores de import | número exacto + errores | P1 |
| PRE-08 | Alcance y exclusiones | lista de lo que queda fuera (VM, credenciales, red) | declaración en cabecera | P2 |
| PRE-09 | Herramientas de medición | versiones de `pytest`, `pymongo`, `pandas`, `matplotlib` | `pip show` | P3 |
| PRE-10 | Plan de evidencia | carpeta `openspec/audit/evidencia/2026-11-07/` con logs crudos | índice de logs | P3 |

### CTR — Contrato y rúbrica (8)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| CTR-01 | Fidelidad PDF → spec | extraer texto de `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (pypdf) y comparar celda a celda con `contrato-reto/spec.md` | tabla X/Y celdas idénticas + desvíos | P0 |
| CTR-02 | Fidelidad DOCX → spec | leer `word/document.xml` de `Tema_8_...docx` §16 y cotejar pesos 15/15/20/15/10/15/10 | celdas + desvíos | P0 |
| CTR-03 | Pesos de la evaluación | 46,7 % / 13,3 % / 40 % y Tema 8 separado | cita de línea en PDF y spec | P1 |
| CTR-04 | Umbrales 0/3/7/10 | comprobar que ningún "10" se transcribió como SHOULD | diff semántico por criterio | P0 |
| CTR-05 | Enmiendas propias marcadas | `P-01`…`P-08`, canónico 18–34, `CARGA-SEGURA` etiquetados como extensión, no como rúbrica | grep + lectura | P2 |
| CTR-06 | Requisitos adicionales del PDF | objetivos 1–2, JSON/CSV, limpieza, transformaciones, Python, entregables | checklist | P1 |
| CTR-07 | Duplicidad de IDs | `EXTRACCION-01` y `CONCLUSION-01` repetidos; decidir si es extensión válida | listado de IDs y colisión | P2 |
| CTR-08 | Contradicciones internas de specs | p. ej. cabecera "PASS" vs cuerpo "gate pendiente"; escenarios Kafka→Mongo vs Kafka→HDFS | tabla requisito↔línea↔contradicción | P1 |

**Entregable:** `openspec/audit/matriz_fidelidad_rubrica_2026-11-07.md`.

### REQ — Cobertura de requisitos (7)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| REQ-01 | Inventario de requisitos | enumerar las 44 cabeceras de las 5 specs, con ID, línea y tipo (SHALL/SHOULD) | CSV `requisitos_2026-11-07.csv` | P1 |
| REQ-02 | Requisito → implementación | para cada ID, `fichero:línea` que lo implementa | matriz 42×1 | P1 |
| REQ-03 | Requisito → test | para cada ID, test que lo afirma (o "sin test") | matriz requisito→test | P1 |
| REQ-04 | Requisito → evidencia de datos | para cada ID, artefacto/consulta que lo demuestra | matriz requisito→artefacto | P1 |
| REQ-05 | Requisitos huérfanos | SHALL sin implementación o sin test | lista | P1 |
| REQ-06 | Requisitos zombis | implementación sin requisito (código que nadie exige) | lista | P3 |
| REQ-07 | Escenarios nivel 7 vs 10 | comprobar que existen ambos y que el 10 es el exigido | conteo de escenarios | P2 |

**Entregable:** `openspec/audit/matriz_requisitos_2026-11-07.csv` (ID, spec, línea, implementación, test, evidencia, veredicto).

### EXT — Extracción (12)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| EXT-01 | Automatización de API | contar extractores con `requests`/`_common.Cliente`, `main()` y salida en `raw` | lista de scripts + `main()` + fichero generado | P1 |
| EXT-02 | Automatización de scraping | regex/HTML sobre Fotocasa, Pisos, RealtyAPI; verificar que parsea HTML real, no fixtures | `fichero:línea` + muestra de registro parseado | P1 |
| EXT-03 | Reparto API vs scraping | clasificar cada fuente: API estructurada / scraping / descarga directa | tabla por fuente | P1 |
| EXT-04 | Cobertura de fuentes | 25 fuentes declaradas vs extractores reales | tabla fuente→script→artefacto | P2 |
| EXT-05 | `main()` ejecutable | cada script devuelve 0 y escribe artefacto (o declara dependencia de red) | log por script (sin re-descargar si no hay red) | P2 |
| EXT-06 | Sidecars de procedencia | 39 scripts con `main()` vs sidecars en `_meta` (67 ficheros) | ratio y lista de huérfanos | P2 |
| EXT-07 | Raw inmutable | `.FROZEN`, guards, lista blanca de 2 escritores, `assert_raw_writable` | `test_raw_guardrails` + grep | P0 |
| EXT-08 | Manifest raw | 356 ficheros reales vs 354 fichas; explicar `.FROZEN`/`.gitkeep` | diff exacto de nombres | P1 |
| EXT-09 | SHA-256 del manifest | recalcular N muestras (pequeña, media, grande) | 3/3 hashes iguales | P1 |
| EXT-10 | `property_fingerprint` | determinismo, campos usados, dedup posterior | función + test + conteo de duplicados | P1 |
| EXT-11 | Outliers en extracción | rangos 3–50 €/m², 10–500 m², habitaciones entero; IQR por segmento | código + conteo de descartes | P1 |
| EXT-12 | Cuarentena geo y re-resolución Pisos | `geo_invalida`, orden de resolución, 759→594 | conteo antes/después + test | P1 |

### TRF — Transformación y silver (12)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| TRF-01 | DAG declarado | 34 nodos en `SCRIPTS`, entradas/salidas, grupos | volcado del dict | P2 |
| TRF-02 | Orden topológico | `--check` sin ciclos, sin entradas ausentes | salida de `run_all.py --check` | P1 |
| TRF-03 | Escritores in-place | detectar scripts que modifican `raw` o sobrescriben silver sin control | grep + lista | P0 |
| TRF-04 | `dim_municipios` base vs enricher | el enricher corre después o `n_anuncios_raw` desaparece | orden en `SCRIPTS` + comprobación de columna | P1 |
| TRF-05 | Idempotencia | doble ejecución de un subconjunto → mismo SHA de salida | 2 hashes | P1 |
| TRF-06 | Encoding | BOM `utf-8-sig` en CSV silver, lectura tolerante | `head -c 3` en N ficheros | P2 |
| TRF-07 | `codigo_ine` | zfill(5), ceros a la izquierda en Araba, `int(float())` en Fotocasa | conteo de longitudes 4/5 y nulos | P1 |
| TRF-08 | Imputación declarada | oficial / IDW / comarcal / contexto, sin imputar en silencio | columna `metodo_imputacion` + conteos 159/93/252 | P0 |
| TRF-09 | Nulos y tipos | matriz de missingness por columna, coerciones silenciosas | tabla 42 CSV × columnas clave | P1 |
| TRF-10 | Duplicados | por `property_fingerprint`, `(portal,id_anuncio)`, nombre de municipio | conteos exactos | P1 |
| TRF-11 | Coherencia entre ficheros | mismos municipios y conteos entre silver, Mongo y CSV de resultados | 3 vías contrastadas | P1 |
| TRF-12 | Manifest silver | 191 ficheros vs `ingestion_manifest` 354 (raw) vs run_manifest | explicar cada cifra | P1 |

### MON — Modelo Mongo, CRUD y consistencia (12)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| MON-01 | Inventario de colecciones | 14 vivas + 14 `__backup`; documentar por qué hay backups | lista con conteos | P2 |
| MON-02 | Tipos BSON reales | `Decimal128`, `bool`, `datetime`, `GeoJSON`, arrays; muestreo por colección | `$type` counts | P1 |
| MON-03 | Embedding vs referencing | decidir y demostrar con consulta que atraviesa la relación | consulta + resultado | P1 |
| MON-04 | Campo común | `_id` de 5 dígitos vs `codigo_ine` explícito; el evaluador debe verlo | `$lookup` reproducible | P1 |
| MON-05 | Integridad referencial | 594/594 anuncios con municipio; 252/252 en 10 colecciones; ECVI 7/29 | conteos por colección | P1 |
| MON-06 | CRUD 4 operaciones | insert/update/delete/find con contadores y comprobación | código + test | P1 |
| MON-07 | Carga segura | staging → backup → rename; CSV vacío aborta; índices tras swap | código + test | P0 |
| MON-08 | Sincronización CSV↔Mongo | 594 CSV = 594 Mongo; sin huérfanos ni faltantes | diff de IDs | P1 |
| MON-09 | Limpieza ≥4 operaciones | nulos, duplicados, tipos, formato, `$unset` | 5 operaciones con contadores | P1 |
| MON-10 | Atomicidad/transacciones | `find_one_and_update` + dominio; sonda standalone documentada | código + test | P1 |
| MON-11 | Backups | `__backup` restaurables y fechados; no confundir con colecciones de negocio | conteo + fecha | P2 |
| MON-12 | Errores no silenciados | `ensure_indexes` propaga; excepciones tipadas | grep + test | P2 |

### IDX — Índices y rendimiento (6)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| IDX-01 | Inventario de índices | 9 índices declarados vs `list_indexes()` real | lista con nombre, clave, opciones | P1 |
| IDX-02 | `explain()` before/after | COLLSCAN vs IXSCAN con `hint {$natural:1}` sin borrar índices | `stage`, `docsExamined`, `keysExamined`, `nReturned` | P1 |
| IDX-03 | Justificación por índice | unique, compuesto ESR, multikey, `2dsphere` sparse, parcial | tabla índice→consulta que sirve | P2 |
| IDX-04 | Índices no usados | detectar índices sin consulta asociada | lista | P3 |
| IDX-05 | Cobertura de consultas | las consultas de `mongo_queries.py` usan índice cuando aplica | `explain` por consulta | P2 |
| IDX-06 | Coste de agregaciones | `explain` de pipelines pesados; `allowDiskUse` si aplica | tiempos y stages | P3 |

### AGG — Agregaciones e indicadores (12)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| AGG-01 | Número de pipelines | 10 funciones (`PIPELINE_ORDER`) vs "9 pipelines" documentado | lista y conteo | P1 |
| AGG-02 | Etapas por pipeline | ≥5 etapas distintas, `$group` + `$lookup`/`$unwind`/`$facet` | conteo por pipeline | P1 |
| AGG-03 | Ejecución real | cada pipeline devuelve filas (252/252/2/10/…) | tabla pipeline→filas | P1 |
| AGG-04 | Winsorización | percentiles 1–99, recorte no imputación, mediana correcta | revisión de expresión + contraste numérico | P1 |
| AGG-05 | Exclusión IQR | Q1/Q3 por municipio, bornes 1,5·IQR, efecto en `precio_medio_eur` | conteo de excluidos | P1 |
| AGG-06 | Tier A/B/C/D | regla n≥30, n_precio, C/D sin precio; 4/3/57/188 | tabla de conteos | P1 |
| AGG-07 | Capas de precio | oficial 159, IDW 93, contexto 252, sin mezcla | 3 CSV + `is_imputed` | P0 |
| AGG-08 | Indicadores ≥5 de 2+ fuentes | esfuerzo 18–34, tensión, paro, €/m², VPO terminadas | tabla indicador→fuente→cobertura | P1 |
| AGG-09 | Paro 252/252 | `tasa_paro_lanbide_pct`, no `tasa_paro_aprox_pct` | conteo + grep del campo inválido | P1 |
| AGG-10 | Ranking solo n≥30 | 4 Tier A, resto `n_insuficiente`; sin ordenar Barakaldo n=6 | CSV + lógica | P1 |
| AGG-11 | Modalidades separadas | temporal vs larga estancia, no media combinada | conteo y medias por grupo | P1 |
| AGG-12 | Decimal128/NaN/inf | `_fnum`, `_csv_value`, sin `NaN` en CSV/PNG | grep de `nan`/`inf` | P2 |

### REP — Reproducibilidad y artefactos (8)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| REP-01 | Doble ejecución | `run_analisis_mongo.py` dos veces → misma huella | 2 hashes | P1 |
| REP-02 | Huella publicada | `huella` del script vs valor en docs | coincidencia | P2 |
| REP-03 | Frescura de artefactos | mtime de PNG/CSV vs último CSV silver | tabla mtime | P1 |
| REP-04 | CSV canónicos | 6 canónicos + 1 VPO + 5 extras con filas esperadas | conteo por fichero | P1 |
| REP-05 | PNG canónicos | 12 en disco vs 13 "emitidos"; g1/A1 duplicado | lista y hash | P2 |
| REP-06 | Orden canónico de filas | `_orden_canonico` produce CSV estables | diff entre 2 ejecuciones | P2 |
| REP-07 | Rutas absolutas/relativas | funciona desde otra cwd y en Windows | ejecución en 2 cwd | P2 |
| REP-08 | Semillas y determinismo | sin aleatoriedad no sembrada (bootstrap, muestreo) | grep + 2 ejecuciones | P2 |

### DAT — Calidad y suficiencia del dato (14)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| DAT-01 | Universo municipal | 252 reales vs 253 con "C.A. de Euskadi" (00001) | conteo y filtro por prefijo 01/20/48 | P1 |
| DAT-02 | Cobertura de anuncios | 83/252 con anuncios; 64 municipios en 594; 53 residencial | tabla de cobertura | P1 |
| DAT-03 | Robustez n≥30 | solo 4 municipios; % del total | 4/252 y lista | P1 |
| DAT-04 | Tiers y edge cases | A 4, B 3, C 57, D 188; sin bucket huérfano | tabla + reconciliación | P1 |
| DAT-05 | Alquiler oficial | 159/252; 93 imputados por comarca; etiquetados | conteo + columna | P0 |
| DAT-06 | Proxies | renta municipal ≠ salario; emancipación CAE ≠ municipal | revisión de textos y variables | P1 |
| DAT-07 | Mezcla de años | anuncios 2026 vs alquiler/renta 2024 | tabla de años por fuente | P1 |
| DAT-08 | Falacia ecológica | conclusión municipal con renta media | revisión de conclusiones | P1 |
| DAT-09 | Sesgo urbano/rural | concentración Bilbao/Donostia/Getxo/Vitoria | distribución y % | P1 |
| DAT-10 | Valores atípicos | precios > umbral, €/m² imposibles, superficies 0 | conteo y ejemplos | P1 |
| DAT-11 | Missingness por indicador | matriz indicador × municipios con dato | CSV de cobertura | P1 |
| DAT-12 | Coherencia temporal | fechas de extracción, `_metadata`, `fecha_carga` | muestreo | P2 |
| DAT-13 | Granularidad | municipal vs comarcal vs área funcional vs CAE | tabla por variable | P1 |
| DAT-14 | Defendibilidad | qué conclusiones se sostienen y cuáles no | veredicto O1–O4 | P1 |

### TST — Tests (10)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| TST-01 | Suite completa | `pytest tests -q` con exit code y resumen | passed/failed/skipped exactos | P1 |
| TST-02 | Colectados vs ejecutados | 178 collected vs 177+1 skipped documentado | tabla | P1 |
| TST-03 | Requisito → test | 44 requisitos con test o "sin test" | matriz | P1 |
| TST-04 | Asserts triviales | `assert True`, `assert x is not None` sin dominio, tests que no afirman | lista con línea | P1 |
| TST-05 | Skips y xfail | 25 referencias; distinguir destructivos de cobertura ausente | tabla skip→motivo | P1 |
| TST-06 | Aislamiento | tests no contaminan `vivienda_euskadi`; 594/252 antes y después | conteos antes/después | P0 |
| TST-07 | Tests destructivos | `MONGO_ALLOW_DESTRUCTIVE=1`, colección de test, limpieza | código + ejecución controlada | P1 |
| TST-08 | Tests de integración | HDFS/Kafka con dobles, sin broker | 11 tests offline | P2 |
| TST-09 | Cobertura de código crítico | `pytest --cov` opcional en `storage/` y `analysis/` | % por módulo | P3 |
| TST-10 | Tests de regresión de hallazgos | cada P1 corregido tiene test que lo bloquea | lista hallazgo→test | P2 |

### INF — HDFS, Kafka e integración (10)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| INF-01 | HDFS originales | 352/356 ficheros, bytes y SHA | `LISTSTATUS` + 3 SHA | P1 |
| INF-02 | HDFS procesados | existencia de `/data/procesado`; si no, waiver explícito | `LISTSTATUS` o 404 | P1 |
| INF-03 | Recuperación | descarga de 1 fichero y comparación SHA | hash local == remoto | P1 |
| INF-04 | Estado resumible | `hdfs_upload_raw.json`, reanudación | fichero + prueba | P2 |
| INF-05 | Productor Kafka | `produce()` + Future/callback, topic y partición | código + offsets | P1 |
| INF-06 | Consumidor Kafka | `poll()` real, no `for msg in consumer`, descarte por SHA | código + lag 0 | P1 |
| INF-07 | Integración extremo a extremo | cadena hasta Mongo; rama Kafka→HDFS separada | diagrama + evidencia | P1 |
| INF-08 | Waiver | "solo raw" y "Kafka→HDFS" documentados con doble lectura | párrafo de defensa | P1 |
| INF-09 | Evidencia congelada | fecha, conteos, offsets; nunca usada para subir nota | anexo fechado | P2 |
| INF-10 | Reproducibilidad sin clúster | tests offline y stubs suficientes | ejecución | P2 |

### VIS — Visualización y presentación (10)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| VIS-01 | PNG desde Mongo | 12 PNG generados por `exportar_png_desde_mongo`, sin literales | código + ejecución | P1 |
| VIS-02 | Valores del gráfico vs CSV | cada PNG contrastado con su CSV de origen | 3 muestras numéricas | P1 |
| VIS-03 | Dashboards manuales | `dashboard*.html` con valores tecleados → no son evidencia RA4 | grep de literales | P1 |
| VIS-04 | Presentación HTML | `index.html` generado desde template y build | build reproducible + diff | P2 |
| VIS-05 | SVG de la presentación | 11 assets, valores y fuentes; `.bak` no usado | inventario + referencias | P2 |
| VIS-06 | PDF de presentación | `presentacion.pdf` generado y actualizado | mtime + páginas | P2 |
| VIS-07 | Capturas | 10 `shots/*.jpg` corresponden a las diapositivas | revisión visual | P3 |
| VIS-08 | Gráficos Tier | `chart_tierB_range`, `chart_mapa_tier`, `chart_effort_vs_n` | requisitos chart_* + datos | P2 |
| VIS-09 | Mapas | 252/252, capas etiquetadas, sin municipios inventados | conteo de features | P1 |
| VIS-10 | Coherencia visual | mismos colores/escalas entre mapa, ranking y tabla | revisión | P3 |

### DOC — Documentación (9)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| DOC-01 | Inventario numérico único | extraer todas las cifras activas y fijar el valor verdadero | `inventario_numerico_2026-11-07.md` | P2 |
| DOC-02 | Barrido de contradicciones | `grep` de 759/594/843, 356/354/352, 191/188/185, 178/177/151/145/136 | tabla valor→ficheros | P1 |
| DOC-03 | README vs realidad | conteos, comandos, estructura, estado por fase | checklist línea a línea | P1 |
| DOC-04 | Docs vigentes vs archivo | `docs/README.md` apunta a docs archivadas como núcleo | lista de enlaces muertos/obsoletos | P2 |
| DOC-05 | Enlaces internos | todos los `[..](..)` resuelven | script de comprobación | P3 |
| DOC-06 | Mermaid válido | sintaxis y render de los diagramas | render o parser | P3 |
| DOC-07 | Trazabilidad fuente→dato | cada cifra clave con fuente y fecha | tabla | P1 |
| DOC-08 | Documentos duplicados | `informe_auditoria_*` v1/v2/v3 conviviendo; decidir vigente | lista | P3 |
| DOC-09 | Terminología | `esfuerzo_joven_pct` vs `_18_34`, legacy 16–29 marcado | grep + glosario | P2 |

### SEC — Seguridad y configuración (7)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| SEC-01 | Secretos versionados | `git ls-files` de `.env`, `api.txt`, claves | lista vacía | P0 |
| SEC-02 | `.env` y `.gitignore` | `.env` ignorado, `.env.example` completo | diff de variables usadas vs declaradas | P2 |
| SEC-03 | Credenciales en código | grep de password/token/URI con usuario | lista | P0 |
| SEC-04 | IPs internas por defecto | 10.22.87.x / 192.168.x en código | lista + si es configurable | P2 |
| SEC-05 | Operaciones destructivas | `MONGO_ALLOW_DESTRUCTIVE`, `drop`, `delete_many` | gate en código, no solo convención | P0 |
| SEC-06 | Permisos de ficheros | `.env` no legible por todos (Windows ACL) | comprobación | P3 |
| SEC-07 | Datos personales | anuncios sin teléfonos/nombres/direcciones exactas | muestreo de campos | P1 |

### COD — Código y arquitectura (9)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| COD-01 | Duplicación | `_load_env` vs dotenv, canonicalize 4 veces, loaders repetidos | lista con líneas | P3 |
| COD-02 | Errores silenciados | 90 `except Exception`; cuáles ocultan fallos | tabla por criticidad | P1 |
| COD-03 | Dead code | `if False`, variables muertas, imports sin uso | `ruff`/`pyflakes` si disponible | P2 |
| COD-04 | Acoplamiento | `storage` importa `analysis`, rutas hardcodeadas | grafo de imports | P2 |
| COD-05 | Contratos de función | type hints, retornos, `None` implícitos | muestreo | P3 |
| COD-06 | Entrypoints | 2 entrypoints Mongo sin encadenar (`run_mongo_pipeline` vs `run_analisis_mongo`) | grep de llamadas | P1 |
| COD-07 | Configuración | YAML de fuentes vs URLs hardcodeadas | diff | P2 |
| COD-08 | Logs | `print` en librerías (43), ausencia de logging estructurado | conteo | P3 |
| COD-09 | Escalabilidad | memoria del uploader, `f.read()` de 114 MB, N+1 en lookups | revisión + medición | P2 |

### GIT — Repositorio e higiene (6)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| GIT-01 | Árbol de trabajo | 49 M + 3 ??; decidir si entran en el baseline o se estacionan | lista y diff | P1 |
| GIT-02 | Untracked sospechosos | `.svg.bak`, `scratchpad/*`, `vaultVivienda/` | `git status` + `.gitignore` | P2 |
| GIT-03 | Changes sin archivar | 21 en `openspec/changes/`, decidir merge/archivo | lista con estado | P2 |
| GIT-04 | Convención de commits | mensajes y `Verify:`; sin atribución de agente | `git log` | P3 |
| GIT-05 | Archivo vs vivo | `archive/` no referenciado por código activo | grep de imports | P2 |
| GIT-06 | Tamaño del repo | binarios, PDF, GIF/WebP, `.venv` fuera | `du` + `git ls-files` | P3 |

### DEF — Defensa y entregables (6)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| DEF-01 | Informe final | tablas, gráficos, conclusiones O1–O4, cifras vigentes | checklist | P1 |
| DEF-02 | Guion 12 min | cubre los 19 criterios v2 (+7 Tema 8) y el waiver | matriz criterio→minuto | P1 |
| DEF-03 | Demo | comandos ejecutables en vivo, sin dependencia oculta del clúster | ensayo seco | P1 |
| DEF-04 | Matriz O1–O4 | cada conclusión ligada a indicador de Mongo | tabla | P1 |
| DEF-05 | Nota defendible | puntuación 0/3/7/10 por criterio con evidencia | matriz final | P1 |
| DEF-06 | Preguntas del tribunal | top-10 preguntas con respuesta y evidencia | anexo | P2 |

---

## 3.bis Barridos exhaustivos (359 verificaciones)

Además de los 168 puntos de método de §3, la auditoría incluye un barrido con **una fila por elemento**: 40 fuentes (`SRC`), 41 scripts de extracción (`EXF`), 44 de transformación (`TRN`), 28 colecciones (`MCO`), 10 pipelines (`AGP`), 44 requisitos (`RQS`), 26 filas de rúbrica (19 v2 + 7 Tema 8) (`RUB`), 22 ficheros de test (`TSF`), 9 índices (`IDX-I`), 16 CSV (`CSV`), 12 PNG (`PNG`), 24 assets de presentación (`VIS-A`), 30 documentos (`DOC-F`) y 13 variables de entorno (`ENV`).

El detalle, con qué se verifica y cómo, está en **`plan_auditoria_v5_barridos_2026-11-07.md`**. Ese anexo es vinculante: un elemento sin fila no está auditado.

---

## 4. Matriz de trazabilidad rúbrica → auditoría

| # | Criterio (rúbrica) | Requisito(s) | Puntos de control | Nota umbral |
|---|---|---|---|---|
| 1 | BDA · Extracción API+scraping | `EXTRACCION-01/02` | EXT-01…05, CTR-06 | 10 |
| 2 | BDA · HDFS originales+procesados+recuperación | `HDFS-01` | INF-01…04 | 10 literal / 7 waiver |
| 3 | BDA · Kafka productor+consumidor | `KAFKA-01` | INF-05, INF-06 | 10 |
| 4 | BDA · Integración hasta MongoDB | `INTEGRACION-01` | INF-07, INF-08, MON-05 | 10 / 7 estricto |
| 5 | SBD · Integración de fuentes | `INTEGRACION-01`, `EXTRACCION-02` | MON-04, MON-05 | 10 |
| 6 | SBD · Construcción del conjunto | `MODELO-01` | MON-02, MON-03 | 10 |
| 7 | SBD · Limpieza ≥4 operaciones | `LIMPIEZA-01`, `TRANSFORM-01` | MON-09, TRF-09/10 | 10 |
| 8 | SBD · Automatización | `CARGA-SEGURA-01` | COD-06, MON-07, TRF-01/02 | 10 |
| 9 | SBD · Modelado + embedding/referencing | `MODELO-01` | MON-02, MON-03 | 10 |
| 10 | SBD · CRUD + comprobación | `PYMONGO-01` | MON-06 | 10 |
| 11 | SBD · Consultas ≥5 (anidado + 2 condiciones) | `CONSULTAS-01` | AGG-03, IDX-05 | 10 |
| 12 | SBD · Aggregation ≥3 / 5 etapas | `AGREGACION-01` | AGG-01, AGG-02 | 10 |
| 13 | SBD · Índices + explain | `INDICES-01` | IDX-01, IDX-02 | 10 |
| 14 | SBD · Consistencia atómica | `TRANSACCIONES-01` | MON-10 | 10 |
| 15 | SBD · Datos heterogéneos | `DATOS-HETEROGENEOS-01` | EXT-03, MON-02, TRF-06 | 10 |
| 16 | SBD · Automatización del análisis | `AUTOMATIZACION-ANALISIS-01` | REP-01, AGG-03 | 10 |
| 17 | SBD · ≥5 indicadores de 2+ fuentes | `INDICADORES-01` | AGG-08, DAT-11 | 10 |
| 18 | SBD · ≥3 municipios comparados | `RESPUESTA-01`, `CONCLUSION-01` | DEF-04, AGG-10 | 10 |
| 19 | SBD · ≥3 conjuntos para visualizar | `PREPARACION-VISUALIZACION-01` | VIS-01, REP-04 | 10 |
| 20 | Tema 8 · Modelado 15 % | `MODELO-01` | MON-01…04 | 10 |
| 21 | Tema 8 · CRUD/limpieza/consultas 15 % | `PYMONGO-01`, `CONSULTAS-01`, `LIMPIEZA-01` | MON-06/09, AGG-03 | 10 |
| 22 | Tema 8 · Aggregation 20 % | `AGREGACION-01` | AGG-01…05 | 10 |
| 23 | Tema 8 · Índices 15 % | `INDICES-01` | IDX-01…04 | 10 |
| 24 | Tema 8 · Transacciones 10 % | `TRANSACCIONES-01` | MON-10 | 10 |
| 25 | Tema 8 · PyMongo profesional 15 % | `PYMONGO-PRO-01` | COD-01…09, MON-12 | 10 |
| 26 | Tema 8 · Defensa 10 % | `ENTREGABLES-01` | DEF-01…06 | 10 |

**Regla de conversión:** un criterio solo sube a 10 si **todos** sus puntos asociados son `CUMPLE`; si uno es `CUMPLE CON SALVEDAD`, la nota máxima es 7 salvo waiver escrito; si alguno es `NO VERIFICABLE`, la nota es `PENDIENTE`, no 10.

---

## 5. Plan de ejecución

### 5.1 Fases y dependencias

```
F0 Preflight ──► F1 Contrato ──► F2 Requisitos
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
F3 Extracción+Transformación   F4 Mongo+Índices+Agg      F5 Tests+Código
        └──────────────────────────┼──────────────────────────┘
                                   ▼
                    F6 Datos+suficiencia+Reproducibilidad
                                   ▼
                    F7 Infra (HDFS/Kafka) + Vis + Docs + Seguridad
                                   ▼
                    F8 Git + Defensa + Comparativa v3/v4 → F9 Informe+Backlog → F10 Jueces
```

| Fase | Contenido | Puntos | Est. | Gate de salida |
|---|---|---|---:|---|
| F0 | Preflight y baseline | PRE-01…10 | 1,0 h | digest + accesos + inventario |
| F1 | Contrato y rúbrica | CTR-01…08 | 1,5 h | fidelidad X/Y + desvíos |
| F2 | Cobertura de requisitos | REQ-01…07 + RQS-01…44 | 2,5 h | matriz 44 requisitos |
| F3 | Extracción y transformación | EXT-01…12, TRF-01…12 + SRC-01…40, EXF-01…41, TRN-01…44 | 5,0 h | raw/manifest/SHA/DAG |
| F4 | Mongo, índices, agregaciones | MON-01…12, IDX-01…06, AGG-01…12 + MCO-01…28, AGP-01…10, IDX-I01…09 | 5,0 h | 14 colecciones + 10 pipelines |
| F5 | Tests y código | TST-01…10, COD-01…09 + TSF-01…22 | 3,0 h | suite + deuda |
| F6 | Datos y reproducibilidad | DAT-01…14, REP-01…08 + CSV-01…16, PNG-01…12 | 3,5 h | doble huella + cobertura |
| F7 | Infra, visual, docs, seguridad | INF-01…10, VIS-01…10, DOC-01…09, SEC-01…07 + VIS-A01…24, DOC-F01…30, ENV-01…13 | 5,0 h | waivers + contradicciones |
| F8 | Git, defensa, comparativa y veredicto | GIT-01…06, DEF-01…06 + RUB-01…26 | 3,0 h | tabla v3→v5 + checklist de entrega |
| F9 | Informe y backlog | redacción | 1,5 h | informe + backlog |
| F10 | Jueces independientes | 2 revisores | 1,5 h | confirmado/refutado |
| **Total** | | **527** | **~33 h** | |

### 5.2 Orquestación (máx. 3 agentes concurrentes)

| Ola | Agentes | Fases | Regla |
|---|---|---|---|
| 1 | 3 | F0, F1, F2 | Fundacional; nadie puntúa sin contrato ni baseline |
| 2 | 3 | F3, F4, F5 | Sin solape de ficheros; F4 es el más largo |
| 3 | 3 | F6, F7, F8 | F6 depende de F3+F4; F7 no toca código |
| 4 | 2 | F9, F10 | Jueces no leen transcripciones ajenas |

**Regla de conflicto:** si dos agentes necesitan el mismo fichero o la misma colección Mongo, se serializa. Toda la auditoría es read-only, así que el riesgo es de medición, no de escritura.

### 5.3 Checkpoints obligatorios

| Checkpoint | Cuándo | Qué se congela |
|---|---|---|
| CP1 | Tras F0 | commit, diff hash, inventario, accesos |
| CP2 | Tras F2 | matriz de requisitos cerrada |
| CP3 | Tras F4 | conteos Mongo y pipelines congelados |
| CP4 | Tras F6 | huella de doble ejecución |
| CP5 | Tras F8 | comparativa v3→v5 |
| CP6 | Cierre | digest idéntico + informe + backlog |

---

## 6. Entregables

| Fichero | Contenido |
|---|---|
| `openspec/audit/plan_auditoria_v5_2026-11-07.md` | Este plan |
| `openspec/audit/informe_auditoria_v5_2026-11-07.md` | 527 verificaciones con veredicto, evidencia triple, falsación y severidad |
| `openspec/audit/plan_auditoria_v5_barridos_2026-11-07.md` | Anexo con las 359 verificaciones elemento a elemento |
| `openspec/audit/barrido_elementos_2026-11-07.csv` | Volcado de las 359 filas con veredicto y evidencia |
| `openspec/audit/matriz_requisitos_2026-11-07.csv` | 44 requisitos × implementación × test × evidencia |
| `openspec/audit/matriz_fidelidad_rubrica_2026-11-07.md` | PDF/DOCX vs spec, celda a celda |
| `openspec/audit/inventario_numerico_2026-11-07.md` | Valor verdadero de cada cifra y dónde se cita |
| `openspec/audit/contradicciones_2026-11-07.md` | H1…H10 resueltas/confirmadas |
| `openspec/audit/inventario_fuentes_2026-11-07.md` | API/scraping/descarga + cobertura medida por join |
| `openspec/audit/backlog_v5_2026-11-07.md` | P0/P1/P2/P3 con riesgo y esfuerzo, separado del informe |
| `openspec/audit/evidencia/2026-11-07/` | Logs crudos de cada comando citado |

---

## 7. Criterios de aceptación de la auditoría

- [ ] Las 527 verificaciones tienen veredicto (`CUMPLE`, `CUMPLE CON SALVEDAD`, `NO CUMPLE`, `NO VERIFICABLE`, `N/A`) con evidencia triple.
- [ ] Los 359 elementos del anexo tienen fila propia con veredicto.
- [ ] Los 19 criterios v2 (+7 del Tema 8) tienen nota 0/3/7/10 o `PENDIENTE`, con falsación anotada.
- [ ] Los 44 requisitos de las specs están mapeados a implementación, test y evidencia.
- [ ] Las 10 hipótesis H1…H10 están resueltas con número y fuente.
- [ ] La suite se ejecutó con exit code y resumen exacto; los skips están justificados uno a uno.
- [ ] Doble ejecución del análisis con huella idéntica (o diferencia explicada).
- [ ] Digest del árbol idéntico al de apertura; cero escrituras en `data/` y Mongo.
- [ ] Informe y backlog separados; ningún arreglo aplicado durante la auditoría.
- [ ] Dos jueces independientes clasifican cada afirmación como confirmada/refutada/no verificable.

**Un solo criterio no cumplido invalida el cierre de la auditoría**, no la entrega del proyecto.

---

## 8. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| 49 cambios sin commitear | Baseline no reproducible | PRE-01: pinear commit + hash del diff; si cambia a mitad, reiniciar la fase afectada |
| Mongo cambia durante la auditoría | Conteos inconsistentes | Snapshot lógico al inicio (conteos + hashes de `_id`) y re-medida al cierre |
| Sin acceso a HDFS/Kafka | INF en `NO VERIFICABLE` | Evidencia congelada fechada; nunca para subir nota |
| Tests destructivos | Riesgo de borrar datos | `MONGO_ALLOW_DESTRUCTIVE` ausente por defecto; conteos 594/252 antes/después |
| Documentación desincronizada | Conclusiones erróneas | DOC-02: inventario numérico único antes de puntuar |
| Sesgo del auditor | Nota inflada | Umbral literal + falsación + 2 jueces ciegos |
| Volumen (527 verificaciones) | Fatiga y atajos | Lotes por dominio, checkpoint por fase, evidencia en logs |
| `except Exception` generalizado | Fallos ocultos | COD-02 prioriza los que envuelven carga/índices/escritura |
| Artefactos stale | Números "de memoria" | REP-03 compara mtime antes de citar cualquier PNG/CSV |
| Waivers verbales | Disputa en defensa | INF-08: frase escrita, doble lectura, fila propia en el informe |

---

## 9. Fuera de alcance

- Reparar cualquier hallazgo (va a `backlog_v5`, con autorización).
- Reescribir la rúbrica o "suavizar" umbrales.
- Subir procesados a HDFS o cambiar el waiver.
- Ejecutar extracción contra internet si no hay red de clase (se audita por código + artefactos).
- Auditar los proyectos Mongo ajenos (`tienda`, `certificacion*`) salvo para probar aislamiento.
- Valorar la defensa oral en vivo (solo el guion escrito).

---

## 10. Preguntas abiertas (no bloquean el plan)

1. ¿La auditoría se ejecuta con el árbol actual (49 M) o se estaciona en un commit limpio antes de empezar?
2. ¿Mongo se considera snapshot inmutable durante la auditoría o se permite que otro proceso escriba?
3. ¿Los 21 `openspec/changes` sin archivar se auditan como vigentes o se archivan antes?
4. ¿El informe final va en español (convención actual) o en inglés (convención SDD)?
5. ¿Se incluye `pytest --cov` o se deja como P3 opcional?
6. ¿La comparativa es contra v3, contra v4 o contra ambas?

---

## Anexo A — Comandos base de la auditoría

```bash
# Baseline
git rev-parse HEAD
git status --porcelain | tee openspec/audit/evidencia/2026-11-07/git_status.txt
git diff | sha256sum
git ls-files -s | sha256sum

# Entorno
.venv/Scripts/python.exe --version
.venv/Scripts/python.exe -m pip freeze | sha256sum

# Datos
find data/raw -type f | wc -l
find data/procesado -type f | wc -l
find data/resultados -type f | wc -l
wc -l docs/raw_manifest_sha256.txt

# Tests
.venv/Scripts/python.exe -m pytest tests -q; echo "EXIT=$?"
.venv/Scripts/python.exe -m pytest tests --collect-only -q | tail -3

# Mongo (solo lectura)
.venv/Scripts/python.exe -c "from pymongo import MongoClient; c=MongoClient('mongodb://localhost:27017'); db=c['vivienda_euskadi']; print(len(db.list_collection_names())); [print(n, db[n].estimated_document_count()) for n in sorted(db.list_collection_names())]"

# Análisis reproducible (escribe en data/resultados: coordinar con el usuario)
.venv/Scripts/python.exe analysis/run_analisis_mongo.py --salida /tmp/audit_v5_run1
.venv/Scripts/python.exe analysis/run_analisis_mongo.py --salida /tmp/audit_v5_run2
diff -r /tmp/audit_v5_run1 /tmp/audit_v5_run2
```

> Los comandos que escriben (`run_analisis_mongo.py`, tests destructivos) se ejecutan solo con autorización explícita y contra directorio temporal, nunca contra `data/resultados/` real.

---

## Anexo B — Plantilla de fila del informe

```markdown
| ID | Punto | Veredicto | Evidencia (comando + salida + fichero:línea) | Falsación | Sev. si falla |
|---|---|---|---|---|---|
| (ID) | Integridad referencial | CUMPLE | `db.anuncios.count_documents({"ubicacion.codigo_ine":{$exists:true}})` → 594/594; `storage/load_mongo.py:212` | Si <594 → NO CUMPLE | P1 |
```

## Anexo C — Plantilla de comparativa

```markdown
| Métrica | v3 (2026-11-06) | v4 (2026-11-07) | v5 (hoy) | Delta | Veredicto |
|---|---:|---:|---:|---:|---|
| Tests colectados | 145 | 151 (plan) | 178 | +27 | A confirmar |
| `anuncios` | 759 | — | 594 | −165 | Revisar narrativa |
```

---

*Relaciones: `openspec/specs/contrato-reto/spec.md` (verdad), `openspec/specs/*/spec.md` (44 requisitos), `openspec/audit/informe_auditoria_v3_2026-11-06.md` (baseline técnico), `openspec/audit/plan_auditoria_v4_2026-11-07.md` (baseline de método), `docs/contrato_datos_raw.md` (raw inmutable), `AGENT.md` (convenciones).*
