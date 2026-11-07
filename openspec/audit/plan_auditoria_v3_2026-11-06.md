# Plan de auditoría v3 — rubric-first, exigente, sin acceso a Hadoop/Kafka

**Fecha:** 2026-11-06
**Alcance:** código, datos locales (`data/`), MongoDB local, tests, documentación y entregables, evaluados **criterio por criterio contra el umbral de 10 puntos** de la rúbrica v2.
**Modo:** solo lectura. No se modifica `data/`, `storage/`, `transform/`, `extract/`, `analysis/`, `tests/` ni datos de producción en MongoDB. Las reparaciones van a un backlog aparte, tras autorización.
**Fuente de verdad:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (págs. 3-4) y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` (sección 16), **cotejados contra el binario, no contra la transcripción**.
**Restricción declarada:** sin acceso hoy al clúster del centro (`10.22.87.215`) ni al broker Kafka. Todo lo que dependa de ellos se marca como evidencia congelada (§4), nunca como PASS.

---

## 0. Preflight (se ejecuta al arrancar; nada se supone)

| # | Comprobación | Comando | Por qué |
|---|---|---|---|
| 0.1 | Baseline git | `git status --short`, `git log -1` | Fijar el árbol auditado |
| 0.2 | Digest de cierre | `git ls-files -s \| sha256sum` antes y después | Probar que la auditoría no escribió |
| 0.3 | Entorno Python | `.venv/Scripts/python.exe --version`, `pip freeze \| sha256sum` | Reproducibilidad |
| 0.4 | MongoDB local | `ping` a `localhost:27017`, `getCollectionNames()`, `count_documents` de `anuncios`/`municipios` | Sin Mongo se cae F4, F5 y F8 |
| 0.5 | Inventario de datos | nº de ficheros en `data/raw`, `data/procesado`, `data/resultados` | Base de los conteos de F7 |
| 0.6 | Suite | `pytest tests --collect-only -q` | Saber qué se puede ejecutar |

Si 0.4 falla, la auditoría baja a "estática" y se declara en la cabecera del informe.

---

## 1. Regla de puntuación (lo que hace exigente esta auditoría)

1. **Umbral literal.** Un criterio solo vale **10** si se demuestra exactamente el enunciado de la columna 10, palabra por palabra. "Casi" es 7.
2. **Evidencia triple.** Cada fila exige: **comando ejecutado + salida numérica + `fichero:línea`** del código que lo produce. Sin las tres, no hay 10.
3. **La documentación no es evidencia** (P-08). Un README que dice "9 pipelines" no cuenta; cuentan las etapas contadas en `analysis/mongo_aggregations.py` y los CSV regenerados.
4. **No verificable ≠ 10.** Se marca `PENDIENTE` y se explica qué falta para verificarlo.
5. **Prueba de falsación.** Para cada criterio se anota qué observación lo bajaría a 7. Si esa observación aparece, baja.
6. **Sin datos simulados** (P-02), **sin valores tecleados** (P-05), **alquiler de Eustat, no del INE** (P-03), **alquiler como eje, no compraventa** (P-01).

---

## 2. Fases

### F1 — Fidelidad de la rúbrica (PDF/docx → spec)
Extraer el texto de `brief/*.pdf` (pdfplumber) y del `.docx`, y **comparar celda a celda** con las tablas de `openspec/specs/contrato-reto/spec.md`. Objetivo: detectar cualquier "suavizado" (un 10 del PDF convertido en SHOULD en el contrato) antes de puntuar con la vara equivocada. Entregable: tabla de fidelidad X/Y celdas idénticas + diferencias.

### F2 — BDA RA1 (4 criterios)
Extracción (API + scraping reales, `main()` que corre, sidecars), HDFS (originales **y** procesados + recuperación), Kafka (productor **y** consumidor procesando), Integración (flujo completo hasta MongoDB).
Nota: el waiver verbal de la profesora ("en HDFS solo raw") **se documenta como excepción autorizada**, no como cambio de rúbrica: el informe dará las dos lecturas (PDF literal y criterio con waiver) y dirá cuál se defiende.

### F3 — SBD RA1 (4 criterios, 46,7 %)
Integración de fuentes (2+ y campo común), construcción del conjunto (2+ colecciones + relación/embedding/referencia demostrada), limpieza (≥4 operaciones **incluyendo** nulos, duplicados y tipos/formato), automatización (carga+limpieza+transformación sin editar a mano en Mongo).

### F4 — SBD RA3 (6 criterios, 13,3 %)
Modelado (decisión embedding/referencing **explicada y demostrada**), CRUD (4 operaciones **y comprobación por código** del resultado), consultas (≥5 útiles, con una de anidados/arrays y otra de 2+ condiciones), aggregation (≥3 pipelines del reto, ≥5 etapas distintas, `$group` + `$lookup|$unwind|$facet`), índices (`explain()` antes/después con COLLSCAN/IXSCAN y `totalDocsExamined`), consistencia (transacción real o atómica + justificación técnica).

### F5 — SBD RA4 (5 criterios, 40 %)
Datos heterogéneos, automatización del análisis, ≥5 indicadores de 2+ fuentes, ≥3 municipios comparados con conclusión ligada a indicador de Mongo, ≥3 conjuntos generados automáticamente para representar.

### F6 — Tema 8 (7 bloques con peso propio)
Modelado 15 %, CRUD/limpieza/consultas 15 %, Aggregation 20 %, Índices 15 %, Transacciones 10 %, PyMongo profesional 15 % (cursores, cliente reutilizado, errores), Defensa 10 % (solo verificable lo que esté escrito en guion).
Comprobaciones extra que casi nadie cubre: tipos de índice justificados uno a uno (unique/compuesto/multikey/2dsphere/sparse/partial/TTL), iteración de cursores, `MongoClient` único y URI configurable, manejo de errores.

### F7 — Integridad y reproducibilidad de datos
Manifest raw (354 vs ficheros reales), `.FROZEN`, guards (`test_raw_guardrails`), silver (188 / manifest 185), `transform/run_all.py --check`, doble ejecución de `run_analisis_mongo.py` con la misma huella SHA-256, conteos (759 anuncios, 83 municipios, 252 municipios, 159 con alquiler oficial, 4 robustos). Cualquier número que no cuadre con la documentación se anota.

### F8 — Tests: cobertura criterio → test
Para cada uno de los 19 criterios: ¿existe una comprobación ejecutable? Tabla `criterio → test → qué afirma`. Se buscan específicamente tests que **no afirman nada** (asserts triviales, `skip`/`xfail`, literales copiados) y criterios **sin ningún test** (riesgo P-08).
Ejecución de la suite; verificar que `anuncios`=759 y `municipios`=252 siguen intactos después (pytest escribe en BD de test).

### F9 — Documentación y entregables + barrido de contradicciones
Esquema de arquitectura, informe con tablas y gráficos, guion de demo. Barrido de cifras repetidas en todos los `.md` buscando contradicciones (759/845, 354/352, 188/185, 14/16/27, 134/136/145, 9 pipelines, broker y particiones). Cada contradicción cuenta como riesgo de defensa, no como punto de rúbrica.

### F10 — Seguridad (P-07)
Credenciales, `.env` fuera de git, ficheros sensibles versionados, cadenas de conexión en código.

### F11 — Matriz final y backlog
Informe con: matriz de 26 filas (19 v2 + 7 Tema 8), hallazgos P0-P3, lo no verificable, y **backlog ordenado por impacto en nota** (coste estimado vs puntos que recupera).

---

## 3. Matriz de comprobación (lo que exijo en cada fila)

### BDA RA1

| Criterio | Umbral 10 literal | Evidencia que exijo | Falsación |
|---|---|---|---|
| Extracción Python | Automatiza API **y** scraping | ≥1 cliente API y ≥1 scraper con `main()` ejecutable, sidecar/log por fuente, ficheros en `data/raw` con fecha | Todo el raw viene de descargas manuales o de un solo tipo de fuente |
| HDFS | Organiza originales **y procesados** y demuestra recuperación | `LISTSTATUS` de `/raw` y `/procesado`, SHA local==remoto, tamaño igual | Solo hay `raw` (→ 7 por PDF; el waiver se cita aparte) |
| Kafka | Productor **y consumidor** Python funcionan y procesan mensajes | Código de ambos, offsets commiteados, lag 0, mensajes descartados por SHA | El consumidor no lee el topic o no procesa (solo existe) |
| Integración | Flujo completo **hasta MongoDB** | Cadena ejecutable que acaba escribiendo en Mongo, con documento de prueba | Kafka termina en HDFS y Mongo se llena por otra vía (→ 7) |

### SBD RA1 (46,7 %)

| Criterio | Umbral 10 | Evidencia | Falsación |
|---|---|---|---|
| Integración de fuentes | 2+ fuentes + ≥1 campo común | Conteo de colecciones con datos y join 100 % por `codigo_ine` | Alguna fuente sin relacionar o join parcial |
| Construcción del conjunto | 2+ colecciones + relación/embedding/referencia | Estructura real en Mongo + consulta que atraviesa la relación | Solo colecciones planas sin vínculo demostrado |
| Limpieza PyMongo | ≥4 operaciones incl. nulos, duplicados, tipos/formato | Cada operación con `fichero:línea` y contador (`matched/modified`) | Hay 3 operaciones, o falta nulos/duplicados/tipos |
| Automatización | Script hace carga+limpieza+transformación sin tocar Mongo a mano | Cadena de scripts ejecutable en orden, sin pasos manuales | Requiere una edición manual en Compass/mongosh |

### SBD RA3 (13,3 %)

| Criterio | Umbral 10 | Evidencia | Falsación |
|---|---|---|---|
| Modelado | 2+ colecciones, tipos adecuados + decisión embedding/referencing **explicada** | Documento + estructura + justificación ligada a patrón de acceso | Existe la decisión pero no se explica, o los tipos son texto para todo |
| CRUD PyMongo | 4 operaciones **y comprobación por código** | Código con `insert/update/delete/find` + `assert` del resultado | Las 4 llamadas sin ninguna comprobación (→ 7) |
| Consultas | ≥5 útiles, 1 con anidados/arrays, 1 con 2+ condiciones | Inventario contado por tipo desde el código | 4 consultas, o ninguna con arrays/anidados |
| Aggregation | ≥3 pipelines del reto, 5 etapas, `$group` + `$lookup|$unwind|$facet` | Conteo de pipelines y de etapas distintas | 2 pipelines o 4 etapas |
| Índices | `explain()` antes/después, COLLSCAN/IXSCAN y `totalDocsExamined` | Salida real de `explain` con ambos planes | Solo se crea el índice sin comparar planes |
| Consistencia | Transacción real o atómica + justificación | `update_one` atómico demostrado y razonado, o `with_transaction` | Se afirma "no hace falta" sin demostración por código |

### SBD RA4 (40 %)

| Criterio | Umbral 10 | Evidencia | Falsación |
|---|---|---|---|
| Datos heterogéneos | Estructuras distintas adaptadas con Python/PyMongo | ≥3 formatos de origen (CSV/JSON/XLSX/HTML) normalizados, con el código que lo hace | Todo llega ya tabular |
| Automatización análisis | Un script ejecuta **todos** los análisis y devuelve resultados listos | Un entrypoint, N pipelines, CSV de salida | Hay que lanzar 5 scripts a mano |
| Indicadores | ≥5 indicadores combinando 2+ fuentes | Cada indicador con fórmula, fuente y CSV | 4 indicadores, o todos de una sola fuente |
| Respuesta al reto | ≥3 municipios comparados, conclusión ligada a indicador de Mongo | Tabla de 3+ municipios con indicador calculado en Mongo | Conclusiones narrativas sin indicador detrás |
| Preparación visualización | ≥3 conjuntos autogenerados por PyMongo | ≥3 CSV con fecha de generación y script que los produce | CSV copiados o generados con valores tecleados (P-05) |

### Tema 8 (pesos 15/15/20/15/10/15/10)
Igual que las filas correspondientes de RA3/RA1, más: tipos de índice justificados individualmente, cursores iterados (no `list(find())` sin motivo), `MongoClient` reutilizado, manejo de errores, y guion de defensa que permita explicar cada decisión.

---

## 4. Lo que NO se puede verificar hoy (y cómo se trata)

| Elemento | Estado | Trato |
|---|---|---|
| HDFS del centro (`10.22.87.215:50070`) | Sin acceso | Evidencia congelada 2026-11-06: 352 ficheros, 895.596.949 B idénticos, 13/13 SHA `Igual? True`. Se cita con fecha y se marca **congelada** |
| Broker Kafka (`10.22.87.215:9092`) | Sin acceso | Evidencia congelada: offsets `0:1068..0:1419`, lag 0, 1420 mensajes |
| Extracción desde internet | Sin red de clase | Se verifica por código + artefactos en `data/raw`, no por re-ejecución |

**Regla:** la evidencia congelada sirve para no bajar la nota por falta de acceso, **nunca para subirla**. Si un criterio solo se sostiene con evidencia congelada, el informe lo dice en la misma fila.

---

## 5. Entregables

1. `openspec/audit/informe_auditoria_v3_2026-11-06.md`:
   - Cabecera con baseline, digest inicio/fin y acceso disponible.
   - Fidelidad de rúbrica (F1) con diferencias encontradas.
   - Matriz de 26 filas: criterio · umbral 10 · evidencia medida · nota · qué falta.
   - Hallazgos P0 (tumba nota) / P1 / P2 / P3, cada uno con evidencia.
   - Contradicciones documentales (F9).
   - Criterios sin test (F8).
   - Backlog de reparación ordenado por puntos recuperados / horas.
2. Nada más. Cero cambios en código, datos o Mongo de producción.

## 6. Reglas de conducta

- Solo lectura; `pytest` escribe en la BD de test (se verifica 759/252 antes y después).
- Ningún criterio se marca cubierto sin comando ejecutado (P-08).
- Si un número del informe no cuadra con la documentación, manda el número medido y se anota la discrepancia.
- Al terminar: digest del árbol idéntico al de apertura.

## 7. Orden y esfuerzo estimado

| Fase | Contenido | Est. |
|---|---|---|
| F1 | Fidelidad PDF/docx vs spec | 15 min |
| F2 | BDA RA1 (4) | 20 min |
| F3 | SBD RA1 (4) | 20 min |
| F4 | SBD RA3 (6) | 40 min |
| F5 | SBD RA4 (5) | 25 min |
| F6 | Tema 8 (7) | 25 min |
| F7 | Integridad/reproducibilidad | 20 min |
| F8 | Tests criterio→test + suite | 20 min |
| F9 | Documentación + contradicciones | 25 min |
| F10 | Seguridad | 10 min |
| F11 | Matriz, hallazgos, backlog | 25 min |
| **Total** | | **~4 h** |

Se puede entregar por bloques: F1+F2 (BDA) primero, luego SBD-RA1, luego RA3+RA4, y el informe final al cierre.
