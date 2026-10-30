# Auditoría spec-vs-proyecto — bigdata-vivienda-euskadi

**Fecha:** 2026-10-30
**Modo:** Read-only (auditoría directa, sin subagentes por rate limit)
**Fuente de verdad:** OpenSpec specs (contrato-reto, extraccion-datos, almacenamiento-y-streaming, mongodb-y-analisis, presentacion-de-resultados) + PDF/DOCX

---

## 1. Extracción de datos (extraccion-datos/spec.md)

| Req | Estado | Evidencia |
|---|---|---|
| EXTRACCION-01 (API + scraping) | ✅ CUMPLE | 35 scripts en `extract/`: API (01_eustat, 02_eustat_alquiler, 06_ine, 07_ine_salarios, 16_serpavi, 17_osrm, 18_lanbide, 22_geo_areas, 23_certificados) + scraping (05_fotocasa, 08_pisos, 09_realtyapi). HTML crudo preservado en `data/raw/html_fotocasa/` (101 páginas). Raw JSON/CSV con metadata. |
| EXTRACCION-02 (≥3 fuentes independientes) | ✅ CUMPLE | Eustat, INE, euskadi.eus, b5m, Fotocasa, Pisos.com, RealtyAPI, SERPAVI, OSRM, Lanbide. Fallo de una no aborta el resto (main_ingest.py con modo replay-raw). |
| FORMATO-01 (JSON/CSV con metadata) | ⚠️ PARCIAL | 60 JSONs en raw; 9 sin fuente/fecha_extraccion (documentado como anomalía histórica). Encoding: 1 archivo Latin-1 (etxebide_indicador_86.csv). Resto UTF-8-sig. |
| COMPLEMENTARIOS-01 (salarios + población) | ✅ CUMPLE | INE EPA salarios (06, 07), OVJ 1.564€, Eustat población (01), Lanbide paro (18), afiliación SS, ocupación juvenil. Valores reales, no simulados (P-02). |
| PYTHON-01 (todo en Python, venv) | ✅ CUMPLE | 35 scripts Python, requirements.txt, .venv funcional. |

**Veredicto extracción:** 4/5 CUMPLE, 1 PARCIAL (FORMATO-01 por metadata/encoding documentados). Nota: ~9/10.

---

## 2. Almacenamiento y streaming (almacenamiento-y-streaming/spec.md)

| Req | Estado | Evidencia |
|---|---|---|
| HDFS-01 (originales + procesados, recuperación) | ❌ NO CUMPLE | Sin docker-compose, sin HDFS config, sin scripts de subida/recuperación. `data/raw/` y `data/procesado/` existen localmente pero no en HDFS. |
| KAFKA-01 (productor + consumidor Python) | ❌ NO CUMPLE | Sin scripts Kafka, sin productor/consumidor. |
| INTEGRACION-01 (flujo completo a MongoDB) | ❌ NO CUMPLE | Sin pipeline end-to-end. No hay conexión entre componentes. |

**Veredicto almacenamiento/streaming:** 0/3 CUMPLE. **Fuera de alcance actual** (usuario lo quitó del análisis). Pendiente para Fase 4-8.

---

## 3. MongoDB y análisis (mongodb-y-analisis/spec.md)

