# Auditoria de datos con DuckDB
**Fecha:** generada automaticamente
**Directorio:** data/procesado/

## 1. Inventario de archivos
| Archivo | Filas | Columnas |
|---|---|---|
| alquiler_municipal_completo.csv | 252 | 19 |
| alquiler_municipal_enriquecido.csv | 252 | 18 |
| alquiler_seccion.csv | 1569 | 19 |
| alquiler_seccion_resumen.csv | 159 | 6 |
| analisis_variables_base.csv | 252 | 38 |
| anuncios_fotocasa_enriquecido.csv | 471 | 26 |
| anuncios_fotocasa_filtrado.csv | 471 | 42 |
| anuncios_habitaciones_unificados.csv | 201 | 9 |
| anuncios_pisos_dirigido.csv | 263 | 15 |
| anuncios_pisos_enriquecido.csv | 235 | 19 |
| anuncios_pisos_filtrado.csv | 235 | 24 |
| anuncios_realtyapi_enriquecido.csv | 139 | 17 |
| anuncios_unificados.csv | 759 | 13 |
| anuncios_vivienda_residencial.csv | 570 | 14 |
| anuncios_vivienda_residencial_filtrado.csv | 570 | 19 |
| cert_energetico_moda_municipio.csv | 252 | 2 |
| cert_energetico_municipal_252.csv | 252 | 11 |
| comparativa_compra_alquiler_af.csv | 15 | 7 |
| dim_municipios.csv | 252 | 9 |
| dim_municipios_enriquecido.csv | 252 | 65 |
| distancias_capitales_252.csv | 252 | 11 |
| distancias_haversine_252.csv | 63504 | 3 |
| ecvi_compraventa_limpio.csv | 29 | 7 |
| emancipacion_tier3_93.csv | 93 | 15 |
| eustat_demografia_renta_252.csv | 252 | 9 |
| f4_pisos_informe.csv | 62 | 3 |
| fotocasa_dirigido_informe.csv | 62 | 3 |
| informe_entity_resolution.csv | 8 | 5 |
| municipio_area_funcional_ecvi.csv | 252 | 9 |
| municipios_faltantes_93.csv | 93 | 5 |
| poblacion_joven_municipal.csv | 252 | 5 |
| renta_municipal_referencia.csv | 252 | 7 |
| transporte_paradas_municipio_enriquecido.csv | 252 | 7 |
| udalmap_empleo_corregido.csv | 252 | 26 |

Total: 34 archivos

## 2. Nulos por archivo (columnas con nulos)
### alquiler_municipal_completo.csv
- `idw_vecinos`: 159 nulos

### analisis_variables_base.csv
- `tasa_desempleo_juvenil_real_pct`: 53 nulos

### anuncios_fotocasa_enriquecido.csv
- `trastero`: 432 nulos
- `parking`: 383 nulos
- `terraza`: 329 nulos
- `barrio`: 237 nulos
- `ascensor`: 152 nulos
- `distrito`: 114 nulos
- `banos`: 17 nulos
- `habitaciones`: 13 nulos
- `precio_eur`: 8 nulos
- `superficie_m2`: 4 nulos

### anuncios_fotocasa_filtrado.csv
- `motivo_outlier`: 451 nulos
- `trastero`: 432 nulos
- `jardin`: 429 nulos
- `precio_reducido_eur`: 419 nulos
- `parking`: 383 nulos
- `terraza`: 329 nulos
- `barrio`: 237 nulos
- `ascensor`: 152 nulos
- `calefaccion`: 142 nulos
- `distrito`: 114 nulos

### anuncios_habitaciones_unificados.csv
- `titulo`: 155 nulos
- `subtitulo`: 155 nulos
- `superficie_m2`: 68 nulos
- `habitaciones`: 51 nulos
- `precio_eur`: 1 nulos

### anuncios_pisos_dirigido.csv
- `tipo_inmueble`: 260 nulos
- `nombre_canonico`: 218 nulos
- `precio_eur`: 32 nulos
- `habitaciones`: 9 nulos
- `banos`: 8 nulos
- `superficie_m2`: 6 nulos

