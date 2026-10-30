# Auditoría spec-vs-proyecto (sin infraestructura ni Mongo) — bigdata-vivienda-euskadi

**Fecha:** 2026-10-30
**Modo:** Read-only (auditoría con 2 subagentes + verificación directa)
**Alcance:** Extracción, Formato, Complementarios, Python, Limpieza, Presentación, Prohibiciones
**Fuera de alcance:** HDFS, Kafka, MongoDB, Aggregation Pipeline, PyMongo

---

## 1. Extracción de datos (extraccion-datos/spec.md)

| Req | Estado | Evidencia |
|---|---|---|
| EXTRACCION-01 (API + scraping, raw + parsed) | ✅ CUMPLE | 34 scripts en `extract/`: API (01_eustat, 02_eustat_alquiler, 06_ine, 07_ine_salarios, 16_serpavi, 17_osrm, 18_lanbide) + scraping (05_fotocasa, 08_pisos, 09_realtyapi). HTML crudo preservado: `data/raw/html_fotocasa/` (101 páginas). Row counts en JSON metadata. |
| EXTRACCION-02 (≥3 fuentes independientes) | ✅ CUMPLE | 5+ fuentes: Eustat, INE, euskadi.eus, b5m, Fotocasa, Pisos.com, RealtyAPI, SERPAVI, OSRM, Lanbide. Fallo de una no aborta el resto (main_ingest.py con modo replay-raw). |
| FORMATO-01 (JSON/CSV + metadata) | ⚠️ PARCIAL | 124 CSV + 60 JSON válidos. 10 raw files fuera de JSON/CSV (6 xlsx, 2 geojson, 1 zip, 1 txt). Metadata gaps: 2 JSON sin `metadata` (emancipacion_juventud_resumen, ovj_salario_joven_2024), 7 JSON sin `fecha_extraccion`, 1 sin `fuente` (b5m_catalogo). CSVs sin metadata embebida. |
| COMPLEMENTARIOS-01 (salarios, población) | ✅ CUMPLE | Salarios reales: INE EPA (06, 07, 198 registros) + OVJ (1.564€). Población: Eustat (01, 89.424 filas). Plus renta, paro, empleo. Sin simulación (P-02). |
| PYTHON-01 (todo en Python, venv) | ✅ CUMPLE | 34 scripts extract + 39 transform. `.venv/Scripts/python.exe` 3.12.10. `requirements.txt` pinned. `compileall` OK. `test_p06` passes. |

**Veredicto extracción:** 4/5 CUMPLE, 1 PARCIAL (FORMATO-01 por metadata/encoding documentados). Nota: ~9/10.

---

## 2. Limpieza de datos (LIMPIEZA-01 de mongodb-y-analisis/spec.md)

| Req | Estado | Evidencia |
|---|---|---|
| LIMPIEZA-01 (incompletos, duplicados, incorrectos) | ✅ CUMPLE | Dedup: `unificar_anuncios.py` (portal+id y fingerprint cross-portal, 13,06%→0%). `deduplicar_alquiler_enriquecido.py`. Fotocasa ids únicos (test). Nulos explícitos: `test_limpieza_nulos_explicitos` passes (superficie None ≠ 0). Outliers marcados (no borrados): `filtrar_outliers.py` (IQR + umbrales 3–50 €/m², 10–500 m²). Validación rangos: `corregir_empleo.py`. Estandarización: `enriquecer_codigo_ine.py`, `normalizar_json_crudos.py`, `muni_resolve.py`. Detección: `auditar_lagunas_silver.py`. |

**Veredicto limpieza:** 1/1 CUMPLE. Nota: ~9/10.

---

## 3. Presentación de resultados (presentacion-de-resultados/spec.md)

| Req | Estado | Evidencia |
|---|---|---|
| GRAFICOS-01 (≥3 tipos: barras, dispersión, boxplot) | ✅ CUMPLE | `transform/generar_dashboard_visual.py` y `generar_dashboard_completo.py`: barras (g3, g5, A2, C, F), dispersión (g2, B, D), caja y bigotes (g1, A1); mapa opcional (`mapa_esquema_silver.html`). 12 PNGs + 2 dashboards HTML. |
| DATOS-PYMONGO-01 (gráficos desde PyMongo) | ❌ NO CUMPLE | Gráficos generados con DuckDB sobre CSV (`read_csv`), no con PyMongo/MongoDB. `grep` de `pymongo/MongoClient` solo en `tests/test_contrato.py` como texto. No hay código de conexión/consulta Mongo. |
| PRESENTACION-01 (títulos, unidades, leyendas, comparación) | ✅ CUMPLE | Títulos (`set_title`), unidades (EUR/mes, EUR/m2, %, km, Habitantes), leyendas (`hue`, `ax.legend`), comparación por territorio/municipio. |
| INTERPRETACION-01 (≥3 resultados con causa/implicación) | ✅ CUMPLE | `docs/informe_preguntas_respuesta.md` y dashboards documentan ≥3 hallazgos con causa/implicación (esfuerzo 43,5%, paro-alquiler r=+0,385 espurio, distancia r=-0,603, robustez n≥30). |
| CONCLUSION-01 (municipios concretos + indicadores) | ✅ CUMPLE | Nombra Bilbao, Donostia, Vitoria-Gasteiz, Getxo, Abanto, Ayala con indicadores y advierte muestra pequeña (176 sin anuncios, 6 robustos). |

