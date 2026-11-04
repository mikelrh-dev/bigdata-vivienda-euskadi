# Exploración de viabilidad — fuentes detalladas por el usuario (pipeline raw)

**Fecha:** 2026-11-03  
**Alcance:** análisis de viabilidad (solo lectura/web, sin implementación) de incorporar al pipeline raw (capa bronze `data/raw/`) ocho familias de fuentes propuestas por el usuario para `bigdata-vivienda-euskadi`.  
**Método:** verificación de URL/API real, formato, granularidad municipal, esfuerzo de extracción, licencia, preguntas desbloqueadas y valor analítico. No se ha modificado ningún archivo del repositorio salvo este informe.  
**Dimensión de referencia:** 252 municipios (Álava 51, Bizkaia 112, Gipuzkoa 88) — `data/raw/dim_municipios.csv`.  
**Convención del proyecto:** solo `extract/*.py` escribe en `data/raw/` (append-only, inmutable); manifest SHA-256 y tests `test_raw_guardrails.py` / `test_raw_inmutable.py`. Cualquier incorporación nueva debe seguir esa convención.

---

## 0. Criterios de viabilidad usados

| Criterio | Qué se valora |
|---|---|
| **URL/API estable** | Endpoint público y documentado, sin scraping frágil (o scraping acotado y reproducible). |
| **Formato** | CSV/JSON/XLSX/ODS/GTFS/GeoJSON/SHP/PBF parseable con pandas/geopandas/pyshp. |
| **Granularidad municipal** | Dato a nivel de municipio (o agregable sin ambigüedad a los 252). |
| **Esfuerzo de extracción** | Bajo (descarga directa), Medio (parseo/limpieza), Alto (API compleja, self-host, rate limits). |
| **Licencia** | Reutilización permitida (atribución citada). |
| **Valor analítico** | Qué preguntas de `docs/preguntas_analisis_profesional.md` desbloquea o mejora; si aporta valor real o es redundante. |

---

## 1. Matriz resumen

| # | Fuente propuesta | Estado actual en repo | URL/API principal (verificada) | Formato | Granularidad municipal | Esfuerzo | Licencia | Preguntas desbloqueadas | Aporta valor |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Udalmap extendido (Eustat/Open Data) | Parcial: 47/222 indicadores (`extract/19_udalmap_*`) | `https://api.euskadi.eus/udalmap/indicators` (222) | JSON (API), XLSX/CSV por indicador | 252/252 (todos los 222) | Bajo (loop genérico) | CC BY 4.0 | C2,C3,C6,E1,E2,E3,B6,D2 + nuevos (123,150,30,38,67) | Medio-bajo (marginal) |
| 2 | ECVI/compraventa + áreas funcionales DOT (OVV/GeoEuskadi) | Implementado: `extract/20_ecvi_compraventa.py`, `extract/22_geo_areas_funcionales.py` | `observatoriovivienda.euskadi.eus/.../ECVI` (XLSX/ODS); `geo.euskadi.eus/.../AREAS_FUNCIONALES_5000_ETRS89.zip` | XLSX/ODS (multi-cabecera), SHP | ECVI: TH/Área funcional/Municipio (secretos en pequeños); áreas: 252/252 mapeo | Medio | CC BY 4.0 | F5, C1 (parcial) | Alto para F5 (ya resuelto) |
| 3 | Certificados eficiencia energética | Implementado: `extract/23_certificados_energeticos.py` (252/252) | `opendata.euskadi.eus/.../certificados_{araba,bizkaia,gipuzkoa}.csv`; API `api-energy-efficiency` | CSV/XLSX (por TH), JSON API | Edificio (agregable a 252/252) | Medio | CC BY 4.0 | C5 | Alto (ya resuelto) |
| 4 | Stock VPO/Alokabide | Parcial: `etxebide_solicitudes.csv` 252/252; promociones no ingeridas; stock solo agregado por TH | Promociones Etxebide CSV/XLS; Udalmap ind. VPO terminadas (‰ hab.); Alokabide sin dataset municipal abierto | CSV/XLS (promociones), PDF (memorias) | Promociones: municipal; stock: TH/tamaño (no municipal) | Medio | CC BY 4.0 | C1 | Alto para C1 (con limitación de stock) |
| 5 | Matriz OSRM completa (Docker Geofabrik) | Parcial: solo capitales (`extract/17_osrm_tiempos.py`, 3 destinos) | `download.geofabrik.de/europe/spain/pais-vasco-latest.osm.pbf` (66 MB); Docker `osrm/osrm-backend` | OSM PBF → matriz JSON/CSV NxN | Par de municipios (252×252) | Alto (Docker daemon apagado; procesado + cálculo) | ODbL (OSM) | D3, D1 mejorado | Alto para D3 (enriquecimiento, no bloqueante) |
| 6 | GTFS enriquecido (Moveuskadi) | Parcial: 13/35 operadores (`extract/11_transporte_gtfs_paradas.py`) | Índice `opendata.euskadi.eus/transport/moveuskadi/data-index-gtfs.json` (35 operadores) | GTFS ZIP | Paradas por municipio | Medio | CC BY 4.0 | D2 | Alto (resuelve 51/252 nulos) |
| 7 | Proxies emancipación juvenil municipal (Padrón/Censo microdatos) | Parcial: población joven estimada (no fuente real) | INE Padrón tablas 33691/33859/33938 (`servicios.ine.es/wstempus`); Censo 2021 hogares; Eustat población municipal | CSV/JSON (INE), PX (Eustat) | Población 18-34: municipal; hogares jóvenes: solo municipios grandes (secreto) | Medio-Alto | CC BY 4.0 (INE) | E1,E2, proxies B6/G4 | Medio (mejora proxy, no desbloquea tasa municipal) |
| 8 | Salario joven municipal (Atlas renta + OVJ + IRPF foral) | Parcial: Eustat renta personal municipal (total 18+); OVJ CA | INE ADRH (tablas 31115/31125); OVJ CSV; IRPF foral Gipuzkoa (Open Data Euskadi); Bizkaia memoria IRPF (datos.gob.es); Eustat PX_173402_crpf_rpf_rp11s.px | CSV (INE/OVJ), XLSX/CSV (IRPF), PX (Eustat) | Atlas/IRPF: municipal (sin edad); OVJ: CA (18-34) | Medio | CC BY 4.0 | B3, A3, G3 (validación) | Bajo para "salario joven municipal" (no existe); medio para validación cruzada |

