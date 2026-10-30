# Extracción de datos — Especificación

**Capacidad:** `extraccion-datos`
**Estado:** Desplegada
**Criterios cubiertos:** BDA-RA1 Extracción (10), BDA formato JSON/CSV,
objetivo 2 (salarios/población), requisito "todo en Python"
**Contrato:** `../contrato-reto/spec.md`

---

## Purpose

Recoger datos reales de vivienda en alquiler en Euskadi mediante **API y
scraping**, más información complementaria (salarios, población e indicadores),
y guardarlos en formato JSON o CSV, todo en Python.

Las fuentes concretas citadas (Eustat, INE, Fotocasa, euskadi.eus, b5m) son
la instancia de este proyecto; el reto exige automatizar una API y un
scraping, no unas fuentes fijas ni un esquema universal.

---

## Requirements

### Requirement: EXTRACCION-01 — Automatiza una API y scraping

El sistema SHALL obtener los precios del alquiler automatizando **a la vez**
una API y un scraping, y SHALL guardar la respuesta original junto con la forma
parseada.

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

#### Scenario: Las fuentes son independientes

- GIVEN Eustat, INE, euskadi.eus, b5m y Fotocasa
- WHEN una fuente deja de responder
- THEN las demás siguen aportando datos
- AND el fallo queda registrado sin abortar la extracción completa

### Requirement: FORMATO-01 — JSON o CSV

Todo dato extraído SHALL guardarse en JSON o CSV, con metadatos de fuente,
fecha y número de registros.

#### Scenario: Todo dato es JSON o CSV

- GIVEN cualquier fuente del contrato
- WHEN se guarda
- THEN el fichero es JSON o CSV válido
- AND su nombre indica la fuente y el contenido

### Requirement: COMPLEMENTARIOS-01 — Salarios y población

El sistema SHALL incluir información complementaria de **salarios**, población
y al menos otro indicador relevante.

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

#### Scenario: Un script reproduce una fuente

- GIVEN un script de extracción
- WHEN se ejecuta con el Python del proyecto
- THEN descarga y guarda los datos
- AND puede repetirse sin romperse