| Req | Estado | Evidencia |
|---|---|---|
| MODELO-01 (modelo justificado, relaciones) | ❌ NO CUMPLE | Sin colecciones MongoDB, sin modelo documental, sin justificación embedding vs referencing. |
| PYMONGO-01 (insert, update, delete, verify) | ❌ NO CUMPLE | Sin scripts PyMongo. Sin insert_one/find/update_one/delete. |
| CONSULTAS-01 (campos anidados, arrays) | ❌ NO CUMPLE | Sin consultas MongoDB. |
| AGREGACION-01 (≥4 etapas) | ❌ NO CUMPLE | Sin Aggregation Pipeline. Agregaciones actuales son pandas-based (no MongoDB). |
| LIMPIEZA-01 (incompletos, duplicados, incorrectos) | ✅ CUMPLE | `unificar_anuncios.py` (dedup por portal+id_anuncio + fingerprint cross-portal), `corregir_empleo.py` (validación rangos), `normalizar_json_crudos.py` (inyección metadata, zfill). `filtrar_outliers.py` (marcado es_outlier). |
| TRANSFORM-01 (transformaciones en MongoDB) | ❌ NO CUMPLE | Transformaciones en pandas, no en MongoDB. |
| INDICES-01 (índice justificado + explain) | ❌ NO CUMPLE | Sin índices MongoDB. |
| TRANSACCIONES-01 (atomicidad multidocumento) | ❌ NO CUMPLE | Sin transacciones. |
| DISTRIBUIDA-01 (replica sets/sharding) | ❌ NO CUMPLE | Solo conceptual, no implementado. |
| PYMONGO-PRO-01 (proyecto profesional) | ❌ NO CUMPLE | Sin conexión reutilizable, sin manejo de errores PyMongo, sin README de ejecución Mongo. |
| VALIDACION-01 (schema validation) | ⚠️ PARCIAL | Contract tests en `test_contrato.py` (54 passed) validan schema de datos, pero no via JSON Schema de MongoDB. |

**Veredicto MongoDB/análisis:** 1/11 CUMPLE (LIMPIEZA-01), 1 PARCIAL (VALIDACION-01), 9 NO CUMPLE. **Fuera de alcance actual** (usuario lo quitó). Pendiente para Fase 6-7.

---

## 4. Presentación de resultados (presentacion-de-resultados/spec.md)

| Req | Estado | Evidencia |
|---|---|---|
| GRAFICOS-01 (≥3 tipos: barras, dispersión, boxplot) | ✅ CUMPLE | `data/resultados/`: 12 PNGs (bar charts, scatter, boxplot, heatmaps) + 2 dashboards HTML. Scripts: `generar_dashboard_completo.py`, `generar_dashboard_visual.py`, `generar_graficos_*.py`. |
| DATOS-PYMONGO-01 (gráficos desde PyMongo) | ❌ NO CUMPLE | Gráficos generados desde pandas/CSV, no desde consultas PyMongo (no hay Mongo). |
| PRESENTACION-01 (títulos, unidades, leyendas, comparación) | ✅ CUMPLE | Dashboards HTML con títulos, ejes, leyendas. `mapa_esquema_silver.html` con esquema. |
| INTERPRETACION-01 (≥3 resultados con causa e implicación) | ✅ CUMPLE | `docs/informe_preguntas_respuesta.md` (42 preguntas, 8.2/10), `docs/metodologia.md` (IDW, salario ajustado, tensión social), `docs/gaps_misconceptions_errores.md`. |
| CONCLUSION-01 (municipios concretos + indicadores) | ✅ CUMPLE | 6 robustos identificados (Bilbao 239, Donostia 130, Vitoria 48, Getxo 40, Abanto 31, Ayala 30). Tipología Nivel1/2/3. Conclusión documentada en informe_preguntas_respuesta.md. |

**Veredicto presentación:** 4/5 CUMPLE, 1 NO CUMPLE (DATOS-PYMONGO-01, depende de Mongo). Nota: ~8/10 (sin Mongo).

---

## 5. Prohibiciones (P-01 a P-08, contrato-reto/spec.md)

