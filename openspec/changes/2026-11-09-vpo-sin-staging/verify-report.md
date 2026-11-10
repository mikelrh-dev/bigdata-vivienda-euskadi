# Verify report: vpo-sin-staging

Fecha: 2026-11-09
Veredicto: **PASS**
Alcance: eliminar `data/staging/` del flujo del indicador 73 sin alterar
`data/raw/udalmap_vpo_terminadas.csv`, su manifest ni la copia HDFS.

## 1. Cambios aplicados

| Fichero | Cambio |
|---|---|
| `extract/26_vpo_terminadas.py` | Descarga en memoria, `validar(bytes)`, `--desde-raw` (alias `--sin-descargar`), `--promote` idempotente y no destructivo |
| `.gitignore` | Eliminada la entrada `data/staging/` |
| `data/staging/` | Eliminado (solo contenía `vpo/indicator.csv`, 35.427 B) |
| `openspec/changes/2026-11-05-cierre-suficiencia-auditoria/` | `design.md`, `proposal.md`, `specs/vpo-municipal/spec.md` y `tasks.md` actualizados |
| `openspec/changes/2026-11-09-vpo-sin-staging/` | Proposal, spec delta, design, tasks y este verify-report |

## 2. Evidencia antes/después

| Comprobación | Antes | Después |
|---|---|---|
| Raw local | 35.427 B, SHA `70a2937a…1294706`, mtime `1793914427` | **Idéntico** |
| Manifest | Línea 354 con el mismo SHA | **Idéntica** |
| HDFS `GETFILESTATUS` | 200, `length=35427` | **200, `length=35427`** |
| HDFS `OPEN` | 35.427 B, SHA `70a2937a…1294706` | **Idéntico** |
| HDFS `data/raw` | 201 entradas, contiene `udalmap_vpo_terminadas.csv` | **Idéntico** |
| `data/staging` | Existía con 1 CSV | **Eliminado** |
| `.gitignore` | Ignoraba `data/staging/` | **Sin entrada** |

HDFS `data/procesado` sigue devolviendo **404**; queda fuera de este cambio
(gap C2 de la auditoría).

## 3. Pruebas de flujo

### `--desde-raw`

```text
origen: raw existente ...\data\raw\udalmap_vpo_terminadas.csv
validacion OK: 272 codigos de 5 digitos (>= 252), 2024 0.00-62.55 por mil
sha256 payload: 70a2937a...1294706
sin --promote: data/raw no se ha tocado
exit 0
```

### `--desde-raw --promote`

```text
--promote no aplica con --desde-raw
exit 1
```

### `promover()` directo

| Caso | Resultado |
|---|---|
| Mismo SHA | `(ruta, False)`; mtime y SHA intactos |
| SHA distinto | `SystemExit` con “raw inmutable”; fichero intacto |
| Raw ausente (temp) | Escribe el payload, `escrito=True`, 35.427 B |

### Descarga real sin `--promote`

```text
origen: descarga https://opendata.euskadi.eus/.../indicator.csv
validacion OK: 272 codigos de 5 digitos (>= 252), 2024 0.00-62.55 por mil
sha256 payload: 70a2937a...1294706
sin --promote: data/raw no se ha tocado
exit 0
```

Después de la descarga: `STAGING_NO_CREADO` y raw con el mismo SHA/mtime.

## 4. Tests y gates

| Comando | Resultado |
|---|---|
| `pytest tests/test_raw_inmutable.py tests/test_raw_guardrails.py tests/test_vpo_municipal.py -q` | **15 passed**, exit 0 |
| `pytest tests -q` | **238 colectados, 236 passed, 2 skipped**, exit 0 |
| `python scripts/verificar_gobernanza.py` | **TODO OK** (46 requisitos, 45/34 scripts, 188 silver, 11 pipelines) |
| `python transform/run_all.py --check` | **exit 0** |
| `git diff --check` | **exit 0** |

## 5. Inmutabilidad

- `tests/test_raw_inmutable.py` valida el `.FROZEN`, los SHA del manifest y que
  no haya ficheros nuevos sin listar: **PASS**.
- `tests/test_raw_guardrails.py` valida que ningún transform escriba en raw sin
  guard: **PASS**.
- La sonda de `promover()` comprobó `st_mtime_ns` antes/después: **sin cambio**.
- El `--promote` con SHA distinto aborta antes de escribir.
- No se creó ningún fichero en `data/raw/` durante la verificación.

## 6. Notas

- No se añadieron tests; la suite sigue en 238 colectados.
- No se ejecutó `transform/limpiar_vpo_municipal.py`: el silver no se toca.
- La evidencia histórica `openspec/audit/evidencia/2026-11-08/inventario_archivos.csv`
  conserva la fila de staging como foto de esa fecha; no se reescribe.
- El cambio no altera el gap de HDFS `procesado` (404).
