# Contrato del Reto SBD + BDA — Especificación

**Capacidad:** `contrato-reto`
**Estado:** Aceptado — vinculante; fuente v2 sin versionar en git
**Fecha:** 2026-11-04
**Fuente de verdad:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (rúbrica v2, reemplaza a la v1 `brief/RETO 1Evaluacion SBD-BDA.pdf`)
**Specs detalladas:** `../extraccion-datos`, `../almacenamiento-y-streaming`,
`../mongodb-y-analisis`, `../presentacion-de-resultados`

---

## Purpose

Este documento es el contrato. Transcribe la rúbrica del reto y asigna un
requisito y un escenario verificable a cada criterio. Cualquier implementación
que no satisfaga un criterio al nivel de **10 puntos** no cumple el contrato.

Si el código y este contrato discrepan, el contrato manda (o se cambia el
contrato antes de cambiar el código).

---

## La rúbrica (transcrita literal del PDF)

### BDA — RA1. Gestión de soluciones y almacenamiento

| Criterio | 0 puntos | 3 puntos | 7 puntos | **10 puntos** |
|---|---|---|---|---|
| Extracción de datos mediante Python | No obtiene datos | Obtiene datos de una fuente manualmente | Automatiza una API o scraping | **Automatiza API y scraping** |
| Almacenamiento HDFS | No almacena datos | Crea directorios | Guarda y recupera archivos | **Organiza originales y procesados y demuestra su recuperación** |
| Kafka | No funciona | Crea un tópico | Envía mensajes con productor Python | **Productor y consumidor Python funcionan y procesan mensajes** |
| Integración | No hay integración | Los componentes funcionan por separado | Integra dos o más componentes | **Demuestra el flujo completo hasta MongoDB** |

### SBD — RA1. Adquisición, integración y tratamiento de datos

**Peso en la 1.ª evaluación (v2): 46,7 %**

| Criterio | 0 puntos | 3 puntos | 7 puntos | **10 puntos** |
|---|---|---|---|---|
| Integración de fuentes | No carga datos en MongoDB | Carga datos de 1 fuente | Carga datos de 2 fuentes diferentes | **Carga datos de 2 o más fuentes diferentes y las relaciona mediante al menos 1 campo común** |
| Construcción del conjunto de datos | No existe una estructura de datos funcional | Guarda todos los datos en una colección sin tratamiento | Utiliza 2 o más colecciones o documentos anidados/arrays | **Utiliza 2 o más colecciones y demuestra al menos 1 relación, embedding o referencia entre datos** |
| Limpieza y transformación con PyMongo | No realiza limpieza | Realiza 1 operación de limpieza o transformación | Realiza al menos 3 operaciones diferentes | **Realiza al menos 4 operaciones diferentes, incluyendo tratamiento de nulos/ausentes, duplicados y tipos/formato de datos** |
| Automatización | El tratamiento se realiza manualmente | Existe algún script Python parcial | Los datos se cargan y transforman mediante scripts Python | **Un script o conjunto de scripts permite ejecutar carga + limpieza + transformación, sin modificar manualmente los datos en MongoDB** |

### SBD — RA3. Gestión y almacenamiento en MongoDB

**Peso en la 1.ª evaluación (v2): 13,3 %**

| Criterio | 0 puntos | 3 puntos | 7 puntos | **10 puntos** |
|---|---|---|---|---|
| Modelado MongoDB | No crea una BD funcional | Crea al menos 1 colección | Utiliza 2 o más colecciones con tipos de datos adecuados | **Además, utiliza y demuestra al menos 1 decisión de embedding/referencing y explica por qué la ha utilizado** |
| CRUD con PyMongo | No utiliza PyMongo | Realiza insert | Realiza mediante PyMongo insert + update + delete + find | **Realiza las 4 operaciones y comprueba mediante código que el resultado es el esperado** |
| Consultas | No realiza consultas | Realiza consultas con igualdad | Utiliza al menos 4 tipos diferentes entre filtros, comparación, operadores lógicos, proyección, sort, arrays o campos anidados | **Realiza al menos 5 consultas útiles para el reto, incluyendo una con campos anidados o arrays y otra combinando 2 o más condiciones** |
| Aggregation Pipeline | No utiliza aggregate() | Pipeline con $match y/o $group | Crea al menos 2 pipelines y utiliza 4 etapas diferentes en total | **Crea al menos 3 pipelines que respondan preguntas del reto y utiliza 5 etapas diferentes, incluyendo $group y al menos una entre $lookup, $unwind o $facet** |
| Índices y rendimiento | No crea índices | Crea 1 índice | Crea un índice relacionado con una consulta y ejecuta explain() | **Compara mediante explain() la consulta antes/después o con/sin índice e identifica COLLSCAN/IXSCAN y totalDocsExamined** |
| Consistencia | No aplica lo trabajado | Solo describe el concepto | Identifica en su proyecto una operación atómica o un caso donde podría necesitarse una transacción | **Implementa una transacción real si su modelo la necesita; si no la necesita, demuestra mediante código una operación atómica y justifica técnicamente por qué una transacción sería innecesaria** |

