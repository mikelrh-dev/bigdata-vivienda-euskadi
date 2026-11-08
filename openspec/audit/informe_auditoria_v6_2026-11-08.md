# Auditoría integral v6 — `bigdata-vivienda-euskadi`

**Fecha:** 2026-11-08 · **Baseline:** `3171d5a906062f5bb85ab2e0c0423af604979a6a` (rama `master`)
**Modo:** solo lectura. Única escritura: `openspec/audit/` (informe, CSV y evidencia).
**Método:** framework `archive/framework_auditoria_completo2/` (rúbrica 0/3/7/10, P1/P2/P3, semáforo GO/NO-GO) + catálogo de IDs v5.
**Evidencia:** `openspec/audit/evidencia/2026-11-08/` (logs crudos de cada comando).

---

## 0. Veredicto

**APTO CON RESERVAS.** No hay P0: no hay secretos versionados, los dos manifiestos verifican 354/188 con 0 errores, la suite pasa (240 passed, 2 skipped) y los conteos de producción son estables (594 anuncios, 252 municipios, 594/594 con `codigo_ine` de 5 dígitos).

Hay **4 hallazgos P1**, **9 P2** y **6 P3**. Los P1 no rompen la demo, pero **contradicen cifras que el evaluador verá en README, AGENT, guion y spec**, y dos gates automatizados (`run_all --check` y `verificar_fase_datos`) terminan en rojo. Corregirlos es trabajo documental y de rerun, no de rediseño.

| Gate | Resultado | Evidencia |
|---|---|---|
| `pytest tests` | **240 passed, 2 skipped**, exit 0 | `pytest_exacto.txt` |
| `gate_extremo_a_extremo.py --offline` | **OK**, 354/188/14/0/lag 0; PENDA-01 pendiente | `gate_offline.txt` |
| `gate_extremo_a_extremo.py --vivo` sin `GATE_LIVE` | **exit 2** (aborta sin red) | `gate_vivo_sin_env.txt` |
| `extract/generar_manifest.py --verify` | **OK**: 354 raw + 188 silver, 0 errores | `manifest_verify.txt` |
| `transform/run_all.py --check` | **exit 1**: 1 script desactualizado | `run_all_check.txt` |
| `scripts/verificar_fase_datos.py` | **exit 1 / PENDIENTE**: FAIL 07 paro-cero | `verificar_fase_datos.txt` |
| `scripts/verificar_gobernanza.py` | **exit 1**: 3 cifras canónicas desfasadas | `gobernanza.txt` |

---

## 1. Integridad de la auditoría y cobertura de ficheros

### 1.1 Baseline pineado

| Comprobación | Valor |
|---|---|
| HEAD | `3171d5a906062f5bb85ab2e0c0423af604979a6a` |
| Árbol (al pinear) | 22 entradas = 3 `M` + 19 `??`; 416 ignoradas. Tras añadir este informe y el CSV: 3 `M` + 21 `??` |
| Digest del diff | `2f16f8e4f3c8139951cf66971c214f9c96d5f22b84adc7bf79fa01fe04ea7e8d` |
| Digest del índice | `7b486d93bc52561d20b7dbe2f76eeca40ecc9779180a9b89d3ce5ad9d4990b94` |
| `git diff --check` | limpio (exit 0) |
| Python | 3.12.10 (`.venv`) |

> El digest se capturó al cierre, no al abrir. Se compensa con que **no se escribió fuera de `openspec/audit/`**: el diff de los 3 ficheros modificados es el que ya existía al empezar (`+604/−36`).

### 1.2 Barrido de ficheros (no se dejó ninguno fuera del inventario)

`openspec/audit/evidencia/2026-11-08/inventario_archivos.csv`: **1416 filas**, una por fichero, con tamaño, líneas, SHA-256, estado git, sintaxis Python y patrones encontrados.

