# Diferencias entre mi versión y `VersionAlex` — auditoría de capas y reconstrucción

**Fecha:** 2026-11-11
**Alcance:** comparar tu árbol (`bigdata-vivienda-euskadi/`) con
`VersionAlex/bigdata-vivienda-euskadi-refactor-separar-capas-pipeline/bigdata-vivienda-euskadi-refactor-separar-capas-pipeline/`
en todo lo relativo a **quién escribe en `data/raw/`** y a **qué se puede reconstruir** al borrar `data/procesado/` y `data/resultados/`.
**Naturaleza:** análisis de solo lectura. No se ha modificado código ni datos.

---

## 0. Método

La exploración se organizó en dos líneas independientes (los "dos subagentes"):

| Línea | Pregunta | Evidencia usada |
|---|---|---|
| **A — Integridad de capas** | ¿Quién escribe en `raw`? ¿Se respeta la inmutabilidad? ¿Qué scripts escriben en la capa equivocada? | Lectura de los 39 extractores y 34/32 transforms, `transform/_raw_guard.py`, regex de escrituras, `tests/test_raw_guardrails.py`, `tests/test_raw_inmutable.py` |
| **B — Reconstrucción** | Si borro `procesado/` y `resultados/`, ¿qué vuelve y con qué comando? | `SCRIPTS`/`EXCLUIDOS`/`BASES` de ambos `run_all.py`, README, CI, `transform/quality/`, ejecución real de tests |

Herramientas: `codegraph` (índice ya existente en la raíz), diff recursivo entre árboles,
auditoría programática de las declaraciones `in`/`out` contra el disco y ejecución de tests
focalizados con `.venv/Scripts/python.exe`.
No se usó Context7: el problema es de arquitectura interna del repo, no de comportamiento
de una librería externa.

**Resultado de las comprobaciones ejecutadas**

```
TU VERSIÓN   tests/test_run_all.py + test_raw_guardrails.py + test_raw_inmutable.py → 15 passed
ALEX         tests/test_run_all.py + test_quality_metadata.py                     → 10 passed
ALEX         tests/test_raw_guardrails.py + test_raw_inmutable.py                 → 6 failed
```

Los 6 fallos de Alex **no son de código**: su copia tiene `data/raw/` vacío (0 ficheros),
así que los tests que exigen `.FROZEN` y el manifiesto raw fallan por entorno. Es decir,
la refactorización no se validó sobre una copia con datos.

---

## 1. Qué es cada árbol

- **Tu versión (raíz):** es el `HEAD` del repo (`a29abeb`, "rebuild limpio de transform (4 fallos) + auditoria v10"). 34 scripts en el DAG, 8 excluidos, bases `raw`/`proc`/`res`, 356 ficheros en `data/raw`, manifiesto canónico en `docs/raw_manifest_sha256.txt`.
- **`VersionAlex`:** copia posterior (11-nov) del refactor "separar capas". No tiene `.git` propio, no trae `openspec/`, no trae datos. 32 scripts en el DAG, 6 excluidos, bases solo `raw`/`proc`, `transform/quality/` nuevo, `f4_pisos_dirigido.py` movido a `extract/`, figuras/mapas/auditorías movidos de `transform/` a `analysis/`.

Las dos versiones comparten historia: el commit v10 de la raíz y la copia de Alex **no son la misma línea**. Alex contiene algunas correcciones que tú ya tenías (F-04) y **le faltan otras que tú ya tenías** (F-03). Por eso no se puede decir "Alex es más nuevo, adoptemos todo".

---

## 2. Línea A — Integridad de la capa raw

### 2.1 Lo que Alex hace bien (y deberíamos conservar)

