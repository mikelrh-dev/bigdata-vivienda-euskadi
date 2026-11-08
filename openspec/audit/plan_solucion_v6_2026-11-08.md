# Plan de solución v6 — cierre de hallazgos de la auditoría

**Fecha:** 2026-11-08 · **Base:** auditoría v6 (`informe_auditoria_v6_2026-11-08.md`, 4 P1 / 9 P2 / 6 P3)
**Estado:** PLAN. No se ha aplicado ningún cambio. Ejecutar por fases, con autorización para las que escriben en `data/`.
**Objetivo:** dejar el proyecto en **GO** con cifras únicas, gates verdes y sin contradicciones en la defensa, sin maquillar datos para que cuadren con la documentación.

---

## 0. Principios

1. **La verdad es lo medido, no lo documentado.** Se corrigen los documentos para que digan 594/16/11/45/242/28+8; nunca se revierte el dato a 759/14/10/44/178/12.
2. **Una sola fuente de cifras.** `data/resultados/README.md` + una tabla canónica nueva; README, AGENT, guion y spec enlazan a ella.
3. **Gate verde o waiver escrito, nunca silencio.** Un FAIL conocido no se convierte en PASS cambiando el umbral; se arregla el dato o se declara `CUMPLE CON SALVEDAD` con fuente.
4. **Cada fase, un commit revisable.** Nada de un commit gigante con gate + docs + datos.
5. **Nada de reescribir historia ni borrar backups** sin autorización expresa.

---

## 1. Decisiones que hay que tomar antes de empezar

| # | Decisión | Recomendación | Alternativa |
|---|---|---|---|
| D1 | ¿Cuántas colecciones son "canónicas"? | **14 de negocio + 2 de habitaciones + 14 backups = 30**; decir siempre las tres cifras | Declarar 16 vivas y documentar las 2 de habitaciones como extensión |
| D2 | ¿Qué hacer con el paro-cero (check 07)? | **Recalcular** `tasa_paro_lanbide_pct` desde paro/activos; si activos=0 → `NULL` + `metodo_imputacion=ninguno`. Es un dato inconsistente (paro 0 con tasa 0,28) | Si Lanbide publica 0,28 con paro 0, documentarlo con captura y convertir 07 en `CUMPLE CON SALVEDAD` |
| D3 | ¿Se versionan los resultados? | **Sí los CSV** (texto, 17 ficheros); **no los PNG** (binarios, se regeneran) + manifiesto SHA de PNG | Dejar todo local y mantener el skip documentado |

> D2 es la única que puede cambiar cifras: afecta a Aramaio, Gaintza y Usansolo (ninguno está en el top-4). Si se recalcula, revisar si esos valores aparecen en CSV/figuras.

---

## 2. Fase 0 — Preparación (30 min)

| Paso | Acción | Comando / criterio |
|---|---|---|
| F0.1 | Rama de trabajo | `git switch -c fix/auditoria-v6` (no trabajar en `master`) |
| F0.2 | Pinear baseline | `git rev-parse HEAD; git diff \| sha256sum; git ls-files -s \| sha256sum` |
| F0.3 | Inventario de cifras obsoletas | `grep -rnE "10 pipelines\|759\|13 PNG\|12 PNG\|178 tests\|177 passed\|14 colecciones\|44 scripts\|6 CSV" --include=*.md --include=*.py . \| grep -v archive` → guardar en `openspec/audit/evidencia/2026-11-08/grep_cifras.txt` |
| F0.4 | Congelar trabajo actual | Commits por unidad (ver F4.4) **antes** de mezclar arreglos |

**Salida:** rama, baseline y lista cerrada de sustituciones.

---

## 3. Fase 1 — Gates verdes (2–3 h) · P1-03 y P1-04

### S3. Staleness de `normalizar_json_crudos.py` (P1-03)

**Causa:** `transform/normalizar_json_crudos.py` recorre **todos** los `data/raw/*.json` y escribe `*_normalizado.json`; dos Lanbide tienen mtime posterior a su salida, así que `run_all.py --check` marca `normalizar_json_crudos.py` como `DESACTUALIZADO`.

