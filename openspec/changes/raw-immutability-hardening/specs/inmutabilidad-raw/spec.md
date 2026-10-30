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
