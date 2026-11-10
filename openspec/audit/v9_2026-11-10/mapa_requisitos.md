# Mapa de requisitos v9 — 46 requisitos → 19 criterios rúbrica + 7 criterios Tema 8

**Unidad:** W1.2 (auditoría v9, read-only) · **Fecha:** 2026-11-10
**Naturaleza:** solo lectura. No se modificó código, datos, Mongo, HDFS ni Kafka; no hubo commit/push; no se instalaron dependencias. Única escritura: este fichero.
**Entrada:** `openspec/specs/*/spec.md` (5 ficheros, 1.850 líneas), `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (123 líneas extraídas), `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` (266 líneas extraídas), `AGENT.md`, `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`.
**Referencia de formato:** `openspec/audit/v8_2026-11-09/matriz_rubrica_v8.md` (misma numeración C1–C19).

---

## 1. Resumen ejecutivo

- **46 requisitos con ID canónico** (`[A-Z]+-\d{2}`) + **4 requisitos con ID no canónico** (`chart_*`, en minúscula) = **50 encabezados `### Requirement:`**. El gate de gobernanza solo audita 46. Ver hallazgo **H-M1**.
- **Los 19 criterios de la rúbrica tienen todos al menos un requisito.** Ningún criterio de las 19 tablas del PDF queda huérfano.
- **Los 7 criterios del Tema 8 (docx §16) tienen todos al menos un requisito.** Ninguno huérfano.
- **26 de los 46 requisitos canónicos no tienen un criterio C1–C19 directo**: son requisitos/objetivos adicionales del PDF (FORMATO-01, PYTHON-01, COMPLEMENTARIOS-01), extensiones propias declaradas (OUTLIER-01, DEDUP-01, PISOS-*, RAW-01, CARGA-SEGURA-01, RENTA-01, HAB-01, CAPAS-01, VERIFICACION-01, ARQUITECTURA-01, GATE-JOIN-01, RESPUESTA-01, CONCLUSION-02, PISOS-05, BOOTSTRAP-01, DOCS-01) o respaldos del docx no ponderados en §16 (DISTRIBUIDA-01, VALIDACION-01). Todos apoyan al menos un criterio o un objetivo del PDF.
- **Ningún P0/P1.** No se detuvo la ejecución.

---

## 2. Los 19 criterios de la rúbrica (PDF)

Transcripción literal del PDF en `openspec/specs/contrato-reto/spec.md:29-82`; verificado contra el PDF en 2026-11-10.

