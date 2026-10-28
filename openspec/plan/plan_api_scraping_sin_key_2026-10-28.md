# Plan API/Scraping SIN KEY y SIN descarga directa

**Fecha:** 2026-10-28  
**Objetivo:** Cubrir gaps usando solo fuentes que el agente puede ejecutar directamente (API o scraping, sin registro ni descarga directa de Open Data).  
**Principio:** No imputar ni usar proxies. Si no hay dato real, marcar "sin dato".  
**Ejecución:** Solo planificación. No se ejecuta nada hasta autorización explícita.

---

## 1. Fuentes disponibles (sin key, sin descarga directa)

| # | Fuente | Tipo | Gap que cubre | Puntuación mejora datos crudos (0-10) | Justificación |
|---|---|---|---|---|---|
| A | Fotocasa endpoint interno (API no documentada) | API (sin key) | Anuncios en municipios pequeños (G2) | 3/10 | Puede dar más listings sin scraping HTML, pero la mayoría de municipios pequeños ya mostraron 0 resultados en scraping directo. Valor marginal. |
| B | OSM Overpass (API pública) | API (sin registro) | Contexto municipal: servicios a 500m (interpretación) | 2/10 | Alto valor para justificar conclusiones, pero no añade datos de precio/alquiler. Solo contexto. |
| C | SEPE/Lanbide API (si existe) o scraping web | API o scraping | Paro juvenil por municipio (G3) | 5/10 | Complementa `tasa_paro_lanbide_pct` con paro por edad. Si existe API, alto valor; si no, scraping más difícil. |
| D | Etxebide web scraping | Scraping | Vivienda protegida (VPO) para jóvenes | 3/10 | Oferta real alternativa a mercado libre, pero scraping de web (más frágil). No cubre alquiler de mercado. |
| E | Observatorio Vasco Vivienda (scraping PDF/tablas) | Scraping | Contexto de precios por comarca | 2/10 | Solo comarcal (no municipal), valor de contexto. Extracción de PDF puede ser frágil. |

**Puntuación media de mejora de datos crudos:** (3+2+5+3+2)/5 = **3.0/10**.

---

## 2. RA1 (ya cubierto)

- **API:** Eustat bankupx, INE (69301-69330, Atlas renta), INE salarios, RealtyAPI, Udalmap (si API).
- **Scraping:** Fotocasa HTML, Pisos.com HTML.

RA1 (10 pts) ya está cubierto con API+scraping. Las fuentes sin key/descarga directa son **complementarias**, no obligatorias.

---

## 3. Fuentes excluidas (requieren key o descarga directa)

| Fuente | Motivo de exclusión |
|---|---|
| Idealista RapidAPI | Requiere key del usuario (registro en RapidAPI). |
| EMAL fianzas (ODS) | Descarga directa de Open Data (consultar con profesora). |
| Etxebide VPO (CSV) | Descarga directa de Open Data (consultar con profesora). |
| SEPE/Lanbide (CSV) | Descarga directa de Open Data (consultar con profesora). |
| GTFS Euskadi (ZIP) | Descarga directa de Open Data (consultar con profesora). |
| Observatorio (PDF/CSV directo) | Descarga directa de Open Data (consultar con profesora). |
| Catastro API | Excluye País Vasco/Navarra. |
| Idealista oficial | Requiere empresa + CIF (no viable). |

---

## 4. Orden de ejecución recomendado (solo sin key, sin descarga directa)

1. C (SEPE/Lanbide API/scraping) — cubre paro juvenil (5/10).
2. A (Fotocasa endpoint interno) — valor marginal en anuncios (3/10).
3. D (Etxebide scraping) — alternativa VPO (3/10).
4. B (OSM Overpass) — contexto servicios (2/10).
5. E (Observatorio scraping) — contexto comarcal (2/10).

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