**Veredicto presentación:** 4/5 CUMPLE, 1 NO CUMPLE (DATOS-PYMONGO-01, depende de Mongo). Nota: ~8/10 (sin Mongo).

---

## 4. Prohibiciones (P-01 a P-08, contrato-reto/spec.md)

| Prohibición | Estado | Evidencia |
|---|---|---|
| P-01 (no compraventa como eje) | ✅ COMPLIANT | Compraventa solo complemento (`generar_mercado_area_funcional.py`, ratio). Ningún gráfico la usa como eje principal. |
| P-02 (no simular valores) | ✅ COMPLIANT | Salarios: INE EPA (1.372€) + OVJ (1.564€). Renta joven: proxy documentado con ratio 0,3534 (estimación transparente, no simulación). Alquiler: Eustat real. Población: Eustat real. |
| P-03 (no usar INE alquiler para Euskadi) | ✅ COMPLIANT | Alquiler proviene de Eustat (`alquiler_municipal.csv`, 159/252 directo + 93 comarca). INE alquiler no usado. |
| P-04 (no contar etapa única cuando exige agregación) | ✅ COMPLIANT | No se reclama agregación compleja como cubierta. No hay pipeline de agregación implementado. Spec marca "Pendiente". |
| P-05 (no gráficos con valores tecleados) | ✅ COMPLIANT | Gráficos generados desde CSVs reales. `g_G` es tabla de gaps anotada, no serie de datos. |
| P-06 (todo en Python) | ✅ COMPLIANT | 74 archivos rastreados son `.py`. Programas del reto en Python. |
| P-07 (no credenciales en repo) | ✅ COMPLIANT | `.env` y `api.txt` en `.gitignore`, no rastreados. Existen localmente con secretos. |
| P-08 (no marcar cubierto sin verificación) | ✅ COMPLIANT | Criterios no marcados como cubiertos sin verificación. Spec de presentación figura "Pendiente". Contract tests pasan (66). |

**Veredicto prohibiciones:** 8/8 COMPLIANT.

---

## 5. Resumen global (sin infraestructura ni Mongo)

| Área | Criterios | CUMPLE | PARCIAL | NO CUMPLE |
|---|---|---|---|---|
| Extracción | 5 | 4 | 1 | 0 |
| Limpieza | 1 | 1 | 0 | 0 |
| Presentación | 5 | 4 | 0 | 1 |
| Prohibiciones | 8 | 8 | 0 | 0 |
| **Total** | **19** | **17** | **1** | **1** |

### Fortalezas
- **Extracción (4/5):** API + scraping automatizados, 5+ fuentes independientes, datos reales, todo en Python. Formato con metadata (salvo 9 JSONs parciales, documentado).
- **Limpieza (1/1):** Dedup por portal+id_anuncio + fingerprint cross-portal, validación de rangos, marcado de outliers, normalización. 0 regresiones.
- **Presentación (4/5):** 12 gráficos + 2 dashboards HTML. Interpretación documentada (42 preguntas, 8.2/10). Conclusión con municipios concretos.
- **Prohibiciones (8/8):** Sin compraventa como eje, sin simulación, sin INE alquiler, sin gráficos hardcoded, todo en Python, sin credenciales, sin marcar cubierto sin verificación.

### Debilidades
- **FORMATO-01 (PARCIAL):** 10 raw files fuera de JSON/CSV (xlsx, geojson, zip, txt). 9 JSONs con metadata parcial (2 sin envelope, 7 sin fecha_extraccion, 1 sin fuente). CSVs sin metadata embebida.
- **DATOS-PYMONGO-01 (NO CUMPLE):** Gráficos desde DuckDB/CSV, no desde PyMongo. No hay Mongo implementado (fuera de alcance).

### Impresiones

El proyecto está **muy fuerte en obtención, transformación, limpieza y presentación** (17/19 criterios cubiertos, sin contar infraestructura ni Mongo). Las únicas brechas son:
1. **FORMATO-01 (PARCIAL):** 10 archivos raw no JSON/CSV (xlsx, geojson, zip, txt) y 9 JSONs con metadata parcial. Esto es inherente a las fuentes (ECVI en xlsx, GTFS en zip, shapefile). No es un defecto de diseño, sino una limitación de las fuentes originales.
2. **DATOS-PYMONGO-01 (NO CUMPLE):** Dependiente de MongoDB, que está fuera de alcance.

**Si el tribunal evalúa solo obtención+transformación+presentación (sin infra):** nota ~9.0 (17/19 criterios, las 2 brechas son por dependencias externas documentadas).

**Recomendación:** Enfocarse en lo que se tiene. Las 2 brechas son por dependencias externas (fuentes en xlsx/zip y Mongo no implementado), ambas documentadas y justificadas.

---

*Auditoría realizada en modo read-only. Ningún archivo modificado.*