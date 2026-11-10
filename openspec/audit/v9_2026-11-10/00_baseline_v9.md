# Baseline v9 — 2026-11-10 (read-only)

**Naturaleza:** baseline de solo lectura generado por el agente planificador. No es la auditoría: es la foto de partida.
**Guardrails respetados:** no se escribió en `data/`, Mongo, HDFS ni Kafka; no se ejecutó `load_all`/`clean_all`/`run_analisis_mongo` completo ni el productor Kafka; no se instalaron dependencias; no hubo commit ni push.

---

## 1. Git

| Elemento | Valor |
|---|---|
| HEAD | `47065f699b5c71244a3d2439c2a74cfb74790a42` |
| Rama | `master` (origen `origin/master`) |
| Último commit | `47065f6` docs: auditoria v7 + gobernanza y docs alineados a vivienda_euskadi |
| Árbol de trabajo | 38 entradas: **19 staged**, **15 modified**, **46 ficheros untracked** (4 entradas de directorio) |
| Tracked | 617 ficheros |
| `git diff --check` | limpio (solo avisos de CRLF en `docs/analisis_vault_vs_rubrica.md` y `scripts/verificar_gobernanza.py`) |

**Staged (19):** 10 renombramientos `scratchpad/… → archive/scratchpad/…` y `docs/pendiente_duckdb_pymongo_2026-11-05.md → docs/archive/2026-11/…`, más `.gitignore`, `README.md`, `AGENT.md`, `docs/README.md`, `docs/arquitectura_datos.md`, `docs/auditoria_10_10_SDD_2026-11-05.md`, `docs/guion_defensa.md`, `extract/26_vpo_terminadas.py`, 4 docs de `openspec/changes/2026-11-05-cierre-suficiencia-auditoria/`, `scripts/verificar_gobernanza.py`, `transform/run_all.py`; borrados `requirements-legacy.txt`, `scratchpad/sha1.txt`, `scratchpad/sha2.txt`, `scripts/validar_fuentes_nuevas.py`, `tests/test_fuentes_validacion.py`, `transform/auditoria_duckdb.py`, `transform/generar_dashboard_completo.py`, `transform/generar_dashboard_visual.py`.

**Modified (15):** `.gitignore`, `AGENT.md`, `README.md`, `docs/README.md`, `docs/analisis_vault_vs_rubrica.md`, `docs/arquitectura_datos.md`, `docs/auditoria_10_10_SDD_2026-11-05.md`, `docs/guion_defensa.md`, `extract/26_vpo_terminadas.py`, `scripts/verificar_gobernanza.py`, `transform/run_all.py` y 4 docs de `openspec/changes/2026-11-05-cierre-suficiencia-auditoria/`.

**Untracked (4 directorios):** `openspec/audit/limpieza_2026-11-09/`, `openspec/audit/plan_reauditoria_v8_2026-11-09.md`, `openspec/audit/v8_2026-11-09/`, `openspec/changes/2026-11-09-vpo-sin-staging/`.

> El árbol de trabajo es el estado de partida. **No se tocó.** Los cambios staged/modified son del usuario (limpieza 2026-11-09 + cambio VPO sin staging).

---

## 2. Inventario v9

**Excluidos:** `.git/**`, `.venv/**` (7.264 `.py`, 54 `.md`), `__pycache__/**`, `.pytest_cache/**`, `graphify-out/**` (caché AST, 0 `.py`).

| Extensión | Ficheros |
|---|---:|
| `.md` | **437** |
| `.json` | 249 |
| `.csv` | 214 |
| `.py` | **184** |
| `.html` | 115 |
| `.zip` | 49 |
| `.txt` | 43 |
| `.png` | 37 |
| `.mmd` | 15 |
| `.svg` | 11 |
| `.jpg` | 10 |
| `.xlsx` | 6 |
| `.pdf` | 4 |
| `.yaml` | 3 |
| sin extensión | 8 |
| **Total** | **1.406** |

**`.py` por área:**

