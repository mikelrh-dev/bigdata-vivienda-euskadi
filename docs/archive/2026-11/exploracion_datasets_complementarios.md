# Exploración de viabilidad — datasets complementarios para el pipeline raw

**Fecha:** 2026-11-03  
**Alcance:** evaluación de incorporación al pipeline (capa bronze `data/raw/`) de cinco familias de fuentes complementarias propuestas para el proyecto `bigdata-vivienda-euskadi`.  
**Método:** solo lectura del repositorio + búsqueda/extracción web de fuentes oficiales. No se ha modificado ningún archivo del repositorio salvo este informe.  
**Dimensión de referencia:** 252 municipios (Álava 51, Bizkaia 112, Gipuzkoa 88) — `data/raw/dim_municipios.csv`.

---

## 0. Criterios de viabilidad usados

| Criterio | Qué se valora |
|---|---|
| **URL/API estable** | Endpoint público y documentado, sin scraping frágil. |
| **Formato** | CSV/JSON/XLSX/ODS/GTFS/GeoJSON parseable con pandas/geopandas. |
| **Granularidad municipal** | Dato a nivel de municipio (o agregable sin ambigüedad a los 252). |
| **Esfuerzo de extracción** | Bajo (descarga directa), Medio (parseo/limpieza), Alto (API compleja, rate limits, self-host). |
| **Licencia** | Reutilización permitida (atribución citada). |
| **Valor analítico** | Qué preguntas de `docs/preguntas_analisis_profesional.md` desbloquea o mejora. |

Convención del proyecto (capa bronze): solo `extract/*.py` escribe en `data/raw/` (append-only, inmutable); manifest SHA-256 y tests `test_raw_guardrails.py` / `test_raw_inmutable.py`. Cualquier incorporación nueva debe seguir esa convención.

---

## 1. Matriz resumen

| # | Fuente | Estado en repo | URL/API principal | Formato | Granularidad municipal | Esfuerzo | Licencia | Preguntas desbloqueadas |
|---|---|---|---|---|---|---|---|---|
| 1 | EMAL / Mercado de Alquiler (Open Data Euskadi) | Parcial (73/252 municipios en `emal_fianzas.csv`) | Open Data Euskadi (informes + ODS EMAL 2016-2026) | ODS/XLSX/CSV/PDF | Municipal parcial (secreto estadístico) | Medio-Alto | CC BY 4.0 | A4, A6, F1, F2 |
| 2 | Salarios / afiliación joven SS-INE-OVJ | Parcial (OVJ CA; Eustat renta municipal; Lanbide paro) | OVJ CSV, Eustat PXWeb, INE wstempus, Lanbide | CSV/JSON/PX/HTML | Salario joven: **no municipal**; afiliación SS: municipal posible (INE) | Alto | CC BY 4.0 (INE/Open Data Euskadi) | B3, B6, A3 |
| 3 | Parque vivienda pública (Etxebide/Alokabide) | Parcial (`etxebide_solicitudes.csv` 252/252; promociones no ingeridas) | Open Data Euskadi (promociones CSV/XLS; EDYVI ODS) | CSV/XLS/ODS | Promociones: municipal; stock: agregado por TH/tamaño | Medio | CC BY 4.0 | C1 |
| 4 | Certificados de eficiencia energética | Identificado como "resuelto" (252/252) en `puntos_flacos_dataset.md`; verificar ingesta raw | Open Data Euskadi (CSV/XLSX por TH + API REST) | CSV/XLSX/JSON API | Edificio (agregable a municipio) | Medio | CC BY 4.0 | C5 |
| 5 | Matrices OSRM / GTFS | Parcial (solo capitales en `osrm_tiempos_capitales.csv`; 13 GTFS ZIP) | OSRM Table API / b5m API; Moveuskadi GTFS index | JSON/CSV/GTFS ZIP | Par de municipios (OSRM); paradas por municipio (GTFS) | Medio-Alto | ODbL (OSM) + CC BY 4.0 (Moveuskadi) | D2, D3 |

---

## 2. Detalle por fuente

### 2.1 EMAL — Estadística del Mercado de Alquiler (Open Data Euskadi)

