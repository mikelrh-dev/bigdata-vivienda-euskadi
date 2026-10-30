# Delta for Extracción de datos

## ADDED Requirements

### Requirement: EXTRACCION-TEMP-01 — Temp dir seguro en Windows

El sistema SHALL resolver el directorio temporal bajo el proyecto o
`tempfile.gettempdir()`, creando los directorios necesarios, y SHALL NOT
hardcodear `/tmp`.

#### Scenario: Temp bajo proyecto/gettempdir

- GIVEN `22_geo_areas_funcionales.py`
- WHEN resuelve el temp dir
- THEN usa `tempfile.gettempdir()` o un path bajo el proyecto
- AND crea el directorio si no existe

#### Scenario: Sin /tmp hardcodeado

- GIVEN el código fuente
- WHEN se escanea
- THEN no aparece `/tmp` como literal
- AND funciona en Windows sin error de path

### Requirement: EXTRACCION-LOT-01 — Lots dirigidos con nombre único

El sistema SHALL generar nombres de lotes dirigidos con segundos y token de
ejecución (`anuncios_pisos_dirigido_{YYYYMMDDHHMMSS}_{token}.json`), sin
sobrescribir existentes, manteniendo append-only.

#### Scenario: Nombre único por ejecución

- GIVEN dos ejecuciones el mismo día
- WHEN se guardan los lots
- THEN los nombres difieren por segundos y token
- AND no se sobrescribe ningún lote previo

#### Scenario: Sin colisión

- GIVEN un nombre ya existente
- WHEN se intenta guardar con el mismo nombre
- THEN se genera un nuevo nombre único
- AND el lote previo se conserva
