# Verificación dinámica v9 — 2026-11-10 (solo lectura)

**Unidad:** W3.1 · **Ronda 4** · **Criterios:** todos (19 rúbrica + Tema 8)
**Instrumento:** `.venv` Python 3.12.10 + pytest 9.1.1 + pymongo → MongoDB 9.0.2 (`localhost:27017`, db `vivienda_euskadi`)
**Guardrails respetados:** no se modificó código, datos, HDFS ni Kafka; no se instalaron dependencias; no hubo commit/push. **No se ejecutó ningún test mutador de producción** (los 6 tests que dropean/recrean índices o escriben en Mongo se deseleccionaron; ver §2.1 y §5.1).
**Aviso de estado:** la base productiva **cambió durante la auditoría** (ver P0-1). Toda medición de Mongo es una foto con timestamp, no un estado congelado.

---

## 0. Ejecutado vs solo leído

**Ejecutado (herramienta real):**

| Comando | Resultado |
|---|---|
| `pytest tests --collect-only -o addopts="" -q` | **237 tests** colectados |
| `pytest tests --collect-only … --deselect <6>` | **231/237 (6 deseleccionados)** |
| `pytest tests -q -rs` (6 mutadores deseleccionados) | exit **0**; 2 skipped; 0 failed |
| `pytest tests -q -rs <25 ficheros focales>` (6 mutadores deseleccionados) | exit **0**; 2 skipped; 0 failed |
| `.venv/Scripts/python.exe -m compileall -q -f extract transform storage analysis scripts tests` | exit **0**; 134 `.py` |
| `ast.parse` sobre los 134 `.py` (sonda en scratch) | **134/134 parsean, 0 errores de sintaxis** |
| `scripts/verificar_gobernanza.py` | **TODO OK** (46 requisitos, 42 scripts, 34 DAG, 188 silver, 11 pipelines, 0 env sin declarar) |
| `transform/run_all.py --check` | exit **0** (34 scripts, todos `[OK ]`) |
| `scripts/gate_extremo_a_extremo.py --offline` | **RESULTADO gate: OK** (354 SHA raw, 188 silver, 14 colecciones, 0 duplicados, lag 0); `PENDA-01` HDFS/Kafka |
| `scripts/run_mongo_pipeline.py --dry-run` | `dry-run: imports ok, ping=True, sin mutar producción`; exit **0** |
| `scripts/verificar_fase_datos.py` | **PASS 17/18**; solo **FAIL 07** conocido (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26); huella `c5c498d3…`; su sub-check 11 `pytest tests/test_fase_datos.py` → PASS |
| `git diff --check` | exit **0**; solo avisos CRLF en `docs/analisis_vault_vs_rubrica.md` y `scripts/verificar_gobernanza.py` |
| Sondas Mongo read-only (`list_collection_names`, `estimated_document_count`, `list_indexes`, `serverStatus`, `currentOp`) | ver §3 |
| `grep -a` sobre `mongod.log` (`/c/Program Files/MongoDB/Server/9.0/log/mongod.log`) | ver P0-1 |

**Solo leído (sin ejecutar):** `AGENT.md`, `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `informe_extract.md`, `informe_transform.md`, `informe_storage_analysis_scripts.md`, `informe_mongo_v9.md`, `informe_datos_v9.md`, `mapa_tests.md`, `rubrica_reextraida.md`, `mapa_requisitos.md`, `desviaciones_rubrica_contrato.md`, `.github/workflows/quality-gate.yml`, `requirements.txt`, `pyproject.toml`, `.env.example`, `.env`, `storage/mongo.py`, `storage/load_mongo.py`, `storage/clean_mongo.py`, `analysis/mongo_indexes.py`, `analysis/mongo_aggregations.py`, `tests/test_mongo.py`, `tests/test_mongo_indices.py`, `tests/test_mongo_consistencia.py`, `tests/test_mongo_pipeline.py`, `tests/test_pisos_ubicacion_real.py`.

**No ejecutado (guardrails):** los 6 tests mutadores (`test_mongo.py::test_indexes_explain`, `::test_explain_promo`, `::test_clean_mongo`, `::test_crud_demo`, `test_mongo_indices.py::test_indexes_explain_totalDocsExamined`, `test_mongo_consistencia.py::test_atomicidad_documental`); `load_all`/`clean_all`/`ensure_indexes`; `run_analisis_mongo`; `explain_before_after`; el productor Kafka; el gate vivo (`GATE_LIVE=1`); ninguna instalación; ningún commit/push.

---

## 1. Suite completa y focales

### 1.1 Suite completa

```
$ .venv/Scripts/python.exe -m pytest tests -q -rs \
    --deselect tests/test_mongo.py::test_indexes_explain \
    --deselect tests/test_mongo.py::test_explain_promo \
    --deselect tests/test_mongo_indices.py::test_indexes_explain_totalDocsExamined \
    --deselect tests/test_mongo.py::test_clean_mongo \
    --deselect tests/test_mongo.py::test_crud_demo \
    --deselect tests/test_mongo_consistencia.py::test_atomicidad_documental
