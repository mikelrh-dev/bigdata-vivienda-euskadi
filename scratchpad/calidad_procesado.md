# Informe de calidad: data/procesado (actual) vs data/procesado_pre_silver (backup)

- Directorio actual: `C:/Users/mikel/Documents/bigdata-vivienda-euskadi/data/procesado`
- Backup previo: `C:/Users/mikel/Documents/bigdata-vivienda-euskadi/data/procesado_pre_silver`
- Archivos en actual: 89 (incl. .gitkeep)
- Archivos en backup: 107 (incl. .gitkeep)
- Archivos comunes analizados: 88

## 1. Resumen general

- Archivos comunes tabulares comparados: **86**
- Archivos comunes no tabulares/omitidos: **2**
- Archivos solo en backup (eliminados del actual): **18**
- Archivos solo en actual (nuevos): **0**
- Archivos con alguna regresión (filas/cols/nulos): **0**
- Archivos con alguna mejora: **0**
- Archivos con valores idénticos (mismas filas/cols/valores): **86** / 86
- Verificación de integridad: los 88 archivos comunes son byte-idénticos (MD5) entre actual y backup; por tanto no hay cambios de filas/columnas/nulos en la intersección.
- Filas totales (tabulares): backup 595,636 -> actual 595,636 (delta +0)
- Nulos totales (tabulares): backup 44,514 -> actual 44,514 (delta +0)

### Archivos comunes no tabulares (omitidos de comparación tabular)

- `emancipacion_juventud_resumen_normalizado.json`
- `municipios_euskadi_252.geojson`

## 2. Archivos eliminados (solo en backup)

- Total eliminados: **18** (tabulares: 15, no tabulares/backup: 3)
- Estos archivos no existen en el procesado actual; se consideran **regresión de disponibilidad** aunque sus equivalentes comunes sean idénticos.

### Tabulares eliminados

- `alquiler_rescatado_seccion.csv`
- `analisis_variables_base.csv`
- `emancipacion_tier3_93.csv`
- `f4_pisos_informe.csv`
- `informe_calidad_f5.csv`
- `municipios_faltantes_93.csv`
- `pob_rank.csv`
- `r1_batch_1.json`
- `r1_batch_2.json`
- `r1_batch_3.json`
- `r1_batch_4.json`
- `r1_fotocasa_informe.csv`
- `r1_municipios_objetivo.json`
- `r1_pisos_informe.csv`
- `r1_sin_alquiler.json`

### No tabulares / logs / backups eliminados

- `f4_fotocasa.log`
- `f4_pisos_objetivo.json.bak_r1`
- `v1_detalle.log`

## 3. Archivos nuevos (solo en actual)

- (ninguno)

## 4. Comparación por archivo (comunes tabulares)

