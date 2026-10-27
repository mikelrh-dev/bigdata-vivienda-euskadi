# Auditoría Completa — bigdata-vivienda-euskadi

**Fecha:** 2026-10-27  
**Modo:** Solo lectura y diagnóstico (sin modificar código de producción).  
**Frameworks aplicados:** `03_framework_auditoria_dato_puro.md` (dato puro) + `02_modulos_fase.md` Módulo A (extracción y entity resolution).  
**Módulos B, C, D:** No aplicables (infraestructura HDFS/Kafka/MongoDB y visualización no implementadas).

---

## 1. Métricas Reales Observadas

| Fuente | Registros válidos | Municipios únicos | % sobre 252 | n≥30 | n 5-29 | n<5 | codigo_ine % | Outliers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| alquiler_municipal.csv | 253 | 159 | 63.1% | — | — | — | 100% | — |
| anuncios_fotocasa.csv | 466 | 53 | 21.0% | 3 | 9 | 41 | 100% | 13 |
| anuncios_pisos.csv | 192 | 29 | 11.5% | 0 | 11 | 18 | 100% | 9 |
| anuncios_realtyapi.csv | 139 | 3 | 1.2% | 3 | 0 | 0 | 100% | 5 |
| eustat_renta_municipal.csv | 252 | 252 | 100% | — | — | — | 100% | — |
| udalmap_empleo.csv | 252 | 252 | 100% | — | — | — | 100% | — |
| distancias_capitales.csv | 259 | 252 | 100% | — | — | — | 100% | — |
| distancias_municipios.json | 5.000 pares | 5 orígenes | 2.8% | — | — | — | — | — |
| emancipacion_juventud.csv | 866 filas | — | — | — | — | — | — | — |
| ine_salarios_edad.csv | 198 filas | — | — | — | — | — | — | — |

**Inventario de ficheros raw (FASE 0):** 27 CSV/JSON en `data/raw/`. Registros brutos por fichero en el transcript del subagente (task-0.log).

**Detalles clave:**
- Fotocasa temporal vs larga estancia: 20.70 vs 16.22 €/m² (diferencia -21.6%). No mezclar.
- Superficie válida (15-300 m² + habitaciones no nulo): Fotocasa 95.6%, Pisos.com 94.0%, RealtyAPI 99.3%.
- Correlación Pearson renta municipal vs alquiler municipal: **r = 0.2094** (<0.3).
- Alquiler municipal: 9 distritos, 37 municipios con más de un distrito, max 9 distritos por municipio.
- Udalmap paro: 248/252 municipios con valores negativos (media -10.10%, min -32.46). Fórmula mal derivada.
- Distancias capitales: 2 códigos duplicados (requiere dedup).
- Distancias municipios: solo 5.000/180.488 pares (2.77%), 5 municipios origen en muestra.
- Eustat renta municipal: 252/252 en 2024, 24 etiquetas no-municipio (CA, provincias, comarcas).
- Emancipación: parsea correctamente con `delimiter=';' quotechar='"'` (866 filas, 9 columnas).
- INE salarios edad: nacional (1.372,8 € para 16-24 años). No hay salario municipal gratuito.

**Variantes entity resolution (todas mapeadas):**
- Fotocasa: `Arrankudiaga / Zollo` → `Arrankudiaga-Zollo`, `Arrasate / Mondragón` → `Arrasate/Mondragón`, `Donostia - San Sebastián` → `Donostia / San Sebastián`.
- RealtyAPI: `Donostia-San Sebastián` → `Donostia / San Sebastián` (código 20069).

---

## 2. Auditoría Módulo A — Extracción y Entity Resolution

| Métrica | Fotocasa | Pisos.com | RealtyAPI | Alquiler municipal |
|---|---:|---:|---:|---:|
| Total registros | 480 | 218 | 139 | 253 |
| codigo_ine válido (5 dígitos) | 100% | 100% | 100% | 100% |
| Cruce con Eustat + empleo | 100% | 100% | 100% | 100% |

**Pisos.com superficie/habitaciones:**
- superficie_m2 no nulos: 213/218 (97.7%)
- habitaciones no nulos: 210/218 (96.3%)
- ambos no nulos: 206/218 (94.5%)

**HTML crudos Fotocasa (EXTRACCION-01):**
- `data/raw/html_fotocasa/` contiene **0 archivos HTML**. **NO CUMPLE** EXTRACCION-01.

**GeoJSON (municipios_euskadi.geojson):**
- Features: 259 (257 códigos únicos, 252 municipios canónicos cubiertos)
- CRS: EPSG:4326 ✓
- Distancias Haversine: 0 NaN ✓
- Distancias capitales: 259 filas, 2 duplicados (requiere dedup)

**Suite de tests:**
- 18 passed, 0 failed, 0 xfail, 0 skip ✓

---

## 3. Gaps y Sesgos