---

## 2. Detalle por fuente

### 2.1 Udalmap extendido (Eustat/Open Data)

- **URL/API real:**
  - Listado de los 222 indicadores: `https://api.euskadi.eus/udalmap/indicators`
  - Por indicador: `https://api.euskadi.eus/udalmap/indicators/{id}` (JSON)
  - API oficial documentada: `https://opendata.euskadi.eus/api-udalmap/?api=udalmap`
  - Descargas por grupo en catálogo datos.gob.es (XLSX/CSV) y Open Data Euskadi.
- **Formato:** JSON (API REST, sin autenticación); XLSX/CSV por indicador/grupo en descarga. HTML entities en nombres (decodificar).
- **Granularidad municipal:** 252/252 para los 222 indicadores (municipal). Algunos con series temporales 1996→2025.
- **Esfuerzo de extracción:** bajo. Un loop genérico sobre los 222 IDs ya es viable (patrón de `extract/19_udalmap_indicadores_adicionales.py`). Parseo trivial: `municipalities` → `years[0]` → último valor no nulo.
- **Licencia:** CC BY 4.0 (Open Data Euskadi) — atribución al Gobierno Vasco.
- **Preguntas desbloqueadas:** ya cubre C2,C3,C6,E1,E2,E3,B6,D2 (parcial). Los indicadores no extraídos de mayor valor añadido: `123` (accesibilidad del municipio), `150` (tiempo medio de acceso a la capital del TH), `30` (densidad comercial minorista), `38` (deuda viva municipal por habitante), `67` (densidad de viviendas en suelo residencial), `15` (índice de rotación contractual). El resto (medio ambiente, infraestructuras, contenedores, teléfonos públicos) es marginal para emancipación/vivienda.
- **Aporta valor:** medio-bajo. La fuente ya está parcialmente integrada (47/222). Extraer los ~10-15 indicadores adicionales de alto valor es de bajo coste y mejora D1/D2/accesibilidad; extraer los 222 completos añade ruido y almacenamiento sin preguntas nuevas. No es bloqueante.
- **Recomendación:** incorporar solo el subconjunto de alto valor (~10-15 IDs) con un script genérico; documentar el resto como disponible pero no prioritario.

### 2.2 ECVI/compraventa + áreas funcionales DOT (OVV/GeoEuskadi)

