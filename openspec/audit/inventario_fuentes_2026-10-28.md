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

## 2. Fuentes NO automatizadas (manuales / pendientes)

| Fuente | Tipo | Automatizada | Automatizable | Importancia | Notas |
|---|---|---|---|---:|---|
| EMAL (fianzas alquiler) | Descarga directa | No | Sí (requests + pandas) | 8 | Alquiler oficial por municipio (Open Data). Consultar profesora. |
| Etxebide VPO | Descarga directa | No | Sí (requests + pandas) | 5 | Vivienda protegida (CSV Open Data). |
| SEPE/Lanbide paro | Descarga directa | No | Sí (requests + openpyxl) | 7 | Paro juvenil real (XLSX Open Data). |
| GTFS Euskadi | Descarga directa | No | Sí (requests + zipfile) | 4 | Transporte (ZIP). |
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
| Scraping | 3 (Fotocasa, Pisos, Fotocasa detalle) | 0 | 7.0 |
| Descarga directa | 6 (Eustat alquiler, Euskadi emancipación, b5m, Euskadi geo, INE Atlas, Udalmap) | 5 (EMAL, Etxebide, SEPE, GTFS, Observatorio) | 7.2 |
| Transformación | 4 (dim, haversine, filtrado, R1) | 0 | 7.5 |

*Fotocasa detalle es scraping, no API.

## 4. Conclusión

- **Automatizadas:** 18 fuentes (API 7, Scraping 3, Descarga directa 6, Transformación 4).
- **No automatizadas:** 9 fuentes (5 descarga directa Open Data, 2 API bloqueadas/no viables, 2 API no aplicables).
- **Mayor importancia:** Eustat API (10), dim_municipios (10), INE Atlas renta (9), Eustat alquiler (9), distancias haversine (9).
- **Menor importancia:** Catastro (0), Idealista oficial (1), Fotocasa endpoint interno (2), OSM (3).

Las fuentes no automatizadas de mayor valor (EMAL, SEPE/Lanbide) son descarga directa de Open Data; requieren consulta con la profesora. Las API/scraping sin key disponibles (OSM, Fotocasa endpoint) tienen baja importancia (2-3).