# Contrato del Reto SBD + BDA — Especificación

**Capacidad:** `contrato-reto`
**Estado:** Aceptado — vinculante
**Fecha:** 2026-10-23
**Fuente de verdad:** `RETO 1Evaluacion SBD-BDA.pdf` (rúbrica y requisitos)
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

### SBD — RA3. Gestión, almacenamiento y consultas en MongoDB

| Criterio | 0 puntos | 3 puntos | 7 puntos | **10 puntos** |
|---|---|---|---|---|
| Modelado MongoDB | No crea la BD | Crea una colección sin estructura definida | Diseña colecciones con campos adecuados | **Justifica el modelo y las relaciones entre datos** |
| Operaciones PyMongo | No realiza operaciones | Inserta documentos | Inserta, actualiza y elimina documentos | **Además, automatiza las operaciones y comprueba resultados** |
| Consultas | No realiza consultas | Realiza consultas simples | Utiliza filtros, proyecciones y ordenaciones | **Combina condiciones y consultas sobre campos anidados o arrays** |
| Aggregation Pipeline | No utiliza agregaciones | Utiliza $match y $group | Utiliza al menos cuatro etapas diferentes | **Combina varias etapas para obtener indicadores complejos** |

### SBD — RA4. Visualización y presentación de resultados

| Criterio | 0 puntos | 3 puntos | 7 puntos | **10 puntos** |
|---|---|---|---|---|
| Gráficos | No crea gráficos | Presenta un gráfico | Presenta tres tipos de gráficos | **Presenta tres tipos adecuados a los datos** |
| Datos utilizados | No utiliza datos reales | Introduce valores manualmente | Obtiene los datos de MongoDB | **Genera gráficos directamente a partir de consultas PyMongo** |
| Presentación | No presenta resultados | Presenta gráficos sin títulos | Incluye títulos, unidades y leyendas cuando proceda | **Además, los gráficos facilitan la comparación entre municipios** |
| Interpretación | No interpreta | Describe lo que aparece | Explica tres resultados relevantes | **Relaciona resultados y explica sus implicaciones** |

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
| 8 | Agregación: ≥4 etapas, indicadores complejos | `AGREGACION-01` | mongodb-y-analisis |
| 9 | Gráficos: ≥3 tipos adecuados | `GRAFICOS-01` | presentacion-de-resultados |
| 10 | Datos: gráficos desde consultas PyMongo | `DATOS-PYMONGO-01` | presentacion-de-resultados |
| 11 | Presentación: títulos, unidades, leyendas, comparar | `PRESENTACION-01` | presentacion-de-resultados |
| 12 | Interpretación: relaciona y explica | `INTERPRETACION-01` | presentacion-de-resultados |
| 13 | Salarios / población / indicadores | `COMPLEMENTARIOS-01` | extraccion-datos |
| 14 | Formato JSON o CSV | `FORMATO-01` | extraccion-datos |
| 15 | Limpieza: incompletos, duplicados, incorrectos | `LIMPIEZA-01` | mongodb-y-analisis |
| 16 | Transformaciones en MongoDB | `TRANSFORM-01` | mongodb-y-analisis |
| 17 | Resultado final: municipios y por qué | `CONCLUSION-01` | presentacion-de-resultados |
| 18 | Todo en Python | `PYTHON-01` | extraccion-datos |

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

## Regla de lectura (contract-first)

Antes de escribir o modificar código, la sesión **MUST**:

1. Leer `openspec/specs/contrato-reto/spec.md`.
2. Identificar qué requisitos toca el cambio.
3. Confirmar que cada criterio afectado queda verificable.

La verificación se registra en `tests/test_contrato.py` (escenarios
comprobables) y en el informe de resultados (criterios de proceso).
