# Verificación de arreglos v9 contra rúbrica, contrato y restricciones de infraestructura

**Fecha:** 2026-11-10 · **Naturaleza:** solo lectura · **Autor:** subagente v9 (verificación)
**Entrada:** `plan_fixes_v9.md`, `incidente_p0_mongo.md`, `rubrica_reextraida.md`, `desviaciones_rubrica_contrato.md`, `matriz_rubrica_v8.md`, `openspec/specs/contrato-reto/spec.md` + las 5 specs de dominio, `AGENT.md`, `openspec/config.yaml`, `00_baseline_v9.md`, `informe_mongo_v9.md`, `verificacion_dinamica.md`.
**Guardrails respetados:** no se modificó código, datos, Mongo, HDFS ni Kafka; no se ejecutó ningún test, pipeline, gate vivo ni generador; no se instalaron dependencias; no hubo commit/push. **Única escritura en el repo: este informe.** Las sondas son read-only (`pymongo` de lectura, `grep`, `read_file`).

---

## 1. Veredicto

**Ningún arreglo de `plan_fixes_v9.md` contradice directamente la rúbrica del reto ni las restricciones de infraestructura del usuario.** Ninguno asume HDFS o Kafka vivos, ni introduce un flujo Kafka→Mongo. El plan excluye explícitamente C2/C3 (`plan_fixes_v9.md:223`) y la cadena real verificada por código es Windows>Kafka>HDFS (`storage/kafka_raw_producer.py:49-79` → `storage/kafka_hdfs_uploader.py:92-186`), sin Mongo.

**Hay dos contradicciones de segundo orden** (el arreglo read-only deja obsoleto un escenario del spec; el barrido documental no cubre una línea Kafka→Mongo pre-existente) y **seis riesgos de cobertura** que no son bloqueantes pero que el plan no cierra. Detalle en §5 y §6.

---

## 2. Método y evidencia ejecutada

**Ejecutado (herramienta real, read-only):**

- `pymongo` de solo lectura sobre `localhost:27017` / `vivienda_euskadi`: `anuncios` 594 docs con `list_indexes()` → `['_id_']`; `etxebide_promociones` con `idx_promo_ine_estado_tipo`; `municipios` con `idx_municipios_territorio_nombre`; 30 colecciones; 424 docs con `ubicacion.coordenadas` y 170 con `null`.
- `explain("executionStats")` read-only con y sin `hint: {"$natural": 1}` para los filtros `48001`, `20069`, `48020` + `modalidad=larga_estancia` + `precio_eur≤1000`: **todos dan COLLSCAN 594** porque el índice ESR está ausente. Confirma que el "after" IXSCAN solo es demodable tras restaurar los índices (P0-1) y que el filtro por defecto `48001` devolvería 0 docs.
- `grep -rn "os.replace|NamedTemporaryFile|mkstemp|fsync" transform/` → **0** (confirma T-04).
- `grep -c "__main__"` sobre los 7 scripts de T-05 → **0** en los 7 (confirma T-05).
- `grep -n "_load_dim()" transform/muni_resolve.py` → `_load_dim()` en `:23` y llamada en `:53` a nivel de módulo (confirma H-T3).
- `read_file` de todos los ficheros citados en §3 y §4.

**Solo leído (sin ejecutar):** los documentos de auditoría v8/v9, el PDF/docx vía informes, `AGENT.md`, `openspec/config.yaml`, los 5 specs, `docs/modelo_mongodb.md`, `docs/guion_defensa.md`, `docs/guion_defensa_12min.md`, `docs/README.md`, `openspec/project.md`, `analysis/mongo_indexes.py`, `storage/mongo.py`, `storage/load_mongo.py`, `analysis/run_analisis_mongo.py`, `tests/*`, `extract/_common.py`, `transform/muni_resolve.py`, `scripts/*`, `.github/workflows/quality-gate.yml`.

