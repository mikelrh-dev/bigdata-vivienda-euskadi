# Plan de auditoría v5 — Anexo de barridos exhaustivos

**Fecha:** 2026-11-07
**Padre:** `plan_auditoria_v5_2026-11-07.md`
**Contenido:** 359 verificaciones elemento a elemento, además de los 168 puntos de método. **Total: 527**.
**Regla:** cada fila exige evidencia triple (comando + salida + `fichero:línea`) y veredicto de §2.1 del plan padre. Ninguna fila se cierra por lectura de documentación.

| Barrido | Prefijo | Filas | Universo |
|---|---|---:|---|
| Fuentes declaradas | `SRC` | 40 | `config/fuentes.yaml` + README |
| Scripts de extracción | `EXF` | 41 | `extract/*.py` |
| Scripts de transformación | `TRN` | 44 | `transform/*.py` |
| Colecciones Mongo | `MCO` | 28 | 14 vivas + 14 `__backup` |
| Pipelines de agregación | `AGP` | 10 | `PIPELINE_ORDER` |
| Requisitos de las specs | `RQS` | 44 | 5 specs |
| Criterios de rúbrica | `RUB` | 26 | PDF + DOCX |
| Ficheros de test | `TSF` | 22 | `tests/*.py` |
| Índices | `IDX-I` | 9 | `ensure_indexes()` |
| CSV de resultados | `CSV` | 16 | `data/resultados/*.csv` |
| PNG de resultados | `PNG` | 12 | `data/resultados/*.png` |
| Assets de presentación | `VIS-A` | 24 | 10 SVG + 10 shots + HTML + template + PDF + build |
| Documentos activos | `DOC-F` | 30 | raíz + `docs/` + specs + `plan/` |
| Variables de entorno | `ENV` | 13 | código + `.env.example` |
| **Total barridos** | | **359** | |
| Puntos de método (plan padre) | | 168 | |
| **Total auditoría** | | **527** | |

---

## B1. Fuentes declaradas — `SRC-01…40`

| ID | Fuente | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| SRC-01 | Eustat bankupx · población por edad (`PX_010154`) | API JSON viva, municipio×edad, 252 municipios | Ejecutar extractor 01; contar filas y códigos distintos |
| SRC-02 | Eustat bankupx · renta municipal (`PX_173402 rp11s`) | Año 2024, €/persona, 252 | Join con `dim_municipios`; nulos explicados |
| SRC-03 | Eustat bankupx · renta por edad (`rp03`) | Base del canónico 18–34 y del legacy 16–29 | Verificar grupos de edad y ponderación |
| SRC-04 | Eustat bankupx · PIB municipal (`PX_170120`) | Cobertura y año; uso real en indicadores | Grep de consumo; si no se usa, declararlo |
| SRC-05 | Eustat bankupx · tenencia (`PX_122404`) | Alquiler vs propiedad; cobertura | Conteo y comparación con alquiler oficial |
| SRC-06 | Eustat ExtractorBlob · alquiler territorial | 3 territorios, año 2024, columnas €/m² y €/mes | Descarga/parseo y conteo |
| SRC-07 | Eustat ExtractorBlob · alquiler municipal | **159 oficiales**; eje del estudio | Join 159/252; sin imputar como oficial |
| SRC-08 | Eustat ExtractorBlob · distrito/sección | Granularidad fina; ¿se usa o es lastre? | Grep de uso; decidir mantener o declarar |
| SRC-09 | euskadi.eus · emancipación juvenil | 867 filas, 16 indicadores, solo CAE/TH | Verificar granularidad; no presentar como municipal |
| SRC-10 | B5M Gipuzkoa · catálogo/geo | 88 municipios de Gipuzkoa; no sustituye cartografía completa | Conteo de features |
| SRC-11 | B5M Gipuzkoa · distancias | 180.488 pares, solo Gipuzkoa; no extrapolar | Conteo y contraste con Haversine |
| SRC-12 | INE 69301 · población | API abierta; contraste con Eustat | Diferencias por municipio documentadas |
| SRC-13 | INE 69302 · hogares y viviendas | Cobertura y uso | Conteo; si no se usa, marcarlo |
| SRC-14 | INE 69303 · actividad/desempleo | Solo 113 ciudades; no cubre 252 | Conteo de municipios alcanzados |
| SRC-15 | INE 69323 · indicadores vivienda | Cobertura urbana; uso | Join y conteo |
| SRC-16 | INE 69330 · indicadores urbanos | Cobertura urbana; uso | Join y conteo |
| SRC-17 | INE EPA · salarios por edad/decil | Proxy salarial; no municipal | Verificar granularidad y limitación declarada |
| SRC-18 | INE ECVI · compraventa | XLSX territorial; 29 docs; join 7/29 | Recalcular join y documentar el parcial |
| SRC-19 | geo.euskadi · municipios | SHP 252; mapa maestro y `codigo_ine` | Conteo de polígonos y códigos |
| SRC-20 | geo.euskadi · comarcas | Base de imputación comarcal (93) | Conteo de comarcas y asignación |
| SRC-21 | geo.euskadi · territorios | 3 TH; agregación territorial | Conteo y coherencia con dim |
| SRC-22 | geo.euskadi · áreas funcionales | Base de ECVI y mercado de área | Conteo y join |
| SRC-23 | Open Data Euskadi · EMAL fianzas | Contratos/fianzas; mismos 159 que alquiler | Join; no cierra el gap de 93 |
| SRC-24 | Etxebide · promociones | 406 promociones; 77 municipios; `NumViviendas` vacío | Conteo y declaración de stock no público |
| SRC-25 | Etxebide · solicitudes | 5.040 docs; tensión social municipal | Join 252/252 y cálculo de tensión |
| SRC-26 | GTFS · transporte | 13 operadores; paradas por municipio | Conteo de paradas y municipios |
| SRC-27 | Lanbide · paro juvenil | 252/252 tras normalización | Conteo exacto; sin `tasa_paro_aprox_pct` |
| SRC-28 | Lanbide · histórico paro joven | Serie 2026; tendencia | Fechas, cobertura y uso |
| SRC-29 | Udalmap · indicadores adicionales | API/CSV; cobertura y año | Join y conteo |
| SRC-30 | Udalmap · extendido | Índice de confort; 252 | Fórmula y nulos |
| SRC-31 | Udalmap · VPO terminadas | 272 códigos → 252; flujo quinquenal, no stock | Conteo y filtro de comarcas |
| SRC-32 | SERPAVI · renta municipal | Mismos 159 que Eustat; ¿aporta algo? | Join y delta por municipio |
| SRC-33 | INE Atlas de renta | Rellena faltantes de renta; ¿cuántos? | Conteo de municipios aportados |
| SRC-34 | OSRM · tiempos a capitales | 252 municipios; ruta vs Haversine | Conteo y comparación de método |
| SRC-35 | Fotocasa · scraping | HTML con JSON embebido; 428 anuncios; 3 provincias | Parseo real, sin fixture; conteo por provincia |
| SRC-36 | Pisos.com · scraping | 247 anuncios; re-resolución de ubicación 2026-11-07 | Conteo y evidencia textual de municipio |
| SRC-37 | RealtyAPI/Idealista | API no oficial; 84 anuncios; key opcional | Verificar estado de la key y uso real |
| SRC-38 | Certificados energéticos | Municipal; 252; contraste ECVI territorial | Conteo y moda por municipio |
| SRC-39 | Centros educativos | Equipamiento municipal | Conteo y join |
| SRC-40 | Centros sanitarios | Equipamiento municipal | Conteo y join |

