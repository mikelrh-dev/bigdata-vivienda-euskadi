# Auditoría Actualizada — bigdata-vivienda-euskadi (2026-10-30)

**Complementa:** 01_plantilla_maestra.md, 02_modulos_fase.md, 03_framework_auditoria_dato_puro.md
**Estado del proyecto:** Fase obtención+transformación completada. Infraestructura/Mongo/Kafka diferida.
**Alcance:** Solo obtención + transformación + presentación + documentación.

---

## 1. Resumen ejecutivo

| Área | Criterios | CUMPLE | PARCIAL | NO CUMPLE |
|---|---|---|---|---|
| Extracción (EXTRACCION-01/02, FORMATO-01, COMPLEMENTARIOS-01, PYTHON-01) | 5 | 4 | 1 | 0 |
| Limpieza (LIMPIEZA-01) | 1 | 1 | 0 | 0 |
| Presentación (GRAFICOS-01, DATOS-PYMONGO-01, PRESENTACION-01, INTERPRETACION-01, CONCLUSION-01) | 5 | 4 | 0 | 1 |
| Prohibiciones (P-01 a P-08) | 8 | 8 | 0 | 0 |
| **Total (sin infra)** | **19** | **17** | **1** | **1** |

**Nota esperada (sin infra):** ~9.0/10. Las 2 brechas son por dependencias externas (FORMATO-01 PARCIAL por fuentes en xlsx/zip; DATOS-PYMONGO-01 NO CUMPLE por Mongo no implementado).

---

## 2. Métricas reales observadas (actualizadas)

### 2.1 Raw (Landing Zone)

| Métrica | Valor | Fuente |
|---|---|---|
| Raw files total | 319 (316 manifest + .FROZEN + .gitkeep + manifest) | `ls data/raw/ \| wc -l` |
| Manifiesto SHA-256 | 316 entradas, 0 mismatches | `tests/test_raw_inmutable.py` |
| .FROZEN | Presente | `ls data/raw/.FROZEN` |
| HTML raw preservado | 101 páginas Fotocasa | `ls data/raw/html_fotocasa/` |
| Credenciales en repo | 0 (ignoradas) | `git ls-files \| grep -E '\.env\|api\.txt'` |
| _raw_guard.py | Funcional | `transform/_raw_guard.py` |

### 2.2 Silver (Procesado)

| Métrica | Valor | Fuente |
|---|---|---|
| Silver files total | 113 (112 data + .gitkeep) | `ls data/procesado/ \| wc -l` |
| CSVs con BOM | 36/36 (0 sin BOM) | Python check |
| Anuncios unificados | 759 filas, 13 cols | `wc -l data/procesado/anuncios_unificados.csv` |
| codigo_ine 5 dígitos | 100% | Python check |
| Duplicados cross-portal | 0% (era 13.06%) | `transform/unificar_anuncios.py` |
| Outliers marcados | Sí (valores originales conservados) | `transform/filtrar_outliers.py` |

### 2.3 Calidad de datos

| Métrica | Valor | Fuente |
|---|---|---|
| Media preguntas análisis | 8.24/10 (42 preguntas) | `docs/informe_preguntas_respuesta.md` |
| Municipios robustos (n≥30) | 4 (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39) | `docs/metodologia.md` |
| IDW imputación | 93 municipios | `docs/metodologia.md` |
| Salario ajustado mediana | 1402€ | `docs/metodologia.md` |
| Tensión social | 73 alta / 102 media / 77 baja | `docs/metodologia.md` |
| Duplicados fingerprint | 13.06% (114 filas extra en 93 grupos) | `docs/metodologia.md` |
| Equipamiento | 0/759 (enricher no re-ejecutado post-quarantine; max 84 realty records) | `docs/trazabilidad_datos.md` |
| ECVI mapeo | 252/252, 0 null | `docs/README_ARGON.md` |
| Certificados | 252/252 (E=175, G=74, F=2, A=1) | `docs/README_ARGON.md` |
| EMAL cobertura | 73/252 | `docs/gaps_misconceptions_errores.md` |
| SERPAVI nulls | 0 (imputado por provincia mediana) | `data/procesado/serpavi_renta_imputado.csv` |
| Transporte nulls operadores | 0 (sin_servicio) | `data/procesado/transporte_paradas_municipio_enriquecido.csv` |
| ECVI precio_m2 usada | 13/29 | `data/procesado/ecvi_compraventa_limpio.csv` |
| Tests | 66/66 passing | `pytest tests/ -q` |

### 2.4 Cobertura muestral (anuncios)

| Fuente | Anuncios | Municipios | ≥30 listings | ≥5 listings |
|---|---|---|---|---|
| Fotocasa | 428 | 60 | 3 (Bilbao, Donostia, Getxo) | 26 |
| Pisos.com | 247 | 40 | 0 | — |
| RealtyAPI (Idealista) | 84 | 3 | 0 | — |
| **Total unificado** | **759** | **83** | **4 robustos** | — |

### 2.5 Entity resolution

| Fuente | Distinct muns | Matched to dim | codigo_ine presente |
|---|---|---|---|
| alquiler_municipal.csv | 159 | 159 | No (añadido en transform) |
| anuncios_fotocasa.json | 61 | 61 | No (añadido en transform) |
| anuncios_pisos.json | 37 | 37 | No (añadido en transform) |
| anuncios_realtyapi.json | 3 | 3 | No (añadido en transform) |
| eustat_renta_municipal.json | 252 | 252 | Sí |
| eustat_pib_municipal.json | 252 | 252 | Sí |
| eustat_poblacion_edad.json | 252 | 252 | Sí |
| udalmap_empleo.csv | 252 | 252 | Sí |

