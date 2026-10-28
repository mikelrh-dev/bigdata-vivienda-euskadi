# Reauditoría comparativa — Framework de Auditoría de Dato Puro (post-incorporación)

**Fecha:** 2026-10-28
**Fuente del framework:** `framework_auditoria_completo2/03_framework_auditoria_dato_puro.md`
**Auditoría anterior:** `openspec/audit/reauditoria_framework_2026-10-28.md` (8.1/10)
**Ejecución:** 4 sub-agentes en paralelo (FASE 0+1, FASE 2, FASE 3, FASE 4). SOLO LECTURA.

---

## 1. Métricas reales observadas

### FASE 0 — Inventario real (sobre 252 municipios)

| Fuente | Registros | Válidos | Municipios | % 252 | codigo_ine % |
|---|---:|---:|---:|---:|---:|
| anuncios_fotocasa | 471 | 453 | 56 | 22.2 | 99.6 |
| anuncios_pisos | 230 | 200 | 35 | 13.9 | 100.0 |
| anuncios_realtyapi | 139 | 138 | 3 | 1.2 | 100.0 |
| alquiler_municipal | 253 | 253 | 159 | 63.1 | 100.0 |
| eustat_renta_municipal | 98532 | 89607 | 252 | 100.0 | 91.3 (raw; 252/252 tras filtro) |
| udalmap_empleo | 252 | 252 | 252 | 100.0 | 100.0 |
| educacion_centros (NUEVO) | 1309 | 1309 | 197 | 78.2 | 100.0 |
| salud_centros (NUEVO) | 528 | 528 | 231 | 91.7 | 100.0 |
| distancias_capitales_252 | 252 | 252 | 252 | 100.0 | 100.0 |
| distancias_haversine_252 | 63504 | 63504 | 252 | 100.0 | 100.0 |
| distancias_municipios (legacy) | 5000 | 5000 | 5 | 2.0 | 0.0 |
| emancipacion_juventud | 866 | 866 | 0 | 0.0 | 0.0 (territorial) |

### FASE 1 — Entity resolution

- `codigo_ine`: Fotocasa 99.6% (2 null = Las Rozas de Madrid, fuera de Euskadi), Pisos 100%, RealtyAPI 100%, alquiler 100%.
- Variantes mapeadas a canónico (Arrankudiaga/Zollo, Donostia-San Sebastián) vía `dim_municipios` variantes.
- Eustat: 24 agregados (CA, 3 provincias, 20 comarcas) en raw (276 ámbitos, 8568 filas). Filtrados en `transform/dim_municipios.py` por longitud de código. `renta_municipal_completa` 252/252.

### FASE 2 — Cobertura muestral

Anuncios por municipio:

| Fuente | n total | munis | n>=30 | 5-29 | <5 |
|---|---:|---:|---:|---:|---:|
| Fotocasa (raw) | 471 | 61 | 3 (Bilbao 189, Donostia 80, Getxo 40) | 9 | 49 |
| Fotocasa (filtrado) | 470 | 60 | 3 | 9 | 48 |
| Pisos (raw) | 230 | 37 | 2 (Ayala 30, Abanto 30) | 11 | 24 |
| Pisos (filtrado) | 218 | 30 | 2 | 11 | 17 |
| RealtyAPI | 139 | 3 | 3 (Bilbao 50, Donostia 50, Vitoria 39) | 0 | 0 |

- Unión de fuentes de anuncios: 82 municipios con al menos un anuncio.
- Oficial + anuncios: 172 municipios. 80 municipios sin ninguna fuente.
- Temporal vs larga estancia (Fotocasa, filtrado): mediana 18.82 vs 15.52 €/m² (+21.3%, flagged). Mean 20.15 vs 16.06 (+25.5%).
- Alquiler oficial: 159/252 (63.1%), 253 distritos, sin n muestral por distrito. 93 municipios sin dato.

### FASE 3 — Calidad estadística

Outliers (IQR) y superficie válida:

| Fuente | Outliers IQR (high) | Superficie válida % |
|---|---:|---:|
| Fotocasa (raw) | 14 | 95.3 |
| Pisos (raw) | 9 | 93.5 |
| RealtyAPI | 5 | 100.0 (1 sup>300) |
| Fotocasa (filtrado) | 12 | 95.5 |
| Pisos (filtrado) | 9 | 94.0 |