## B2. Scripts de extracción — `EXF-01…41`

| ID | Script | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| EXF-01 | `01_eustat_api.py` | API bankupx, 5 tablas, `main()` | Ejecutar en seco; artefactos y sidecar |
| EXF-02 | `02_eustat_alquiler.py` | ExtractorBlob de alquiler; 159 municipios | Conteo y comparación con fuente |
| EXF-03 | `03_euskadi_emancipacion.py` | CSV 867 filas; 16 indicadores | Parseo y conteo |
| EXF-04 | `04_b5m_geo.py` | Geo Gipuzkoa; no confundir con 252 | Conteo de municipios |
| EXF-05 | `05_fotocasa_scraper.py` | Scraping real de HTML/JSON embebido | Regex/parseo sobre HTML real; >0 anuncios |
| EXF-06 | `06_ine_api.py` | 5 tablas INE; `null` de alquiler | Conteo y manejo de nulos |
| EXF-07 | `07_ine_salarios.py` | EPA por edad/decil | Estructura y años |
| EXF-08 | `08_pisos_scraper.py` | Regex sobre `ad-preview`; ubicación real | Parseo y evidencia textual |
| EXF-09 | `09_fotocasa_dirigido.py` | Scraping dirigido a municipios faltantes | Lista objetivo y resultados |
| EXF-10 | `09_realtyapi.py` | API opcional; clave y límites | Sin key debe fallar limpio, no simular |
| EXF-11 | `10_opendata_bizilagun_etxebide.py` | EMAL/Etxebide; fuentes directas | Parseo y conteo |
| EXF-12 | `10_ovj_salario.py` | Salario joven OVJ | Estructura y uso como proxy |
| EXF-13 | `10_scraping_faltantes.py` | Rellena municipios sin anuncios | Delta de cobertura |
| EXF-14 | `11_transporte_gtfs_paradas.py` | GTFS 13 operadores | Conteo de paradas |
| EXF-15 | `12_enriquecer_json_anidado.py` | Aplanado/estructura anidada | Antes/después y tipos |
| EXF-16 | `13_scraping_habitaciones.py` | Habitaciones vs vivienda completa | Conteo y no mezclar |
| EXF-17 | `14_add_metadata_fingerprint.py` | Fingerprint determinista | Dos ejecuciones → mismo hash |
| EXF-18 | `15_add_geojson.py` | GeoJSON por anuncio; 424 esperados | Conteo y validez de coordenadas |
| EXF-19 | `16_serpavi_renta.py` | Renta fiscal; 159 | Join y solapamiento |
| EXF-20 | `17_osrm_tiempos.py` | Tiempos a capitales; API real | Conteo 252 y tiempos >0 |
| EXF-21 | `18_lanbide_paro_juvenil.py` | Paro municipal; 252 | Conteo y normalización de códigos |
| EXF-22 | `19_udalmap_indicadores_adicionales.py` | API Udalmap | Conteo y años |
| EXF-23 | `20_ecvi_compraventa.py` | XLSX ECVI; territorial | Parseo y 29 docs |
| EXF-24 | `21_lanbide_historico_paro_joven.py` | Serie histórica | Fechas y cobertura |
| EXF-25 | `22_geo_areas_funcionales.py` | SHP áreas funcionales | Conteo de áreas |
| EXF-26 | `23_certificados_energeticos.py` | Certificados municipales | Conteo 252 y moda |
| EXF-27 | `24_etxebide_promociones.py` | 406 promociones | Conteo y campos vacíos |
| EXF-28 | `25_udalmap_extendido.py` | Confort y variables extendidas | Conteo y fórmula |
| EXF-29 | `26_vpo_terminadas.py` | 272→252; filtro comarcal | Conteo y descartes |
| EXF-30 | `_common.py` | Cliente HTTP, `.env`, utilidades | Revisar duplicidad con dotenv y timeouts |
| EXF-31 | `educacion_centros.py` | Centros educativos | Conteo y join |
| EXF-32 | `entity_resolution.py` | Resolución de nombres → `codigo_ine` | Tasa de acierto y variantes |
| EXF-33 | `euskadi_geo.py` | SHP → GeoJSON | Conteo y CRS |
| EXF-34 | `fotocasa_detalle.py` | Detalle de anuncio | Campos extraídos y nulos |
| EXF-35 | `generar_ingestion_manifest.py` | Manifest 354 fichas | SHA y conteo |
| EXF-36 | `generar_manifest.py` | Manifest alternativo | ¿Duplicado? Decidir vigente |
| EXF-37 | `ine_atlas_renta.py` | Renta Atlas | Municipios aportados |
| EXF-38 | `main_ingest.py` | Orquestador de extracción | Lista de scripts y orden |
| EXF-39 | `normalizar_metadata.py` | Metadatos y fechas | Consistencia entre ficheros |
| EXF-40 | `salud_centros.py` | Centros sanitarios | Conteo y join |
| EXF-41 | `udalmap_empleo.py` | Empleo Udalmap | Conteo y campos |

