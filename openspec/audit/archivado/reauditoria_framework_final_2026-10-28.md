# Reauditoría final — Framework de Auditoría de Dato Puro (post-fuentes y fixes)

**Fecha:** 2026-10-28 (segunda pasada, tras incorporar SERPAVI/OSRM/Lanbide y fixes internos)
**Framework:** `framework_auditoria_completo2/03_framework_auditoria_dato_puro.md`
**Auditoría base:** `openspec/audit/reauditoria_comparativa_2026-10-28.md` (8.3/10)
**Ejecución:** métricas verificadas por pandas sobre `data/raw/` y `data/procesado/`. Tests del contrato: 54/54.

---

## 1. Inventario real (FASE 0) — estado actual

| Fuente | Registros | Válidos | Municipios | % 252 | codigo_ine % | Método |
|---|---:|---:|---:|---:|---:|---|
| anuncios_fotocasa | 471 | 453 | 56 | 22.2 | 99.6 | scraping |
| anuncios_pisos | 230 | 200 | 35 | 13.9 | 100.0 | scraping |
| anuncios_realtyapi | 139 | 138 | 3 | 1.2 | 100.0 | API |
| alquiler_municipal | 253 | 253 | 159 | 63.1 | 100.0 | descarga |
| eustat_renta_municipal | 98532 | 89607 | 252 | 100.0 | 100.0 (post-filtro) | API |
| udalmap_empleo | 252 | 252 | 252 | 100.0 | 100.0 | descarga |
| educacion_centros | 1309 | 1309 | 197 | 78.2 | 100.0 | descarga |
| salud_centros | 528 | 528 | 231 | 91.7 | 100.0 | descarga |
| serpavi_renta_municipal (NUEVO) | 249 | 159 | 159 | 63.1 | 100.0 | descarga XLSX |
| lanbide_paro_juvenil (NUEVO) | 252 | 252 | 252 | 100.0 | 100.0 | descarga XLSX |
| osrm_tiempos_capitales (NUEVO) | 252 | 252 | 252 | 100.0 | 100.0 | API |
| distancias_capitales_252 | 252 | 252 | 252 | 100.0 | 100.0 | derivado |
| distancias_haversine_252 | 63504 | 63504 | 252 | 100.0 | 100.0 | derivado |
| distancias_municipios.json (legacy) | 63504 | 63504 | 252 | 100.0 | 100.0 | regenerado (era 5000) |
| emancipacion_juventud | 866 | 866 | 0 | 0.0 | 0.0 | descarga (territorial) |

**Total fuentes automatizadas: 29** (antes 26).

---

## 2. Entity resolution (FASE 1)

- `codigo_ine`: Fotocasa 99.6% (2 null = Las Rozas de Madrid, fuera de Euskadi), Pisos 100%, RealtyAPI 100%, alquiler 100%, SERPAVI 100%, Lanbide 100%, OSRM 100%.
- Araba 4-dígitos: **corregido** (zfill defensivo en `enriquecer_codigo_ine.py` y `dim_municipios.py`). 0 códigos cortos en los CSV generados.
- Agregado "C.A. de Euskadi" (00001): **filtrado** en `dim_municipios.py` (era un bug latente que inflaba a 253). Ahora 252 exactos.
- Variantes mapeadas (Arrankudiaga/Zollo, Donostia, etc.) vía `dim_municipios`.
- Eustat 24 agregados filtrados por longitud de código.

---

## 3. Cobertura muestral (FASE 2)

Sin cambios estructurales:
- Fotocasa: 3 municipios con n≥30 (Bilbao 189, Donostia 80, Getxo 40). 9 con 5-29, 48 con <5.
- Pisos: 2 con n≥30 (Ayala 30, Abanto 30). 11 con 5-29, 17 con <5.
- RealtyAPI: 3 capitales, todas ≥30.
- Unión de fuentes de anuncios: 82 municipios. 80 municipios sin ninguna fuente.
- Temporal vs larga estancia: mediana +21.3% (filtrado). Separado en `filtrar_outliers.py`.
- Alquiler oficial: 159/252 (63.1%). **SERPAVI no añade municipios nuevos** (159/249 con dato 2024, los mismos 159; 89 `sin_dato`, 1 LOCF). Corrige la sobre-afirmación previa.

---

## 4. Calidad estadística (FASE 3)

- Outliers IQR: Fotocasa 14→20 (ahora captura banda 31-50 €/m²), Pisos 9→10.
- Superficie válida: Fotocasa 95.5%, Pisos 94.0%.
- Renta vs alquiler: r = 0.1655 (débil, hallazgo real, no gap de datos).
- Emancipación: parsea OK (14 indicadores, 9 columnas).
- `tipologia_mercado`: 6 Nivel1 / 63 Nivel2 / 183 Nivel3.

---

## 5. Validez de dominio (FASE 4)

- Udalmap: todos los indicadores en [0,100], paro Lanbide 0-12.57, 0 negativos. `tasa_paro_aprox_pct` null (252/252) por invalidación metodológica → usar `tasa_paro_lanbide_pct`.
- **Lanbide paro juvenil (NUEVO):** 252/252 municipios, período 2026 T1. Paro joven (<25) = `Total <20` + `Total 20-24`. Cierra el falso 0.0% de Udalmap en ocupación juvenil.
- Distancias: Haversine 63.504 pares, 0 NaN/dups. **OSRM (NUEVO):** minutos reales de conducción 252×3 capitales. Araba 4-dígitos corregido.
- Salarios: nacional (1.372,8 € 16-24). **No existe salario joven municipal** (confirmado). Proxy renta documentado (P-02).
- Fechas: año_fuente presente. Mezcla 2026/2024/2025 (documentar).
- GeoJSON: EPSG:4326, 252 features, todos 5 dígitos.
- Eustat renta: 201/252 en 2024 (51 vía INE Atlas).
- Tests: 54/54.