**No ejecutado (guardrails):** `ensure_indexes()`, cualquier test, `load_all`/`clean_all`, `run_analisis_mongo`, generadores de manifiesto, productor Kafka, gate vivo, instalación, commit/push. Ninguna escritura fuera de este informe.

---

## 3. Verificación por arreglo

### 3.1 P0

| # | Arreglo | ¿Contradice rúbrica/contrato? | Evidencia |
|---|---|---|---|
| P0-1 | Restaurar los 4 índices de `anuncios` con `ensure_indexes()` | **No.** Es el prerequisito para C13/T4. Idempotente; no toca datos. Requiere autorización de escritura (hoy prohibida). | `plan_fixes_v9.md:157,177`; `analysis/mongo_indexes.py:62-94`; `incidente_p0_mongo.md:15-17,43-45`; spec `mongodb-y-analisis/spec.md:298-321`; rúbrica C13 en `rubrica_reextraida.md:58` y `contrato-reto/spec.md:65`. Sonda ejecutada: `anuncios` solo `_id_`. |
| P0-2 | `explain_before_after` read-only con `hint:{"$natural":1}`; blindar tests | **Contradice el escenario del spec INDICES-01** (véase C-1). No contradice la rúbrica: el nivel 10 permite «antes/después **o con/sin índice**». | `plan_fixes_v9.md:66-78,158`; `analysis/mongo_indexes.py:107-149`; `tests/test_mongo_indices.py:14-49`; `tests/test_mongo.py:289-298,332-335`; spec `mongodb-y-analisis/spec.md:300-314`; `informe_mongo_v9.md:92-105,184` (HM-08). |
| P0-2b | `tests/test_mongo_geo.py:13` con mongomock o `get_test_db()` | **No.** Evita la mutación real. Riesgo menor de cobertura (véase R-4). | `plan_fixes_v9.md:72`; `tests/test_mongo_geo.py:11-45`; `tests/test_load_mongo.py:37-43`. |
| P0-3 | Corregir guion: IXSCAN con filtro real, referencing | **No.** Corrige una afirmación falsa (C9). Riesgo de sobrecorrección en `guion_defensa_12min.md:144` (véase R-3). | `plan_fixes_v9.md:159,179`; `docs/guion_defensa.md:9-10,33,44,51`; `docs/guion_defensa_12min.md:36,143-146,175,222`. |
| P0-4 | Corregir atribución del incidente y P1-1 | **No.** La corrección es exacta. | `plan_fixes_v9.md:23-26,160,180`; `incidente_p0_mongo.md:9-13`; `verificacion_dinamica.md:154`; `tests/test_load_mongo.py:37-43` (mongomock); `tests/test_mongo_geo.py:13` (mutador real); `tests/test_mongo_consistencia.py:129-144` (14 loaders parcheados + `ensure_indexes` parcheado). |

### 3.2 P1

| # | Arreglo | ¿Contradice? | Evidencia |
|---|---|---|---|
| P1-5 | Barrido documental H-02…H-07, H-14, H-15, DS1-*, DS2-* | **No introduce contradicciones**, pero deja líneasKafka→Mongo y Docker sin cubrir (véase C-2). | `plan_fixes_v9.md:34-62,161,184`; `docs/modelo_mongodb.md:11,40,111,115,129-134,144-152,160-180`; `docs/README.md:34,36`; `openspec/project.md:6,30,38,68,75,80`; `AGENT.md:4`. |
| P1-6 | D-01/D-11 manifiestos | **No.** Regenerar el acta no toca raw. | `plan_fixes_v9.md:112-129,162,185`. |
| P1-7 | H-SA-01/H-M1 gobernanza | **No.** Corrige un ciego del gate y el conteo `chart_*`. | `plan_fixes_v9.md:133-149,163,186`; `scripts/verificar_gobernanza.py:36,64-65`. |
| P1-8 | HM-03/HM-06 flags de calidad y colecciones duplicadas | **No.** Requiere escritura (`clean_all()`); la duplicación queda como decisión abierta. | `plan_fixes_v9.md:164,187`. |