………………… [100%]
SKIPPED [1] tests/test_pisos_ubicacion_real.py:202: artefactos de data/resultados no versionados …
SKIPPED [1] tests/test_pisos_ubicacion_real.py:255: skip separado: MONGO_ALLOW_DESTRUCTIVE!=1
EXIT=0
```

- **exit 0**, **2 skipped**, **0 failed**, **0 error**.
- Colecta: `237 tests collected`; con los 6 deseleccionados: `231/237 tests collected (6 deselected)`. La suite ejecutó **231** tests.
- Los 2 skips son exactamente los documentados en `mapa_tests.md` H-T6: artefactos no versionados y `MONGO_ALLOW_DESTRUCTIVE!=1`.
- **Versión de pytest:** el `.venv` tiene **pytest 9.1.1**; `requirements.txt` fija `pytest==8.3.3`. La suite se ejecutó con una versión **distinta de la declarada** (no se instaló nada). Es el mismo desajuste que `mapa_tests.md` §9 ya registró como límite.

### 1.2 Suites focales

| Focal | Ficheros | Resultado |
|---|---|---|
| **raw** | `test_crudos.py`, `test_raw_guard_runtime.py`, `test_raw_guardrails.py`, `test_raw_inmutable.py`, `test_manifest_sha.py`, `test_fase_datos.py` | incluidos en la pasada focal: exit 0 |
| **vpo** | `test_vpo_municipal.py` | incluido: exit 0 |
| **mongo** | `test_clean_mongo.py`, `test_integracion_mongo.py`, `test_load_mongo.py`, `test_mongo.py`, `test_mongo_comparativa.py`, `test_mongo_consistencia.py`, `test_mongo_geo.py`, `test_mongo_indices.py`, `test_mongo_orquestador.py`, `test_mongo_pipeline.py`, `test_mongo_pymongo_pro.py`, `test_mongo_queries.py` (6 mutadores deseleccionados) | incluidos: exit 0 |
| **contrato** | `test_contrato.py` | incluido: exit 0 |
| **manifest** | `test_manifest_sha.py`, `test_raw_inmutable.py` | incluidos: exit 0 |
| **run_all** | `test_run_all.py` | incluido: exit 0 |
| **extremo a extremo** | `test_extremo_a_extremo.py` | incluido: exit 0 |

Comando único (25 ficheros, 6 mutadores deseleccionados):

```
$ .venv/Scripts/python.exe -m pytest tests -q -rs <25 ficheros> --deselect <6>
EXIT_FOCALES=0 ; 2 skipped ; 0 failed ; 0 error
```

**Lectura:** la suite es verde **porque se deseleccionaron los 6 tests que escriben en Mongo**. Sin esa deselección, la suite ejecuta `explain_before_after()` / `explain_promo_before_after()` sobre la colección viva (H-T2) y `test_load_all_no_silencia_indices` llama a `load_mongo.load_all()` real (§5.1). El verde no es evidencia de que la suite sea segura de ejecutar en producción.

---

## 2. Gates

| Gate | Comando | Salida literal | Veredicto |
|---|---|---|---|
| Gobernanza | `scripts/verificar_gobernanza.py` | `OK requisitos: 46 cabeceras, 46 IDs únicos` · `OK transform: 42 scripts, 34 nodos DAG` · `OK silver: 188 entradas` · `OK env: sin declarar: ninguna` · `OK pipelines: 11 pipelines en PIPELINE_ORDER` · **`TODO OK`** | **OK** |
| DAG | `transform/run_all.py --check` | 34 líneas `[OK ] …` (parsear_secciones … auditar_lagunas_silver); `EXIT_CHECK=0` | **OK** |
| Gate offline | `scripts/gate_extremo_a_extremo.py --offline` | `OK manifiesto raw 354 SHA` · `OK silver 188` · `OK 14 colecciones` · `OK 0 duplicados en reintentos` · `OK lag 0` · `PENDA-01: HDFS/Kafka centro (10.22.87.215) solo en vivo mañana; pendiente hoy.` · **`RESULTADO gate: OK`** | **OK** (con PENDA-01 declarado) |
| Mongo pipeline | `scripts/run_mongo_pipeline.py --dry-run` | `dry-run: imports ok, ping=True, sin mutar producción`; exit 0 | **OK** |
| Fase de datos | `scripts/verificar_fase_datos.py` | `PASS 01…PASS 06`, **`FAIL 07 FAIL conocido paro-cero (Aramaio 0.28, Gaintza 1.45, Usansolo 3.26)`**, `PASS 08…PASS 18` · `RESULTADO: PENDIENTE (ver FAIL)` · `HUELLA SHA-256: c5c498d3…` | **PENDIENTE** (solo FAIL 07; igual que baseline v9 y v8) |
| Compile | `compileall` + `ast.parse` | 134/134 `.py`, 0 errores de sintaxis | **OK** |
| Diff | `git diff --check` | exit 0; avisos CRLF en 2 ficheros | **OK** |

**Nota sobre `verificar_fase_datos.py`:** el FAIL 07 es el conocido paro-cero de 3 municipios, documentado y no enmascarado; el propio script emite la huella y el resultado PENDIENTE. No es un fallo nuevo.

---

## 3. Mongo: estado observado (concurrente, no congelado)

Sondas read-only con pymongo (sin escribir):

| Timestamp | `anuncios` | `etxbide_promociones` | `municipios` | `vpo_municipal` |
|---|---|---|---|---|
| 08:57:29 | 594 docs; **solo `_id_`** | 406 docs; `idx_promo_ine_estado_tipo` | 252; `idx_municipios_territorio_nombre` | 252 |
| 09:01:33 | 594 docs; solo `_id_` | **406 docs**; `idx_promo_ine_estado_tipo` | 252 | 252 |
| 09:02:41–09:09:25 | 594 docs; solo `_id_` | **ausente** (0 docs, sin índices, la colección ya no existe) | 252 | 252 |

- `anuncios.fecha_carga` = `2026-11-10 07:59:48`; `anuncios__backup.fecha_carga` = `07:58:44`.
- `serverStatus.uptime` ≈ 73 900 s; con `conn497`/`conn521` operando sobre `vivienda_euskadi.anuncios` a las 08:58:45 y 08:59:48 (ver P0-1).
- **El estado de la base productiva no es estable durante la auditoría.** La colección `etxbide_promociones` (406 documentos) y su `__backup` desaparecieron entre las 09:01:33 y las 09:02:41, mientras yo solo ejecutaba sondas read-only. Los índices de `anuncios` (los 4 documentados en `informe_mongo_v9.md`) están ausentes.

---

## 4. CI

`.github/workflows/quality-gate.yml` (solo leído):

```yaml
jobs:
  pytest_offline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - name: Instalar
        run: pip install -r requirements.txt pytest mongomock
      - name: Pytest offline (sin red)
        run: python -m pytest tests -q
        env: { GATE_LIVE: '0' }
  gate_vivo_manual:
    if: github.event_name == 'workflow_dispatch' && inputs.gate_vivo == true
    steps:
      - run: python scripts/gate_extremo_a_extremo.py --vivo
        env: { GATE_LIVE: '1' }
