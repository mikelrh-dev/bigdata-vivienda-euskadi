# Auditoría Completa — bigdata-vivienda-euskadi (ACTUALIZADA)

**Fecha:** 2026-10-27 (re-ejecutada tras Fase 0 y Fase 1 del plan de mejora)  
**Modo:** Solo lectura y diagnóstico (sin modificar código de producción).  
**Frameworks aplicados:** `03_framework_auditoria_dato_puro.md` (dato puro) + `02_modulos_fase.md` Módulo A (extracción y entity resolution).  
**Módulos B, C, D:** No aplicables (infraestructura HDFS/Kafka/MongoDB y visualización no implementadas).

---

## 1. Métricas Reales Observadas (ACTUALIZADAS)

| Fuente | Registros válidos | Municipios únicos | % sobre 252 | n≥30 | n 5-29 | n<5 | codigo_ine % | Outliers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| alquiler_municipal.csv | 253 | 159 | 63.1% | — | — | — | 100% | 0 |
| alquiler_municipal_completo (procesado) | 252 | 252 (159 mun + 93 comarcal) | 100% | — | — | — | 100% | 0 |
| anuncios_fotocasa.csv | 469 (455 válidos) | 57 | 22.6% | 3 | 9 | 45 | 100% | 12 (max 83.33) |
| anuncios_pisos.csv | 218 (192 válidos) | 29 | 11.5% | 0 | 11 | 18 | 100% | 9 (max 43.92) |
| anuncios_realtyapi.csv | 139 | 3 | 1.2% | 3 | 0 | 0 | 100% | 5 (max 55.63) |
| eustat_renta_municipal.csv | 252 | 252 | 100% | — | — | — | 100% | — |
| udalmap_empleo.csv | 252 | 252 | 100% | — | — | — | 100% | paro: 252 None |
| distancias_capitales.csv | 252 | 252 | 100% | — | — | — | 100% | 0 dup |
| distancias_municipios.json | 5.000 pares | 5 orígenes | 2.8% | — | — | — | — | — |
| emancipacion_juventud.csv | 866 | — | — | — | — | — | — | 0 |
| ine_atlas_renta.csv | 252 | 252 | 100% | — | — | — | 100% | — |
| ine_salarios_edad.csv | 198 | 0 (nacional) | 0% | — | — | — | — | — |
| html_fotocasa | 17 archivos | — | — | — | — | — | — | — |

**Mejoras respecto a auditoría anterior:**
- Alquiler completo: 159 → 252 municipios (93 comarcales añadidos).
- Paro: 248 negativos → 252 None (documentado, no negativo).
- HTML crudos: 0 → 17 archivos (EXTRACCION-01 cumple).
- Distancias: 259 (2 dup) → 252 (0 dup).
- Fotocasa: 480 → 469 anuncios (tras re-scraping con 20 páginas).
- Renta: añadido `anio_fuente` (2024 en todos).

**Detalles clave:**
- Fotocasa temporal vs larga estancia: 303 temporal (20.21 €/m²) vs 166 larga estancia (16.28 €/m²); diferencia +24.1%. No mezclar.
- Superficie válida (15-300 m² + habitaciones no nulo): Fotocasa 95.5%, Pisos.com 94.0%, RealtyAPI 99.3%.
- Correlación Pearson renta vs alquiler: r = 0.1795 (renta_completa) / 0.2094 (Eustat). Débil.
- Udalmap: actividad 40.63-60.09, ocupación 41.39-74.14, paro 252/252 None con nota.
- Entity resolution: variantes Fotocasa y RealtyAPI mapeadas a canónico (100%).
- Emancipación: parsea correctamente con `;` + `"` (866 filas, 14 indicadores).

---

## 2. Auditoría Módulo A — Extracción y Entity Resolution (ACTUALIZADA)

| Métrica | Fotocasa | Pisos.com | RealtyAPI | Alquiler municipal |
|---|---:|---:|---:|---:|
| Total registros | 469 | 218 | 139 | 253 |
| codigo_ine válido (5 dígitos) | 100% | 100% | 100% | 100% |
| Cruce con Eustat + empleo | 100% | 100% | 100% | 100% |

**Pisos.com superficie/habitaciones:**
- superficie_m2 no nulos: 213/218 (97.7%)
- habitaciones no nulos: 210/218 (96.3%)
- ambos no nulos: 206/218 (94.5%)

**HTML crudos Fotocasa (EXTRACCION-01):** ✅ 17 archivos `.html` en `data/raw/html_fotocasa/`, todos no vacíos.

**GeoJSON (municipios_euskadi.geojson):**
- Features: 259 (257 códigos únicos, 252 municipios canónicos cubiertos)
- CRS: EPSG:4326 ✓
- Distancias Haversine: 0 NaN ✓
- Distancias capitales: 252 filas, 252 códigos únicos, 0 duplicados ✓

**Suite de tests:**
- 18 passed, 0 failed, 0 xfail, 0 skip ✓

---

## 3. Gaps y Sesgos (ACTUALIZADOS)

### P1 — Crítico (reducidos tras Fase 0)
1. **Paro municipal no disponible** (252/252 None) → no se puede calcular tasa de paro municipal; solo actividad/ocupación. Usar EPA provincial.
2. **Alquiler oficial sin n muestral** (sin columna de contratos) en 159 municipales + 93 comarcales → no se sabe robustez de la media.
3. **Distancias municipio-municipio incompletas**: 5.000/180.488 pares (2.8%) → no se puede responder "municipio barato a <30 km" para todos.
4. **Muestra de anuncios insuficiente para ranking municipal**: solo 3 mun. con n≥30 en Fotocasa, 0 en Pisos, 3 capitales en Realty; 195 mun. sin Fotocasa, 223 sin Pisos, 249 sin Realty.
5. **RealtyAPI solo 3 municipios** (capitales) → no representativo del territorio.