| Tipo | Ficheros | Comprobación aplicada |
|---|---:|---|
| `.md` | 413 | Inventario + enlaces internos (20 resolubles; 9 rotos, todos en `archive/`) |
| `.json` | 301 | 199 parseados OK (los >25 MB solo tamaño); **0 JSON inválidos** |
| `.csv` | 201 | 185 cabeceras leídas; **5 mal** (3 ECVI con cabecera vacía, 2 en latin-1); 18 sin BOM |
| `.py` | 190 | **0 errores de sintaxis** (`compile()` de los 190) |
| `.html` | 115 | Inventario; dashboards marcados como manuales en `data/resultados/README.md` |
| `.zip` | 49 | Inventario y tamaño (no se descomprimen: datos de origen) |
| `.png` | 46 | Inventario (28 principales + 8 anexo + 10 de presentación/demo) |
| `.txt` | 20 | Inventario |
| `.jpg` | 12 | Inventario (capturas de presentación) |
| `.svg` | 11 | Inventario |
| `.mmd` | 10 | Inventario |
| Otros | 49 | Inventario |
| **Total** | **1416** | **560 tracked + 856 no trackeados** (19 `??` reales + 837 dentro de rutas ignoradas) |

**13 ficheros >25 MB** no se hashearon (solo tamaño/mtime): los 3 certificados energéticos (118/73/55 MB), `distancias_b5m_gipuzkoa.json` (92 MB ×2), `serpavi_renta_municipal.xlsx` (71 MB) y otros. Es una limitación declarada, no un hallazgo.

**Lectura por tipo:** no se leyó línea a línea cada binario ni cada CSV de 118 MB; se auditó su existencia, tamaño, hash (cuando aplica), cabecera/parseo y su coherencia con manifiestos y conteos. Todo fichero de texto con extensión auditables pasó por el barrido de patrones.

---

## 2. Baseline medido hoy

| Hecho | Valor | Fuente |
|---|---:|---|
| Tests colectados | **242** (197 funciones, 32 ficheros) | `pytest --collect-only` |
| Tests ejecutados | **240 passed, 2 skipped** en 18,63 s | `pytest_exacto.txt` |
| `data/raw` / manifest | **356 / 354** | `find`, `wc -l` |
| `data/procesado` / manifest silver | **191 / 188** | `find`, gate |
| `data/resultados` | **58** = 50 raíz + 8 anexo | `find` |
| CSV de resultados | **17** (8 `mongo_*.csv`) | `ls` |
| PNG | **28 principales + 8 anexo = 36** | `find` |
| `extract/*.py` | 41 | `ls` |
| `transform/*.py` | **45**; DAG **34**; 11 fuera | AST de `run_all.py` |
| Pipelines | **11** en `PIPELINE_ORDER` | `run_analisis_mongo.py:49` |
| Mongo `vivienda_euskadi` | **30 colecciones = 16 vivas + 14 `__backup`** | `mongo_audit.json` |
| `anuncios` | **594**; 594 con `codigo_ine` de 5 dígitos; 594 con GeoJSON Point | idem |
| `municipios` | **252**; todos `_id` de 5 dígitos | idem |
| Changes vivos | **6** + 32 archivados en `archive/` | `ls` |
| Secretos trackeados | **0** (`.env` y `api.txt` ignorados) | `git ls-files` |

**Colecciones vivas (16):** `alquiler_municipal` 252, `anuncios` 594, `anuncios_habitaciones_unificados` 201, `anuncios_habitaciones_unificados_bigdata` 201, `certificados_energeticos` 252, `ecvi_compraventa` 29, `emancipacion_juventud` 1, `etxebide_promociones` 406, `etxebide_solicitudes` 5040, `indicadores` 252, `municipios` 252, `osrm_tiempos` 252, `udalmap_empleo` 252, `udalmap_extendido` 252, `udalmap_indicadores` 252, `vpo_municipal` 252.

---

## 3. Hallazgos

