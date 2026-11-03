# Contrato de datos — Especificación

**Capacidad:** `contrato-datos`
**Estado:** Propuesta (cambio `raw-immutability-hardening`)
**Contrato:** `../extraccion-datos/spec.md`, `../contrato-reto/spec.md`

---

## Purpose

Define el contrato de la capa raw (inmutable por defecto) y de la capa
procesada (salidas aditivas), incluyendo inventario/manifest, esquemas
(`codigo_ine` tipado estricto) y resolución normalizada de municipios.

## Requirements

### Requirement: CONTRATO-RAW-01 — Capa raw inmutable por defecto

El sistema SHALL tratar `data/raw/` como inmutable por defecto. Solo los
scripts de `extract/*` MAY crear nuevos ficheros raw (adquisición). Los
transforms NO SHALL escribir en `data/raw/` salvo opt-in razonado a través
del guard compartido.

#### Scenario: Transform por defecto no toca raw

- GIVEN un transform ejecutado sin flags de mutación
- WHEN finaliza
- THEN no se crea ni modifica ningún fichero bajo `data/raw/`
- AND su salida se escribe en `data/procesado/`

#### Scenario: Escritura raw requiere guard

- GIVEN un transform que necesita escribir raw (p. ej. `f4_pisos_dirigido`)
- WHEN invoca `assert_raw_writable(reason)` con reason no vacío
- THEN la escritura se permite
- AND sin reason (o vacío) se lanza error y no se escribe

### Requirement: CONTRATO-RAW-02 — Manifest completo

El sistema SHALL mantener `docs/raw_manifest_sha256.txt` con una entrada por
cada fichero bajo `data/raw/` (excepto `.FROZEN`, `.gitkeep`,
`ingestion_manifest.json`), sin huérfanos ni faltantes.

#### Scenario: Sin huérfanos en el manifest

- GIVEN el árbol `data/raw/`
- WHEN se ejecuta el test de contrato
- THEN todo fichero raw (salvo excepciones) aparece en el manifest
- AND todo hash del manifest coincide con el fichero

#### Scenario: Drift reconciliado

- GIVEN el manifest con conteo previo desfasado (312 vs 317)
- WHEN se reconcilia
- THEN el conteo del manifest coincide con los ficheros existentes

### Requirement: CONTRATO-RAW-03 — `codigo_ine` tipado estricto

El sistema SHALL tipar `codigo_ine` como string de exactamente 5 caracteres
(zfill), preservando nulos como `None`/vacío, en todos los ficheros raw y
procesados.

#### Scenario: Código válido

- GIVEN un registro con municipio resuelto
- WHEN se persiste
- THEN `codigo_ine` es string de longitud 5 con prefijo de provincia
  (`01`, `20` o `48`)
- AND no se convierte a entero ni se pierden ceros a la izquierda

#### Scenario: Nulo preservado

- GIVEN un registro sin municipio resuelto
- WHEN se persiste
- THEN `codigo_ine` es `None` o vacío
- AND no se interpreta como `0` ni `00000`

### Requirement: CONTRATO-PROC-01 — Dedup determinista del canónico

El sistema SHALL deduplicar `anuncios_unificados.csv` por `(portal, id_anuncio)`
con entrada ordenada, prioridad explícita y reporte de duplicados, de forma
reproducible.

#### Scenario: Dedup reproducible

- GIVEN la misma entrada en distinto orden
- WHEN se unifica
- THEN el conjunto resultante y el orden son idénticos
- AND se emite un reporte de duplicados eliminados

#### Scenario: Prioridad explícita

- GIVEN duplicados con campos distintos
- WHEN se deduplica
- THEN se conserva el registro según la prioridad documentada
- AND no se pierden filas no duplicadas

### Requirement: CONTRATO-PROC-02 — Salidas aditivas

El sistema SHALL garantizar que toda salida derivada de
`anuncios_unificados.csv` tenga al menos las mismas columnas que el canónico;
las nuevas features se añaden como columnas adicionales o ficheros separados,
nunca reduciendo.

#### Scenario: Superset de columnas

- GIVEN un fichero derivado (`*_enriquecido`, `*_filtrado`, etc.)
- WHEN se compara con `anuncios_unificados.csv`
- THEN sus columnas son superset del canónico
- AND no se eliminan columnas del canónico

#### Scenario: Reducción prohibida

- GIVEN un transform que reescribe el canónico
- WHEN intenta guardar con menos columnas
- THEN la operación falla (guardrail)
- AND el canónico conserva su esquema