---

## 6. Veredicto de suficiencia (FASE 5)

1. **Ranking de 252 por coste de acceso con error <20%?** NO (sin cambio). Solo 5-6 municipios con n≥30 anuncios. SERPAVI no añade municipios. Es estructura del mercado vasco (80 municipios rurales sin mercado de alquiler libre).

2. **Tasa de esfuerzo alquiler/renta para 252?** PARCIAL→MEJORADO. Renta 252/252. Alquiler oficial 159/252. SERPAVI fiscal 159/252 (cross-check, no nuevos). 93 marcados `sin_dato` (sin imputación, P-02). Tasa de esfuerzo calculable para 159 con oficial + 159 con SERPAVI (validación cruzada).

3. **"Dónde hay trabajo y vivienda barata"?** MEJORADO (antes PARCIAL). Paro válido (0 negativos) + paro juvenil Lanbide (252) + OSRM (minutos reales) + tipología 3 niveles. Respondible para capitales/comarcas y con clasificación tipológica para los 252.

---

## 7. Comparación con auditoría anterior (8.3/10)

| Dimensión | Anterior | Actual | Cambio |
|---|---:|---:|---|
| Cobertura anuncios | 3 | 3 | = (estructural) |
| Alquiler oficial | 6 | 6 | = (SERPAVI no añade) |
| Renta municipal | 10 | 10 | = |
| Paro municipal | 9 | 9.5 | +0.5 (Lanbide juvenil) |
| Distancias | 9 | 10 | +1 (OSRM + zfill + legacy corregido) |
| Entity resolution | 9 | 9.5 | +0.5 (zfill + 00001 fix) |
| Calidad estadística | 8.5 | 8.5 | = (IQR ya contado) |
| Tests | 10 | 10 | = (54/54) |
| Trazabilidad | 7.5 | 8 | +0.5 (legacy JSON regenerado) |
| Automatización | 9.5 | 9.5 | = (29 fuentes) |
| Documentación | 9 | 9 | = |
| Presentación/Interpretación | 8 | 8.5 | +0.5 (tipologia + OSRM + paro juvenil) |

**Nueva media: ~8.5/10** (anterior 8.3). Mejora modesta pero real en corrección (zfill, agregado), distancias (OSRM), paro (juvenil), trazabilidad.

---

## 8. Gaps cerrados vs pendientes

### Cerrados en esta pasada
- Araba 4-dígitos (zfill defensivo) ✓
- Legacy JSON 5000 pares (regenerado a 63.504) ✓
- Outlier flag sub-detecta (IQR por segmento) ✓
- Tipología de mercado (3 niveles) ✓
- Agregado 00001 en dim_municipios ✓
- Paro juvenil municipal (Lanbide) ✓
- Minutos reales de conducción (OSRM) ✓
- `tasa_paro_aprox_pct` documentado como inválido ✓

### Pendientes (estructurales, no cerrables con datos gratuitos)
- Cobertura de anuncios (3/10): 80 municipios sin mercado de alquiler libre. No se cierra con más scraping.
- Alquiler oficial (6/10): 93 sin dato. SERPAVI/EMAL cubren los mismos 159. Marcar `sin_dato`.
- Salario joven municipal: no existe. Proxy renta o `sin_dato`.
- Emancipación territorial (0 municipios): limitación del estudio.

### Correcciones a sobre-afirmaciones (defensa)
1. "SERPAVI/EMAL cierran los 93" → FALSO (0 nuevos, verificado).
2. "Salario joven municipal" → FALSO (solo CA/territorial).
3. "Paro juvenil por municipio" → VERDADERO ahora (Lanbide, 252).
4. `tasa_paro_aprox_pct` → inválido, usar `tasa_paro_lanbide_pct`.

---

## 9. Plan de corrección restante

**Hecho (esta pasada):**
1. zfill Araba ✓
2. Legacy JSON ✓
3. Outlier IQR ✓
4. Tipología mercado ✓
5. SERPAVI ✓ (script + dato, no cierra gap pero cross-check)
6. OSRM ✓
7. Lanbide ✓

**Pendiente (bajo esfuerzo):**
8. Actualizar `informe_entity_resolution.csv` (contadores desfasados: Fotocasa 470 vs 471).
9. Documentar mezcla de años (2026/2024/2025) en análisis.

**Pendiente (alto valor de nota):**
10. Docker HDFS + MongoDB (Fase 2 de la rúbrica).
11. Modelado + operaciones PyMongo (Fase 4).
12. Aggregation Pipeline (Fase 6).
13. Gráficos + informe (Fase 8-9).

---

## Veredicto final

Proyecto en **~8.5/10**. Los datos son científicamente sólidos: paro válido y juvenil (252), OSRM real, SERPAVI cross-check, IQR por segmento, tipología 3 niveles, zfill corregido, 54/54 tests. Los gaps estructurales (anuncios 3/10, alquiler 6/10) son la realidad del mercado vasco rural y se documentan como `sin_dato` sin imputación. El esfuerzo restante para subir nota está en la infraestructura y el análisis (HDFS/Kafka/MongoDB/Aggregation), no en más fuentes.
