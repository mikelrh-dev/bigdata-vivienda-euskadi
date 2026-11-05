# Archive Report: bloque-4-conclusiones-entrega

Fecha: 2026-11-05
Modo: openspec
Cambio: `bloque-4-conclusiones-entrega`
Archivado en: `openspec/changes/archive/2026-11-05-bloque-4-conclusiones-entrega/`
Estado: **intentional-with-warnings** (override explícito del orquestador, sin ocultar)

## Override del orquestador

La tarea delegada instruye archivar a pesar de los warnings del `verify-report` y conservarlos como estado documentado:

> Mantén los warnings del verify-report en el merge (tasks sin marcar [x] y trazabilidad sin entrada Bloque 4) como estado documentado, sin ocultar.

Este archive procede bajo ese override. No se marcan tareas como completadas ni se crea la entrada de trazabilidad en esta fase. Los warnings quedan abiertos y auditables.

## Estado final (a cierre, jerarquía Final-State Authority)

- **verify-report** (2026-11-05) y **apply-progress** son snapshots intermedios (rango bajo). No se presentan como hechos finales.
- **Hechos finales aportados por el orquestador** en el lanzamiento (rango superior a snapshots): 130 passed, manifest 353/184, CSV 253/253/3 con huella `f1e78870`, comparativa 5 líneas con paro no nulo, `fillna` vacío, `metodo_imputacion` presente. Se recogen como estado final técnico.
- **Warnings de proceso** (verificados de nuevo tras el move, ver §Verificación): `tasks.md` 0 `[x]` / 11 `[ ]` y `docs/trazabilidad_vm.md` sin entrada Bloque 4 (última entrada Bloque 3). **Siguen abiertos a cierre**; no se cierran ni se ocultan en este archive.

## Gate de Tasks (Task Completion Gate)

`tasks.md` archivado contiene **0 `[x]` / 11 `[ ]`** (tareas 1.1–1.4, 2.1–2.3, 3.1–3.3, 4.1 todas `[ ]`).

- Condición normal del gate: bloquearía el archive.
- Vía de excepción aplicada: override explícito del orquestador citado arriba + `verify-report` PASS WITH WARNINGS sin CRITICAL. No hay CRITICAL que bloquee (sin issues CRITICAL informados).
- Reconciliación NO ejecutada: no se marcan casillas `[x]` en el `tasks.md` archivado; el conteo 0/11 se preserva byte a byte en el move mecánico.

## Specs sincronizados

| Dominio | Acción | Detalle |
|---------|--------|---------|
| `presentacion-de-resultados` | Updated | 2 MODIFIED reemplazados, 1 ADDED appendido |

Deltas en `spec.md` (fichero único en raíz del change, ver nota estructural):

- ADDED `RESPUESTA-01` — Respuesta comparativa de 4 robustos (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39) con matriz O1-O4, mediana 26,61, 25,2 % sobre 30, advertencia Getxo 40 vs Vitoria-Gasteiz 39 (1 anuncio), trazabilidad en `docs/trazabilidad_vm.md`, sin tocar `data/raw`/raw HDFS, sin carpeta nueva, sin subir procesado.
- MODIFIED `INDICADORES-01` — 5 indicadores con pipeline Mongo verdadero o silver justificado, `metodo_imputacion` preservado, sin `fillna` mediana sin `is_imputed`, CSV 253/253/3 regenerables.
- MODIFIED `CONCLUSION-01` — Guion Tema 8 de 1 página (embedding, índices, atomicidad, HDFS centro + Kafka pid 1832), 10 criterios y lagunas, 16-29 legacy / 18-34 canónico, solo lectura HDFS, prod intacta.

Fuentes de verdad actualizadas:

- `openspec/specs/presentacion-de-resultados/spec.md`: `INDICADORES-01` (línea 114), `CONCLUSION-01` (línea 176) reemplazados; `RESPUESTA-01` (línea 203) appendido tras `CONCLUSION-01`, antes del Mapa trazable. Requisitos preservados intactos: `DATOS-HETEROGENEOS-01`, `AUTOMATIZACION-ANALISIS-01`, `PREPARACION-VISUALIZACION-01` y el Mapa §13–§14.

## Chequeo REMOVED / RENAMED (antes del merge)

- `spec.md` contiene `## ADDED Requirements` y `## MODIFIED Requirements`; **no contiene `## REMOVED Requirements` ni `## RENAMED Requirements`** (grep verificado).
- Ningún merge destructivo: no hubo advertencia de destrucción que bloquear que emitir. Si hubiera habido REMOVED/RENAMED, se habría advertido antes de mergear.

