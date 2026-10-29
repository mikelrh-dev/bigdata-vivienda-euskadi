# Trazabilidad de datos — Fase 1 + Tier2/Tier3

> Actualizado 2026-10-29.  
> Referencia: `docs/inventario_datos.md` (inventario de 302 archivos crudos en `data/raw/` y 93 en `data/procesado/`) y `docs/plan_gestion_datos_fase1.md`.

## Transformaciones ejecutadas

### Fase 1 (originales)

| Tarea | Script | Entrada (origen) | Salida (destino) | Filas | Motivo |
|---|---|---|---|---|---|
| 1.1 Normalizar `codigo_ine` | `transform/normalizar_json_crudos.py` | `data/raw/*.json` (47) | `data/procesado/*_normalizado.json` (47) | — | Forzar `str.zfill(5)` en `codigo_ine` raíz y `ubicacion.codigo_ine`; eliminar `None`. |
| 1.2 Limpiar ECVI | `transform/limpiar_ecvi.py` | `data/raw/ecvi_ecvi_es_2026t2_t{1,2,3}_{2,3}.csv` (6) | `data/procesado/ecvi_compraventa_limpio.json` + `.csv` | 29 | Parser de cabeceras múltiples → columnas nombradas (territorio, área funcional, municipio). |
| 1.3 Desglosar Eustat | `transform/limpiar_eustat_demografia.py` | `data/raw/eustat_renta_municipal.csv`, `eustat_poblacion_edad.csv` | `data/procesado/eustat_demografia_renta_252.json` + `.csv` | 252 | Renta personal (ambos/hombres/mujeres), renta disponible, población total, año. `poblacion_joven_15_29` = null (no disponible en fuente). |
| 1.4 Unificar anuncios | `transform/unificar_anuncios.py` | `anuncios_fotocasa_enriquecido_geo.json`, `anuncios_pisos_enriquecido_geo.json`, `anuncios_realtyapi.json` | `data/procesado/anuncios_unificados.json` + `.csv` | 840 | Esquema único: `ubicacion` anidada + `equipamiento` array + `auditoria`. |

### Tier2 / Tier3 (nuevos)

| Tarea | Script | Entrada (origen) | Salida (destino) | Filas | Motivo |
|---|---|---|---|---|---|
| Geo áreas funcionales | `extract/22_geo_areas_funcionales.py` | Shapefile `AREAS_FUNCIONALES_5000_ETRS89` + `data/raw/municipios_euskadi.geojson` | `data/raw/areas_funcionales_municipios.csv` | 252 | Correspondencia municipio → área funcional por point-in-polygon (centroide). |
| Mapeo ECVI | `transform/asignar_area_funcional_ecvi.py` | `data/raw/areas_funcionales_municipios.csv` + `data/procesado/ecvi_compraventa_limpio.csv` | `data/procesado/municipio_area_funcional_ecvi.csv` | 252 | Cruce municipio → área funcional con ECVI compraventa (precio medio total/m²). |
| Población joven municipal | `transform/generar_poblacion_joven_municipal.py` | `data/raw/eustat_poblacion_edad.csv` | `data/procesado/poblacion_joven_municipal.csv` | 252 | Estimación transparente de población 15-29 (0.25×(0-19)+0.222×(20-64)). |
| Municipios faltantes 93 | `transform/generar_municipios_faltantes_93.py` | `data/procesado/alquiler_municipal_completo.csv` + `dim_municipios.csv` + `data/raw/eustat_poblacion_edad.csv` | `data/procesado/municipios_faltantes_93.csv` | 93 | Identifica municipios sin alquiler directo con territorio, población y tipología. |
| Análisis variables base | `transform/generar_analisis_variables_base.py` | `dim_municipios.csv` + `renta_municipal_completa.csv` + `alquiler_municipal_completo.csv` + `distancias_capitales_252.csv` + `udalmap_empleo_corregido.csv` | `data/procesado/analisis_variables_base.csv` | 252 | Merge de variables base y cálculo de esfuerzo (hogar, Eustat, joven). |
| Emancipación Tier3 (93) | `transform/generar_emancipacion_tier3_93.py` | `municipios_faltantes_93.csv` + Udalmap/renta/OSRM/transporte/educación/salud/dim | `data/procesado/emancipacion_tier3_93.csv` | 93 | Clasificación Tier3: no_emancipa / compra_commuting / desierto. |