### P1 — bloquean el 10 de un criterio o contradicen la defensa

| ID | Hallazgo | Evidencia |
|---|---|---|
| **P1-01** | Cifras nucleares desfasadas en README/AGENT/arquitectura/guion: 14 colecciones, 10 pipelines, 44 scripts, 12 PNG (13 emitidos), 6 CSV, 178 tests, 759 anuncios. Lo medido es 16 vivas, 11 pipelines, 45 scripts, 28+8 PNG, 8 CSV Mongo (17 totales), 242 tests, 594 anuncios. | `README.md:102,103,120,165,166`; `AGENT.md:4,9`; `docs/arquitectura_datos.md:60,61,69`; `docs/guion_defensa.md:19,32`; `mongo_audit.json`; `pytest_exacto.txt` |
| **P1-02** | La spec se contradice con su propia implementación: exige/declara `13 PNG + 6 CSV` y `759 anuncios/424 Point`, cuando hay 8 CSV Mongo, 28+8 PNG y 594/594 Point. | `openspec/specs/mongodb-y-analisis/spec.md:188,395,401,439`; `mongo_audit.json`; `data/resultados/README.md` |
| **P1-03** | El gate del DAG no pasa: `run_all.py --check` sale 1 por `normalizar_json_crudos.py` desactualizado (entradas más nuevas que salidas). La afirmación «34/34» no es reproducible hoy sin regenerar. | `run_all_check.txt`; `transform/run_all.py` |
| **P1-04** | El gate de fase no pasa: `verificar_fase_datos.py` deja **FAIL 07** (paro-cero en Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26) y devuelve `PENDIENTE`; README/arquitectura siguen vendiendo «18/18». | `verificar_fase_datos.txt`; `scripts/verificar_fase_datos.py`; `docs/arquitectura_datos.md:58` |

### P2 — deuda que degrada auditoría, defensa o reproducibilidad

| ID | Hallazgo | Evidencia |
|---|---|---|
| **P2-01** | `verificar_gobernanza.py` sale 1: espera 45 requisitos, 44 scripts y 10 pipelines; hay 46 IDs numéricos, 45 scripts y 11 pipelines. | `gobernanza.txt`; `scripts/verificar_gobernanza.py` |
| **P2-02** | Mongo tiene 16 colecciones vivas frente al contrato de 14; las 2 extra son `anuncios_habitaciones_unificados` y `..._bigdata`, con 201 documentos y las mismas claves (posible duplicado legacy). | `mongo_audit.json`; `analysis/mongo_aggregations.py:668,673` |
| **P2-03** | El CI dispara en `push` a `main`, pero la rama es `master`: el gate no corre en push. | `.github/workflows/quality-gate.yml:7`; `git branch --show-current` |
| **P2-04** | 50 cabeceras de requisito, 46 con ID numérico y 4 `chart_*` sin ID; gobernanza solo cuenta 46. Trazabilidad incompleta. | `matriz_requisitos_2026-11-08.csv`; `presentacion-de-resultados/spec.md` |
| **P2-05** | Delta sin commitear: 3 `M` (+604/−36) y 19 `??`, incluidos gate, CI, 10 tests, `pyproject.toml`, `Makefile`, `uv.lock` y `generar_figuras_N.py`. | `git status`; `git diff --stat` |
| **P2-06** | `data/resultados` solo versiona `.gitkeep`: 58 artefactos locales no están en git; un test se salta por ello. | `git ls-files data/resultados`; `tests/test_pisos_ubicacion_real.py:202` |
| **P2-07** | El framework archivado no es ejecutable: `diagnostico.py` calcula `ROOT` como `parent.parent` y apunta a `archive/`; el runbook invoca `verificar_fase_datos.py` en raíz (real: `scripts/`). | `archive/framework_auditoria_completo2/diagnostico.py`; `07_runbook_agente.md` |
| **P2-08** | El gate offline valida 14 nombres contra el código, no contra Mongo: con 16 vivas sigue en verde. | `gate_offline.txt`; `scripts/gate_extremo_a_extremo.py` |
| **P2-09** | Dos fuentes de verdad documentales chocan: `README.md` (12 PNG/6 CSV/10 pipelines) vs `data/resultados/README.md` (28+8 PNG/8 CSV/11 pipelines). | Ambos README |

