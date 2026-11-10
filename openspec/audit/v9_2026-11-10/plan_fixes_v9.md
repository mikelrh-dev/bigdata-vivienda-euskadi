# Plan de arreglos v9 — cómo se harían y si compensan para la defensa

**Fecha:** 2026-11-10 · **Naturaleza:** solo lectura · **Autor:** subagente v9 (planificación)
**Entrada:** `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `AGENT.md`, `incidente_p0_mongo.md`, `rubrica_reextraida.md`, `mapa_requisitos.md`, `desviaciones_rubrica_contrato.md`, `informe_extract.md`, `informe_transform.md`, `informe_storage_analysis_scripts.md`, `mapa_tests.md`, `informe_mongo_v9.md`, `informe_datos_v9.md`, `doc_sweep_1.md`, `doc_sweep_2.md`, `verificacion_dinamica.md`.
**Guardrails respetados:** no se modificó código, datos, Mongo, HDFS ni Kafka; no se ejecutó ningún test, pipeline, gate vivo ni generador; no se instalaron dependencias; no hubo commit/push. **Única escritura en el repo: este plan.** Las sondas son read-only (`pymongo` de lectura, `grep`, `read_file`, `sha256sum`).
**P0/P1:** ninguno nuevo sin reportar. El P0-1 de `verificacion_dinamica.md` sigue abierto y se recoge aquí como prioridad 0.

---

## 0. Estado vivo verificado en esta sesión (read-only)

Sondas `pymongo` de solo lectura sobre `localhost:27017` / `vivienda_euskadi` (MongoDB 9.0.2):

| Elemento | Estado ahora | Evidencia |
|---|---|---|
| `anuncios` | 594 docs, **solo `_id_`** | `list_indexes()` → `['_id_']` |
| `etxbide_promociones` | **406 docs, con `idx_promo_ine_estado_tipo`** | `estimated_document_count` + `list_indexes` |
| `anuncios__backup` | 594 docs, solo `_id_` | idem |
| Colecciones | 30 = 16 vivas + 14 `__backup` | `list_collection_names` |
| `anuncios.fecha_carga` | 2026-11-10 07:59:48 | `find_one({}, {'fecha_carga':1})` |
| HDFS 50070 / Kafka 9092 | no alcanzables | baseline v9 §7 |

**Dos correcciones a los informes de la carpeta** (cambian el plan de arreglos):

1. **`incidente_p0_mongo.md:9-13` atribuye la pérdida de índices a `tests/test_load_mongo.py`. Es incorrecto.** Ese fichero usa `mongomock` vía el fixture `mongo_tmp` (`tests/test_load_mongo.py:37-43`), que parchea `storage.mongo.get_db`; `replace_collection` resuelve `get_db` en `storage/mongo.py:155` en tiempo de llamada, así que nunca toca prod. **El mutador real es `tests/test_mongo_geo.py:13`** (`n = load_anuncios()` sin mongomock, sin `skipif`) y los tests de `explain` (H-T2). El incidente debe corregirse antes de que el plan se ejecute.
2. **`verificacion_dinamica.md:154` (P1-1) sobre `test_load_all_no_silencia_indices` es exagerado.** `tests/test_mongo_consistencia.py:131-144` parchea los 14 loaders a `lambda: 1`, así que `load_all()` **no** llama a `replace_collection`; `ensure_indexes` también va parcheado (`:137,:144`). Lo que sí hace es leer conteos de prod en solo lectura. El riesgo real de P1-1 son `test_mongo_geo.py` y los tests de `explain`.

**Estado transitorio:** entre dos sondas separadas ~1 min, `etxbide_promociones` pasó de ausente a presente (406 docs + índice). Hay **otro agente mutando Mongo en paralelo**. Cualquier restauración de índices debe coordinarse o verificarse después.

---

## 1. Agrupación por tipo de arreglo

### (a) Deriva documental — H-02…H-07, H-14, H-15, DS1-\*, DS2-\*

**Cómo se arregla.** Un barrido sustituyendo las cifras canónicas del baseline v9 (`00_baseline_v9.md:151`) en los ficheros citados, con `grep -n` previo para no deixar ninguna:

| Cifra | Valor vigente | Ficheros a corregir (fichero:línea) |
|---|---|---|
| 759 → **594** | anuncios | `docs/modelo_mongodb.md:11,40,129,140,162,164,170,172,176`; `docs/informe_capacidad_mongo.md:8,48,66`; `openspec/project.md:68`; `storage/clean_mongo.py:386` (H-12); `mongodb-y-analisis/spec.md:255,394,407` (H-M2) |
| 424/759 → **424/594**, nulos 335 → **170** | geo | `docs/modelo_mongodb.md:40,164` |
| 14+13 → **16 vivas + 14 `__backup`** | colecciones | `docs/modelo_mongodb.md:111,160`; `docs/informe_capacidad_mongo.md:3,8`; `docs/informe_final.md:26,144`; `docs/preguntas_analisis_profesional.md:99,120`; `docs/guion_defensa_12min.md:143,222` |
| 10 → **11** pipelines | pipelines | `docs/modelo_mongodb.md:111,180`; `docs/matriz_indicadores.md:19`; `docs/informe_final.md:26,145`; `docs/preguntas_analisis_profesional.md:99,120`; `docs/guion_defensa_12min.md:35,143,171`; `analysis/run_analisis_mongo.py:1151` (H-11 argparse) |
| 5/6 CSV → **8** CSV | CSV | `docs/modelo_mongodb.md:180-188`; `docs/informe_final.md:27`; `docs/README.md:34` (H-06); `docs/guion_defensa_12min.md:143,171,249` |
| 173/113/40 → **204/126/50/39** | comparativa | `docs/modelo_mongodb.md:115`; `docs/matriz_indicadores.md:32`; `docs/informe_capacidad_mongo.md:14,87-89,93-95,99`; `docs/preguntas_analisis_profesional.md:84,91,120`; `docs/analisis_vault_vs_rubrica.md:35` (H-15) |
| 177 tests → **237 (235 passed, 2 skipped)** | tests | `docs/informe_final.md:142`; `docs/guion_defensa_12min.md:36,170` |
| IXSCAN 1 → **IXSCAN con filtro `20069` (1 doc) o `48020` (8)** | explain | `README.md:287`; `AGENT.md:4`; `docs/arquitectura_datos.md:69`; `docs/guion_defensa.md:10,33,51`; `docs/guion_defensa_12min.md:36,175`; `docs/modelo_mongodb.md:129-134` |
| 12 PNG → **28+8 PNG** | artefactos | `docs/guion_defensa_12min.md:143,171,249` |
| `HTMLEOF` literal | borrar | `docs/README.md:36` (H-14) |
| 136 tests / 185 silver / 9 pipelines / 759 / VM pendiente | `openspec/project.md:6,68,75,80` | H-07 |

Pasos concretos:
1. Restaurar los índices primero (prioridad 0), porque el número de `explain` depende de ellos.
2. Ejecutar `grep -rn` de cada cifra vieja sobre `docs/`, `README.md`, `AGENT.md`, `openspec/project.md`, `analysis/run_analisis_mongo.py`, `storage/clean_mongo.py`.
3. Sustituir por el valor vigente y, en `explain`, **nombrar el filtro** («filtro `20069`, 1 doc» o «filtro `48020`, 8 docs») para que sea reproducible (HM-08).
4. Corregir `docs/README.md:36` (borrar `HTMLEOF`) y `docs/README.md:34` (4 CSV → 8).
5. Re-ejecutar `scripts/verificar_gobernanza.py` y el gate offline para confirmar que nada se rompió.
6. Opcional pero recomendable: añadir al barrido una comprobación de que el guion no contradice el modelo (DS2-23: «embedding» → en realidad es **referencing por `codigo_ine`**; `anuncios` es colección separada).

**Esfuerzo:** S por fichero, **M en total** (~60-90 min si se hace en lote con un script de sustitución y revisión manual).
**Riesgo:** **1/10** — solo documentación; el único riesgo es dejar una cifra a medias o citar un `explain` cuyo filtro no sea el que se ejecutó.
**Compensa para la defensa:** **SÍ, y es el grupo con mejor ratio coste/beneficio.** El tribunal contrasta cifras con el PDF y con el sistema vivo; el guion (`docs/guion_defensa.md`, `docs/guion_defensa_12min.md`) es el documento que se lee en voz alta. DS2-01 (P1) y DS2-23 (embeddings) son las dos contradicciones más probables de ser leídas.

### (b) Tests que mutan producción — H-T2, P1-1, F-01

**H-T2 / HM-01 — los tests y el "análisis" dropean y recrean índices de prod.**
Cómo se arregla:
1. `analysis/mongo_indexes.py:107-132` (`explain_before_after`): sustituir el `drop_demo_index()` + `create_index` del "antes" por un `explain` con `hint: {"$natural": 1}` (fuerza COLLSCAN sin dropear), como ya hizo `informe_mongo_v9.md:92` en su sonda read-only. El "después" se obtiene con el índice presente (asegurar `ensure_indexes()` antes, fuera del `explain`).
2. `analysis/mongo_indexes.py:135-149` (`explain_promo_before_after`): idem.
3. `analysis/mongo_indexes.py:152-158` (`index_report`): ya no muta.
4. `tests/test_mongo.py:290,296-298` y `:333`; `tests/test_mongo_indices.py:17,33,49`: llamar a la versión read-only y **eliminar** `mi.ensure_indexes()` del cuerpo del test (o dejarlo como garantía final, pero nunca como parte del "before").
5. `tests/test_mongo_geo.py:13`: envolver `load_anuncios()` con el fixture `mongo_tmp` de `tests/test_load_mongo.py:37-43` (mongomock) o añadir `pytest.importorskip`/`skipif(not ping())` y usar `get_test_db()`. **Este es el test que realmente dejó `anuncios` sin índices.**
6. `analysis/run_analisis_mongo.py:1164-1173`: no ejecutar `explain_before_after` en `main()` (o ejecutar la versión read-only).
7. Corregir `incidente_p0_mongo.md:9-13` (atribución) y `verificacion_dinamica.md:154` (P1-1).

**Esfuerzo:** **M** (~45-60 min + verificación con `pytest tests/test_mongo_indices.py` y `tests/test_mongo_geo.py`).
**Riesgo:** **2/10** — el cambio es local; el riesgo es que el "before" con `hint` no reporte `COLLSCAN` en algún planificador y el test falle. Mitiga: asertionar `stage == "COLLSCAN"` solo si el hint se aplica, o usar `explain(..., hint={"$natural":1})` y registrar el stage real.
**Compensa para la defensa:** **SÍ, imprescindible.** La demo ejecuta `pytest`; si la suite vuelve a dropear los índices, el `explain` del criterio C13 se cae **en directo**. Es el arreglo que protege al arreglo de la prioridad 0.

**F-01 — 20/41 `guardar_json` lanzarían `ValueError` al re-ejecutar extract.**
Cómo se arregla (opciones de `informe_extract.md:247-250`):
1. Alinear la validación con la realidad: que `extract/_common.py:199-205` **avise** en raw (como ya hace fuera de raw, `:206-209`) o que los 20 llamadores pasen `url`. Son 20 llamadas con el mismo `metadata={...}`; se pueden corregir en lote.
2. Declarar el modo congelado: bandera `RAW_FROZEN` en `_common` que haga `guardar_json` saltar (no escribir) cuando el destino exista y el SHA coincida, como `extract/26_vpo_terminadas.py:114-122`.
3. Mover `ingestion_manifest.json` fuera de raw (F-04): escribirlo en `data/procesado/_meta/` y retirarlo de `RAW_DIR` (`extract/main_ingest.py:217-222,284-289`).
Pasos: editar `extract/_common.py`, los 16+4 llamadores listados en `informe_extract.md:37-52`, y `extract/main_ingest.py`; verificar con `python -c "import ast; ast.parse(...)"` sobre los 41 ficheros y con un `main_ingest --mode replay-raw` (no live).
**Esfuerzo:** **M/L** (~90 min si se hace el lote de 20 llamadores; S si se elige la opción 2).
**Riesgo:** **4/10** — tocar 20 puntos de escritura de extracción; si se rompe uno, la re-ejecutabilidad mejora pero el raw congelado no se ve afectado (read-only).
**Compensa para la defensa:** **NO directamente.** El raw está congelado y la defensa no re-ejecuta extract; el C1 se acredita con el código y con el raw ya producido. **Recomendable** para la reproducibilidad (H18 del plan), pero **puede esperar** hasta después de la defensa.

### (c) Código / arquitectura — T-01, T-04, T-05, H-SA-02, HM-01

**T-01 — rutas `data/` relativas al cwd + `_common.py` crea el árbol al importar.**
Cómo: `extract/_common.py:38-44` → derivar `DATA_DIR` de `Path(__file__).resolve().parents[1]` en lugar de `os.getenv("DATA_DIR", "data")`, o mover el `mkdir` a un `main()`; los 10 scripts que usan `os.path.join("data", …)` listados en `informe_transform.md:43` heredan el efecto. Mitigación ya existente: `transform/run_all.py:40` hace `os.chdir(PROJECT_ROOT)`.
**Esfuerzo M · Riesgo 4/10 · Compensa NO para la defensa** (la demo corre desde la raíz; el orquestador ya hace `chdir`). Recomendable.

**T-04 — ninguna escritura atómica en `transform/` (49 llamadas, 0 primitivas).**
Cómo: envolver las escrituras de los hubs (`dim_municipios.csv`, `anuncios_unificados.*`, `run_manifest.json`) con `NamedTemporaryFile`/`os.replace` (plantilla ya ausente en todo `transform/`; verificado: `grep -rn "os.replace\|NamedTemporaryFile\|mkstemp\|fsync" transform/` → 0). Sitios en `informe_transform.md:97-105`.
**Esfuerzo M · Riesgo 5/10 · Compensa NO** (el silver ya está generado y la defensa no ejecuta transforms). Puede esperar.

**T-05 — 7 scripts ejecutan su pipeline al importar.**
Cómo: añadir `if __name__ == "__main__":` y mover el código de módulo a `main()` en `transform/asignar_area_funcional_ecvi.py`, `enriquecer_equipamiento_realtyapi.py`, `generar_analisis_variables_base.py`, `generar_emancipacion_tier3_93.py`, `generar_fingerprint.py`, `generar_municipios_faltantes_93.py`, `generar_poblacion_joven_municipal.py` (verificado: 0 ocurrencias de `__main__` en los 7). También `transform/muni_resolve.py:53` (`_load_dim()` en importación), que es la causa ejecutada de H-T3.
**Esfuerzo M · Riesgo 4/10 · Compensa NO directamente**, pero **recomendable** porque importar `muni_resolve` en un test o script muta silver; es la misma familia que H-T3 (la suite no se colecciona desde fuera de la raíz).

**H-SA-02 — `replace_collection` no es atómico en su conjunto.**
Cómo: `storage/mongo.py:152-164` → crear los índices en `staging` antes del `rename`, o recrearlos tras el swap dentro del mismo `load_all`; y `scripts/run_mongo_pipeline.py:70-73` → mover `ensure_indexes()` **después** de `clean_all()` (hoy está dentro de `load_all`, antes del dedup). También `storage/load_mongo.py:607-615`.
**Esfuerzo M · Riesgo 6/10 · Compensa NO para la defensa** (no hay recarga durante la demo; hoy 0 duplicados). Puede esperar; es el arreglo con más riesgo de todos porque toca el swap de colecciones.

**HM-01 — el entrypoint de análisis no es read-only.** Arriba, en (b): es el mismo arreglo que H-T2.

### (d) Datos / manifiestos — D-01, D-02, D-03, D-11

**D-01 — dos manifiestos raw discrepando en 2 ficheros.**
Evidencia ejecutada: `docs/raw_manifest_sha256.txt` (`fa363e45…`, `c8eef595…`) vs `data/procesado/_meta/ingestion_manifest.json` (`76e20ea9…`, `ccd22d03…`) para `lanbide_paro_historico_joven.json` y `lanbide_paro_juvenil.json`; el disco coincide con el manifiesto de `docs/`.
Cómo: regenerar el acta con `python extract/generar_ingestion_manifest.py` (lee raw + sidecars y reescribe `_meta/ingestion_manifest.json`; verificado que existe y que excluye `.FROZEN`/`.gitkeep`/manifest). No toca raw.
**Esfuerzo S · Riesgo 1/10 · Compensa SÍ** (procedencia; barato y cierra una contradicción audible).

**D-02 — `_meta/index.json` no hashea el raw vigente (0/61).**
Cómo: documentar en el propio `_meta/index.json` o en `docs/` que su `hash_sha256` es el del **payload fuente**, no del wrapper raw; o regenerarlo con el SHA del wrapper. No hay generador propio (es registro de extracción 2026-10-23…11-03).
**Esfuerzo S · Riesgo 2/10 · Compensa NO directamente.** Recomendable (una línea de documentación).

**D-03 — `dim_municipios` duplicado raw vs procesado con esquemas distintos.**
Evidencia ejecutada: raw 252×9 sha `77d0feb6…`; procesado 252×12 sha `261ad2c7…`; 9 scripts leen la copia de raw (`informe_transform.md:55-68`).
Cómo: unificar en `data/procesado/dim_municipios.csv` con fallback a raw (patrón ya mayoritario) y retirar `dim_municipios.*` del manifiesto raw canónico, o declarar raw como histórico.
**Esfuerzo M · Riesgo 4/10 · Compensa NO para la defensa.** Puede esperar; hoy los 252 códigos coinciden.

**D-11 — `_meta/ingestion_manifest.json` no está en el manifiesto silver.**
Evidencia ejecutada: `grep -c "ingestion_manifest" data/procesado/manifest_sha256.txt` → 0; 188 entradas vs 189 ficheros en disco.
Cómo: incluirlo en el manifiesto silver o declararlo como fichero de control excluido (convención). Coherente con D-01.
**Esfuerzo XS · Riesgo 1/10 · Compensa SÍ** (cierra el 189 vs 188 con una decisión explícita).

### (e) Config / CI / gobernanza — H-SA-01, H-T1, H-SA-11

**H-SA-01 — el gate no captura `os.environ.get(...)` y declara «0 env sin declarar» cuando hay 2 sin declarar.**
Evidencia: `scripts/verificar_gobernanza.py:64-65` (solo `getenv`/`environ[...]`); `scripts/gate_extremo_a_extremo.py:195` usa `os.environ.get("GATE_LIVE")`; `transform/_raw_guard.py:68` usa `os.environ.get("RAW_GUARD_AUDIT_LOG")`; `grep -nE 'GATE_LIVE|RAW_GUARD' .env.example` → **no declaradas**.
Cómo: añadir `re.findall(r"os\.environ\.get\(\s*['\"]([A-Z0-9_]+)['\"]", texto)` al escáner de `verificar_gobernanza.py`, y declarar las dos variables en `.env.example`.
**Esfuerzo XS · Riesgo 1/10 · Compensa SÍ** (el gate es evidencia de gobernanza; hoy imprime una cabecera falsa).

**H-T1 — la suite no es hermética: 40 tests exigen Mongo local y CI no lo provee.**
Cómo: (a) añadir `services:` con un contenedor Mongo al `.github/workflows/quality-gate.yml:18-30`; o (b) añadir `skipif(not ping())` a los 9 ficheros que necesitan Mongo sin guard (`mapa_tests.md:213`); o (c) deseleccionar los tests de Mongo en CI con `-m "not mongo_live"`. Opción (b) es la que menos toca el workflow.
**Esfuerzo M · Riesgo 2/10 · Compensa NO para la defensa** (CI no se muestra en la demo), pero **recomendable** porque hoy el job `pytest_offline` no puede pasar en GitHub.

**H-SA-11 — CI solo ejecuta `pytest`; no corre gobernanza, `run_all --check` ni `run_mongo_pipeline --dry-run`; el job vivo sonda una IP privada desde runner público.**
Cómo: añadir tres pasos al workflow (`python scripts/verificar_gobernanza.py`, `python transform/run_all.py --check`, `python scripts/run_mongo_pipeline.py --dry-run`) y mover `gate_vivo_manual` a un runner self-hosted o documentar que es manual en local.
**Esfuerzo S · Riesgo 1/10 · Compensa NO.** Puede esperar; no es un defecto del proyecto (el gate vivo requiere red centro).

**H-M1 — 50 encabezados `### Requirement:` vs 46 IDs canónicos: 4 `chart_*` escapan al gate.**
Evidencia: `grep -cE '^### Requirement: ' openspec/specs/*/spec.md` → 50; el patrón de `verificar_gobernanza.py:36` exige mayúscula inicial y los 4 `chart_*` (`presentacion-de-resultados/spec.md:306,317,339,378`) no matchean.
Cómo: ampliar el regex a `([A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*-\d{2})` o declarar la convención `chart_*` como ID válido; actualizar el docstring `verificar_gobernanza.py:5` y el conteo esperado (46 → 50).
**Esfuerzo XS · Riesgo 1/10 · Compensa SÍ** (evita un subrecuento futuro; barato).

