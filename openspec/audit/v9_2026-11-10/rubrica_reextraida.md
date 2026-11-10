# Rúbrica reextraída del PDF — auditoría v9 (W1.1)

**Fecha:** 2026-11-10 · **Unidad:** W1.1 · **Naturaleza:** solo lectura · **Autor del artefacto:** subagente v9
**Entrada:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf`, `openspec/specs/contrato-reto/spec.md`, `openspec/audit/v8_2026-11-09/matriz_rubrica_v8.md`
**Guardrails respetados:** no se modificó código, datos, Mongo, HDFS ni Kafka; no se instalaron dependencias; no hubo commit/push. Única escritura: este informe.

---

## 1. Fuente de verdad

**La fuente de verdad de los 19 criterios es el PDF v2**, no el contrato ni la matriz v8.

| Elemento | Valor | Evidencia |
|---|---|---|
| Fichero | `brief/RETO 1Evaluacion SBD-BDAv2.pdf` | `ls brief/` |
| SHA-256 | `6f75e97ff127bf3a25b93962a03f4c3957d526ee6ca66895717104e75b07b185` | `sha256sum` |
| Páginas | **6** | `pypdf.PdfReader` → `len(r.pages)` |
| Metadatos | Autor `Ainhoa Zugadi Zulueta`; Creator `Microsoft® Word LTSC`; CreationDate `D:20261030124454+01'00'` | `pypdf` `r.metadata` |
| Tamaño | 340.916 B | `ls -la` |
| Extracto layout | 178 líneas | `pdftotext -layout` (fichero en scratch) |
| Contrato declara la precedencia | «Fuente de verdad: `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (rúbrica v2, reemplaza a la v1)» | `openspec/specs/contrato-reto/spec.md:6` |
| `AGENT.md` | «contrato `pdf v2` más `docx Tema 8` como evaluación separada» | `AGENT.md:4` |

El docx `Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` es **evaluación separada** (sección 16, pesos 15/15/20/15/10/15/10) y **no** forma parte de los 19 criterios. No se mezcla.

---

## 2. Los 19 criterios, transcritos literal del PDF

Escala uniforme: **0 / 3 / 7 / 10 puntos**. Transcripción literal (sin negrita añadida en el cuerpo; la columna de 10 puntos es el nivel exigido por el contrato).

### 2.1 BDA — RA1. Gestión de soluciones y almacenamiento (4 criterios)

| # | Criterio | 0 puntos | 3 puntos | 7 puntos | 10 puntos |
|---|---|---|---|---|---|
| 1 | Extracción de datos mediante Python | No obtiene datos | Obtiene datos de una fuente manualmente | Automatiza una API o scraping | Automatiza API y scraping |
| 2 | Almacenamiento HDFS | No almacena datos | Crea directorios | Guarda y recupera archivos | Organiza originales y procesados y demuestra su recuperación |
| 3 | Kafka | No funciona | Crea un tópico | Envía mensajes con productor Python | Productor y consumidor Python funcionan y procesan mensajes |
| 4 | Integración | No hay integración | Los componentes funcionan por separado | Integra dos o más componentes | Demuestra el flujo completo hasta MongoDB |

### 2.2 SBD — RA1. Adquisición, integración y tratamiento de datos (4 criterios) · **Peso 46,7 %**

| # | Criterio | 0 puntos | 3 puntos | 7 puntos | 10 puntos |
|---|---|---|---|---|---|
| 5 | Integración de fuentes | No carga datos en MongoDB | Carga datos de 1 fuente | Carga datos de 2 fuentes diferentes | Carga datos de 2 o más fuentes diferentes y las relaciona mediante al menos 1 campo común |
| 6 | Construcción del conjunto de datos | No existe una estructura de datos funcional | Guarda todos los datos en una colección sin tratamiento | Utiliza 2 o más colecciones o documentos anidados/arrays | Utiliza 2 o más colecciones y demuestra al menos 1 relación, embedding o referencia entre datos |
| 7 | Limpieza y transformación con PyMongo | No realiza limpieza | Realiza 1 operación de limpieza o transformación | Realiza al menos 3 operaciones diferentes | Realiza al menos 4 operaciones diferentes, incluyendo tratamiento de nulos/ausentes, duplicados y tipos/formato de datos |
| 8 | Automatización | El tratamiento se realiza manualmente | Existe algún script Python parcial | Los datos se cargan y transforman mediante scripts Python | Un script o conjunto de scripts permite ejecutar carga + limpieza + transformación, sin modificar manualmente los datos en MongoDB |