### anuncios_pisos_enriquecido.csv
- `tipo_inmueble`: 232 nulos
- `precio_eur`: 22 nulos
- `nombre_canonico_resuelto`: 17 nulos
- `habitaciones`: 8 nulos
- `banos`: 8 nulos
- `superficie_m2`: 6 nulos
- `ubicacion`: 5 nulos
- `equipamiento`: 5 nulos

### anuncios_pisos_filtrado.csv
- `tipo_inmueble`: 232 nulos
- `motivo_outlier`: 225 nulos
- `precio_m2_calculado`: 28 nulos
- `precio_eur`: 22 nulos
- `nombre_canonico_resuelto`: 17 nulos
- `habitaciones`: 8 nulos
- `banos`: 8 nulos
- `superficie_m2`: 6 nulos
- `ubicacion`: 5 nulos
- `equipamiento`: 5 nulos

### anuncios_realtyapi_enriquecido.csv
- `barrio`: 65 nulos
- `exterior`: 8 nulos
- `planta`: 6 nulos

### anuncios_unificados.csv
- `equipamiento`: 759 nulos
- `titulo`: 512 nulos
- `subtitulo`: 512 nulos
- `precio_eur`: 37 nulos
- `habitaciones`: 22 nulos
- `superficie_m2`: 10 nulos

### anuncios_vivienda_residencial.csv
- `banos`: 570 nulos
- `url_detalle`: 570 nulos
- `titulo`: 309 nulos
- `subtitulo`: 309 nulos
- `precio_eur`: 36 nulos
- `habitaciones`: 19 nulos
- `superficie_m2`: 7 nulos

### anuncios_vivienda_residencial_filtrado.csv
- `banos`: 570 nulos
- `url_detalle`: 570 nulos
- `motivo_outlier`: 554 nulos
- `titulo`: 309 nulos
- `subtitulo`: 309 nulos
- `precio_m2_calculado`: 42 nulos
- `precio_eur`: 36 nulos
- `habitaciones`: 19 nulos
- `superficie_m2`: 7 nulos

### dim_municipios_enriquecido.csv
- `tasa_desempleo_juvenil_real_pct`: 53 nulos

### ecvi_compraventa_limpio.csv
- `precio_m2_usada_eur`: 29 nulos
- `codigo_ine`: 22 nulos

### emancipacion_tier3_93.csv
- `alquiler_eur_m2`: 93 nulos

### eustat_demografia_renta_252.csv
- `poblacion_joven_15_29`: 252 nulos

### informe_entity_resolution.csv
- `no_resueltos`: 6 nulos

### municipio_area_funcional_ecvi.csv
- `precio_m2_usada_eur`: 252 nulos

### transporte_paradas_municipio_enriquecido.csv
- `operadores`: 51 nulos

## 3. Duplicados por clave
- `alquiler_municipal_enriquecido.csv` / `codigo_ine`: 93 duplicados
- `alquiler_municipal_enriquecido.csv` / `municipio`: 93 duplicados
- `alquiler_seccion.csv` / `codigo_ine`: 1410 duplicados
- `alquiler_seccion.csv` / `municipio`: 1410 duplicados
- `anuncios_fotocasa_enriquecido.csv` / `codigo_ine`: 410 duplicados
- `anuncios_fotocasa_enriquecido.csv` / `municipio`: 410 duplicados
- `anuncios_fotocasa_filtrado.csv` / `codigo_ine`: 410 duplicados
- `anuncios_fotocasa_filtrado.csv` / `municipio`: 410 duplicados
- `anuncios_habitaciones_unificados.csv` / `codigo_ine`: 192 duplicados
- `anuncios_habitaciones_unificados.csv` / `municipio`: 190 duplicados
- `anuncios_pisos_dirigido.csv` / `codigo_ine`: 222 duplicados
- `anuncios_pisos_enriquecido.csv` / `codigo_ine`: 198 duplicados
- `anuncios_pisos_filtrado.csv` / `codigo_ine`: 198 duplicados
- `anuncios_realtyapi_enriquecido.csv` / `codigo_ine`: 136 duplicados
- `anuncios_realtyapi_enriquecido.csv` / `municipio`: 136 duplicados
- `anuncios_unificados.csv` / `codigo_ine`: 676 duplicados
- `anuncios_unificados.csv` / `municipio`: 676 duplicados
- `anuncios_vivienda_residencial.csv` / `codigo_ine`: 494 duplicados
- `anuncios_vivienda_residencial.csv` / `municipio`: 494 duplicados
- `anuncios_vivienda_residencial_filtrado.csv` / `codigo_ine`: 494 duplicados
- `anuncios_vivienda_residencial_filtrado.csv` / `municipio`: 494 duplicados
- `ecvi_compraventa_limpio.csv` / `codigo_ine`: 21 duplicados