- **URL/API real:**
  - Tablas ECVI (XLSX/ODS trimestrales e interanuales): `https://observatoriovivienda.euskadi.eus/estadistica/tablas-estadisticas-estadistica-de-compraventa-de-inmuebles-ecvi/webovv00-content/es/`
  - Áreas funcionales (SHP): `https://www.geo.euskadi.eus/cartografia/DatosDescarga/Limites/AREAS_FUNCIONALES_5000_ETRS89.zip`
  - Ficha metodológica: `https://observatoriovivienda.euskadi.eus/ficha-metodologica-de-la-estadistica-de-compraventa-de-inmueble-ecvi/webovv00-result/es/`
- **Formato:** XLSX/ODS con multi-cabecera (tablas anchas); SHP (ETRS89, UTM30) para áreas funcionales.
- **Granularidad municipal:** ECVI publica a nivel de Territorio Histórico, Área funcional, Municipio (solo grandes ciudades con suficiente volumen; secreto estadístico para pequeños) y, en capitales, por distrito/barrio. Las áreas funcionales DOT cubren los 252 municipios (mapeo completo municipio→área funcional ya generado por `extract/22_geo_areas_funcionales.py`).
- **Esfuerzo de extracción:** medio. Scraping de la página para descubrir enlaces `.xlsx` actuales; parseo con `skiprows`/multi-cabecera; shapefile point-in-polygon para el mapeo. Ya implementado en `extract/20_ecvi_compraventa.py` y `extract/22_geo_areas_funcionales.py`.
- **Licencia:** CC BY 4.0 (OVV/Open Data Euskadi); geoEuskadi CC BY 4.0.
- **Preguntas desbloqueadas:** F5 (compraventa vs alquiler), C1 (parcial, VPO/compraventa).
- **Aporta valor:** alto para F5, pero con limitación estructural: ECVI no es municipal fino para los 245 municipios pequeños (solo 7 con precio directo). El valor real está en el análisis por área funcional (15 áreas) mapeado a municipio, ya disponible. No aporta nueva fuente más allá de lo existente; es "ya resuelto" parcialmente. Recomendación: mantener; mejorar extracción de precio medio por área funcional y documentar secreto estadístico (G1/G5).

### 2.3 Certificados de eficiencia energética

- **URL/API real:**
  - Descargas por territorio: `https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_{araba,bizkaia,gipuzkoa}.csv` (y variantes por capital: `_bilbao`, `_donostia`, `_vitoria`, `_v2`).
  - API REST: `https://opendata.euskadi.eus/api-energy-efficiency/?api=energy-efficiency`
  - Catálogo: `https://datos.gob.es/es/catalogo/a16003011-registro-de-certificados-de-eficiencia-energetica-de-euskadi`
- **Formato:** CSV/XLSX/XML/JSON (descarga por TH); JSON (API por edificio/vivienda/certificado).
- **Granularidad municipal:** nivel edificio (con coordenadas y código postal/municipio), agregable a los 252 municipios (cobertura 252/252 ya verificada en `puntos_flacos_dataset.md`).
- **Esfuerzo de extracción:** medio. Descarga de 6 CSVs grandes (actualización semanal); agregación por municipio y clase energética (A-G); cálculo de % viviendas por clase. Ya implementado en `extract/23_certificados_energeticos.py`.
- **Licencia:** CC BY 4.0 (Open Data Euskadi).
- **Preguntas desbloqueadas:** C5 (certificado energético por municipio y coste total).
- **Aporta valor:** alto. Ya resuelto (252/252). La API permite actualización incremental y consultas por edificio. Recomendación: mantener descarga batch; opcionalmente usar API para enriquecer anuncios (cruce por coordenadas). No nueva fuente.

### 2.4 Stock VPO/Alokabide

- **URL/API real:**
  - Promociones Etxebide (CSV/XLS): `https://www.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/es_vpo/index.shtml`
  - Indicador Udalmap "VPO terminadas en último quinquenio (‰ habitantes)": catálogo Open Data Euskadi (descarga XLSX/CSV/API).
  - Alokabide: NO publica dataset municipal de stock abierto. Solo agregados por TH en memorias anuales (PDF) y acuerdos del consejo de administración. Registro de contratos de Alokabide en Open Data Euskadi (contratación pública, no stock).
  - Visesa: memoria de gestión (PDF) con promociones por municipio.