| Área | `.py` |
|---|---:|
| `extract/` | 41 |
| `transform/` | 42 |
| `storage/` | 7 |
| `analysis/` | 7 |
| `scripts/` | 7 |
| `tests/` | 30 |
| **Núcleo activo** | **134** |
| `docs/archive/` (histórico) | 35 |
| `archive/` (histórico) | 12 |
| `openspec/audit/` (histórico) | 2 |
| `docs/presentacion/` | 1 |
| **Total** | **184** |

**Ficheros por capa (top):** `data/` 605, `openspec/` 337, `docs/` 146, `vaultVivienda/` 100, `archive/` 47, `transform/` 42, `extract/` 41, `tests/` 30, `demo-kpi/` 9, `demo-mapa/` 8, `analysis/` 7, `scripts/` 7, `storage/` 7, `brief/` 2, `config/` 2, `plan/` 2.

**Tamaño:** `data/` 1,1 GB; `docs/` 12 MB; `openspec/` 3,9 MB; `demo-mapa/` 9,9 MB; `demo-kpi/` 5,0 MB; `vaultVivienda/` 1,3 MB; `archive/` 2,1 MB; `tests/` 1,9 MB; `transform/` 1,3 MB.

> Nota de deriva: v8 inventarió 1.482 ficheros y 193 `.py`; v9 tiene **1.406** y **184**. La diferencia la explica la limpieza 2026-11-09 (59 ficheros retirados) y el re-conteo. El recuento de v8 queda como histórico.

---

## 3. Conteos vigentes

| Elemento | Valor | Cómo se obtuvo |
|---|---|---|
| Tests | **237 colectados · 235 passed · 2 skipped** | `pytest tests` (ejecutado) |
| Ficheros de test | 30 | `find tests -name 'test_*.py'` |
| Requisitos con ID | **46** | `grep -rhoE "^### Requirement: …" openspec/specs/` |
| Specs | 5 (`contrato-reto`, `extraccion-datos`, `almacenamiento-y-streaming`, `mongodb-y-analisis`, `presentacion-de-resultados`) | `find openspec/specs` |
| Scripts `transform/` | **42** (34 en DAG) | `verificar_gobernanza.py` |
| Pipelines | **11** (`PIPELINE_ORDER`) | `analysis/run_analisis_mongo.py` |
| CSV `mongo_*` | **8** | `ls data/resultados/mongo_*.csv` |
| Raw local | **356** ficheros recursivos = 354 canónicos + `.FROZEN` + `.gitkeep` | `find data/raw` |
| Manifest raw | **354** SHA | `wc -l docs/raw_manifest_sha256.txt` |
| Silver | **191** ficheros, **188** entradas en `manifest_sha256.txt`, 42 CSV | `find data/procesado` |
| Resultados | **58** ficheros (8 `mongo_*` + comparativa + bootstrap + PNG + HTML) | `find data/resultados` |
| Mongo colecciones | **30** (16 vivas + 14 `__backup`) | `pymongo` read-only |
| `anuncios` | **594** | `estimated_document_count` |
| `municipios` | **252** | idem |
| `vpo_municipal` | **252** | idem |
| Comparativa | Bilbao **204**, Donostia **126**, Getxo **50**, Vitoria-Gasteiz **39** | `comparativa_3_municipios_mongo.csv` |
| CSV `mongo_*` filas | 253 / 253 / 253 / 253 / 3 / 253 / 323 / 252 | `wc -l` |
| Índices `anuncios` | `idx_anuncios_ine_modalidad_precio`, `idx_anuncios_geo`, `idx_anuncios_portal_id`, `idx_anuncios_equipamiento` | `index_information()` |

---

## 4. Ejecuciones y checks (read-only)