## Micro-tareas Fase 1.5 (ejecutadas)

| Tarea | Script | Entrada | Salida | Impacto |
|---|---|---|---|---|
| A. Verificar udalmap JSON | (verificación) | `udalmap_empleo_corregido.json`, `udalmap_indicadores_adicionales.json` | — | C6/C2/C3/E1-E3/B6: datos ya presentes en JSON normalizado |
| B. Enriquecer GTFS | `transform/enriquecer_gtfs_conectividad.py` | 13 ZIPs en `data/raw/gtfs/` + `municipios_euskadi.geojson` | `data/procesado/transporte_paradas_municipio_enriquecido.csv` (252) | D2: 6→9 |
| C. Enriquecer equipamiento RealtyAPI | `transform/enriquecer_equipamiento_realtyapi.py` | `anuncios_unificados.json` + `anuncios_realtyapi.json` | `anuncios_unificados.json` + `.csv` actualizados | C4/C5: parcial (139/840) |

## Quick wins silver (post-Tier2/Tier3)

| Tarea | Script / Comando | Entrada | Salida | Impacto |
|---|---|---|---|---|
| paradas_por_1000_hab | inline Python | `transporte_paradas_municipio_enriquecido.csv` + `eustat_demografia_renta_252.csv` | `transporte_paradas_municipio_enriquecido.csv` (252, 0 nulos) | D2: 6→9 (paradas_por_1000_hab derivado) |
| Fingerprint duplicados | `transform/generar_fingerprint.py` | `anuncios_unificados.json` (840) | `anuncios_unificados.csv` (840, 727 únicos, 113 duplicados = 13.45%) | trazabilidad de duplicados |
| Cert energético moda | inline Python | `anuncios_fotocasa_detalle.json` (470, 3 nulos) | `cert_energetico_moda_municipio.csv` (60 municipios) | C5: 6→7 (parcial) |

## Relación con inventario de datos

- `docs/inventario_datos.md` inventaria los **303 archivos crudos** en `data/raw/` y **94 archivos** en `data/procesado/`.
- `data/raw/` no se modificó (solo lectura); la única adición raw nueva es `areas_funcionales_municipios.csv` y `ovj_salario_joven_2024.json` (añadidos sin modificar existentes).
- Tras Tier2/Tier3 + quick wins, `data/procesado/` contiene los derivados listados arriba + `cert_energetico_moda_municipio.csv`.

## Certificados energéticos (Open Data Euskadi) — nuevo (2026-10-29)

- `extract/23_certificados_energeticos.py` → descarga 6 CSVs (3 territoriales + 3 ciudades) de certificados de eficiencia energética.
- `transform/generar_cert_energetico_municipal.py` → agrega por municipio: moda + distribución A-G. **252/252 municipios con datos reales** (antes 60/252 con moda de anuncios).
- Raw: `certificados_energeticos_{araba,bizkaia,gipuzkoa,bilbao,donostia,vitoria}_completo.csv` (9 archivos incluyendo v2).
- Procesado: `cert_energetico_municipal_252.csv` (252×11).
- Fuente: Open Data Euskadi (registro oficial de certificados de eficiencia energética).
- Impacto: C5 sube de 7 a 8 (de proxy a dato real por municipio).

## Limitaciones documentadas actualizadas

- `poblacion_joven_15_29` queda null en Eustat (solo grupos 0-19, 20-64, ≥65); se estima en `poblacion_joven_municipal.csv`.
- ECVI solo cubre territorios, áreas funcionales y 7 municipios >40k hab.
- Anuncios unificados: solo Fotocasa tiene `equipamiento` array; Pisos/RealtyAPI vacío.
- Modalidad inferida por heurística (temporal si `alquiler_temporal`=true, habitación si tipo contiene "habitación", resto larga_estancia).
- Cert. energético: ahora 252/252 municipios con distribución real (antes 60/252 con moda de anuncios).
- Estimación de población 15-29 es aproximación, no dato real.
- `operadores` en transporte: 51 nulos (municipios sin operador GTFS registrado).
- Cert energético: solo 60 municipios con moda (de 470 anuncios Fotocasa, 3 nulos cert).