- **Formato:** CSV/XLS (promociones); PDF (memorias Alokabide/Visesa); XLSX/CSV (indicador Udalmap).
- **Granularidad municipal:** promociones: municipal (estado: en proyecto/en construcción/terminada, tipo VPO/VS, régimen compra/alquiler). Stock VPO real: agregado por TH/tamaño de municipio (no municipal). El indicador Udalmap "VPO terminadas en último quinquenio" ya cubre 252/252.
- **Esfuerzo de extracción:** medio. Parseo del CSV de promociones Etxebide; conteo por municipio/estado/tipo. Las memorias PDF requieren extracción manual/semi-automatizada (bajo valor marginal).
- **Licencia:** CC BY 4.0 (Open Data Euskadi).
- **Preguntas desbloqueadas:** C1 (proporción de VPO por municipio y efecto en accesibilidad).
- **Aporta valor:** alto para C1, pero con limitación clave: no existe stock VPO municipal histórico público (solo promociones recientes y terminadas en últimos 5 años). El indicador Udalmap ya resuelve la cobertura 252/252. Recomendación: incorporar promociones Etxebide (CSV) para contar VPO por municipio/estado; documentar que el stock histórico no es público y que se usa "VPO terminadas en último quinquenio" como proxy. Valor medio-alto.

### 2.5 Matriz OSRM completa (Docker Geofabrik)

- **URL/API real:**
  - Extracto País Vasco: `https://download.geofabrik.de/europe/spain/pais-vasco-latest.osm.pbf` (66 MB, actualizado diariamente).
  - Extracto España (alternativa): `https://download.geofabrik.de/europe/spain-latest.osm.pbf` (1,4 GB).
  - Docker: `osrm/osrm-backend` (imagen oficial) con pipeline MLD (extract → partition → customize → routed).
  - API local: `http://localhost:5000/table/v1/driving/`
- **Formato:** OSM PBF → preprocesado OSRM (`.osrm`); salida matriz JSON/CSV NxN (distancias en metros, duraciones en segundos).
- **Granularidad municipal:** par de municipios (centroide→centroide por red viaria). 252×252 = 63.504 pares.
- **Esfuerzo de extracción:** alto. Verificado: Docker está instalado (v29.7.2) pero el daemon NO está corriendo (`failed to connect to docker API`). Pasos: (1) arrancar Docker Desktop; (2) descargar extracto 66 MB; (3) `osrm-extract` con perfil car; (4) `osrm-partition` + `osrm-customize`; (5) `osrm-routed` en puerto 5000; (6) calcular matriz en chunks (la Table API acepta ~100 coords por request; MLD). Tiempo total estimado: 30-90 min de procesado + cálculo. Requiere ~2-4 GB RAM.
- **Licencia:** ODbL (OpenStreetMap) — atribución obligatoria a OSM contributors.
- **Preguntas desbloqueadas:** D3 (distancia por carretera vs Haversine cambia el ranking de accesibilidad), D1 mejorado.
- **Aporta valor:** alto para D3 y análisis par-a-par (clustering, accesibilidad entre municipios, isocronas). Pero ya se tienen distancias a las 3 capitales (3 destinos). La matriz completa es enriquecimiento, no bloqueante. Recomendación: viable técnicamente (Docker instalado), pero alto esfuerzo; prioridad media. Arrancar Docker Desktop primero y validar con un extracto pequeño. No implementar sin decisión explícita del usuario (coste de tiempo/compute).

### 2.6 GTFS enriquecido (Moveuskadi)

- **URL/API real:**
  - Índice de feeds: `https://opendata.euskadi.eus/transport/moveuskadi/data-index-gtfs.json` (verificado: 35 operadores, actualizado 2026-11-03).
  - Feeds por operador: `https://opendata.euskadi.eus/transport/moveuskadi/{operador}/gtfs_{operador}.zip` (patrón verificado en el índice).
  - Catálogo: `https://www.moveuskadi.euskadi.eus/aa27aModuloWar/descarga`
- **Formato:** GTFS ZIP (stops.txt, routes.txt, trips.txt, stop_times.txt, shapes.txt).
- **Granularidad municipal:** paradas georreferenciadas por municipio (asignación espacial punto-en-polígono o nearest centroid). Cobertura actual: 13/35 operadores → 201/252 municipios con dato; 51 nulos.
- **Esfuerzo de extracción:** medio. Descargar 35 ZIPs (~tamaños variables, total estimado 100-300 MB); parsear `stops.txt`; asignar municipio por coordenadas (shapely o point-in-polygon); calcular `paradas_por_1000_hab`, `expediciones_dia`, `tiene_tren_metro`. Ya implementado parcialmente en `extract/11_transporte_gtfs_paradas.py` (13 operadores).
- **Licencia:** CC BY 4.0 (Moveuskadi/Open Data Euskadi).
- **Preguntas desbloqueadas:** D2 (municipios mejor conectados por transporte público tienen alquiler más caro).
- **Aporta valor:** alto. Resolvería los 51/252 nulos actuales y mejoraría la robustez de D2. Esfuerzo razonable (ampliar el script existente de 13 a 35 operadores). Recomendación: alta prioridad; bajo riesgo. El único coste es tiempo de descarga/parseo.