| ID | Criterio (nivel 10, literal) | PDF línea | Peso |
|---|---|---|---|
| **C1** | Extracción de datos mediante Python — «Automatiza API y scraping» | 76 | BDA RA1 |
| **C2** | Almacenamiento HDFS — «Organiza originales y procesados y demuestra su recuperación» | 77 | BDA RA1 |
| **C3** | Kafka — «Productor y consumidor Python funcionan y procesan mensajes» | 78 | BDA RA1 |
| **C4** | Integración — «Demuestra el flujo completo hasta MongoDB» | 79 | BDA RA1 |
| **C5** | Integración de fuentes — «Carga datos de 2 o más fuentes diferentes y las relaciona mediante al menos 1 campo común» | 91 | SBD RA1 46,7 % |
| **C6** | Construcción del conjunto de datos — «Utiliza 2 o más colecciones y demuestra al menos 1 relación, embedding o referencia entre datos» | 92 | SBD RA1 46,7 % |
| **C7** | Limpieza y transformación con PyMongo — «Realiza al menos 4 operaciones diferentes, incluyendo tratamiento de nulos/ausentes, duplicados y tipos/formato de datos» | 93 | SBD RA1 46,7 % |
| **C8** | Automatización — «Un script o conjunto de scripts permite ejecutar carga + limpieza + transformación, sin modificar manualmente los datos en MongoDB» | 94 | SBD RA1 46,7 % |
| **C9** | Modelado MongoDB — «Además, utiliza y demuestra al menos 1 decisión de embedding/referencing y explica por qué la ha utilizado» | 104 | SBD RA3 13,3 % |
| **C10** | CRUD con PyMongo — «Realiza las 4 operaciones y comprueba mediante código que el resultado es el esperado» | 105 | SBD RA3 13,3 % |
| **C11** | Consultas — «Realiza al menos 5 consultas útiles para el reto, incluyendo una con campos anidados o arrays y otra combinando 2 o más condiciones» | 106 | SBD RA3 13,3 % |
| **C12** | Aggregation Pipeline — «Crea al menos 3 pipelines que respondan preguntas del reto y utiliza 5 etapas diferentes, incluyendo $group y al menos una entre $lookup, $unwind o $facet» | 107 | SBD RA3 13,3 % |
| **C13** | Índices y rendimiento — «Compara mediante explain() la consulta antes/después o con/sin índice e identifica COLLSCAN/IXSCAN y totalDocsExamined» | 108 | SBD RA3 13,3 % |
| **C14** | Consistencia — «Implementa una transacción real si su modelo la necesita; si no la necesita, demuestra mediante código una operación atómica y justifica técnicamente por qué una transacción sería innecesaria» | 109 | SBD RA3 13,3 % |
| **C15** | Datos heterogéneos — «Integra datos procedentes de fuentes con estructuras diferentes y los adapta mediante Python/PyMongo» | 119 | SBD RA4 40 % |
| **C16** | Automatización del análisis — «Un script ejecuta automáticamente todos los análisis principales y devuelve resultados preparados para su representación» | 120 | SBD RA4 40 % |
| **C17** | Indicadores — «Calcula al menos 5 indicadores, combinando información procedente de 2 o más fuentes» | 121 | SBD RA4 40 % |
| **C18** | Respuesta al reto — «Compara al menos 3 municipios/zonas y cada conclusión está vinculada a un indicador calculado con MongoDB» | 122 | SBD RA4 40 % |
| **C19** | Preparación para visualización — «Genera automáticamente mediante PyMongo al menos 3 conjuntos de resultados diferentes preparados para representar» | 123 | SBD RA4 40 % |

---

## 3. Los 7 criterios del Tema 8 (docx §16)

Transcripción literal del docx §16 en `openspec/specs/contrato-reto/spec.md:88-98`; verificado contra el docx en 2026-11-10.

| ID | Criterio Tema 8 | Peso | docx línea | Qué se valora |
|---|---|---|---|---|
| **T1** | Modelado documental | 15 % | 232-234 | Diseño coherente y decisiones justificadas según datos y patrones de acceso |
| **T2** | CRUD, limpieza y consultas | 15 % | 235-237 | Uso correcto de PyMongo, tipos, operadores, arrays y documentos embebidos |
| **T3** | Aggregation | 20 % | 238-240 | Pipelines útiles, correctos, explicados y vinculados a la pregunta del reto |
| **T4** | Índices y rendimiento | 15 % | 241-243 | Índices justificados y evidencia con explain() |
| **T5** | Transacciones y consistencia | 10 % | 244-246 | Decisión razonada y, cuando proceda, implementación correcta |
| **T6** | PyMongo profesional | 15 % | 247-249 | Organización, conexión, errores, resultados y reproducibilidad |
| **T7** | Defensa técnica | 10 % | 250-252 | Capacidad individual para explicar decisiones y comportamiento del sistema |

Los pesos Tema 8 **no se suman** a 46,7 % / 13,3 % / 40 % (declarado en `contrato-reto/spec.md:86`).

---

## 4. Los 46 requisitos con ID canónico → criterios

Orden por spec. «C» = criterio rúbrica (19); «T» = criterio Tema 8 (7). «—» = sin criterio directo de las 19 (ver §6).

### 4.1 `contrato-reto/spec.md` (2)

| ID | Texto (resumen fiel) | Spec:línea | C | T |
|---|---|---|---|---|
| ENTREGABLES-01 | Entregar código organizado, datos originales en HDFS y MongoDB, esquema de arquitectura, informe con gráficos y tablas, y demostración con explicación de decisiones; frase contractual «HDFS centro + Mongo local sin Docker Compose en el repo» | contrato-reto/spec.md:129-163 | — (apoya C18/C19; entregables PDF 53-57) | T7 |
| ARQUITECTURA-01 | Invariantes globales: sin Docker; HDFS solo raw 352; Kafka→HDFS, nunca Kafka→Mongo; sin imputar comarcal/IDW como municipal; Nivel y Tier ortogonales | contrato-reto/spec.md:165-174 | — (apoya C4) | T7 (parcial) |

