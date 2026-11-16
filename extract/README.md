# `extract/` — descarga y normaliza hacia `data/raw`

`data/raw` es inmutable (marcador `.FROZEN`). Todo lo que escribe aquí lo hace con guard.

## Cómo se ejecuta

`main_ingest.py` ejecuta en orden alfabético todos los `NN_*.py` (glob `[0-9][0-9]_*.py`) y después los de `AUX_SCRIPTS`.

→ Un extractor nuevo debe llamarse `NN_nombre.py` o añadirse a `AUX_SCRIPTS`. Si no, existe pero no se ejecuta nunca.

## Lo que no es un extractor (y no debe moverse)

| Fichero | Qué es |
|---|---|
| `generar_manifest.py` | Genera y verifica el manifiesto SHA-256. Lo invoca `scripts/run_pipeline.py`; el canónico es `docs/raw_manifest_sha256.txt` |
| `normalizar_metadata.py` | Normaliza la metadata de los JSON de `raw` (WP-07) |
| `generar_ingestion_manifest.py` | Acta máquina-legible de la ingesta (WP-17) |

Están aquí porque **operan sobre `raw`**, pero no descargan nada: los tres los lanza `run_pipeline`, no `main_ingest`.

Librerías sin `__main__` (no son pasos): `_common.py` (HTTP, logging, guardado con guard de raw) y `entity_resolution.py` (municipio → `codigo_ine`).

## Una excepción al revés

`scripts/descargar_ipc_ine.py` **sí** es un extractor (importa `_common`, escribe en `data/raw`), pero vive en `scripts/`. No se mueve: el PDF ya entregado (`docs/presentacion_v2/presentacion_v2.pdf`) cita esa ruta, y moverlo obliga a regenerar el deck.