## 4. Rangos de variables clave
| Archivo | Columna | Min | Max | Media |
|---|---|---|---|---|
| alquiler_municipal_completo.csv | cuantia_media_eur_mes_media | 386.0 | 1051.0 | 594.44 |
| alquiler_municipal_enriquecido.csv | cuantia_media_eur_mes_media | 386.0 | 1224.0 | 651.94 |
| alquiler_seccion.csv | cuantia_media_eur_mes_media | 386.0 | 1737.0 | 758.64 |
| analisis_variables_base.csv | renta_personal_total_eur | 11939.0 | 40243.0 | 26118.42 |
| analisis_variables_base.csv | cuantia_media_eur_mes_media | 386.0 | 1051.0 | 594.44 |
| analisis_variables_base.csv | dist_centroide_comarca_km | 0.7 | 24.64 | 7.45 |
| anuncios_fotocasa_enriquecido.csv | precio_eur | 80 | 8500 | 1669.68 |
| anuncios_fotocasa_enriquecido.csv | superficie_m2 | 1 | 6973 | 116.34 |
| anuncios_fotocasa_filtrado.csv | precio_eur | 80 | 8500 | 1669.68 |
| anuncios_fotocasa_filtrado.csv | superficie_m2 | 1 | 6973 | 116.34 |
| anuncios_habitaciones_unificados.csv | precio_eur | 240 | 109000 | 1514.13 |
| anuncios_habitaciones_unificados.csv | superficie_m2 | 1 | 322 | 109.8 |
| anuncios_pisos_dirigido.csv | precio_eur | 150 | 9500 | 1532.04 |
| anuncios_pisos_dirigido.csv | superficie_m2 | 22 | 910 | 107.91 |
| anuncios_pisos_enriquecido.csv | precio_eur | 150.0 | 9500.0 | 1536.38 |
| anuncios_pisos_enriquecido.csv | superficie_m2 | 22.0 | 910.0 | 111.68 |
| anuncios_pisos_filtrado.csv | precio_eur | 150 | 9500 | 1536.38 |
| anuncios_pisos_filtrado.csv | superficie_m2 | 22 | 910 | 111.68 |
| anuncios_realtyapi_enriquecido.csv | precio_eur | 680.0 | 9500.0 | 1946.91 |
| anuncios_realtyapi_enriquecido.csv | superficie_m2 | 16.0 | 356.0 | 99.06 |
| anuncios_unificados.csv | precio_eur | 80.0 | 9500.0 | 1697.83 |
| anuncios_unificados.csv | superficie_m2 | 16.0 | 6973.0 | 114.25 |
| anuncios_vivienda_residencial.csv | precio_eur | 150.0 | 9500.0 | 1677.42 |
| anuncios_vivienda_residencial.csv | superficie_m2 | 16.0 | 6973.0 | 121.42 |
| anuncios_vivienda_residencial_filtrado.csv | precio_eur | 150.0 | 9500.0 | 1677.42 |
| anuncios_vivienda_residencial_filtrado.csv | superficie_m2 | 16.0 | 6973.0 | 121.42 |
| dim_municipios_enriquecido.csv | renta_personal_total_eur | 11939.0 | 40243.0 | 26118.42 |
| dim_municipios_enriquecido.csv | cuantia_media_eur_mes_media | 386.0 | 1051.0 | 594.44 |
| dim_municipios_enriquecido.csv | esfuerzo_min_pct | 26.994060300217537 | 66.2393268723856 | 41.48 |
| dim_municipios_enriquecido.csv | esfuerzo_max_pct | 50.893168066683906 | 124.88410997263595 | 78.2 |
| dim_municipios_enriquecido.csv | dist_centroide_comarca_km | 0.7 | 24.64 | 7.45 |
| distancias_capitales_252.csv | dist_centroide_comarca_km | 0.7 | 24.64 | 7.46 |
| emancipacion_tier3_93.csv | n_paradas | 0 | 22 | 2.84 |
| transporte_paradas_municipio_enriquecido.csv | n_paradas | 0 | 857 | 22.88 |
| transporte_paradas_municipio_enriquecido.csv | paradas_por_1000_hab | 0.0 | 70.06 | 8.78 |
| udalmap_empleo_corregido.csv | renta_personal_total_eur | 11939.0 | 40243.0 | 26118.42 |