### 4.2 `extraccion-datos/spec.md` (12)

| ID | Texto (resumen fiel) | Spec:línea | C | T |
|---|---|---|---|---|
| EXTRACCION-01 | Automatiza **a la vez** API y scraping; guarda respuesta original junto con la forma parseada | extraccion-datos/spec.md:35-57 | **C1** | — |
| EXTRACCION-02 | Combina al menos 3 fuentes independientes; ninguna insustituible; fallo registrado sin abortar | extraccion-datos/spec.md:59-73 | **C1** (apoya C5) | — |
| FORMATO-01 | Todo dato en JSON o CSV con metadatos de fuente, fecha y n_registros | extraccion-datos/spec.md:75-87 | — (requisito BDA PDF 36) | — |
| COMPLEMENTARIOS-01 | Salarios, población y ≥1 indicador más; paro Lanbide 252/252; sin imputar comarcal/IDW | extraccion-datos/spec.md:89-126 | — (objetivo 2 PDF 22; apoya C17) | — |
| PYTHON-01 | Todos los programas en Python, ejecutables desde venv dedicado | extraccion-datos/spec.md:128-141 | — (requisito PDF 19, 47) | — |
| GATE-JOIN-01 | MUST NOT crear extractor nuevo sin join real contra `dim_municipios` 252; provenance + manifest | extraccion-datos/spec.md:143-160 | — (extensión propia) | — |
| EXTRACCION-03 | Ubicación real de pisos desde subtítulo/título; `codigo_ine` no se propaga sin coincidencia textual | extraccion-datos/spec.md:162-178 | — (apoya C7/C15) | — |
| PISOS-01 | Orden subtítulo→título→gazetteer→fallback→cuarentena; `municipio_busqueda` nunca como ubicación | extraccion-datos/spec.md:180-189 | — (apoya C7/C15) | — |
| PISOS-02 | `geo_invalida=True` y cuarentena reversible fuera de `dim_municipios`/Euskadi o sin subtítulo | extraccion-datos/spec.md:191-206 | — (apoya C7/C15) | — |
| OUTLIER-01 | Filtra `precio_m2` [3,50] y `superficie_m2` [10,500]; excluye IQR del precio medio; `habitaciones` entero | extraccion-datos/spec.md:208-224 | — (apoya C7) | — |
| DEDUP-01 | Dedup por `property_fingerprint`; primer anuncio conserva, resto con motivo `duplicado_fingerprint` | extraccion-datos/spec.md:226-242 | — (apoya C7) | — |
| VERIFICACION-01 | Gate FAIL 06 (`594/843`) y FAIL 07 (paro-cero Aramaio/Gaintza/Usansolo) no enmascarados; huella SHA-256 | extraccion-datos/spec.md:244-270 | — (apoya C8; meta P-08) | T6 (parcial) |

### 4.3 `almacenamiento-y-streaming/spec.md` (3)

| ID | Texto (resumen fiel) | Spec:línea | C | T |
|---|---|---|---|---|
| HDFS-01 | Originales en rutas separadas + recuperación con tamaño en bytes igual; SHOULD procesados en HDFS | almacenamiento-y-streaming/spec.md:35-60 | **C2** | — |
| KAFKA-01 | Productor y consumidor Python que funcionen offline y procesen mensajes reales; SHOULD vivo sobre broker real | almacenamiento-y-streaming/spec.md:62-95 | **C3** | — |
| INTEGRACION-01 | 2+ fuentes relacionadas por ≥1 campo común; SHOULD flujo completo en vivo hasta MongoDB | almacenamiento-y-streaming/spec.md:97-146 | **C4**, **C5**, **C8** | — |

### 4.4 `mongodb-y-analisis/spec.md` (19)