**Riesgo de cascada (importante):** el script reescribe **todos** los `*_normalizado.json`. `run_all.py::_estado` (`transform/run_all.py:325-350`) compara `mtime(entrada) > min(mtime(salida))`, así que al tocarlos todos sus consumidores pasan a `DESACTUALIZADO`. **El `--check` no queda en 0 solo con este rerun.**

**Procedimiento seguro (escribe en `data/procesado`, regenerable):**

```bash
# 0) copia y huellas
cp -a data/procesado /tmp/procesado_backup
find data/procesado -name '*_normalizado.json' -print0 | sort -z | xargs -0 sha256sum > /tmp/norm_antes.txt
# 1) rerun
.venv/Scripts/python.exe transform/normalizar_json_crudos.py
# 2) restaurar mtime de los ficheros con contenido idéntico
.venv/Scripts/python.exe - <<'PY'
import hashlib, os
from pathlib import Path
bak = Path('/tmp/procesado_backup')
for p in Path('data/procesado').glob('*_normalizado.json'):
    b = bak / p.name
    if b.exists() and hashlib.sha256(p.read_bytes()).digest() == hashlib.sha256(b.read_bytes()).digest():
        os.utime(p, (b.stat().st_atime, b.stat().st_mtime))
PY
# 3) contenido cambiado
diff /tmp/norm_antes.txt /tmp/norm_despues.txt | head -20
# 4) ver consumidores stale y ejecutar SOLO esa cadena
.venv/Scripts/python.exe transform/run_all.py --check
```

**Aceptación:** `run_all.py --check` `EXIT=0` **tras ejecutar la cadena afectada**, y el diff de contenido solo contiene los 2 JSON de Lanbide. **Si el rerun cambia más de 2 ficheros, o la cadena afectada supera ~5 scripts, parar**: valorar `--check` por hash de contenido o dejar el gate en `CUMPLE CON SALVEDAD` con el detalle, en lugar de reejecutar todo el DAG antes de la defensa.

**Mejora opcional (P3):** añadir `--solo <nombre>` al script para futuros reruns dirigidos.

### S4. Check 07 paro-cero (P1-04)

**Causa:** `scripts/verificar_fase_datos.py:67-90` **fuerza FAIL** cuando hay `paro_registrado_cero=True` con tasa no nula distinta de los 3 casos documentados; con los 3 conocidos también falla a propósito. Es una política, no un bug: el gate nunca podrá estar en verde.

**Procedimiento:**

1. Localizar el productor de la tasa:
   ```bash
   grep -rn "paro_registrado_cero\|tasa_paro_lanbide_pct" transform/*.py
   ```
2. Recalcular la tasa desde los conteos que ya existen (`paro_registrado / activos * 100`). Si `activos` es 0 o nulo → `NULL`.
3. Mantener `paro_registrado_cero=True` y añadir/actualizar `metodo_imputacion="ninguno"`. **No imputar comarcal.**
4. Regenerar el silver afectado y el CSV `udalmap_paro.csv` si cambia.
5. Verificar:
   ```bash
   .venv/Scripts/python.exe scripts/verificar_fase_datos.py; echo "EXIT=$?"
   ```
   **Aceptación:** `RESULTADO: OK 18/18` y `EXIT=0`.

**Si se demuestra que 0,28/1,45/3,26 son los valores oficiales de Lanbide:** no tocar el dato; adjuntar fuente y cambiar el check a `CUMPLE CON SALVEDAD` (una línea `WAIVER` en el script, sin convertir el FAIL en PASS genérico). Esta vía requiere aprobación porque relaja un gate.

---

## 4. Fase 2 — Gobernanza y contrato (1–2 h) · P2-01, P2-02, P2-04 y P2-08

### S5. IDs de los 4 `chart_*` y guardián

**Causa:** `verificar_gobernanza.py` cuenta solo IDs con `-NN`; los 4 `chart_*` no tienen sufijo numérico (46 de 50 cabeceras). Además espera 45 requisitos, 44 scripts y 10 pipelines.

**Procedimiento:**

1. Añadir ID a cada cabecera sin renombrar el requisito:
   - `### Requirement: chart_tierB_range` → `### Requirement: CHART-TIERB-01 — chart_tierB_range ...`
   - `CHART-MAPA-01`, `CHART-EFFORT-01`, `CHART-HABIT-01` (mismo patrón).
