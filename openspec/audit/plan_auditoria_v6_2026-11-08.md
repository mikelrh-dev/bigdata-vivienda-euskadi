# Plan de auditoría v6 — auditoría integral con el framework existente

**Fecha:** 2026-11-08
**Estado:** PLAN. No se ejecuta en esta sesión. No se modifica `data/`, `extract/`, `transform/`, `storage/`, `analysis/`, `tests/`, MongoDB, HDFS ni Kafka.
**Sustituye a:** `plan_auditoria_v5_2026-11-07.md` como plan vigente. v5 y su informe quedan como baseline ejecutado (9 de 14 barridos completos) y como catálogo de IDs; nunca como evidencia vigente.
**Objetivo:** auditar todo el proyecto —contrato, datos, código, infraestructura, tests, documentación y entrega— reutilizando el método del framework existente y re-ejecutando la evidencia, no heredando veredictos.

---

## 0. Qué cambia respecto a v5

1. **Se adopta el framework ya existente**, no se inventa otro: `archive/framework_auditoria_completo2/` (8 `.md` + `diagnostico.py`), con su rúbrica 0/3/7/10, su escala P1/P2/P3 y su semáforo GO/GO con deuda/NO-GO.
2. **El framework cubre solo la fase de datos** (obtención + transformación; Mongo/HDFS/Kafka solo como *readiness*). El proyecto ya tiene esas piezas implementadas, así que el método del framework se aplica a los 18 dominios usando el catálogo de IDs de v5 para lo que el framework no alcanza.
3. **Se añade un bloque delta** por el cambio `gate-extremo-a-extremo-offline` (gate offline, CI, 10 ficheros de test nuevos, `pyproject.toml`, `Makefile`, `uv.lock`), que v5 no pudo auditar porque no existía.
4. **Se corrigen dos defectos del framework** que lo invalidan tal cual está archivado (§1.2) y una cifra del plan v5 (F-07: 19 criterios v2 + 7 Tema 8, no 26 v2).
5. **Se re-mide el baseline hoy**: 242 tests colectados (v5: 178), 32 ficheros de test (v5: 22), 58 ficheros en `data/resultados` (v5: 33) y 28 PNG (v5: 12). Ese crecimiento es, por sí mismo, materia de auditoría (H12–H17).

---

## 1. Framework adoptado

### 1.1 Artefactos y uso

| Artefacto | Qué aporta | Uso en v6 |
|---|---|---|
| `archive/framework_auditoria_completo2/README.md` | Semáforo 🟢/🟡/🔴 y reglas de oro | Veredicto final por fase |
| `01_alcance_y_reglas.md` | Raw inmutable, alcance, mapa de carpetas | `PRE`, `EXT`, `TRF`, `SEC` |
| `02_rubrica_auditable.md` | Rúbrica 0/3/7/10 con umbral literal | `CTR`, `DEF` y matriz final |
| `03_extraccion.md` | Checks API + scraping, manifests, secretos | `EXT-01…12` |
| `04_transformacion.md` | DAG, `codigo_ine`, `dtype`, limpieza honesta | `TRF-01…12` |
| `05_suficiencia_dato.md` | Gate GO/NO-GO con error <20 %, n≥30, sesgos | `DAT-01…14` y veredicto de suficiencia |
| `06_readiness_mongo_infra.md` | Contrato silver → Mongo/HDFS/Kafka | Regresión de `MON` e `INF` (ya implementados) |
| `07_runbook_agente.md` | Formato de informe + prohibiciones | Estructura del informe v6 |
| `diagnostico.py` | Chequeo rápido ejecutable | `PRE-07` tras corregir la ruta (ver 1.2) |

**Catálogo operativo:** `plan_auditoria_v5_2026-11-07.md` + `plan_auditoria_v5_barridos_2026-11-07.md`. Sus IDs (`PRE`, `CTR`, `REQ`, `EXT`, `TRF`, `MON`, `IDX`, `AGG`, `REP`, `DAT`, `TST`, `INF`, `VIS`, `DOC`, `SEC`, `COD`, `GIT`, `DEF` y los 14 barridos) se conservan para poder comparar v3 → v4 → v5 → v6 sin renumerar.