## B3. Scripts de transformación — `TRN-01…44`

| ID | Script | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| TRN-01 | `_raw_guard.py` | Guard de escritura en `raw` | Lista blanca y `assert_raw_writable` |
| TRN-02 | `aplicar_cobertura_mercado.py` | `n_anuncios_raw`; corre tras dim base | Orden y columna presente |
| TRN-03 | `asignar_area_funcional_ecvi.py` | Área funcional por municipio | Join y nulos |
| TRN-04 | `auditar_lagunas_silver.py` | Profiling de 42 CSV | Filas, nulos, cobertura/252 |
| TRN-05 | `auditoria_duckdb.py` | Legacy DuckDB; ¿sigue vivo? | Grep de uso; declarar legacy |
| TRN-06 | `calcular_renta_joven.py` | Renta 18–34 ponderada | Fórmula del YAML y resultado |
| TRN-07 | `calcular_tension_social.py` | Tensión por solicitudes | Fórmula y 252 |
| TRN-08 | `completar_alquiler_comarca.py` | Imputación comarcal 93 | `metodo_imputacion=IDW/comarca` |
| TRN-09 | `construir_dim_gold.py` | Capa gold; ¿se usa? | Consumo real |
| TRN-10 | `corregir_empleo.py` | Corrige paro inválido | `tasa_paro_lanbide_pct` presente |
| TRN-11 | `deduplicar_alquiler_enriquecido.py` | Duplicados de alquiler | Conteo antes/después |
| TRN-12 | `dim_municipios.py` | Base 252; código y nombres | 252 y unicidad de `_id` |
| TRN-13 | `enriquecer_codigo_ine.py` | zfill(5) y resolución | Longitudes 5/5 |
| TRN-14 | `enriquecer_equipamiento_realtyapi.py` | Equipamiento por anuncio | Array y vocabulario |
| TRN-15 | `enriquecer_gtfs_conectividad.py` | Conectividad transporte | Join y nulos |
| TRN-16 | `f4_pisos_dirigido.py` | Dirigido Pisos | ¿En DAG? Resultados |
| TRN-17 | `filtrar_outliers.py` | Rangos y IQR por segmento | Descartes y no pérdida total |
| TRN-18 | `generar_analisis_variables_base.py` | Variables base | Columnas y 252 |
| TRN-19 | `generar_anuncios_residencial_filtrado.py` | Residencial 326/53 | Conteo |
| TRN-20 | `generar_cert_energetico_moda_municipio.py` | Moda municipal | 252 y nulos |
| TRN-21 | `generar_cert_energetico_municipal.py` | Certificados por municipio | Duplicidad con TRN-20 |
| TRN-22 | `generar_dashboard_completo.py` | Dashboard con literales | ¿Evidencia RA4? Debe ser no |
| TRN-23 | `generar_dashboard_visual.py` | PNG de dashboard | Fuente de datos |
| TRN-24 | `generar_distancias.py` | Matriz 252×252 Haversine | Conteo de pares |
| TRN-25 | `generar_emancipacion_tier3_93.py` | Emancipación para 93 | No fingir municipal |
| TRN-26 | `generar_f4_pisos_objetivo.py` | Objetivo de scraping | Lista y uso |
| TRN-27 | `generar_fingerprint.py` | Fingerprint de dedup | Determinismo |
| TRN-28 | `generar_fotocasa_dirigido_informe.py` | Informe de dirigido | Cifras y fuente |
| TRN-29 | `generar_mapa_esquema.py` | PyVis de 40 CSV | Nodos y aristas reales |
| TRN-30 | `generar_mercado_area_funcional.py` | Mercado por área | Join y conteo |
| TRN-31 | `generar_municipios_faltantes_93.py` | Lista de 93 | Conteo exacto |
| TRN-32 | `generar_poblacion_joven_municipal.py` | Población 15–29 | Bandas y no derivar de 0–19 |
| TRN-33 | `generar_vistas_mercado.py` | Vistas de mercado | Conteo |
| TRN-34 | `imputar_nulos_fuentes.py` | Imputación declarada | Método y `is_imputed` |
| TRN-35 | `limpiar_ecvi.py` | Limpieza ECVI | Tipos y códigos |
| TRN-36 | `limpiar_eustat_demografia.py` | Limpieza demografía | Bandas y 252 |
| TRN-37 | `limpiar_vpo_municipal.py` | Limpieza VPO | 252 y estados |
| TRN-38 | `muni_resolve.py` | Resolución de municipios | Variantes y aciertos |
| TRN-39 | `normalizar_json_crudos.py` | JSON → tabular | Tipos y anidados |
| TRN-40 | `parsear_secciones.py` | Secciones censales | ¿Se usa? |
| TRN-41 | `rescatar_features_nlp.py` | Features de texto | Precisión y falsos positivos |
| TRN-42 | `run_all.py` | DAG 34 nodos y `--check` | Topológico y sin huecos |
| TRN-43 | `unificar_anuncios.py` | 594 unificados; zfill | Conteo y duplicados |
| TRN-44 | `validar_renta.py` | Validación de renta | Reglas y rechazos |