| ID | Texto (resumen fiel) | Spec:línea | C | T |
|---|---|---|---|---|
| MODELO-01 | Responder en `docs/modelo_mongodb.md` las 7 preguntas docx §5; ≥1 decisión embedding/referencing justificada | mongodb-y-analisis/spec.md:25-41 | **C6**, **C9** | T1 |
| PYMONGO-01 | Sustituir `except Exception` por tipadas con log; comprobar `matched_count`/`modified_count`/`deleted_count` | mongodb-y-analisis/spec.md:44-58 | **C10** | T2 |
| CARGA-SEGURA-01 | Staging + `<name>__backup` + rename atómico; no ventana vacía; índices tras el swap | mongodb-y-analisis/spec.md:61-112 | — (apoya C8) | T6 |
| CONSULTAS-01 | ≥4 tipos (nivel 7) / ≥5 consultas con anidada/array y 2+ condiciones (nivel 10); familias Tema 8 | mongodb-y-analisis/spec.md:114-176 | **C11** | T2 |
| AGREGACION-01 | Mediana winsorizada 1–99 + exclusión IQR; `pipeline_tier_por_municipio` 252 filas; ranking `n≥30` | mongodb-y-analisis/spec.md:178-236 | **C12** | T3 |
| RAW-01 | Raw inmutable; HDFS solo raw 352; Kafka→HDFS; recarga staging+backup+rename | mongodb-y-analisis/spec.md:238-248 | — (apoya C2, C3) | — |
| LIMPIEZA-01 | `$unset` explícito con `deleted_count`; función canónica única; conteo de anuncios | mongodb-y-analisis/spec.md:251-270 | **C7** | T2 |
| TRANSFORM-01 | ≥3 operaciones (nivel 7) / ≥4 con nulos, duplicados y tipos (nivel 10) | mongodb-y-analisis/spec.md:273-295 | **C7**, **C8** | T2 |
| INDICES-01 | `explain("executionStats")` COLLSCAN→IXSCAN con `totalDocsExamined=1`; geo/multikey/parcial documentados | mongodb-y-analisis/spec.md:298-321 | **C13** | T4 |
| TRANSACCIONES-01 | Commit/abort multidocumento en `vivienda_euskadi_test` o justificación READ; no tocar prod | mongodb-y-analisis/spec.md:324-336 | **C14** | T5 |
| DISTRIBUIDA-01 | Explicar replica sets y sharding (PRIMARY/SECONDARY, oplog, concerns, ARBITER, mongos, shard key) | mongodb-y-analisis/spec.md:339-357 | — (respaldo docx §10, no ponderado en §16) | T7 (parcial) |
| PYMONGO-PRO-01 | Proyecto Python mantenible: conexión reutilizable, URI configurable, cursores, upsert, bulk_write, README | mongodb-y-analisis/spec.md:359-376 | — | **T6** |
| VALIDACION-01 | SHOULD validación de esquema (JSON Schema) si aporta valor, o justificar | mongodb-y-analisis/spec.md:378-388 | — (respaldo §15; apoya T2) | T2 (parcial) |
| RESPALDO-01 | Backups de `municipios`/`indicadores`; Point GeoJSON documentados; listing 16 colecciones | mongodb-y-analisis/spec.md:390-402 | — (apoya T6) | T6 |
| RENTA-01 | `validar_renta.py` como paso de `run_all.py` o justificación firmada | mongodb-y-analisis/spec.md:403-422 | — (apoya C17) | — |
| PISOS-03 | Conteos honestos `n_anuncios=594`, `n_anuncios_raw=843`; sin imputación IDW/comarcal | mongodb-y-analisis/spec.md:424-439 | — (apoya C17, C18) | — |
| PISOS-04 | Paro Lanbide 252/252; carga staging+backup+rename; doble ejecución con SHA idéntico | mongodb-y-analisis/spec.md:441-457 | — (apoya C17) | — |
| CAPAS-01 | Tres capas de precio (oficial 159 / IDW 93 / contexto 252) con `metodo_imputacion` e `is_imputed` | mongodb-y-analisis/spec.md:477-499 | — (apoya C17, C19) | — |
| HAB-01 | `pipeline_habitaciones_por_municipio` (9 filas, n=201/n_precio=200), pipeline nº 11, CSV canónico | mongodb-y-analisis/spec.md:501-530 | — (apoya C12, C17) | T3 (parcial) |

### 4.5 `presentacion-de-resultados/spec.md` (10 canónicos + 4 `chart_*`)