- Split Fotocasa: larga estancia 4 outliers, temporal 11 outliers.
- Renta vs alquiler: r = 0.1655 (n=139), prácticamente igual al anterior (0.17).
- Emancipación: parsea correctamente (14 indicadores, 9 columnas, sin corrupción). Resuelto el problema previo de `;` en campos.
- Procesado outlier flag sub-detecta: Fotocasa 12 IQR vs 7 marcados; Pisos 9 vs 1 marcado (umbral 50€/m²).

### FASE 4 — Validez de dominio

Udalmap (252 municipios):

| Indicador | min | max | media | negativos | NaN |
|---|---:|---:|---:|---:|---:|
| tasa_actividad_pct | 40.63 | 60.09 | 49.79 | 0 | 0 |
| tasa_ocupacion_pct | 41.39 | 74.14 | 54.86 | 0 | 0 |
| tasa_paro_lanbide_pct | 0.00 | 12.57 | 5.91 | 0 | 0 |
| tasa_ocupacion_juvenil_16_24 | 0.00 | 87.50 | 42.39 | 0 | 0 |
| tasa_paro_aprox_pct | — | — | — | 0 (null) | 252 |

Distancias: haversine completo 63504 pares, 0 NaN, 0 duplicados, 252 orígenes/destinos. Araba 4-dígitos: 54 (capitales), 51 (252), 12852 pares (haversine). JSON legacy: 5000 pares (2.78%).
Salarios: nacional (1372.8€ 16-24), sin municipal. Proxy renta documentado.
Fechas: año_fuente presente. Anuncios 2026, renta/alquiler 2024, distancias 2025 (mezcla temporal a documentar).
GeoJSON: EPSG:4326, 252 features, todos 5 dígitos. OK.
Eustat: 201/252 municipios con dato 2024 (51 dependen de INE Atlas).
Tests: 54 passed, 0 failed.

---

## 2. Gaps y sesgos (P1 / P2 / P3)

### P1 Crítico
- Cobertura de anuncios: solo 3 municipios con n>=30 en Fotocasa (Bilbao, Donostia, Getxo), 2 en Pisos (Ayala, Abanto). 80 municipios sin ninguna fuente. Insuficiente para ranking municipal fino.
- Alquiler oficial: 93/252 sin dato (36.9%). Sin n muestral por distrito (no se sabe representatividad).
- Araba 4-dígitos en CSV (54/51/12852): rompe joins si se lee como texto sin zfill. Persiste. JSON conserva 5 dígitos.
- distancias_municipios.json legacy: solo 5000/180488 pares (2.78%). No usable para consultas arbitrarias (aunque haversine CSV completo existe).

### P2 Alto
- Procesado outlier flag sub-detecta (12 IQR vs 7 marcados en Fotocasa; 9 vs 1 en Pisos). Umbral 50€/m² pierde rango 36-50.
- Pisos filtering reduce cobertura de 37 a 30 municipios.
- Mezcla temporal/larga estancia: mediana +21.3% (filtrado). Obliga a separar.
- Eustat renta: 201/252 en 2024 (51 dependen de INE Atlas). Mezcla de años entre fuentes.
- Udalmap: ocupación juvenil min 0.0 en algunos municipios (posible falta de dato disfrazada de cero). Brecha ocupación>actividad en algunos (bases distintas).
- Renta vs alquiler r=0.1655 (débil): el precio no lo explica la renta local.
- Emancipación: indicadores territoriales (0 municipios), no municipal.

### P3 Medio
- tasa_paro_aprox_pct completamente null (252/252) por invalidación metodológica. Correcto, pero consumidores deben usar tasa_paro_lanbide_pct.
- informe_entity_resolution.csv desactualizado (Fotocasa 470 vs raw 471; Pisos 218 vs raw 230).
- Eustat raw contiene 24 agregados (8568 filas); consumidores directos del CSV deben filtrar por longitud de código.
- Salario municipal por edad no existe; proxy renta documentado (P-02 cumplido).
- distancias_capitales.csv: 259 filas, 2 códigos duplicados (1003, 48072). Usar distancias_capitales_252.csv.

---

## 3. Veredicto de suficiencia (FASE 5)

1. ¿Ranking de 252 municipios por coste de acceso con error <20%?
   NO. Solo 3 municipios con n>=30 (Fotocasa), 2 (Pisos), 3 (RealtyAPI, capitales). 80 municipios sin ninguna fuente. Mejora marginal vs anterior (unión 82 vs 75 municipios con anuncios), pero muestra robusta sin cambio.

2. ¿Tasa de esfuerzo alquiler/renta para 252?
   PARCIAL. Renta completa (252/252 con INE Atlas para 51). Alquiler oficial solo 159/252 (63.1%). 93 sin dato oficial. Posible con proxy comarcal pero no municipal fino.