---

## 2. Tabla priorizada

| # | ID | Título | Cómo se arregla (fichero:sitio) | Esfuerzo | Riesgo | Compensa | Prioridad |
|---|---|---|---|---|---|---|---|
| 1 | **P0-1 / DS1-01 / DS2-01** | Los 4 índices de `anuncios` no existen; C13/T4 no son reproducibles | Ejecutar `ensure_indexes()` (`analysis/mongo_indexes.py:62-94`) **con autorización de escritura**; verificar `list_indexes()` → 4 índices | **S** | 1 | **SÍ — imprescindible** | **P0** |
| 2 | **H-T2 / HM-01 / P1-1** | Los tests y el "análisis" dropean/recrean índices de prod | `analysis/mongo_indexes.py:107-149` versión read-only con `hint:$natural`; `tests/test_mongo.py:290,296-298,333`, `tests/test_mongo_indices.py:17,33,49`; `tests/test_mongo_geo.py:13` con mongomock; `analysis/run_analisis_mongo.py:1164-1173` | **M** | 2 | **SÍ — imprescindible** | **P0** |
| 3 | **DS2-01 / H-03 / DS2-23 / DS2-24** | El guion de defensa afirma IXSCAN con índices ausentes, 24 índices, «embedding» incorrecto | Corregir `docs/guion_defensa.md:9,10,33,44,51` y `docs/guion_defensa_12min.md:36,143-146,175,222` con el filtro real y referencing | **S** | 1 | **SÍ — imprescindible** | **P0** |
| 4 | **incidente_p0_mongo.md / verificacion_dinamica.md** | Atribución errónea del incidente y P1-1 exagerado | Corregir `incidente_p0_mongo.md:9-13` (el mutador es `test_mongo_geo.py`) y `verificacion_dinamica.md:154` | **S** | 0 | **SÍ — imprescindible** | **P0** |
| 5 | **H-02…H-07, H-14, H-15, DS1-\*, DS2-\*** | Deriva documental en 12+ ficheros | Barrido con las cifras canónicas (tabla de la §1a) sobre `docs/`, `README.md`, `AGENT.md`, `openspec/project.md`, `analysis/run_analisis_mongo.py`, `storage/clean_mongo.py` | **M** | 1 | **SÍ** | **P1** |
| 6 | **D-01 / D-11** | Manifiestos discrepando / acta fuera del manifiesto silver | Regenerar `data/procesado/_meta/ingestion_manifest.json` con `extract/generar_ingestion_manifest.py`; decidir su exclusión en el manifest silver | **S** | 1 | **SÍ** | **P1** |
| 7 | **H-SA-01 / H-M1** | Gate con ciego `os.environ.get`; 4 requisitos `chart_*` fuera del conteo | `scripts/verificar_gobernanza.py:36,64-65` + `.env.example` (2 variables) | **XS** | 1 | **SÍ** | **P1** |
| 8 | **HM-03 / HM-06** | Flags de calidad ausentes en prod; `anuncios_habitaciones_*` duplicadas | Ejecutar `clean_all()` tras la carga (autorización); decidir cuál de las dos colecciones es canónica | **S** | 3 | Parcial | **P1** |
| 9 | **T-01 / T-05 / H-T3** | Rutas relativas al cwd; 7 scripts mutan silver al importar; suite no colecciona fuera de la raíz | `extract/_common.py:38-44`; 7 ficheros de `transform/` (ver §1c); `transform/muni_resolve.py:53` | **M** | 4 | No directly | **P2** |
| 10 | **F-01 / F-02 / F-04** | 20/41 `guardar_json` fallan al re-ejecutar; raw read-only; manifiesto en raw | `extract/_common.py:199-205` (aviso o `RAW_FROZEN`); 20 llamadores de `informe_extract.md:37-52`; mover `ingestion_manifest.json` | **M/L** | 4 | No | **P2** |
| 11 | **T-04 / H-SA-02** | Escrituras no atómicas en silver; swap de colección no atómico | `NamedTemporaryFile`+`os.replace` en hubs; mover `ensure_indexes` tras `clean_all` (`scripts/run_mongo_pipeline.py:70-73`) | **M** | 5-6 | No | **P2** |
| 12 | **D-02 / D-03** | `_meta/index.json` no hashea el raw; `dim_municipios` doble fuente | Documentar el alcance del hash; unificar la dim en procesado con fallback | **S/M** | 2-4 | No | **P2** |
| 13 | **H-T1 / H-SA-11** | CI sin Mongo; CI no corre gates; gate vivo con IP privada | `services:` Mongo o `skipif`; 3 pasos de gate en el workflow | **M** | 2 | No | **P2** |