| Check | Comando | Resultado |
|---|---|---|
| Suite | `pytest tests` | exit 0; **235 passed, 2 skipped** |
| Gobernanza | `scripts/verificar_gobernanza.py` | **TODO OK**: 46 requisitos, 42 scripts, 34 DAG, 188 silver, 11 pipelines, 0 env sin declarar |
| DAG | `transform/run_all.py --check` | exit 0 |
| Gate offline | `scripts/gate_extremo_a_extremo.py --offline` | **OK** (354 SHA raw, 188 silver, 14 colecciones, 0 duplicados, lag 0); `PENDA-01` HDFS/Kafka vivo |
| Fase de datos | `scripts/verificar_fase_datos.py` | exit 1 solo por **FAIL 07** conocido (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26); huella `c5c498d3…` |
| Diff | `git diff --check` | limpio |
| Mongo | `pymongo` read-only | 30 colecciones; 594/252/252; índices presentes |
| HDFS | sonda `GETFILESTATUS` | **timeout**; puerto 50070 no alcanzable |
| Kafka | sonda metadata/offsets | **`NoBrokersAvailable`**; puerto 9092 no alcanzable |

**No ejecutados (guardrails):** `load_all`, `clean_all`, `run_analisis_mongo` completo, productor Kafka, gate vivo (`GATE_LIVE=1`), instalación de dependencias, commit/push.

---

## 5. SHA raw / HDFS

- **Raw local:** `data/raw/udalmap_vpo_terminadas.csv` — SHA `70a2937a3026b01c5e73ff641241c2fad0a77c3b995d2863034fba2da1294706` (registrado en v8; el fichero no se ha tocado y el manifest de 354 SHA cuadra con el gate offline).
- **HDFS (v8, histórico):** `data/raw` `fileCount=352`, `directoryCount=6`; VPO `length=35427`, SHA idéntico; `data/procesado` **404**.
- **HDFS (v9):** **no verificable** (puerto 50070 caído). Se usa el histórico v8 como evidencia clasificada, no como revalidación.
- **Manifest local:** 354 SHA; gate offline verifica 354/354 OK.
- **Silver:** 188 entradas; gate offline verifica 188/188 OK.

---

## 6. Estado de H-02…H-07 (y nuevos)

Comprobado por `grep` sobre los documentos activos. **Los seis siguen abiertos**: los documentos no se han tocado desde v8.

| ID | Sev. | Criterio | Estado | Evidencia v9 |
|---|---|---|---|---|
| H-02 | P2 | C9/C12 | **ABIERTO** | `docs/modelo_mongodb.md:11,40,111,115,129,160,162,180` (759, 424/759, 14+13, 10 pipelines, 5 CSV, 173/113/40, explain 759/1) |
| H-03 | P2 | C13 | **ABIERTO** | `README.md:287`, `AGENT.md:4`, `docs/arquitectura_datos.md:69`, `docs/guion_defensa.md:10,33,51`, `docs/guion_defensa_12min.md:175`, `docs/modelo_mongodb.md:129-132` (IXSCAN 1) |
| H-04 | P2 | C12/C16/C19 | **ABIERTO** | `docs/matriz_indicadores.md:19,32`, `docs/informe_final.md:27,145`, `docs/informe_capacidad_mongo.md:3,8,14,48`, `docs/preguntas_analisis_profesional.md:84,91,99,120`, `docs/guion_defensa_12min.md:35,143,171,222` |
| H-05 | P2 | C18 | **ABIERTO** | `docs/modelo_mongodb.md:115`, `docs/matriz_indicadores.md:32`, `docs/preguntas_analisis_profesional.md:84,91,120`, `docs/informe_capacidad_mongo.md:87,88,94,95,99`, `docs/analisis_vault_vs_rubrica.md:35` (173/113/40) |
| H-06 | P2 | C19 | **ABIERTO** | `docs/README.md:34` («la única evidencia válida son los 4 CSV») vs `EXPORTS_8` (8 CSV) |
| H-07 | P2 | Contexto | **ABIERTO** | `openspec/project.md:6,68,75,80` (136 tests, 185 silver, 9 pipelines, 5 CSV, 759, VM pendiente) |
| H-08 | P2 | C1/C2 | **ABIERTO** | `extract/26_vpo_terminadas.py` sin regeneración de manifest al escribir raw nuevo (no se tocó código) |
| H-09 | P2 | C1 | **ABIERTO** | `docs/contrato_datos_raw.md` vs `transform/_raw_guard.py` (`.FROZEN`) |
| H-10 | P3 | C1 | **ABIERTO** | `extract/26_vpo_terminadas.py` `validar()` no comprueba pertenencia a `dim_municipios` |
| H-11 | P3 | C16 | **ABIERTO** | `analysis/run_analisis_mongo.py` argparse dice «9 pipelines + 5 CSV» |
| H-12 | P3 | C10 | **ABIERTO** | `storage/clean_mongo.py` docstring cita 759 |
| H-13 | P3 | Estructura | **ABIERTO** | `docs/archive/scratchpad/bom.json` conserva BOM (`ef bb bf`) y no parsea como JSON estricto |
| **H-14** | P3 | Estructura doc | **NUEVO** | `docs/README.md:36` termina en literal `HTMLEOF` |
| **H-15** | P3 | C18 | **NUEVO** | `docs/analisis_vault_vs_rubrica.md:35` (173/113/40) |