3. ¿"Dónde hay trabajo y vivienda barata"?
   PARCIAL (mejorado). Paro ahora válido (0 negativos, Lanbide 0-12.57%). Distancias completas en haversine CSV. Pero cobertura de anuncios baja (80 munis sin fuente) y 93 sin alquiler oficial. Se puede responder para capitales/comarcas, no para los 252.

---

## 4. Comparación con auditoría anterior (8.1/10)

| Dimensión | Anterior | Nuevo | Cambio |
|---|---:|---:|---|
| Cobertura anuncios | 3 | 3 | = (3 mun n>=30, sin cambio robusto) |
| Alquiler oficial | 6 | 6 | = (159/252, 93 sin dato) |
| Renta municipal | 10 | 10 | = (252/252) |
| Paro municipal | 7 | 9 | +2 (negativo resuelto) |
| Distancias | 9 | 9 | = (haversine completo, pero Araba 4-digit persiste en CSV) |
| Entity resolution | 8 | 9 | +1 (99.6-100%, variantes, Eustat filtrado) |
| Calidad estadística | 8 | 8.5 | +0.5 (pisos 0%->94%, emancipación OK, outliers split) |
| Tests | 10 | 10 | = (54/54) |
| Trazabilidad | 7 | 7.5 | +0.5 (manifest via main_ingest) |
| Automatización | 9 | 9.5 | +0.5 (26 fuentes, +educación/salud) |
| Documentación | 9 | 9 | = |

Nueva media: ~8.3/10 (anterior 8.1). Mejora modesta porque las dimensiones débiles (anuncios 3, alquiler 6) son estructurales y no se han cerrado. Las mejoras reales son en paro, entity resolution, calidad y automatización.

### Resueltos vs anterior
- Paro negativo (-10.10% Baliarrain): RESUELTO (Lanbide 0-12.57, 0 negativos).
- Pisos superficie 0%: RESUELTO (93.5% raw, 94.0% filtrado).
- Emancipación corrupta (; en campos): RESUELTO (parsea OK, 14 indicadores).
- Distancias 5k pares: PARCIALMENTE (haversine CSV completo 63504; JSON legacy 5000 persiste).
- Araba 4-dígitos: PERSISTE en CSV (54/51/12852). Necesita zfill.
- Eustat 24 agregados: FILTRADO en transform (dim_municipios por longitud código). OK.
- EPSG: VERIFICADO (4326, 252 features). OK.

---

## 5. Plan de corrección quirúrgico

### P1 (crítico, hacer antes de defensa)
1. Corregir Araba 4-dígitos: `transform/enriquecer_codigo_ine.py` (zfill en CSV). Esfuerzo bajo (1-2h). Verificar: 0 códigos de 4 dígitos en todos los CSV.
2. Separar temporal/larga estancia en agregaciones (ya flag, falta documentar en pipeline). Esfuerzo bajo.
3. Marcar 80 municipios sin ninguna fuente como "sin dato" (limitación estructural). Documentar. Esfuerzo bajo.

### P2 (alto, recomendable)
4. Recalcular outlier flag en `transform/filtrar_outliers.py` con IQR por segmento (temporal/larga) en vez de umbral fijo 50€/m². Esfuerzo medio (2-3h).
5. Actualizar `informe_entity_resolution.csv` (contadores desfasados). Esfuerzo bajo.
6. Filtrar Eustat 24 agregados en consumidores directos del CSV (o documentar que transform ya lo hace). Esfuerzo bajo.
7. Reemplazar `distancias_municipios.json` legacy (5000 pares) por el haversine completo, o eliminarlo y usar `distancias_haversine_252.csv`. Esfuerzo bajo.

### P3 (medio, opcional)
8. Buscar dataset de Lanbide paro por edad (si se quiere desglose 16-19/20-24/25-29). Esfuerzo medio.
9. Incorporar Observatorio Vivienda (comarcal) si se quiere contexto de mercado. Esfuerzo medio.
10. Documentar mezcla de años (anuncios 2026 vs renta 2024 vs distancias 2025) en análisis.

---

## Veredicto final

El proyecto pasa de 8.1 a ~8.3/10. Mejoras reales y verificables en paro, entity resolution, calidad y automatización. Gaps estructurales persistentes: cobertura de anuncios (3/10) y alquiler oficial (6/10). No es un 9/10 hasta cerrar cobertura municipal o documentar el límite (ranking comarcal + capitales). Los datos son científicamente más sólidos que antes (paro válido, superficie real, emancipación parseable, haversine completo).