### 2.7 Proxies de emancipación juvenil municipal (Padrón/Censo microdatos)

- **URL/API real:**
  - INE Padrón por municipio/sexo/edad (año a año): tabla `33691` → `https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33691?tip=AM` (y `33859`, `33721`).
  - INE Padrón por municipio/sexo/edad (grupos quinquenales): tabla `33938` → `https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33938?tip=AM`.
  - INE Censo 2021 (hogares por edad del sustentador principal) vía INEbase (tablas de hogares por municipio).
  - Eustat población municipal (grupos amplios 0-19/20-64/65+): `PX_010154_cepv1_ep06b.px`.
  - OVJ emancipación: `https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv` (solo CAE).
- **Formato:** CSV/JSON (INE wstempus, paginado); PX (Eustat); CSV (OVJ).
- **Granularidad municipal:** población joven (18-34) por municipio: sí, vía INE Padrón (cobertura completa, 252/252, aunque con supresión por secreto en municipios muy pequeños para desgloses finos). Hogares unipersonales jóvenes por municipio: solo para municipios con suficiente tamaño (secreto estadístico para los <~10.000 hab.). Tasa de emancipación real: solo CAE (OVJ/Eustat), no municipal.
- **Esfuerzo de extracción:** medio-alto. API INE con paginación y metadatos; normalización de códigos INE (5 dígitos); agregación por tramos 16-24/25-34; gestión de supresiones. Censo hogares: descarga de tablas INEbase por municipio (formato CSV/XLSX) con parseo.
- **Licencia:** CC BY 4.0 (INE) — atribución al INE.
- **Preguntas desbloqueadas:** E1 (población extranjera), E2 (variación de población), proxies para B6 (desempleo juvenil real) y G4 (comunicación de limitaciones).
- **Aporta valor:** medio. La población joven municipal real (Padrón) reemplazaría la estimación actual (basada en grupos amplios de Eustat), mejorando E1/E2 y los proxies de emancipación. Pero no desbloquea la tasa de emancipación municipal (que es territorial por secreto estadístico). Los hogares jóvenes por municipio solo cubrirán las capitales y municipios grandes. Recomendación: incorporar población joven municipal (Padrón) con prioridad media; hogares jóvenes solo si la cobertura es suficiente (>50% de municipios). Documentar G4.

### 2.8 Salario joven municipal (Atlas renta + OVJ + IRPF foral)

- **URL/API real:**
  - INE Atlas de Distribución de Renta de los Hogares (ADRH), renta media/mediana municipal: tabla `31115` → `https://www.ine.es/jaxiT3/files/t/csv_bd/31115.csv` (y `31125` para distribución por fuente de ingresos).
  - OVJ empleo y situación económica (salario neto joven): `https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_empleo_econom/opendata/iovj-empleo-economico.csv`
  - IRPF foral Gipuzkoa (importes medios por municipio y comarca, 2007-...): `https://opendata.euskadi.eus/catalogo/-/estadisticas-impuesto-renta-personas-fisicas-municipios-y-comarcas/`
  - IRPF foral Bizkaia: memoria anual en datos.gob.es (Diputación Foral de Bizkaia).
  - IRPF foral Álava: similar (Diputación Foral de Álava; verificar disponibilidad).
  - Eustat renta personal media municipal: `https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp11s.px`