### P2 — Alto
1. Outliers €/m²: 12 Fotocasa (hasta 83.33), 9 Pisos (43.92), 5 Realty (55.63); varios en superficies pequeñas (25 m²).
2. Correlación renta–alquiler débil (r≈0.18–0.21) → el precio no se explica por renta local; documentado.
3. 93 municipios con dato comarcal (proxy), no municipal → pérdida de granularidad.
4. Superficie válida 94-99% pero ~5-6% sin habitaciones.
5. Fotocasa temporal vs larga difieren 24% → obliga a separar en cualquier agregación.

### P3 — Medio (mejorados)
1. Salario solo nacional (1.372,8 €, 16-24 años) → usar renta como proxy municipal. Documentado.
2. Distancias solo a 3 capitales (no red completa entre municipios).
3. 17 HTML crudos Fotocasa presentes (≥10) → OK. EXTRACCION-01 cumple.
4. Eustat 2024 vs INE Atlas 2024 alineados; `anio_fuente` presente (2024).
5. Paro documentado como no disponible (no negativo).

---

## 4. Veredicto de Suficiencia (ACTUALIZADO)

**Parcial — mejorado.** Tras las correcciones de Fase 0 y Fase 1:

- **Renta:** 252/252 ✓ (Eustat + INE Atlas, fuente independiente).
- **Alquiler:** 252/252 ✓ (159 municipal + 93 comarcal). Se puede calcular tasa de esfuerzo alquiler/renta para los 252 municipios, aunque 93 usan proxy comarcal y el alquiler oficial no tiene n muestral.
- **Paro:** 252/252 None ✗ (Udalmap no publica paro municipal). No se puede calcular tasa de paro municipal ni concluir "trabajo + vivienda barata".
- **Distancias:** 252/252 a capitales ✓, pero solo 2.8% de pares municipio-municipio. No se puede responder "municipio barato a <30 km" para todos.
- **Anuncios:** Solo 6 municipios con n≥30 (3 Fotocasa + 3 capitales Realty). No se puede hacer ranking municipal fino de coste de acceso con error <20%.

**Suficiente para:** análisis comarcal y capitales, tasa de esfuerzo para 252 municipios (con proxy comarcal), ranking de 6 municipios con muestra robusta.

**Insuficiente para:** ranking municipal fino de 252, conclusión "trabajo + vivienda barata" (falta paro municipal), respuesta "municipio barato a <30km" (faltan distancias).

**Recomendación:** Completar paro con EPA provincial, ampliar scraping a n≥30 en municipios objetivo, regenerar distancias municipio-municipio para candidatos. Fase 3 (infraestructura) solo cuando el dato sea sólido.

---

## 5. Módulos B, C, D — No implementados

| Módulo | Estado | Evidencia |
|---|---|---|
| B — Infraestructura HDFS/Kafka/MongoDB | No implementado | `storage/`, `visualization/`, `notebooks/` vacíos. Sin `docker-compose.yml`. |
| C — MongoDB, limpieza, aggregation pipeline | No implementado | Sin colecciones, sin pipelines. |
| D — Visualización e informe | No implementado | `visualization/` y `notebooks/` vacíos. |

**Recomendación:** No auditar B/C/D hasta que exista infraestructura. Priorizar correcciones P1 (paro municipal, distancias, scraping).

---

## 6. Plan de Corrección Quirúrgico (ACTUALIZADO)

| # | Acción | Archivos | Esfuerzo | Verificación | Estado |
|---|---|---|---|---|---|
| 1 | Corregir paro: usar EPA provincial o documentar no disponible | `extract/udalmap_empleo.py` | Medio | paro no negativo | ✅ Hecho (None + nota) |
| 2 | Generar HTML crudos Fotocasa | `extract/05_fotocasa_scraper.py` | Bajo | ≥1 HTML | ✅ Hecho (17 archivos) |
| 3 | Completar alquiler (agregar a comarca) | `transform/completar_alquiler_comarca.py` | Medio | 252 municipios | ✅ Hecho |
| 4 | Dedup distancias_capitales | `extract/euskadi_geo.py` | Bajo | 0 dup | ✅ Hecho |
| 5 | Ampliar scraping n≥30 | `extract/05_fotocasa_scraper.py` | Alto | ≥10 mun. n≥30 | ⏳ Pendiente |
| 6 | Regenerar distancias (candidatos) | `extract/04_b5m_geo.py` | Medio | ≥50% pares | ⏳ Pendiente |
| 7 | Añadir año_fuente | `extract/ine_atlas_renta.py` | Bajo | columna presente | ✅ Hecho |
| 8 | Documentar proxy salario | `docs/decision_salario_proxy.md` | Bajo | doc existe | ✅ Hecho |
| 9 | Documentar correlación | `docs/correlacion_renta_alquiler.md` | Bajo | doc existe | ✅ Hecho |
| 10 | Separar temporal/larga | `transform/filtrar_outliers.py` | Bajo | columna tipo_alquiler | ✅ Hecho |

**Espera tu OK antes de ejecutar las acciones pendientes (5, 6).**