| Prohibición | Estado | Evidencia |
|---|---|---|
| P-01 (no compraventa como eje) | ✅ COMPLIANT | Eje principal es alquiler (anuncios_unificados, alquiler_municipal). Compraventa (ECVI) es complementario en `comparativa_compra_alquiler_af.csv`, no eje. |
| P-02 (no simular valores) | ✅ COMPLIANT | Salarios: INE EPA (1.372€) + OVJ (1.564€). Renta joven: proxy documentado con ratio 0,3534 (estimación transparente, no simulación). Alquiler: Eustat real. Población: Eustat real. Sin valores inventados. |
| P-03 (no usar INE alquiler para Euskadi) | ✅ COMPLIANT | Alquiler proviene de Eustat (`alquiler_municipal.csv`, 159/252 directo + 93 comarca). INE alquiler no usado. Documentado en P-03. |
| P-04 (no contar etapa única cuando exige agregación) | ❌ VIOLATION | AGREGACION-01 exige ≥4 etapas. No hay Aggregation Pipeline implementado (pandas-based). Si se marca como cubierto, sería violación. Actualmente no se marca como cubierto (spec dice "Pendiente"). |
| P-05 (no gráficos con valores tecleados) | ✅ COMPLIANT | Gráficos generados desde CSVs reales (pandas/matplotlib). Sin valores hardcoded en código de gráficos. |
| P-06 (todo en Python) | ✅ COMPLIANT | 35 scripts extract + 39 transform, todos Python. Requirements.txt. Venv funcional. |
| P-07 (no credenciales en repo) | ✅ COMPLIANT | `.env` y `api.txt` en `.gitignore`. No credenciales commiteadas. |
| P-08 (no marcar cubierto sin verificación) | ⚠️ PARCIAL | Contract tests (54 passed) verifican extracción/formato. Pero criterios de Mongo/agregación/presentación PyMongo no tienen verificación observable (no implementados). Los specs marcan "Pendiente", lo cual es honesto. |

**Veredicto prohibiciones:** 6/8 COMPLIANT, 1 VIOLATION (P-04, pero no se marca como cubierto), 1 PARCIAL (P-08).

---

## 6. Resumen global

| Área | Criterios | CUMPLE | PARCIAL | NO CUMPLE |
|---|---|---|---|---|
| Extracción | 5 | 4 | 1 | 0 |
| Almacenamiento/Streaming | 3 | 0 | 0 | 3 |
| MongoDB/Análisis | 11 | 1 | 1 | 9 |
| Presentación | 5 | 4 | 0 | 1 |
| Prohibiciones | 8 | 6 | 1 | 1 (P-04) |
| **Total** | **32** | **15** | **3** | **14** |

### Fortalezas (lo que está bien)
- **Extracción (4/5):** API + scraping automatizados, 3+ fuentes independientes, datos reales, todo en Python. Formato JSON/CSV con metadata (salvo 9 JSONs con metadata parcial, documentado).
- **Limpieza (LIMPIEZA-01):** Dedup por portal+id_anuncio + fingerprint cross-portal, validación de rangos, marcado de outliers, normalización de metadata. 0 regresiones.
- **Presentación (4/5):** 12 gráficos + 2 dashboards HTML con títulos/leyendas. Interpretación documentada (42 preguntas, 8.2/10). Conclusión con municipios concretos y tipología.
- **Prohibiciones (6/8):** Sin compraventa como eje, sin simulación, sin INE alquiler, sin gráficos hardcoded, todo en Python, sin credenciales.

### Debilidades (lo que falta)
- **MongoDB/Análisis (1/11):** Sin colecciones, sin PyMongo, sin consultas, sin aggregation, sin índices, sin transacciones. Solo LIMPIEZA-01 se cumple (y en pandas, no en Mongo).
- **Almacenamiento/Streaming (0/3):** Sin HDFS, sin Kafka, sin integración end-to-end.
- **P-04:** Sin Aggregation Pipeline (criterio de agregación compleja).
- **DATOS-PYMONGO-01:** Gráficos desde pandas, no desde PyMongo.

### Impresiones

El proyecto está **muy fuerte en obtención y transformación** (extracción 4/5, limpieza 1/1, presentación 4/5, prohibiciones 6/8) pero **completamente pendiente en infraestructura** (HDFS/Kafka/Mongo = 0/14 criterios). Esto es coherente con el estado del usuario: "me quedo solo en obtención + transformación".

**Si el tribunal evalúa solo obtención+transformación:** nota ~8.5-9.0 (extracción + limpieza + presentación + prohibiciones fuertes, deuda documentada).

**Si el tribunal evalúa el reto completo (incluye HDFS/Kafka/Mongo):** nota ~4-5 (15/32 criterios cubiertos, 14 pendientes en infra).

**Recomendación:** Para la defensa, enfocarse en lo que se tiene (obtención, transformación, limpieza, presentación) y ser transparente sobre lo que falta (infra). Los specs marcan "Pendiente" honestamente, lo cual es preferible a marcar como cubierto sin verificación (P-08).

---

*Auditoría realizada en modo read-only. Ningún archivo modificado.*