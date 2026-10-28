# Plan de Recopilación API/Scraping (sin descargas directas)

**Fecha:** 2026-10-28  
**Objetivo:** Cubrir gaps con fuentes que cumplen RA1 (API o scraping). Las descargas directas se consultan con la profesora antes de usarlas.  
**Principio:** No imputar ni usar proxies. Si no hay dato real, marcar "sin dato".  
**Ejecución:** Solo planificación. No se ejecuta nada hasta autorización explícita.

---

## 1. Fuentes API/Scraping y puntuación de cobertura de gaps (0-10)

| # | Fuente | Tipo | Gap que cubre | Puntuación | Justificación |
|---|---|---|---|---|---|
| R3a | Fotocasa endpoint interno (API no documentada) | API (sin key) | Anuncios en municipios pequeños (93 sin alquiler) | 4/10 | Puede dar más listings sin scraping HTML, pero la mayoría de municipios pequeños ya mostraron 0 resultados en scraping directo. Valor marginal. |
| R3b | Idealista RapidAPI (API) | API (key del usuario) | Anuncios + lat/lng en municipios pequeños | 6/10 | Mayor cobertura y coordenadas exactas, pero requiere key y no garantiza municipios pequeños (200 req/mes). |
| R3c | OSM Overpass (API pública) | API (sin registro) | Contexto municipal: servicios a 500m (supermercados, ambulatorios, transporte) | 7/10 | Alto valor para interpretación/conclusiones, sin registro, sin coste. Limitar a municipios objetivo para no sobrecargar. |
| R3d | SEPE/Lanbide API (si existe) o scraping web | API o scraping | Paro juvenil por municipio (16-24, 25-29) | 5/10 | Complementa `tasa_paro_lanbide_pct`. Si existe API, alto valor; si no, scraping más difícil. |
| R3e | Etxebide web scraping | Scraping | Vivienda protegida (VPO) en alquiler/venta para jóvenes | 4/10 | Oferta real alternativa a mercado libre, pero scraping de web (más frágil). |
| R3f | Observatorio Vasco Vivienda (scraping PDF/tablas) | Scraping | Contexto de precios por comarca | 3/10 | Solo comarcal (no municipal), valor de contexto. Extracción de PDF puede ser frágil. |

**Puntuación media de cobertura de gaps:** (4+6+7+5+4+3)/6 = **4.8/10**.

---

## 2. Fuentes ya cumplidas (RA1)

- **API:** Eustat bankupx, INE (69301-69330, Atlas renta), INE salarios, RealtyAPI, Udalmap (si API).
- **Scraping:** Fotocasa HTML, Pisos.com HTML.

RA1 (10 pts) ya está cubierto con API+scraping. Las fuentes R3a-R3f son **complementarias**, no obligatorias.

---

## 3. Fuentes descartadas (descarga directa, consultar con profesora)

| Fuente | Motivo de descarte (solo API/scraping) |
|---|---|
| EMAL fianzas (ODS) | Descarga directa de Open Data. |
| Etxebide VPO (CSV) | Descarga directa de Open Data. |
| SEPE/Lanbide (CSV) | Descarga directa de Open Data. |
| GTFS Euskadi (ZIP) | Descarga directa de Open Data. |
| Observatorio (PDF/CSV directo) | Descarga directa de Open Data. |
| Catastro API | Excluye País Vasco/Navarra. |

---

## 4. Orden de ejecución recomendado (solo API/scraping)

1. R3c (OSM Overpass) — alto valor, sin registro, sin coste.
2. R3a (Fotocasa endpoint interno) — prueba sin key, valor marginal.
3. R3d (SEPE/Lanbide API/scraping) — verificar si existe API primero.
4. R3e (Etxebide scraping) — scraping de web.
5. R3f (Observatorio scraping) — scraping de PDF/tablas.
6. R3b (Idealista RapidAPI) — solo si el usuario obtiene key.

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