### 1.2 Desviaciones del framework que la auditoría debe resolver antes de usarlo

| # | Defecto | Evidencia medida hoy | Efecto | Tratamiento en v6 |
|---|---|---|---|---|
| D1 | `diagnostico.py` calcula `ROOT = Path(__file__).resolve().parent.parent`; al vivir en `archive/framework_auditoria_completo2/`, apunta a `archive/`, no a la raíz | Ejecutado: reporta «falta `docs/raw_manifest_sha256.txt`», «falta `data/raw/.FROZEN`», «falta `data/procesado/`» (los tres existen) | Falso NO-GO en fase datos | `PRE-00`: ejecutar una copia corregida en `scratchpad/audit_v6/` (`parents[2]`), sin tocar el original archivado |
| D2 | `07_runbook_agente.md` invoca `verificar_fase_datos.py` en la raíz | El fichero real es `scripts/verificar_fase_datos.py` | Comando del runbook falla | `PRE-00`: usar la ruta real y anotar la desviación |
| D3 | El framework referencia `archivosReto/RETO 1Evaluacion SBD-BDA.pdf` | El PDF/DOCX vigentes están en `brief/` (`RETO 1Evaluacion SBD-BDAv2.pdf`, `Tema_8_...docx`) | Fuente de verdad mal citada | `CTR-00`: fijar `brief/` como fuente y verificar que la versión v2 es la que manda |
| D4 | El alcance del framework excluye Mongo/HDFS/Kafka como implementación | El proyecto ya los tiene (14 colecciones, 10 pipelines, gate vivo opt-in) | Auditaría de menos | Aplicar `06` como regresión y el catálogo v5 para implementación |

**Regla:** ninguna de estas desviaciones se «arregla» dentro de la auditoría; se documentan en `hallazgos_v6` y, si el usuario autoriza, van al backlog como cambio aparte.

---

## 2. Baseline medido (preflight de esta planificación, 2026-11-08)

| Hecho medido | Valor | Comando / fuente |
|---|---:|---|
| Commit HEAD | `3171d5a` | `git rev-parse --short HEAD` |
| Árbol de trabajo | **20 entradas** = 3 `M` + 17 `??` | `git status --porcelain` |
| Python | 3.12.10 | `.venv/Scripts/python.exe --version` |
| Tests colectados | **242** | `pytest tests --collect-only -q` (suma por fichero) |
| Ficheros de test | **32** | `ls tests/*.py` |
| `data/raw` | **356** ficheros | `find data/raw -type f` |
| Manifest raw | **354** entradas | `wc -l docs/raw_manifest_sha256.txt` |
| `.FROZEN` | presente (0 bytes, 2026-10-29) | `ls -la data/raw/.FROZEN` |
| `data/procesado` | **191** ficheros = 42 CSV + 78 JSON raíz + resto en `_meta` | `find` + `ls` |
| Manifest silver | 188 entradas (verificado en v5) | `data/procesado/manifest_sha256.txt` |
| `data/resultados` | **58** ficheros = 17 CSV + 28 PNG + 13 otros | `ls` |
| Scripts `extract/*.py` | **41** | `ls extract/*.py` |
| Scripts `transform/*.py` | **45** (v5: 44) | `ls transform/*.py` |
| Changes sin archivar | **6** (+32 en `changes/archive`) | `ls -d openspec/changes/*/` (sin `archive/`) |
| Gate offline | existe y `--help` responde; **no ejecutado en esta planificación** | `scripts/gate_extremo_a_extremo.py --help` |
| Framework | existe, archivado y con D1–D3 | ejecución de `diagnostico.py` |

### 2.1 Delta contra v5 y nuevas hipótesis

