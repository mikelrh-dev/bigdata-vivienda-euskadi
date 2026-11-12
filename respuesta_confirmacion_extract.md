# Confirmación: qué hace extract/

**Veredicto: sí, la afirmación de Alex es correcta.** extract/ no es solo descarga de externos. Algunos scripts de extract/ escriben productos fuera de `data/raw/`, directamente en `data/procesado/` o en carpetas intermedias.

## Scripts de extract/ que escriben fuera de raw (confirmados por código)

### 1. extract/normalizar_metadata.py
Escribe sidecars e índice en `data/procesado/_meta/`. No escribe en raw. Es un script de normalización de metadata, no de extracción de datos nuevos.

### 2. extract/generar_ingestion_manifest.py
Escribe el manifiesto en `data/procesado/_meta/ingestion_manifest.json`. No escribe en raw. Es un script manifiesto.

### 3. extract/generar_manifest.py con `--write`
Escribe un manifiesto tanto en `data/raw/` (o donde esté raw) como en `data/procesado/`. Es un script de manifiesto.

### 4. extract/09_fotocasa_dirigido.py
Guarda en:
- `data/raw/` (datos extraídos de fotocasa dirigido)
- `data/procesado/fotocasa_dirigido_informe.csv` (informe)

En `data/procesado/`, además de sus datos extraídos en raw.

### 5. extract/26_vpo_terminadas.py
Usa `data/staging/vpo/` temporalmente, luego copia el resultado final a `data/raw/`. No escribe directamente en `data/procesado/`, pero sí usa una carpeta intermedia antes de llegar a raw.

### 6. extract/22_geo_areas_funcionales.py
Usa una carpeta temporal del sistema y deja su salida final en `data/raw/`. No escribe en `data/procesado/`.

## Qué escriben los demás scripts de extract/ (resumen)

Los demás scripts de extract/ escriben exclusivamente en `data/raw/` o en carpetas temporales antes de copiar a raw. No escriben en `data/procesado/`. Esto confirma que extract/ es principalmente descarga y transformación de crudos, pero tiene excepciones documentadas por Alex.

## Confirmación sin ejecutar nada

No se ejecutó nada. La confirmación se basa en lectura de código real de estos scripts y sus rutas de escritura declaradas. La afirmación de Alex es correcta y coincide con lo que dice el código.

## Importante para el contexto del problema de tu compañero

Esto refuerza la conclusión principal:

- `extract/` no es solo descarga de externos. Tiene scripts que preparan productos de procesado (metadata, manifiestos, informes de captura dirigida).
- Si tu compañero ejecutó solo `transform/run_all.py` tras borrar `data/procesado/` y `data/resultados/`, le falta todo lo que producen estos scripts de extract/ que no están en el orquestador.
- Además, `transform/run_all.py` no genera todo `data/procesado/` porque parte de lo que hay en esa carpeta viene de extract/.

Esto significa que la reconstrucción completa requiere ejecutar extract/ + transform/run_all.py + analysis/ + generar_figuras_N.py + scripts manuales excluidos.

## Resumen ejecutivo

Alex dijo la verdad. extract/ tiene scripts que escriben en `data/procesado/` (normalizar_metadata.py, generar_ingestion_manifest.py, generar_manifest.py --write, 09_fotocasa_dirigido.py) y scripts que usan carpetas temporales antes de llegar a raw (26_vpo_terminadas.py, 22_geo_areas_funcionales.py). No todos los scripts de extract/ escriben exclusivamente en raw. Esto no es un bug, es por diseño, y confirma que la regeneración con solo `transform/run_all.py` es insuficiente.