## B4. Colecciones Mongo — `MCO-01…28`

| ID | Colección | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| MCO-01 | `municipios` (252) | `_id` 5 dígitos, demografía anidada, tipos | Muestreo + `$type` + unicidad |
| MCO-02 | `anuncios` (594) | GeoJSON, array equipamiento, Decimal128, unique portal+id | Muestreo y `list_indexes()` |
| MCO-03 | `alquiler_municipal` (252) | 159 oficial + 93 IDW; `metodo_imputacion` | Conteo por método |
| MCO-04 | `indicadores` (252) | 252 filas; campos derivados | Conteo y nulos |
| MCO-05 | `certificados_energeticos` (252) | Moda y distribución | Conteo y nulos |
| MCO-06 | `ecvi_compraventa` (29) | Join parcial 7/29 | Recalcular y declarar |
| MCO-07 | `emancipacion_juventud` (1) | Documento único CAE | Estructura y granularidad |
| MCO-08 | `etxebide_promociones` (406) | 77 municipios; `NumViviendas` vacío | Conteo y campos |
| MCO-09 | `etxebide_solicitudes` (5.040) | 252 municipios; tensión | Conteo y join |
| MCO-10 | `osrm_tiempos` (252) | Tiempos por capital | Conteo y valores |
| MCO-11 | `udalmap_empleo` (252) | Paro y actividad | Conteo y tipos |
| MCO-12 | `udalmap_extendido` (252) | Confort y variables | Conteo y nulos |
| MCO-13 | `udalmap_indicadores` (252) | Indicadores adicionales | Conteo |
| MCO-14 | `vpo_municipal` (252) | VPO por municipio | Conteo y estados |
| MCO-15 | `municipios__backup` (252) | Restaurable y fechado | Conteo y `$out`/rename |
| MCO-16 | `anuncios__backup` (594) | Copia íntegra | Diff de IDs |
| MCO-17 | `alquiler_municipal__backup` (252) | Copia íntegra | Diff de IDs |
| MCO-18 | `indicadores__backup` (252) | Copia íntegra | Diff de IDs |
| MCO-19 | `certificados_energeticos__backup` (252) | Copia íntegra | Diff de IDs |
| MCO-20 | `ecvi_compraventa__backup` (29) | Copia íntegra | Diff de IDs |
| MCO-21 | `emancipacion_juventud__backup` (1) | Copia íntegra | Diff |
| MCO-22 | `etxebide_promociones__backup` (406) | Copia íntegra | Diff de IDs |
| MCO-23 | `etxebide_solicitudes__backup` (5.040) | Copia íntegra | Diff de IDs |
| MCO-24 | `osrm_tiempos__backup` (252) | Copia íntegra | Diff de IDs |
| MCO-25 | `udalmap_empleo__backup` (252) | Copia íntegra | Diff de IDs |
| MCO-26 | `udalmap_extendido__backup` (252) | Copia íntegra | Diff de IDs |
| MCO-27 | `udalmap_indicadores__backup` (252) | Copia íntegra | Diff de IDs |
| MCO-28 | `vpo_municipal__backup` (252) | Copia íntegra | Diff de IDs |

## B5. Pipelines de agregación — `AGP-01…10`

| ID | Pipeline | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| AGP-01 | `pipeline_indicadores_municipio` | 252 filas, `$lookup` + `$addFields`, winsor/IQR | Ejecutar y contar; revisar etapas |
| AGP-02 | `pipeline_alquiler_por_municipio` | 252 filas, niveles y mediana | Ejecutar y contar |
| AGP-03 | `pipeline_modalidades` | 2 filas; temporal vs larga | Conteo y medias separadas |
| AGP-04 | `pipeline_top_municipios_por_esfuerzo` | 10 filas; orden y umbral | Conteo y orden |
| AGP-05 | `pipeline_esfuerzo_por_sexo` | 252; ¿aporta al reto? | Conteo y sentido |
| AGP-06 | `pipeline_accesibilidad_extendida` | 252; minutos y confort | Conteo y nulos |
| AGP-07 | `pipeline_udalmap_extendido_osrm` | 252; join Udalmap+OSRM | Conteo |
| AGP-08 | `pipeline_vpo_por_municipio` | 322 filas; promociones | Conteo |
| AGP-09 | `pipeline_vpo_terminadas` | 251 filas; flujo | Conteo y año |
| AGP-10 | `pipeline_tier_por_municipio` | 252; A/B/C/D y `n_precio` | Conteo por tier |

## B6. Requisitos de las specs — `RQS-01…44`