### P1 — Crítico
1. **93 municipios sin alquiler oficial** (159/252). Sin `n` muestral por distrito → no se sabe si la media viene de 2 o 200 contratos.
2. **Paro negativo en 248/252 municipios** (media -10.10%, min -32.46). Fórmula mal derivada. Invalida cualquier conclusión de "trabajo + vivienda barata".
3. **Fotocasa cubre solo 53/252 municipios (21.0%)**, solo 3 con n≥30.
4. **Pisos.com cubre 29/252 (11.5%)**, 0 municipios con n≥30.
5. **RealtyAPI solo 3 municipios** (capitales).
6. **Distancias municipios: solo 5.000/180.488 pares (2.77%)**, 5 municipios origen en muestra. No se puede responder "municipio barato a <30km".
7. **HTML crudos Fotocasa ausentes** (EXTRACCION-01 no cumple). Sin trazabilidad de extracción.

### P2 — Alto
1. **Temporal vs larga estancia en Fotocasa difieren 21.6%** (20.70 vs 16.22 €/m²). No mezclar nunca.
2. **Correlación Pearson renta vs alquiler = 0.2094** (<0.3). La renta local explica poco el precio.
3. **Outliers IQR:** Fotocasa 13 (hasta 36.05 €/m²), Pisos 9 (hasta 29.58), RealtyAPI 5 (hasta 35.73). Muchos de 15 m² mal parseados.
4. **Distancias capitales: 2 códigos duplicados** requieren dedup.
5. **Fechas:** Eustat 2024 vs INE Atlas 2022. Añadir columna `año_fuente`.

### P3 — Medio
1. **Pisos.com superficie válida 94.0%** (contradice diagnóstico previo de 0%), pero 8 anuncios sin habitaciones.
2. **Fotocasa superficie válida 95.6%; RealtyAPI 99.3%.**
3. **Emancipación parsea correctamente** con `delimiter=';' quotechar='"'` (866 filas, 9 columnas).
4. **INE salarios edad es nacional** (1.372,8 € 16-24). Usar renta como proxy, no salario municipal.
5. **Distancias capitales cobertura 252/252** tras dedup.
6. **Eustat renta municipal cubre 252/252** en 2024.
7. **INE Atlas cubre 252/252** (fuente independiente, validación cruzada con Eustat).

---

## 4. Veredicto de Suficiencia

**Datos insuficientes para ranking fino de 252 municipios.** Solo 3 municipios con n≥30 en Fotocasa y 0 en Pisos; alquiler oficial cubre 159/252 sin `n` muestral. Renta cubre 252/252 (Eustat + INE Atlas). Paro invalido en 248/252 y distancias solo 2.77% de pares.

**Suficiente para:** análisis comarcal y capitales, ranking de 3 municipios con n≥30, tasa de esfuerzo para 159 municipios con alquiler oficial (sin n muestral).

**Insuficiente para:** ranking municipal fino de 252, tasa de esfuerzo 252/252, conclusión "trabajo + vivienda barata" hasta corregir paro y completar cobertura.

---

## 5. Módulos B, C, D — No implementados

| Módulo | Estado | Evidencia |
|---|---|---|
| B — Infraestructura HDFS/Kafka/MongoDB | **No implementado** | `storage/`, `visualization/`, `notebooks/` vacíos. Sin `docker-compose.yml`. |
| C — MongoDB, limpieza, aggregation pipeline | **No implementado** | Sin colecciones, sin pipelines. |
| D — Visualización e informe | **No implementado** | `visualization/` y `notebooks/` vacíos. |

**Recomendación:** No auditar B/C/D hasta que exista infraestructura. Priorizar correcciones P1 (paro, cobertura alquiler, HTML crudos).

---

## 6. Plan de Corrección Quirúrgico

| # | Acción | Archivos | Esfuerzo | Verificación |
|---|---|---|---|---|
| 1 | Corregir fórmula tasa_paro en `udalmap_empleo.py` o sustituir por EPA/INE provincial; validar rango 0-100 | `extract/udalmap_empleo.py` | Medio | `udalmap_empleo.csv` paro min≥0, max≤100 |
| 2 | Completar alquiler oficial para 93 municipios faltantes (INE Atlas/observatorios) o agregar a comarca | `extract/02_eustat_alquiler.py` | Alto | `alquiler_municipal.csv` 252 municipios únicos |
| 3 | Generar HTML crudos de Fotocasa (EXTRACCION-01) | `extract/05_fotocasa_scraper.py` | Medio | `data/raw/html_fotocasa/` ≥1 archivo |
| 4 | Ampliar scraping hasta n≥30 en municipios objetivo; separar temporal vs larga estancia | `extract/05_fotocasa_scraper.py`, `extract/08_pisos_scraper.py` | Alto | n≥30 en ≥10 municipios |
| 5 | Deduplicar distancias_capitales (2 códigos) | `extract/04_b5m_geo.py` | Bajo | 0 duplicados |
| 6 | Regenerar distancias_municipios completo o para candidatos | `extract/04_b5m_geo.py` | Alto | ≥50% pares |
| 7 | Añadir columna `año_fuente` a renta y alquiler | `transform/dim_municipios.py` o nuevo | Bajo | Columna presente en CSV |
| 8 | Documentar renta como proxy de salario (no hay salario municipal gratuito) | `docs/` | Bajo | Documento en docs/ |

**Espera mi OK antes de editar.**
PY