**Cifras vigentes que deben sustituir a las anteriores:** 594 anuncios; 16 vivas + 14 `__backup` = 30 colecciones; **11** pipelines; **8** CSV `mongo_*`; **204/126/50/39**; explain **IXSCAN 68/68**; **237** tests (235 passed, 2 skipped); **188** silver; **354** SHA raw.

---

## 7. Infraestructura

| Servicio | Estado v9 | Evidencia |
|---|---|---|
| Mongo local `localhost:27017` | **OK** | `pymongo` responde; 30 colecciones |
| HDFS centro `10.22.87.215:50070` | **NO alcanzable** | `curl` timeout; puerto cerrado |
| Kafka centro `10.22.87.215:9092` | **NO alcanzable** | `NoBrokersAvailable` |

**Deriva v8→v9:** v8 sí acreditó HDFS (352 raw, `procesado` 404) y Kafka (352/352, lag 0) en vivo. En v9 la red centro no responde. **No es un fallo del proyecto:** se documenta y se usa el histórico v8 como evidencia clasificada. El gate offline lo declara `PENDA-01`.

---

## 8. Qué se comprobó ejecutando vs solo leyendo

**Ejecutado (herramienta real):** `git status/log/rev-parse/diff --check`; `find`/`ls`/`du`/`wc`; `pytest tests` (suite completa, exit 0, 235 passed / 2 skipped); `pytest tests --collect-only -q` (237); `scripts/verificar_gobernanza.py` (TODO OK); `transform/run_all.py --check` (exit 0); `scripts/gate_extremo_a_extremo.py --offline` (OK); `scripts/verificar_fase_datos.py` (exit 1 solo FAIL 07); consultas read-only a Mongo (`list_collection_names`, `estimated_document_count`, `index_information`); sondas de red a HDFS/Kafka; `grep` de cifras en docs; `xxd` del BOM.

**Solo leído (sin ejecutar):** el contenido del PDF y del docx (vía `read_file`, auto-extracción); los documentos de auditoría v8; `openspec/specs/**`; `docs/**` activos (contraste por `grep`, no lectura línea a línea completa); los `.py` (no se ejecutó ni `compileall` ni `ast.parse` en esta sesión: se hizo el inventario y el conteo, no el parseo).

**No comprobado en v9 (requiere red o ejecución pesada):** HDFS `GETFILESTATUS`/`OPEN`/`GETCONTENTSUMMARY`; offsets Kafka; `explain()` vivo (se usa el histórico v8: IXSCAN 68/68); ejecución de los 11 pipelines; byte a byte de todo `data/raw`.

---

## 9. Límites de este baseline

- La red centro está caída: C2 y C3 no se revalidan en vivo.
- No se ejecutó la suite en un entorno limpio; la dependencia oculta de DuckDB ya fue eliminada en la limpieza 2026-11-09, pero no se reinstaló el entorno desde cero.
- Los `git status` con 19 staged / 15 modified / 4 untracked son el estado de partida y **no se tocaron**.
- El baseline es una foto, no un veredicto: el veredicto v9 se producirá en la fase 6.