### 3.3 P2 diferidos

| # | Arreglo | ¿Contradice? | Evidencia |
|---|---|---|---|
| P2-9 | T-01/T-05/H-T3 rutas cwd y efectos al importar | **No.** Verificado por `grep`. | `plan_fixes_v9.md:92-102,165,191`; `extract/_common.py:38-44`; `transform/muni_resolve.py:53`. |
| P2-10 | F-01/F-02/F-04 `guardar_json` | **No directamente**, pero la opción 1a debilita FORMATO-01 (véase R-5). | `plan_fixes_v9.md:80-88,166,191`; `extract/_common.py:199-209`. |
| P2-11 | T-04/H-SA-02 escrituras atómicas y swap | **No.** Alinea con CARGA-SEGURA-01. | `plan_fixes_v9.md:96-106,167,191`; `storage/mongo.py:152-164`; `scripts/run_mongo_pipeline.py:70-73`; `storage/load_mongo.py:607-615`. |
| P2-12 | D-02/D-03 hash y dim duplicada | **No.** | `plan_fixes_v9.md:117-124,168,191`. |
| P2-13 | H-T1/H-SA-11 CI | **No.** El workflow no toca HDFS/Kafka. | `plan_fixes_v9.md:138-144,169,191`; `.github/workflows/quality-gate.yml:18-30`. |

---

## 4. Casos críticos

### 4.1 Restaurar los 4 índices de `anuncios` — ¿contradice algo? ¿Sigue cumpliendo C13?

**No contradice.** Es el único camino para que C13/T4 vuelva a ser reproducible: sin el índice ESR, todo `explain` da COLLSCAN 594 (sonda ejecutada). `ensure_indexes()` es idempotente y no toca documentos (`analysis/mongo_indexes.py:62-94`). El incidente atribuye la pérdida a `replace_collection` (`storage/mongo.py:152-164`), que no recrea índices; `load_all` sí los recrea (`storage/load_mongo.py:607-615`). Restaurar no altera ninguna cifra de la rúbrica y devuelve el estado al baseline. **Requiere autorización de escritura** (`plan_fixes_v9.md:221`), hoy prohibida por la misión.

### 4.2 `explain_before_after` read-only con `hint:$natural` — ¿sigue demostrando COLLSCAN/IXSCAN y totalDocsExamined?

**Sí para la rúbrica, no para el escenario literal del spec.** El nivel 10 de C13 dice «Compara mediante explain() la consulta antes/después **o con/sin índice** e identifica COLLSCAN/IXSCAN y totalDocsExamined» (`rubrica_reextraida.md:58`; `contrato-reto/spec.md:65`). Forzar COLLSCAN con `hint:{"$natural":1}` y comparar con el índice presente es la variante «con/sin índice»: identifica ambos stages y ambos `totalDocsExamined`. El test `tests/test_mongo_indices.py:21-31` sigue pasando (594 > 0/1/8).

**Pero el spec INDICES-01 escenario dice «GIVEN el índice ESR eliminado … AND after.totalDocsExamined es 1»** (`mongodb-y-analisis/spec.md:309-314`). El arreglo **no elimina** el índice (usa hint) y el filtro por defecto `48001` devuelve **0 docs** (sonda ejecutada; `informe_mongo_v9.md:100-105`, HM-08). El plan aplaza la decisión del filtro (`plan_fixes_v9.md:222`) y el barrido documental **no toca el spec**. Resultado: el escenario del spec queda obsoleto y el demo con el filtro por defecto mostraría «IXSCAN 0», débil pero conforme a la rúbrica. **No es bloqueante para C13** (la rúbrica no exige un número concreto), pero sí es una contradicción fix-vs-spec que el plan no cierra.

