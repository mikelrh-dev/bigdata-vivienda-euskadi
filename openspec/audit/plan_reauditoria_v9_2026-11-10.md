# Plan de auditoría v9 — 2026-11-10

**Proyecto:** bigdata-vivienda-euskadi
**Naturaleza:** planificación. Este documento no ejecuta la auditoría: solo la diseña, la fundamenta y la deja lista para autorización.
**Contrato:** `openspec/specs/contrato-reto/spec.md` es la verdad. Si código y contrato discrepan, manda el contrato.
**Fuentes de la rúbrica:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (19 criterios) y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` (Tema 8, 7 criterios con pesos).
**Referencia inmediata:** `openspec/audit/plan_reauditoria_v8_2026-11-09.md`, `openspec/audit/v8_2026-11-09/`.

---

## 0. Estado de partida y deriva v8→v9

### 0.1 Baseline de partida (verificado ejecutando, no asumido)

| Elemento | Valor v9 (2026-11-10) | Fuente |
|---|---|---|
| HEAD | `47065f699b5c71244a3d2439c2a74cfb74790a42` | `git rev-parse HEAD` |
| Rama | `master` (origen `origin/master`) | `git branch` |
| Árbol de trabajo | 38 entradas: 19 staged, 15 modified, 4 untracked (46 ficheros untracked por `git ls-files --others`) | `git status --porcelain` |
| Ficheros tracked | 617 | `git ls-files \| wc -l` |
| Inventario v9 (excl. `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `graphify-out`) | **1.406 ficheros** | `find` + script `inv_v9.py` |
| Extensión | 437 `.md`, 249 `.json`, 214 `.csv`, **184 `.py`**, 115 `.html`, 49 `.zip`, 43 `.txt`, 37 `.png` | idem |
| `.py` activos (extract/transform/storage/analysis/scripts/tests) | **134** (41+42+7+7+7+30) | idem |
| `.py` históricos (`docs/archive` 35, `archive/` 12, `openspec/audit` 2, `docs/presentacion` 1) | 47 | idem |
| Tests | **237 colectados · 235 passed · 2 skipped** · 30 ficheros | `pytest tests` (ejecutado) |
| Gobernanza | **TODO OK**: 46 requisitos, 42 scripts `transform/`, 34 en DAG, 188 silver, 11 pipelines, 0 env sin declarar | `scripts/verificar_gobernanza.py` |
| `transform/run_all.py --check` | exit 0 | ejecutado |
| `scripts/gate_extremo_a_extremo.py --offline` | **OK** (354 SHA raw + 188 silver + 14 colecciones + 0 duplicados + lag 0); `PENDA-01` HDFS/Kafka vivo | ejecutado |
| `scripts/verificar_fase_datos.py` | exit 1 solo por **FAIL 07** conocido (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26) | ejecutado |
| `git diff --check` | limpio | ejecutado |
| Raw local | 356 ficheros recursivos = **354 canónicos + `.FROZEN` + `.gitkeep`**; `docs/raw_manifest_sha256.txt` = 354 SHA | `find` + `wc -l` |
| Silver | 191 ficheros, `manifest_sha256.txt` 188 entradas, 42 CSV | `find` + `wc -l` |
| Resultados | 58 ficheros; **8 `mongo_*.csv`** | `ls data/resultados` |
| MongoDB (local, lectura) | **30 colecciones** (16 vivas + 14 `__backup`); `anuncios` **594**; `municipios` 252; `vpo_municipal` 252; índices `idx_anuncios_ine_modalidad_precio`, `idx_anuncios_geo`, `idx_anuncios_portal_id`, `idx_anuncios_equipamiento`, `idx_municipios_territorio_nombre` | `pymongo` read-only |
| Comparativa | Bilbao **204**, Donostia **126**, Getxo **50**, Vitoria-Gasteiz **39** | `comparativa_3_municipios_mongo.csv` |
| HDFS centro (`10.22.87.215:50070`) | **NO alcanzable** (timeout; puerto cerrado) | sonda v9 |
| Kafka centro (`10.22.87.215:9092`) | **NO alcanzable** (`NoBrokersAvailable`) | sonda v9 |
| Mongo local (`localhost:27017`) | alcanzable | sonda v9 |

### 0.2 Deriva v8→v9 detectada

1. **Limpieza 2026-11-09 (post-v8), ya ejecutada.** `openspec/audit/limpieza_2026-11-09/reauditoria_ejecucion_2026-11-09.md` retiró **59 ficheros** (48 borrados, 11 archivados), eliminó el residuo DuckDB del flujo activo (4 scripts legacy, `tests/test_fuentes_validacion.py`, `scripts/validar_fuentes_nuevas.py`, `requirements-legacy.txt`) y alineó `README.md`, `AGENT.md`, `transform/run_all.py`, `scripts/verificar_gobernanza.py` y `docs/README.md`.
   - Efecto en cifras: suite **238 → 237 colectados** (236 → 235 passed); `transform/` **45 → 42 scripts** (34 en DAG); el universo pasa de 1.482 a **1.406 ficheros**.
   - Consecuencia: **v9 debe re-inventariar desde cero**, no heredar `cobertura_archivos_v8.csv` (su recuento queda desfasado en 76 ficheros y en los contadores de scripts/tests).
2. **Infraestructura centro no verificable en vivo.** v8 sí acreditó HDFS (`fileCount=352`, `data/procesado` 404, SHA idéntico) y Kafka (topic `vivienda_euskadi`, 1 partición, end 352, committed 352, lag 0). En v9 los puertos 50070 y 9092 no responden. El gate offline lo declara `PENDA-01`.
   - Consecuencia: C2 y C3 **no pueden revalidarse en vivo**; se usan como histórico v8 (clasificado, no reescrito) y la sonda v9 documenta la caída. **No se infla ni se degrada la nota por la caída de red**: la nota v8 se mantiene como referencia y el informe lo declara.