| ID | Requisito | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| RQS-01 | `HDFS-01` | Originales + procesados + recuperación | `LISTSTATUS` y SHA; waiver si falta procesado |
| RQS-02 | `KAFKA-01` | Productor y consumidor procesan | Código + offsets + lag |
| RQS-03 | `INTEGRACION-01` | Flujo completo hasta Mongo | Cadena ejecutable; rama Kafka aparte |
| RQS-04 | `ENTREGABLES-01` | Esquema, informe, demo | Checklist de §DEF |
| RQS-05 | `EXTRACCION-01a` | API **y** scraping automatizados | ≥1 de cada con `main()` |
| RQS-06 | `EXTRACCION-02` | No hay fuente única | ≥2 fuentes independientes |
| RQS-07 | `FORMATO-01` | Todo dato JSON o CSV | Inventario de extensiones |
| RQS-08 | `COMPLEMENTARIOS-01` | Salario, población, paro 252/252 | Conteos por variable |
| RQS-09 | `PYTHON-01` | Todo en Python | Sin notebooks/SQL como ejecución |
| RQS-10 | `GATE-JOIN-01` | Fuente nueva con join previo | Validador de cobertura antes de alta |
| RQS-11 | `EXTRACCION-01b` | Ubicación real Pisos por texto | Evidencia textual y código |
| RQS-12 | `PISOS-01` | Orden de resolución verificable | Traza de pasos |
| RQS-13 | `PISOS-02` | Cuarentena `geo_invalida` | Conteo y motivo |
| RQS-14 | `OUTLIER-01` | Rangos + IQR en extracción | Descartes y no pérdida total |
| RQS-15 | `DEDUP-01` | Dedup por fingerprint | 0 duplicados cross-portal |
| RQS-16 | `MODELO-01` | Modelo justificado y relaciones | Esquema + doc + consulta |
| RQS-17 | `PYMONGO-01` | CRUD con excepciones tipadas | Código + test |
| RQS-18 | `CARGA-SEGURA-01` | Sin ventana vacía ni borrado irreversible | Staging→backup→rename |
| RQS-19 | `CONSULTAS-01` | 5 útiles, anidado y 2 condiciones | Ejecutar y contar |
| RQS-20 | `AGREGACION-01` | Winsor + IQR + 5 CSV | Ejecutar y verificar |
| RQS-21 | `TIER-01` | Raw inmutable, HDFS solo raw, Kafka→HDFS | Guards + waiver |
| RQS-22 | `LIMPIEZA-01` | ≥4 operaciones con nulos/dup/tipos | Contadores |
| RQS-23 | `TRANSFORM-01` | Transformaciones en Mongo | `$set/$convert/$unset` |
| RQS-24 | `INDICES-01` | `explain()` before/after | COLLSCAN vs IXSCAN |
| RQS-25 | `TRANSACCIONES-01` | Atómica o transacción | Código + test |
| RQS-26 | `DISTRIBUIDA-01` | Conceptos explicables | Guion + doc |
| RQS-27 | `PYMONGO-PRO-01` | Cliente, errores, cursores | Revisión de código |
| RQS-28 | `VALIDACION-01` | Validación de esquema si procede | Justificación |
| RQS-29 | `RESPALDO-01` | Backups y geo en lectura pura | Colecciones y consultas |
| RQS-30 | `RENTA-01` | `validar_renta` o justificación | Código/acta |
| RQS-31 | `PISOS-03` | Conteos honestos, sin imputar precio | Municipio sin anuncio = `None` |
| RQS-32 | `PISOS-04` | Paro 252/252 Lanbide | Conteo y campo correcto |
| RQS-33 | `CAPAS-01` | Oficial/IDW/contexto etiquetadas | 3 CSV y mapa |
| RQS-34 | `DATOS-HETEROGENEOS-01` | CSV/JSON/XLSX/GTFS/HTML adaptados | ≥3 formatos y código |
| RQS-35 | `AUTOMATIZACION-ANALISIS-01` | Un script ejecuta todo | Entry point y salidas |
| RQS-36 | `INDICADORES-01` | ≥5 indicadores de 2+ fuentes | Tabla indicador→fuente |
| RQS-37 | `PREPARACION-VISUALIZACION-01` | ≥3 conjuntos automáticos | ≥3 CSV con huella |
| RQS-38 | `CONCLUSION-01a` | Guion Tema 8 de 1 página | 10 criterios y lagunas |
| RQS-39 | `RESPUESTA-01` | 4 robustos y matriz O1–O4 | Tabla y cifras |
| RQS-40 | `CONCLUSION-01b` | Tiers A/B/C/D y ranking n≥30 | Conteos y conciliación 62/252 |
| RQS-41 | `PISOS-05` | Esfuerzo contextual y frase literal | Texto exacto |
| RQS-42 | `chart_tierB_range` | Barras Tier B con rango y mediana | SVG + datos |
| RQS-43 | `chart_mapa_tier` | Coroplético 4 niveles y capas | SVG + 252 features |
| RQS-44 | `chart_effort_vs_n` | Burbuja solo Tier A | 4 puntos, sin inventar |

## B7. Criterios de rúbrica — `RUB-01…26`