### 4.3 Blindar tests (mongomock) — ¿rompe alguna cobertura de C13 u otra?

**No rompe C13.** Los tests de `explain` pasan a read-only y siguen asertando COLLSCAN/IXSCAN y `totalDocsExamined` (`tests/test_mongo_indices.py:21-47`). De hecho **fortalecen** C13: hoy la suite muta prod (H-T2) y la demo cae si se ejecuta `pytest` (`plan_fixes_v9.md:78`). El arreglo corrige la causa real del incidente (`tests/test_mongo_geo.py:13`), no el chivo expiatorio (`tests/test_load_mongo.py`, que sí usa mongomock en `tests/test_load_mongo.py:37-43`).

**Riesgo menor:** `test_mongo_geo.py` es el único test que verifica el geo real de prod (424/594). Envolverlo con mongomock o `get_test_db()` pierde esa aserción sobre prod (la carga se prueba con datos sintéticos o en BD de test). No degrada un criterio de rúbrica (C6/C15 no exigen un test geo), pero conviene preservar una lectura read-only de prod en otro test o en el gate.

### 4.4 Barrido documental — ¿puede introducir alguna contradicción?

**No introduce cifras incorrectas** (las reemplazos son los canónicos de `00_baseline_v9.md:151`: 594, 424/594, 16+14, 11, 8, 204/126/50/39, 237, IXSCAN con filtro, 28+8 PNG). Pero **dos imprecisiones**:
- La columna «valor viejo» no coincide con el texto real en dos sitios: `analysis/run_analisis_mongo.py:1151` dice «9 pipelines + 5 CSV» (el plan dice 10) y `docs/README.md:34` dice «4 CSV» (el plan dice 5/6). Los valores nuevos (11 y 8) son correctos; el barrido debe buscar el texto real, no el de la tabla.
- El rango `docs/guion_defensa_12min.md:143-146` incluye la línea 144, que **ya es correcta** («embedding de demografía/empleo/demanda social en municipios; referencing por codigo_ine para anuncios»). Aplicar «embedding → referencing» a ese rango corrompería una línea buena. La corrección de DS2-23 debe apuntar solo a `docs/guion_defensa.md:9`.

**Y deja sin cubrir** las líneas que sí contradicen el contrato y la restricción del usuario (véase C-2).

### 4.5 Arreglos que mencionan HDFS/Kafka — ¿asumen viva o flujo Kafka>Mongo?

**Ninguno.** El plan excluye C2/C3 (`plan_fixes_v9.md:223`) y ningún arreglo toca HDFS/Kafka. El flujo real verificado por código es Windows>Kafka>HDFS (`storage/kafka_raw_producer.py:49-79` publica manifiestos; `storage/kafka_hdfs_uploader.py:92-186` consume y hace put WebHDFS), sin Mongo. La nota de planificación del contrato lo confirma (`contrato-reto/spec.md:101`). Los arreglos P2 (T-04, H-SA-02, F-01, H-T1, H-SA-11) no asumen HDFS/Kafka vivos.

**Pero** el barrido documental deja intactas dos líneas que sí describen un flujo o una infra prohibidos:
- `openspec/project.md:38`: «Fuentes → HDFS → Kafka (VM) → **MongoDB**» — describe Kafka→Mongo, prohibido por `contrato-reto/spec.md:167` (ARQUITECTURA-01) y por la restricción del usuario.
- `openspec/project.md:30`: «MongoDB (**Docker Desktop**) + PyMongo» — contradice «sin Docker» (`contrato-reto/spec.md:167`) y ENTREGABLES-01.
- `docs/guion_defensa.md:5`: describe HDFS/Kafka como disponibles («lag 0», «topic vigente»), insuperable ahora (red caída, `00_baseline_v9.md:160-163`).

El plan no introduce estas contradicciones, pero su barrido no las elimina.

---

## 5. Contradicciones

