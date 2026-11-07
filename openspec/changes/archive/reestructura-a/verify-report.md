# Verify Report: reestructura-a (opción A, sin mover código)

Fecha: 2026-11-04

Cambios (solo movimientos + 3 ajustes de ruta, ningún import del pipeline tocado):
- `verificacion_crudos.py`, `verificar_fase_datos.py` (git mv) + `launch_duckdb_ui.py` → `scripts/`
- `archivosReto/` → `brief/` (git mv, 2 ficheros); dir eliminada
- `accesoHadoop/Kafka_Ejercicio.ipynb` → `notebooks/`; dir eliminada
- `b1.html`, `data_regen/`, `framework_auditoria_completo2/` → `archive/`
- `docs/`: 19 md → `docs/archive/2026-11/`; quedan 8 vigentes + `raw_manifest_sha256.txt`
- logs: `raw_guard_audit.log` solo en `logs/` (eliminadas copias raíz/transform/scratchpad)
- Rutas: `scripts/verificar_fase_datos.py` ROOT→parents[1], `scripts/launch_duckdb_ui.py` BASE→parent del parent, `scripts/verificacion_crudos.py` RAW relativo a ROOT

Verificado:
- `py_compile` scripts/ OK; ROOT resuelve a la raíz y el manifest existe
- `.venv/Scripts/python.exe -m pytest -q` → 108 passed

No verificado (fuera de alcance): ejecutar `scripts/verificar_fase_datos.py` completo (corre pytest interno 2 veces).

Resultado: PASS.

## Addenda 2026-11-04: guard escribe en un solo log
- `transform/_raw_guard.py`: `_DEFAULT_AUDIT_LOG` ahora es `logs/raw_guard_audit.log` y `AUDIT_LOG_PATHS` queda con una sola entrada (override por `RAW_GUARD_AUDIT_LOG` intacto; nadie importaba `AUDIT_LOG_PATHS`).
- Eliminadas copias en raíz/`transform/`/`scratchpad/`/`data/procesado/`.
- Verificado: `pytest -q` 108 passed y tras la suite completa no se regenera ningún log fuera de `logs/`.
- Nota de auditoría: el supuesto defecto de encoding en 'Sebastián' (U+FFFD) fue falsa alarma de visualización de terminal; codepoint verificado `0xe1` en CSV y en Mongo. Sin cambios de datos.
