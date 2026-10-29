# Plan de regeneración de data/raw/ (modificados in place)

## Contexto
35 archivos en `data/raw/` fueron modificados in place por `transform/enriquecer_codigo_ine.py`, que añadió `codigo_ine`, `nombre_canonico`, `anio_fuente`. Los originales no están disponibles (sin backups). El manifest SHA-256 refleja el estado post-modificación.

## Archivos modificados (35)
CSV (20): alquiler_municipal, alquiler_seccion, anuncios_fotocasa, anuncios_fotocasa_habitaciones, anuncios_fotocasa_larga, anuncios_fotocasa_temporal, anuncios_pisos, anuncios_pisos_busqueda, anuncios_pisos_habitaciones, anuncios_realtyapi, dim_municipios, ine_atlas_renta, renta_municipal_completa, renta_municipal_referencia, udalmap_empleo, udalmap_empleo_corregido, udalmap_indicadores_adicionales.

JSON (15): anuncios_fotocasa, anuncios_fotocasa_enriquecido, anuncios_fotocasa_enriquecido_geo, anuncios_fotocasa_enriquecido_meta, anuncios_fotocasa_geo, anuncios_fotocasa_habitaciones, anuncios_fotocasa_habitaciones_geo, anuncios_fotocasa_habitaciones_meta, anuncios_fotocasa_meta, anuncios_pisos_habitaciones, anuncios_pisos_habitaciones_geo, anuncios_pisos_habitaciones_meta, dim_municipios, ine_atlas_renta, renta_municipal_completa, udalmap_empleo, udalmap_empleo_corregido, udalmap_indicadores_adicionales.

## Scripts que los generan (originalmente)
- 02_eustat_alquiler.py → alquiler_municipal, alquiler_seccion
- 05_fotocasa_scraper.py + fotocasa_detalle.py → anuncios_fotocasa*
- 08_pisos_scraper.py → anuncios_pisos*
- 09_realtyapi.py → anuncios_realtyapi*
- 13_scraping_habitaciones.py → anuncios_*_habitaciones*
- entity_resolution.py → dim_municipios
- ine_atlas_renta.py → ine_atlas_renta, renta_municipal_completa
- udalmap_empleo.py → udalmap_empleo
- corregir_empleo.py → udalmap_empleo_corregido
- 19_udalmap_indicadores_adicionales.py → udalmap_indicadores_adicionales
- parsear_secciones.py → alquiler_seccion
- completar_alquiler_comarca.py → alquiler_municipal (comarcal)
- dim_municipios.py (transform) → dim_municipios
- validar_renta.py → renta_municipal_completa, renta_municipal_referencia
- generar_distancias.py → dim_municipios
- filtrar_outliers.py → anuncios_fotocasa.json
- 12_enriquecer_json_anidado.py → anuncios_fotocasa_enriquecido.json
- 14_add_metadata_fingerprint.py → anuncios_fotocasa*.json, anuncios_pisos_habitaciones.json
- 15_add_geojson.py → anuncios_fotocasa_meta.json
- enriquecer_gtfs_conectividad.py → udalmap_empleo_corregido.csv
- f4_pisos_dirigido.py → anuncios_pisos.csv, dim_municipios.json

## Plan de regeneración (para mañana)

### Paso 1: Backup
```bash
cp -r data/raw data/raw_modified_2026-10-28
```

### Paso 2: Crear raw vacío
```bash
rm -rf data/raw && mkdir data/raw
```

### Paso 3: Ejecutar APIs estables (en orden)
```bash
python extract/01_eustat_api.py
python extract/02_eustat_alquiler.py
python extract/03_euskadi_emancipacion.py
python extract/04_b5m_geo.py
python extract/06_ine_api.py
python extract/07_ine_salarios.py
python extract/10_opendata_bizilagun_etxebide.py
python extract/11_transporte_gtfs_paradas.py
python extract/16_serpavi_renta.py
python extract/17_osrm_tiempos.py
python extract/18_lanbide_paro_juvenil.py
python extract/19_udalmap_indicadores_adicionales.py
python extract/20_ecvi_compraventa.py
python extract/21_lanbide_historico_paro_joven.py
```