## Verificación de IDs inventados (`grep` en `openspec/specs/`)

- `INDICADORES-01`: existe como Requirement canónico en `presentacion-de-resultados/spec.md` (línea 114 pre-merge). MODIFIED válido, no inventado.
- `CONCLUSION-01`: existe como Requirement canónico (línea 183 pre-merge). MODIFIED válido, no inventado.
- `RESPUESTA-01`: **no existe** en `openspec/specs/` antes del merge (`grep -rn RESPUESTA-01` vacío, exit 1). Es ADDED genuino, no inventado. Tras el merge, `grep -c RESPUESTA-01 openspec/specs/presentacion-de-resultados/spec.md` = 1.
- `PREPARACION-VISUALIZACION-01` y `AGREGACION-01` citados en `proposal.md` como capacidades modificadas: **sin delta** en `spec.md` — ya existen sin cambios en main specs; sin merge, sin acción.

## Nota estructural (5 ficheros)

La orden pedía `specs/*/spec.md` (convención `_shared/openspec-convention.md`: `specs/{dominio}/spec.md`). El change real contiene **5 ficheros con delta en raíz**: `proposal.md`, `design.md`, `tasks.md`, `verify-report.md`, `spec.md` (sin subcarpeta `specs/`). El move mecánico preserva la estructura real sin reorganizar ni reescribir bytes vía modelo. El merge se hizo desde `spec.md` raíz contra `openspec/specs/presentacion-de-resultados/spec.md`.

## Contenido del archive

- `proposal.md` ✅
- `spec.md` (delta en raíz, 5 ficheros totales) ✅
- `design.md` ✅
- `tasks.md` (0/11 `[x]`, warning abierto) ✅
- `verify-report.md` (PASS WITH WARNINGS, warnings abiertos) ✅
- `archive-report.md` (este fichero, aditivo, excluido de la comparación `diff -r`) ✅

## Move mecánico y readback `diff -r` (MANDATORY)

```
snapshot_root=$(mktemp -d "${TMPDIR:-/tmp}/sdd-archive.XXXXXX")
cp -R "openspec/changes/bloque-4-conclusiones-entrega" "$snapshot_root/source"
git mv openspec/changes/bloque-4-conclusiones-entrega openspec/changes/archive/2026-11-05-bloque-4-conclusiones-entrega
# git mv: fatal: source directory is empty (untracked) -> fallback mv
mv openspec/changes/bloque-4-conclusiones-entrega openspec/changes/archive/2026-11-05-bloque-4-conclusiones-entrega
diff -r "$snapshot_root/source" "openspec/changes/archive/2026-11-05-bloque-4-conclusiones-entrega"
```

Salida verbatim de `diff -r` (vacía = idéntico):

```
(empty — no differences)
```

Verificación post-move:

- `ls openspec/changes/archive/2026-11-05-bloque-4-conclusiones-entrega/` → `design.md, proposal.md, spec.md, tasks.md, verify-report.md`
- `ls openspec/changes/bloque-4-conclusiones-entrega` → `No such file or directory` (fuente ausente)
- `grep -c "\[x\]" tasks.md` archivado → `0`; `grep -c "\[ \]"` → `11`
- `grep -n "Bloque 4" docs/trazabilidad_vm.md` → vacío (exit 1); `grep -n "pid 1832"` solo líneas 14–40 de Bloque 1
- `git status --short data/raw` → vacío (sin tocar `data/raw`)

## Guardrails de esta fase

- No se tocó `data/raw` ni raw HDFS. No se creó carpeta nueva en `data/`. No se subió procesado.
- No se hizo `git add` / `git commit` / `git push` en esta fase. El merge en `openspec/specs/presentacion-de-resultados/spec.md` y el move a archive quedan como cambios visibles en `git status --short`, sin commitear.
- El `tasks.md` archivado conserva 0/11 `[x]` y la trazabilidad conserva su última entrada en Bloque 3. Ambos warnings quedan como estado documentado de cierre.

## SDD Cycle

Ciclo completo bajo override intencional: planificado (proposal/spec/design/tasks), implementado (según apply/verify técnico), verificado PASS WITH WARNINGS, sincronizado y archivado. Ciclo cerrado con 2 warnings de proceso abiertos (trazabilidad Bloque 4 y marcado de tareas) documentados, sin ocultar.