| ID | Criterio | Umbral 10 literal | Qué evidencia lo demuestra |
|---|---|---|---|
| RUB-01 | BDA · Extracción | Automatiza API **y** scraping | `EXF` con API + scraping reales |
| RUB-02 | BDA · HDFS | Originales **y procesados** + recuperación | `INF-01…04` |
| RUB-03 | BDA · Kafka | Productor **y consumidor** procesan | `INF-05/06` |
| RUB-04 | BDA · Integración | Flujo completo **hasta MongoDB** | `INF-07` |
| RUB-05 | SBD · Integración de fuentes | 2+ fuentes y ≥1 campo común | `MCO-02`, join 594/594 |
| RUB-06 | SBD · Construcción del conjunto | 2+ colecciones y relación/embedding/referencia | `MCO-01/02` |
| RUB-07 | SBD · Limpieza | ≥4 operaciones con nulos, duplicados, tipos | `TRN-11/17/34`, `MON-09` |
| RUB-08 | SBD · Automatización | Carga+limpieza+transformación sin tocar Mongo | `TRN-42`, `MON-07` |
| RUB-09 | SBD · Modelado | 2+ colecciones, tipos, decisión explicada | `MCO-01…04` |
| RUB-10 | SBD · CRUD | 4 operaciones + comprobación por código | `MON-06` |
| RUB-11 | SBD · Consultas | 5 útiles, anidado/array, 2+ condiciones | `AGP`, `CONSULTAS-01` |
| RUB-12 | SBD · Aggregation | 3 pipelines, 5 etapas, `$group`+`$lookup` | `AGP-01…10` |
| RUB-13 | SBD · Índices | `explain()` before/after y `totalDocsExamined` | `IDX-I01/02` |
| RUB-14 | SBD · Consistencia | Atómica demostrada o transacción | `MON-10` |
| RUB-15 | SBD · Datos heterogéneos | Estructuras distintas adaptadas | `SRC-01…40`, `EXF` |
| RUB-16 | SBD · Automatización análisis | Un script ejecuta **todos** los análisis | `AGP` + `CSV` |
| RUB-17 | SBD · Indicadores | ≥5 de 2+ fuentes | `RQS-36` |
| RUB-18 | SBD · Respuesta al reto | ≥3 municipios, conclusión con indicador | `DEF-04` |
| RUB-19 | SBD · Visualización | ≥3 conjuntos automáticos PyMongo | `CSV-01…16`, `PNG` |
| RUB-20 | Tema 8 · Modelado 15 % | Decisiones justificadas | `MCO-01…04` |
| RUB-21 | Tema 8 · CRUD/limpieza/consultas 15 % | PyMongo, tipos, operadores | `MON-06/09`, `AGP-03` |
| RUB-22 | Tema 8 · Aggregation 20 % | Útiles, correctos, explicados | `AGP-01…10` |
| RUB-23 | Tema 8 · Índices 15 % | Justificados + explain | `IDX-I01…09` |
| RUB-24 | Tema 8 · Transacciones 10 % | Decisión razonada e implementada | `MON-10` |
| RUB-25 | Tema 8 · PyMongo profesional 15 % | Organización, conexión, errores | `ENV`, `MCO`, `MON-12` |
| RUB-26 | Tema 8 · Defensa 10 % | Explicar decisiones | `DEF-01…06` |

## B8. Ficheros de test — `TSF-01…22`

| ID | Fichero | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| TSF-01 | `test_contrato.py` | Contrato y cifras clave | Ejecutar y revisar asserts |
| TSF-02 | `test_crudos.py` | Raw íntegro y estructura | Ejecutar |
| TSF-03 | `test_dedup_fingerprint.py` | Fingerprint y dedup | Ejecutar y comprobar determinismo |
| TSF-04 | `test_fase_datos.py` | Gate de fase de datos | Ejecutar; 18/18 declarado |
| TSF-05 | `test_fuentes_validacion.py` | Validación de fuentes | Ejecutar |
| TSF-06 | `test_hdfs.py` | HDFS con dobles | Ejecutar sin clúster |
| TSF-07 | `test_indicadores.py` | Indicadores y fórmulas | Ejecutar |
| TSF-08 | `test_kafka_pipeline.py` | Productor/consumidor offline | Ejecutar; 11 tests |
| TSF-09 | `test_mongo.py` | CRUD, contadores, Mongo | Ejecutar aislado |
| TSF-10 | `test_mongo_comparativa.py` | Comparativa de municipios | Ejecutar |
| TSF-11 | `test_mongo_consistencia.py` | Atomicidad y standalone | Ejecutar |
| TSF-12 | `test_mongo_geo.py` | GeoJSON y consultas geo | Ejecutar |
| TSF-13 | `test_mongo_indices.py` | `explain()` e índices | Ejecutar |
| TSF-14 | `test_mongo_orquestador.py` | Orquestador de análisis | Ejecutar |
| TSF-15 | `test_mongo_pipeline.py` | Pipeline Mongo | Ejecutar |
| TSF-16 | `test_mongo_pymongo_pro.py` | PyMongo profesional | Ejecutar |
| TSF-17 | `test_mongo_queries.py` | Consultas y arrays | Ejecutar; vocabulario real |
| TSF-18 | `test_pisos_ubicacion_real.py` | Ubicación Pisos | Ejecutar |
| TSF-19 | `test_raw_guardrails.py` | Guards de escritura | Ejecutar |
| TSF-20 | `test_raw_inmutable.py` | Inmutabilidad raw | Ejecutar |
| TSF-21 | `test_tier_confianza.py` | Tiers y ranking | Ejecutar |
| TSF-22 | `test_vpo_municipal.py` | VPO municipal | Ejecutar |

## B9. Índices — `IDX-I01…I09`

| ID | Índice | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| IDX-I01 | `idx_anuncios_ine_modalidad_precio` | ESR compuesto y uso en filtro | `explain` → IXSCAN, docs=1 |
| IDX-I02 | `idx_anuncios_geo` | `2dsphere` sparse | Consulta geo y `list_indexes` |
| IDX-I03 | `idx_anuncios_portal_id` | Unique `(portal,id_anuncio)` | 0 duplicados y error al repetir |
| IDX-I04 | `idx_anuncios_equipamiento` | Multikey | Consulta de array e IXSCAN |
| IDX-I05 | `idx_municipios_territorio_nombre` | Compuesto de filtro+orden | `explain` y orden |
| IDX-I06 | `idx_alquiler_ine_distrito_nivel` | Compuesto de granularidad | `explain` |
| IDX-I07 | `idx_promo_ine_estado_tipo` | Compuesto de promociones | `explain` |
| IDX-I08 | `idx_cert_moda` | Índice simple de moda | Uso real |
| IDX-I09 | `idx_udx_id` | Índice sobre `_id` | ¿Redundante? Justificar |