2. Actualizar `scripts/verificar_gobernanza.py`:
   - `len(ids) == 50 and len(set(ids)) == 50`
   - `len(transform) == 45 and dag == 34`
   - `pipelines == 11`
3. Verificar:
   ```bash
   .venv/Scripts/python.exe scripts/verificar_gobernanza.py; echo "EXIT=$?"
   ```
   **Aceptación:** `TODO OK`, `EXIT=0`.

> Si se prefiere no tocar la spec, la alternativa es que el guardián cuente **50 cabeceras** (46 numéricas + 4 nombradas) y valide unicidad por texto. Es menos trazable; no recomendada.

### S6. Contrato Mongo: 14 + 2 (P2-02, P2-08)

**Causa:** `load_mongo.py` define 14 loaders; `anuncios_habitaciones_unificados` y `..._bigdata` (201 docs cada una) se leen en agregaciones pero no tienen dueño de carga.

**Procedimiento:**

1. Comparar `_id` de ambas colecciones (solo lectura):
   ```python
   a = set(db.anuncios_habitaciones_unificados.distinct("_id"))
   b = set(db.anuncios_habitaciones_unificados_bigdata.distinct("_id"))
   print(len(a), len(b), len(a ^ b))
   ```
2. Si son idénticas: con autorización, renombrar la legacy a `anuncios_habitaciones_unificados_bigdata__backup_20261108` (no borrar) y dejar una sola viva.
3. Documentar el productor real (`transform/generar_vistas_mercado.py` + carga) en `docs/modelo_mongodb.md`; si procede, añadir `load_habitaciones()` a `storage/load_mongo.py`.
4. Actualizar el gate offline a **16 nombres** (14 + 2) y el `--vivo` a comparar `list_collection_names()` real.

**Aceptación:** 16 vivas (o 15 si se archiva la legacy), 14 backups + 1 backup nuevo, y `gate --offline` en verde con la lista correcta.

---

## 5. Fase 3 — Documentación y spec (2–3 h) · P1-01, P1-02, P2-09

### S1. Tabla canónica (crear una vez)

Añadir a `data/resultados/README.md` (o `docs/inventario_numerico.md` enlazado desde README):

| Métrica | Valor canónico |
|---|---:|
| Municipios | 252 |
| Anuncios | 594 (326 larga + 268 temporal) |
| Colecciones | 14 negocio + 2 habitaciones + 14 backups |
| Pipelines | 11 |
| `transform/*.py` / DAG | 45 / 34 |
| Raw / manifest / HDFS | 356 / 354 / 352 |
| Silver / manifest | 191 / 188 |
| Tests | 242 colectados · 240 passed · 2 skipped |
| CSV en `data/resultados` | 17 (8 `mongo_*`) |
| PNG | 28 principales + 8 anexo |
| Requisitos | 50 cabeceras / 50 IDs |
| Changes | 6 vivos + 32 archivados |

> Los 17 CSV incluyen 2 que no están en la tabla actual de `data/resultados/README.md`: `auditoria_lagunas_silver.csv` y `mongo_habitaciones_por_municipio.csv`. Añadirlos antes de publicar la tabla.

### S2. Sustituciones exactas

| Fichero | Ahora | Debe decir |
|---|---|---|
| `README.md:102` | 14 colecciones | 14 de negocio + 2 de habitaciones |
| `README.md:103,122,260,304` | 10 pipelines | 11 pipelines |
| `README.md:120` | 44 scripts; 34 en el DAG | 45 scripts; 34 en el DAG |
| `README.md:110,148,259` | 177 passed, 1 skipped (178) | 240 passed, 2 skipped (242) |
| `README.md:165` | 6 CSV canónicos | 8 CSV desde Mongo (17 en total) |
| `README.md:166` | 12 PNG únicos (13 emitidos) | 28 PNG principales + 8 de anexo |
| `AGENT.md:4` | 10 pipelines | 11 pipelines |
| `AGENT.md:9` | 178 tests (177 passed, 1 skipped) | 242 tests (240 passed, 2 skipped) |
| `docs/arquitectura_datos.md:58` | 18/18, 151 passed | 18/18, 242 tests (solo tras S4) |
| `docs/arquitectura_datos.md:60` | 759, 83 mun | 594, 64 mun (y 83/252 como cobertura histórica, si se mantiene) |
| `docs/arquitectura_datos.md:61,69` | 14 colecciones, 10 pipelines | 14 + 2, 11 pipelines |
| `docs/guion_defensa.md:19,32` | 10 pipelines, 6 CSV, 12 PNG | 11, 8, 28+8 |
| `docs/guion_defensa_12min.md:35,143,170,171,249` | 10/14/6/12/177 | 11/16/8/28+8/240+2 |
| `openspec/specs/mongodb-y-analisis/spec.md:188,439` | 13 PNG + 6 CSV | 28 PNG + 8 CSV |
| `openspec/specs/mongodb-y-analisis/spec.md:395` | 759 anuncios, 424 Point | 594 anuncios, 594 Point |
| `openspec/specs/mongodb-y-analisis/spec.md:401` | 16 colecciones | 30 (16 vivas + 14 backups) |