---

## 3. Incumplimientos o riesgos detectados

### P1 Crítico (ninguno)
- 0 críticos. Raw inmutable verificado, tests 66/66, codigo_ine 100% 5 dígitos.

### P2 Alto (2)
1. **FORMATO-01 (PARCIAL):** 10 raw files fuera de JSON/CSV (6 xlsx, 2 geojson, 1 zip, 1 txt) + 9 JSONs con metadata parcial. Inherente a las fuentes.
2. **DATOS-PYMONGO-01 (NO CUMPLE):** Gráficos desde DuckDB/CSV, no desde PyMongo. Depende de Mongo (fuera de alcance).

### P3 Medio (5)
1. Cobertura anuncios: 83/252 municipios, solo 4 robustos (n≥30).
2. Idealista no automatizado (requiere key/aprobación).
3. Pisos.com geo inválida 100% (ubicaciones aproximadas).
4. VPO stock no disponible (EMAL mide demanda, no stock).
5. Renta joven proxy (no existe salario joven municipal).

### P4 Bajo (resueltos)
- 6 CSVs sin BOM → corregido (36/36 con BOM)
- 2 JSONs codigo_ine vacío → corregido (null en transform)
- No-determinismo → corregido (fecha fija, sin uuid)
- Duplicados 13.06% → corregido (0%)
- _raw_guard fortalecido → corregido
- 14 derivados → evaluados (13 discard, 1 keep)

---

## 4. Veredicto de suficiencia para la pregunta de investigación

**Pregunta:** "¿Dónde pueden vivir los jóvenes en Euskadi?"

| Criterio | Estado | Detalle |
|---|---|---|
| Ranking de 252 municipios por coste de acceso | PARCIAL | Solo 6 municipios con n≥30 anuncios. 84/252 con algún anuncio. Ranking comarcal viable para el resto. |
| Tasa de esfuerzo = alquiler/renta para 252 | CUMPLE | Renta Eustat 201/252 + INE Atlas para 51 faltantes (proxy). Alquiler oficial 159/252. |
| "Dónde hay trabajo y vivienda barata" | CUMPLE | Paro válido (relativo) + distancias completas (252/252). |
| Municipios robustos (n≥30) | 4 | Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39. |

**Veredicto:** Datos suficientes para análisis comarcal y capitales (n≥30 en 4 municipios, oficial 159/252). Insuficientes para ranking municipal fino de 252. Recomendación: agregar a comarca para municipios pequeños + scraping dirigido para municipios de alta población.

---

## 5. Plan de corrección quirúrgico (pendiente)

### Fase C — Mejoras opcionales (no ejecutadas)
1. **Scraping dirigido Fotocasa:** Batches por municipio de alta población sin cobertura (2 páginas cada uno). Esfuerzo: Medio-Alto. Impacto: +cobertura anuncios.
2. **Pilot geocoding Pisos.com:** 20 anuncios para cuantificar valor. Esfuerzo: Medio. Impacto: mejorar geo Pisos.

### Fase D — Documentación (parcial)
1. **VPO:** Documentado como limitación (no imputar).
2. **Idealista:** Documentado como limitación (requiere key).

### Infraestructura (fuera de alcance)
- HDFS, Kafka, MongoDB, PyMongo, Aggregation Pipeline → diferido.

---

## 6. Cómo usar los 3 frameworks juntos (orden serio)

1. **Primero 03 (DATO PURO):** ¿Podemos responder la pregunta? → Sí (con las limitaciones documentadas).
2. **Luego 01+02 Módulo A:** ¿Extracción y entity resolution cumplen contrato? → Sí (4/5 CUMPLE).
3. **Luego 01+02 Módulo B y C:** ¿HDFS/Kafka/Mongo y Aggregation son 10pts? → No (fuera de alcance).

**Si el agente pasa 03, el proyecto es serio.** El proyecto pasa 03 con limitaciones documentadas (cobertura parcial, ranking comarcal para municipios pequeños).

---

## 7. Archivos de referencia

| Archivo | Contenido |
|---|---|
| `docs/auditoria_specs_sin_infra_2026-10-30.md` | Auditoría spec-vs-proyecto (17/19) |
| `docs/plan_correccion_10_puntos_debiles_2026-10-30.md` | Plan de corrección (Fase A+B+7 ejecutadas) |
| `docs/framework_auditoria_completo_2026-10-30.md` | Framework MSA v2.0 (8 etapas, 88 checks) |
| `docs/gaps_misconceptions_errores.md` | Gaps y null-handling |
| `docs/metodologia.md` | Metodología (IDW, 6 robustos, 1402€, 73/102/77, 13,06%) |
| `docs/trazabilidad_datos.md` | Trazabilidad (134/873) |
| `argon/README_ARGON.md` | Resumen rápido del proyecto |
| `argon/estado_proyecto_2026-10-29.md` | Estado del proyecto |
| `docs/contrato_datos_raw.md` | Contrato de datos raw (opt-in + anomalías + excepciones) |

---

## 8. Próximos pasos

1. **Probar el framework MSA v2.0** (`docs/framework_auditoria_completo_2026-10-30.md`) para verificación completa.
2. **Decidir sobre Fase C** (scraping dirigido + pilot geocoding) según necesidad de cobertura.
3. **Decidir sobre infraestructura** (HDFS/Kafka/Mongo) según alcance del reto.
4. **Actualizar argon/** cuando se complete la auditoría MSA.