### SBD — RA4. Procesamiento, análisis y preparación de resultados

**Peso en la 1.ª evaluación (v2): 40 %**

| Criterio | 0 puntos | 3 puntos | 7 puntos | **10 puntos** |
|---|---|---|---|---|
| Datos heterogéneos | No integra datos | Trabaja con una estructura simple | Utiliza arrays, documentos anidados o datos con estructuras diferentes | **Integra datos procedentes de fuentes con estructuras diferentes y los adapta mediante Python/PyMongo** |
| Automatización del análisis | Los resultados se obtienen manualmente | Ejecuta consultas manuales | Un script PyMongo ejecuta consultas/agregaciones | **Un script ejecuta automáticamente todos los análisis principales y devuelve resultados preparados para su representación** |
| Indicadores | No calcula indicadores | Calcula 1 indicador | Calcula al menos 3 indicadores relacionados con vivienda/emancipación | **Calcula al menos 5 indicadores, combinando información procedente de 2 o más fuentes** |
| Respuesta al reto | No responde a la pregunta | Presenta datos sin conclusión | Obtiene conclusiones para al menos 2 municipios o zonas | **Compara al menos 3 municipios/zonas y cada conclusión está vinculada a un indicador calculado con MongoDB** |
| Preparación para visualización | No prepara resultados | Copia resultados manualmente | Genera mediante PyMongo datos utilizables para gráficos | **Genera automáticamente mediante PyMongo al menos 3 conjuntos de resultados diferentes preparados para representar** |

### Evaluación separada — Tema 8 MongoDB (`Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, sección 16)

Los pesos siguientes NO son pesos v2: son la evaluación separada de la parte MongoDB del Tema 8. No se suman ni se mezclan con 46,7 % / 13,3 % / 40 %.

| Criterio (Tema 8) | Peso | Qué se valora |
|---|---|---|
| Modelado documental | 15 % | Diseño coherente y decisiones justificadas según datos y patrones de acceso |
| CRUD, limpieza y consultas | 15 % | Uso correcto de PyMongo, tipos, operadores, arrays y documentos embebidos |
| Aggregation | 20 % | Pipelines útiles, correctos, explicados y vinculados a la pregunta del reto |
| Índices y rendimiento | 15 % | Índices justificados y evidencia con explain() |
| Transacciones y consistencia | 10 % | Decisión razonada y, cuando proceda, implementación correcta |
| PyMongo profesional | 15 % | Organización, conexión, errores, resultados y reproducibilidad |
| Defensa técnica | 10 % | Capacidad individual para explicar decisiones y comportamiento del sistema |


### Requisitos adicionales del PDF

Las fuentes concretas citadas en este contrato y en los specs (Eustat, INE,
Fotocasa, euskadi.eus, b5m) son la instancia de este proyecto; el reto exige
automatizar API y scraping con fuentes reales, no unas fuentes fijas ni un
esquema universal.

- Objetivo 1: *"Recopilar datos reales sobre precios de alquiler o compraventa
  mediante API y web scraping."*
- Objetivo 2: *"Obtener información complementaria sobre salarios, población u
  otros indicadores que consideréis relevantes."*
- Requisito BDA: *"Gestión de datos en formato JSON o CSV."*
- Requisito SBD: *"Limpieza de datos incompletos, duplicados o incorrectos."*
- Requisito SBD: *"Transformaciones mediante operaciones de MongoDB."*
- Requisito SBD: *"Consultas y agregaciones para obtener indicadores
  estadísticos."*
- *"Todos los programas desarrollados deberán estar escritos en Python."*
- Entregable: *"Datos: ficheros originales almacenados en HDFS y base de datos
  MongoDB."*
- Resultado final: *"Debéis demostrar, utilizando datos reales, qué municipios de
  Euskadi ofrecen mejores posibilidades de emancipación para una persona joven y
  explicar por qué."*
- *"Las conclusiones deberán estar respaldadas por los datos analizados."*

## Entregables del reto

### Requirement: ENTREGABLES-01 — Entregables y demostración

El sistema SHALL entregar código fuente organizado, datos originales en HDFS y
MongoDB, un esquema de arquitectura del recorrido de los datos, un informe de
resultados con gráficos y tablas, y una demostración con explicación de las
decisiones técnicas.

#### Scenario: El esquema de arquitectura existe

- GIVEN el flujo completo
- WHEN se documenta
- THEN existe un esquema explicativo desde el origen de los datos hasta el
  análisis

#### Scenario: El informe incluye tablas y gráficos