**Aceptación:**

```bash
grep -rnE "10 pipelines|759|13 PNG|12 PNG|178 tests|177 passed|14 colecciones|44 scripts|6 CSV" --include=*.md . | grep -v archive | grep -v openspec/audit
# sin resultados (o solo citas históricas explícitas con "pre-change")
```

Y `README.md` enlaza a la tabla canónica en vez de repetir cifras.

### S9. Fuente única

`data/resultados/README.md` pasa a ser el índice oficial; README general solo resume y enlaza. Actualizar la tabla de 15→17 CSV y añadir el bloque de PNG (28+8).

---

## 6. Fase 4 — Repo, CI y resultados (2–3 h) · P2-03, P2-05, P2-06

### S7. CI en la rama correcta

```yaml
on:
  push:
    branches: [master, main]
  pull_request:
  workflow_dispatch:
```

**Aceptación:** el workflow aparece en el primer push a `master`; el job offline sigue en verde **en un clon limpio** (sin `data/` local). Probar antes con `git clone . /tmp/clean && cd /tmp/clean && pytest -o addopts="" -q`. No añadir `gobernanza`/`fase_datos` al CI: leen `data/` no versionado y fallarían por diseño; quedan como gates locales documentados.

### S8. Commits por unidad

| Commit | Contenido |
|---|---|
| 1 | `scripts/gate_extremo_a_extremo.py`, `.github/`, 10 tests nuevos, `pyproject.toml`, `Makefile`, `uv.lock` |
| 2 | `analysis/run_analisis_mongo.py` (11 pipelines, 8 CSV, 28+8 PNG), `transform/generar_figuras_N.py` |
| 3 | `transform/run_all.py` (+1) y `tests/test_pisos_ubicacion_real.py` |
| 4 | Docs + spec (S1/S2/S9) |
| 5 | `openspec/audit/` (informe, plan, CSV, evidencia) |

Antes de cada uno: `git diff --check` y `pytest` del área tocada.

### S9bis. Resultados versionados

- Añadir `data/resultados/*.csv` (17, texto) al índice; mantener PNG ignorados.
- Generar `data/resultados/manifest_sha256.txt` con los PNG.
- **Ajustar antes `tests/test_pisos_ubicacion_real.py`:** hoy termina con `assert pngs and csvs`; en CI no hay PNG (ignorados), así que con solo CSV trackeados **el test falla**. Cambiarlo a «tracked ⊆ local, sin exigir PNG» o versionar un manifiesto SHA de PNG sin los binarios.
- Actualizar `.gitignore` (`!data/resultados/*.csv`) y hacer dry-run en clon limpio.

**Aceptación:** `git ls-files data/resultados` muestra 17 CSV; el test ya no aparece como skip y pasa en clon limpio **sin PNG**; los PNG siguen fuera de git.

### S10. Framework de auditoría (P2-07)

- `archive/framework_auditoria_completo2/diagnostico.py`: `ROOT = Path(__file__).resolve().parents[2]`.
- Runbook: `scripts/verificar_fase_datos.py` (no raíz).
- Smoke test manual; no se usa para puntuar.

---

## 7. Fase 5 — Higiene P3 (2 h, opcional antes de defensa)

