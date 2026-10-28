# Plan API/Scraping vs Gaps de Auditoría (reauditoria_2026-10-28)

**Fecha:** 2026-10-28  
**Objetivo:** Mapear cada gap de la auditoría a las fuentes API/scraping disponibles y puntuar (0-10) cuánto cubre cada una.  
**Principio:** No imputar ni usar proxies. Si no hay dato real, marcar "sin dato".  
**Ejecución:** Solo planificación. No se ejecuta nada hasta autorización explícita.

---

## 1. Gaps de la auditoría (reauditoria_2026-10-28.md)

### P1 Crítico
| G1 | Alquiler oficial solo 159/252 (63.1%); 93 mun sin dato; sin n muestral. |
| G2 | Anuncios: cobertura municipal baja (71/252, 28.2%); solo 4 mun con n>=30. |
| G3 | tasa_paro_aprox_pct 100% NaN (usar Lanbide). |
| G4 | 51 mun de Araba con codigo_ine de 4 dígitos en distancias -> rompe join. |
| G5 | Outliers de €/m² sin depurar (superficies pequeñas/mal parseadas). |

### P2 Alto
| G6 | Temporal vs larga diferencia ~24% -> no mezclar. |
| G7 | Renta vs alquiler r≈0.28 (<0.3) -> documentar. |
| G8 | distancias_municipios.json solo 5.000/180.488 pares (2.77%). |
| G9 | Mezcla de años (anuncios 2026 vs resto 2024) sin año_fuente en todos. |
| G10 | Inconsistencia de flags temporal en Fotocasa (304 vs 316, 3 NaN). |
| G11 | anuncios_pisos.csv nombre_canonico vacío en 218/218. |
| G12 | HTML crudos no versionados (data/raw ignorado por git). |

### P3 Medio
| G13 | Superficie válida <100% (Pisos 85.3%). |
| G14 | distancias_capitales.csv raw 259 filas (7 fuera de dim). |
| G15 | Eustat 24 agregados a filtrar (si no, n=252 falso). |
| G16 | EPSG: origen 25830 -> 4326 declarado sin prueba explícita. |
| G17 | Araba solo 1 HTML frente a 12 Bizkaia / 4 Gipuzkoa. |

---

## 2. Fuentes API/Scraping disponibles y puntuación por gap (0-10)

| Fuente | G1 (alquiler 93) | G2 (anuncios) | G3 (paro) | G4 (Araba códigos) | G5 (outliers) | G6 (temporal/larga) | G7 (renta/alquiler) | G8 (distancias 2.77%) | G9 (años) | G10 (flags) | G11 (nombre_canonico) | G12 (HTML) | G13 (superficie) | G14 (259 filas) | G15 (Eustat agregados) | G16 (EPSG) | G17 (Araba 1 HTML) | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fotocasa endpoint interno (API sin key) | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | **9** |
| Idealista RapidAPI (API, key) | 5 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **11** |
| OSM Overpass (API, sin key) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| SEPE/Lanbide API o scraping (paro) | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** |
| Etxebide web scraping (VPO) | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** |
| Observatorio scraping (comarcal) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |

**Puntuación total por fuente (sobre 17 gaps):** Fotocasa endpoint 9/17, Idealista RapidAPI 11/17, OSM 0/17, SEPE/Lanbide 5/17, Etxebide 3/17, Observatorio 1/17.

---

## 3. Interpretación

- **La mayoría de gaps (G4-G17) son de corrección/transformación de datos existentes**, no de recopilación de nuevas fuentes. Ninguna fuente API/scraping los cubre (0 en todas).
- **Solo los gaps P1 de recopilación (G1, G2, G3) pueden cubrirse parcialmente** con fuentes API/scraping:
  - G1 (alquiler 93 sin dato): Idealista RapidAPI (5), Fotocasa endpoint (2), Etxebide VPO (3, como alternativa protegida).
  - G2 (anuncios cobertura): Idealista RapidAPI (6), Fotocasa endpoint (3).
  - G3 (paro approx NaN): SEPE/Lanbide (5).
- **OSM, Observatorio** no cubren ningún gap de la auditoría directamente (0 en todos). Su valor es de contexto/interpretación, no de cobertura de gaps.

---

## 4. Conclusión

Las fuentes API/scraping disponibles **cubren parcialmente solo 3 de los 17 gaps** (G1, G2, G3). Los 14 gaps restantes (G4-G17) requieren corrección/transformación de datos existentes, no nuevas fuentes.

Si el objetivo es cubrir gaps con API/scraping, la prioridad es:
1. Idealista RapidAPI (key del usuario) — mayor cobertura de G1 y G2 (11 pts).
2. SEPE/Lanbide API/scraping — cubre G3 (5 pts).
3. Fotocasa endpoint interno — valor marginal en G1/G2 (9 pts).

OSM, Etxebide y Observatorio no cubren gaps de la auditoría (0-3 pts) y son de contexto/interpretación.

---

## 5. Fuentes descartadas (descarga directa, consultar con profesora)

| Fuente | Motivo de descarte (solo API/scraping) |
|---|---|
| EMAL fianzas (ODS) | Descarga directa de Open Data. |
| Etxebide VPO (CSV) | Descarga directa de Open Data. |
| SEPE/Lanbide (CSV) | Descarga directa de Open Data. |
| GTFS (ZIP) | Descarga directa de Open Data. |
| Observatorio (PDF/CSV directo) | Descarga directa de Open Data. |
| Catastro API | Excluye País Vasco/Navarra. |

---

## 6. Orden de ejecución recomendado (solo API/scraping)

1. Idealista RapidAPI (si el usuario obtiene key) — mayor cobertura de G1/G2.
2. SEPE/Lanbide API/scraping — cubre G3.
3. Fotocasa endpoint interno — valor marginal en G1/G2.
4. OSM Overpass — contexto (no cubre gaps).
5. Etxebide scraping — alternativa VPO (no cubre gaps).
6. Observatorio scraping — contexto comarcal (no cubre gaps).

---

## 7. Verificación global (al cerrar cada fase)

- Código INE 100% en todas las fuentes nuevas.
- Municipios cubiertos vs 252 (documentar %).
- Sin proxies ni imputaciones.
- Tests actualizados con nuevos umbrales si procede.
- Informe de gaps actualizado en `openspec/audit/`.

---

## 8. Nota sobre documentación

Cada fase ejecutada generará:
- Script en `extract/`.
- Datos en `data/raw/` (CSV + JSON).
- Informe en `openspec/audit/` con métricas antes/después.
- Actualización de `openspec/plan/plan_mejora_*.md`.

No se ejecutará nada hasta autorización explícita del usuario.