| ID | Arreglo | Evidencia | Impacto |
|---|---|---|---|
| **C-1** | P0-2: `explain_before_after` read-only con `hint:$natural` | El fix fuerza COLLSCAN con el índice presente; el escenario del spec dice «GIVEN el índice ESR eliminado» y `after.totalDocsExamined=1` para el filtro `48001` (`mongodb-y-analisis/spec.md:300-314`). Sonda ejecutada: `48001` → 0 docs; `20069` → 1; `48020` → 8 (`informe_mongo_v9.md:100-105`). El plan aplaza el filtro (`plan_fixes_v9.md:222`) y no actualiza el spec. | **Contratito fix-vs-spec.** C13/T4 siguen siendo demostrables con otro filtro (la rúbrica lo permite), pero el escenario literal del spec queda obsoleto y el demo con filtro por defecto muestra IXSCAN 0. No bloquea la defensa; debe cerrarse actualizando el spec o fijando el filtro. |
| **C-2** | P1-5: barrido documental | El barrido toca `openspec/project.md:6,68,75,80` (figuras) pero no `:38` (Kafka→Mongo) ni `:30` (Docker Desktop); tampoco `docs/guion_defensa.md:5` (HDFS/Kafka vivo). | **Pre-existente, no introducida por el plan, pero no resuelta.** Deja en el repo una línea que describe el flujo prohibido Kafka→Mongo y una mención Docker que el contrato prohíbe. Riesgo de defensa si el tribunal las lee. El barrido debería ampliarse a esas tres líneas. |

**No hay más contradicciones.** Los demás arreglos son consistentes con la rúbrica y el contrato.

---

## 6. Cobertura riesgo (criterios que podrían degradarse)

| ID | Criterio | Riesgo | Causa | Mitigación |
|---|---|---|---|---|
| **R-1** | C13 / T4 | Medio-bajo | El fix read-only mantiene el filtro por defecto `48001` (0 docs); el escenario del spec exige `totalDocsExamined=1`. | Fijar el filtro en `20069` (1 doc) o `48020` (8 docs) y actualizar el escenario del spec. No degrada la rúbrica (que permite «con/sin índice»). |
| **R-2** | C2 / C3 | Bajo | El barrido no toca las cifras/afirmaciones de HDFS/Kafka; el guion sigue diciendo «lag 0» y «352 en HDFS» sin la reserva de red caída. | Añadir en el guion una nota de que la evidencia HDFS/Kafka es el histórico v8 y que la revalidación en vivo está pendiente de red. No cambia la nota (C2 ya está en 7; C3 en 10 por histórico). |
| **R-3** | C9 (Modelado) | Bajo-medio | DS2-23 se enuncia como «embedding → referencing»; aplicado al rango `guion_defensa_12min.md:143-146` borraría la decisión de embedding en `municipios`, que es la que C9 pide justificar. | Corregir solo `docs/guion_defensa.md:9` (que sí es falsa) y redactar «embedding en `municipios`; referencing por `codigo_ine` para `anuncios`». No tocar la línea 144. |
| **R-4** | C6 / C15 | Bajo | `test_mongo_geo.py` con mongomock pierde la aserción sobre el geo real de prod (424/594). | Preservar una lectura read-only de prod en el gate o en otro test; o documentar que la cobertura geo real vive en `informe_mongo_v9.md`. |
| **R-5** | C1 / FORMATO-01 | Bajo (P2 diferido) | F-01 opción 1a («avise en raw» en `extract/_common.py:200-205`) relaja la validación estricta que FORMATO-01 acredita. | Elegir la opción 2 (`RAW_FROZEN`) o 1b (pasar `url`); no debilitar `guardar_json` en raw. |
| **R-6** | C16 | Bajo | Si P0-2 elimina el `explain` de `analysis/run_analisis_mongo.py:1161-1173` en vez de usar la versión read-only, el demo pierde la salida COLLSCAN→IXSCAN. | Mantener la versión read-only en `main()` (la que imprime `explain before/after`), no eliminarla. |

