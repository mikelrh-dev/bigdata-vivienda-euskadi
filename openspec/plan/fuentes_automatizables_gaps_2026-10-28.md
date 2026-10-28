# Fuentes automatizables para cerrar gaps — bigdata-vivienda-euskadi (2026-10-28)

**Objetivo:** Recordar de dónde obtener más datos para cerrar los gaps persistentes, sea descarga directa, scraping o API, siempre que se pueda automatizar.

---

## 1. Gaps persistentes

- Cobertura municipal anuncios (75/252; solo 5 con n≥30).
- Alquiler oficial (159/252; 93 sin dato).
- Paro municipal (solo Lanbide válido; aprox NaN).
- Salario solo nacional (no municipal).
- 169 mun sin anuncios.
- Araba 4-dígitos (54) en distancias.
- EPSG sin prueba explícita.
- Eustat 24 agregados sin filtrar.

---

## 2. Fuentes ya automatizadas (cubren gaps)

| Fuente | Script | Gap que cubre | Estado |
|---|---|---|---|
| EMAL (fianzas) | `extract/10_opendata_bizilagun_etxebide.py` | Alquiler oficial por municipio (730 reg, 2016-2025) | ✅ Hecho |
| Etxebide (solicitudes) | `extract/10_opendata_bizilagun_etxebide.py` | Demanda vivienda protegida (5040 reg) | ✅ Hecho |
| GTFS (paradas) | `extract/11_transporte_gtfs_paradas.py` | Conectividad transporte (252 mun, 2635 paradas) | ✅ Hecho |
| Habitaciones | `extract/13_scraping_habitaciones.py` | Piso compartido (Fotocasa 155 + Pisos 46) | ✅ Hecho |
| INE Atlas renta | `extract/ine_atlas_renta.py` | Rellena 51 mun faltantes (252 total) | ✅ Hecho |
| Eustat (renta, población, PIB, tenencia) | `extract/01_eustat_api.py` | Base socioeconómica | ✅ Hecho |
| Fotocasa scraping | `extract/05_fotocasa_scraper.py` | Anuncios alquiler (470, 60 mun) | ✅ Hecho |
| Pisos.com scraping | `extract/08_pisos_scraper.py` | Anuncios alquiler (218, 30 mun) | ✅ Hecho |
| Udalmap empleo | `extract/udalmap_empleo.py` | Paro/actividad/ocupación (252 mun) | ✅ Hecho |
| Euskadi geo (cartografía) | `extract/euskadi_geo.py` | GeoJSON 252 mun + distancias capitales | ✅ Hecho |
| Euskadi emancipación | `extract/03_euskadi_emancipacion.py` | Jóvenes, coste acceso, Etxebide inscritos | ✅ Hecho |
| INE API (wstempus) | `extract/06_ine_api.py` | Población, hogares, urbanos | ✅ Hecho |
| INE salarios (EPA) | `extract/07_ine_salarios.py` | Salarios (nacional) | ✅ Hecho |
| RealtyAPI (Idealista) | `extract/09_realtyapi.py` | Anuncios (3 capitales, opcional) | ✅ Hecho |
| b5m Gipuzkoa geo | `extract/04_b5m_geo.py` | Solo Gipuzkoa; límites + distancias | ✅ Hecho |
| Fotocasa detalle | `extract/fotocasa_detalle.py` | Enriquece 470 anuncios | ✅ Hecho |
| Entity resolution | `extract/entity_resolution.py` | Mapeo nombre→codigo_ine | ✅ Hecho |
| dim_municipios | `transform/dim_municipios.py` | Tabla de verdad (252 mun) | ✅ Hecho |
| Distancias haversine | `transform/generar_distancias.py` | 63.504 pares (252×252) | ✅ Hecho |
| Filtrado outliers | `transform/filtrar_outliers.py` | Marca 8 outliers | ✅ Hecho |
| R1 dirigido | `transform/f4_pisos_dirigido.py` | Cobertura marginal (+12 Pisos) | ✅ Hecho |
| Enriquecimiento JSON anidado | `extract/12_enriquecer_json_anidado.py` | 471+230 con ubicacion/equipamiento | ✅ Hecho |
| Metadata + fingerprint | `extract/14_add_metadata_fingerprint.py` | _metadata y property_fingerprint | ✅ Hecho |
| GeoJSON 2dsphere | `extract/15_add_geojson.py` | location para Mongo (Fotocasa 471/471) | ✅ Hecho |

---

## 3. Fuentes automatizables ahora (no implementadas)

| Fuente | Tipo | Gap que cubre | Esfuerzo | Prioridad |
|---|---|---|---|---|
| **SEPE/Lanbide (paro juvenil)** | Descarga directa (XLSX, Open Data Euskadi) | Paro municipal real (solo Lanbide válido, aprox NaN) | Bajo (2-3 h) | Alta |
| **Observatorio Vasco Vivienda (EMAL/ECVI)** | Descarga directa (XLSX/PDF, Open Data Euskadi) | Contexto comarcal (precios contratos vs oferta) | Bajo-medio (3-4 h) | Media |
| **Udalmap indicadores adicionales** | Descarga directa (Open Data Euskadi) | Más indicadores municipales (vivienda, empleo, etc.) | Bajo (2 h) | Media |
| **Eustat alquiler por sección censal** | Transformación (ya parseado) | Granularidad intra-municipal | Bajo (1 h) | Baja |

---

## 4. Fuentes no automatizables / no viables

| Fuente | Motivo |
|---|---|
| OSM Overpass | Bloqueado (406) en este entorno. |
| Fotocasa endpoint interno | POST complejo, frágil, bajo valor vs scraping HTML. |
| Idealista oficial | Requiere empresa + CIF (no viable estudiante). |
| Catastro | Excluye País Vasco/Navarra. |

---

## 5. Gaps que no requieren nuevas fuentes (corrección de datos existentes)

| Gap | Acción | Esfuerzo |
|---|---|---|
| Araba 4-dígitos (54) | Corregir en `transform/enriquecer_codigo_ine.py`. | Bajo |
| EPSG sin prueba | Verificar con prueba explícita. | Bajo |
| Eustat 24 agregados | Filtrar en transform. | Bajo |
| Salario solo nacional | Usar renta como proxy (documentado). | N/A |
| Temporal vs larga ~21% | Separar en agregaciones. | Bajo |
| Renta vs alquiler r≈0.27 | Documentar (no explica precio). | N/A |
| 169 mun sin anuncios | Marcar "sin dato de portal" (limitación estructural). | N/A |

---

## 6. Conclusión

Las únicas fuentes automatizables de alto valor que aún no tenemos son **SEPE/Lanbide (paro juvenil)** y **Observatorio (contexto comarcal)**. El resto de gaps se cierran con corrección de datos existentes, no con nuevas fuentes.

**Prioridad recomendada:** SEPE/Lanbide (alto impacto, bajo esfuerzo) → Observatorio (medio impacto) → Udalmap indicadores adicionales (bajo impacto).