| Archivo | Filas backup | Filas actual | Δ filas | Cols backup | Cols actual | Δ cols | Nulos backup | Nulos actual | Δ nulos | Valores idénticos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `alquiler_municipal_completo.csv` | 252 | 252 | +0 | 17 | 17 | +0 | 0 | 0 | +0 | Sí |
| `alquiler_municipal_enriquecido.csv` | 253 | 253 | +0 | 18 | 18 | +0 | 0 | 0 | +0 | Sí |
| `alquiler_municipal_enriquecido.json` | 253 | 253 | +0 | 18 | 18 | +0 | 0 | 0 | +0 | Sí |
| `alquiler_municipal_normalizado.json` | 253 | 253 | +0 | 15 | 15 | +0 | 0 | 0 | +0 | Sí |
| `alquiler_seccion.csv` | 1569 | 1569 | +0 | 19 | 19 | +0 | 1569 | 1569 | +0 | Sí |
| `alquiler_seccion_resumen.csv` | 159 | 159 | +0 | 6 | 6 | +0 | 0 | 0 | +0 | Sí |
| `anuncios_fotocasa_detalle_normalizado.json` | 470 | 470 | +0 | 20 | 20 | +0 | 129 | 129 | +0 | Sí |
| `anuncios_fotocasa_enriquecido.csv` | 471 | 471 | +0 | 26 | 26 | +0 | 1693 | 1693 | +0 | Sí |
| `anuncios_fotocasa_enriquecido.json` | 471 | 471 | +0 | 37 | 37 | +0 | 3181 | 3181 | +0 | Sí |
| `anuncios_fotocasa_enriquecido_geo_normalizado.json` | 471 | 471 | +0 | 41 | 41 | +0 | 2710 | 2710 | +0 | Sí |
| `anuncios_fotocasa_enriquecido_meta_normalizado.json` | 471 | 471 | +0 | 40 | 40 | +0 | 2710 | 2710 | +0 | Sí |
| `anuncios_fotocasa_enriquecido_normalizado.json` | 471 | 471 | +0 | 38 | 38 | +0 | 2710 | 2710 | +0 | Sí |
| `anuncios_fotocasa_filtrado.csv` | 471 | 471 | +0 | 42 | 42 | +0 | 3171 | 3171 | +0 | Sí |
| `anuncios_fotocasa_filtrado.json` | 471 | 471 | +0 | 42 | 42 | +0 | 2720 | 2720 | +0 | Sí |
| `anuncios_fotocasa_geo_normalizado.json` | 471 | 471 | +0 | 39 | 39 | +0 | 2710 | 2710 | +0 | Sí |
| `anuncios_fotocasa_habitaciones_geo_normalizado.json` | 155 | 155 | +0 | 38 | 38 | +0 | 843 | 843 | +0 | Sí |
| `anuncios_fotocasa_habitaciones_meta_normalizado.json` | 155 | 155 | +0 | 37 | 37 | +0 | 843 | 843 | +0 | Sí |
| `anuncios_fotocasa_habitaciones_normalizado.json` | 155 | 155 | +0 | 35 | 35 | +0 | 843 | 843 | +0 | Sí |
| `anuncios_fotocasa_meta_normalizado.json` | 471 | 471 | +0 | 38 | 38 | +0 | 2710 | 2710 | +0 | Sí |
| `anuncios_fotocasa_normalizado.json` | 471 | 471 | +0 | 36 | 36 | +0 | 2710 | 2710 | +0 | Sí |
| `anuncios_pisos_dirigido.csv` | 251 | 251 | +0 | 15 | 15 | +0 | 517 | 517 | +0 | Sí |
| `anuncios_pisos_dirigido.json` | 251 | 251 | +0 | 19 | 19 | +0 | 592 | 592 | +0 | Sí |
| `anuncios_pisos_enriquecido.csv` | 235 | 235 | +0 | 19 | 19 | +0 | 303 | 303 | +0 | Sí |
| `anuncios_pisos_enriquecido.json` | 235 | 235 | +0 | 19 | 19 | +0 | 521 | 521 | +0 | Sí |
| `anuncios_pisos_enriquecido_geo_normalizado.json` | 230 | 230 | +0 | 21 | 21 | +0 | 501 | 501 | +0 | Sí |
| `anuncios_pisos_enriquecido_meta_normalizado.json` | 230 | 230 | +0 | 21 | 21 | +0 | 501 | 501 | +0 | Sí |
| `anuncios_pisos_enriquecido_normalizado.json` | 230 | 230 | +0 | 19 | 19 | +0 | 501 | 501 | +0 | Sí |
| `anuncios_pisos_filtrado.csv` | 235 | 235 | +0 | 24 | 24 | +0 | 556 | 556 | +0 | Sí |
| `anuncios_pisos_filtrado.json` | 235 | 235 | +0 | 25 | 25 | +0 | 549 | 549 | +0 | Sí |
| `anuncios_pisos_geo_normalizado.json` | 230 | 230 | +0 | 19 | 19 | +0 | 501 | 501 | +0 | Sí |
| `anuncios_pisos_habitaciones_geo_normalizado.json` | 46 | 46 | +0 | 19 | 19 | +0 | 186 | 186 | +0 | Sí |
| `anuncios_pisos_habitaciones_meta_normalizado.json` | 46 | 46 | +0 | 19 | 19 | +0 | 186 | 186 | +0 | Sí |
| `anuncios_pisos_habitaciones_normalizado.json` | 46 | 46 | +0 | 17 | 17 | +0 | 186 | 186 | +0 | Sí |
| `anuncios_pisos_meta_normalizado.json` | 230 | 230 | +0 | 19 | 19 | +0 | 501 | 501 | +0 | Sí |
| `anuncios_pisos_normalizado.json` | 235 | 235 | +0 | 19 | 19 | +0 | 521 | 521 | +0 | Sí |
| `anuncios_realtyapi_enriquecido.csv` | 139 | 139 | +0 | 17 | 17 | +0 | 79 | 79 | +0 | Sí |
| `anuncios_realtyapi_enriquecido.json` | 139 | 139 | +0 | 25 | 25 | +0 | 220 | 220 | +0 | Sí |
| `anuncios_realtyapi_normalizado.json` | 139 | 139 | +0 | 25 | 25 | +0 | 220 | 220 | +0 | Sí |
| `anuncios_unificados.csv` | 840 | 840 | +0 | 8 | 8 | +0 | 748 | 748 | +0 | Sí |
| `anuncios_unificados.json` | 840 | 840 | +0 | 12 | 12 | +0 | 86 | 86 | +0 | Sí |
| `b5m_catalogo_normalizado.json` | 29 | 29 | +0 | 15 | 15 | +0 | 81 | 81 | +0 | Sí |
| `dim_municipios.csv` | 252 | 252 | +0 | 9 | 9 | +0 | 0 | 0 | +0 | Sí |
| `dim_municipios.json` | 252 | 252 | +0 | 9 | 9 | +0 | 0 | 0 | +0 | Sí |
| `dim_municipios_normalizado.json` | 252 | 252 | +0 | 9 | 9 | +0 | 0 | 0 | +0 | Sí |
| `distancias_b5m_gipuzkoa_normalizado.json` | 180488 | 180488 | +0 | 15 | 15 | +0 | 0 | 0 | +0 | Sí |
| `distancias_capitales_252.csv` | 252 | 252 | +0 | 11 | 11 | +0 | 0 | 0 | +0 | Sí |
| `distancias_haversine_252.csv` | 63504 | 63504 | +0 | 3 | 3 | +0 | 0 | 0 | +0 | Sí |
| `distancias_municipios_normalizado.json` | 63504 | 63504 | +0 | 3 | 3 | +0 | 0 | 0 | +0 | Sí |
| `ecvi_compraventa_limpio.csv` | 29 | 29 | +0 | 7 | 7 | +0 | 51 | 51 | +0 | Sí |
| `ecvi_compraventa_limpio.json` | 29 | 29 | +0 | 7 | 7 | +0 | 51 | 51 | +0 | Sí |
| `educacion_centros_normalizado.json` | 1309 | 1309 | +0 | 20 | 20 | +0 | 0 | 0 | +0 | Sí |
| `emal_fianzas_ampliado_normalizado.json` | 730 | 730 | +0 | 13 | 13 | +0 | 64 | 64 | +0 | Sí |
| `emal_fianzas_normalizado.json` | 730 | 730 | +0 | 9 | 9 | +0 | 62 | 62 | +0 | Sí |
| `etxebide_solicitudes_normalizado.json` | 5040 | 5040 | +0 | 4 | 4 | +0 | 1 | 1 | +0 | Sí |
| `eustat_demografia_renta_252.csv` | 252 | 252 | +0 | 9 | 9 | +0 | 252 | 252 | +0 | Sí |
| `eustat_demografia_renta_252.json` | 252 | 252 | +0 | 9 | 9 | +0 | 252 | 252 | +0 | Sí |
| `eustat_pib_municipal_normalizado.json` | 13248 | 13248 | +0 | 6 | 6 | +0 | 0 | 0 | +0 | Sí |
| `eustat_poblacion_edad_normalizado.json` | 89424 | 89424 | +0 | 9 | 9 | +0 | 0 | 0 | +0 | Sí |
| `eustat_renta_edad_normalizado.json` | 6426 | 6426 | +0 | 8 | 8 | +0 | 0 | 0 | +0 | Sí |
| `eustat_renta_municipal_normalizado.json` | 98532 | 98532 | +0 | 8 | 8 | +0 | 0 | 0 | +0 | Sí |
| `eustat_tenencia_normalizado.json` | 4416 | 4416 | +0 | 6 | 6 | +0 | 0 | 0 | +0 | Sí |
| `f4_pisos_objetivo.json` | 40 | 40 | +0 | 1 | 1 | +0 | 0 | 0 | +0 | Sí |
| `ine_69301_normalizado.json` | 4407 | 4407 | +0 | 6 | 6 | +0 | 952 | 952 | +0 | Sí |
| `ine_69302_normalizado.json` | 2599 | 2599 | +0 | 6 | 6 | +0 | 90 | 90 | +0 | Sí |
| `ine_69303_normalizado.json` | 904 | 904 | +0 | 6 | 6 | +0 | 0 | 0 | +0 | Sí |
| `ine_69323_normalizado.json` | 1863 | 1863 | +0 | 6 | 6 | +0 | 804 | 804 | +0 | Sí |
| `ine_69330_normalizado.json` | 9999 | 9999 | +0 | 6 | 6 | +0 | 602 | 602 | +0 | Sí |
| `ine_atlas_renta_normalizado.json` | 252 | 252 | +0 | 5 | 5 | +0 | 0 | 0 | +0 | Sí |
| `ine_salarios_decil_normalizado.json` | 20 | 20 | +0 | 8 | 8 | +0 | 2 | 2 | +0 | Sí |
| `ine_salarios_edad_normalizado.json` | 198 | 198 | +0 | 8 | 8 | +0 | 6 | 6 | +0 | Sí |
| `informe_entity_resolution.csv` | 8 | 8 | +0 | 5 | 5 | +0 | 6 | 6 | +0 | Sí |
| `lanbide_paro_historico_joven_normalizado.json` | 29275 | 29275 | +0 | 18 | 18 | +0 | 255 | 255 | +0 | Sí |
| `lanbide_paro_juvenil_normalizado.json` | 252 | 252 | +0 | 12 | 12 | +0 | 0 | 0 | +0 | Sí |
| `municipios_gipuzkoa_lista_normalizado.json` | 126 | 126 | +0 | 4 | 4 | +0 | 0 | 0 | +0 | Sí |
| `osrm_tiempos_capitales_normalizado.json` | 252 | 252 | +0 | 4 | 4 | +0 | 0 | 0 | +0 | Sí |
| `renta_municipal_completa_normalizado.json` | 252 | 252 | +0 | 6 | 6 | +0 | 0 | 0 | +0 | Sí |
| `renta_municipal_referencia.csv` | 252 | 252 | +0 | 7 | 7 | +0 | 0 | 0 | +0 | Sí |
| `salud_centros_normalizado.json` | 528 | 528 | +0 | 12 | 12 | +0 | 0 | 0 | +0 | Sí |
| `serpavi_renta_municipal_normalizado.json` | 249 | 249 | +0 | 9 | 9 | +0 | 445 | 445 | +0 | Sí |
| `transporte_paradas_municipio_enriquecido.csv` | 252 | 252 | +0 | 7 | 7 | +0 | 303 | 303 | +0 | Sí |
| `transporte_paradas_municipio_normalizado.json` | 252 | 252 | +0 | 6 | 6 | +0 | 0 | 0 | +0 | Sí |
| `udalmap_empleo_corregido.csv` | 252 | 252 | +0 | 27 | 27 | +0 | 252 | 252 | +0 | Sí |
| `udalmap_empleo_corregido.json` | 252 | 252 | +0 | 27 | 27 | +0 | 252 | 252 | +0 | Sí |
| `udalmap_empleo_corregido_normalizado.json` | 252 | 252 | +0 | 27 | 27 | +0 | 252 | 252 | +0 | Sí |
| `udalmap_empleo_normalizado.json` | 252 | 252 | +0 | 24 | 24 | +0 | 252 | 252 | +0 | Sí |
| `udalmap_indicadores_adicionales_normalizado.json` | 252 | 252 | +0 | 34 | 34 | +0 | 0 | 0 | +0 | Sí |