### Paso 4: Copiar scraping del backup (no re-ejecutar)
```bash
cp data/raw_modified_2026-10-28/anuncios_fotocasa* data/raw/
cp data/raw_modified_2026-10-28/anuncios_pisos* data/raw/
cp data/raw_modified_2026-10-28/anuncios_realtyapi* data/raw/
```

### Paso 5: Ejecutar transforms que generan archivos derivados
```bash
python transform/corregir_empleo.py
python transform/dim_municipios.py
python transform/validar_renta.py
python transform/completar_alquiler_comarca.py
python transform/parsear_secciones.py
python transform/generar_distancias.py
```

### Paso 6: Comparar hashes
```bash
cd data/raw && sha256sum -c ../../data/raw_modified_2026-10-28/manifest_sha256.txt 2>/dev/null || echo "Comparar manualmente"
```

### Paso 7: Decisión
- Si los hashes coinciden → raw está crudo de nuevo. Eliminar backup.
- Si no coinciden → restaurar backup y documentar limitación.

## Nota sobre inmutabilidad de raw
A futuro, `data/raw/` es **inmutable**. Toda normalización va a `data/procesado/`. Si se regenera raw exitosamente, reprocesar todo lo necesario en `data/procesado/` (normalizar_json_crudos, limpiar_ecvi, limpiar_eustat_demografia, unificar_anuncios, etc.).

## Nota sobre error 400 de Eustat
La API de Eustat devolvió 400 (rate limiting/bloqueo por IP). Reintentar mañana puede funcionar si el bloqueo es temporal. Si persiste, documentar y usar datos existentes.

## Fecha del plan
2026-10-29 (noche). Mañana reintentar.

---

## Reanálisis 2026-10-29 (ejecución pendiente)

### 1. Qué se verificó (evidencia real)

- Backup de seguridad creado: `data/raw_backup_2026-10-29/` (380 MB). `data/raw` sigue intacto.
- Manifest SHA-256 (`data/raw/manifest_sha256.txt`, 47 entradas, solo CSV): **todos OK** contra `data/raw` actual (tras limpiar CRLF). Pero el manifest NO cubre JSON ni los archivos añadidos después (ECVI, Lanbide histórico, etc.).
- Test de Eustat API hoy: `ExtractorBlob` responde 200, pero el contenido **cambió** (22.399 vs 22.667 bytes vs backup). Conclusión: regenerar raw NO producirá hashes idénticos; la comparación de hashes del Paso 6 no es un criterio válido para APIs vivas.
- `.bak_f0` de `transform/enriquecer_codigo_ine.py`: **no existen** (0 archivos). Los originales pre-enriquecimiento no están disponibles.
- `tests/test_crudos.py` exige `codigo_ine` en raw (`alquiler_municipal`, `anuncios_*`, `renta_municipal_completa`, etc.). Por tanto un raw "crudo" sin entity resolution rompe los tests actuales.

### 2. Archivos realmente modificados in place por `enriquecer_codigo_ine.py`

Solo 8 (no 35 como decía el plan original):

- `alquiler_municipal.csv` / `.json`  (+ codigo_ine, nombre_canonico, anio_fuente)
- `anuncios_fotocasa.csv` / `.json`     (+ codigo_ine, nombre_canonico, anio_fuente)
- `anuncios_pisos.csv` / `.json`       (+ codigo_ine, nombre_canonico_resuelto, anio_fuente, es_busqueda_no_ubicacion)
- `anuncios_realtyapi.csv` / `.json`    (+ codigo_ine, nombre_canonico, anio_fuente)

El resto de raw (Eustat, INE, Udalmap, GTFS, SERPAVI, OSRM, Lanbide, ECVI, educacion, salud, EMAL, Etxebide, etc.) NO pasó por `enriquecer_codigo_ine.py`; su `codigo_ine` viene de la propia fuente o de extractores que lo añaden en origen.