| ID | Texto (resumen fiel) | Spec:línea | C | T |
|---|---|---|---|---|
| DATOS-HETEROGENEOS-01 | Integra estructuras diferentes y las adapta mediante Python/PyMongo | presentacion-de-resultados/spec.md:60-84 | **C15** | — |
| AUTOMATIZACION-ANALISIS-01 | Un script ejecuta automáticamente todos los análisis principales y devuelve resultados preparados | presentacion-de-resultados/spec.md:86-112 | **C16** | — |
| INDICADORES-01 | 5 indicadores non-legacy con pipeline Mongo o silver justificado; CSV 253/253/3 con huella | presentacion-de-resultados/spec.md:114-137 | **C17** | — |
| PREPARACION-VISUALIZACION-01 | ≥3 conjuntos automáticos para representar; nunca tecleados; regenerables | presentacion-de-resultados/spec.md:139-174 | **C19** | — |
| CONCLUSION-01 | Guion Tema 8 de 1 página con 10 criterios y lagunas; 16–29 legacy; canónico 18–34 | presentacion-de-resultados/spec.md:176-201 | **C18** | T7 |
| RESPUESTA-01 | Compara 4 robustos (204/126/50/39) con paro no nulo o silver; matriz O1–O4; corrección 759→594 en 4 docs | presentacion-de-resultados/spec.md:203-237 | **C18** (extensión propia) | — |
| CONCLUSION-02 | Tiers A/B/C/D; conciliación 62/252 vs `n_precio=7`; ranking solo `n≥30` | presentacion-de-resultados/spec.md:239-286 | **C18** (extensión propia) | — |
| PISOS-05 | Esfuerzo municipal citado literalmente «252 contextual sobre 159» | presentacion-de-resultados/spec.md:288-304 | **C18** (extensión propia) | — |
| BOOTSTRAP-01 | Bootstrap con `n_larga_solo_vivienda` 67/60/39/37; IC95 Bilbao y Getxo | presentacion-de-resultados/spec.md:356-365 | **C18** (extensión propia) | — |
| DOCS-01 | Corrección 759→594 en `build_presentacion.py:218` y `docs/presentacion/README.md:62`; frase ortogonal Nivel/Tier | presentacion-de-resultados/spec.md:367-376 | **C19** (extensión propia) | — |
| **chart_tierB_range** ⚠ | 3 barras (Sopela 19, Zarautz 15, Santurtzi 11) con min-max y mediana temporal vs larga | presentacion-de-resultados/spec.md:306-315 | **C19** (fuera del conteo canónico) | — |
| **chart_mapa_tier** ⚠ | Coroplético 4 niveles, capas 159/93/252, `<2 MB`, sin duplicado g1/A1 | presentacion-de-resultados/spec.md:317-337 | **C19** (fuera del conteo canónico) | — |
| **chart_effort_vs_n** ⚠ | Burbuja solo Tier A (4 puntos) con banda `n_insuficiente` | presentacion-de-resultados/spec.md:339-354 | **C19** (fuera del conteo canónico) | — |
| **chart_habitaciones_medianas** ⚠ | Tres series (temporal/larga/habitaciones); solo Bilbao 96 y Donostia 66 firmes | presentacion-de-resultados/spec.md:378-403 | **C19** (fuera del conteo canónico) | — |

⚠ = ID en minúscula; no captado por el gate de gobernanza (H-M1).

---

## 5. Mapa inverso: criterio → requisitos

### 5.1 Rúbrica (19)

