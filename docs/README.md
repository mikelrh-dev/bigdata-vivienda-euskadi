# Índice de documentación — BigData Vivienda Euskadi

`docs/` conserva solo lo que el repositorio necesita para ejecutarse y defenderse.

| Ruta | Qué es |
|---|---|
| `raw_manifest_sha256.txt` | SHA-256 canónico de los 355 ficheros raw. Lo leen `scripts/gate_extremo_a_extremo.py`, `scripts/verificar_fase_datos.py`, `scripts/verificar_reproducibilidad.py`, `extract/generar_manifest.py`, el preflight de `scripts/run_pipeline.py` y `tests/test_raw_inmutable.py`; no se mueve. |
| `baseline_gold_sha256.json` | Huella del gold publicado. `scripts/verificar_reproducibilidad.py` la compara con el gold regenerado; se rehace con `--regenerar-baseline`. |
| `matriz-comparabilidad.md` | Matriz de comparabilidad entre fuentes y años. La lee `tests/test_comparabilidad.py` y la cita `config/parametros_estudio.yaml`. |
| `memoria/` | `memoria.pdf` y las figuras de `figuras/`. Las fuentes Markdown y `build.py` están en el checkout local, fuera de git. |
| `presentacion_v2/` | `presentacion_v2.pdf`. Las fuentes, el guion y los assets están en el checkout local, fuera de git. |
| `assets/readme/` | Imágenes que usa el README raíz. |

## Dónde está el resto

- **Fuentes de la memoria y del deck** (Markdown, `build.py`, `_cifras.*`, `index.html`, `guion.md`, `assets/`): presentes en el checkout local y excluidas de git por `.gitignore`. Los PDF se regeneran desde ahí con `docs/memoria/build.py`.
- **`openspec/`** (specs, cambios y auditorías): presente en el checkout local, fuera de git. `scripts/verificar_gobernanza.py` avisa y omite la verificación de requisitos cuando no lo encuentra.
- El histórico antiguo (planes, auditorías y versiones anteriores) queda en el archivo local externo, no versionado.