- GIVEN los resultados calculados
- WHEN se redacta el informe
- THEN incluye gráficos, tablas y conclusiones

#### Scenario: La demostración explica decisiones

- GIVEN el sistema ejecutable
- WHEN se demuestra
- THEN se ejecuta el flujo y se explican las decisiones técnicas

---

## Mapeo criterio → requisito

| # | Criterio (nivel 10) | Requisito | Spec detallada |
|---|---|---|---|
| 1 | Extracción: API y scraping | `EXTRACCION-01`, `EXTRACCION-02` | extraccion-datos |
| 2 | HDFS: originales, procesados, recuperación | `HDFS-01` | almacenamiento-y-streaming |
| 3 | Kafka: productor y consumidor | `KAFKA-01` | almacenamiento-y-streaming |
| 4 | Integración: flujo completo a MongoDB | `INTEGRACION-01` | almacenamiento-y-streaming |
| 5 | Modelado: justifica modelo y relaciones | `MODELO-01` | mongodb-y-analisis |
| 6 | PyMongo: inserta, actualiza, elimina, comprueba | `PYMONGO-01` | mongodb-y-analisis |
| 7 | Consultas: campos anidados o arrays | `CONSULTAS-01` | mongodb-y-analisis |
| 8 | Agregación v2: ≥3 pipelines, 5 etapas con $group y lookup/unwind/facet | `AGREGACION-01` | mongodb-y-analisis |
| 9 | RA4 v1 Gráficos superado por RA4 v2 Indicadores y Preparación (ver filas 19-27) | `INDICADORES-01`, `PREPARACION-VISUALIZACION-01` | presentacion-de-resultados |
| 10 | RA4 v1 Datos superado por RA4 v2 Automatización del análisis (ver filas 19-27) | `AUTOMATIZACION-ANALISIS-01` | presentacion-de-resultados |
| 11 | RA4 v1 Presentación superado por RA4 v2 Datos heterogéneos y Preparación (ver filas 19-27) | `DATOS-HETEROGENEOS-01`, `PREPARACION-VISUALIZACION-01` | presentacion-de-resultados |
| 12 | RA4 v1 Interpretación superado por RA4 v2 Respuesta al reto (ver fila 17) | `CONCLUSION-01` | presentacion-de-resultados |
| 13 | Salarios / población / indicadores | `COMPLEMENTARIOS-01` | extraccion-datos |
| 14 | Formato JSON o CSV | `FORMATO-01` | extraccion-datos |
| 15 | Limpieza: incompletos, duplicados, incorrectos | `LIMPIEZA-01` | mongodb-y-analisis |
| 16 | Transformaciones en MongoDB | `TRANSFORM-01` | mongodb-y-analisis |
| 17 | Resultado final: municipios y por qué | `CONCLUSION-01` | presentacion-de-resultados |
| 18 | Todo en Python | `PYTHON-01` | extraccion-datos |
| 19 | RA1 Integración de fuentes v2: 2+ fuentes con campo común | `INTEGRACION-01` | almacenamiento-y-streaming |
| 20 | RA1 Construcción conjunto v2: 2+ colecciones con relación/embedding/referencia | `MODELO-01` | mongodb-y-analisis |
| 21 | RA1 Automatización v2: carga + limpieza + transformación sin tocar MongoDB a mano | `INTEGRACION-01`, `LIMPIEZA-01`, `TRANSFORM-01` | almacenamiento-y-streaming, mongodb-y-analisis |
| 22 | RA3 Índices v2: explain() antes/después con COLLSCAN/IXSCAN y totalDocsExamined | `INDICES-01` | mongodb-y-analisis |
| 23 | RA3 Consistencia v2: transacción real o atómica justificada | `TRANSACCIONES-01` | mongodb-y-analisis |
| 24 | RA4 Datos heterogéneos v2: estructuras diferentes adaptadas con Python/PyMongo | `DATOS-HETEROGENEOS-01` | presentacion-de-resultados |
| 25 | RA4 Automatización del análisis v2: script de todos los análisis principales | `AUTOMATIZACION-ANALISIS-01` | presentacion-de-resultados |
| 26 | RA4 Indicadores v2: ≥5 indicadores de 2+ fuentes | `INDICADORES-01` | presentacion-de-resultados |
| 27 | RA4 Preparación visualización v2: ≥3 conjuntos auto-generados para gráficos | `PREPARACION-VISUALIZACION-01` | presentacion-de-resultados |

