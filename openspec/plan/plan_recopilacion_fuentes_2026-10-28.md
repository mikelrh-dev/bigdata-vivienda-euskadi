# Plan de Recopilación de Fuentes Adicionales (sin proxies, sin infraestructura)

**Fecha:** 2026-10-28  
**Objetivo:** Cubrir los gaps de información con datos crudos y reales, documentando cada fuente.  
**Principio:** No imputar ni usar proxies. Si no hay dato real, marcar "sin dato".  
**Ejecución:** Solo planificación. No se descarga ni modifica nada hasta autorización explícita.

---

## 1. Fuentes priorizadas (agente puede obtener directamente)

### R2a — EMAL Fianzas de Alquiler (precio real por municipio)
- **Fuente:** Estadística del Mercado de Alquiler (Gobierno Vasco) — fianzas depositadas.
- **URL:** https://www.euskadi.eus/contenidos/estadistica/122417_emal_tablas_estad/opendata/EMAL-2016-2025_es.ods (verificada 200 OK).
- **Quién obtiene:** Agente (descarga directa, sin registro).
- **Gap que cubre:** 93 municipios sin alquiler oficial (Eustat solo publica n≥10 contratos). EMAL puede tener fianzas reales para esos municipios.
- **Campos clave:** renta media €/mes, mediana, P25, P75, por municipio/territorio y tamaño.
- **Archivos a crear:** `extract/10_emal_fianzas.py`, `data/raw/emal_fianzas.csv`, `data/raw/emal_fianzas.json`.
- **Verificación:** filas por municipio, % cobertura sobre 252, n muestral si está disponible, codigo_ine al 100%.
- **Riesgo:** EMAL puede estar a nivel de territorio/tamaño de municipio, no municipal exacto. Si es así, documentar y no imputar.

### R2b — Etxebide VPO Promociones (vivienda protegida para jóvenes)
- **Fuente:** Open Data Euskadi — promociones Etxebide.
- **URL:** https://www.euskadi.eus/contenidos/dataset/promociones_etxebide/opendata/promociones.csv (verificar).
- **Quién obtiene:** Agente (descarga directa).
- **Gap que cubre:** Emancipación juvenil — alternativa real a mercado libre (VPO en alquiler/venta, alojamientos dotacionales).
- **Campos clave:** tipo de promoción, régimen (alquiler/venta), coordenadas UTM, municipio, número de viviendas.
- **Archivos a crear:** `extract/11_etxebide_vpo.py`, `data/raw/etxebide_vpo.csv`, `data/raw/etxebide_vpo.json`.
- **Verificación:** municipios cubiertos, código INE 100%, coordenadas válidas.
- **Riesgo:** Puede no tener precio exacto; documentar como "oferta protegida" sin precio.

### R2c — SEPE/Lanbide Open Data (paro por municipio y grupo de edad)
- **Fuente:** SEPE/Lanbide Open Data.
- **URL:** Buscar en opendata.euskadi.eus (paro registrado por municipio y edad).
- **Quién obtiene:** Agente (descarga directa, sin registro).
- **Gap que cubre:** "Dónde hay trabajo" — paro juvenil (16-24, 25-29) por municipio, complementando `tasa_paro_lanbide_pct`.
- **Campos clave:** municipio, grupo de edad, paro registrado, fecha.
- **Archivos a crear:** `extract/12_lanbide_paro_edad.py`, `data/raw/lanbide_paro_edad.csv`, `data/raw/lanbide_paro_edad.json`.
- **Verificación:** municipios cubiertos, grupo de edad presente, código INE 100%, sin negativos.
- **Riesgo:** Puede estar solo a nivel territorial, no municipal. Si es así, documentar.

### R2d — OSM Overpass (servicios a 500m del municipio)
- **Fuente:** OpenStreetMap Overpass API.
- **URL:** https://overpass-api.de/api/interpreter (sin registro).
- **Quién obtiene:** Agente (consulta directa).
- **Gap que cubre:** Interpretación — justificar "por qué este municipio es mejor" con datos reales (supermercados, ambulatorios, paradas de transporte).
- **Campos clave:** tipo de servicio, coordenadas, distancia al centroide municipal.
- **Archivos a crear:** `extract/13_osm_servicios.py`, `data/raw/osm_servicios_municipios.csv`, `data/raw/osm_servicios_municipios.json`.
- **Verificación:** servicios por municipio, coordenadas válidas, sin duplicados.
- **Riesgo:** Consulta pesada; limitar a municipios objetivo (capitales + comarcas principales) o centroides.

