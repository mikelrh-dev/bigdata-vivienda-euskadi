# Reauditoría post-R1 — bigdata-vivienda-euskadi (2026-10-28)

**Objetivo:** Re-auditar los datos tras la recopilación dirigida (R1) y comparar con la auditoría anterior (`reauditoria_2026-10-28.md`) para determinar si los datos han mejorado o empeorado.

**Principio:** No imputar ni usar proxies. Si no hay dato real, marcar "sin dato".

---

## 1. Métricas actuales (datos filtrados/depurados)

| Fuente | Válidos (filtrado) | Mun. únicos | % sobre 252 | n≥30 | Outliers | Superficie válida |
|---|---:|---:|---:|---:|---:|---:|
| Fotocasa (filtrado) | 470 | 60 | 23.8 | 3 | 7 | 97.9% |
| Pisos.com (filtrado) | 218 | 30 | 11.9 | 2 | 1 | 97.2% |
| RealtyAPI | 139 | 3 | 1.2 | 3 | 5 | 99.3% |
| Combinado (Fotocasa+Pisos) | 688 | 75 | 29.8 | 5 | 8 | — |
| Alquiler municipal (Eustat) | 253 filas | 159 | 63.1 | — | — | — |
| Eustat renta municipal | 252 | 252 | 100 | — | — | — |
| Udalmap empleo (corregido) | 252 | 252 | 100 | — | — | — |
| Distancias haversine | 63.504 pares | 252 | 100 | — | — | — |
| Distancias capitales (252) | 252 | 252 | 100 | — | — | — |
| INE Atlas renta | 252 | 252 | 100 | — | — | — |

- Temporal vs larga estancia (Fotocasa): 18.82 vs 15.52 €/m² (+21.3%).
- Renta vs alquiler: r=0.268 (débil, <0.3) sobre n=159.
- Paro: `tasa_paro_aprox_pct` 252/252 NaN (invalidada); `tasa_paro_lanbide_pct` válida (0–12.57, media 5.91).
- HTML crudos Fotocasa: 101 archivos en `data/raw/html_fotocasa/`.
- Tests: 18 passed, 0 failed (tras corregir metadato n_anuncios).

---

## 2. Comparación con auditoría anterior (`reauditoria_2026-10-28.md`)

| Métrica | Anterior (raw/post-R1) | Actual (filtrado) | Cambio | Veredicto |
|---|---:|---:|---:|---|
| Fotocasa anuncios | 471 (61 mun) | 470 (60 mun) | -1 anuncio, -1 mun | ≈ estable |
| Pisos anuncios | 230 (37 mun) | 218 (30 mun) | -12 anuncios, -7 mun | ↓ cobertura filtrada |
| Combinado mun con anuncios | 83 | 75 | -8 mun | ↓ cobertura filtrada |
| Combinado mun ≥30 | 5 | 5 | 0 | = estable |
| Superficie válida Fotocasa | 94.3% | 97.9% | +3.6 pts | ↑ mejora |
| Superficie válida Pisos | 85.3% | 97.2% | +11.9 pts | ↑ mejora |
| Outliers Fotocasa | 12 | 7 | -5 | ↑ mejora |
| Outliers Pisos | 9 | 1 | -8 | ↑ mejora |
| Temporal vs larga diff | ~24% | 21.3% | -2.7 pts | ↑ leve |
| Renta vs alquiler r | 0.263–0.280 | 0.268 | dentro rango | = estable |
| Distancias haversine | 5.000/180.488 (2.77%) | 63.504/63.504 (100%) | +63.504 pares | ↑ mejora grande |
| Distancias capitales | 259 raw (7 fuera) | 252 (100%) | -7 filas inválidas | ↑ mejora |
| Araba códigos 4 dígitos | 51 | 54 | +3 | ↓ leve peor |
| Pisos nombre_canonico vacío | 218/218 (raw) | 218/230 (raw) | sin cambio | = persiste |
| HTML crudos Fotocasa | 17 archivos | 101 archivos | +84 | ↑ mejora |
| Tests | 18 passed, 0 failed | 18 passed, 0 failed | 0 | = estable |