### P3 — higiene

| ID | Hallazgo | Evidencia |
|---|---|---|
| **P3-01** | 9 enlaces markdown rotos, todos en documentación archivada de la VM. | Barrido de enlaces |
| **P3-02** | 5 CSV raw con cabecera vacía o latin-1 (3 ECVI, `etxebide_indicador_86`, `udalmap_vpo_terminadas`); 18 CSV sin BOM, uno de resultados. | Barrido CSV |
| **P3-03** | 98 `except Exception` y 289 `print()` en código activo (extract/transform/storage/analysis/scripts/tests). | Conteo por grep |
| **P3-04** | 20 asserts débiles (`assert True`/`is not None`) y 2 skips justificados. | Conteo tests + `pytest -rs` |
| **P3-05** | `.env.example` empieza con `[TEMPLATE]`, línea que no es `KEY=VALUE`; 15 variables declaradas, 0 usadas sin declarar. | `.env.example`; `gobernanza.txt` |
| **P3-06** | `storage/load_mongo.py` define 14 loaders; las 2 colecciones de habitaciones se leen en agregaciones pero no se cargan allí, sin dueño documentado. | `storage/load_mongo.py`; `analysis/mongo_aggregations.py:668` |

---

## 4. Resultados por dominio (18)

| Dominio | Veredicto | Evidencia principal |
|---|---|---|
| **PRE** Preflight | CUMPLE CON SALVEDAD | Baseline, entorno y accesos OK; digest de apertura no capturado |
| **CTR** Contrato | **NO CUMPLE** | Spec con 13 PNG/6 CSV y 759 anuncios (P1-02); pesos y umbrales no alterados |
| **REQ** Requisitos | CUMPLE CON SALVEDAD | 50 cabeceras / 46 IDs; 4 `chart_*` sin ID; 118 escenarios; 130 SHALL |
| **EXT** Extracción | CUMPLE | 41 extractores, 40 fuentes, `main()` y raw; manifiesto raw 354/354 |
| **TRF** Transformación | **NO CUMPLE** | 45 scripts / 34 DAG; `--check` sale 1 por staleness (P1-03) |
| **MON** Mongo/CRUD | CUMPLE CON SALVEDAD | 594/252 estables, 594/594 `codigo_ine` y geo; 16 vivas vs 14 contrato |
| **IDX** Índices | CUMPLE | 24 índices en 16 colecciones (16 `_id` + 8 de negocio); COLLSCAN→IXSCAN |
| **AGG** Agregaciones | CUMPLE | 11 pipelines, 8 CSV Mongo, `$group/$lookup/$unwind` |
| **REP** Reproducibilidad | CUMPLE CON SALVEDAD | Manifiestos 0 errores; `run_analisis` +595 líneas sin commitear |
| **DAT** Datos | CUMPLE CON SALVEDAD | dim 252/252; 594 anuncios en 64 municipios; capas 159/93/252; tier no re-contado |
| **TST** Tests | CUMPLE CON SALVEDAD | 240 passed / 2 skipped; 20 asserts débiles |
| **INF** HDFS/Kafka | **NO VERIFICABLE** | Sin acceso al centro; solo código, configuración y evidencia congelada |
| **VIS** Visualización | CUMPLE CON SALVEDAD | 36 PNG y 8 CSV desde Mongo; README dice 12/6 |
| **DOC** Documentación | **NO CUMPLE** | Deriva numérica extensa (P1-01, P2-09) |
| **SEC** Seguridad | CUMPLE | 0 secretos trackeados, `.env`/`api.txt` ignorados, 0 env sin declarar |
| **COD** Código | CUMPLE CON SALVEDAD | 0 errores de sintaxis; 98 `except Exception`, 289 prints |
| **GIT** Repositorio | CUMPLE CON SALVEDAD | 3 M + 19 ??; 6 changes sin archivar; sin atribución de agente |
| **DEF** Defensa | CUMPLE CON SALVEDAD | 4 municipios, 8 CSV, 36 PNG; guion con cifras viejas |