| # | v5 (2026-11-07) | Hoy (2026-11-08) | Delta | Hipótesis que abre |
|---|---:|---:|---:|---|
| Tests colectados | 178 | **242** | +64 | H12: docs/AGENT siguen citando 178/177 |
| Ficheros de test | 22 | **32** | +10 | H12b: 10 nuevos del gate, ¿todos offline y con asserts reales? |
| `data/resultados` | 33 | **58** | +25 | H13: ¿26 PNG reales o artefactos de `generar_figuras_N.py` sin declarar? |
| PNG | 12 | **28** | +16 | H13b: docs dicen 12 únicos / 13 emitidos |
| `transform/*.py` | 44 | **45** | +1 | H14: ¿el nuevo script entra en `run_all.py` o queda fuera del DAG? |
| Árbol git | 65 | **20** | −45 | H15: 49 cambios de v5 ya commiteados; 17 `??` son el gate |
| Changes sin archivar | 21 | **6** | −15 | H16: ¿archivo real o pérdida de trazabilidad? |
| Manifest raw / raw | 354 / 356 | 354 / 356 | 0 | Sin cambio: sigue vigente la reconciliación 2 excluidos |
| Marco de auditoría | plan v5 | framework con D1–D3 | — | H17: el framework archivado no es ejecutable tal cual |

**Regla:** estas cifras dimensionan; no son veredictos. Si un dato no se reproduce en F0, el informe corrige el baseline y anota la desincronización.

### 2.2 Hipótesis ya visibles (no hallazgos)

| # | Observación | Dónde | Qué la resolvería |
|---|---|---|---|
| H12 | 242 tests hoy vs 178 en docs, AGENT y v5 | `README.md`, `AGENT.md`, `openspec/audit/informe_auditoria_v5_...` | Contar y ejecutar; decidir cifra vigente |
| H13 | 28 PNG vs «12 únicos / 13 emitidos» | `data/resultados`, `README.md` | Inventario con mtime y origen por PNG |
| H14 | 45 transforms vs 44 documentados y 34 nodos del DAG | `transform/`, `run_all.py:SCRIPTS` | `run_all.py --check` + lista de excluidos |
| H15 | 17 `??` incluyen gate, CI, `pyproject.toml`, `Makefile`, `uv.lock` sin commitear | `git status` | Decidir si entran en el baseline o se estacionan |
| H16 | 6 changes sin archivar, uno es el gate (no archivado a propósito) | `openspec/changes/` | Leer `tasks.md` de cada uno y clasificar |
| H17 | `diagnostico.py` da 6 falsos MAL por `ROOT` | `archive/framework_auditoria_completo2/diagnostico.py:12` | Copia corregida en `scratchpad/` |
| H18 | CI dispara en `push: branches [main]`, pero la rama es `master` | `.github/workflows/quality-gate.yml` | Confirmar rama por defecto y si el gate corre en push |
| H19 | `Makefile` usa `.venv/Scripts/python.exe` (solo Windows) | `Makefile:5` | Verificar que CI no depende del Makefile o declarar límite |

---

## 3. Alcance y dimensionamiento

| Bloque | Filas | Fuente |
|---|---:|---|
| Puntos de método v5 (18 dominios) | 168 | `plan_auditoria_v5_...md` §3 |
| Barridos v5 (14 universos) | 359 | `plan_auditoria_v5_barridos_...md` |
| **Subtotal heredado** | **527** | IDs estables, sin renumerar |
| Delta gate/CI | **12** | Bloque `GTE-01…12` (§5) |
| Filas nuevas de barrido | **28** | +10 tests, +16 PNG, +1 CSV, +1 transform (TSF/PNG/CSV/TRN) |
| **Total v6** | **567** | Cifra cerrada en F0; si el recontado difiere, se corrige aquí |

**Corrección F-07:** la rúbrica son **19 criterios v2 + 7 del Tema 8 = 26 filas**, no «26 criterios v2». La matriz de §Anexo C usa 19 + 7.

**Regla de sustitución:** las 28 filas nuevas **reemplazan** el universo del barrido correspondiente; no se suman dos veces. Un elemento nuevo sin fila propia no está auditado.

---

## 4. Reglas de la auditoría (framework + v5)