### 2.3 SBD — RA3. Gestión y almacenamiento en MongoDB (6 criterios) · **Peso 13,3 %**

| # | Criterio | 0 puntos | 3 puntos | 7 puntos | 10 puntos |
|---|---|---|---|---|---|
| 9 | Modelado MongoDB | No crea una BD funcional | Crea al menos 1 colección | Utiliza 2 o más colecciones con tipos de datos adecuados | Además, utiliza y demuestra al menos 1 decisión de embedding/referencing y explica por qué la ha utilizado |
| 10 | CRUD con PyMongo | No utiliza PyMongo | Realiza insert | Realiza mediante PyMongo insert + update + delete + find | Realiza las 4 operaciones y comprueba mediante código que el resultado es el esperado |
| 11 | Consultas | No realiza consultas | Realiza consultas con igualdad | Utiliza al menos 4 tipos diferentes entre filtros, comparación, operadores lógicos, proyección, sort, arrays o campos anidados | Realiza al menos 5 consultas útiles para el reto, incluyendo una con campos anidados o arrays y otra combinando 2 o más condiciones |
| 12 | Aggregation Pipeline | No utiliza aggregate() | Pipeline con $match y/o $group | Crea al menos 2 pipelines y utiliza 4 etapas diferentes en total | Crea al menos 3 pipelines que respondan preguntas del reto y utiliza 5 etapas diferentes, incluyendo $group y al menos una entre $lookup, $unwind o $facet |
| 13 | Índices y rendimiento | No crea índices | Crea 1 índice | Crea un índice relacionado con una consulta y ejecuta explain() | Compara mediante explain() la consulta antes/después o con/sin índice e identifica COLLSCAN/IXSCAN y totalDocsExamined |
| 14 | Consistencia | No aplica lo trabajado | Solo describe el concepto | Identifica en su proyecto una operación atómica o un caso donde podría necesitarse una transacción | Implementa una transacción real si su modelo la necesita; si no la necesita, demuestra mediante código una operación atómica y justifica técnicamente por qué una transacción sería innecesaria |

### 2.4 SBD — RA4. Procesamiento, análisis y preparación de resultados (5 criterios) · **Peso 40 %**

| # | Criterio | 0 puntos | 3 puntos | 7 puntos | 10 puntos |
|---|---|---|---|---|---|
| 15 | Datos heterogéneos | No integra datos | Trabaja con una estructura simple | Utiliza arrays, documentos anidados o datos con estructuras diferentes | Integra datos procedentes de fuentes con estructuras diferentes y los adapta mediante Python/PyMongo |
| 16 | Automatización del análisis | Los resultados se obtienen manualmente | Ejecuta consultas manuales | Un script PyMongo ejecuta consultas/agregaciones | Un script ejecuta automáticamente todos los análisis principales y devuelve resultados preparados para su representación |
| 17 | Indicadores | No calcula indicadores | Calcula 1 indicador | Calcula al menos 3 indicadores relacionados con vivienda/emancipación | Calcula al menos 5 indicadores, combinando información procedente de 2 o más fuentes |
| 18 | Respuesta al reto | No responde a la pregunta | Presenta datos sin conclusión | Obtiene conclusiones para al menos 2 municipios o zonas | Compara al menos 3 municipios/zonas y cada conclusión está vinculada a un indicador calculado con MongoDB |
| 19 | Preparación para visualización | No prepara resultados | Copia resultados manualmente | Genera mediante PyMongo datos utilizables para gráficos | Genera automáticamente mediante PyMongo al menos 3 conjuntos de resultados diferentes preparados para representar |

**Total: 4 + 4 + 6 + 5 = 19 criterios.** Verificado por conteo de filas en las cuatro tablas del PDF.

---

## 3. Pesos en la 1.ª evaluación

| RA | Peso | Dónde está en el PDF | Comentario |
|---|---|---|---|
| **BDA RA1** | **NO declarado** | — | No existe ninguna línea «Peso en la 1.ª evaluación» en la sección BDA (página 3). |
| SBD RA1 | **46,7 %** | página 4, línea 108 del extracto | «Peso en la 1.ª evaluación: 46,7 %» |
| SBD RA3 | **13,3 %** | página 5, línea 131 del extracto | «Peso en la 1.ª evaluación: 13,3 %» |
| SBD RA4 | **40 %** | página 6, línea 159 del extracto | «Peso en la 1.ª evaluación: 40 %» |