Notas de mapeo (v2): los criterios RA3 (Modelado, CRUD, Consultas,
Aggregation), RA1 (Limpieza, Transformación) y RA4 (Respuesta) se
satisfacen con los requisitos ya listados (`MODELO-01`, `PYMONGO-01`,
`CONSULTAS-01`, `AGREGACION-01`, `LIMPIEZA-01`, `TRANSFORM-01`,
`CONCLUSION-01`). Los criterios Tema 8 (sección 16) se evalúan aparte
y se satisfacen con los mismos `MODELO-01`, `PYMONGO-01`,
`CONSULTAS-01`, `AGREGACION-01`, `INDICES-01`, `TRANSACCIONES-01` y
`ENTREGABLES-01`.

`CARGA-SEGURA` y los endurecimientos propios de este proyecto (p. ej.
canónico 18–34) son **extensión propia**: no forman parte de los
descriptores v2 ni de los pesos Tema 8 y no les sustituyen.

---

## Prohibiciones (anti-desvío)

El sistema **MUST NOT**:

- **P-01** Usar datos de compraventa como eje cuando el criterio evalúa el
  alquiler.
- **P-02** Simular valores de salario, alquiler o población: todos los valores
  provienen de las fuentes del contrato.
- **P-03** Usar el alquiler del INE para Euskadi: la API lo devuelve a `null`
  por el régimen foral. El alquiler proviene de Eustat.
- **P-04** Contar con una sola etapa un criterio que exige agregación compleja.
- **P-05** Generar gráficos con valores tecleados a mano.
- **P-06** Escribir en un lenguaje distinto de Python los programas del reto.
- **P-07** Dejar credenciales en el repositorio (`.env`, `api.txt`).
- **P-08** Marcar un criterio como cubierto sin una verificación observable.

---

## Indicador canónico de esfuerzo (enmienda 2026-11-04, 18-34)

El indicador canónico de esfuerzo joven es `esfuerzo_joven_pct_18_34`
(`alquiler_anual / renta_joven_estimada_18_34 × 100`, base municipal fiscal),
donde `renta_joven_estimada_18_34 = renta_municipal_18plus × (renta_media_18_34_CAE / renta_media_18plus_CAE)`
con ponderación por anchura sobre bandas Eustat CAE 2024 18-19 (2 años),
20-24 (5), 25-29 (5) y 30-34 (5):
`ratio_18_34 = (2×1599 + 5×8156 + 5×20109 + 5×25609)/17/28170`.
Los subgrupos `renta_joven_estimada_18_24` y `renta_joven_estimada_25_34` son
escalares CAE sobre la renta municipal (mismo ratio nacional); el ranking
municipal por edad es idéntico entre subgrupos y **no** se interpreta como
renta municipal por edad. `esfuerzo_joven_pct` (base `renta_joven_estimada_16_29`)
queda como legacy para comparabilidad hasta archive. `esfuerzo_ovj_referencia_pct`
(salario OVJ neto 2024, constante autonómica) es una referencia y **no se usa
para ordenar municipios**. Las variantes antiguas en fracción
(`esfuerzo_renta_*`) quedan retiradas.

## JOVEN-18-34 — Canónico de renta y emancipación

El sistema SHALL usar de 18 a 34 años como canónico de renta y
emancipación joven. La renta SHALL construirse con bandas Eustat CAE
18-19, 20-24, 25-29 y 30-34 y ponderación explícita por anchura. Los
subgrupos 18-24 y 25-34 SHALL ser escalares CAE, no tasas municipales.

#### Scenario: Renta 18-34 con ponderación explícita

- GIVEN Eustat CAE 2024 con 1599, 8156, 20109, 25609 y total 28170
- WHEN se calcula `renta_joven_estimada_18_34`
- THEN `ratio = (2*1599+5*8156+5*20109+5*25609)/17/28170`
- AND el nivel municipal es renta municipal 18+ por ratio

#### Scenario: Subgrupos CAE sin fingir municipal

- GIVEN bandas 18-24 y 25-34 CAE
- WHEN se calculan `renta_joven_estimada_18_24` y `_25_34`
- THEN ambos son escalares CAE sobre renta municipal
- AND el ranking municipal por edad se declara idéntico

#### Scenario: Esfuerzo 18-34 etiquetado

- GIVEN `renta_18_34` y `alquiler_anual`
- WHEN se calcula `esfuerzo_joven_pct_18_34`
- THEN el campo se guarda y el `esfuerzo_16_29` legacy se conserva

#### Scenario: Paro y población no renombrados

- GIVEN paro_menores_25 y población 0-19/20-64
- WHEN se migra a 18-34
- THEN paro y población mantienen sus bandas reales
- AND `poblacion_18_34_est` se etiqueta como estimación

---

## Regla de lectura (contract-first)

Antes de escribir o modificar código, la sesión **MUST**:

1. Leer `openspec/specs/contrato-reto/spec.md`.
2. Identificar qué requisitos toca el cambio.
3. Confirmar que cada criterio afectado queda verificable.

La verificación se registra en `tests/test_contrato.py` (escenarios
comprobables) y en el informe de resultados (criterios de proceso).