3. **H-02…H-07 siguen abiertos** (comprobado por `grep`, no por lectura completa). Los documentos activos conservan 759, 14+13, 10/9 pipelines, 4/5/6 CSV, 173/113/40 e IXSCAN 1. Detalle en el §5.
4. **H-08…H-13 siguen abiertos**: no se tocó código después de v8. `docs/archive/scratchpad/bom.json` conserva el BOM (`ef bb bf`) y no parsea como JSON estricto (H-13).
5. **Nuevo H-14 (higiene doc):** `docs/README.md` termina con un literal `HTMLEOF` en la línea 36, residuo de un heredoc. No afecta a ninguna cifra, pero es un defecto visible en un documento que se cita en la defensa.
6. **Nuevo H-15 (drift doc):** `docs/analisis_vault_vs_rubrica.md:35` sigue con «Bilbao 173, Donostia 113, Getxo 40, Vitoria 39» (variante de H-05).
7. **Sin regresión de código:** `git diff --check` limpio; suite verde; gobernanza OK; `run_all --check` 0; gate offline OK. La limpieza no rompió el flujo.

### 0.3 Consecuencias para el diseño de v9

- **Re-inventario obligatorio** (el universo cambió) y **re-conteo de tests** (237, no 238).
- **HDFS/Kafka en modo histórico + sonda**: el plan incluye un intento de sonda read-only y, si falla, registra la limitación sin bloquear la auditoría.
- **La deriva documental es el eje central**: 6 hallazgos P2 abiertos que no bajan la nota pero sí pueden tumbar una defensa. v9 los barrerá con precisión y los convertirá en unidades de trabajo con ficheros concretos.
- **No se ejecuta la auditoría en este documento**: solo se planifica. El baseline v9 ya está generado en `00_baseline_v9.md`.

---

## 1. Objetivo

Auditar el proyecto completo con **evidencia nueva** (no heredada de v8) y determinar:

1. Si el proyecto sigue defendible frente a los **19 criterios / 190 puntos** de la rúbrica v2 y frente a los **7 criterios / 100 %** del Tema 8.
2. Si la limpieza 2026-11-09 y los cambios pendientes han introducido regresiones en código, datos, tests, CI, Mongo o documentación.
3. El estado real de **H-02…H-07** (drift documental) y de **H-08…H-15**, con evidencia fichero:línea.
4. Qué puede **tumbar el tribunal** en una defensa real y qué respuesta escrita existe para cada ángulo.
5. Un plan de fix separado, con prioridad y dependencias, que **no se ejecuta** durante la auditoría.

**Fuera de alcance:** corregir nada, ejecutar `load_all`/`clean_all`/`run_analisis_mongo` completo, producir en Kafka, escribir en HDFS/Mongo/`data/`, instalar dependencias o hacer commit/push.

---

## 2. Universo y cobertura (nivel de control por capa)