**Ningún criterio que hoy está en 10 degrada a 0 ni a 3 por estos arreglos.** Los criterios en 10 según `matriz_rubrica_v8.md` son C1, C3-C19; los riesgos son de matices o de demo, no de pérdida de nivel.

---

## 7. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `pymongo` de solo lectura: conteos, `list_indexes`, `count_documents` de coordenadas sobre `vivienda_euskadi`.
- `explain("executionStats")` con y sin `hint:{"$natural":1}` para tres filtros.
- `grep -rn` de primitivas de escritura atómica en `transform/`; `grep -c "__main__"` en 7 scripts; `grep -n "_load_dim()"`.
- `read_file` de los ficheros citados.

**Solo leído (sin ejecutar):** los informes v8/v9, el PDF/docx (vía informes), `AGENT.md`, `openspec/config.yaml`, las 5 specs, `docs/**`, `analysis/**`, `storage/**`, `tests/**`, `extract/**`, `transform/**`, `scripts/**`, `.github/workflows/**`.

**No ejecutado (guardrails):** `ensure_indexes()`, tests, `load_all`/`clean_all`, `run_analisis_mongo`, generadores, productor Kafka, gate vivo, instalación, commit/push.

---

## 8. Límites de este informe

- Las sondas de Mongo son una foto con timestamp; el agente paralelo puede seguir mutando (el plan ya advierte `plan_fixes_v9.md:28`).
- No se verificó el estado de HDFS/Kafka más allá de leer el código y el baseline: la red centro sigue caída (`00_baseline_v9.md:160-163`), así que ningún arreglo se juzga por su comportamiento en vivo.
- La verificación es de documento y código, no de ejecución de los arreglos: los fixes están planificados, no aplicados.
- Las referencias de línea apuntan a los ficheros en el estado actual del repo (master, HEAD `47065f6` según `00_baseline_v9.md:12`); pueden moverse si otro agente commitea.

---

## 9. Entrega

- **report_path:** `openspec/audit/v9_2026-11-10/verificacion_rubrica_fixes.md` (este fichero).
- **contradicciones:** C-1 (P0-2 deja obsoleto el escenario INDICES-01 del spec: hint vs «índice eliminado» y filtro `48001` → 0 docs; el plan fija el filtro pero no actualiza el spec) y C-2 (P1-5 no cubre `openspec/project.md:38` Kafka→Mongo, `:30` Docker y `docs/guion_defensa.md:5` HDFS/Kafka vivo).
- **cobertura_riesgo:** R-1 (C13/T4, spec vs filtro por defecto), R-2 (C2/C3, cifras HDFS/Kafka sin reserva de red), R-3 (C9, sobrecorrección del embedding), R-4 (C6/C15, test geo de prod), R-5 (C1/FORMATO-01, opción 1a de F-01), R-6 (C16, eliminar el explain de `main()`).
- **veredicto:** **Ningún arreglo contradice directamente la rúbrica del reto ni las restricciones de infraestructura del usuario; no hay ninguno que asuma HDFS/Kafka vivos ni flujo Kafka→Mongo.** Hay dos contradicciones de segundo orden (C-1, C-2) y seis riesgos de cobertura no bloqueantes (R-1…R-6). Ningún criterio en 10 degrada de nivel por estos arreglos.
- **executed:** sondas `pymongo` read-only (conteos, índices, explain con/sin hint), `grep` de primitivas atómicas/`__main__`/`_load_dim`, `read_file` de los arreglos y specs.
- **read_only:** todo el código, datos, Mongo, HDFS, Kafka; informes v8/v9, baseline, plan, AGENT.md, config, specs, docs.
- **blockers:** ninguno para la verificación. P0-1 sigue requiriendo autorización de escritura en Mongo, hoy prohibida por la misión.
