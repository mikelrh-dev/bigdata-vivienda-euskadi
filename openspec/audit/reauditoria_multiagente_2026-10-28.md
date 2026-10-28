# Reauditoría multiagente — Framework de Dato Puro (post-plan crudos)

**Fecha:** 2026-10-28 (tercera pasada, tras plan crudos + fixes de dtype/encoding)
**Framework:** `framework_auditoria_completo2/03_framework_auditoria_dato_puro.md`
**Método:** subagentes fallaron por rate limit (HTTP 429); métricas verificadas directamente con pandas + pytest.
**Tests:** 57/57 en verde.

---

## 1. Métricas reales observadas (verificadas)

| Fuente | Registros | Municipios | % 252 | n>=30 | codigo_ine % |
|---|---:|---:|---:|---:|---:|
| anuncios_fotocasa | 471 | 61 | 24.2 | 3 | 99.6 |
| anuncios_pisos | 235 | 37 | 14.7 | 2 | 100.0 |
| anuncios_realtyapi | 139 | 3 | 1.2 | 3 | 100.0 |
| alquiler_municipal | 253 | 159 | 63.1 | — | 100.0 |
| eustat_renta_municipal | 98532 | 252 | 100.0 | — | 100.0 (post-filtro) |
| udalmap_empleo | 252 | 252 | 100.0 | — | 100.0 |
| educacion_centros | 1309 | 197 | 78.2 | — | 100.0 |
| salud_centros | 528 | 231 | 91.7 | — | 100.0 |
| serpavi_renta_municipal | 249 | 159 (con dato 2024) | 63.1 | — | 100.0 |
| lanbide_paro_juvenil | 252 | 252 | 100.0 | — | 100.0 |
| osrm_tiempos_capitales | 252 | 252 | 100.0 | — | 100.0 |
| distancias_haversine_252 | 63504 | 252 | 100.0 | — | 100.0 |
| distancias_municipios.json | 63504 | 252 | 100.0 | — | 100.0 (regenerado) |
| dim_municipios | 252 | 252 | 100.0 | — | 100.0 (00001 filtrado) |
| emancipacion_juventud | 866 | 0 | 0.0 | — | 0.0 (territorial) |

**Total fuentes automatizadas: 29.** Tests: 57/57.

---

## 2. Comparación con auditoría anterior (8.5/10)

| Dimensión | Anterior | Actual | Cambio |
|---|---:|---:|---|
| Cobertura anuncios | 3 | 3 | = (estructural) |
| Alquiler oficial | 6 | 6 | = (SERPAVI 0 nuevos) |
| Renta municipal | 10 | 10 | = |
| Paro municipal | 9.5 | 9.5 | = (Lanbide juvenil) |
| Distancias | 10 | 10 | = (OSRM + zfill + legacy) |
| Entity resolution | 9.5 | 9.5 | = (zfill + 00001 fix) |
| Calidad estadística | 8.5 | 8.5 | = (IQR por segmento) |
| Tests | 10 | 10 | = (57/57) |
| Trazabilidad | 8 | 8 | = (legacy JSON regenerado + leer_csv_seguro) |
| Automatización | 9.5 | 9.5 | = (29 fuentes) |
| Documentación | 9 | 9 | = |
| Presentación/Interpretación | 8.5 | 8.5 | = (tipologia + OSRM + paro juvenil) |

**Nueva media: ~8.5/10** (sin cambio respecto a la anterior; los fixes de dtype/encoding y tests crudos no suben nota pero mejoran robustez).

---

## 3. Veredicto de suficiencia (FASE 5)

1. **Ranking de 252 por coste de acceso con error <20%?** NO. Solo 5-7 municipios con n>=30 anuncios. Estructura del mercado vasco rural.

2. **Tasa de esfuerzo alquiler/renta para 252?** PARCIAL. Renta 252/252. Alquiler oficial 159/252. SERPAVI 159/249 (cross-check, 0 nuevos). 93 `sin_dato`.

3. **"Dónde hay trabajo y vivienda barata"?** MEJORADO. Paro válido (0 negativos) + paro juvenil Lanbide (252) + OSRM (minutos reales) + tipología 3 niveles (6/63/183). Respondible para capitales/comarcas y con clasificación tipológica para los 252.

---

## 4. Gaps cerrados vs pendientes

### Cerrados
- Araba 4-dígitos (zfill defensivo + leer_csv_seguro) ✓
- Legacy JSON 5000 pares (regenerado a 63.504) ✓
- Outlier flag sub-detecta (IQR por segmento) ✓
- Tipología de mercado (3 niveles) ✓
- Agregado 00001 en dim_municipios ✓
- Paro juvenil municipal (Lanbide) ✓
- Minutos reales de conducción (OSRM) ✓
- dtype/encoding robusto en transforms (leer_csv_seguro) ✓
- Tests crudos (3 nuevos, 57 total) ✓

### Pendientes (estructurales, no cerrables)
- Cobertura de anuncios (3/10): 80 municipios sin mercado de alquiler libre.
- Alquiler oficial (6/10): 93 sin dato. SERPAVI/EMAL cubren los mismos 159.
- Salario joven municipal: no existe. Proxy renta o `sin_dato`.
- Emancipación territorial (0 municipios): limitación del estudio.

---

## 5. Plan de corrección restante

**Hecho (esta pasada):** dtype/encoding + leer_csv_seguro + tests crudos + verificación.

**Pendiente (bajo esfuerzo):**
- Actualizar `informe_entity_resolution.csv` (contadores desfasados).
- Documentar mezcla de años (2026/2024/2025).

**Pendiente (alto valor de nota):**
- Docker Compose (HDFS + MongoDB).
- Modelado + operaciones PyMongo.
- Aggregation Pipeline.
- Gráficos + informe.

---

## Veredicto final

Proyecto en **~8.5/10**. Datos científicamente sólidos: 57/57 tests, paro válido y juvenil (252), OSRM real, SERPAVI cross-check, IQR por segmento, tipología 3 niveles, zfill corregido, dtype robusto. Gaps estructurales (anuncios 3/10, alquiler 6/10) son la realidad del mercado vasco rural, documentados como `sin_dato` sin imputación. El esfuerzo restante para subir nota está en infraestructura y análisis (HDFS/Kafka/MongoDB/Aggregation), no en más fuentes.
