# Plan de Mejora — bigdata-vivienda-euskadi

**Basado en:** `openspec/audit/auditoria_completa_2026-10-27.md`  
**Fecha:** 2026-10-27  
**Estado:** Borrador — pendiente de aprobación del usuario antes de ejecutar.

---

## Principio rector

La pregunta de investigación es: **¿Dónde pueden vivir los jóvenes en Euskadi?**  
Para responderla con rigor necesitamos: renta municipal (✓ 252/252), alquiler municipal (✗ 159/252, sin n muestral), paro válido (✗ 248/252 negativos), distancias completas (✗ 2.77% de pares), cobertura de portales (✗ solo 3 municipios con n≥30).

**No tocar infraestructura (HDFS/Kafka/MongoDB) hasta que el dato sea sólido.** Priorizar corrección de dato sobre feature nueva.

---

## Fase 0 — Correcciones críticas (P1) — Bloquean cualquier conclusión

### 0.1 Corregir tasa de paro (udalmap_empleo)

**Problema:** 248/252 municipios con paro negativo (media -10.10%, min -32.46). Fórmula mal derivada.

**Acción:**
- Revisar `extract/udalmap_empleo.py`: la fórmula `tasa_paro` probablemente es `(parados / activos) * 100` pero los datos de Udalmap vienen ya como tasa o con signo invertido.
- Alternativa: sustituir por EPA provincial (INE) o INE tasa de paro municipal si disponible.
- Validar: `tasa_paro` en [0, 100], `tasa_actividad` en [0, 100], `tasa_ocupacion` en [0, 100].

**Archivos:** `extract/udalmap_empleo.py`  
**Esfuerzo:** Medio (1-2h)  
**Verificación:** `udalmap_empleo.csv` → min paro ≥0, max ≤100, media razonable (5-20%).  
**Dependencias:** Ninguna.  
**Riesgo:** Si Udalmap no tiene tasa válida, sustituir fuente completa (EPA provincial). Impacto en spec `extraccion-datos`.

---

### 0.2 Generar HTML crudos de Fotocasa (EXTRACCION-01)

**Problema:** `data/raw/html_fotocasa/` contiene 0 archivos. Sin trazabilidad de extracción.

**Acción:**
- Modificar `extract/05_fotocasa_scraper.py` para guardar cada página HTML en `data/raw/html_fotocasa/{municipio}_{pagina}.html` antes de parsear.
- Añadir checksum (SHA256) al metadata de salida.

**Archivos:** `extract/05_fotocasa_scraper.py`  
**Esfuerzo:** Bajo (30min)  
**Verificación:** `ls data/raw/html_fotocasa/` ≥ 1 archivo; `sha256sum` reproducible.  
**Dependencias:** Ninguna.

---

### 0.3 Completar alquiler oficial para 93 municipios faltantes

**Problema:** `alquiler_municipal.csv` cubre 159/252 municipios. 93 sin dato oficial. Sin `n` muestral por distrito.

**Acción (opción A — recomendada):** Agregar a comarca para los 93 faltantes, documentando que el valor es comarcal, no municipal. Añadir columna `nivel_geografico` ("municipal" / "comarcal").

**Acción (opción B):** Buscar fuentes adicionales (INE Atlas de alquiler, observatorios autonómicos) para los 93. Esfuerzo alto, cobertura incierta.

**Archivos:** `extract/02_eustat_alquiler.py`, `transform/dim_municipios.py` o nuevo `transform/agregar_comarca.py`  
**Esfuerzo:** Medio (opción A) / Alto (opción B)  
**Verificación:** `alquiler_municipal.csv` → 252 municipios únicos; columna `nivel_geografico` presente.  
**Dependencias:** 0.1 (paro) no bloquea, pero conviene hacer juntos.

---

### 0.4 Deduplicar distancias_capitales

**Problema:** 2 códigos duplicados en `distancias_capitales.csv` (259 filas, 252 municipios).

**Acción:**
- En `extract/04_b5m_geo.py`, añadir `drop_duplicates(subset=['codigo_ine'])` antes de guardar.
- Verificar que los 2 duplicados no tienen valores distintos (si los tienen, decidir cuál mantener).