---

## 5. Bloque delta: gate extremo a extremo (`GTE`)

| ID | Punto | Veredicto | Evidencia |
|---|---|---|---|
| GTE-01 | Offline pasa y no usa red | CUMPLE | exit 0; test con `socket.create_connection` prohibido |
| GTE-02 | Umbrales 354/188/14/0/lag 0 | CUMPLE CON SALVEDAD | 354/188 OK; 14 es lista de código, no Mongo real (16) |
| GTE-03 | `--vivo` sin `GATE_LIVE` aborta | CUMPLE | exit 2 con mensaje PENDA-01 |
| GTE-04 | `--vivo` con centro | NO VERIFICABLE | Sin acceso a 10.22.87.215 |
| GTE-05 | No escribe en `data/` | CUMPLE CON SALVEDAD | Código read-only y test hermético; sin par de hashes antes/después |
| GTE-06 | 10 tests nuevos afirman umbral | CUMPLE | `test_umbrales_normativos`, tamper y conteo |
| GTE-07 | E2E hermético | CUMPLE | `tmp_path` + fakes + socket bloqueado |
| GTE-08 | Integración Mongo mock/skip | CUMPLE | `mongomock` con insert/find, upsert y agregación |
| GTE-09 | CI dispara en la rama correcta | **NO CUMPLE** | `branches: [main]` vs `master` |
| GTE-10 | CI reproduce entorno | CUMPLE CON SALVEDAD | Instala `requirements.txt` + pytest + mongomock; sin lock |
| GTE-11 | Umbral con fuente única | **NO CUMPLE** | Duplicado en gate, tests, spec y docs |
| GTE-12 | PENDA-01 no se declara PASS | CUMPLE | «pendiente hoy» en la salida |

---

## 6. Rúbrica (19 v2 + 7 Tema 8)

| # | Criterio | Veredicto |
|---:|---|---|
| 1 | BDA · Extracción API + scraping | CUMPLE |
| 2 | BDA · HDFS originales + recuperación | CUMPLE CON SALVEDAD (vivo N/V) |
| 3 | BDA · Kafka productor + consumidor | CUMPLE CON SALVEDAD (vivo N/V) |
| 4 | BDA · Integración hasta MongoDB | CUMPLE CON SALVEDAD (vivo N/V) |
| 5 | SBD · Integración de fuentes | CUMPLE |
| 6 | SBD · Construcción del conjunto | CUMPLE |
| 7 | SBD · Limpieza ≥4 operaciones | CUMPLE |
| 8 | SBD · Automatización | CUMPLE CON SALVEDAD (`--check` en rojo) |
| 9 | SBD · Modelado + embedding/referencing | CUMPLE |
| 10 | SBD · CRUD + comprobación | CUMPLE |
| 11 | SBD · Consultas ≥5 | CUMPLE |
| 12 | SBD · Aggregation ≥3 / 5 etapas | CUMPLE (11 pipelines) |
| 13 | SBD · Índices + `explain()` | CUMPLE |
| 14 | SBD · Consistencia atómica | CUMPLE |
| 15 | SBD · Datos heterogéneos | CUMPLE |
| 16 | SBD · Automatización del análisis | CUMPLE |
| 17 | SBD · ≥5 indicadores de 2+ fuentes | CUMPLE |
| 18 | SBD · ≥3 municipios comparados | CUMPLE (4) |
| 19 | SBD · ≥3 conjuntos para visualizar | CUMPLE (8 CSV + 36 PNG) |
| 20 | Tema 8 · Modelado 15 % | CUMPLE |
| 21 | Tema 8 · CRUD/limpieza/consultas 15 % | CUMPLE |
| 22 | Tema 8 · Aggregation 20 % | CUMPLE |
| 23 | Tema 8 · Índices 15 % | CUMPLE |
| 24 | Tema 8 · Transacciones 10 % | CUMPLE |
| 25 | Tema 8 · PyMongo profesional 15 % | CUMPLE |
| 26 | Tema 8 · Defensa 10 % | CUMPLE CON SALVEDAD (P1-01) |

