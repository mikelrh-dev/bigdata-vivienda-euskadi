# Extracción de datos — Especificación

**Capacidad:** `extraccion-datos`
**Estado:** Desplegada
**Criterios cubiertos:** BDA-RA1 Extracción (10), BDA formato JSON/CSV,
objetivo 2 (salarios/población), requisito "todo en Python"
**Contrato:** `../contrato-reto/spec.md`
**Fuente de verdad:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` — cotejo 2026-11-05 (objetivos 1-2, líneas 21-22; requisitos BDA líneas 33-36 y requisito Python línea 47; BDA RA1 líneas 72-79; entregable 2 línea 54)

---

## Purpose

Recoger datos reales de vivienda en alquiler en Euskadi mediante **API y
scraping**, más información complementaria (salarios, población e indicadores),
y guardarlos en formato JSON o CSV, todo en Python.

Las fuentes concretas citadas (Eustat, INE, Fotocasa, euskadi.eus, b5m) son
la instancia de este proyecto; el reto exige automatizar una API y un
scraping, no unas fuentes fijas ni un esquema universal.
_Evidencia PDF (sin requisitos nuevos):_ objetivo 1 «Recopilar datos reales
sobre precios de alquiler o compraventa mediante API y web scraping» (PDF
línea 21); objetivo 2 «Obtener información complementaria sobre salarios,
población u otros indicadores que consideréis relevantes» (PDF línea 22);
requisito BDA «Extracción de datos mediante API y scraping» (PDF línea 33) y
«Gestión de datos en formato JSON o CSV» (PDF línea 36); requisito «Todos los
programas desarrollados deberán estar escritos en Python» (PDF línea 47).
Extraído bruto: respuesta original junto con forma parseada (EXTRACCION-01) y
ficheros originales para HDFS (entregable 2, PDF línea 54).

---

## Requirements

### Requirement: EXTRACCION-01 — Automatiza una API y scraping

El sistema SHALL obtener los precios del alquiler automatizando **a la vez**
una API y un scraping, y SHALL guardar la respuesta original junto con la forma
parseada.
_Trazabilidad PDF (cotejo 2026-11-05):_ objetivo 1 (PDF línea 21), requisito
BDA (PDF línea 33) y criterio BDA RA1 Extracción, 10 puntos «Automatiza API y
scraping» (PDF línea 76, tabla líneas 72-79). Extraído bruto: respuesta
original + forma parseada (entregable 2, PDF línea 54, para HDFS).

#### Scenario: La API del proyecto responde datos completos (instancia: Eustat/INE)

- GIVEN la API de Eustat (`bankupx`) y el INE (`wstempus`) en esta instancia
- WHEN se ejecutan los scripts de extracción
- THEN cada tabla se descarga completa y se guarda en `data/raw/`
- AND el número de filas se registra en el log

#### Scenario: El scraping del proyecto produce anuncios reales (instancia: Fotocasa)

- GIVEN las tres provincias (Álava, Bizkaia, Gipuzkoa)
- WHEN se ejecuta el scraper
- THEN se obtienen anuncios únicos con precio, municipio y superficie
- AND el HTML crudo se conserva para poder reparsear sin repetir la descarga

### Requirement: EXTRACCION-02 — No hay fuente única

El sistema SHALL combinar al menos tres fuentes independientes de forma que
ninguna sea insustituible.
_Trazabilidad PDF (cotejo 2026-11-05):_ objetivos 1-2 (PDF líneas 21-22) y
requisito BDA (PDF línea 33). Las tres fuentes son instancia del proyecto
para garantizar datos reales sin fuente única; el PDF exige API y scraping
(2 vías) con fuentes reales, no un número fijo de fuentes.

#### Scenario: Las fuentes son independientes

- GIVEN Eustat, INE, euskadi.eus, b5m y Fotocasa
- WHEN una fuente deja de responder
- THEN las demás siguen aportando datos
- AND el fallo queda registrado sin abortar la extracción completa

### Requirement: FORMATO-01 — JSON o CSV

Todo dato extraído SHALL guardarse en JSON o CSV, con metadatos de fuente,
fecha y número de registros.
_Trazabilidad PDF (cotejo 2026-11-05):_ requisito BDA «Gestión de datos en
formato JSON o CSV» (PDF línea 36).

#### Scenario: Todo dato es JSON o CSV

- GIVEN cualquier fuente del contrato
- WHEN se guarda
- THEN el fichero es JSON o CSV válido
- AND su nombre indica la fuente y el contenido

### Requirement: COMPLEMENTARIOS-01 — Salarios y población

El sistema SHALL incluir información complementaria de **salarios**, población
y al menos otro indicador relevante.
_Trazabilidad PDF (cotejo 2026-11-05):_ objetivo 2 «Obtener información
complementaria sobre salarios, población u otros indicadores que consideréis
relevantes» (PDF línea 22). Extraído bruto: salario real (INE EPA /
Observatorio, no simulado) y población municipal con código INE.

#### Scenario: El salario está presente y es real

- GIVEN que Eustat no publica salario municipal por edad
- WHEN se incorpora el salario
- THEN proviene del INE (EPA, salario medio por grupo de edad) o del dato
  oficial del Observatorio Vasco de la Juventud
- AND el valor NO se simula ni se inventa

#### Scenario: La población por municipio está disponible

- GIVEN la tabla de población de Eustat
- WHEN se extrae
- THEN cada municipio tiene su población y su código INE

### Requirement: PYTHON-01 — Todo en Python

Todos los programas SHALL estar escritos en Python y SHALL ser ejecutables
desde un venv dedicado.
_Trazabilidad PDF (cotejo 2026-11-05):_ «Debéis desarrollar una solución
utilizando Python» (PDF línea 19) y «Todos los programas desarrollados
deberán estar escritos en Python» (PDF línea 47).

#### Scenario: Un script reproduce una fuente

- GIVEN un script de extracción
- WHEN se ejecuta con el Python del proyecto
- THEN descarga y guarda los datos
- AND puede repetirse sin romperse

### Requirement: GATE-JOIN-01 — Nueva fuente con join previo

El sistema MUST NOT crear un extractor nuevo sin antes ejecutar un join real contra dim_municipios 252. La validación SHALL contar municipios alcanzados, filas y códigos INE de 5 dígitos. Solo una cobertura documentada alta autoriza el extractor.
_Trazabilidad (cotejo 2026-11-05):_ extensión propia del proyecto (guardia de calidad para nuevas fuentes), sin cita directa en PDF. No es criterio v2 ni peso Tema 8. Se mantiene como guardia de extraído bruto: provenance (fuente, url, fecha, n_registros, sha256) y manifest regenerado.

#### Scenario: Fuente con cobertura insuficiente no entra

- GIVEN una fuente candidata sin join
- WHEN se evalúa su alta
- THEN el sistema la marca baja
- AND no se crea extractor ni carga en Mongo

#### Scenario: Fuente con cobertura alta entra con provenance

- GIVEN una fuente con municipios alcanzados documentados
- WHEN se aprueba el extractor
- THEN el raw guarda fuente, url, fecha, n_registros y sha256
- AND el manifest se regenera

---

## Evidencia PDF (objetivos, requisitos, extraído bruto — sin SHALL nuevos)
- **Objetivo 1** (PDF línea 21): «Recopilar datos reales sobre precios de
  alquiler o compraventa mediante API y web scraping». Evidencia para
  EXTRACCION-01 y EXTRACCION-02.
- **Objetivo 2** (PDF línea 22): «Obtener información complementaria sobre
  salarios, población u otros indicadores que consideréis relevantes».
  Evidencia para COMPLEMENTARIOS-01.
- **Requisitos BDA** (PDF líneas 33-36): «Extracción de datos mediante API y
  scraping» (PDF línea 33) y «Gestión de datos en formato JSON o CSV»
  (PDF línea 36). Evidencia para EXTRACCION-01 y FORMATO-01.
- **Requisito Python** (PDF línea 47): «Todos los programas desarrollados
  deberán estar escritos en Python» (con PDF línea 19). Evidencia para
  PYTHON-01.
- **Extraído bruto**: respuesta original + forma parseada (EXTRACCION-01) y
  ficheros originales para HDFS (entregable 2, PDF línea 54). GATE-JOIN-01
  garantiza provenance y cobertura previa al extraído bruto nuevo.
- **Nota de fuentes**: las fuentes concretas citadas (Eustat, INE, Fotocasa,
  euskadi.eus, b5m) son la instancia de este proyecto; el reto exige
  automatizar una API y un scraping con datos reales, no unas fuentes fijas
  ni un esquema universal. Se mantiene la nota original del Purpose.

## Mapa trazable PDF → requisito
| Requisito | PDF (líneas) | Criterio rubric / evidencia | Estado (2026-11-05) |
|---|---|---|---|
| EXTRACCION-01 | Objetivo 1 línea 21; requisito BDA línea 33; BDA RA1 línea 76 (líneas 72-79); entregable 2 línea 54 | BDA RA1 Extracción 10 pts «Automatiza API y scraping»; extraído bruto (original + parseada) | SHALL acreditado; fuentes = instancia (Eustat/INE API, Fotocasa scraping). |
| EXTRACCION-02 | Objetivos 1-2 líneas 21-22; requisito BDA línea 33 | Sin fuente única: 3+ fuentes independientes (instancia del proyecto) | SHALL acreditado (5 fuentes reales); el PDF no fija número de fuentes. |
| FORMATO-01 | Requisito BDA línea 36 | «Gestión de datos en formato JSON o CSV» | SHALL acreditado: JSON/CSV con fuente, fecha y n_registros. |
| COMPLEMENTARIOS-01 | Objetivo 2 línea 22 | «Obtener información complementaria sobre salarios, población u otros indicadores» | SHALL acreditado: salarios reales (INE EPA / Observatorio), población municipal con código INE. |
| PYTHON-01 | Líneas 19 y 47 | «Utilizando Python» / «Todos los programas ... escritos en Python» | SHALL acreditado: scripts Python en venv dedicado. |
| GATE-JOIN-01 | Sin cita directa PDF | Extensión propia: join previo contra dim_municipios 252 + provenance | Guardia de calidad (MUST NOT); no es criterio v2 ni peso Tema 8. |