## 5. Regresiones detectadas

- (ninguna regresión por filas/columnas/nulos)

## 6. Mejoras detectadas

- (ninguna mejora por filas/columnas/nulos)

## 7. Cambios de columnas (faltantes/sobrantes)

- (sin cambios de columnas en ningún archivo)

## 8. Cambios de nulos por columna (solo diferencias)

- (sin cambios en conteo de nulos por columna)

## 9. Archivos con mismas dimensiones/columnas pero valores no idénticos

- (ninguno)

## 10. Archivos no idénticos por cambio de estructura

- Total: 0

## 10b. Conteo de nulos por columna (archivos con nulos)

Se listan solo columnas con nulos (>0); el conteo es idéntico en backup y actual (sin diferencias).

### `alquiler_seccion.csv`
- `territorio`: 1569

### `anuncios_fotocasa_detalle_normalizado.json`
- `antiguedad_cod`: 3
- `cert_energetico`: 3
- `banos_detalle`: 3
- `fecha_publicacion_detalle`: 3
- `distrito_detalle`: 114
- `es_temporal_detalle`: 3

### `anuncios_fotocasa_enriquecido.csv`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `precio_eur`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `ascensor`: 152
- `parking`: 383
- `terraza`: 329
- `trastero`: 432

### `anuncios_fotocasa_enriquecido.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1
- `nombre_canonico_resuelto`: 471