| Criterio | Requisitos directos | ¿Cubierto? |
|---|---|---|
| C1 Extracción API y scraping | EXTRACCION-01, EXTRACCION-02 | ✅ |
| C2 HDFS originales/procesados/recuperación | HDFS-01, RAW-01 | ✅ |
| C3 Kafka productor y consumidor | KAFKA-01, RAW-01 | ✅ |
| C4 Integración flujo completo a MongoDB | INTEGRACION-01 | ✅ |
| C5 Integración de fuentes (2+ y campo común) | INTEGRACION-01, MODELO-01 | ✅ |
| C6 Construcción del conjunto (2+ colecciones + relación) | MODELO-01 | ✅ |
| C7 Limpieza y transformación PyMongo (4+ ops) | LIMPIEZA-01, TRANSFORM-01 | ✅ |
| C8 Automatización (carga+limpieza+transformación) | INTEGRACION-01, LIMPIEZA-01, TRANSFORM-01, CARGA-SEGURA-01 | ✅ |
| C9 Modelado MongoDB (embedding/referencing) | MODELO-01 | ✅ |
| C10 CRUD con PyMongo (4 ops comprobadas) | PYMONGO-01 | ✅ |
| C11 Consultas (5 útiles, anidada/array, 2+ condiciones) | CONSULTAS-01 | ✅ |
| C12 Aggregation (3+ pipelines, 5 etapas) | AGREGACION-01 | ✅ |
| C13 Índices y rendimiento (explain antes/después) | INDICES-01 | ✅ |
| C14 Consistencia (transacción o atómica justificada) | TRANSACCIONES-01 | ✅ |
| C15 Datos heterogéneos | DATOS-HETEROGENEOS-01 | ✅ |
| C16 Automatización del análisis | AUTOMATIZACION-ANALISIS-01 | ✅ |
| C17 Indicadores (5+, 2+ fuentes) | INDICADORES-01 | ✅ |
| C18 Respuesta al reto (3+ municipios, conclusión↔indicador) | CONCLUSION-01, RESPUESTA-01, CONCLUSION-02, PISOS-05, BOOTSTRAP-01, DOCS-01 | ✅ |
| C19 Preparación para visualización (3+ conjuntos) | PREPARACION-VISUALIZACION-01, chart_tierB_range, chart_mapa_tier, chart_effort_vs_n, chart_habitaciones_medianas, DOCS-01 | ✅ |

**Criterios de la rúbrica sin requisito: ninguno (0/19).**

### 5.2 Tema 8 (7)

| Criterio | Requisitos directos | ¿Cubierto? |
|---|---|---|
| T1 Modelado documental 15 % | MODELO-01, CONSULTAS-01 (parcial), VALIDACION-01 | ✅ |
| T2 CRUD, limpieza y consultas 15 % | PYMONGO-01, LIMPIEZA-01, TRANSFORM-01, CONSULTAS-01, VALIDACION-01 (parcial) | ✅ |
| T3 Aggregation 20 % | AGREGACION-01, HAB-01 (parcial) | ✅ |
| T4 Índices y rendimiento 15 % | INDICES-01 | ✅ |
| T5 Transacciones y consistencia 10 % | TRANSACCIONES-01 | ✅ |
| T6 PyMongo profesional 15 % | PYMONGO-PRO-01, CARGA-SEGURA-01, RESPALDO-01, VERIFICACION-01 (parcial) | ✅ |
| T7 Defensa técnica 10 % | ENTREGABLES-01, CONCLUSION-01, DISTRIBUIDA-01 (parcial), ARQUITECTURA-01 (parcial) | ✅ |

**Criterios Tema 8 sin requisito: ninguno (0/7).**

---

## 6. Requisitos sin criterio directo de las 19 tablas

26 de 46 canónicos + 4 `chart_*` no tienen un criterio C1–C19 directo. Se agrupan por naturaleza:

| Naturaleza | Requisitos | Apoyan a |
|---|---|---|
| Requisitos/objetivos del PDF fuera de las 19 tablas | FORMATO-01 (BDA PDF 36), PYTHON-01 (PDF 19, 47), COMPLEMENTARIOS-01 (objetivo 2 PDF 22) | C1, transversal, C17 |
| Invariantes y meta-reglas | ARQUITECTURA-01, GATE-JOIN-01, VERIFICACION-01 | C4, C8 |
| Endurecimientos de extracción/limpieza | EXTRACCION-03, PISOS-01, PISOS-02, OUTLIER-01, DEDUP-01 | C7, C15 |
| Endurecimientos Mongo/almacenamiento | RAW-01, CARGA-SEGURA-01, DISTRIBUIDA-01, VALIDACION-01, RESPALDO-01, RENTA-01, PISOS-03, PISOS-04, CAPAS-01, HAB-01 | C2/C3, C8, C17, C12, T6, T2 |
| Endurecimientos de presentación/conclusión | RESPUESTA-01, CONCLUSION-02, PISOS-05, BOOTSTRAP-01, DOCS-01 | C18, C19 |
| IDs no canónicos (fuera del conteo) | chart_tierB_range, chart_mapa_tier, chart_effort_vs_n, chart_habitaciones_medianas | C19 |