1. **Solo lectura.** Única escritura: `.md`, `.csv` y logs en `openspec/audit/` y `scratchpad/audit_v6/`. Nada de `data/`, código, Mongo (`insert/update/delete/drop`), HDFS ni Kafka.
2. **Evidencia triple.** (a) comando, (b) salida numérica o literal, (c) `fichero:línea`. Sin las tres: `NO VERIFICABLE`.
3. **La documentación no es evidencia.** Un README que dice «242 tests» no puntúa; puntúa la ejecución. La documentación se audita como documentación (`DOC`).
4. **Umbral literal.** 10 solo si se cumple la columna del 10 palabra por palabra. «Casi» = 7.
5. **No verificable ≠ 10.** Se marca `PENDIENTE` con la lista exacta de lo que falta.
6. **Falsación obligatoria.** Cada `CUMPLE` frágil anota qué observación lo convertiría en `NO CUMPLE`.
7. **Un fallo, una severidad.** P0 tumba la entrega; P1 tumba un criterio; P2 degrada; P3 es deuda.
8. **Sin arreglos.** Se detecta y documenta; las reparaciones van a `backlog_v6` con autorización aparte.
9. **Baseline pineado.** Commit + `git diff | sha256sum` + `git ls-files -s | sha256sum` al abrir y al cerrar.
10. **Prohibiciones del runbook (`07`):** no pedir pipelines/índices/transacciones como si no existieran, no regenerar raw, no tocar `data/raw/`, no puntuar 10 sin evidencia.

### 4.1 Veredicto y severidad

| Veredicto | Significado |
|---|---|
| `CUMPLE` | Evidencia triple y umbral literal |
| `CUMPLE CON SALVEDAD` | Se cumple con excepción declarada (waiver, límite de acceso) |
| `NO CUMPLE` | La evidencia contradice el umbral |
| `NO VERIFICABLE` | Falta acceso, dato o ejecución |
| `N/A` | No aplica, justificado |

| Sev. | Definición | Efecto |
|---|---|---|
| **P0** | Integridad rota, dato falso, secreto expuesto, entrega imposible | Bloquea entrega |
| **P1** | Criterio de rúbrica < 10 o requisito SHALL incumplido | Baja nota |
| **P2** | Deuda que degrada calidad o defensa | Afecta P2/P3 |
| **P3** | Higiene, duplicación, estilo | Backlog |

---

## 5. Bloque delta: gate extremo a extremo y CI (`GTE-01…12`)

| ID | Punto a auditar | Cómo se verifica | Evidencia exigida | Si falla |
|---|---|---|---|---|
| GTE-01 | Gate offline pasa y no toca red | `python scripts/gate_extremo_a_extremo.py --offline`; exit 0; revisar que no abre sockets | salida + exit + grep de `socket/requests` | P1 |
| GTE-02 | Umbrales literales 354/188/14/0/lag 0 | Contraste con disco: 356 raw, 191 procesado, 14 colecciones, manifiestos 354/188 | tabla umbral→valor→exclusión explicada | P1 |
| GTE-03 | `--vivo` sin `GATE_LIVE=1` aborta | Ejecutar sin la variable: exit 2 y sin conexión | salida + exit | P1 |
| GTE-04 | `--vivo` con `GATE_LIVE=1` | Solo si hay centro; si no, `NO VERIFICABLE` fechado | salida o declaración | P2 |
| GTE-05 | Gate no escribe en `data/` | Hash del árbol antes/después | dos hashes idénticos | P0 |
| GTE-06 | Los 10 tests nuevos afirman de verdad | Revisar asserts: umbrales, no `assert True` | lista test→assert→umbral | P1 |
| GTE-07 | E2E offline hermético | `test_extremo_a_extremo` usa `tmp_path` + fakes, sin red | código + ejecución aislada | P1 |
| GTE-08 | Integración Mongo con `mongomock`/skip | El skip está justificado, no oculta cobertura | test + motivo | P2 |
| GTE-09 | CI dispara donde debe | `on.push.branches: [main]` vs rama `master` | rama por defecto + job real o N/V | P1 |
| GTE-10 | CI reproduce el entorno | CI instala `requirements.txt` + `pytest` + `mongomock`; ¿coincide con `.venv`? | diff de dependencias | P2 |
| GTE-11 | Umbral único (no duplicado) | 354/188/14 están en script, spec, README y tests | grep + tabla de duplicados | P2 |
| GTE-12 | PENDA-01 no se declara PASS offline | Leer salida del gate y el spec | línea literal | P1 |