**Qué aporta:** fianzas depositadas (proxy de rotación/oferta real), renta media de nuevos contratos, contratos vigentes, separación vivienda habitual vs temporada, por tipo de vivienda. Complementa Eustat (alquiler oficial) y anuncios (oferta).

- **URL/API:**
  - Definiciones: https://opendata.euskadi.eus/definiciones-de-la-estadistica-del-mercado-de-alquiler-ema/webopd00-catalogo/es/
  - Informes de resultados: https://opendata.euskadi.eus/informes-de-resultados-de-la-estadistica-del-mercado-de-alquiler-ema/webopd00-catalogo/es/
  - Tablas EMAL 2016-2026 (ODS): https://www.ivap.euskadi.eus/contenidos/estadistica/122417_emal_tablas_estad/opendata/EMAL-2016-2026_es.ods
  - Informe trimestral (ejemplo 2025T2, PDF): https://www.euskadi.eus/contenidos/documentacion/122417_informe_emal_2025t2/es_def/Informe-EMAL-trimestral-062025.pdf
- **Formato:** ODS/XLSX/CSV/PDF; multi-cabecera, tablas anchas.
- **Granularidad municipal:** parcial. El repo ya tiene `emal_fianzas.csv` con `codigo_ine` en 73/252 y `municipio` en 67/252 (inventario). El resto queda suprimido por secreto estadístico o falta de fianzas suficientes. EMAL publica agregados por territorio histórico, comarca y tamaño de municipio.
- **Esfuerzo de extracción:** medio-alto. Requiere parseo de ODS/XLSX con `skiprows`, normalización de municipios y cruce con `dim_municipios`. Actualización trimestral manual o semi-automatizada.
- **Licencia:** CC BY 4.0 (Open Data Euskadi) — https://opendata.euskadi.eus/general/-/informacion-legal-opendata/
- **Preguntas desbloqueadas:** A4 (diferencias entre alquiler oficial, anuncios y fianzas EMAL), A6 (temporal vs larga estancia), F1 (temporal ≈24% más caro), F2 (oficial vs anuncios). También rotación/liquidez por municipio donde hay dato.
- **Limitación clave:** no cubre los 252 municipios; la comparación debe documentar "sin dato" y usar agregado comarcal para el resto (coherente con G1/G3).

---

### 2.2 Salarios y afiliación joven (SS / INE / OVJ / Eustat)

**Qué aporta:** cerrar la brecha de B6 ("falta población activa joven municipal") y mejorar B3 (afiliación SS 16-24 vs paro). El repo ya documenta que **no existe salario joven municipal** (`fuentes_salario_joven.md`, `decision_salario_proxy.md`).

Subfuentes y su viabilidad:

| Subfuente | URL | Granularidad | Formato | Viabilidad |
|---|---|---|---|---|
| OVJ — Empleo y situación económica | https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_empleo_econom/opendata/iovj-empleo-economico.csv | CA Euskadi (18-34 / 16-29) x sexo | CSV | Ya usado (salario neto joven 1.564 €/mes, 2024). Solo territorial. |
| OVJ — Emancipación y vivienda | https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv | CA joven | CSV | Contexto; no municipal. |
| Eustat — Renta personal media municipal | https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp11s.px | Municipio x sexo x tipo de renta (total 18+) | PX/JSON | Ya usado (proxy principal). Sin edad. |
| Eustat — Renta personal por edad | https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp03.px | CA x sexo x edad | PX/JSON | Ratio edad/total para proxy. Solo CA. |
| INE — Estadística de Afiliación a la SS (IOE 58015) | https://ine.es/dyngs/IOE/operacion.htm?numinv=58015 | Municipal o inferior; clasificación por edad | API wstempus (`DATOS_TABLA`) | **Candidata nueva.** Requiere explorar series por municipio y tramo de edad; posible supresión por secreto estadístico. Esfuerzo alto. |
| INE — EPA/EES salarios | https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/66239 (ej.) | Nacional/CCAA x edad x decil | JSON | Ya referenciado. No municipal. |
| Lanbide — Informe anual de afiliación | https://www.lanbide.euskadi.eus/estudios-estadisticas/-/estadistica/informe-anual-afiliacion/ | CA Euskadi | PDF | Contexto anual; no municipal fino. |