### `anuncios_fotocasa_enriquecido_geo_normalizado.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1

### `anuncios_fotocasa_enriquecido_meta_normalizado.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1

### `anuncios_fotocasa_enriquecido_normalizado.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1

### `anuncios_fotocasa_filtrado.csv`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1
- `precio_m2_calculado`: 10
- `motivo_outlier`: 451

### `anuncios_fotocasa_filtrado.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1
- `precio_m2_calculado`: 10

### `anuncios_fotocasa_geo_normalizado.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1

### `anuncios_fotocasa_habitaciones_geo_normalizado.json`
- `precio_eur`: 1
- `precio_reducido_eur`: 134
- `precio_texto`: 1
- `barrio`: 75
- `distrito`: 3
- `superficie_m2`: 22
- `habitaciones`: 5
- `banos`: 20
- `calefaccion`: 67
- `parking`: 155
- `ascensor`: 16
- `terraza`: 37
- `trastero`: 152
- `jardin`: 155

### `anuncios_fotocasa_habitaciones_meta_normalizado.json`
- `precio_eur`: 1
- `precio_reducido_eur`: 134
- `precio_texto`: 1
- `barrio`: 75
- `distrito`: 3
- `superficie_m2`: 22
- `habitaciones`: 5
- `banos`: 20
- `calefaccion`: 67
- `parking`: 155
- `ascensor`: 16
- `terraza`: 37
- `trastero`: 152
- `jardin`: 155