---

## 6. Fases, gates y esfuerzo

```
F0 Preflight ──► F1 Contrato ──► F2 Requisitos
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
F3 Extracción+Transformación   F4 Mongo+Índices+Agg      F5 Tests+Gate+Código
        └──────────────────────────┼──────────────────────────┘
                                   ▼
                    F6 Datos+suficiencia+Reproducibilidad
                                   ▼
                    F7 Infra + Vis + Docs + Seguridad
                                   ▼
                    F8 Git + Defensa + Comparativa → F9 Informe+Backlog → F10 Jueces
```

| Fase | Contenido | Puntos | Est. | Gate de salida |
|---|---|---|---:|---|
| F0 | Preflight, framework corregido, baseline y digest | PRE-01…10 + PRE-00 | 1,5 h | copia de `diagnostico.py` OK + digest + accesos |
| F1 | Contrato y rúbrica (PDF v2 + DOCX Tema 8) | CTR-01…08 + CTR-00 | 1,5 h | 19 criterios v2 + 7 Tema 8 cotejados |
| F2 | Requisitos | REQ-01…07 + RQS | 2,5 h | matriz 45 cabeceras / 45 IDs |
| F3 | Extracción y transformación | EXT, TRF, SRC, EXF, TRN | 5,0 h | raw/manifest/SHA/DAG/45 scripts |
| F4 | Mongo, índices, agregaciones | MON, IDX, AGG, MCO, AGP | 5,0 h | 14 vivas + 10 pipelines |
| F5 | Tests, gate y código | TST, COD, TSF, **GTE** | 4,0 h | 242 tests + gate offline + 12 GTE |
| F6 | Datos, suficiencia, reproducibilidad | DAT, REP, CSV, PNG | 4,0 h | GO/NO-GO de `05` + doble huella |
| F7 | Infra, visual, docs, seguridad | INF, VIS, DOC, SEC | 4,5 h | waivers + contradicciones |
| F8 | Git, defensa, comparativa | GIT, DEF, RUB | 3,0 h | tabla v5→v6 + matriz 26 |
| F9 | Informe y backlog | redacción | 1,5 h | informe + backlog separados |
| F10 | Jueces independientes | 2 revisores | 1,5 h | confirmado/refutado |
| **Total** | | **567** | **~34,5 h** | |

**Dependencias:** F3 y F4 no pueden compartir ficheros ni colección; F6 depende de F3+F4; F7 no toca código; F10 no lee transcripciones ajenas.

---

## 7. Orquestación y checkpoints

| Ola | Agentes | Fases | Regla |
|---|---:|---|---|
| 1 | 3 | F0, F1, F2 | Nadie puntúa sin baseline ni contrato |
| 2 | 3 | F3, F4, F5 | Sin solape; F4 es el más largo |
| 3 | 3 | F6, F7, F8 | F6 depende de F3+F4 |
| 4 | 2 | F9, F10 | Jueces ciegos entre sí |

| Checkpoint | Cuándo | Qué se congela |
|---|---|---|
| CP0 | Tras corregir el framework | salida de `diagnostico.py` con exit 0 y rutas reales |
| CP1 | Tras F0 | commit, hashes, inventario, accesos |
| CP2 | Tras F2 | matriz de requisitos |
| CP3 | Tras F4 | conteos Mongo y pipelines |
| CP4 | Tras F5 | 242 tests + gate offline + 12 GTE |
| CP5 | Tras F8 | comparativa v5→v6 |
| CP6 | Cierre | digest idéntico + informe + backlog |

---

## 8. Entregables