| # | Cambio | Por qué importa |
|---|---|---|
| A+1 | `transform/f4_pisos_dirigido.py` → `extract/f4_pisos_dirigido.py` | Es una **captura externa** (scraper): su sitio natural es `extract/`. Antes vivía en `transform/` y escribía en `raw` con una excepción en el guardarraíl (`EXCLUIDOS` + allowlist de test). Ahora el DAG Silver ya no tiene ninguna excepción. |
| A+2 | `extract/{normalizar_metadata,generar_manifest,generar_ingestion_manifest}.py` → `transform/quality/` | Producían **silver** (`_meta/`, manifiestos) desde la capa de extracción. Es una violación de capas real y era una de las razones por las que "solo `transform/run_all.py`" no reconstruía `procesado/`. Ahora están en la capa correcta. |
| A+3 | `extract/_common.py`: elimina el `mkdir` de `raw/procesado/resultados` al importar | **Importar un helper ya no crea ni muta capas.** Es la corrección de higiene más importante del lote: evita que un simple `import _common` "resucite" directorios que el usuario había borrado. |
| A+4 | `transform/run_all.py`: `BASES` sin `res` y `_resolver` lanza `ValueError` ante base desconocida | El DAG Silver ya no puede escribir en `resultados/` por accidente. Antes caía silenciosamente en `PROCESADO_DIR` (`root = BASES.get(base, PROCESADO_DIR)`), que es justo el tipo de fallback que enmascara errores. Hay test nuevo: `test_dag_solo_resuelve_raw_y_proc`. |
| A+5 | Nuevo `test_no_transform_writes_resultados` y retirada de la excepción de `f4_pisos_dirigido` en `verificar_fase_datos.py` (check 15) | Refuerza por test lo que antes era una convención. |
| A+6 | README: "`data/raw/`: capturas originales; **no es una salida regenerable del transform**" | Es la formulación correcta del contrato. Debe quedarse. |

### 2.2 Regresiones y roturas de buenas prácticas

#### R1 (crítico) — `run_all.py --check` vuelve a dar falso verde cuando falta un raw

Alex revirtió la comprobación de existencia de entradas declaradas:

```python
# Alex, transform/run_all.py (_estado)
ausentes = [ref for ref in SCRIPTS[script].get("in", [])
            if not any(ch in ref for ch in ("*", "?", "[")) and not _resolver(ref)]
```

`_resolver()` **siempre** devuelve una lista no vacía para una ref concreta (exista o no el
fichero), así que `not _resolver(ref)` es siempre `False` y `ausentes` siempre queda vacío.
Además eliminó el test que lo protegía
(`test_estado_entrada_inexistente_no_da_falso_ok`).

Demostración ejecutada sobre su propio `run_all.py`:

```
raw/x.csv exists? False
estado: ('OK', '1 salidas al día')
```

Esto es **exactamente el fallo que estabais investigando**: si `raw` pierde ficheros,
el orquestador dice que todo está al día y no lo detectas hasta que un script falla o,
peor, produce un CSV vacío. Tu versión sí lo detecta (`_resolver(ref)[0].exists()`),
y por eso ese test existe.

#### R2 (alto) — `extract/26_vpo_terminadas.py` pierde la protección append-only

Tu versión:

```python
def promover(payload):
    nuevo = _sha256_bytes(payload)
    if RAW_CSV.exists():
        actual = _sha256(RAW_CSV)
        if actual == nuevo:  return RAW_CSV, False   # idempotente
        raise SystemExit(...)                        # SHA distinto -> no sobrescribe
```

Alex:

```python
def escribir_raw(contenido):
    assert_raw_writable("...")      # solo exige reason + .FROZEN
    RAW_CSV.write_bytes(contenido)  # sobrescribe siempre
```

El guardarraíl sigue ahí, pero **se ha perdido la semántica de inmutabilidad**: ya no se
compara el SHA ni se rechaza un contenido distinto. `raw` pasa de "append-only verificado"
a "sobrescribible con una razón". También desaparecen `--promote` / `--desde-raw`.

#### R3 (alto) — `extract/f4_pisos_dirigido.py` escribe derivados en raw en cada ejecución

En Alex:

```python
guardar_json(RAW_DIR / "anuncios_pisos_dirigido.json", viejos, ...)   # merge acumulado
open(RAW_DIR / "anuncios_pisos_dirigido.csv", "w")                    # reescritura
open(RAW_DIR / "f4_pisos_informe.csv", "w")                           # informe QA
```

- El **merge acumulado** de `anuncios_pisos.json` + lote nuevo es un producto derivado, no
  una captura: en `raw` no debería vivir.
- Los tres se abren en modo `w`: **se sobrescriben en cada pasada**. Se ha movido el script
  a la capa correcta, pero se ha metido un escritor no inmutable dentro de `raw`.
- Tu versión escribía el merge y el informe en `procesado/`, que es su sitio.

Corolario: la regla "solo `extract` escribe en raw" no basta; hace falta "solo escribe
**capturas nuevas e inmutables**".

#### R4 (alto) — contrato roto de los objetivos F4

Alex cambió el **consumidor** y no el **productor**:

| Pieza | Tu versión | Alex |
|---|---|---|
| `extract/09_fotocasa_dirigido.py` lee objetivos de | `procesado/f4_pisos_objetivo.json` | **`raw/f4_pisos_objetivo.json`** |
| `transform/generar_f4_pisos_objetivo.py` escribe en | `procesado/` | `procesado/` (sin cambios) |
| `extract/f4_pisos_dirigido.py` lee objetivos de | `procesado/` | `procesado/` |

Nadie genera `raw/f4_pisos_objetivo.json`. El código hace `if objetivos_path.exists(): ... else: usar todos`, así que **degrada en silencio**: la captura dirigida deja de ser dirigida y
nadie se entera. Es una regresión funcional además de una inconsistencia de capas.

#### R5 (medio) — el manifiesto canónico de raw se mueve a un directorio ignorado y sin productor

- Tu versión: `extract/generar_manifest.py --write` escribe `docs/raw_manifest_sha256.txt`
  (versionado en git) y además una copia silver. `tests/test_raw_inmutable.py` y
  `scripts/verificar_fase_datos.py` verifican contra `docs/`.
- Alex: `CANONICAL = data/raw/manifest_sha256.txt`, y el `--write` **ya no lo genera**
  ("verifica Raw y Silver; escribe solo el manifiesto Silver"). `.gitignore` ignora
  `data/raw/*`.

Consecuencia: la **única referencia externa** que permitía demostrar que `raw` ha perdido
ficheros desaparece con `raw`. Si el fallo original era "parte de los datos de raw dejaron
de estar", esta decisión **elimina el detector del fallo**.

#### R6 (medio) — los scripts de `transform/quality/` quedan huérfanos

Se mueven a la capa correcta, pero:

- no están en `SCRIPTS` de `run_all.py` (el orquestador usa un registro explícito, no escanea subdirectorios);
- no se mencionan en el README;
- no están en el CI.

Solo los ejecutan los tests con `tmp_path`. Es decir: **el problema que motivó el refactor
(`procesado/` no reconstruible con un comando) sigue igual** para `_meta/`,
`ingestion_manifest.json` y `manifest_sha256.txt`; ahora simplemente están mejor colocados.

#### R7 (medio) — se revierten correcciones del DAG que tú ya tenías

| Script | Tu versión | Alex | Efecto |
|---|---|---|---|
| `generar_cert_energetico_municipal.py` | `in: [raw:certificados_energeticos_*_completo.csv, proc:dim_municipios.csv]` | `in: []` | Sin aristas: puede ejecutarse antes que su entrada real (es el F-03 del informe v10) |
| `generar_cert_energetico_moda_municipio.py` | `in: [proc:cert_energetico_municipal_252.csv]` | `in: []` | Fallo en cascada del anterior |
| `generar_analisis_variables_base.py` | `in: [... proc:udalmap_empleo_corregido.csv ...]` | `in: [... raw:udalmap_empleo_corregido.csv ...]` | El script lee `PROC` (`generar_analisis_variables_base.py:71`), así que la declaración es falsa y `--check` ordena mal |
| `normalizar_json_crudos.py` | caso especial para huérfano glob→glob | eliminado | Falsos `DESACTUALIZADO` |
| `verificar_gobernanza.py` | existe y asserta 34 nodos DAG / 50 cabeceras | **eliminado** | Se pierde el assert; el DAG baja a 32 sin decisión documentada |