### `anuncios_fotocasa_habitaciones_normalizado.json`
- `precio_eur`: 1
- `precio_reducido_eur`: 134
- `precio_texto`: 1
- `barrio`: 75
- `distrito`: 3
- `superficie_m2`: 22
- `habitaciones`: 5
- `banos`: 20
- `calefaccion`: 67
- `parking`: 155
- `ascensor`: 16
- `terraza`: 37
- `trastero`: 152
- `jardin`: 155

### `anuncios_fotocasa_meta_normalizado.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1

### `anuncios_fotocasa_normalizado.json`
- `codigo_ine`: 2
- `nombre_canonico`: 2
- `uuid_anuncio`: 18
- `precio_eur`: 8
- `precio_reducido_eur`: 419
- `precio_texto`: 8
- `barrio`: 237
- `distrito`: 114
- `superficie_m2`: 4
- `habitaciones`: 13
- `banos`: 17
- `calefaccion`: 142
- `parking`: 383
- `ascensor`: 152
- `terraza`: 329
- `trastero`: 432
- `jardin`: 429
- `descripcion`: 1

### `anuncios_pisos_dirigido.csv`
- `nombre_canonico`: 218
- `precio_eur`: 29
- `tipo_inmueble`: 248
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8

### `anuncios_pisos_dirigido.json`
- `precio_eur`: 29
- `tipo_inmueble`: 248
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 33
- `ubicacion`: 21
- `equipamiento`: 21
- `nombre_canonico`: 218