---

## 3. Imprescindible vs opcional

### Imprescindible antes de la defensa (P0)

1. **Restaurar los 4 índices de `anuncios`** (prioridad 1). Sin ellos, C13 (10 puntos RA3, 13,3 %) y T4 (15 % Tema 8) no tienen evidencia reproducible y el `explain` del guion es COLLSCAN 594. Es un `ensure_indexes()` idempotente; no toca datos.
2. **Blindar los tests que mutan producción** (prioridad 2). La demo ejecuta `pytest`; si vuelve a correr `test_mongo_geo.py` o los tests de `explain`, los índices caen delante del tribunal. Incluye corregir la atribución del incidente.
3. **Corregir el guion de defensa** (prioridad 3): IXSCAN con el filtro real, 24 índices después de restaurar, referencing (no embedding).
4. **Corregir el incidente y el P1-1** (prioridad 4): que el siguiente agente no persiga un test equivocado.

### Recomendable (P1)

- Barrido documental completo (H-02…H-07, H-14, H-15, DS1-\*, DS2-\*): es lo que el tribunal puede contrastar.
- D-01 + D-11: procedencia y manifiestos, coste bajo.
- H-SA-01 + H-M1: gobernanza, coste muy bajo.
- HM-03: flags de calidad (si hay tiempo y autorización).