### 3. Por qué el plan original no es ejecutable tal cual

1. `rm -rf data/raw` destruye 177 archivos, muchos no regenerables (scraping Fotocasa/Pisos/RealtyAPI inestable, ECVI, etc.).
2. El Paso 6 (comparar hashes) fallará siempre: las APIs devuelven datos actualizados y el scraping no se re-ejecuta.
3. El Paso 5 no incluye `enriquecer_codigo_ine.py`, así que el raw regenerado no tendría `codigo_ine` en los 8 archivos anteriores y rompería `tests/test_crudos.py`.
4. No hay `.bak_f0`, así que no se puede "restaurar original" si algo falla.

### 4. Opciones

**Opción A — Congelar raw actual (recomendada, bajo riesgo)**
- Considerar `data/raw` actual como versión congelada (incluye entity resolution en origen, que es comportamiento documentado de los extractores).
- No regenerar ni modificar in place. Nuevas transformaciones escriben a `data/procesado/`.
- `enriquecer_codigo_ine.py` deja de modificar raw; si se necesita re-enriquecer, se hace sobre copia en `data/procesado/`.
- Actualizar tests para leer `codigo_ine` desde procesado cuando corresponda (cambio mayor, coordinar con el otro agente).

**Opción B — Regeneración paralela (validación, sin tocar raw)**
- Crear `data/raw_regen/` y ejecutar los extractores de APIs estables ahí (Eustat, INE, Open Data, GTFS, SERPAVI, OSRM, Lanbide, ECVI, Udalmap, EMAL, Etxebide).
- Copiar scraping desde `data/raw_backup_2026-10-29/` (no re-scrapear).
- Ejecutar transforms derivados en `data/raw_regen/`.
- Comparar estructura (columnas, filas, rangos) con `data/raw`, no hashes exactos.
- Si la regeneración es consistente, promover `raw_regen` → `raw` (con backup previo).

**Opción C — Regeneración destructiva (plan original)**
- Solo si se acepta pérdida de inmutabilidad estricta y se asume que los tests se ajustarán. No recomendada.

### 5. Decisión pendiente

Antes de ejecutar cualquier opción, confirmar con el usuario:
- ¿Opción A (congelar) o B (regeneración paralela)?
- ¿Se modifica `enriquecer_codigo_ine.py` para escribir a `data/procesado/` (cambio de arquitectura)?
- ¿Se actualiza `tests/test_crudos.py` para no exigir `codigo_ine` en raw?

Backup disponible en `data/raw_backup_2026-10-29/` para restaurar si se opta por B/C.

---

## Ejecución Opción A — 2026-10-29

- `data/raw/.FROZEN` creado (marker de congelado).
- `data/raw` puesto en modo solo lectura (`chmod -R a-w`).
- `transform/enriquecer_codigo_ine.py` modificado: aborta por defecto si `.FROZEN` existe; override con `--force`.
- `tests/test_crudos.py`: 3 passed (sin cambios).
- Manifest SHA-256: 47/47 OK (raw intacto).
- Backup de seguridad: `data/raw_backup_2026-10-29/` (380 MB).

Convención vigente: `data/raw` es inmutable. Toda normalización/enriquecimiento va a `data/procesado/`.

---

## Garantía profesional de inmutabilidad (2026-10-29)

- Manifest canonical completo (297 archivos, incluidos JSON y derivados): `docs/raw_manifest_sha256.txt` (versionable en git).
- Test de integridad: `tests/test_raw_inmutable.py` (verifica `.FROZEN` + hashes del manifest). Falla si alguien altera raw.
- `data/raw` sigue en `.gitignore`; solo el manifest y el test se versionan.
- Para modificar raw de forma consciente: borrar `.FROZEN`, registrar el motivo, regenerar manifest con `find data/raw -type f ! -name .FROZEN | sort | xargs sha256sum > docs/raw_manifest_sha256.txt`, y volver a congelar.

Nota: esto detecta alteraciones **posteriores** al manifest. No recupera versiones pre-modificación (no existen backups previos).