Ninguno es huérfano en absoluto: cada uno refuerza un criterio o un objetivo del PDF. El contrato lo declara en `contrato-reto/spec.md:219-221` (extensión propia) y `contrato-reto/spec.md:222-267` (mapa docx).

---

## 7. Prohibiciones propias P-01 … P-08

Fuente: `openspec/specs/contrato-reto/spec.md:298-312`. No son criterios v2 ni pesos Tema 8.

| ID | Prohibición | Cobertura en requisitos | Verificación observable |
|---|---|---|---|
| **P-01** | Usar compraventa como eje cuando el criterio evalúa alquiler | Sin Requirement con ID; invariante en ARQUITECTURA-01 y canónico 18–34 (`contrato-reto/spec.md:333-366`) | El eje es alquiler Eustat; no compraventa |
| **P-02** | Simular valores de salario, alquiler o población | EXTRACCION-01, COMPLEMENTARIOS-01, CAPAS-01 | `metodo_imputacion`/`is_imputed` por fila; escenario «El salario está presente y es real» (extraccion-datos/spec.md:100-106) |
| **P-03** | Usar el alquiler del INE para Euskadi (devuelve `null`) | Sin Requirement con ID; canónico 18–34 y COMPLEMENTARIOS-01 | El alquiler proviene de Eustat; INE alquiler Euskadi = `null` |
| **P-04** | Contar con una sola etapa un criterio de agregación compleja | AGREGACION-01 | Mediana winsorizada + exclusión IQR + tier + ranking (mongodb-y-analisis/spec.md:178-236) |
| **P-05** | Generar gráficos con valores tecleados a mano | PREPARACION-VISUALIZACION-01, INDICADORES-01, chart_* | Escenario «Sin valores inventados» (presentacion-de-resultados/spec.md:350-354) |
| **P-06** | Escribir en lenguaje distinto de Python | PYTHON-01 | 184 `.py`; escenario «Un script reproduce una fuente» (extraccion-datos/spec.md:136-141) |
| **P-07** | Dejar credenciales en el repositorio (`.env`, `api.txt`) | Sin Requirement con ID | `scripts/verificar_gobernanza.py:60-68` comprueba 0 env usadas sin declarar en `.env.example` |
| **P-08** | Marcar un criterio cubierto sin verificación observable | VERIFICACION-01 (gate con huella SHA-256) | `scripts/verificar_gobernanza.py` (TODO OK); escenarios con salida literal |

**P-01, P-03 y P-07 no tienen Requirement con ID.** No es un hueco de cobertura (los tres están verificados por código/gate), pero el mapa no puede citar un ID para ellos; W1.3 debe decidir si se formalizan como requisito o se declaran como invariante/guardia sin ID.

---

## 8. Hallazgos

### H-M1 · P3 · 50 encabezados `### Requirement:` vs 46 IDs canónicos: 4 requisitos escapan al gate de gobernanza

**Evidencia (ejecutada):**

```
$ grep -cE '^### Requirement: ' openspec/specs/*/spec.md
openspec/specs/almacenamiento-y-streaming/spec.md: 3
openspec/specs/contrato-reto/spec.md: 2
openspec/specs/extraccion-datos/spec.md: 12
openspec/specs/mongodb-y-analisis/spec.md: 19
openspec/specs/presentacion-de-resultados/spec.md: 14      → total 50

$ grep -rhoE "^### Requirement: [A-Z0-9_-]+" openspec/specs/ | wc -l
46
```

`scripts/verificar_gobernanza.py:35-38` filtra con `re.search(r"([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{2})", line)`, que exige **mayúscula inicial**. Los 4 requisitos `chart_tierB_range`, `chart_mapa_tier`, `chart_effort_vs_n` y `chart_habitaciones_medianas` (presentacion-de-resultados/spec.md:306, 317, 339, 378) empiezan en minúscula y no matchean. El docstring del propio script (`scripts/verificar_gobernanza.py:5`) dice «46 cabeceras de requisito», pero hay 50.

**Impacto:** el gate imprime `TODO OK: 46 requisitos` sin auditar 4 requisitos que tienen SHALL y escenarios propios y que son la prueba de C19. No invalida la cobertura (los 4 están cubiertos por C19), pero es una **derivación de instrumentación**: cualquier recuento futuro de «requisitos del proyecto» que use el gate subestimará en 4. W2.5 y W6.1 deben corregir el patrón o declarar la convención `chart_*` como ID válido. Severidad P3 (no P0/P1).