**Suma SBD: 46,7 + 13,3 + 40 = 100,0 %.** El PDF solo pondera la parte SBD; BDA RA1 se evalúa (4 criterios × 10 = 40 puntos) pero **sin peso declarado**. No se encontró ningún peso de BDA en el PDF (6 páginas revisadas, 3 líneas «Peso», página 3 sin ninguna).

---

## 4. Cotejo con el contrato (`openspec/specs/contrato-reto/spec.md`)

### 4.1 Literal: 76/76 celdas idénticas, 0 diferencias

El contrato transcribe las cuatro tablas en las líneas 35-38, 48-51, 61-66 y 76-80. Comparación programática normalizando mayúsculas y espacios (script `compare_rubrica.py`, scratch): **las 76 celdas (19 criterios × 4 niveles) aparecen literalmente en el texto del PDF. 0 MISS.**

| Contrato | PDF | Resultado |
|---|---|---|
| líneas 35-38 (BDA RA1) | líneas 74-79 | 16/16 OK |
| líneas 48-51 (SBD RA1) | líneas 89-94 | 16/16 OK |
| líneas 61-66 (SBD RA3) | líneas 102-109 | 24/24 OK |
| líneas 76-80 (SBD RA4) | líneas 117-123 | 20/20 OK |

**Única diferencia formal:** el contrato escribe la cabecera de la columna final como `**10 puntos**` (negrita propia) y las celdas de 10 puntos en negrita; el PDF no usa negrita. No es una diferencia literal de contenido.

Las notas de trazabilidad del contrato son correctas respecto al extracto del PDF:
- BDA RA1 → PDF líneas 72-79, peso **ausente** (`spec.md:40`).
- SBD RA1 → PDF líneas 85-94, peso 46,7 % en línea 87 (`spec.md:53`).
- SBD RA3 → PDF líneas 98-109, peso 13,3 % en línea 100 (`spec.md:68`).
- SBD RA4 → PDF líneas 113-123, peso 40 % en línea 115 (`spec.md:82`).

### 4.2 Discrepancia contractual: 4 RAs, 3 pesos

`spec.md:12` dice: «Cubre BDA RA1, SBD RA1, SBD RA3 y SBD RA4 con pesos 46,7 % / 13,3 % / 40 % en la 1.ª evaluación.» Enumera **cuatro** RAs pero da **tres** pesos; BDA RA1 queda sin peso, igual que en el PDF. No es un error de transcripción: el contrato reproduce fielmente la laguna del PDF. Se registra como hallazgo (H-R1).

### 4.3 La numeración del mapeo del contrato no coincide con la rúbrica

El contrato incluye una tabla «Mapeo criterio → requisito» (`spec.md:182-208`) de **27 filas**, no 19. Su numeración es **distinta** de la numeración canónica 1-19 de la rúbrica y del v8. Ejemplo: el «criterio 5» del contrato es **Modelado**; en la rúbrica, el criterio 5 es **Integración de fuentes**. Ver H-R3.

---

## 5. Cotejo con la matriz v8 (`matriz_rubrica_v8.md`)

### 5.1 Cobertura: 19/19 criterios, misma numeración 1-19

La matriz v8 tiene 19 filas con la numeración 1-19 en el **mismo orden** que el PDF: BDA 1-4, SBD RA1 5-8, SBD RA3 9-14, SBD RA4 15-19. No faltan criterios ni sobra ninguno. Mapeo completo:

| # | PDF (literal) | v8 (etiqueta) | Contrato mapeo (línea) |
|---|---|---|---|
| 1 | Extracción de datos mediante Python | BDA · Extracción Python (API **y** scraping) | 182 |
| 2 | Almacenamiento HDFS | BDA · HDFS (originales **y** procesados + recuperación) | 183 |
| 3 | Kafka | BDA · Kafka (productor y consumidor procesan) | 184 |
| 4 | Integración | BDA · Integración (flujo completo hasta MongoDB) | 185 |
| 5 | Integración de fuentes | SBD RA1 · Integración de fuentes (2+ y campo común) | 200 |
| 6 | Construcción del conjunto de datos | SBD RA1 · Construcción (2+ colecciones + relación/embedding/referencia) | 201 |
| 7 | Limpieza y transformación con PyMongo | SBD RA1 · Limpieza PyMongo (4+ ops con nulos, duplicados y tipos) | 196 |
| 8 | Automatización | SBD RA1 · Automatización (carga+limpieza+transformación) | 202 |
| 9 | Modelado MongoDB | SBD RA3 · Modelado (+ embedding/referencing explicado) | 186 |
| 10 | CRUD con PyMongo | SBD RA3 · CRUD (4 ops + comprobación en código) | 187 |
| 11 | Consultas | SBD RA3 · Consultas (5 útiles, anidada/array y 2+ condiciones) | 188 |
| 12 | Aggregation Pipeline | SBD RA3 · Aggregation (3+ pipelines, 5 etapas, `$group` + `$lookup`/`$unwind`/`$facet`) | 189 |
| 13 | Índices y rendimiento | SBD RA3 · Índices (`explain` antes/después, `COLLSCAN`/`IXSCAN`, `totalDocsExamined`) | 203 |
| 14 | Consistencia | SBD RA3 · Consistencia (atómica + justificación o transacción) | 204 |
| 15 | Datos heterogéneos | SBD RA4 · Datos heterogéneos (estructuras distintas adaptadas) | 205 |
| 16 | Automatización del análisis | SBD RA4 · Automatización del análisis | 206 |
| 17 | Indicadores | SBD RA4 · Indicadores (5+, 2+ fuentes) | 207 |
| 18 | Respuesta al reto | SBD RA4 · Respuesta al reto (3+ municipios, conclusión ↔ indicador) | 198 |
| 19 | Preparación para visualización | SBD RA4 · Preparación visualización (3+ conjuntos automáticos) | 208 |

### 5.2 Redacciones distintas (etiquetas v8 vs PDF literal)

16 de 19 etiquetas v8 aparecen literalmente en el PDF; 3 son paráfrasis y 6 más abrevan. Ninguna cambia el criterio, pero la matriz v8 **no es una transcripción literal**:

| # | v8 | PDF literal | Tipo |
|---|---|---|---|
| 1 | Extracción Python | Extracción de datos mediante Python | paráfrasis |
| 2 | HDFS | Almacenamiento HDFS | abreviado |
| 6 | Construcción | Construcción del conjunto de datos | abreviado |
| 7 | Limpieza PyMongo | Limpieza y transformación con PyMongo | paráfrasis |
| 9 | Modelado | Modelado MongoDB | abreviado |
| 10 | CRUD | CRUD con PyMongo | abreviado |
| 12 | Aggregation | Aggregation Pipeline | abreviado |
| 13 | Índices | Índices y rendimiento | abreviado |
| 19 | Preparación visualización | Preparación para visualización | paráfrasis |

Evidencia: `compare_v8.py` → 16 `OK` / 3 `MISS` sobre la etiqueta base (las 3 MISS son exactamente las paráfrasis de arriba).

### 5.3 Discrepancia de fondo: v8 no aplica los pesos del PDF

- La matriz v8 puntúa **puntos brutos** por criterio (10 por criterio): `BDA RA1: 37/40 · SBD RA1: 40/40 · SBD RA3: 60/60 · SBD RA4: 50/50` → `187/190 (98,4 %)`. No menciona en ningún sitio los pesos 46,7 / 13,3 / 40.
- El PDF pondera por RA: SBD RA1 46,7 %, RA3 13,3 %, RA4 40 %. BDA RA1 sin peso.
- Bajo los pesos del PDF (distribuyendo el peso de cada RA uniformemente entre sus criterios), la parte **SBD = 100,0 %** (todos los criterios SBD a 10). La parte **BDA = 37/40 = 92,5 %** en su propia escala.
- El «187/190 (98,4 %)» de v8 es, por tanto, un **promedio de puntos brutos** que pondera implícitamente BDA RA1 con 4/19 (21,05 %) y cada RA SBD por su número de criterios (RA1 21,05 %, RA3 31,58 %, RA4 26,32 %) — un modelo distinto del PDF. Ver H-R2.

---

## 6. Hallazgos

**Recuento: P0 = 0 · P1 = 0 · P2 = 3 · P3 = 2.** Ningún P0/P1: no se detuvo la auditoría.