| Fichero | Contenido |
|---|---|
| `openspec/audit/plan_auditoria_v6_2026-11-08.md` | Este plan |
| `openspec/audit/informe_auditoria_v6_2026-11-08.md` | Veredicto por punto, evidencia triple, falsación |
| `openspec/audit/barrido_v6_delta_2026-11-08.csv` | 28 filas nuevas + 12 GTE |
| `openspec/audit/matriz_requisitos_2026-11-08.csv` | Requisito → código → test → evidencia |
| `openspec/audit/matriz_rubrica_2026-11-08.md` | 19 v2 + 7 Tema 8, 0/3/7/10 o DIFERIDO |
| `openspec/audit/hallazgos_v6_2026-11-08.csv` | P0/P1/P2/P3 con falsación |
| `openspec/audit/backlog_v6_2026-11-08.md` | Reparaciones propuestas, fuera del informe |
| `openspec/audit/evidencia/2026-11-08/` | Logs crudos de cada comando citado |
| `scratchpad/audit_v6/diagnostico.py` | Copia corregida del framework (no versionada) |

---

## 9. Criterios de aceptación

- [ ] Las 567 verificaciones tienen veredicto con evidencia triple.
- [ ] `diagnostico.py` corregido devuelve exit 0 antes de puntuar (CP0).
- [ ] Los 242 tests se ejecutan con exit code y resumen exacto; cada skip justificado.
- [ ] `gate_extremo_a_extremo.py --offline` pasa; `--vivo` sin `GATE_LIVE=1` aborta con 2.
- [ ] Los 12 puntos `GTE` tienen veredicto; H18 (rama `main` vs `master`) resuelta.
- [ ] Los 19 criterios v2 + 7 del Tema 8 tienen nota 0/3/7/10 o `DIFERIDO`, con falsación.
- [ ] Los 45 requisitos están mapeados a implementación, test y evidencia.
- [ ] H12–H19 resueltas con número y fuente.
- [ ] Doble ejecución del análisis con huella idéntica (o diferencia explicada).
- [ ] Digest del árbol idéntico al de apertura; cero escrituras en `data/` y Mongo.
- [ ] Informe y backlog separados; ningún arreglo aplicado.
- [ ] Dos jueces independientes clasifican cada afirmación como confirmada/refutada/no verificable.

Un criterio no cumplido invalida el cierre de la auditoría, no la entrega del proyecto.

---

## 10. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Framework archivado y roto (D1) | Falso NO-GO inicial | CP0: copia corregida + salida esperada 354/188/252 |
| 17 `??` sin commitear | Baseline no reproducible | PRE-01: hash del diff; decidir si entran o se estacionan |
| Crecimiento a 58 resultados / 28 PNG | Cifras y docs desalineadas | F6: inventario con mtime y origen por artefacto |
| CI en `main` con rama `master` | Gate nunca corre en push | GTE-09 + `workflow_dispatch` como evidencia alternativa |
| Sin acceso a HDFS/Kafka | INF en `NO VERIFICABLE` | Evidencia congelada fechada; nunca para subir nota |
| Mongo cambia durante la auditoría | Conteos inconsistentes | Snapshot lógico al inicio y re-medida al cierre |
| Tests destructivos | Borrado de datos | `MONGO_ALLOW_DESTRUCTIVE` ausente; conteos 594/252 antes/después |
| Volumen (567) | Fatiga y atajos | Lotes por dominio + checkpoint por fase + logs |
| Sesgo del auditor | Nota inflada | Umbral literal + falsación + 2 jueces ciegos |

---

## 11. Fuera de alcance

- Reparar hallazgos (va a `backlog_v6` con autorización).
- Reescribir la rúbrica o suavizar umbrales.
- Subir procesados a HDFS o cambiar el waiver «HDFS solo raw».
- Re-scrapear o regenerar `data/raw`.
- Auditar proyectos Mongo ajenos (`tienda`, `certificacion*`) salvo para probar aislamiento.
- Valorar la defensa oral en vivo (solo guion escrito).

---

## 12. Preguntas abiertas (no bloquean el plan)

1. ¿Se corrige `diagnostico.py` en el original o solo en la copia de `scratchpad/` (recomendado)?
2. ¿El baseline se toma con los 17 `??` o se estacionan antes de F0?
3. ¿Se ejecuta `--vivo` si el centro responde, o se marca `NO VERIFICABLE` como en v5?
4. ¿Se autoriza una reproducción desde cero (`extract` + `transform`) en directorio temporal?
5. ¿El informe va en español (convención del repo) y con anexo de evidencia?
6. ¿Se comparan los 28 PNG nuevos contra los CSV o se declaran fuera del alcance de RA4?