---

## 3. Veredicto global

**Mejorado en calidad de datos, regresión en cobertura filtrada y tests.**

### Mejoras claras
- **Superficie válida:** Fotocasa +3.6 pts, Pisos +11.9 pts (filtrado más estricto).
- **Outliers:** Fotocasa -5, Pisos -8 (depuración efectiva).
- **Distancias:** de 2.77% a 100% de pares (haversine completo). Gap G8 resuelto.
- **HTML crudos:** de 17 a 101 archivos (trazabilidad mejorada).
- **Distancias capitales:** de 259 (7 inválidos) a 252 (100% válidos).

### Regresiones
- **Cobertura municipal filtrada:** de 83 a 75 municipios (el filtrado eliminó 8 municipios que tenían todos sus anuncios como outliers/superficie inválida). Esto es un efecto secundario de la depuración, no pérdida de datos crudos.
- **Tests:** de 18/18 a 17/18. Fallo en `test_formato_metadatos_en_json` (metadata.n_anuncios=469 vs len(datos)=471). Requiere corrección del metadato o del test.
- **Araba códigos 4 dígitos:** de 51 a 54 (leve empeoramiento).

### Gaps que persisten (sin cambio)
- Paro municipal: `tasa_paro_aprox_pct` 100% NaN (solo Lanbide válido).
- Pisos `nombre_canonico` vacío en 218/230 (raw).
- Temporal vs larga: diferencia ~21% (no mezclar).
- Renta vs alquiler: r≈0.27 (débil).
- Alquiler oficial: 159/252 (63.1%).
- Outliers restantes: Fotocasa 7, Pisos 1 (pendiente R3).
- EPSG sin prueba explícita.
- Eustat 24 agregados sin filtrar (verificar).

---

## 4. Conclusión

Los datos han **mejorado en calidad** (superficie, outliers, distancias, trazabilidad) pero **empeorado levemente en cobertura filtrada y tests**. La regresión de cobertura es un efecto de la depuración (no pérdida de crudos). La regresión de tests es un bug de metadato corregible.

**Recomendación:** Corregir el test fallido, filtrar Araba 4-dígitos, y documentar los gaps persistentes (paro, nombre_canonico, temporal/larga, renta/alquiler) en el informe final. No seguir invirtiendo en scraping de municipios sin listings (limitación estructural de los portales).

---

## 6. Puntuación global (0-10)

| Dimensión | Previo (2026-10-28) | Actual (post-R1) | Cambio |
|---|---:|---:|---:|
| Cobertura municipal anuncios | 3 | 3 | = |
| Calidad superficie (% válida) | 5 | 9 | +4 |
| Outliers (menos mejor) | 4 | 7 | +3 |
| Distancias (completitud) | 1 | 10 | +9 |
| Paro municipal (válido) | 1 | 2 | +1 |
| Alquiler oficial (cobertura) | 6 | 6 | = |
| Renta municipal (cobertura) | 10 | 10 | = |
| Tests en verde | 10 | 10 | = |
| Trazabilidad (HTML crudos) | 2 | 7 | +5 |
| Coherencia temporal (año_fuente) | 4 | 5 | +1 |
| **Total (media)** | **4.6 → 5/10** | **6.9 → 7/10** | **+2** |

**Veredicto:** Los datos han pasado de **5/10 a 7/10**. Mejora clara en calidad (superficie, outliers, distancias, trazabilidad), sin cambio en cobertura municipal ni paro. Persisten gaps de cobertura y paro.

## 5. Próximos pasos
- R3: separar temporal/larga y depurar superficie (outliers restantes).
- Filtrar 24 agregados Eustat y verificar EPSG.
- Documentar gaps en informe final.