**Archivos:** `extract/04_b5m_geo.py`  
**Esfuerzo:** Bajo (15min)  
**Verificación:** `distancias_capitales.csv` → 252 filas, 0 duplicados.  
**Dependencias:** Ninguna.

---

## Fase 1 — Cobertura muestral (P1/P2) — Mejora la robustez del ranking

### 1.1 Ampliar scraping hasta n≥30 en municipios objetivo

**Problema:** Solo 3 municipios con n≥30 en Fotocasa, 0 en Pisos.com. 41 municipios con n<5.

**Acción:**
- Identificar los 20-30 municipios objetivo (capitales + comarcas principales + municipios con alquiler alto).
- Ampliar scraping de Fotocasa y Pisos.com a esos municipios hasta n≥30.
- Separar temporal vs larga estancia (columna `tipo_alquiler`: "temporal" / "larga_estancia").

**Archivos:** `extract/05_fotocasa_scraper.py`, `extract/08_pisos_scraper.py`  
**Esfuerzo:** Alto (4-6h)  
**Verificación:** `anuncios_fotocasa.csv` → ≥10 municipios con n≥30; columna `tipo_alquiler` presente.  
**Dependencias:** 0.2 (HTML crudos).

---

### 1.2 Regenerar distancias_municipios (completo o candidatos)

**Problema:** Solo 5.000/180.488 pares (2.77%), 5 municipios origen. No se puede responder "municipio barato a <30km".

**Acción (opción A — recomendada):** Generar distancias para todos los pares de los 252 municipios (180.488 pares) usando Haversine sobre GeoJSON. Fichero ~2.4MB ya existe parcialmente.

**Acción (opción B):** Generar solo para los 20-30 municipios candidatos (capitales + baratos) → ~20×252 = 5.040 pares.

**Archivos:** `extract/04_b5m_geo.py`  
**Esfuerzo:** Medio (opción A) / Bajo (opción B)  
**Verificación:** `distancias_municipios.json` → pares ≥ 50% del total o candidatos completos.  
**Dependencias:** Ninguna.

---

### 1.3 Añadir columna `año_fuente`

**Problema:** Eustat 2024 vs INE Atlas 2022 mezclados sin trazabilidad.

**Acción:**
- Añadir `año_fuente` a `renta_municipal_completa.csv` y `alquiler_municipal.csv`.
- Documentar en `docs/` la regla: usar el año más reciente disponible por municipio.

**Archivos:** `extract/ine_atlas_renta.py`, `extract/02_eustat_alquiler.py`  
**Esfuerzo:** Bajo (30min)  
**Verificación:** Columna presente en ambos CSV.  
**Dependencias:** Ninguna.

---

## Fase 2 — Calidad estadística (P2) — Mejora el rigor

### 2.1 Separar temporal vs larga estancia en análisis

**Problema:** Diferencia 21.6% (20.70 vs 16.22 €/m²). Mezclar infla el precio.

**Acción:**
- En `transform/filtrar_outliers.py`, añadir filtro por `tipo_alquiler`.
- En tests, verificar que no se mezclan.

**Archivos:** `transform/filtrar_outliers.py`, `tests/test_contrato.py`  
**Esfuerzo:** Bajo (30min)  
**Verificación:** Test que compara medias temporal vs larga y falla si se mezclan.  
**Dependencias:** 1.1 (columna tipo_alquiler).

---

### 2.2 Documentar renta como proxy de salario

**Problema:** INE salarios edad es nacional (1.372,8 € 16-24). No hay salario municipal gratuito.

**Acción:**
- Crear `docs/decision_salario_proxy.md` explicando que se usa renta municipal (Eustat) como proxy de capacidad económica, no salario.
- Añadir nota en el informe final y en el código (comentario).

**Archivos:** `docs/decision_salario_proxy.md`  
**Esfuerzo:** Bajo (15min)  
**Verificación:** Documento existe y está referenciado en `openspec/`.  
**Dependencias:** Ninguna.

---