```

**H-T1 confirmado por lectura del workflow:** el job `pytest_offline` **no define ningún `services:`** (ni Mongo ni ningún contenedor). `mapa_tests.md` ya acreditó con ejecución que, con Mongo inalcanzable, la suite da **31 ERROR + 9 FAILED** (40 tests exigen Mongo vivo) y que solo 3 ficheros tienen guard `skipif` por Mongo ausente. Por tanto:

- El job `pytest_offline` **no puede pasar en GitHub Actions** (fallará en el mismo `pip install`/pytest por los 40 tests que requieren `localhost:27017`).
- El job `gate_vivo_manual` sonda `10.22.87.215` (IP privada del centro) desde un runner público de GitHub: es inalcanzable por diseño; el job **nunca puede pasar** en GitHub (H-SA-11).
- El workflow **no ejecuta** `verificar_gobernanza.py`, `run_all.py --check` ni `run_mongo_pipeline.py --dry-run` (H-SA-11).

---

## 5. Hallazgos

**Recuento: P0 = 1 · P1 = 1 · P2 = 2 · P3 = 1.**

| ID | Sev. | Título | Evidencia | Impacto |
|---|---|---|---|---|
| **P0-1** | **P0** | **La base productiva mutó durante la auditoría:** `etxbide_promociones` (406 docs) y su `__backup` desaparecieron, y `anuncios` perdió sus 4 índices. El `mongod.log` prueba dropeos/renames sobre `vivienda_euskadi.anuncios` a las 08:58:45 y 08:59:48, y drops sobre `vivienda_euskadi_test` a las 08:59:49, durante mi ventana de ejecución. | `mongod.log`: `resource":"vivienda_euskadi.anuncios","reason":"renameCollection"` (conn497, 08:58:45; conn521, 08:59:48); `resource":"vivienda_euskadi_test._probe_clean","reason":"drop"` (conn524, 08:59:49). Sondas propias: 09:01:33 `etx=406`+índice → 09:02:41 `etx=0`/colección ausente → 09:09:25 `etx` ausente, `anuncios` solo `_id_`. | **La evidencia de Mongo no es una instantánea congelada y parte de ella se perdió.** No pude restaurar nada (guardrail). C2/C3/C19 y cualquier cifra derivada de `etxbide_promociones` quedan sin base en este estado. **Reportado, no arreglado.** |
| **P1-1** | **P1** | La suite **no era segura de ejecutar contra producción**: `test_mongo_geo.py:13` llamaba `load_anuncios()` real (sin aislar) y los tests de `explain` dropeaban/recreaban índices. Corrección `2026-11-10-defensa-v9-p0`: `test_mongo_geo.py` usa `get_test_db()` y el explain es read-only con `hint:{"$natural":1}`. `test_load_all_no_silencia_indices` **no** mutaba prod: `tests/test_mongo_consistencia.py:131-144` parchea los 14 loaders a `lambda: 1` y `ensure_indexes`, así que `load_all()` no llama a `replace_collection()`; solo lee conteos de prod en solo lectura. | `tests/test_mongo_consistencia.py:131-144` (loaders y `ensure_indexes` parcheados); `tests/test_mongo_geo.py:27` (`get_test_db`); `analysis/mongo_indexes.py:101-138` (explain read-only); `storage/load_mongo.py:590-616` (`load_all` → `replace_collection` + `ensure_indexes`). | La suite completa (sin deseleccionar) dropeaba/recreaba colecciones vivas y dejaba índices ausentes. Tras el cambio, `pytest tests -q` es verde (235 passed + 2 skipped) y `list_indexes()`/recuentos de prod son idénticos antes/después. |
| **H-T1** | **P2** | La suite no es hermética: 40 tests exigen Mongo local y el CI no lo provee. | `mapa_tests.md` (ejecutado): `MONGO_HOST=127.0.0.1 MONGO_PORT=1 pytest tests` → 31 ERROR + 9 FAILED; `.github/workflows/quality-gate.yml` sin `services:` (este informe, §4). | El job `pytest_offline` no puede pasar en GitHub. |
| **H-T2** | **P2** | Los tests mutan producción Mongo: drop→create de índices ESR. | `tests/test_mongo.py:290,333`; `tests/test_mongo_indices.py:17,33` → `analysis/mongo_indexes.py:124-131,141-148` (este informe, solo leído; ya documentado en `mapa_tests.md` y `informe_mongo_v9.md` HM-01/H-SA-06). | Ventana sin índice; si `create_index` falla o el test se interrumpe, el índice prod queda ausente. Es consistente con el estado observado en P0-1. |
| **H-SA-11** | **P3** | CI solo ejecuta `pytest`; no corre gobernanza, `run_all --check` ni `run_mongo_pipeline --dry-run`; el job vivo sonda una IP privada desde runner público. | `.github/workflows/quality-gate.yml:17-43` (este informe, §4). | Cobertura de gates incompleta; `gate_vivo_manual` no puede pasar en GitHub. |

**Hallazgos heredados que esta unidad confirma o no contradice:** H-T3 (dependencia del cwd), H-T4 (hallazgos R1/R2 sin tests), H-T5 (assert tautológico), H-T6 (skips que enmascaran), H-T7 (valores vivos pinneados), H-T8 (8 requisitos y T7 sin test) — todos de `mapa_tests.md`, no re-ejecutados en esta unidad.

---

## 6. Criterios cubiertos

- **C1–C19:** la suite verde (231/2, 2 skipped) y los gates OK cubren formalmente todos los criterios con test, con las reservas de `mapa_tests.md` (C9/C17/C19 parciales; C13 con mutación de prod).
- **C2/C3:** no revalidables en vivo (HDFS 50070 / Kafka 9092 caídos); el gate offline declara `PENDA-01`. No se infla ni degrada la nota por la caída de red.
- **C19:** los 8 CSV `mongo_*` y los artefactos se verifican en disco (`verificar_fase_datos.py` PASS 01–04, 06, 17), pero el test de artefactos (`test_pisos_ubicacion_real.py:202`) está **SKIPPED** y `etxbide_promociones` ya no existe en prod (P0-1).
- **Tema 8:** T2–T6 cubiertos por tests; T1 parcial; T7 sin test (defensa oral).

---

## 7. Bloqueos y límites

- **P0-1:** la base productiva cambió durante la auditoría; **no se restauró nada** (guardrail de solo lectura). Las cifras de Mongo de esta unidad son fotos con timestamp.
- **Límite:** no ejecuté los 6 tests mutadores para no agravar P0-1; su efecto se documenta por lectura del código y por el `mongod.log`.
- **Límite:** la red centro (HDFS 50070 / Kafka 9092) no se sondea en esta unidad; el gate offline lo declara `PENDA-01`.
- **Límite:** `pytest` 9.1.1 en `.venv` vs `pytest==8.3.3` en `requirements.txt` (no se instaló nada).
- **Límite:** no ejecuté `compileall` sobre el árbol completo (solo sobre `extract transform storage analysis scripts tests`); `docs/archive/`, `archive/`, `openspec/audit/` y `.venv/` quedan fuera, igual que en el inventario del baseline.

---

## 8. Entrega

- **report_path:** `openspec/audit/v9_2026-11-10/verificacion_dinamica.md` (este fichero).
- **criteria_covered:** 19/19 criterios con suite+gates (reservas de `mapa_tests.md`); C2/C3 no revalidables en vivo (PENDA-01); C19 con artefactos verificados en disco y 1 test SKIPPED.
- **findings:** P0-1 (P0, producción mutada durante la auditoría: `etxbide_promociones` y sus índices ausentes), P1-1 (P1, la suite no es segura contra producción: `load_all` real y parcheo insuficiente), H-T1 (P2, CI sin Mongo), H-T2 (P2, tests mutan índices prod), H-SA-11 (P3, CI no corre los gates).
- **executed:** suite 231/2 (6 mutadores deseleccionados) exit 0; focales 25 ficheros exit 0; `compileall` 134 `.py` exit 0; `ast.parse` 134/134; gobernanza TODO OK; `run_all --check` exit 0; gate offline OK; `run_mongo_pipeline --dry-run` exit 0; `verificar_fase_datos` PASS 17/18 (solo FAIL 07); `git diff --check` exit 0; sondas Mongo read-only; `grep` sobre `mongod.log`.
- **read_only:** todo el código, datos, Mongo, HDFS, Kafka; los informes R1–R3, baseline, plan, AGENT.md, workflow, requirements, `.env*`; `storage/mongo.py`, `storage/load_mongo.py`, `storage/clean_mongo.py`, `analysis/mongo_indexes.py`, `tests/*`.
- **blockers:** **P0-1** (producción mutada; no restaurada). La auditoría dinámica no puede declararse limpia sobre una base que cambió durante la medición.