| ID | Acción | Aceptación |
|---|---|---|
| P3-01 | Corregir o marcar los 9 enlaces de `archive/windows_vm_2026-11-06/docs_vm` | 0 enlaces rotos fuera de archivo |
| P3-02 | Lectura tolerante `utf-8-sig`→`latin-1` en los 5 CSV raw; documentar cabecera vacía ECVI | Los 5 se leen sin excepción |
| P3-03 | Acotar `except Exception` en carga/índices/escritura; `logging` en código nuevo | Sin `except Exception` en rutas críticas |
| P3-04 | Sustituir 20 asserts débiles por asserts de dominio | `grep "assert True"` = 0 |
| P3-05 | Comentar `[TEMPLATE]` en `.env.example` | `python-dotenv` lo ignora o no está |
| P3-06 | Documentar el productor de habitaciones o integrarlo en `load_mongo.py` | Dueño único escrito |

---

## 8. Orden recomendado y dependencias

```
F0 baseline
 └─► S3 staleness ──► S4 paro-cero ──► S5 gobernanza ──► S1/S2 docs ──► S7 CI
                                     │                         │
                                     └─► S6 Mongo ◄────────────┘
                                                                 └─► S8 commits ──► S9bis resultados
                                                                                      └─► P3
```

**Por qué este orden:** S4 cambia el estado del gate (18/18), así que la documentación se actualiza **después** para no volver a mentir. S5 fija las cifras canónicas que S2 usará. S6 y S7 no bloquean la defensa, pero sí el «GO» completo.

**Esfuerzo total:** F0 0,5 h · F1 2–3 h · F2 1–2 h · F3 2–3 h · F4 2–3 h · P3 2 h ≈ **10–13 h** (1,5 jornadas).

---

## 9. Verificación final (una sola pasada)

```bash
set -e
.venv/Scripts/python.exe -m pytest tests -o addopts="" -q -rs
.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline
.venv/Scripts/python.exe transform/run_all.py --check
.venv/Scripts/python.exe scripts/verificar_fase_datos.py
.venv/Scripts/python.exe scripts/verificar_gobernanza.py
.venv/Scripts/python.exe extract/generar_manifest.py --verify
grep -rnE "10 pipelines|759|13 PNG|12 PNG|178 tests|177 passed|14 colecciones|44 scripts|6 CSV" --include=*.md . | grep -v archive | grep -v openspec/audit
git diff --check
```

**GO si:** pytest verde, gate offline OK, `--check` 0, fase datos `OK 18/18`, gobernanza `TODO OK`, manifest 0 errores, grep de cifras vacío y `git diff --check` limpio.

---

## 10. Riesgos y rollback

| Riesgo | Mitigación |
|---|---|
| El rerun de `normalizar_json_crudos.py` toca más de 2 ficheros | Hashes antes/después; si el diff es amplio, parar y comparar contenido |
| Recalcular el paro cambia cifras en CSV/figuras | Revisar los 3 municipios; no están en top-4; regenerar y anotar el cambio |
| Archivar la colección legacy de habitaciones | Renombrar a `__backup_<fecha>`, nunca `drop`; comparar `_id` antes |
| Commitear resultados y generar ruido en cada rerun | Versionar solo CSV; PNG + manifiesto SHA aparte |
| Tocar la spec durante la defensa | S2 se hace y se commitea antes del ensayo; congelar después |
| Un gate sigue rojo | No publicar «GO»; declarar `PENDIENTE` con el FAIL exacto (como hoy) |

**Rollback:** cada fase es un commit; revertir con `git revert <sha>`. Los datos se regeneran desde `data/raw` y los hashes de `/tmp/norm_*.txt`; no se usa `git reset --hard`.

---

## 11. Fuera de alcance

- Auditar HDFS/Kafka en vivo (sigue `N/V` hasta acceso al centro).
- Cambiar los 594 a 759 o cualquier cifra para que cuadre con documentos viejos.
- Relajar umbrales del gate sin waiver escrito.
- Borrar backups o reescribir historia de git.

---

*Relacionado: `informe_auditoria_v6_2026-11-08.md`, `hallazgos_v6_2026-11-08.csv`, `analisis_beneficio_riesgo_v6_2026-11-08.md`, `evidencia/2026-11-08/`, `plan_auditoria_v6_2026-11-08.md`.*