## B10. CSV de resultados — `CSV-01…16`

| ID | Fichero | Filas esperadas | Qué se verifica |
|---|---|---:|---|
| CSV-01 | `mongo_esfuerzo_por_municipio.csv` | 252 | Columnas, huella, frescura |
| CSV-02 | `mongo_alquiler_por_municipio.csv` | 252 | Niveles y mediana |
| CSV-03 | `mongo_modalidades.csv` | 2 | Temporal vs larga |
| CSV-04 | `mongo_accesibilidad_extendida.csv` | 252 | Minutos y confort |
| CSV-05 | `mongo_vpo_por_municipio.csv` | 322 | Promociones |
| CSV-06 | `mongo_tier_confianza.csv` | 252 | A/B/C/D |
| CSV-07 | `mongo_vpo_terminadas_por_municipio.csv` | 251 | Flujo VPO |
| CSV-08 | `capa_oficial.csv` | 159 | `is_imputed=False` |
| CSV-09 | `capa_idw.csv` | 93 | `is_imputed=True` |
| CSV-10 | `capa_contexto.csv` | 252 | Etiqueta de contexto |
| CSV-11 | `udalmap_paro.csv` | 252 | Paro sin imputar |
| CSV-12 | `ranking_esfuerzo.csv` | 4 | Solo n≥30 |
| CSV-13 | `comparativa_3_municipios_mongo.csv` | 4 | 4 robustos |
| CSV-14 | `bootstrap_robustos.csv` | 4 | Incertidumbre |
| CSV-15 | `sensibilidad_idw.csv` | 2 | Escenarios |
| CSV-16 | `auditoria_lagunas_silver.csv` | 42 | Profiling de 42 CSV |

## B11. PNG de resultados — `PNG-01…12`

| ID | Fichero | Fuente | Qué se verifica |
|---|---|---|---|
| PNG-01 | `A1_distribucion_esfuerzo_por_TH.png` | `pipeline_indicadores_municipio` | Valores vs CSV y duplicado con g1 |
| PNG-02 | `A2_pct_inasequibles_por_TH.png` | indicadores | % >30 por territorio |
| PNG-03 | `B_paro_vs_precio.png` | indicadores | Ejes, nulos y correlación |
| PNG-04 | `C_vpo_antiguedad_por_TH.png` | VPO | Estados y conteos |
| PNG-05 | `D_distancia_vs_precio.png` | accesibilidad + indicadores | Minutos OSRM |
| PNG-06 | `E_demografia_edad.png` | accesibilidad | Confort vs esfuerzo |
| PNG-07 | `F_comparativa_th.png` | alquiler | Medias por TH |
| PNG-08 | `G_gaps_limitaciones.png` | indicadores | Conteos, no literales |
| PNG-09 | `g2_renta_vs_alquiler.png` | indicadores | Renta vs alquiler |
| PNG-10 | `g3_top10_precio_medio.png` | indicadores | n≥3 y outliers |
| PNG-11 | `g4_distribucion_anuncios.png` | indicadores | Histograma |
| PNG-12 | `g5_esfuerzo_robustos.png` | indicadores | n≥30 y umbral 30 |

## B12. Assets de presentación — `VIS-A01…A24`

| ID | Asset | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| VIS-A01 | `chart_effort_vs_n.svg` | Burbuja 4 Tier A, sin inventar | Datos vs `mongo_tier_confianza.csv` |
| VIS-A02 | `chart_mapa_tier.svg` | 252/252 y capas | Conteo de municipios |
| VIS-A03 | `chart_tierB_range.svg` | 3 barras con rango y mediana | Datos Tier B |
| VIS-A04 | `histograma_esfuerzo.svg` | Distribución y umbral 30 | Valores vs CSV |
| VIS-A05 | `robustos.svg` | 4 robustos y n | Conteo |
| VIS-A06 | `sensibilidad.svg` | Escenarios IDW | Valores vs CSV |
| VIS-A07 | `territorios.svg` | 3 TH | Agregación |
| VIS-A08 | `topo.svg` | Topografía/relieve | Fuente y licencia |
| VIS-A09 | `trama.svg` | Trama/estructura | Fuente y coherencia |
| VIS-A10 | `tramos.svg` | Tramos/segmentos | Fuente y coherencia |
| VIS-A11 | `index.html` | Build desde template | Diff reproducible |
| VIS-A12 | `index.template.html` | Placeholders y datos | Variables sustituidas |
| VIS-A13 | `presentacion.pdf` | Páginas y cifras | Mtime y contenido |
| VIS-A14 | `build_presentacion.py` | Generación determinista | 2 ejecuciones → mismo HTML |
| VIS-A15 | `shots/s1.jpg` | Diapositiva 1 | Coincide con HTML |
| VIS-A16 | `shots/s2.jpg` | Diapositiva 2 | Coincide |
| VIS-A17 | `shots/s3.jpg` | Diapositiva 3 | Coincide |
| VIS-A18 | `shots/s4.jpg` | Diapositiva 4 | Coincide |
| VIS-A19 | `shots/s5.jpg` | Diapositiva 5 | Coincide |
| VIS-A20 | `shots/s6.jpg` | Diapositiva 6 | Coincide |
| VIS-A21 | `shots/s7.jpg` | Diapositiva 7 | Coincide |
| VIS-A22 | `shots/s8.jpg` | Diapositiva 8 | Coincide |
| VIS-A23 | `shots/s9.jpg` | Diapositiva 9 | Coincide |
| VIS-A24 | `shots/s10.jpg` | Diapositiva 10 | Coincide |

