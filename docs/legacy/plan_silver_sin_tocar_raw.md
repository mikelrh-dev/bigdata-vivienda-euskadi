# Plan: procesamiento silver sin tocar raw (raw inmutable)

> Planificación. NO ejecutar sin confirmación. Raw permanece congelado.

## 1. Situación actual

- `data/raw/` congelado (`.FROZEN`, read-only, manifest + test).
- `data/procesado/` desactualizado (pre-regeneración).
- Resultados de la regeneración paralela en `data_regen/procesado/` (referencia).
- Muchos transforms leen raw y **escriben a raw** (violación bronce): corregir_empleo, dim_municipios, generar_distancias, validar_renta, parsear_secciones, f4_pisos_dirigido, enriquecer_codigo_ine.

## 2. Objetivo

Ejecutar todo el procesamiento posterior (silver) escribiendo **solo** a `data/procesado/`, sin modificar `data/raw/`. Raw sigue inmutable.

## 3. Inventario de transforms (I/O)

### A. Leen raw, escriben raw (REQUIEREN CAMBIO)
| Script | Lee | Escribe (actual) | Debe escribir a |
|---|---|---|---|
| `corregir_empleo.py` | raw/udalmap_empleo.csv | raw/udalmap_empleo_corregido.csv/.json | procesado/udalmap_empleo_corregido.csv/.json |
| `dim_municipios.py` | raw/* (eustat, anuncios, alquiler, emal) | raw/dim_municipios.csv/.json | procesado/dim_municipios.csv/.json |
| `generar_distancias.py` | raw/dim_municipios.csv, distancias_capitales.csv, geojson | raw/distancias_capitales_252.csv, distancias_haversine_252.csv, geojson modificado | procesado/... |
| `validar_renta.py` | raw/renta_municipal_completa.csv, dim_municipios.csv | raw/renta_municipal_referencia.csv | procesado/renta_municipal_referencia.csv |
| `parsear_secciones.py` | raw/alquiler_seccion_*_original.csv | raw/alquiler_seccion.csv + procesado/alquiler_seccion_resumen.csv | procesado/alquiler_seccion.csv + resumen |
| `f4_pisos_dirigido.py` | raw/anuncios_pisos.json, dim_municipios.json, procesado/f4_pisos_objetivo.json | raw/anuncios_pisos.csv/.json + procesado/f4_pisos_informe.csv | procesado/anuncios_pisos_filtrado.csv/.json + informe |
| `enriquecer_codigo_ine.py` | raw/* | raw/* in place (+ backup .bak_f0) | procesado/*_enriquecido + informe |

### B. Leen raw, escriben procesado (OK, sin cambio)
- `completar_alquiler_comarca.py` → procesado/alquiler_municipal_completo.csv
- `filtrar_outliers.py` → procesado/*_filtrado.json/.csv
- `limpiar_ecvi.py` → procesado/ecvi_compraventa_limpio.csv/.json
- `limpiar_eustat_demografia.py` → procesado/eustat_demografia_renta_252.csv/.json
- `normalizar_json_crudos.py` → procesado/*_normalizado.json
- `unificar_anuncios.py` → procesado/anuncios_unificados.csv/.json
- `enriquecer_equipamiento_realtyapi.py` → procesado/anuncios_unificados.csv (append)
- `enriquecer_gtfs_conectividad.py` → procesado/transporte_paradas_municipio_enriquecido.csv
- `generar_fingerprint.py` → procesado/anuncios_unificados.csv

## 4. Cambios necesarios (mínimos, sin tocar raw)

Para cada script del grupo A, modificar:
- Rutas de salida: `RAW_DIR / "x"` → `PROC_DIR / "x"` (donde PROC_DIR = ROOT/data/procesado).
- Lecturas siguen de `RAW_DIR` (raw inmutable).
- `generar_distancias.py`: el geojson modificado (municipios_euskadi.geojson) debe escribirse a procesado, no a raw. O dejar el geojson en raw (es crudo de geografía) — decisión: mantener geojson en raw (es crudo), pero las distancias derivadas van a procesado.

## 5. Orden de ejecución (silver)

1. `enriquecer_codigo_ine.py` → procesado/*_enriquecido + informe (leer raw, escribir procesado).
2. `corregir_empleo.py` → procesado/udalmap_empleo_corregido.
3. `dim_municipios.py` → procesado/dim_municipios (leer enriquecidos de procesado).
4. `validar_renta.py` → procesado/renta_municipal_referencia (+ implementar renta_joven).
5. `completar_alquiler_comarca.py` → procesado/alquiler_municipal_completo.
6. `parsear_secciones.py` → procesado/alquiler_seccion.csv + resumen.
7. `generar_distancias.py` → procesado/distancias_*.
8. `filtrar_outliers.py`, `normalizar_json_crudos.py`, `limpiar_*`, `unificar_anuncios.py`, `generar_fingerprint.py`, `enriquecer_*`.

## 6. Implementar renta_joven (deuda)

Según `docs/metodologia.md`: `renta_joven_estimada = renta_municipal_18plus * (renta_media_18_34_CAE / renta_media_18plus_CAE)`. Requiere datos Eustat RPF por edad (raw/eustat_renta_edad.csv o similar). Implementar en `validar_renta.py` o en un nuevo transform `calcular_renta_joven.py` en procesado.

## 7. Verificación

- `data/raw/` no modificado (test_raw_inmutable.py sigue pasando).
- `data/procesado/` contiene todos los archivos esperados (comparar con inventario).
- Tests actualizados: `tests/test_crudos.py` lee `codigo_ine` desde procesado.
- Consumidores (scratchpad/analysis.py, EDA) apuntan a procesado.

## 8. Riesgos

- Muchos scripts hardcodean rutas a raw; requiere cambios coordinados.
- `dim_municipios.py` lee múltiples fuentes; si alguna falta, falla.
- El geojson se modifica in place en generar_distancias; mover esa escritura a procesado.

## 9. Decisión pendiente

- ¿Se modifican los transforms ahora (grupo A) o se crea un wrapper que redirige salidas?
- ¿Se implementa renta_joven en esta fase o se deja para después?
- ¿Se actualizan los tests de crudos para leer de procesado?