### Requirement: CONTRATO-RESOLVE-01 — Resolución normalizada de municipios

El sistema SHALL resolver municipios usando claves normalizadas con `norm()`
(ascii, minúsculas, espacios normalizados) tanto en el mapa de dimensión como
en `MANUAL_MAP`, de modo que variantes acentuadas y con barra resuelvan al
código canónico, con fallback fuzzy.

#### Scenario: Variante acentuada resuelve

- GIVEN municipio `"Donostia/San Sebastián"` o `"Donostia - San Sebastián"`
- WHEN se resuelve
- THEN devuelve el código INE canónico de Donostia/San Sebastián
- AND sin depender del fallback fuzzy

#### Scenario: Variante con barra/slash

- GIVEN municipio `"Arrasate/Mondragón"` o `"Arrasate - Mondragon"`
- WHEN se resuelve
- THEN devuelve el código INE canónico de Arrasate/Mondragón

#### Scenario: Fallback fuzzy

- GIVEN un municipio sin coincidencia exacta
- WHEN se resuelve
- THEN se aplica el fallback fuzzy con umbral >= 0.85
- AND si no supera el umbral devuelve `None, None`


---

# Inmutabilidad raw — Especificación

**Capacidad:** `inmutabilidad-raw`
**Estado:** Propuesta (cambio `raw-immutability-hardening`)

---

## Purpose

Hacer raw inmutable por diseño: defaults seguros (silver), opt-in razonado
para mutación raw, guard compartido y guardrails estáticos que impiden que
transforms escriban raw.

## Requirements

### Requirement: INMUT-01 — Default silver en enriquecer_codigo_ine

El sistema SHALL hacer que `enriquecer_codigo_ine.py` escriba por defecto en
`data/procesado/` (silver) y NO en `data/raw/`, salvo opt-in explícito.

#### Scenario: Default no toca raw

- GIVEN ejecución sin flags
- WHEN finaliza
- THEN los ficheros enriquecidos se escriben en `data/procesado/`
- AND `data/raw/` no se modifica

#### Scenario: Aviso de deprecación

- GIVEN un caller que invoca con el comportamiento legacy (raw in-place)
- WHEN se ejecuta
- THEN se emite aviso de deprecación
- AND se mantiene `--force`/`--write-raw` para el procedimiento documentado

### Requirement: INMUT-02 — Guard compartido `assert_raw_writable`

El sistema SHALL proveer `transform/_raw_guard.py` con
`assert_raw_writable(reason)` que exige un reason no vacío y documenta la
intención antes de cualquier escritura raw desde un transform.

#### Scenario: Reason válido permite escritura

- GIVEN `assert_raw_writable("f4 directed scrape lot")`
- WHEN se llama
- THEN no lanza excepción
- AND queda registrado el motivo

#### Scenario: Reason vacío bloquea

- GIVEN `assert_raw_writable("")` o `None`
- WHEN se llama
- THEN lanza excepción
- AND no se realiza escritura

### Requirement: INMUT-03 — Sin writes raw en transforms

El sistema SHALL garantizar mediante guardrail estático (AST/grep) que ningún
fichero en `transform/*.py` escriba en `data/raw/` fuera de la allow-list
(`f4_pisos_dirigido.py` vía guard).

#### Scenario: Scan estático pasa

- GIVEN el conjunto de transforms
- WHEN se ejecuta el guardrail
- THEN no se detectan escrituras raw no autorizadas
- AND `f4_pisos_dirigido.py` aparece solo vía `_raw_guard`

#### Scenario: Nuevo script no autorizado falla

- GIVEN un transform nuevo que escribe en `data/raw/`
- WHEN se ejecuta el guardrail
- THEN el test falla
- AND se lista el fichero infractor

### Requirement: INMUT-04 — Opt-in razonado para mutación raw

El sistema SHALL exigir `--write-raw --reason <texto>` para que un transform
escriba raw, y SHALL re-ejecutar el procedimiento de re-congelación.

#### Scenario: Flags completos permiten mutación

- GIVEN `--write-raw --reason "re-freeze after source update"`
- WHEN se ejecuta
- THEN se permite la escritura raw
- AND se documenta el motivo

#### Scenario: Flag incompleto bloquea

- GIVEN solo `--write-raw` sin `--reason`
- WHEN se ejecuta
- THEN se aborta con error
- AND raw no se modifica


---

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