## B13. Documentos activos — `DOC-F01…F30`

| ID | Documento | Qué se verifica | Cómo / criterio |
|---|---|---|---|
| DOC-F01 | `README.md` | Cifras, comandos, estado | Contraste con medición |
| DOC-F02 | `AGENT.md` | Stack, hechos, convenciones | Contraste |
| DOC-F03 | `openspec/project.md` | Estado y fases | Contraste |
| DOC-F04 | `openspec/specs/contrato-reto/spec.md` | Rúbrica y entregables | Fidelidad PDF/DOCX |
| DOC-F05 | `openspec/specs/extraccion-datos/spec.md` | 11 requisitos | Implementación |
| DOC-F06 | `openspec/specs/almacenamiento-y-streaming/spec.md` | 3 requisitos | Implementación |
| DOC-F07 | `openspec/specs/mongodb-y-analisis/spec.md` | 18 requisitos | Implementación |
| DOC-F08 | `openspec/specs/presentacion-de-resultados/spec.md` | 11 requisitos | Implementación |
| DOC-F09 | `docs/README.md` | Índice y vigencia | Enlaces y docs archivadas |
| DOC-F10 | `docs/metodologia.md` | Método y decisiones | Cifras vigentes |
| DOC-F11 | `docs/informe_final.md` | Informe y conclusiones | Cifras y tablas |
| DOC-F12 | `docs/conclusiones_municipios.md` | Ranking y O1–O4 | Coherencia |
| DOC-F13 | `docs/datos_finales_conclusiones_2026-11-05.md` | Snapshot de datos | Fecha y vigencia |
| DOC-F14 | `docs/arquitectura_datos.md` | Arquitectura y flujo | Diagrama vs código |
| DOC-F15 | `docs/modelo_mongodb.md` | Modelo y decisiones | Esquema real |
| DOC-F16 | `docs/matriz_indicadores.md` | Indicador→fuente | Cobertura |
| DOC-F17 | `docs/diccionario_columnas.md` | Columnas y tipos | Silver real |
| DOC-F18 | `docs/reglas_limpieza.md` | Reglas | Código |
| DOC-F19 | `docs/contrato_datos_raw.md` | Inmutabilidad | Guards |
| DOC-F20 | `docs/preguntas_analisis_profesional.md` | Preguntas y respuestas | Indicadores |
| DOC-F21 | `docs/informe_capacidad_mongo.md` | Capacidad y límites | Medición |
| DOC-F22 | `docs/pendiente_duckdb_pymongo_2026-11-05.md` | Deuda DuckDB | Estado real |
| DOC-F23 | `docs/analisis_vault_vs_rubrica.md` | Análisis vs rúbrica | Criterios |
| DOC-F24 | `docs/auditoria_10_10_SDD_2026-11-05.md` | Auditoría previa | Vigencia |
| DOC-F25 | `docs/trazabilidad_vm.md` | VM y HDFS | 1.582 líneas; vigencia |
| DOC-F26 | `docs/guion_defensa.md` | Guion largo | Cobertura |
| DOC-F27 | `docs/guion_defensa_12min.md` | Guion 12 min | Tiempos y criterios |
| DOC-F28 | `docs/presentacion/README.md` | Presentación | Assets y build |
| DOC-F29 | `plan/PLAN.md` | Plan general | Estado |
| DOC-F30 | `plan/PLAN_10.md` | Plan 10/10 | Requisitos y cierre |

## B14. Variables de entorno — `ENV-01…13`

| ID | Variable | Declarada en `.env.example` | Qué se verifica |
|---|---|---|---|
| ENV-01 | `DATA_DIR` | Sí | Usada, default y rutas |
| ENV-02 | `HDFS_URL` | Sí | Usada y sin secreto |
| ENV-03 | `HDFS_USER` | Sí | Usada y sin secreto |
| ENV-04 | `KAFKA_BOOTSTRAP_SERVERS` | **No** | Usada en código; falta en template |
| ENV-05 | `KAFKA_GROUP_ID` | **No** | Usada; falta en template |
| ENV-06 | `KAFKA_IDLE_MS` | **No** | Usada; falta en template |
| ENV-07 | `KAFKA_TOPIC` | Sí | Valor y coherencia |
| ENV-08 | `MONGO_DB` | Sí | Valor y test DB |
| ENV-09 | `MONGO_HOST` | Sí | Default localhost |
| ENV-10 | `MONGO_PORT` | Sí | 27017 |
| ENV-11 | `MONGO_TEST_DB` | **No** | Usada en tests; aislamiento |
| ENV-12 | `MONGO_URI` | **No** | Usada; prioridad sobre host/port |
| ENV-13 | `REALTYAPI_KEY` | Sí | Secreto vacío por defecto |

---

## Cierre del anexo

- **Cobertura:** 40 fuentes, 41 extractores, 44 transforms, 28 colecciones, 10 pipelines, 44 requisitos, 26 filas de rúbrica (19 v2 + 7 Tema 8), 22 tests, 8 índices, 16 CSV, 12 PNG, 24 assets, 30 documentos, 13 variables.
- **Regla:** cada fila se marca `CUMPLE` / `CUMPLE CON SALVEDAD` / `NO CUMPLE` / `NO VERIFICABLE` / `N/A` con evidencia triple.
- **Salida esperada:** `openspec/audit/barrido_elementos_2026-11-07.csv` con las 359 filas y su veredicto.