| ID | Severidad | Título | Evidencia | Impacto |
|---|---|---|---|---|
| **H-R1** | **P2** | El PDF no declara peso para BDA RA1; el contrato reproduce la laguna (4 RAs, 3 pesos) | PDF 6 páginas, solo 3 líneas «Peso en la 1.ª evaluación» (págs. 4-6); `spec.md:12` enumera BDA RA1 y da 3 pesos | No se puede calcular la nota ponderada completa; la valoración de BDA queda en 37/40 sin peso. Riesgo de defensa si se presenta un porcentaje único |
| **H-R2** | **P2** | La matriz v8 puntúa puntos brutos (187/190) sin aplicar los pesos del PDF (46,7/13,3/40) | `matriz_rubrica_v8.md:3-4`; `informe_reauditoria_v8.md:121-127`; PDF págs. 4-6 | La nota v8 no es la nota ponderada del PDF. SBD ponderado = 100,0 %; BDA = 37/40 (92,5 %). El 98,4 % mezcla dos escalas |
| **H-R3** | **P2** | La numeración del mapeo criterio→requisito del contrato (27 filas) no coincide con la numeración canónica 1-19 de la rúbrica; incluye criterios RA4 v1 superados y requisitos que no son criterios v2 | `spec.md:182-208` vs PDF; ej. contrato «5 Modelado» = rúbrica #9; contrato «19 RA1 Integración de fuentes v2» = rúbrica #5 | Riesgo de trazabilidad: un lector que cruce «criterio 5» entre contrato y rúbrica/v8 compara criterios distintos. Las filas 190-193 (RA4 v1) y 194/195/199 (requisitos) no son criterios v2 |
| **H-R4** | **P3** | Las etiquetas de la matriz v8 son paráfrasis, no literales (3 de 19 divergen: #1, #7, #19) | `compare_v8.py` → 16 OK / 3 MISS; `matriz_rubrica_v8.md:10,16,28` | Menor: no cambia la cobertura ni la nota; pero la matriz v8 no puede usarse como transcripción literal de la rúbrica |
| **H-R5** | **P3** | Las referencias de línea del contrato apuntan al extracto del PDF (read_file), no a un PDF con numeración física estable | `spec.md:40,53,68,82`; el PDF no tiene números de línea | Menor: se resuelve citando página y sección; las referencias siguen siendo reproducibles con el extracto |

---

## 7. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `pypdf.PdfReader` → 6 páginas, metadata, extracción de texto por página.
- `pdftotext -layout` (poppler, `/mingw64/bin/pdftotext.exe`) → 178 líneas en scratch.
- `sha256sum` del PDF, el contrato y la matriz v8.
- `git status --porcelain` sobre las tres entradas: solo `matriz_rubrica_v8.md` es untracked; el PDF y el contrato están limpios (sin cambios).
- Scripts de comparación en scratch (`compare_rubrica.py`, `compare_v8.py`, `probe_pdf_meta.py`, `conv_reto.py`): 76/76 celdas OK; 19 filas v8, 16 OK / 3 paráfrasis; 3 pesos en el PDF.
- `read_file` sobre el PDF (auto-extracción), el contrato, la matriz v8, `informe_reauditoria_v8.md`, baseline, plan, `AGENT.md`, `unidades_trabajo_v9.csv`.

**Solo leído (sin ejecutar):** los documentos de auditoría v8 y v9; `AGENT.md`; `openspec/specs/contrato-reto/spec.md`.

**No ejecutado:** ningún pipeline, `load_all`/`clean_all`/`run_analisis_mongo`, productor Kafka, escritura en `data/`, Mongo, HDFS o Kafka. No se instaló `pdfplumber` (no estaba en `.venv`; solo `pypdf 6.21.4`), respetando la prohibición de instalar dependencias. No hubo commit/push.

---

## 8. Límites de este informe

- El PDF es la fuente de verdad, pero no declara el peso de BDA RA1; cualquier nota ponderada completa requiere que la entidad evaluadora lo aclare (H-R1).
- La comparación literal se hizo normalizando mayúsculas, espacios y guiones; no se comparó la tipografía (negritas, tamaños) del PDF.
- Las referencias de línea del contrato se validaron contra el extracto de `read_file`, no contra un PDF numerado (H-R5).
- La matriz v8 está **untracked** en git (`?? openspec/audit/v8_2026-11-09/matriz_rubrica_v8.md`); el PDF y el contrato están limpios. Este estado es el de partida y no se tocó.