### 2.3 Correlación renta vs alquiler documentada

**Problema:** r = 0.2094. La renta local explica poco el precio.

**Acción:**
- En el informe final, documentar que el precio de alquiler no se explica por la renta local (r<0.3).
- Explorar otras variables explicativas: distancia a capitales, tasa de paro (cuando corregido), densidad de población.

**Archivos:** `docs/` o `notebooks/`  
**Esfuerzo:** Bajo (documentación) / Medio (análisis adicional)  
**Verificación:** Informe menciona r=0.2094 y su interpretación.  
**Dependencias:** 0.1 (paro corregido).

---

## Fase 3 — Infraestructura (P2/P3) — Solo cuando el dato sea sólido

### 3.1 Levantar HDFS + Kafka + MongoDB (docker-compose)

**Acción:**
- Crear `docker-compose.yml` con HDFS (namenode + datanode), Kafka (zookeeper + broker), MongoDB.
- Definir rutas HDFS: `/raw/`, `/procesado/`.
- Productor/consumidor Kafka con idempotencia (upsert por `codigo_ine` + `fuente`).

**Archivos:** `docker-compose.yml`, `storage/`, scripts en `extract/` o nuevo `streaming/`  
**Esfuerzo:** Alto (6-8h)  
**Verificación:** `docker compose up` → contenedores healthy; HDFS accesible; Kafka topic creado; Mongo colección con datos.  
**Dependencias:** Fase 0 y 1 completadas.

---

### 3.2 Aggregation pipeline MongoDB (4+ etapas)

**Acción:**
- Pipeline con `$match`, `$lookup`, `$unwind`, `$group`, `$project`, `$sort`.
- Distinguir municipios con muestra representativa (n≥5 anuncios) vs dato oficial Eustat.

**Archivos:** nuevo `analytics/mongo_pipeline.py` o similar  
**Esfuerzo:** Medio (3-4h)  
**Verificación:** Pipeline devuelve resultados; no pierde municipios en `$lookup`.  
**Dependencias:** 3.1.

---

### 3.3 Visualización (3+ tipos de gráfico)

**Acción:**
- Barras: ranking de municipios por coste de acceso.
- Dispersión: renta vs alquiler / tasa de esfuerzo.
- Boxplot: distribución por territorio/municipio.
- Mapa coroplético: 252 municipios.
- Todos con título, unidades, leyenda. Cero hardcoding (leer de PyMongo).

**Archivos:** `visualization/`, `notebooks/`  
**Esfuerzo:** Medio (4-5h)  
**Verificación:** 3+ tipos de gráfico; código sin números hardcodeados.  
**Dependencias:** 3.1, 3.2.

---

## Resumen de priorización

| Fase | Acciones | Esfuerzo total | Bloquea conclusión |
|---|---|---|---|
| 0 (P1 crítico) | 0.1, 0.2, 0.3, 0.4 | ~3-4h | Sí |
| 1 (cobertura) | 1.1, 1.2, 1.3 | ~6-8h | Parcialmente |
| 2 (calidad) | 2.1, 2.2, 2.3 | ~1-2h | No |
| 3 (infra) | 3.1, 3.2, 3.3 | ~13-17h | No (post-dato) |

**Recomendación:** Ejecutar Fase 0 completa antes de cualquier otra cosa. Fase 1 en paralelo si hay tiempo. Fase 2 documentación. Fase 3 solo cuando el dato sea sólido y haya tiempo antes de la entrega.

---

## Criterio de éxito (veredicto de suficiencia)

Después de Fase 0 + Fase 1:
- Paro válido en 252/252 (0 negativos).
- Alquiler oficial en 252/252 (con nivel_geografico).
- ≥10 municipios con n≥30 en portales.
- Distancias para ≥50% de pares o candidatos completos.
- HTML crudos presentes.

Si se cumplen todos → se puede responder "¿Dónde pueden vivir los jóvenes?" con error <20% para capitales y comarcas. Para ranking fino de 252, se necesita Fase 1 completa + más scraping.

**Espera tu OK para ejecutar Fase 0.**
PY