#### R8 (bajo) — efectos secundarios menores

- `extract/_common.py` sin `mkdir`: correcto como principio, pero algunos extractores que
  hacen `df.to_csv(RAW_DIR / ...)` sin `mkdir` fallarán en un clon limpio en vez de crear
  el directorio. Es aceptable (fail-fast), pero conviene documentarlo.
- `filtrar_outliers.py`: se retira `proc:log_filtrado.txt` de `out` (queda solo en glob).
- `deduplicar_alquiler_enriquecido.py`: Alex lo convierte en nodo real con productor
  (`enriquecer_codigo_ine.py` declara las salidas). **Esto sí es mejor que tu parche de
  "saltar si no existe"** y es adoptable.

---

## 3. Línea B — ¿Se puede reconstruir todo?

### 3.1 Estado real de las declaraciones

Comprobado importando ambos `run_all.py` y contrastando con el disco:

| Métrica | Tu versión | Alex |
|---|---|---|
| Scripts en `SCRIPTS` | 34 | 32 |
| Excluidos | 8 | 6 |
| Bases declaradas | `raw`, `proc`, `res` | `raw`, `proc` |
| Salidas `res:` | 2 | 0 |
| Entradas `raw:` concretas ausentes en disco | **0** | 16 (su copia no tiene datos; no evaluable) |
| Salidas `proc:` que además existen en `raw` | **5** (`alquiler_seccion.csv`, `dim_municipios.csv/.json`, `distancias_capitales_252.csv`, `distancias_haversine_252.csv`) | 0 (sin datos) |

Las 5 duplicaciones de tu versión son relevantes: hay **artefactos derivados congelados
dentro de `raw`**. No rompen la ejecución, pero son la razón por la que "raw" no es
estrictamente "solo capturas": si alguien regenera `raw` desde cero, esos 5 no vuelven.

### 3.2 Ficheros de raw que **ningún script del repo produce**

Búsqueda de producto en todo el código (excluyendo `data/`):

| Fichero en `data/raw/` | Productor | Estado |
|---|---|---|
| `eustat_pib_municipal.csv/.json` | — | Solo aparece en manifiestos y auditorías |
| `eustat_tenencia.csv/.json` | — | Ídem |
| `emal_fianzas_ampliado.csv/.json` | — | Solo lo **lee** `scripts/verificacion_crudos.py` |
| `alquiler_municipio_original.csv` | — | Captura manual; `02_eustat_alquiler.py` genera otros `alquiler_*_original.csv` |

Esto confirma el diagnóstico de fondo: **`raw` no es una salida regenerable**. No es un bug
de un script concreto, es un contrato que hay que declarar y proteger. La respuesta correcta
no es "que todo se regenere", sino:

1. `raw` es un artefacto congelado, versionado fuera de git (HDFS / copia firmada).
2. Un manifiesto **externo a `raw`** demuestra integridad y detecta pérdidas.
3. `transform` nunca escribe en `raw`, y `extract` solo añade capturas inmutables.
4. Todo lo demás (`procesado`, `resultados`) se reconstruye desde `raw` con un comando.

### 3.3 Lo que sigue sin tener orquestador

| Producto | Productor | ¿Lo ejecuta un orquestador? |
|---|---|---|
| `procesado/_meta/*`, `ingestion_manifest.json` | `transform/quality/*` | **No** (ni en tu versión ni en Alex) |
| `procesado/manifest_sha256.txt` | `transform/quality/generar_manifest.py --write` | **No** |
| `resultados/*.csv`, PNG | `analysis/run_analisis_mongo.py`, `analysis/sensibilidad.py`, `analysis/generar_figuras_N.py` | **No** (solo Mongo, manual) |
| `resultados/dashboard*.html` | manual | **No** |
| `raw/manifest_sha256.txt` (Alex) | nadie | **No** |