---

## Anexo A — Comandos base

```bash
# CP0: framework utilizable (copia corregida, sin tocar el archivado)
mkdir -p scratchpad/audit_v6
cp archive/framework_auditoria_completo2/diagnostico.py scratchpad/audit_v6/
# editar en la copia: ROOT = Path(__file__).resolve().parents[2]
.venv/Scripts/python.exe scratchpad/audit_v6/diagnostico.py; echo "EXIT=$?"

# Baseline
git rev-parse HEAD
git status --porcelain | tee openspec/audit/evidencia/2026-11-08/git_status.txt
git diff | sha256sum
git ls-files -s | sha256sum

# Entorno
.venv/Scripts/python.exe --version
.venv/Scripts/python.exe -m pip freeze | sha256sum

# Datos
find data/raw -type f | wc -l
find data/procesado -type f | wc -l
find data/resultados -type f | wc -l
wc -l docs/raw_manifest_sha256.txt

# Tests y gates
.venv/Scripts/python.exe -m pytest tests -q; echo "EXIT=$?"
.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline; echo "EXIT=$?"
.venv/Scripts/python.exe scripts/verificar_fase_datos.py; echo "EXIT=$?"
.venv/Scripts/python.exe transform/run_all.py --check; echo "EXIT=$?"

# Mongo (solo lectura)
.venv/Scripts/python.exe -c "from pymongo import MongoClient; db=MongoClient('mongodb://localhost:27017')['vivienda_euskadi']; print(len(db.list_collection_names())); [print(n, db[n].estimated_document_count()) for n in sorted(db.list_collection_names())]"

# Integridad raw
.venv/Scripts/python.exe extract/generar_manifest.py --verify; echo "EXIT=$?"
```

> Los comandos que escriben (`run_analisis_mongo.py`, tests destructivos, reproducción desde cero) solo se ejecutan con autorización explícita y contra directorio temporal, nunca contra `data/resultados/` real.

---

## Anexo B — Plantilla de fila del informe

```markdown
| ID | Punto | Veredicto | Evidencia (comando + salida + fichero:línea) | Falsación | Sev. si falla |
|---|---|---|---|---|---|
| GTE-09 | CI dispara en push | NO CUMPLE | `on.push.branches: [main]` en `.github/workflows/quality-gate.yml:7`; rama `master` en `git branch --show-current` | Si la rama por defecto fuera `main` → CUMPLE | P1 |
```

---

## Anexo C — Matriz de rúbrica (19 v2 + 7 Tema 8)

| Bloque | Criterios | Puntos de control |
|---|---:|---|
| BDA RA1 (PDF v2) | 4 | EXT, INF, MON, REP |
| SBD RA1 (PDF v2) | 4 | EXT, MON, AGG, REP |
| SBD RA3 (PDF v2) | 6 | MON, IDX, AGG, TRF |
| SBD RA4 (PDF v2) | 5 | VIS, DAT, DEF |
| **Subtotal v2** | **19** | |
| Tema 8 (DOCX) | 7 | MON, IDX, AGG, COD, DEF |
| **Total filas** | **26** | |

**Conversión:** un criterio sube a 10 solo si todos sus puntos son `CUMPLE`; con un `CUMPLE CON SALVEDAD`, máximo 7 salvo waiver escrito; con un `NO VERIFICABLE`, `PENDIENTE`, nunca 10.

---

*Relaciones: `openspec/specs/contrato-reto/spec.md` (verdad), `openspec/specs/*/spec.md` (45 requisitos), `openspec/audit/informe_auditoria_v5_2026-11-07.md` (baseline ejecutado), `plan_auditoria_v5_2026-11-07.md` (catálogo de IDs), `archive/framework_auditoria_completo2/` (método y rúbrica), `AGENT.md` (convenciones), `openspec/changes/gate-extremo-a-extremo-offline/` (delta).*