### H-M2 · P3 · Tres requisitos citan cifras stale (759 / 136 tests) que el baseline ya registró

**Evidencia (solo leído):** `mongodb-y-analisis/spec.md:255` («mantener los 759 anuncios tras limpio»), `:394` («424 Point GeoJSON de 759 anuncios»), `:407` («pytest tests SHALL pasar con 136 tests»). El baseline v9 (`00_baseline_v9.md:93`, `:81`) fija el vigente en **594 anuncios** y **237 tests (235 passed, 2 skipped)**.

**Impacto:** el mapa no debe usarse como fuente de cifras; W4.1–W4.3 ya barren estos documentos. No es un hallazgo nuevo (H-02/H-12 del baseline); se registra para que W1.3 no lo cuente como desviación nueva.

### H-M3 · P3 · La tabla «Mapeo criterio → requisito» del contrato enumera 27 filas, no 19

**Evidencia (solo leído):** `contrato-reto/spec.md:180-208` tiene 27 filas; las filas 9–12 corresponden a RA4 **v1** («Gráficos», «Datos», «Presentación», «Interpretación») marcadas como «superado por RA4 v2». El PDF tiene 19 criterios.

**Impacto:** si W1.3 toma esa tabla como enumeración canónica, reportará 27 criterios y duplicará los RA4. La numeración C1–C19 de este informe sigue el PDF, no la tabla del contrato.

### H-M4 · P3 · El baseline no distingue 46 IDs de 50 encabezados

**Evidencia (solo leído):** `00_baseline_v9.md:84` registra «Requisitos con ID | 46 | `grep -rhoE "^### Requirement: …"`» sin señalar que el patrón excluye los 4 `chart_*`.

**Impacto:** la cifra 46 es correcta para el patrón, pero engañosa como total de requisitos. Corregido por H-M1.

---

## 9. Ejecutado vs solo leído

**Ejecutado (herramienta real):**
- `grep -rhoE "^### Requirement: [A-Z0-9_-]+" openspec/specs/ | sort | wc -l` → **46**.
- `grep -cE '^### Requirement: ' openspec/specs/*/spec.md` → **50** (3+2+12+19+14).
- `grep -n "Requirement" scripts/verificar_gobernanza.py` → patrón en línea 36; docstring en línea 5.
- `wc -l openspec/specs/*/spec.md` → 1.850 líneas.
- `find`/`ls` de `openspec/audit/v9_2026-11-10/` y de `matriz_rubrica_v8.md`.

**Solo leído (sin ejecutar):** las 5 specs (1.850 líneas), el PDF (123 líneas), el docx (266 líneas), `AGENT.md`, `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `scripts/verificar_gobernanza.py`, `openspec/audit/v8_2026-11-09/matriz_rubrica_v8.md`.

**No ejecutado (guardrails):** ningún test, ningún pipeline, ninguna consulta a Mongo/HDFS/Kafka, ningún `load_all`/`clean_all`, ningún commit/push, ninguna instalación.

---

## 10. Bloqueos

Ninguno. No se encontró P0/P1. La tarea se completó sin tocar código, datos, Mongo, HDFS ni Kafka.

---

## 11. Entrega

- **report_path:** `openspec/audit/v9_2026-11-10/mapa_requisitos.md` (este fichero).
- **criteria_covered:** 19/19 rúbrica (C1–C19) + 7/7 Tema 8 (T1–T7). 0 criterios sin requisito.
- **findings:** H-M1 (P3, 50 vs 46 requisitos; `chart_*` fuera del gate), H-M2 (P3, cifras stale 759/136 en 3 requisitos), H-M3 (P3, tabla del contrato con 27 filas vs 19 criterios), H-M4 (P3, baseline no distingue 46 IDs de 50 encabezados).
- **executed:** greps de requisitos y del patrón de gobernanza; `wc`/`find`/`ls`.
- **read_only:** specs, PDF, docx, baseline, plan, AGENT.md, script de gobernanza, matriz v8.
- **blockers:** ninguno.