**Conversión:** 15/19 criterios v2 cumplen el umbral 10; 4 quedan en 7 o `PENDIENTE` por acceso vivo, staleness o documentación. No se emite nota numérica: la rúbrica exige evidencia viva para los criterios de infraestructura.

---

## 7. Requisitos y trazabilidad

- **50 cabeceras** `### Requirement:`; **46 IDs numéricos únicos**; **4 `chart_*` sin ID**.
- **118 escenarios** y **130 ocurrencias de SHALL** en las 5 specs.
- Cruce textual por ID: **32** con mención en código y test; **3** solo en código; **15** sin mención en código ni test (son requisitos documentales/contractuales: `ENTREGABLES-01`, `ARQUITECTURA-01`, `DOCS-01`, `VALIDACION-01`…).
- **Limitación:** la ausencia de un ID en el código no prueba que el requisito no se implemente; prueba que **no es rastreable por ID**. La matriz completa está en `matriz_requisitos_2026-11-08.csv`.

---

## 8. Datos y artefactos

| Comprobación | Resultado |
|---|---|
| `dim_municipios.csv` | 252 filas, 252 `codigo_ine` únicos, 252 de 5 dígitos, 0 duplicados |
| `anuncios_unificados.csv` | 594 filas, 64 municipios, 530 repeticiones de `codigo_ine` (esperado: varios anuncios/municipio) |
| Capas de alquiler | 159 oficial + 93 IDW + 252 contexto (filas de CSV) |
| `anuncios` en Mongo | 594; portales 428 Fotocasa / 87 Pisos / 79 RealtyAPI; modalidad 326 larga / 268 temporal |
| Integridad | 594/594 `ubicacion.codigo_ine` de 5 dígitos; 594/594 `ubicacion.coordenadas` GeoJSON Point |
| Duplicados | 0 por `(portal, id_anuncio)`; 0 por `property_fingerprint` |
| Índices | 24 en 16 colecciones vivas (16 `_id` + 8 de negocio) |
| `explain()` | natural: COLLSCAN, 594 docs; con índice: IXSCAN |
| Frescura | mtime máximo de `data/resultados` > mtime máximo de `data/procesado/*.csv` (no stale) |
| Tier A/B/C/D | **no re-contado en esta pasada**; el CSV `mongo_tier_confianza.csv` existe con 252 filas |

---

## 9. Limitaciones de esta auditoría

1. **Sin acceso vivo a HDFS/Kafka** (`10.22.87.215:50070` y `:9092`): INF y los criterios 2–4 quedan `N/V`; se auditó código, configuración y evidencia congelada.
2. **Sin reproducción desde cero** de `extract` + `transform`: escribiría en `data/`; se verificaron estado final y manifiestos.
3. **Sin tests destructivos**: 2 skips (artefactos no versionados y `MONGO_ALLOW_DESTRUCTIVE!=1`).
4. **13 ficheros >25 MB** sin SHA-256 (solo tamaño/mtime).
5. **Mongo en un único instante**: no hay snapshot antes/después; los tests no cambiaron 594/252.
6. **Tier A/B/C/D no re-contado** en esta pasada.
7. **Documentación archivada** se auditó como documentación, no como código vigente.

---

## 10. Backlog priorizado