### `anuncios_pisos_enriquecido.csv`
- `precio_eur`: 22
- `tipo_inmueble`: 232
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 17
- `ubicacion`: 5
- `equipamiento`: 5

### `anuncios_pisos_enriquecido.json`
- `precio_eur`: 22
- `tipo_inmueble`: 232
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 17
- `ubicacion`: 5
- `equipamiento`: 5
- `nombre_canonico`: 218

### `anuncios_pisos_enriquecido_geo_normalizado.json`
- `precio_eur`: 22
- `tipo_inmueble`: 227
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 12
- `nombre_canonico`: 218

### `anuncios_pisos_enriquecido_meta_normalizado.json`
- `precio_eur`: 22
- `tipo_inmueble`: 227
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 12
- `nombre_canonico`: 218

### `anuncios_pisos_enriquecido_normalizado.json`
- `precio_eur`: 22
- `tipo_inmueble`: 227
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 12
- `nombre_canonico`: 218

### `anuncios_pisos_filtrado.csv`
- `precio_eur`: 22
- `tipo_inmueble`: 232
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 17
- `ubicacion`: 5
- `equipamiento`: 5
- `precio_m2_calculado`: 28
- `motivo_outlier`: 225

### `anuncios_pisos_filtrado.json`
- `precio_eur`: 22
- `tipo_inmueble`: 232
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 17
- `ubicacion`: 5
- `equipamiento`: 5
- `precio_m2_calculado`: 28
- `nombre_canonico`: 218

### `anuncios_pisos_geo_normalizado.json`
- `precio_eur`: 22
- `tipo_inmueble`: 227
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 12
- `nombre_canonico`: 218

### `anuncios_pisos_habitaciones_geo_normalizado.json`
- `tipo_inmueble`: 46
- `superficie_m2`: 46
- `habitaciones`: 46
- `banos`: 46
- `total_resultados`: 2

### `anuncios_pisos_habitaciones_meta_normalizado.json`
- `tipo_inmueble`: 46
- `superficie_m2`: 46
- `habitaciones`: 46
- `banos`: 46
- `total_resultados`: 2

### `anuncios_pisos_habitaciones_normalizado.json`
- `tipo_inmueble`: 46
- `superficie_m2`: 46
- `habitaciones`: 46
- `banos`: 46
- `total_resultados`: 2

### `anuncios_pisos_meta_normalizado.json`
- `precio_eur`: 22
- `tipo_inmueble`: 227
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 12
- `nombre_canonico`: 218

### `anuncios_pisos_normalizado.json`
- `precio_eur`: 22
- `tipo_inmueble`: 232
- `superficie_m2`: 6
- `habitaciones`: 8
- `banos`: 8
- `nombre_canonico_resuelto`: 17
- `ubicacion`: 5
- `equipamiento`: 5
- `nombre_canonico`: 218

### `anuncios_realtyapi_enriquecido.csv`
- `barrio`: 65
- `planta`: 6
- `exterior`: 8