## 5. Consistencia entre archivos (joins por codigo_ine)
Base: `analisis_variables_base.csv` = 252 municipios

- `alquiler_municipal_completo.csv`: 252/252 municipios coinciden (252 filas)
- `alquiler_municipal_enriquecido.csv`: 159/252 municipios coinciden (252 filas)
- `alquiler_seccion.csv`: 159/252 municipios coinciden (1569 filas)
- `alquiler_seccion_resumen.csv`: 159/252 municipios coinciden (159 filas)
- `anuncios_fotocasa_enriquecido.csv`: 60/252 municipios coinciden (471 filas)
- `anuncios_fotocasa_filtrado.csv`: 60/252 municipios coinciden (471 filas)
- `anuncios_habitaciones_unificados.csv`: 9/252 municipios coinciden (201 filas)
- `anuncios_pisos_dirigido.csv`: 41/252 municipios coinciden (263 filas)
- `anuncios_pisos_enriquecido.csv`: 37/252 municipios coinciden (235 filas)
- `anuncios_pisos_filtrado.csv`: 37/252 municipios coinciden (235 filas)
- `anuncios_realtyapi_enriquecido.csv`: 3/252 municipios coinciden (139 filas)
- `anuncios_unificados.csv`: 83/252 municipios coinciden (759 filas)
- `anuncios_vivienda_residencial.csv`: 76/252 municipios coinciden (570 filas)
- `anuncios_vivienda_residencial_filtrado.csv`: 76/252 municipios coinciden (570 filas)
- `cert_energetico_moda_municipio.csv`: 252/252 municipios coinciden (252 filas)
- `cert_energetico_municipal_252.csv`: 252/252 municipios coinciden (252 filas)
- `dim_municipios.csv`: 252/252 municipios coinciden (252 filas)
- `dim_municipios_enriquecido.csv`: 252/252 municipios coinciden (252 filas)
- `distancias_capitales_252.csv`: 252/252 municipios coinciden (252 filas)
- `ecvi_compraventa_limpio.csv`: 0/252 municipios coinciden (29 filas)
- `emancipacion_tier3_93.csv`: 93/252 municipios coinciden (93 filas)
- `eustat_demografia_renta_252.csv`: 252/252 municipios coinciden (252 filas)
- `f4_pisos_informe.csv`: 62/252 municipios coinciden (62 filas)
- `fotocasa_dirigido_informe.csv`: 62/252 municipios coinciden (62 filas)
- `municipio_area_funcional_ecvi.csv`: 252/252 municipios coinciden (252 filas)
- `municipios_faltantes_93.csv`: 93/252 municipios coinciden (93 filas)
- `poblacion_joven_municipal.csv`: 252/252 municipios coinciden (252 filas)
- `renta_municipal_referencia.csv`: 252/252 municipios coinciden (252 filas)
- `transporte_paradas_municipio_enriquecido.csv`: 252/252 municipios coinciden (252 filas)
- `udalmap_empleo_corregido.csv`: 252/252 municipios coinciden (252 filas)