**Antes de la defensa (P1, ~2 h):**
1. Actualizar README/AGENT/arquitectura/guion a 16 vivas (o 14 + 2 documentadas), 11 pipelines, 45 scripts/34 DAG, 28+8 PNG, 8 CSV Mongo, 242 tests, 594 anuncios.
2. Corregir la spec `mongodb-y-analisis` (13 PNG/6 CSV, 759 anuncios, 424 Point).
3. Rerun `normalizar_json_crudos.py` o documentar la staleness y dejar `--check` en verde.
4. Resolver check 07: corregir los 3 ceros o convertirlo en `CUMPLE CON SALVEDAD` con waiver escrito.

**Después (P2):** gobernanza 46/45/11; dueño o archivo de las 2 colecciones de habitaciones; CI en `master`; IDs de los 4 `chart_*`; commit del gate/CI; versionar o documentar resultados; corregir rutas del framework; validar colecciones vivas en el gate.

**Higiene (P3):** enlaces archivados, 5 CSV raw, `except Exception`/prints, asserts débiles, `[TEMPLATE]`.

---

## 11. Reproducibilidad

```bash
# Baseline
git rev-parse HEAD && git status --porcelain
git diff | sha256sum && git ls-files -s | sha256sum

# Gates
.venv/Scripts/python.exe -m pytest tests -o addopts="" -q -rs -p no:cacheprovider
.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline
.venv/Scripts/python.exe scripts/verificar_fase_datos.py
.venv/Scripts/python.exe scripts/verificar_gobernanza.py
.venv/Scripts/python.exe transform/run_all.py --check
.venv/Scripts/python.exe extract/generar_manifest.py --verify

# Mongo (solo lectura)
.venv/Scripts/python.exe -c "from pymongo import MongoClient; db=MongoClient('mongodb://localhost:27017')['vivienda_euskadi']; print(len(db.list_collection_names())); [print(n, db[n].count_documents({})) for n in sorted(db.list_collection_names())]"
```

---

## Anexo A — Evidencia generada

| Fichero | Contenido |
|---|---|
| `evidencia/2026-11-08/inventario_archivos.csv` | 1416 ficheros con hash, tamaño, líneas, git, sintaxis y patrones |
| `evidencia/2026-11-08/resumen_estatico.json` | Totales del barrido estático |
| `evidencia/2026-11-08/pytest_exacto.txt` | 240 passed, 2 skipped, motivos de skip |
| `evidencia/2026-11-08/gate_offline.txt` | Gate offline OK + PENDA-01 |
| `evidencia/2026-11-08/gate_vivo_sin_env.txt` | Exit 2 de la guarda viva |
| `evidencia/2026-11-08/manifest_verify.txt` | 354 raw / 188 silver, 0 errores |
| `evidencia/2026-11-08/run_all_check.txt` | Staleness de `normalizar_json_crudos.py` |
| `evidencia/2026-11-08/verificar_fase_datos.txt` | FAIL 07 paro-cero + PENDIENTE |
| `evidencia/2026-11-08/gobernanza.txt` | 3 cifras canónicas desfasadas |
| `evidencia/2026-11-08/mongo_audit.json` | 30 colecciones, índices, integridad, explain |
| `evidencia/2026-11-08/datos_audit.json` | dim, unificados, 17 CSV, 28 PNG |
| `evidencia/2026-11-08/matriz_requisitos_2026-11-08.csv` | 50 cabeceras con impl/test/doc |
| `openspec/audit/hallazgos_v6_2026-11-08.csv` | 19 hallazgos con severidad y acción |

---

*Relaciones: `openspec/specs/contrato-reto/spec.md` (verdad), `archive/framework_auditoria_completo2/` (método), `openspec/audit/informe_auditoria_v5_2026-11-07.md` (baseline previo), `openspec/audit/plan_auditoria_v6_2026-11-08.md` (plan aplicado), `AGENT.md` (convenciones).*
