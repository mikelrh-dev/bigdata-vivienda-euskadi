# Auditoría General Proyecto — 2026-10-28

Verificación: `py_compile OK`, `pytest 54 passed`. Solo lectura salvo los dos .md de auditoría.

## P1 — Errores potenciales (corregir antes de seguir extrayendo)

1. `PY` suelto a fin de fichero en `extract/16_serpavi_renta.py:95`, `extract/18_lanbide_paro_juvenil.py:75`, `extract/ine_atlas_renta.py:250`.
   - Está a nivel módulo, después del `if __name__`. Por subprocess (`main_ingest.py`) no rompe, por `import` lanza `NameError: PY`.
   - Acción: borrar esas 3 líneas. Verificar con `python -c "import extract.16..."` o `py_compile + import`.
2. `transform/dim_municipios.py:86,90,96` lee `anuncios_fotocasa.csv`, `alquiler_municipal.csv`, `anuncios_pisos.csv` sin `dtype=str` ni `encoding='utf-8-sig'`.
   - Pierde zero-padding Araba al comparar y rompe `Donostia - San Sebastián / Ciérvana` con `�`.
   - Acción: `pd.read_csv(..., dtype=str, encoding='utf-8-sig')` + `zfill(5)` como ya hacen `entity_resolution.py`, `generar_distancias.py`, `validar_renta.py`, `corregir_empleo.py`.
3. Directorio basura `C/.../scratchpad 2...` en raíz (comando mal entrecomillado anterior). `du data/raw 352M` + warning filename too long.
   - Acción: `rm -rf` esa carpeta rara, dejar `scratchpad/` solo con `inventory.py/reto.txt` o ignorarlo.

## P2 — Higiene y robustez

- `data/raw 352M` en local, `.gitignore` lo excluye bien (`data/raw/*` + `.env` + `api.txt`). `git ls-files` no rastrea credenciales: OK. Falta subir a HDFS `/raw` + `ingestion_manifest.json` como pide `almacenamiento-y-streaming/spec.md`.
- Untracked: `auditoria_avanzada/`, `framework_auditoria_v3_elite.zip`, `scratchpad/inventory.py`, `scratchpad/reto.txt`, los dos .md nuevos. Decidir qué se versiona y añadir a `.gitignore` lo que sea trabajo temporal.
- `except Exception` genérico en 10+ extractores + `main_ingest.py` que aísla fallos por extractor. Bien para recopilación, mal para debug silencioso: añadir al manifest `stderr_tail` cuando `rc!=0`.
- `eustat_renta_municipal.csv` crudo 275 ámbitos vs `dim` 252. Todo análisis debe filtrar por `dim_cods` o usar `renta_municipal_completa.csv`. Mismo para `distancias_capitales.csv` 259 → usar `_252`.
- `emancipacion_juventud.csv` solo abre con `delimiter=';' quotechar='"'` + `encoding utf-8-sig`. Documentarlo en `_common` o helper.
- ` Ukraina`: `alquiler_municipal.csv` sin `n_muestral`, `pisos` con `municipio_busqueda` ≠ ubicación real, `fotocasa` con `Donostia - San Sebastián` variante. Ya cubierto en auditoría dato puro, pero falta test que lo bloquee.

## P3 — Cobertura tests y fases

- `tests/test_contrato.py` 54 passed cubre contrato-reto, pero no hay tests de: zero-padding (`len==5`, prefijos `01/20/48`), temporal vs larga separados, outliers IQR segmentado, `renta_origen` fila a fila, `codigo_ine` en nuevas fuentes ya existe pero solo rango, no cruce con `dim`.
- Fases B/C/D (`almacenamiento-y-streaming`, `mongodb-y-analisis`, `presentacion-de-resultados`) sin código en repo (`visualization/`, `notebooks/`, `docker-compose.yml` no verificados aquí). No empezar hasta cerrar P1 dato puro.
- `config/fuentes.yaml` y `parametros_estudio.yaml` bien. `requirements.txt` pineado Python 3.12 OK. Añadir `geopandas/pyproj` solo cuando toque SHP→GeoJSON, no antes.

## Ruta mejora (orden)

1. Borrar 3× `PY`, fijar 3× `read_csv` en `dim_municipios.py`, borrar carpeta basura. Re-run `py_compile + pytest + import` de los 3 módulos.
2. Añadir 3 tests nuevos: `codigo_ine 5 dígitos en dim+alquiler+fotocasa+pisos`, `temporal/larga no mezclados`, `renta_completa 252 con origen explícito`.
3. Congelar `data/raw/*.csv` buenos como `_252` y archivar crudos viejos (`capitales.csv 259`, `udalmap sin corregir`).
4. Luego EMAL 73→más y alquiler 159→más (solo dato observado, sin imputar). Recién después HDFS/Kafka/Mongo.