Alex mejora la **pureza** del DAG (quitó `res`), pero **no añade el orquestador extremo a
extremo** que resuelve tu problema original. El README de Alex sigue diciendo que
`transform/run_all.py` genera procesado, sin mencionar `quality/`.

---

## 4. Veredicto

**¿Aporta la versión de Alex?** Sí, en cuatro decisiones que son claramente mejores y
deberían integrarse:

1. `f4_pisos_dirigido` en `extract/`.
2. `quality/` fuera de `extract/` (a `transform/quality/`).
3. `_common` sin efectos secundarios al importar.
4. `run_all` sin base `res:` y con error ante base desconocida; más el nodo real de
   `deduplicar_alquiler_enriquecido` con productor declarado.

**¿Arregla el fallo?** **No.** Arregla la *colocación* de las piezas, pero deja sin resolver
la *reconstrucción* (`quality/` huérfano, `resultados/` sin orquestador) y **introduce tres
regresiones que atacan directamente al fallo investigado**:

- `--check` da falso verde cuando falta un raw (R1),
- se pierde la inmutabilidad verificada por SHA en VPO (R2),
- el manifiesto canónico de raw deja de ser generable y deja de vivir fuera de `raw` (R5).

**¿Tiene arreglo?** Sí. Es un problema de diseño acotado y verificable, no de datos
irrecuperables. Plan abajo.

---

## 5. Plan de corrección propuesto

### P0 — Restaurar los guardarraíles (1–2 h)

1. **`transform/run_all.py::_estado`**: volver a
   `not _resolver(ref)[0].exists()` y restaurar
   `tests/test_run_all.py::test_estado_entrada_inexistente_no_da_falso_ok`.
   *Criterio de aceptación:* el test falla con el código de Alex y pasa con el arreglo.
2. **`extract/26_vpo_terminadas.py`**: recuperar `promover()` con comparación de SHA
   (idempotente si coincide, `SystemExit` si difiere). Mantener `assert_raw_writable`.
   *Criterio:* dos ejecuciones seguidas no reescriben; un payload distinto aborta.
3. **`extract/f4_pisos_dirigido.py`**: escribir en `raw` **solo** el lote nuevo
   (`anuncios_pisos_dirigido_lote.json`). Mover el merge
   (`anuncios_pisos_dirigido.json/.csv`) y `f4_pisos_informe.csv` a `procesado/`.
   *Criterio:* un test que ejecute `main()` con `tmp_path` y compruebe que en `raw` solo
   aparece el lote y que dos ejecuciones no cambian bytes de ficheros existentes.

### P1 — Cerrar el contrato entre capas (medio día)

4. **Objetivos F4**: elegir un único sitio. Recomendado `procesado/` (es configuración
   derivada, no captura) y que lo lean **los dos** consumidores
   (`extract/09_fotocasa_dirigido.py` y `extract/f4_pisos_dirigido.py`).
   *Criterio:* test que verifique que productor y consumidores coinciden; si el fichero no
   existe, fallar explícitamente en vez de degradar a "todos los municipios".
5. **Manifiesto canónico**: volver a `docs/raw_manifest_sha256.txt` (versionado) y que
   `generar_manifest.py --write` lo regenere. `raw/manifest_sha256.txt` puede quedar como
   copia de conveniencia, nunca como fuente de verdad.
   *Criterio:* `pytest tests/test_manifest_sha.py tests/test_raw_inmutable.py` en verde en
   un clon sin `data/raw` (los tests que requieren datos deben hacer `skip` explícito, no
   fallar por entorno).