- **Formato:** CSV (INE ADRH, separador `;`); CSV (OVJ); XLSX/CSV (IRPF foral); PX (Eustat).
- **Granularidad municipal:** Atlas renta (ADRH): municipal (sin desglose por edad). IRPF foral: municipal (renta media/cuota/declaraciones, sin desglose por edad joven). OVJ: CA Euskadi (18-34/16-29). Eustat renta personal: municipal (total 18+, sin edad).
- **Esfuerzo de extracción:** medio. Descarga ADRH (CSV grande, ~8.000 municipios España; filtrar Euskadi); IRPF foral por TH (Gipuzkoa en Open Data Euskadi; Bizkaia/Álava en datos.gob.es o webs forales); normalización de códigos municipales; cruce con `dim_municipios`.
- **Licencia:** CC BY 4.0 (INE, Open Data Euskadi); datos.gob.es (CC BY 4.0).
- **Preguntas desbloqueadas:** B3 (afiliación SS 16-24 como predictor), A3 (esfuerzo con renta joven estimada vs renta hogar), G3 (sesgo del proxy de renta municipal).
- **Aporta valor:** bajo para "salario joven municipal" (no existe a nivel municipal en Euskadi ni en España; ya documentado en `docs/decision_salario_proxy.md` y `docs/fuentes_salario_joven.md`). Medio para validación cruzada de la renta municipal existente (Atlas INE vs Eustat vs IRPF foral) y para mejorar G3 (documentar sesgos del proxy). No inventar salarios municipales por edad. Recomendación: incorporar Atlas renta municipal e IRPF foral como fuentes de validación/contraste (prioridad media-baja); mantener el proxy actual (Eustat renta personal × ratio edad CA) como variable principal. No resuelve B6.

---

## 3. Síntesis de valor y priorización

### Aporta valor real (incorporar)

| Prioridad | Fuente | Motivo |
|---|---|---|
| **Alta** | GTFS enriquecido (35 operadores) | Resuelve 51/252 nulos; esfuerzo razonable; mejora D2 de forma defendible. |
| **Alta** | Certificados energéticos | Ya resuelto 252/252; mantener y usar API para actualización. |
| **Alta** | Stock VPO (promociones Etxebide + Udalmap) | Mejora C1; documentar limitación de stock histórico. |
| **Media** | Población joven municipal (Padrón INE) | Reemplaza estimación actual; mejora E1/E2 y proxies. |
| **Media** | Matriz OSRM completa | Alto valor para D3; requiere Docker activo (actualmente apagado); esfuerzo alto. |
| **Media** | ECVI (mantenimiento) | Ya resuelto a nivel de área funcional; mejorar parseo. |
| **Media-Baja** | Udalmap extendido (10-15 indicadores) | Bajo coste; valor marginal (accesibilidad, tiempo acceso capital, densidad comercial). |
| **Media-Baja** | Atlas renta + IRPF foral | Validación cruzada de renta municipal; no resuelve salario joven. |

### No aporta valor adicional (o ya cubierto)

- **Udalmap completo (222 indicadores):** la mayoría (medio ambiente, infraestructuras, contenedores, teléfonos públicos) no desbloquea preguntas nuevas. Solo ~10-15 son de alto valor. Extraer los 222 añade ruido y almacenamiento sin beneficio analítico.
- **Emancipación juvenil hogares (Censo):** cobertura limitada a municipios grandes por secreto estadístico; no desbloquea la tasa de emancipación municipal (solo CAE).
- **Salario joven municipal:** no existe (secreto estadístico). Los proxies (Atlas renta, IRPF foral) son sin edad. No inventar salarios municipales (coherente con `docs/decision_salario_proxy.md`).
- **Matriz OSRM completa:** alto valor pero no bloqueante; ya se tienen distancias a capitales. Priorizar solo si se necesita análisis par-a-par (clustering, isocronas).

### Limitaciones transversales a documentar (G1-G6)

- **Secreto estadístico:** ECVI, hogares jóvenes, afiliación SS por municipio pequeño → supresiones. Documentar "sin dato" y usar agregado comarcal/área funcional.
- **Mezcla de años:** anuncios 2026, alquiler/renta 2024, padrón 2025, GTFS 2026. Documentar G5.
- **Falacia ecológica:** renta municipal (total 18+) como proxy de renta joven. Documentar G3.
- **Licencias:** todas CC BY 4.0 excepto OSM (ODbL, requiere atribución). Verificar términos específicos en cada ficha de Open Data Euskadi.

---

## 4. Nota final

Este informe es solo análisis. No se ha implementado ninguna extracción ni modificado el repositorio (salvo este archivo). Las decisiones de implementación (qué fuentes incorporar, en qué orden, con qué esfuerzo) quedan a criterio del usuario. Se recomienda priorizar las fuentes de **alta prioridad** (GTFS enriquecido, certificados, VPO promociones, población joven Padrón) por su relación coste/beneficio, y dejar la matriz OSRM completa y el Udalmap extendido completo como mejoras opcionales.
