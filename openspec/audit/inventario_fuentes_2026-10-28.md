# Inventario de fuentes de datos — bigdata-vivienda-euskadi (2026-10-28)

**Leyenda:** Tipo = API / Scraping / Descarga directa. Automatizada = existe script en `extract/` o `transform/` que la ejecuta. Importancia = 0-10 sobre la data final.

## 1. Fuentes automatizadas (con script)

| Fuente | Tipo | Script | Importancia | Notas |
|---|---|---|---:|---|
| Eustat API (bankupx) | API | `extract/01_eustat_api.py` | 10 | Población, renta, PIB, tenencia (252 mun). |
| Eustat alquiler (ExtractorBlob CSV) | Descarga directa | `extract/02_eustat_alquiler.py` | 9 | Alquiler oficial 159/252 mun (63%). |
| Euskadi emancipación | Descarga directa | `extract/03_euskadi_emancipacion.py` | 6 | Jóvenes, coste acceso, Etxebide inscritos. |
| b5m Gipuzkoa geo | API + Descarga directa | `extract/04_b5m_geo.py` | 4 | Solo Gipuzkoa; límites + distancias. |
| Fotocasa scraping | Scraping | `extract/05_fotocasa_scraper.py` | 8 | Anuncios alquiler (470, 60 mun). |
| INE API (wstempus) | API | `extract/06_ine_api.py` | 9 | Población, hogares, urbanos. |
| INE salarios (EPA) | API | `extract/07_ine_salarios.py` | 5 | Solo nacional (sin desglose territorial). |
| Pisos.com scraping | Scraping | `extract/08_pisos_scraper.py` | 7 | Anuncios alquiler (218, 30 mun). |
| RealtyAPI (Idealista) | API (key) | `extract/09_realtyapi.py` | 4 | Solo 3 capitales, opcional. |
| Entity resolution | Transformación | `extract/entity_resolution.py` | 8 | Mapeo nombre→codigo_ine. |
| Euskadi geo (cartografía) | Descarga directa | `extract/euskadi_geo.py` | 7 | GeoJSON 252 mun + distancias capitales. |
| Fotocasa detalle | Scraping | `extract/fotocasa_detalle.py` | 6 | Enriquece 470 anuncios (planta, cert, etc.). |
| INE Atlas renta | Descarga directa (streaming) | `extract/ine_atlas_renta.py` | 9 | Rellena 51 mun faltantes (252 total). |
| Udalmap empleo | Descarga directa (Open Data) | `extract/udalmap_empleo.py` | 7 | Paro/actividad/ocupación (252 mun). |
| dim_municipios | Transformación | `transform/dim_municipios.py` | 10 | Tabla de verdad (252 mun). |
| Distancias haversine | Transformación | `transform/generar_distancias.py` | 9 | 63.504 pares (252×252). |
| Filtrado outliers | Transformación | `transform/filtrar_outliers.py` | 8 | Marca 8 outliers. |
| R1 dirigido (Fotocasa/Pisos) | Scraping dirigido | `transform/f4_pisos_dirigido.py` | 3 | Cobertura marginal (+12 Pisos). |
| EMAL (fianzas alquiler) | Descarga directa | `extract/10_opendata_bizilagun_etxebide.py` | 8 | 730 registros (2016-2025) por municipio. |
| Etxebide (vivienda protegida) | Descarga directa | `extract/10_opendata_bizilagun_etxebide.py` | 6 | 5040 registros (indicador 86). |
| Transporte GTFS (paradas) | Descarga directa | `extract/11_transporte_gtfs_paradas.py` | 5 | 252 municipios, 2635 paradas asignadas. |
| Fotocasa habitaciones | Scraping | `extract/13_scraping_habitaciones.py` | 7 | 155 anuncios (capitales+cabeceras). |
| Pisos habitaciones | Scraping | `extract/13_scraping_habitaciones.py` | 6 | 46 anuncios. |
| Enriquecimiento JSON anidado | Transformación | `extract/12_enriquecer_json_anidado.py` | 7 | 471+230 con ubicacion/equipamiento. |

## 2. Fuentes NO automatizadas (manuales / pendientes)

| Fuente | Tipo | Automatizada | Automatizable | Importancia | Notas |
|---|---|---|---|---:|---|
| SEPE/Lanbide paro | Descarga directa | No | Sí (requests + openpyxl) | 7 | Paro juvenil real (XLSX Open Data). |
| Observatorio Vasco Vivienda | Descarga directa (PDF/XLSX) | No | Parcial (XLSX sí, PDF frágil) | 5 | Contexto comarcal (EMAL, ECVI). |
| OSM Overpass | API | No (bloqueado 406) | No (bloqueado en este entorno) | 3 | Servicios a 500m (contexto). |
| Fotocasa endpoint interno | API (POST complejo) | No | Parcial (reverse-engineering frágil) | 2 | Marginal vs scraping HTML. |
| Idealista oficial | API (empresa+CIF) | No | No (no viable estudiante) | 1 | No viable para estudiante. |
| Catastro | API | No (excluye PV) | No (no aplicable) | 0 | No aplicable. |

## 5. Posibilidad de automatización

- **EMAL, Etxebide VPO, SEPE/Lanbide, GTFS:** automatizables con scripts de descarga directa (`requests` + `pandas`/`openpyxl`/`zipfile`). Trivial, ~1h cada uno.
- **Observatorio (XLSX):** automatizable; (PDF): frágil, depende de layout.
- **Fotocasa endpoint interno:** automatizable parcialmente (reverse-engineering POST body), pero frágil y de bajo valor frente al scraping HTML.
- **OSM Overpass:** bloqueado (406) en este entorno; no automatizable ahora.
- **Idealista oficial:** no viable (empresa + CIF).
- **Catastro:** no aplicable (excluye País Vasco/Navarra).

## 3. Resumen por tipo

| Tipo | Fuentes automatizadas | Fuentes no automatizadas | Importancia media (auto) |
|---|---:|---:|---:|
| API | 7 (Eustat, INE×2, b5m, RealtyAPI, entity, fotocasa_detalle*) | 2 (OSM, Idealista oficial) | 7.4 |
| Scraping | 5 (Fotocasa, Pisos, Fotocasa detalle, Fotocasa habitaciones, Pisos habitaciones) | 0 | 7.0 |
| Descarga directa | 9 (Eustat alquiler, Euskadi emancipación, b5m, Euskadi geo, INE Atlas, Udalmap, EMAL, Etxebide, GTFS) | 2 (SEPE, Observatorio) | 7.2 |
| Transformación | 5 (dim, haversine, filtrado, R1, enriquecimiento JSON) | 0 | 7.5 |

*Fotocasa detalle es scraping, no API.

## 4. Conclusión

- **Automatizadas:** 24 fuentes (API 7, Scraping 5, Descarga directa 9, Transformación 5).
- **No automatizadas:** 6 fuentes (SEPE/Lanbide, Observatorio, OSM, Fotocasa endpoint, Idealista oficial, Catastro).
- **Mayor importancia:** Eustat API (10), dim_municipios (10), INE Atlas renta (9), Eustat alquiler (9), distancias haversine (9), EMAL (8).
- **Menor importancia:** Catastro (0), Idealista oficial (1), Fotocasa endpoint interno (2), OSM (3).

Las fuentes no automatizadas de mayor valor (SEPE/Lanbide) son descarga directa de Open Data; requieren consulta con la profesora. Las API/scraping sin key disponibles (OSM, Fotocasa endpoint) tienen baja importancia (2-3). Nuevos datos cubren gaps de habitaciones, transporte, vivienda protegida y mercado oculto (EMAL).