6. **`transform/quality/`**: añadirlo al DAG (grupo `quality`) o a un orquestador de fase.
   Si se añade al DAG, actualizar `verificar_gobernanza.py` y las cifras de README.
   *Criterio:* `run_all.py --dry-run` muestra `normalizar_metadata`, `generar_ingestion_manifest`
   y `generar_manifest` en orden, después de los scripts que producen sus entradas.

### P1 — Un único punto de entrada reproducible

7. **`scripts/run_pipeline.py`** con fases explícitas y `--check`:

```text
--fase raw        verifica manifiesto + .FROZEN (solo lectura; nunca descarga)
--fase silver     transform/run_all.py
--fase quality    transform/quality/*.py
--fase mongo      scripts/run_mongo_pipeline.py
--fase gold       analysis/run_analisis_mongo.py + sensibilidad + figuras
--fase all        silver → quality → mongo → gold
```

   *Criterio de aceptación:* desde un `raw` íntegro y `procesado/`+`resultados/` borrados,
   `python scripts/run_pipeline.py --fase all --check` lista exactamente los productos que
   se van a generar, y una ejecución posterior produce un `run_manifest` con 0 fallos y
   compara el inventario final contra el esperado.

### P2 — Declarar y proteger lo no regenerable

8. Documento `docs/raw_no_regenerable.md` con la lista de ficheros de `raw` sin productor
   (`eustat_pib_municipal`, `eustat_tenencia`, `emal_fianzas_ampliado`,
   `alquiler_municipio_original`, `alquiler_territorial_original`, páginas HTML y GTFS
   descargados manualmente). Cada uno con: fuente, fecha, SHA y ubicación del respaldo.
9. Gate de integridad que compare `data/raw` contra `docs/raw_manifest_sha256.txt` y falle
   con el **listado de ficheros perdidos**, no solo con un booleano.
10. Reintegrar `scripts/verificar_gobernanza.py` y actualizar sus asserts (nº de scripts,
    nodos del DAG, cabeceras). Si se decide bajar de 34 a 32 nodos, que sea una decisión
    documentada, no un efecto colateral.

---

## 6. Qué adoptar, qué adaptar y qué descartar

| Cambio de Alex | Decisión |
|---|---|
| `f4_pisos_dirigido` en `extract/` | **Adoptar** |
| `quality/` fuera de `extract/` | **Adoptar** la ubicación; **completar** la orquestación |
| `_common` sin `mkdir` al importar | **Adoptar** |
| `BASES` sin `res` + `ValueError` | **Adoptar** (y mantener el test) |
| `test_no_transform_writes_resultados` | **Adoptar** |
| `deduplicar_alquiler_enriquecido` con productor real | **Adoptar** (mejor que el `SKIP`) |
| README "raw no es regenerable" | **Adoptar** y ampliar con la lista P2 |
| `_estado` sin comprobar `exists()` | **Rechazar** (regresión R1) |
| `26_vpo` sobrescribiendo raw | **Rechazar** (regresión R2) |
| Merge/informe F4 en `raw` | **Rechazar** (regresión R3) |
| `09` leyendo objetivos de `raw` | **Rechazar** salvo que el productor también se mueva (R4) |
| Manifiesto canónico en `data/raw/` | **Rechazar** (regresión R5) |
| `in: []` en certificados energéticos | **Rechazar** (R7, es el F-03 ya corregido) |
| `raw:udalmap_empleo_corregido.csv` como entrada | **Rechazar** (el script lee `proc`) |
| Eliminar `verificar_gobernanza.py` | **Rechazar** |

---

## 7. Conclusión en una frase

El refactor de Alex acierta en **dónde debe vivir cada script** y se equivoca en **qué
garantías debe mantener cada capa**: al mover `f4` a `extract` relajó la inmutabilidad de
`raw`, al mover `quality` a `transform` lo dejó sin orquestador, y al tocar el DAG revirtió
la detección de raw incompleto, que es precisamente el síntoma que estabais sufriendo.
La base es aprovechable; hay que integrarla **con los guardarraíles de tu versión**, no en
sustitución de ellos.