## 6. Outliers (>3 sigma) en variables clave
- `alquiler_municipal_completo.csv` / `cuantia_media_eur_mes_media`: 3 outliers (min=386.0, max=1051.0)
- `alquiler_municipal_enriquecido.csv` / `cuantia_media_eur_mes_media`: 6 outliers (min=386.0, max=1224.0)
- `alquiler_seccion.csv` / `cuantia_media_eur_mes_media`: 17 outliers (min=386.0, max=1737.0)
- `analisis_variables_base.csv` / `renta_personal_total_eur`: 4 outliers (min=11939.0, max=40243.0)
- `analisis_variables_base.csv` / `cuantia_media_eur_mes_media`: 3 outliers (min=386.0, max=1051.0)
- `analisis_variables_base.csv` / `dist_centroide_comarca_km`: 4 outliers (min=0.7, max=24.64)
- `anuncios_pisos_enriquecido.csv` / `precio_eur`: 3 outliers (min=150.0, max=9500.0)
- `anuncios_pisos_enriquecido.csv` / `superficie_m2`: 2 outliers (min=22.0, max=910.0)
- `anuncios_realtyapi_enriquecido.csv` / `precio_eur`: 5 outliers (min=680.0, max=9500.0)
- `anuncios_realtyapi_enriquecido.csv` / `superficie_m2`: 4 outliers (min=16.0, max=356.0)
- `anuncios_unificados.csv` / `precio_eur`: 15 outliers (min=80.0, max=9500.0)
- `anuncios_unificados.csv` / `superficie_m2`: 3 outliers (min=16.0, max=6973.0)
- `anuncios_vivienda_residencial.csv` / `precio_eur`: 12 outliers (min=150.0, max=9500.0)
- `anuncios_vivienda_residencial.csv` / `superficie_m2`: 2 outliers (min=16.0, max=6973.0)
- `anuncios_vivienda_residencial_filtrado.csv` / `precio_eur`: 12 outliers (min=150.0, max=9500.0)
- `anuncios_vivienda_residencial_filtrado.csv` / `superficie_m2`: 2 outliers (min=16.0, max=6973.0)
- `dim_municipios_enriquecido.csv` / `renta_personal_total_eur`: 4 outliers (min=11939.0, max=40243.0)
- `dim_municipios_enriquecido.csv` / `cuantia_media_eur_mes_media`: 3 outliers (min=386.0, max=1051.0)
- `dim_municipios_enriquecido.csv` / `esfuerzo_min_pct`: 1 outliers (min=26.994060300217537, max=66.2393268723856)
- `dim_municipios_enriquecido.csv` / `esfuerzo_max_pct`: 1 outliers (min=50.893168066683906, max=124.88410997263595)
- `dim_municipios_enriquecido.csv` / `dist_centroide_comarca_km`: 4 outliers (min=0.7, max=24.64)
- `distancias_capitales_252.csv` / `dist_centroide_comarca_km`: 4 outliers (min=0.7, max=24.64)
- `emancipacion_tier3_93.csv` / `n_paradas`: 2 outliers (min=0, max=22)
- `transporte_paradas_municipio_enriquecido.csv` / `n_paradas`: 3 outliers (min=0, max=857)
- `transporte_paradas_municipio_enriquecido.csv` / `paradas_por_1000_hab`: 5 outliers (min=0.0, max=70.06)
- `udalmap_empleo_corregido.csv` / `renta_personal_total_eur`: 4 outliers (min=11939.0, max=40243.0)

## 7. Resumen
- Archivos auditados: 34
- Generado con DuckDB (sin cargar en RAM)
- Regenerable: `python transform/auditoria_duckdb.py`