### R2e — GTFS Euskadi (tiempo a capitales en transporte público)
- **Fuente:** Open Data Euskadi — GTFS (Euskotren, autobuses).
- **URL:** Buscar en opendata.euskadi.eus (GTFS feeds).
- **Quién obtiene:** Agente (descarga directa).
- **Gap que cubre:** Interpretación — tiempo real a Bilbao/Donostia/Vitoria en transporte público (no solo distancia Haversine).
- **Campos clave:** parada origen, parada destino, tiempo de viaje, modo.
- **Archivos a crear:** `extract/14_gtfs_tiempos.py`, `data/raw/gtfs_tiempos_capitales.csv`, `data/raw/gtfs_tiempos_capitales.json`.
- **Verificación:** municipios cubiertos, tiempos válidos, código INE 100%.
- **Riesgo:** Procesamiento pesado; limitar a municipios objetivo o calcular matriz de tiempos.

### R2f — Observatorio Vasco de la Vivienda (precios por comarca)
- **Fuente:** Observatorio Vasco de la Vivienda (informes trimestrales).
- **URL:** Buscar en euskadi.eus (informes de precios m² por comarca).
- **Quién obtiene:** Agente (descarga de PDF/CSV público).
- **Gap que cubre:** Contexto de precios por comarca (complementa, no municipal).
- **Campos clave:** comarca, precio m², trimestre.
- **Archivos a crear:** `extract/15_observatorio_vivienda.py`, `data/raw/observatorio_vivienda_comarcas.csv`, `data/raw/observatorio_vivienda_comarcas.json`.
- **Verificación:** comarcas cubiertas, precios válidos.
- **Riesgo:** Puede ser solo PDF; requiere extracción de tablas (pdfplumber). Si no es parseable, documentar como fuente consultada.

---

## 2. Fuente opcional (requiere acción del usuario)

### R2g — Idealista RapidAPI (anuncios con lat/lng)
- **Fuente:** RapidAPI Idealista7 (idealista7.p.rapidapi.com).
- **URL:** https://rapidapi.com/ (registro con email).
- **Quién obtiene:** Usuario (debe crear cuenta y obtener API key; 200 req/mes gratis).
- **Gap que cubre:** Cobertura de anuncios (83/252) y coordenadas exactas (lat/lng) para análisis espacial.
- **Campos clave:** precio, m², habitaciones, lat/lng, municipio, locationId.
- **Archivos a crear:** `extract/16_idealista_rapidapi.py`, `data/raw/idealista_rapidapi.csv`, `data/raw/idealista_rapidapi.json`.
- **Verificación:** municipios cubiertos, coordenadas válidas, código INE 100%.
- **Riesgo:** Requiere locationId por municipio; rate limit 200 req/mes. Si no se obtiene key, descartar.

---

## 3. Fuentes descartadas

| Fuente | Motivo de descarte |
|---|---|
| Catastro API | Excluye País Vasco y Navarra; no cubre Euskadi. |
| Idealista oficial (developers.idealista.com) | Requiere empresa + CIF + semanas de espera; no viable para clase. |
| Apify Idealista scraper | Coste ($5 free credit) y no necesario si RapidAPI funciona. |
| Fotocasa endpoint interno | Requiere descubrimiento con DevTools; scraping HTML ya funciona. |

---

## 4. Orden de ejecución recomendado

1. R2a (EMAL) — mayor valor, sin registro.
2. R2b (Etxebide VPO) — alto valor para emancipación.
3. R2c (SEPE/Lanbide paro por edad) — complementa paro.
4. R2d (OSM) — contexto para interpretación.
5. R2e (GTFS) — contexto de transporte.
6. R2f (Observatorio) — contexto comarcal.
7. R2g (Idealista RapidAPI) — solo si el usuario obtiene key.

---

## 5. Verificación global (al cerrar cada fase)

- Código INE 100% en todas las fuentes nuevas.
- Municipios cubiertos vs 252 (documentar %).
- Sin proxies ni imputaciones.
- Tests actualizados con nuevos umbrales si procede.
- Informe de gaps actualizado en `openspec/audit/`.

---

## 6. Nota sobre documentación

Cada fase ejecutada generará:
- Script en `extract/`.
- Datos en `data/raw/` (CSV + JSON).
- Informe en `openspec/audit/` con métricas antes/después.
- Actualización de `openspec/plan/plan_mejora_*.md`.

No se ejecutará nada hasta autorización explícita del usuario.