Universo v9: **1.406 ficheros** (excluye `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `graphify-out`). `.venv` tiene 7.264 `.py` y 54 `.md` y **no se audita**: es entorno, no proyecto. Se incluyen `vaultVivienda`, `demo-mapa`, `demo-kpi`, `archive` y `docs/archive` como capas auxiliares con control de provenance y secretos.

| Capa | Ficheros v9 | Nivel de control |
|---|---:|---|
| Núcleo Python activo (`extract/` 41, `transform/` 42, `storage/` 7, `analysis/` 7, `scripts/` 7) | **104** | AST + lectura semántica + imports + entrypoints + IO/red/mongo/HDFS/Kafka. 100 % leídos. |
| Tests (`tests/`) | **30** | Mapa test → requisito/criterio; asserts; skips; mutaciones; dependencias ocultas. 100 %. |
| OpenSpec (`openspec/specs` 5, `openspec/changes` 255 `.md`, `openspec/audit` histórico, `openspec/project.md`) | **337** | Requisitos con ID, escenarios G/W/T, trazas, staleness, referencias muertas. Activos 100 %; histórico clasificado. |
| Documentación activa (`docs/*.md`) | **18** | Lectura semántica y contraste con código/datos; cifras; comandos; estados «pendiente». 100 %. |
| Config/CI/root (`.github/`, `config/`, `requirements.txt`, `README.md`, `AGENT.md`, `.env.example`) | ~12 | Secretos, env, dependencias, paths, gates. 100 %. |
| Datos (`data/` 605: raw 356, procesado 191, resultados 58) | **605** | Hash, manifest, cabecera, filas, nulos, rangos; raw byte a byte; HDFS si hay red. 100 % inventariado; raw y silver abierto; el resto integridad. |
| Auxiliares (`vaultVivienda/` 100, `archive/` 47, `demo-kpi/` 9, `demo-mapa/` 8, `scratchpad/`, `plan/`, `brief/` 2) | ~170 | Provenance, referencias, secretos, clasificación histórica. `brief/` se relee como fuente de rúbrica. |
| Binarios (`.zip` 49, `.png` 37, `.xlsx` 6, `.pdf` 4, `.jpg` 10, `.svg` 11, `.mp4`/`.webp`) | ~120 | Hash/metadatos/estructura; sin revisión visual salvo petición. |
| Histórico (`docs/archive/` 58 `.md` + `openspec/changes/archive` + `openspec/audit/archivado`) | ~150 | Clasificado, no reescrito; `grep` de cifras y referencias. |

**Definición de «tocado»:** código 100 % parseado y leído; docs activas 100 % contrastadas; datos con integridad y estructura verificadas; generados/archivados con provenance y sin secretos. No se promete lectura línea a línea de binarios ni del `data/raw` completo; sí de sus manifest, cabeceras y hashes.

**Exclusión explícita:** `.venv/**` (entorno), `__pycache__/**`, `.pytest_cache/**`, `graphify-out/**` (caché AST de Graphify, 0 `.py`), `.git/**`. Ninguno se audita ni se cuenta.

---

## 3. Reextracción de la rúbrica y matriz de trazabilidad

### 3.1 Rúbrica v2 (PDF) — 19 criterios, transcripción literal

Extraída con `read_file` (capa de texto) y cotejada con el contrato y con `matriz_rubrica_v8.md`. Sin diferencias literales respecto a v8.

**BDA — RA1. Gestión de soluciones y almacenamiento**

| # | Criterio | 0 | 3 | 7 | **10** |
|---|---|---|---|---|---|
| 1 | Extracción de datos mediante Python | No obtiene datos | Obtiene datos de una fuente manualmente | Automatiza una API o scraping | **Automatiza API y scraping** |
| 2 | Almacenamiento HDFS | No almacena datos | Crea directorios | Guarda y recupera archivos | **Organiza originales y procesados y demuestra su recuperación** |
| 3 | Kafka | No funciona | Crea un tópico | Envía mensajes con productor Python | **Productor y consumidor Python funcionan y procesan mensajes** |
| 4 | Integración | No hay integración | Los componentes funcionan por separado | Integra dos o más componentes | **Demuestra el flujo completo hasta MongoDB** |

**SBD — RA1. Adquisición, integración y tratamiento de datos — peso 46,7 %**

| # | Criterio | 0 | 3 | 7 | **10** |
|---|---|---|---|---|---|
| 5 | Integración de fuentes | No carga datos en MongoDB | Carga datos de 1 fuente | Carga datos de 2 fuentes diferentes | **Carga datos de 2 o más fuentes diferentes y las relaciona mediante al menos 1 campo común** |
| 6 | Construcción del conjunto de datos | No existe una estructura de datos funcional | Guarda todos los datos en una colección sin tratamiento | Utiliza 2 o más colecciones o documentos anidados/arrays | **Utiliza 2 o más colecciones y demuestra al menos 1 relación, embedding o referencia entre datos** |
| 7 | Limpieza y transformación con PyMongo | No realiza limpieza | Realiza 1 operación de limpieza o transformación | Realiza al menos 3 operaciones diferentes | **Realiza al menos 4 operaciones diferentes, incluyendo tratamiento de nulos/ausentes, duplicados y tipos/formato de datos** |
| 8 | Automatización | El tratamiento se realiza manualmente | Existe algún script Python parcial | Los datos se cargan y transforman mediante scripts Python | **Un script o conjunto de scripts permite ejecutar carga + limpieza + transformación, sin modificar manualmente los datos en MongoDB** |

**SBD — RA3. Gestión y almacenamiento en MongoDB — peso 13,3 %**

| # | Criterio | 0 | 3 | 7 | **10** |
|---|---|---|---|---|---|
| 9 | Modelado MongoDB | No crea una BD funcional | Crea al menos 1 colección | Utiliza 2 o más colecciones con tipos de datos adecuados | **Además, utiliza y demuestra al menos 1 decisión de embedding/referencing y explica por qué la ha utilizado** |
| 10 | CRUD con PyMongo | No utiliza PyMongo | Realiza insert | Realiza mediante PyMongo insert + update + delete + find | **Realiza las 4 operaciones y comprueba mediante código que el resultado es el esperado** |
| 11 | Consultas | No realiza consultas | Realiza consultas con igualdad | Utiliza al menos 4 tipos diferentes entre filtros, comparación, operadores lógicos, proyección, sort, arrays o campos anidados | **Realiza al menos 5 consultas útiles para el reto, incluyendo una con campos anidados o arrays y otra combinando 2 o más condiciones** |
| 12 | Aggregation Pipeline | No utiliza aggregate() | Pipeline con $match y/o $group | Crea al menos 2 pipelines y utiliza 4 etapas diferentes en total | **Crea al menos 3 pipelines que respondan preguntas del reto y utiliza 5 etapas diferentes, incluyendo $group y al menos una entre $lookup, $unwind o $facet** |
| 13 | Índices y rendimiento | No crea índices | Crea 1 índice | Crea un índice relacionado con una consulta y ejecuta explain() | **Compara mediante explain() la consulta antes/después o con/sin índice e identifica COLLSCAN/IXSCAN y totalDocsExamined** |
| 14 | Consistencia | No aplica lo trabajado | Solo describe el concepto | Identifica en su proyecto una operación atómica o un caso donde podría necesitarse una transacción | **Implementa una transacción real si su modelo la necesita; si no la necesita, demuestra mediante código una operación atómica y justifica técnicamente por qué una transacción sería innecesaria** |

**SBD — RA4. Procesamiento, análisis y preparación de resultados — peso 40 %**

| # | Criterio | 0 | 3 | 7 | **10** |
|---|---|---|---|---|---|
| 15 | Datos heterogéneos | No integra datos | Trabaja con una estructura simple | Utiliza arrays, documentos anidados o datos con estructuras diferentes | **Integra datos procedentes de fuentes con estructuras diferentes y los adapta mediante Python/PyMongo** |
| 16 | Automatización del análisis | Los resultados se obtienen manualmente | Ejecuta consultas manuales | Un script PyMongo ejecuta consultas/agregaciones | **Un script ejecuta automáticamente todos los análisis principales y devuelve resultados preparados para su representación** |
| 17 | Indicadores | No calcula indicadores | Calcula 1 indicador | Calcula al menos 3 indicadores relacionados con vivienda/emancipación | **Calcula al menos 5 indicadores, combinando información procedente de 2 o más fuentes** |
| 18 | Respuesta al reto | No responde a la pregunta | Presenta datos sin conclusión | Obtiene conclusiones para al menos 2 municipios o zonas | **Compara al menos 3 municipios/zonas y cada conclusión está vinculada a un indicador calculado con MongoDB** |
| 19 | Preparación para visualización | No prepara resultados | Copia resultados manualmente | Genera mediante PyMongo datos utilizables para gráficos | **Genera automáticamente mediante PyMongo al menos 3 conjuntos de resultados diferentes preparados para representar** |

### 3.2 Tema 8 (docx) — 7 criterios con pesos (evaluación separada)

Extraída con `read_file` (auto-extracción del docx). Pesos: **no se suman** a 46,7 / 13,3 / 40.

| Criterio | Peso | Qué se valora | Requisito |
|---|---:|---|---|
| Modelado documental | 15 % | Diseño coherente y decisiones justificadas según datos y patrones de acceso | `MODELO-01` |
| CRUD, limpieza y consultas | 15 % | Uso correcto de PyMongo, tipos, operadores, arrays y documentos embebidos | `PYMONGO-01`, `LIMPIEZA-01`, `CONSULTAS-01` |
| Aggregation | 20 % | Pipelines útiles, correctos, explicados y vinculados a la pregunta del reto | `AGREGACION-01` |
| Índices y rendimiento | 15 % | Índices justificados y evidencia con explain() | `INDICES-01` |
| Transacciones y consistencia | 10 % | Decisión razonada y, cuando proceda, implementación correcta | `TRANSACCIONES-01` |
| PyMongo profesional | 15 % | Organización, conexión, errores, resultados y reproducibilidad | `PYMONGO-PRO-01` |
| Defensa técnica | 10 % | Capacidad individual para explicar decisiones y comportamiento del sistema | `ENTREGABLES-01` + defensa oral |

Las secciones 5, 9, 10, 12, 4, 14, 15 y 17 del docx se mapean a `MODELO-01`, `INDICES-01`, `DISTRIBUIDA-01`, `PYMONGO-PRO-01` y `ENTREGABLES-01` (mapa trazable del contrato, líneas 222-267).

### 3.3 Los 46 requisitos con ID

`grep -rhoE "^### Requirement: [A-Z0-9-]+" openspec/specs/ | sort -u` devuelve **46** en 5 specs:

`AGREGACION-01`, `ARQUITECTURA-01`, `AUTOMATIZACION-ANALISIS-01`, `BOOTSTRAP-01`, `CAPAS-01`, `CARGA-SEGURA-01`, `COMPLEMENTARIOS-01`, `CONCLUSION-01`, `CONCLUSION-02`, `CONSULTAS-01`, `DATOS-HETEROGENEOS-01`, `DEDUP-01`, `DISTRIBUIDA-01`, `DOCS-01`, `ENTREGABLES-01`, `EXTRACCION-01`, `EXTRACCION-02`, `EXTRACCION-03`, `FORMATO-01`, `GATE-JOIN-01`, `HAB-01`, `HDFS-01`, `INDICADORES-01`, `INDICES-01`, `INTEGRACION-01`, `KAFKA-01`, `LIMPIEZA-01`, `MODELO-01`, `OUTLIER-01`, `PISOS-01..05`, `PREPARACION-VISUALIZACION-01`, `PYMONGO-01`, `PYMONGO-PRO-01`, `PYTHON-01`, `RAW-01`, `RENTA-01`, `RESPALDO-01`, `RESPUESTA-01`, `TRANSACCIONES-01`, `TRANSFORM-01`, `VALIDACION-01`, `VERIFICACION-01`.

Añadir las prohibiciones propias **P-01…P-08** (extensión del proyecto, no v2): P-01 compraventa como eje; P-02 simular valores; P-03 alquiler INE Euskadi; P-04 una sola etapa; P-05 gráficos tecleados; P-06 lenguaje distinto de Python; P-07 credenciales; P-08 marcar cubierto sin verificación.

### 3.4 Matriz de trazabilidad 19 criterios → requisito → evidencia → falsador

| # | Criterio (nivel 10) | Requisito | Evidencia v8 (histórico) | Evidencia v9 a revalidar | **Falsador v9** |
|---|---|---|---|---|---|
| 1 | Extracción API **y** scraping | `EXTRACCION-01/02/03` | 41 scripts en `extract/`; APIs y scrapers; `main_ingest.py` |árbol `extract/` 41 `.py`; `main_ingest.py`; tests focales | Que un extractor clave exija intervención manual o que `main_ingest` no orqueste |
| 2 | HDFS originales **y** procesados + recuperación | `HDFS-01` | raw 352 en HDFS, SHA idéntico; `procesado` 404; excepción declarada | **Red caída**: usar evidencia v8 como histórico + sonda v9 | Que `procesado` exista y se recupere, o que el waiver no esté escrito/enlazado |
| 3 | Kafka productor y consumidor procesan | `KAFKA-01` | topic 352/352, lag 0; `storage/kafka_raw_producer.py`, `kafka_hdfs_uploader.py` | **Red caída**: histórico v8 + sonda v9 + tests offline | Que el offset comprometido no avance o que solo haya mocks |
| 4 | Integración flujo completo a MongoDB | `INTEGRACION-01`, `GATE-JOIN-01` | `gate_extremo_a_extremo --offline` OK; `run_mongo_pipeline --dry-run` OK; 11/11 pipelines | gate offline + dry-run + lectura de `scripts/run_mongo_pipeline.py` | Que el flujo a Mongo dependa de un paso manual |
| 5 | Integración de fuentes (2+ y campo común) | `INTEGRACION-01` | `load_all()` 14 colecciones; `$lookup` por `codigo_ine` 594/594 | recuento de colecciones + `$lookup` vivo | Que los `codigo_ine` no casen |
| 6 | Construcción (2+ colecciones + relación) | `MODELO-01` | `municipios` embebe demografía/empleo; `anuncios.ubicacion` anidado; referencia `codigo_ine` | esquema vivo + consultas que usen anidamiento | Que el anidamiento no se use en consultas |
| 7 | Limpieza PyMongo (4+ ops) | `LIMPIEZA-01`, `TRANSFORM-01` | `clean_mongo.py`: canonicalize, mark_nulls, resolve_duplicates, convert_types | AST + tests `test_clean_mongo.py` | Que una operación sea alias de otra |
| 8 | Automatización carga+limpieza+transformación | `INTEGRACION-01`, `LIMPIEZA-01`, `TRANSFORM-01` | `scripts/run_mongo_pipeline.py` `--dry-run` OK | dry-run + lectura del orquestador | Que falte un paso o haya edición manual |
| 9 | Modelado + embedding/referencing explicado | `MODELO-01` | `docs/modelo_mongodb.md` (esquema correcto, cifras desfasadas H-02) | esquema vivo + documento tras barrido H-02 | Que la justificación no corresponda al esquema |
| 10 | CRUD 4 ops + comprobación en código | `PYMONGO-01` | `clean_mongo.py` demo + `test_mongo.py` asserts | tests focales + AST | Que el test solo compruebe que no lanza |
| 11 | Consultas (5 útiles, anidada/array, 2+ condiciones) | `CONSULTAS-01` | `mongo_queries.py` 30 funciones | AST + ejecución read-only con `limit` | Que las 5 sean variantes de igualdad |
| 12 | Aggregation (3+ pipelines, 5 etapas, `$group` + lookup/unwind/facet) | `AGREGACION-01` | 11/11 pipelines; `$lookup`, `$unwind`, `$group`, `$match`, `$addFields`, `$project`, `$sort`, `$limit` | `PIPELINE_ORDER` 11 + ejecución con `limit` | Que `$lookup/$unwind` sean decorativos |
| 13 | Índices (explain antes/después, COLLSCAN/IXSCAN, totalDocsExamined) | `INDICES-01` | índice ESR; explain 68/68 para la consulta de Bilbao; docs dicen IXSCAN 1 (H-03) | `explain()` vivo antes/después | Que los números estén hardcodeados o el índice no se use |
| 14 | Consistencia (atómica + justificación) | `TRANSACCIONES-01` | `storage/mongo.py` `find_one_and_update` + test; transacción rechazada en standalone | test + lectura de `mongo.py` | Que el test no compruebe el valor nuevo |
| 15 | Datos heterogéneos adaptados | `DATOS-HETEROGENEOS-01` | 41 extractores CSV/JSON/HTML/XLSX/ZIP/SHP/GTFS; `unificar_anuncios.py` | árbol `extract/` + `normalizar_json_crudos.py` | Que cada fuente se cargue sin normalización común |
| 16 | Automatización del análisis | `AUTOMATIZACION-ANALISIS-01` | `run_analisis_mongo.py` 11 pipelines, 8 CSV + PNG; argparse dice 9+5 (H-11) | `PIPELINE_ORDER` + `EXPORTS_8` | Que algún análisis principal se haga a mano |
| 17 | Indicadores (5+, 2+ fuentes) | `INDICADORES-01` | `docs/matriz_indicadores.md`; `$lookup` a 6+ colecciones | documento tras barrido H-04 | Que dos indicadores sean el mismo con otro nombre |
| 18 | Respuesta al reto (3+ municipios, conclusión ↔ indicador) | `CONCLUSION-01`, `RESPUESTA-01` | `comparativa_3_municipios_mongo.csv` 204/126/50/39; `docs/conclusiones_municipios.md` | CSV vivo + documento | Que las conclusiones no citen indicador |
| 19 | Preparación visualización (3+ conjuntos) | `PREPARACION-VISUALIZACION-01` | 8 CSV `mongo_*` + 28+8 PNG; `docs/README.md` dice 4 (H-06) | `EXPORTS_8` + `data/resultados` | Que los CSV estén tecleados o los PNG no vengan de Mongo |

### 3.5 Regla de puntuación (anti-inflado)

- Cada criterio se puntúa por **evidencia ejecutable o fichero:línea**, nunca por la cifra que afirma un documento.
- **C2 HDFS** se puntúa con la misma regla que v8: **7/10** si `procesado` sigue 404, con waiver declarado. La caída de red en v9 **no baja ni sube** la nota: se acredita con el histórico v8 y se declara la limitación.
- **C13** se acredita con `explain()` vivo (68/68). El «IXSCAN 1» de los documentos es un filtro distinto; el criterio se cumple.
- Separar explícitamente **«criterio cumple»** de **«documentación lo cuenta bien»**. La deriva documental no baja la nota, pero sí alimenta el ángulo de defensa (§6).

---

## 4. Fases e hipótesis falsables

Cada fase tiene hipótesis falsables y comandos reales en modo solo lectura. Ningún comando escribe en `data/`, Mongo, HDFS o Kafka.

### Fase 0 — Baseline y congelación (COMPLETADA)

Ejecutada por el agente planificador. Entregable: `00_baseline_v9.md`. Comandos: `git status/log/rev-parse`, `find`, `du`, `wc -l`, `pytest tests`, `verificar_gobernanza.py`, `run_all.py --check`, `gate_extremo_a_extremo.py --offline`, `verificar_fase_datos.py`, sondas Mongo/HDFS/Kafka. **Gate A**: si raw/HDFS/Mongo no coinciden con el baseline conocido, parar y reportar. En v9 la red centro no coincide (caída) → se documenta y se continúa con modo histórico.

### Fase 1 — Rúbrica y contrato (hipótesis H1)

- **H1 — Integridad de la rúbrica:** el PDF y el docx vigentes son la fuente v2 y el contrato los transcribe sin desviación literal. **Falsador:** una tabla del contrato que no aparezca literal en el PDF/docx, o un peso distinto (46,7 / 13,3 / 40; Tema 8 15/15/20/15/10/15/10).
- **H2 — Trazabilidad:** los 46 requisitos cubren los 19 criterios y los 7 de Tema 8. **Falsador:** un criterio sin requisito o un requisito huérfano.
- Comandos: `read_file brief/RETO 1Evaluacion SBD-BDAv2.pdf`; `read_file brief/Tema_8_...docx`; `grep -n "Peso en la" contrato`; `grep -rhoE "^### Requirement:" openspec/specs/`.
- Salida: `rubrica_reextracta_v9.md`, `cotejo_fuentes_v9.md`, `matriz_trazabilidad_v9.md`.

### Fase 2 — Auditoría estática integral (hipótesis H3–H8)

- **H3 — Código:** los 104 `.py` activos parsean, no tienen `except` vacíos, no escriben en raw sin guard, no dejan credenciales. **Falsador:** un `open(...,"w")` sobre `data/raw` sin `assert_raw_writable`; un `except:` que trague errores; un secreto en texto plano.
- **H4 — Tests:** los 237 tests son trazables a requisitos y no mutan producción. **Falsador:** un test sin assert, un skip injustificado, un test que escriba en `data/`.
- **H5 — OpenSpec:** 46 requisitos con escenarios G/W/T y referencias vivas. **Falsador:** un escenario sin THEN, un enlace muerto, un cambio cerrado con verify-report vacío.
- **H6 — Datos:** raw 354 SHA coincide con manifest; silver 188; 8 CSV `mongo_*` con filas coherentes. **Falsador:** un SHA distinto, un CSV con cabecera desplazada, un nulo donde el contrato exige dato.
- **H7 — Config/CI:** `.env.example` declara todas las variables; el workflow no requiere red. **Falsador:** una variable usada y no declarada; un paso de CI que falle sin red.
- **H8 — Auxiliares:** `vaultVivienda`, `demo-*`, `archive`, `docs/archive` no tienen secretos ni referencias que engañen. **Falsador:** una credencial, un literal `HTMLEOF`, una referencia a un fichero inexistente.
- Comandos: `python -c "import ast; ast.parse(...)"` (sin escribir `.pyc`); `grep -rn "except:"`; `grep -rn "open(.*['\"]w" --include='*.py'`; `grep -rn "TODO\|FIXME\|XXX"`; `grep -rn "\.env\|api.txt"`; `python -m compileall -q` solo si se acepta escribir `__pycache__` (alternativa: `ast.parse`); `git diff --check`.

### Fase 3 — Verificación dinámica y de datos (hipótesis H9–H12)

- **H9 — Suite:** 235 passed / 2 skipped; focales verdes. **Falsador:** un fallo nuevo tras la limpieza.
- **H10 — Mongo:** 594 anuncios, 252 municipios, 252 vpo; 11 pipelines responden con `limit`; explain COLLSCAN→IXSCAN. **Falsador:** un pipeline que no ejecute, un conteo distinto, un explain sin IXSCAN.
- **H11 — Gobernanza/gates:** TODO OK; `run_all --check` 0; gate offline OK. **Falsador:** un gate que falle o un conteo que no cuadre.
- **H12 — Infra viva:** HDFS/Kafka responden. **Falsador (confirmado en v9):** puertos cerrados. La hipótesis queda **falsada** y se documenta: no se revalida en vivo, se usa el histórico v8.
- Comandos: `pytest tests`; `pytest tests/test_raw_inmutable.py tests/test_vpo_municipal.py tests/test_mongo.py -q`; `.venv/Scripts/python.exe -c` con `pymongo` (`countDocuments`, `aggregate([...{"$limit":2}])`, `explain`); `curl -s --max-time 25 ".../webhdfs/v1/...?op=GETFILESTATUS"`; `kafka` metadata/offsets sin producir; `scripts/verificar_fase_datos.py`.

### Fase 4 — Contrato, rúbrica y barrido documental (hipótesis H13–H15)

- **H13 — Nota:** el proyecto sostiene **187/190** (98,4 %), con C2 en 7 por HDFS procesado. **Falsador:** evidencia nueva que tumbe un criterio (p. ej. un pipeline que no responda, un `$lookup` que no case).
- **H14 — Deriva doc:** H-02…H-07 siguen abiertos y son localizables fichero:línea. **Falsador:** un documento que ya esté corregido (entonces el hallazgo se cierra) o un documento con más cifras desfasadas que las registradas.
- **H15 — Nuevos residuos:** no hay más Haití que H-14 (`HTMLEOF`) y H-15 (173 en `analisis_vault_vs_rubrica.md`). **Falsador:** otro residuo de heredoc o cifra desfasada.
- Comandos: `grep -rn` con los patrones de cifras; `git diff --stat`; lectura de los 18 `.md` activos; `wc -l` de los 8 CSV; `cat comparativa_3_municipios_mongo.csv`.

### Fase 5 — Adversarial y defensa (hipótesis H16–H18)

- **H16 — Adversarial:** un revisor hostil no encuentra un fallo que v8 no viera. **Falsador:** cualquier inconsistencia código↔contrato↔doc.
- **H17 — Tribunal:** las preguntas que pueden tumbar la defensa tienen respuesta escrita con evidencia. **Falsador:** una pregunta sin respuesta o con respuesta que cita una cifra falsa.
- **H18 — Reproducibilidad:** un entorno limpio puede ejecutar el flujo. **Falsador:** una dependencia no declarada (como el caso DuckDB ya limpiado), un paso manual, un path absoluto.
- Skills: `doubt-driven-development`, `code-review-and-quality`, `security-and-hardening`.
- Salida: `angulo_defensa_v9.md`, `simulacro_tribunal_v9.md`.

### Fase 6 — Informe y gate (hipótesis H19)

- **H19 — Cierre:** 100 % del universo clasificado, 100 % de `.py` parseados, 100 % de tests mapeados, 19 criterios con evidencia, 46 requisitos con escenarios, 7 criterios Tema 8 mapeados. **Falsador:** cualquier cobertura < 100 %.
- Salida: `matriz_rubrica_v9.md`, `hallazgos_v9.csv`, `backlog_v9.md`, `informe_reauditoria_v9.md`, `inventario_archivos_v9.csv`, `cobertura_archivos_v9.csv`, `evidencia/`.

---

## 5. Barrido de deriva documental H-02…H-07

Comprobado por `grep` en el baseline v9 (no por lectura completa). **Los seis siguen abiertos**: los documentos no se han tocado desde v8.

| ID | Sev. | Criterio | Estado v9 | Evidencia v9 (fichero:línea) | Unidad de trabajo |
|---|---|---|---|---|---|
| H-02 | P2 | C9/C12 | **ABIERTO** | `docs/modelo_mongodb.md:11` (759), `:40` (424/759), `:111` (14+13, 10 pipelines), `:115` (173/113/40, 5 CSV), `:129` (explain 759/1), `:160`, `:162`, `:180` (5 CSV) | W4.1 |
| H-03 | P2 | C13 | **ABIERTO** | `README.md:287`, `AGENT.md:4`, `docs/arquitectura_datos.md:69`, `docs/guion_defensa.md:10,33,51`, `docs/guion_defensa_12min.md:175`, `docs/modelo_mongodb.md:129-132` (IXSCAN 1) | W4.2, W4.3 |
| H-04 | P2 | C12/C16/C19 | **ABIERTO** | `docs/matriz_indicadores.md:19,32` (10 pipelines), `docs/informe_final.md:27,145` (5 CSV, 10 pipelines), `docs/informe_capacidad_mongo.md:3,8,14,48`, `docs/preguntas_analisis_profesional.md:84,91,99,120`, `docs/guion_defensa_12min.md:35,143,171,222` (14 colecciones, 10 pipelines, 6 CSV) | W4.1, W4.2 |
| H-05 | P2 | C18 | **ABIERTO** | `docs/modelo_mongodb.md:115`, `docs/matriz_indicadores.md:32`, `docs/preguntas_analisis_profesional.md:84,91,120`, `docs/informe_capacidad_mongo.md:87,88,94,95,99`, `docs/analisis_vault_vs_rubrica.md:35` | W4.1, W4.2, W4.3 |
| H-06 | P2 | C19 | **ABIERTO** | `docs/README.md:34` («la única evidencia válida son los 4 CSV») vs `README.md` y `EXPORTS_8` (8 CSV) | W4.3 |
| H-07 | P2 | Contexto | **ABIERTO** | `openspec/project.md:6` (136 tests, 185 silver, 9 pipelines, 5 CSV), `:68` (759), `:75` (VM pendiente), `:80` (9 pipelines) | W4.3 |

**Nuevos:**

| ID | Sev. | Criterio | Estado v9 | Evidencia | Unidad |
|---|---|---|---|---|---|
| H-14 | P3 | Estructura doc | **NUEVO/ABIERTO** | `docs/README.md:36` termina en literal `HTMLEOF` (heredoc) | W4.3 |
| H-15 | P3 | C18 | **NUEVO/ABIERTO** | `docs/analisis_vault_vs_rubrica.md:35` (173/113/40) | W4.3 |

**Cifras vigentes que deben sustituir a las anteriores:** 594 anuncios; 16 vivas + 14 `__backup` = 30 colecciones; 11 pipelines; 8 CSV `mongo_*`; 204/126/50/39; explain IXSCAN 68/68; 237 tests (235 passed, 2 skipped); 188 silver; 354 SHA raw.

---

## 6. Ángulo de defensa: qué puede tumbar el tribunal

1. **«Enseñe el flujo completo hasta MongoDB en vivo.»** Riesgo: la red centro está caída y el gate vivo es `PENDA-01`. Respuesta: gate offline + `run_mongo_pipeline --dry-run` + evidencia v8 en vivo (clasificada como histórica) + declaración honesta de la limitación. **Acción:** no prometer en vivo si no hay red; tener el comando exacto y el log v8 a mano.
2. **«¿Dónde están los procesados en HDFS?»** Riesgo: C2 = 7/10, waiver declarado. Respuesta: excepción escrita + recuperación demostrada de un raw + organización de originales. **Acción:** enlazar el waiver desde `README.md` y el guion, no solo desde el histórico de auditoría (H-01).
3. **«Sus documentos dicen 759 anuncios y 10 pipelines; su Mongo dice 594 y 11. ¿Cuál es la verdad?»** Riesgo: H-02…H-07. Respuesta: el código y los datos son la verdad; los documentos están en corrección. **Acción:** cerrar W4.1–W4.3 **antes** de la defensa; si no, declarar explícitamente que las cifras vigentes son 594/11/8 y que los documentos están desfasados.
4. **«Explique el índice y el explain.»** Riesgo: los documentos dicen IXSCAN 1; la medición reproducible es 68/68. Respuesta: el número depende del filtro; mostrar `explain_before_after()` en vivo y explicar ESR. **Acción:** H-03 cerrado y guion con la medición actual.
5. **«¿Por qué no usa transacciones?»** Riesgo: en standalone no se pueden demostrar. Respuesta: atomicidad documental con `find_one_and_update` + test + justificación técnica + ejemplo plausible de transacción con replica set. **Acción:** tener el test y la explicación preparados (C14 ya está cubierto).
6. **«¿Ha simulado salarios o alquileres?»** Riesgo: P-02. Respuesta: fuentes reales (Eustat, INE, Lanbide, OVJ, portales); proxy de renta e imputación comarcal **declarados**; sin valores simulados. **Acción:** tener la matriz de fuentes y el contrato a mano.
7. **«¿Sus gráficos salen de Mongo o están tecleados?»** Riesgo: P-05 y los HTML manuales. Respuesta: 8 CSV `mongo_*` auto-generados + PNG desde `exportar_png_desde_mongo`; los HTML son manuales y están marcados como no evidencia RA4. **Acción:** H-06 cerrado para que el índice no diga «4 CSV».
8. **«¿Puede reproducir el proyecto desde cero?»** Riesgo: dependencias no declaradas. Ya limpiado el caso DuckDB; el plan vuelve a comprobar `requirements.txt`/`uv.lock` vs imports. **Acción:** H18.
9. **«¿Por qué el FAIL 07 de paro-cero?»** Riesgo: parece un error oculto. Respuesta: está documentado, no enmascarado, con tres municipios y tasa no nula; no se tocan los datos para forzar el gate. **Acción:** declararlo antes de que pregunten.
10. **«¿Quéjustifica el canónico 18-34?»** Riesgo: pregunta de fondo. Respuesta: ponderación por anchura Eustat CAE 2024 con la fórmula del contrato y subgrupos declarados como escalares CAE. **Acción:** no confundir con renta municipal por edad.

---

## 7. Unidades de trabajo para orquestación (máx. 3 concurrentes, ventana deslizante)

Modelo: **3 agentes concurrentes**; cuando uno termina, se lanza el siguiente de la cola respetando `depende_de`. Los ficheros de salida son disjuntos por unidad, por lo que no hay conflictos de escritura. Las unidades marcadas como «misma carpeta» no deben solaparse.

Fase 0 (hecha por el planificador) y Fase 6 (depende de todas) son secuenciales. El detalle completo está en `unidades_trabajo_v9.csv`.

| ID | Fase | Descripción | Capa | Criterios | Solo lectura | Est. | Depende de | Agente |
|---|---|---|---|---|---|---|---|---|
| W0.1 | 0 | Baseline read-only y congelación | todo | — | sí | M | — | planificador (HECHA) |
| W1.1 | 1 | Reextraer rúbrica PDF 19 criterios y cotejar con contrato | brief + contrato | 1–19 | sí | M | — | A |
| W1.2 | 1 | Enumerar 46 requisitos y mapear a 19 criterios + Tema 8 | openspec/specs | 1–19, Tema 8 | sí | M | — | A |
| W1.3 | 1 | Cotejo literal PDF/docx vs contrato (desviaciones) | brief + contrato | todos | sí | S | W1.1 | A |
| W2.1 | 2 | Auditoría estática `extract/` (41 `.py`) | extract | 1, 15 | sí | L | — | B1 |
| W2.2 | 2 | Auditoría estática `transform/` (42 `.py`) | transform | 6, 7, 15 | sí | L | — | B2 |
| W2.3 | 2 | Auditoría estática `storage/`+`analysis/`+`scripts/` (21 `.py`) | storage/analysis/scripts | 2,3,4,10–14,16–19 | sí | L | — | B3 |
| W2.4 | 2 | Auditoría de tests `tests/` (30) y mapa test→requisito | tests | todos | sí | M | — | B4 |
| W3.1 | 3 | Verificación dinámica: suite, focales, gates, CI | tests + gates | todos | sí | M | W2.4 | C1 |
| W3.2 | 3 | Mongo read-only: conteos, 11 pipelines con limit, explain | Mongo | 5,6,9–14,16–19 | sí | M | — | C2 |
| W3.3 | 3 | Datos: raw/silver/CSV, HDFS/Kafka sonda (documentar caída) | data | 2,3,19 | sí | M | — | C3 |
| W4.1 | 4 | Barrido doc: `modelo_mongodb`, `matriz_indicadores`, `informe_capacidad_mongo` | docs | 9,12,17,18 | sí | M | W1.2 | D1 |
| W4.2 | 4 | Barrido doc: `informe_final`, `preguntas_analisis`, `guion_defensa_12min`, `guion_defensa` | docs | 12,13,16,18 | sí | M | W1.2 | D2 |
| W4.3 | 4 | Barrido doc: `docs/README`, `README`, `AGENT`, `openspec/project`, `arquitectura_datos`, `analisis_vault_vs_rubrica` | docs+root+openspec | 2,3,6,13,19 | sí | M | W1.2 | D3 |
| W5.1 | 5 | Pase adversarial: buscar el fallo que v8 no vio | todo | todos | sí | M | W2.1–W2.4 | E1 |
| W5.2 | 5 | Simulacro de tribunal y ángulo de defensa | todo | todos | sí | M | W3.1–W4.3 | E2 |
| W6.1 | 6 | Matriz rúbrica v9 + hallazgos + backlog + informe | openspec/audit/v9 | 1–19 | sí | L | W1–W5 | F1 |

**Ventana deslizante sugerida:**
- **Jornada 1:** W1.1/W1.2/W1.3 (A) + W2.1/W2.2/W2.3 (B1–B3) + W2.4 (B4) → cuando B1 termina, entra W3.2; cuando B2 termina, entra W3.3; cuando B3 termina, entra W3.1.
- **Jornada 2:** W4.1/W4.2/W4.3 (D1–D3) en paralelo (ficheros disjuntos); cuando D1 termina, entra W5.1; cuando D2 termina, entra W5.2.
- **Cierre:** W6.1 (F1) tras todas.

**Reglas de conflicto:** W4.1/W4.2/W4.3 son las únicas que escriben en `docs/`; sus ficheros de salida están particionados y no se solapan. Ninguna otra unidad escribe en `docs/`. Las unidades de código son de solo lectura y no escriben en el repo (salen informes a `openspec/audit/v9_2026-11-10/`).

---

## 8. Skills a usar

| Skill | Uso en v9 |
|---|---|
| `pdf-extraction` | Reextraer y cotejar el PDF de la rúbrica (con `read_file` o `pdfplumber`; `pdfplumber` no está instalado y **no se instala** sin autorización: se usa `read_file`/`pdftotext`). |
| `spec-driven-development` | Contrato, requisitos, escenarios y trazabilidad. |
| `code-review-and-quality` | Revisión multi-eje de código y tests. |
| `doubt-driven-development` | Pase adversarial e hipótesis alternativas. |
| `test-driven-development` | Calidad de tests y cobertura de requisitos. |
| `security-and-hardening` | Secretos, red, paths, escrituras. |
| `documentation-and-adrs` | Deriva doc y decisiones. |
| `systematic-issue-triage` | Clasificación de hallazgos y backlog. |
| `exploratory-data-analysis` | Integridad de CSV, nulos, rangos y conteos. |
| `ci-cd-and-automation` | Workflow offline y gates. |

No se usan skills de ML/modelado, ni `browser-testing` (no hay UI web auditada).

---

## 9. Guardrails (heredadas de v8, vigentes)

1. No escribir en `data/raw`, `data/procesado`, `data/resultados`, Mongo, HDFS ni Kafka.
2. No ejecutar `load_all`, `clean_all`, `run_analisis_mongo` completo ni el productor Kafka.
3. No borrar ni mover ficheros fuera de `openspec/audit/v9_2026-11-10/`.
4. No instalar dependencias (si falta `pdfplumber`, usar `read_file` o `pdftotext`; `pypdf` y `pdftotext` sí están disponibles).
5. No commit ni push.
6. Cualquier prueba de escritura usa `tempfile`, copia o `monkeypatch`; nunca el raw real.
7. Si un gate vivo no tiene modo read-only, no se ejecuta; se documenta la limitación.
8. Los históricos no se reescriben: se clasifican.
9. **Nuevo:** la red centro está caída. No se considerará un fallo del proyecto; se documenta y se usa el histórico v8.
10. **Nuevo:** la limpieza 2026-11-09 ya retiró ficheros; no se revertirá ni se re-moverá. Los `git status` con 19 staged / 15 modified / 4 untracked son el estado de partida y no se tocan.

---

## 10. Criterios de aceptación

- **Cobertura:** 100 % de los **1.406** ficheros inventariados y clasificados; 100 % de los **104** `.py` activos parseados y leídos; 100 % de los **237** tests mapeados; 100 % de los **46** requisitos con escenario; 100 % de los **19** criterios con evidencia; **7** criterios Tema 8 mapeados.
- **Datos:** raw 354 SHA = manifest; silver 188 = manifest; 8 CSV `mongo_*` con filas coherentes; Mongo 594/252/252; comparativa 204/126/50/39.
- **Infra:** HDFS/Kafka documentados como no alcanzables; gate offline OK; `PENDA-01` declarado.
- **Suite:** 235 passed / 2 skipped; gobernanza TODO OK; `run_all --check` 0; `git diff --check` limpio; solo FAIL 07 conocido en fase de datos.
- **Nota:** se sostiene **187/190 (98,4 %)** con C2 = 7 por HDFS procesado; si aparece evidencia nueva que tumbe un criterio, se re-puntúa y se declara.
- **Deriva doc:** H-02…H-07 cerrados o declarados abiertos con plan de fix; H-14 y H-15 incorporados.
- **Veredicto:** PASS / PASS CON RESERVAS / FAIL, con puntuación y reservas explícitas.
- **Ningún fix aplicado sin autorización.**

---

## 11. Opciones de autorización

No se ejecutará ninguna fase hasta recibir una de estas respuestas:

- **«Autorizo la auditoría v9 completa»** → fases 1–6, solo lectura y pruebas, sin mutar datos. Incluye el barrido documental y el ángulo de defensa, pero **no aplica fixes**: solo los propone.
- **«Autorizo solo el barrido documental H-02…H-07»** → fases 1, 4 y 6 acotada; no se toca código ni infra.
- **«Autorizo solo la revalidación de datos y Mongo»** → fases 3 y 6 acotada; no se tocan docs.
- **«Ajusta el plan»** → se modifica antes de ejecutar.

Cualquier fix (documental o de código) se ejecutará en una **sesión separada**, con su propia autorización y su verify-report.