### Puede esperar (P2)

- T-01, T-04, T-05, H-SA-02, F-01, D-02, D-03, H-T1, H-SA-11. Son deuda real, pero ninguna afecta a la demo: el raw está congelado, el silver está generado y CI no se muestra.

### No compensa / es ruido

- **H-R4, H-R5** (etiquetas v8 paráfrasis; referencias de línea dependientes del instrumento): no cambian cobertura ni nota.
- **H-W1.3-3** (7 puntos finales suprimidos en docx §16): ruido tipográfico; la nota «Sin diferencias literales» es falsa en lo formal, pero nadie lo leerá en voz alta.
- **H-W1.3-5 / H-W1.3-6** (solapamiento PDF↔docx; mapeo partido): es diseño declarado, no un defecto.
- **H-M2 / H-M4**: subsumidos por H-M1.
- **DS1-14 / DS1-15 / DS2-25 / DS2-26**: huellas históricas y `git status` del momento; se resuelven etiquetándolos como históricos, no reescribiéndolos.
- **O-1** (baseline con un 253 donde corresponde un 10): error interno del baseline; se corrige si se toca, no es un arreglo del proyecto.

---

## 4. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `pymongo` de solo lectura: `list_collection_names`, `estimated_document_count`, `list_indexes`, `find_one` sobre `anuncios`.
- `grep`/`sed` de las cifras en `docs/`, `README.md`, `AGENT.md`, `openspec/project.md`, `analysis/run_analisis_mongo.py`, `storage/clean_mongo.py`, `tests/`, `openspec/specs/presentacion-de-resultados/spec.md`.
- `read_file` de `extract/_common.py`, `transform/muni_resolve.py`, `storage/mongo.py`, `analysis/mongo_indexes.py`, `scripts/verificar_gobernanza.py`, `.github/workflows/quality-gate.yml`, `tests/test_load_mongo.py`, `tests/test_mongo_geo.py`, `tests/test_mongo_consistencia.py`, `tests/test_mongo.py`, `tests/test_mongo_indices.py`, `transform/run_all.py`, `storage/load_mongo.py`.
- `json.load` + comparación de `docs/raw_manifest_sha256.txt` vs `_meta/ingestion_manifest.json` (D-01) y de `_meta/index.json` (D-02).
- `git status --porcelain`, `git log --oneline -8`.

**Solo leído (sin ejecutar):** los 10 informes de `openspec/audit/v9_2026-11-10/`; `00_baseline_v9.md`; `AGENT.md`; `plan_ejecucion_v9_rondas_2026-11-10.md`; `rubrica_reextraida.md`; `desviaciones_rubrica_contrato.md`.

**No ejecutado (guardrails):** `ensure_indexes()`, cualquier test, `load_all`/`clean_all`, `run_analisis_mongo`, generadores de manifiesto, productor Kafka, gate vivo, instalación, commit/push. Ninguna escritura fuera de este plan.

---

## 5. Límites del plan

- Las prioridades 0 requieren **autorización de escritura en Mongo** (hoy prohibida por la auditoría) y **coordinación con el agente paralelo** que está recargando colecciones.
- El número de `explain` (IXSCAN 1 vs IXSCAN 8) depende del filtro elegido; el plan debe fijar uno y documentarlo (HM-08).
- No se ha verificado el estado de HDFS/Kafka (red caída): C2/C3 no entran en este plan.
- El barrido documental debe hacerse **después** de restaurar los índices, para no escribir un número y tener que reescribirlo.
