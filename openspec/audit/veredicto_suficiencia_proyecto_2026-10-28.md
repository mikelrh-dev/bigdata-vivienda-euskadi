# Veredicto de suficiencia — ¿Los datos actuales permiten un proyecto profesional completo según el PDF?

**Fecha:** 2026-10-28
**Fuentes:** contrato `openspec/specs/contrato-reto/spec.md`, tests `tests/test_contrato.py` (54/54), inventario `data/raw` + `data/procesado`, auditorías previas.
**Veredicto:** PARCIALMENTE SUFICIENTE (datos) + PROYECTO INCOMPLETO (implementación).

---

## 1. Lo que SÍ cubren los datos (soporte real, verificado)

| Criterio del PDF | Estado de datos | Evidencia |
|---|---|---|
| Extracción API+scraping (RA1) | Completo | 471 Fotocasa + 230 Pisos + 139 RealtyAPI + Eustat + INE. 54/54 tests. |
| Limpieza (duplicados, nulos, outliers) | Completo | ids únicos, superficie ≠ 0 o None, outlier flag IQR por segmento. |
| Formato JSON/CSV con metadata | Completo | 29 fuentes, metadata{fuente, fecha, n_*}. |
| Complementarios (población, renta, empleo) | Completo | 252/252 municipios en renta, Udalmap, Lanbide, OSRM, distancias, dim_municipios. |
| Entity resolution | Completo | codigo_ine 99.6-100% en todas las fuentes (Araba zfill corregido). |
| Transformaciones (código) | Completo | dim_municipios, enriquecer, filtrar, tipologia_mercado (6/63/183). |

---

## 2. Lo que los datos NO cubren (limitaciones honestas)

| Limitación | Magnitud | Acción |
|---|---|---|
| Municipios con ≥30 anuncios | Solo 7 (Bilbao, Donostia, Getxo + 3 RealtyAPI capitales) | Aceptar: ranking fino no es posible. Clasificación tipológica para los 252. |
| Municipios con alquiler oficial | 159/252 (63%) | SERPAVI no añade (verificado: 0 nuevos). Marcar 93 como `sin_dato`. |
| Municipios con algún anuncio | 82/252 (33%) | 80 sin mercado de alquiler libre (estructura rural). |
| Salario joven municipal | No existe | Proxy renta municipal o `sin_dato`. |
| Emancipación juvenil municipal | Territorial (0/252) | Narrativa a nivel CA/TH, no municipal. |
| Año de los datos | Mezcla 2026/2024/2025 | Documentar en análisis. |

---

## 3. Las 5 preguntas del PDF

1. **¿Puede emanciparse un joven?** → Respondible a nivel territorial (emancipación 2010-2026) y para 159 municipios (esfuerzo alquiler/renta). Para los otros 93: `sin_dato`.
2. **¿En qué municipios y por qué?** → Parcialmente. Robusto para 7 municipios. Clasificación tipológica (Nivel1/2/3) para los 252 con renta, paro, distancia y mercado. No se puede hacer ranking <20% error para todos.
3. **¿Dónde hay trabajo y vivienda barata?** → Mejorado. Paro juvenil Lanbide (252), Udalmap, OSRM minutos reales. Vivienda barata solo para 159 (oficial) + cross-check SERPAVI. Para 93: estructura de vivienda vacía (Eustat tenencia) + clasificación.
4. **¿Qué municipios ofrecen mejores posibilidades?** → Combinando tipología + paro + distancia + renta, se puede construir un índice compuesto. Limitado por cobertura de anuncios.
5. **¿Qué limitaciones tiene el estudio?** → Documentables: 93 sin alquiler, 80 sin mercado, salario proxy, emancipación territorial, mezcla de años.

---

## 4. Lo que FALTA para un proyecto completo (implementación, no datos)

Los datos son suficientes para soportar todas las fases. Lo que falta es **implementar**:

| Fase (rúbrica) | Estado | Lo que necesita los datos |
|---|---|---|
| HDFS (almacenamiento) | Pendiente | `data/raw/` (originales) + `data/procesado/` (normalizados) — ya existen |
| Kafka (productor/consumidor) | Pendiente | Anuncios JSON (precio + municipio) — ya existen |
| Integración E2E | Pendiente | Flujo fuente→HDFS→Kafka→Mongo — datos listos |
| Modelado MongoDB | Prep done | `dim_municipios` (252, codigo_ine), entity resolution — listo para modelar |
| Operaciones PyMongo | Pendiente | Anuncios + municipios — listos |
| Consultas anidadas/arrays | Pendiente | Anuncios con dirección anidada + características — listos |
| Aggregation Pipeline | Pendiente | Alquiler + renta por municipio — listos |
| Limpieza en Mongo | Hecho (código) | Duplicados resueltos, nulos marcados |
| Transformaciones Mongo | Pendiente | Precios heterogéneos — listos |
| Gráficos (≥3 tipos) | Pendiente | Datos categóricos/continuos/geo — listos |
| Datos desde PyMongo | Pendiente | Resultados de agregación — listos |
| Presentación | Pendiente | Comparar dos municipios cualesquiera — datos listos |
| Interpretación (≥3 hallazgos) | Pendiente | Indicadores calculados — listos |
| Conclusión (municipios concretos) | Pendiente | Ranking calculado — parcial (tipología) |

---

## 5. Conclusión honesta

**Los datos actuales SON suficientes para construir un proyecto profesional completo** (con las limitaciones documentadas). No falta ningún dato crítico: todas las fuentes necesarias para extraction, cleaning, modeling, aggregation, charts e interpretation están presentes y verificadas (54/54 tests).

**Lo que falta es implementar las fases de infraestructura y análisis** (HDFS, Kafka, MongoDB, PyMongo, aggregation, visualización, informe). Esas son las que suman los puntos de rúbrica restantes, y los datos ya las soportan al 100%.

**Recomendación:** no invertir más tiempo en fuentes nuevas. El siguiente paso de mayor retorno es el Docker Compose (HDFS + MongoDB) + modelado + aggregation + gráficos. Con eso el proyecto pasa de "datos preparados" a "proyecto completo defendible".