### `anuncios_realtyapi_enriquecido.json`
- `tipo_extendido`: 139
- `planta`: 6
- `exterior`: 8
- `barrio`: 65
- `descripcion`: 2

### `anuncios_realtyapi_normalizado.json`
- `tipo_extendido`: 139
- `planta`: 6
- `exterior`: 8
- `barrio`: 65
- `descripcion`: 2

### `anuncios_unificados.csv`
- `precio_eur`: 30
- `superficie_m2`: 10
- `codigo_ine`: 2
- `equipamiento`: 706

### `anuncios_unificados.json`
- `precio_eur`: 30
- `superficie_m2`: 10
- `habitaciones`: 21
- `banos`: 25

### `b5m_catalogo_normalizado.json`
- `metadata_link`: 4
- `map_link`: 29
- `table_link`: 29
- `inspire_services`: 19

### `ecvi_compraventa_limpio.csv`
- `codigo_ine`: 22
- `precio_m2_usada_eur`: 29

### `ecvi_compraventa_limpio.json`
- `codigo_ine`: 22
- `precio_m2_usada_eur`: 29

### `emal_fianzas_ampliado_normalizado.json`
- `fianzas`: 2
- `renta_media_eur_mes`: 20
- `renta_media_eur_m2_mes`: 20
- `alquileres_vigentes_2024`: 10
- `alquileres_vigentes_2025`: 10
- `n_muestral`: 2

### `emal_fianzas_normalizado.json`
- `fianzas`: 2
- `renta_media_eur_mes`: 20
- `renta_media_eur_m2_mes`: 20
- `alquileres_vigentes_2024`: 10
- `alquileres_vigentes_2025`: 10

### `etxebide_solicitudes_normalizado.json`
- `etxebide_solicitudes_por_mil`: 1

### `eustat_demografia_renta_252.csv`
- `poblacion_joven_15_29`: 252

### `eustat_demografia_renta_252.json`
- `poblacion_joven_15_29`: 252

### `ine_69301_normalizado.json`
- `anyo`: 476
- `valor`: 476

### `ine_69302_normalizado.json`
- `anyo`: 45
- `valor`: 45

### `ine_69323_normalizado.json`
- `anyo`: 402
- `valor`: 402

### `ine_69330_normalizado.json`
- `anyo`: 301
- `valor`: 301

### `ine_salarios_decil_normalizado.json`
- `anyo`: 1
- `valor_eur`: 1

### `ine_salarios_edad_normalizado.json`
- `anyo`: 3
- `valor_eur`: 3

### `informe_entity_resolution.csv`
- `no_resueltos`: 6

### `lanbide_paro_historico_joven_normalizado.json`
- `municipio`: 251
- `tasa_paro_joven_ratio_pct`: 4

### `serpavi_renta_municipal_normalizado.json`
- `renta_m2_mes_eur`: 89
- `anio_renta`: 89
- `n_declaraciones`: 89
- `renta_m2_p25`: 89
- `renta_m2_p75`: 89

### `transporte_paradas_municipio_enriquecido.csv`
- `operadores`: 51
- `paradas_por_1000_hab`: 252

### `udalmap_empleo_corregido.csv`
- `tasa_paro_aprox_pct`: 252

### `udalmap_empleo_corregido.json`
- `tasa_paro_aprox_pct`: 252

### `udalmap_empleo_corregido_normalizado.json`
- `tasa_paro_aprox_pct`: 252

### `udalmap_empleo_normalizado.json`
- `tasa_paro_aprox_pct`: 252

## 11. Notas metodológicas

- Comparación realizada leyendo CSV con pandas (utf-8/latin-1) y JSON extrayendo la clave `datos` cuando existe; listas de dicts se convierten a DataFrame.
- `NaN`/None se consideran nulos. Igualdad de valores: comparación celda a celda considerando NaN en la misma posición como iguales.
- No se modificaron archivos; solo lectura.
- Archivos no tabulares (logs, geojson, resúmenes) se omitieron del análisis tabular.