- **URL/API principal (nueva):** INE wstempus para la operación 58015 (afiliación SS), con filtro por municipio y edad. Eustat PXWeb para renta municipal/edad.
- **Formato:** PX (Eustat), JSON (INE wstempus), CSV (OVJ), PDF (Lanbide).
- **Granularidad municipal:** salario joven **no existe** a nivel municipal (secreto estadístico, Ley 4/1986). Afiliación SS por municipio y edad es la vía realista para mejorar B3/B6, pero hay que verificar cobertura/supresión.
- **Esfuerzo de extracción:** alto. API INE con paginación y metadatos; normalización de códigos INE; agregación por tramos 16-24/25-34; posible ausencia de valores para municipios pequeños.
- **Licencia:** INE CC BY 4.0 (https://www.ine.es/aviso_legal/); Eustat/Open Data Euskadi CC BY 4.0 para OVJ.
- **Preguntas desbloqueadas:** B3 (afiliación SS 16-24 como predictor del esfuerzo), B6 (tasa de desempleo juvenil real vs ratio), A3 (esfuerzo con renta joven estimada vs renta hogar). No resuelve salario municipal por edad.
- **Recomendación:** incorporar como fuente experimental (`extract/`), documentando supresiones y no inventando salarios municipales (coherente con `decision_salario_proxy.md`).

---

### 2.3 Parque de vivienda pública — Etxebide / Alokabide / EDYVI

**Qué aporta:** proporción de VPO/vivienda social por municipio y su efecto en accesibilidad (C1), y dinamismo de promociones (C6).

- **URL/API:**
  - Promociones Etxebide (CSV): https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.csv
  - Promociones Etxebide (XLS): https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.xls
  - Catálogo datos.gob.es: https://datos.gob.es/en/catalogo/a16003011-promociones-de-etxebide-para-compra-y-alquiler-de-vivienda-protegida1
  - EDYVI — tablas de alquiler social (ODS): https://www.etxebide.euskadi.eus/contenidos/estadistica/ovv_v_edyvi_tablas_alquiler/opendata/Tablas_EDYVI_alquiler_2025-eus.ods
  - Alokabide — registro de contratos (European Data Portal): https://data.europa.eu/data/datasets/https-opendata-euskadi-eus-catalogo-registro-contratos-alokabide-sociedad-alquiler-s-del-2026-?locale=en
  - Open Data Euskadi — Alokabide: https://opendata.euskadi.eus/catalogo/-/registro-contratos-alokabide-sociedad-alquiler-s-del-2026/
- **Formato:** CSV/XLS/ODS; promociones con campos de tipo (VPO, vivienda tasada, vivienda social, alojamiento dotacional), régimen (compra/alquiler), estado de obra y sorteo.
- **Granularidad municipal:**
  - Promociones Etxebide: municipal (ubicación de la promoción; agregable a municipio).
  - EDYVI: agregado por territorio histórico y tamaño de municipio (no todos los 252).
  - Alokabide "registro de contratos": en Open Data aparece como **contratación pública (procurement)**, no como parque de vivienda; no usarlo como stock de vivienda social.
  - El repo ya tiene `etxebide_solicitudes.csv` (252/252, solicitudes por mil) y `etxebide_indicador_86.csv` (201/252).
- **Esfuerzo de extracción:** medio. Parseo CSV/XLS, normalización de municipios, geocodificación de promociones (si se quiere analizar por barrio/distrito), deduplicación por expediente.
- **Licencia:** CC BY 4.0 (Open Data Euskadi).
- **Preguntas desbloqueadas:** C1 (mayor proporción de VPO y efecto en accesibilidad). Complementa C6 (licencias de nueva construcción ya en Udalmap).
- **Limitación clave:** "stock VPO municipal público" sigue incompleto (inventario: ~16/252 con VPO terminada, 83,7% ceros). Las promociones aportan flujo, no stock acumulado.

---

### 2.4 Certificados de eficiencia energética (Open Data Euskadi)

**Qué aporta:** calificación energética por edificio (A-G), año de construcción, superficie, consumo y emisiones; agregable a municipio para responder C5 y coste total de vivienda (alquiler + energía).

- **URL/API:**
  - Catálogo: https://opendata.euskadi.eus/catalogo/-/registro-de-certificados-de-eficiencia-energetica-de-euskadi/
  - API REST: https://opendata.euskadi.eus/api-energy-efficiency/?api=energy-efficiency
  - datos.gob.es: https://datos.gob.es/en/catalogo/a16003011-registro-de-certificados-de-eficiencia-energetica-de-euskadi
  - Datos abiertos sobre viviendas/edificios: https://opendata.euskadi.eus/comunidad-open-data/-/2023/datos-abiertos-sobre-viviendas-y-edificios-de-euskadi/
- **Formato:** CSV/XLSX particionado por territorio histórico (Araba, Bizkaia, Gipuzkoa) y por capitales (Bilbao, Donostia, Vitoria-Gasteiz); versión "desde 30/09/2026" (incremental) y "hasta 30/09/2026" (histórico). API REST para consultas por edificio/vivienda/certificado.
- **Granularidad:** edificio/vivienda (con municipio, dirección, código postal); agregable a municipio (distribución de clases, media de consumo/emisiones, % de edificios con clase E-G).
- **Esfuerzo de extracción:** medio. Volumen alto (Bizkaia histórico ≈113 MB CSV; Gipuzkoa ≈70 MB), particionado por TH, limpieza y agregación. La API REST permite carga incremental semanal.
- **Licencia:** CC BY 4.0 (Open Data Euskadi).
- **Preguntas desbloqueadas:** C5 (clase energética por municipio y efecto en coste total). También calidad de vivienda y rehabilitación.
- **Estado en repo:** `puntos_flacos_dataset.md` ya marca "Cert. energético: 252/252 — RESUELTO: Open Data Euskadi (registro oficial)". Conviene verificar que exista ingesta en `data/raw/` (extract) y manifest; si no, crear `extract/` para certificados con nombre único por lote.

---

### 2.5 Matrices OSRM / GTFS

#### OSRM (distancias/tiempos por carretera)

**Qué aporta:** matriz de distancias/tiempos entre municipios para D3 (OSRM vs Haversine) y accesibilidad real por red viaria, más allá de la distancia a capital (D1).

- **URL/API:**
  - OSRM Table API (documentación): https://project-osrm.org/docs/v5.24.0/api/
  - b5m Gipuzkoa — distancias entre municipios (API): https://b5m.gipuzkoa.eus/web5000/es/api-rest/distancia-entre-municipios
  - b5m Gipuzkoa — CSV bulk (180.488 distancias): https://b5m.gipuzkoa.eus/datasets/GFA_DSET_DISTM_CSV.zip
- **Formato:** JSON (OSRM Table/b5m API), CSV (b5m bulk).
- **Granularidad:** par de municipios (origen-destino); distancia (km) y tiempo (min) por carretera.
- **Esfuerzo de extracción:** medio-alto.
  - b5m cubre Gipuzkoa ↔ Gipuzkoa y territorios adyacentes (Álava, Bizkaia, Navarra, Pirineos Atlánticos) — reutilizable directamente (CSV bulk).
  - Para Álava↔Álava y Bizkaia↔Bizkaia (y pares no cubiertos) hace falta calcular con OSRM (self-host recomendado; la API pública de demo tiene límites de rate y no es apta para 252×252 = 63.504 pares).
  - El repo ya tiene `osrm_tiempos_capitales.csv` (252/252, minutos a las 3 capitales).
- **Licencia:** datos OpenStreetMap bajo ODbL (atribución requerida); código OSRM BSD-2-Clause. b5m: Diputación Foral de Gipuzkoa (verificar términos de uso en la ficha del dataset; presumiblemente abierto).
- **Preguntas desbloqueadas:** D3 (OSRM vs Haversine cambia el ranking), D1/D4 (accesibilidad rural). Requiere matriz completa para no depender solo de capitales.

#### GTFS (transporte público)

**Qué aporta:** conectividad real por transporte público (D2): paradas por 1000 hab, expediciones/día, presencia de tren/metro.

- **URL/API:**
  - Moveuskadi (catálogo): https://opendata.euskadi.eus/catalogo/-/moveuskadi-datos-de-la-red-de-transporte-publico-de-euskadi-operadores-horarios-paradas-calendario-tarifas-etc/
  - Índice GTFS: https://opendata.euskadi.eus/transport/moveuskadi/data-index-gtfs.json
  - Servicios de descarga FTP (SHP): https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/
- **Formato:** GTFS (ZIP con CSV: `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`), índice JSON, SHP.
- **Granularidad:** paradas/rutas por operador; agregable a municipio mediante join espacial de paradas con polígonos municipales (`municipios_euskadi.geojson` / SHP).
- **Esfuerzo de extracción:** medio. El repo ya contiene 13 ZIP GTFS (`data/raw/gtfs/`) y `transporte_paradas_municipio.csv` (252/252 con nulos en operadores). Falta enriquecer con expediciones/día y tipo de modo, y resolver 51 nulos de operadores (inventario).
- **Licencia:** CC BY 4.0 (Moveuskadi/Open Data Euskadi) para los feeds agregados; los operadores individuales (Bizkaibus, Euskotren, etc.) publican bajo sus propios términos abiertos, generalmente compatibles.
- **Preguntas desbloqueadas:** D2 (municipios mejor conectados por TP tienen alquiler más caro). Mejora el índice compuesto de accesibilidad.

---

## 3. Mapeo pregunta → fuentes nuevas

| Pregunta | Fuente nueva que la mejora | Efecto esperado |
|---|---|---|
| A3 (esfuerzo con renta joven vs hogar) | Eustat PX (ya) + OVJ (ya) + INE afiliación (nueva) | Mejor proxy de ingresos joven; no resuelve salario municipal. |
| A4 (oficial vs anuncios vs EMAL) | EMAL (nueva/actualizada) | Tercera fuente de renta (fianzas) para contrastar. |
| A6 (temporal distorsiona accesibilidad) | EMAL (habitual vs temporada) | Cuantifica el sesgo del alquiler temporal. |
| B3 (afiliación SS predice esfuerzo) | INE afiliación SS municipal (nueva) | Sustituye proxy por afiliación real por municipio. |
| B6 (desempleo juvenil real) | INE afiliación SS + Eustat población (ya) | Pasa de ratio a tasa con denominador real (si cobertura suficiente). |
| C1 (proporción VPO y accesibilidad) | Etxebide promociones (nueva) | Flujo de promociones por municipio y tipo. |
| C5 (certificado energético y coste total) | Certificados eficiencia (nueva/verificar ingesta) | Distribución de clases y consumo por municipio. |
| D2 (conectividad TP) | GTFS enriquecido (nueva) | Expediciones/día y modos por municipio. |
| D3 (OSRM vs Haversine) | OSRM matriz completa (nueva) | Ranking por tiempo/distancia real por carretera. |
| F1 (temporal vs larga estancia) | EMAL (nueva) | Cuantificación del diferencial de precio. |

---

## 4. Riesgos y limitaciones (documentar en el informe final)

1. **Secreto estadístico:** EMAL no cubre los 252 municipios; salario joven no existe a nivel municipal; INE afiliación puede tener supresiones en municipios pequeños.
2. **Volumen:** certificados energéticos históricos ≈ 200 MB CSV en total; requiere carga por lotes y agregación temprana.
3. **OSRM público:** no apto para producción a escala; recomendado self-host o reutilizar b5m para Gipuzkoa y calcular el resto por lotes.
4. **GTFS heterogéneo:** 13 operadores con estructuras ligeramente distintas; 51 municipios sin operador resuelto (inventario).
5. **Alokabide:** su "registro de contratos" en Open Data es contratación pública, no stock de vivienda; no usarlo como parque social.
6. **Licencias:** OSM/ODbL exige atribución y share-alike para datos derivados; Open Data Euskadi e INE CC BY 4.0 exigen citar fuente y fecha de actualización.

---

## 5. Recomendación de incorporación (prioridad)

1. **Certificados energéticos** (prioridad alta): ya identificado como resuelto; verificar/crear `extract/` y agregar por municipio (C5).
2. **EMAL actualizado** (prioridad alta): actualizar informes trimestrales y normalizar municipios; documentar cobertura parcial (A4, A6, F1, F2).
3. **GTFS enriquecido** (prioridad media): calcular expediciones/día y modos; resolver nulos de operadores (D2).
4. **OSRM matriz completa** (prioridad media): b5m para Gipuzkoa + cálculo por lotes para el resto (D3).
5. **Etxebide promociones** (prioridad media): ingestar CSV/XLS y agregar por municipio (C1).
6. **Afiliación SS municipal (INE)** (prioridad baja/experimental): explorar series y supresiones antes de comprometer (B3, B6).

---

## 6. Fuentes consultadas (grounded)

- Open Data Euskadi — información legal: https://opendata.euskadi.eus/general/-/informacion-legal-opendata/
- Open Data Euskadi — reutilizar datos: https://opendata.euskadi.eus/como-reutilizar/-/reutilizar-datos-abiertos/
- EMAL — definiciones: https://opendata.euskadi.eus/definiciones-de-la-estadistica-del-mercado-de-alquiler-ema/webopd00-catalogo/es/
- EMAL — informes resultados: https://opendata.euskadi.eus/informes-de-resultados-de-la-estadistica-del-mercado-de-alquiler-ema/webopd00-catalogo/es/
- EMAL — tablas 2016-2026 (ODS): https://www.ivap.euskadi.eus/contenidos/estadistica/122417_emal_tablas_estad/opendata/EMAL-2016-2026_es.ods
- EMAL — informe trimestral 2025T2 (PDF): https://www.euskadi.eus/contenidos/documentacion/122417_informe_emal_2025t2/es_def/Informe-EMAL-trimestral-062025.pdf
- OVJ — empleo económico: https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_empleo_econom/opendata/iovj-empleo-economico.csv
- OVJ — emancipación: https://opendata.euskadi.eus/contenidos/estadistica/gazte_adierazle_emanc_vivienda/opendata/iovj-emancipacion.csv
- Eustat — renta personal municipal (PX): https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp11s.px
- Eustat — renta personal por edad (PX): https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp03.px
- INE — afiliación SS (IOE 58015): https://ine.es/dyngs/IOE/operacion.htm?numinv=58015
- INE — aviso legal/licencia: https://www.ine.es/aviso_legal/
- Lanbide — informe anual afiliación: https://www.lanbide.euskadi.eus/estudios-estadisticas/-/estadistica/informe-anual-afiliacion/
- Etxebide — promociones (CSV): https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.csv
- Etxebide — promociones (XLS): https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.xls
- datos.gob.es — promociones Etxebide: https://datos.gob.es/en/catalogo/a16003011-promociones-de-etxebide-para-compra-y-alquiler-de-vivienda-protegida1
- EDYVI — tablas alquiler social (ODS): https://www.etxebide.euskadi.eus/contenidos/estadistica/ovv_v_edyvi_tablas_alquiler/opendata/Tablas_EDYVI_alquiler_2025-eus.ods
- Alokabide — registro contratos (European Data Portal): https://data.europa.eu/data/datasets/https-opendata-euskadi-eus-catalogo-registro-contratos-alokabide-sociedad-alquiler-s-del-2026-?locale=en
- Certificados energéticos — catálogo: https://opendata.euskadi.eus/catalogo/-/registro-de-certificados-de-eficiencia-energetica-de-euskadi/
- Certificados energéticos — API REST: https://opendata.euskadi.eus/api-energy-efficiency/?api=energy-efficiency
- datos.gob.es — certificados: https://datos.gob.es/en/catalogo/a16003011-registro-de-certificados-de-eficiencia-energetica-de-euskadi
- OSRM — documentación API: https://project-osrm.org/docs/v5.24.0/api/
- b5m Gipuzkoa — distancias municipios: https://b5m.gipuzkoa.eus/web5000/es/api-rest/distancia-entre-municipios
- b5m Gipuzkoa — CSV bulk: https://b5m.gipuzkoa.eus/datasets/GFA_DSET_DISTM_CSV.zip
- Moveuskadi — catálogo GTFS: https://opendata.euskadi.eus/catalogo/-/moveuskadi-datos-de-la-red-de-transporte-publico-de-euskadi-operadores-horarios-paradas-calendario-tarifas-etc/
- Moveuskadi — índice GTFS: https://opendata.euskadi.eus/transport/moveuskadi/data-index-gtfs.json

**Repositorio (solo lectura):** `docs/preguntas_analisis_profesional.md`, `docs/inventario_datos.md`, `docs/puntos_flacos_dataset.md`, `docs/fuentes_salario_joven.md`, `docs/fuentes_cartografia_empleo.md`, `docs/decision_salario_proxy.md`, `docs/contrato_datos_raw.md`.
