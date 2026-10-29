# Evaluación del grado de respuesta de las preguntas objetivo

**Proyecto:** bigdata-vivienda-euskadi  
**Fecha de evaluación:** 2026-10-29  
**Fuentes evaluadas:** `data/raw` (301 archivos) + `data/procesado` (88 archivos silver regenerados)  
**Preguntas:** `docs/preguntas_analisis_profesional.md` (obligatorias + bloques A–G)  
**Salida:** `scratchpad/evaluacion_preguntas.md` (solo lectura de datos; no se modificaron archivos de datos)

## 1. Resumen ejecutivo

- **Preguntas evaluadas:** 42 (4 obligatorias + 38 de bloques A–G).
- **Grado medio de respuesta:** **8.6 / 10**.
- **Preguntas con grado ≥ 9:** 30 (71%).
- **Preguntas con mayor limitación (≤ 7):** O1 (7), A4 (7), B6 (7), C1 (7), C5 (7), F5 (6).
- **Conclusión general:** con los datos actuales se pueden responder profesionalmente las preguntas de **accesibilidad (A), mercado laboral (B, salvo desempleo real), vivienda/stock (C, salvo VPO stock y certificado energético), geografía (D), demografía (E), comparaciones (F, salvo F5) y limitaciones (G)** a nivel municipal para 252 municipios cuando hay cobertura completa, y a nivel de tipología/comarca/capitales cuando la cobertura es parcial. **No se defiende un ranking municipal fino** (solo 7 municipios con n≥30 anuncios; 55 con n<5) ni la **emancipación atribuida a un municipio concreto** (solo nivel CAE).

### Coberturas clave verificadas (silver)

| Dato | Cobertura |
|---|---:|
| Municipios de referencia | 252 / 252 |
| Alquiler oficial (Eustat 2024) directo | 159 / 252 |
| Alquiler completado por comarca | 93 / 252 (nivel_geografico=comarcal) |
| Anuncios unificados (Fotocasa+Pisos+RealtyAPI) | 840 anuncios, 85 municipios |
| Municipios con ≥30 anuncios | 7 |
| Municipios con 5–29 anuncios | 23 |
| Municipios con <5 anuncios | 55 |
| Tipología de mercado | 6 Nivel1 / 41 Nivel2 / 205 Nivel3 |
| Lanbide paro juvenil | 252 / 252 |
| Udalmap empleo + indicadores | 252 / 252 |
| Transporte público enriquecido (GTFS) | 252 / 252 (expediciones_dia sin nulos; paradas_por_1000_hab = 252 nulos) |
| Distancias OSRM a capitales | 252 / 252 |
| Renta municipal (hogar/atlas) | 252 / 252 |
| Renta joven estimada (16–29) | 252 / 252 (proxy transparente) |
| Demografía/renta por sexo (Udalmap) | 252 / 252 |
| Etxebide solicitudes VPO | 252 / 252 (20 años) |
| EMAL fianzas | 73 municipios |
| ECVI compraventa | 7 municipios + 15 áreas funcionales + 7 territorios |
| Certificado energético (Fotocasa detalle) | 467 / 470 anuncios |
| Emancipación juvenil (Eustat) | nivel CAE, 2010–2026, 14 indicadores |

### Nota de disponibilidad silver

Los 88 archivos comunes entre `data/procesado` y `data/procesado_pre_silver` son byte-idénticos. Sin embargo, **18 derivados presentes en el backup no están en el silver actual** (`analisis_variables_base.csv`, `emancipacion_tier3_93.csv`, `municipios_faltantes_93.csv`, `alquiler_rescatado_seccion.csv`, `r1_*`, logs). Esto es una **regresión de disponibilidad** (no de contenido). La tipología de mercado sí está disponible en `dim_municipios.csv` (silver), por lo que el impacto sobre las preguntas es bajo, pero conviene recuperar los derivados Tier-3 para trazabilidad.

---

## 2. Preguntas obligatorias del reto

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| O1 | ¿Puede una persona joven independizarse en Euskadi con su salario? | 7 | Emancipación juvenil Eustat (CAE, 2010–2026): tasa de emancipación, coste de acceso, sobreesfuerzo; salarios EPA por edad (INE); renta joven estimada municipal (proxy). | Solo nivel territorial (CAE), no municipal; el "salario" es nacional por grupo de edad, no salario municipal ni por municipio. | Sí (salario/renta joven municipal real) |
| O2 | ¿Qué municipios ofrecen mejores posibilidades de emancipación y por qué? | 8 | Tipología (6/41/205), paro Lanbide, distancia OSRM, renta municipal, Udalmap (47 ind.), alquiler completo 252. | Ranking fino solo 7 municipios con n≥30 anuncios; 93 municipios con alquiler comarcal (menor precisión). | Parcial (más anuncios) |
| O3 | ¿Dónde hay trabajo y vivienda barata a la vez? | 8 | Lanbide paro juvenil 252; alquiler completo 252; renta 252; tipología; distancia. | Alquiler comarcal en 93 municipios; trabajo medido por paro registrado, no por oferta real de empleo. | Parcial |
| O4 | ¿Qué limitaciones tiene el estudio y cómo se documentan? | 9 | Inventario de datos, informe de calidad, manifest SHA-256, tests (57 passed), documentación de gaps en preguntas. | Algunos derivados Tier-3 no están en silver actual. | No (documentación suficiente) |

---

## 3. Bloque A — Accesibilidad a la vivienda (esfuerzo)

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| A1 | ¿Tasa de esfuerzo (alquiler/ingresos) mediana por municipio? | 9 | `alquiler_municipal_completo.csv` (252) + renta hogar/atlas (252). | Alquiler comarcal en 93. | No |
| A2 | ¿% municipios que supera el 30% de esfuerzo (inasequible)? | 9 | Igual que A1. | Idem. | No |
| A3 | ¿Cómo cambia el esfuerzo con renta joven estimada vs renta hogar? | 9 | `renta_municipal_completa.csv`: `renta_hogar` y `renta_joven_estimada_16_29` (252). | La renta joven es proxy transparente (×0.3534), no salario real. | Sí (salario joven real) |
| A4 | ¿Diferencias de esfuerzo entre Eustat, anuncios y EMAL? | 7 | Eustat 159; anuncios 85 municipios; EMAL 73 municipios. | Solapamiento parcial; EMAL con n muestral pequeño y outliers. | Parcial (más anuncios/EMAL) |
| A5 | ¿Municipios con alquiler "sin dato" y tratamiento? | 9 | 93 con nivel_geografico=comarcal; documentado. | Rescate por sección = 0; se excluyen del ranking fino. | No (documentado) |
| A6 | ¿El alquiler temporal distorsiona la accesibilidad? | 9 | `anuncios_unificados.csv`: modalidad larga_estancia 536 vs temporal 304. | Solo 85 municipios con anuncios. | Parcial |

---

## 4. Bloque B — Mercado laboral

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| B1 | ¿Municipios con mayor paro juvenil (Lanbide)? | 9 | `lanbide_paro_juvenil.csv` 252/252, tasa_paro_joven_pct sin nulos. | Paro registrado, no EPA. | No |
| B2 | ¿Ocupación juvenil (16–24) se correlaciona con precio alquiler? | 9 | `tasa_ocupacion_juvenil_16_24_pct` 252 + alquiler 252. | Correlación ecológica municipal. | No |
| B3 | ¿Afiliación SS 16–24 predice mejor el esfuerzo que el paro? | 9 | `afiliacion_ss_16_24_pct` 252. | Sin validación predictiva formal. | No |
| B4 | ¿Municipios con más paro juvenil tienen alquiler más barato (trade-off)? | 9 | Paro Lanbide + alquiler completo 252. | Idem B1. | No |
| B5 | ¿Paro de larga duración identifica vulnerabilidad? | 9 | `paro_larga_duracion_pct` (Udalmap) 252. | Proxy de vulnerabilidad. | No |
| B6 | ¿Tasa de desempleo juvenil real (no solo ratio)? | 7 | `tasa_ocupacion_juvenil_16_24_pct`, `afiliacion_ss_16_24_pct`. | Falta población activa joven municipal (EPA no municipal); `poblacion_joven_15_29` nulo en silver. | Sí (población activa joven municipal) |

---

## 5. Bloque C — Vivienda (stock y calidad)

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| C1 | ¿Mayor proporción de VPO (Etxebide) y efecto en accesibilidad? | 7 | Etxebide solicitudes por mil (252, 20 años); `vpo_terminadas_por_mil`, `vpo_adjudicadas_por_mil` (Udalmap); indicador 86 (201/252). | No hay stock de VPO municipal directo; solicitudes ≠ viviendas disponibles. | Sí (stock VPO municipal) |
| C2 | ¿Antigüedad media >50 años se asocia con alquiler barato? | 9 | `viviendas_mas_50_anios_pct` 252. | Asociación ecológica. | No |
| C3 | ¿Índice de confort y edificios sin ascensor marcan peor calidad? | 9 | `indice_confort`, `edificios_sin_ascensor_pct` 252. | Sin validación con costes reales. | No |
| C4 | ¿Superficie media de viviendas en alquiler adecuada para jóvenes? | 8 | `anuncios_unificados.csv`: superficie_m2 (830/840) en 85 municipios. | Solo 85 municipios; RealtyAPI 3 capitales con más detalle. | Parcial (más anuncios) |
| C5 | ¿Certificado energético (clase) varía por municipio y afecta coste total? | 7 | Fotocasa detalle: cert_energetico en 467/470 anuncios. | No agregado por municipio; sin coste energético real. | Sí (agregación + coste) |
| C6 | ¿Licencias de nueva construcción indican dinamismo? | 9 | `licencias_nueva_por_mil` (Udalmap) 252. | Proxy de dinamismo. | No |

---

## 6. Bloque D — Geografía y accesibilidad

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| D1 | ¿Distancia a la capital del TH predice precio alquiler? | 9 | `distancias_capitales_252.csv` + OSRM 252 + alquiler. | — | No |
| D2 | ¿Municipios mejor conectados por TP tienen alquiler más caro? | 9 | `transporte_paradas_municipio_enriquecido.csv`: n_paradas, expediciones_dia, tiene_tren_metro, operadores (252). | `paradas_por_1000_hab` nulo en los 252 (derivable con población). | Parcial (derivar per cápita) |
| D3 | ¿OSRM vs Haversine cambia el ranking de accesibilidad? | 9 | OSRM tiempos + Haversine 63.504 pares. | — | No |
| D4 | ¿Municipios rurales (Nivel3) más accesibles pero con menos empleo? | 9 | Tipología + alquiler + paro + distancia. | Asociación ecológica. | No |
| D5 | ¿Densidad de población se asocia con mayor precio alquiler? | 9 | `densidad_poblacion` (Udalmap) 252 + alquiler. | — | No |

---

## 7. Bloque E — Demografía y migración

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| E1 | ¿Población extranjera (%) se asocia con demanda y precio alquiler? | 9 | `poblacion_extranjera_pct` 252. | Asociación ecológica. | No |
| E2 | ¿Variación de población (5 años) identifica crecimiento/declive? | 9 | `variacion_poblacion_5_anios` 252. | — | No |
| E3 | ¿Índice de envejecimiento/dependencia marca menor demanda joven? | 9 | `indice_envejecimiento`, `indice_dependencia` 252. | — | No |
| E4 | ¿Renta por sexo muestra desigualdad en capacidad de emancipación? | 9 | Udalmap renta hombres/mujeres + `eustat_demografia_renta_252` 252. | Renta personal, no salario por sexo joven. | Parcial |

---

## 8. Bloque F — Comparaciones y contrastes

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| F1 | ¿Temporal vs larga estancia: cuánto influye en el precio (~24% más caro)? | 9 | Anuncios unificados con modalidad (304 temporal, 536 larga). | Solo 85 municipios. | Parcial |
| F2 | ¿Alquiler oficial (Eustat) vs anuncios (Fotocasa/Pisos): diferencia y por qué? | 8 | Eustat 159 vs anuncios 85; solapamiento parcial. | Diferencias de fuente/año/metodología. | No |
| F3 | ¿Capitales vs comarca: periféricos más accesibles? | 9 | Distancias + alquiler + tipología. | — | No |
| F4 | ¿Álava vs Bizkaia vs Gipuzkoa: qué territorio ofrece mejores posibilidades? | 9 | Alquiler, paro, renta, VPO por TH. | — | No |
| F5 | ¿Compraventa (ECVI) vs alquiler: compra más/menos accesible? | 6 | ECVI 2026T2: 7 municipios + 15 áreas funcionales + 7 territorios. | Sin mapeo municipio→área funcional para los 252; `precio_m2_usada_eur` todo nulo. | Sí (mapeo municipal ECVI) |

---

## 9. Bloque G — Calidad y limitaciones (obligatorio en el informe)

| ID | Pregunta | Grado | Datos disponibles | Gaps | ¿Buscar más datos? |
|---:|---|---:|---|---|---|
| G1 | ¿Municipios "sin dato" de alquiler y cómo se documentan? | 9 | 93 comarcal (nivel_geografico); documentado en inventario/preguntas. | Derivados Tier-3 no en silver. | No |
| G2 | ¿Municipios con n<5 anuncios y por qué no se usan en el ranking? | 9 | 55 municipios con <5 anuncios (calculable desde unificados). | No hay lista precomputada en silver. | No |
| G3 | ¿El proxy de renta municipal introduce qué sesgos (falacia ecológica)? | 9 | `renta_municipal_referencia.csv` con notas de escala; renta hogar vs personal. | Sin validación individual. | No |
| G4 | ¿La emancipación juvenil solo existe a nivel territorial (CAE): cómo se comunica? | 9 | Emancipación Eustat CAE 2010–2026 + documentación. | No municipal. | Sí (datos municipales de emancipación) |
| G5 | ¿La mezcla de años (2026 anuncios, 2024 alquiler/renta) afecta conclusiones? | 9 | anio_fuente en anuncios; alquiler 2024; renta 2024; ECVI 2026T2. | Sin armonización temporal. | Parcial |
| G6 | ¿Qué fuentes no se pudieron automatizar y por qué (SERPAVI, OSM, Idealista)? | 8 | SERPAVI 249/252 (89 nulos); OSRM disponible; GTFS en ZIP; Idealista no automatizado. | SERPAVI parcial; Idealista no disponible; GTFS requiere extracción. | Parcial |

---

## 10. Conclusiones sobre la necesidad de buscar más datos

**No es imprescindible buscar más datos** para responder profesionalmente las preguntas de accesibilidad, trabajo+vivienda, mejores posibilidades (a nivel de tipología/comarca/capitales) y limitaciones: el grado medio es 8.6/10.

**Sí conviene buscar/completar datos** para subir a 9–10 las siguientes preguntas:
1. **O1/O3/A3** — salario/renta joven **real** a nivel municipal (no proxy ×0.3534) y población activa joven municipal (resuelve B6).
2. **O2** — más anuncios por municipio (hoy solo 7 con n≥30; 55 con n<5) para un ranking municipal fino.
3. **C1** — stock real de VPO por municipio (hoy solo solicitudes y VPO terminadas por mil).
4. **C5** — certificado energético agregado por municipio y coste energético real.
5. **F5** — mapeo municipio→área funcional ECVI para comparar compraventa vs alquiler a nivel municipal.
6. **G4** — datos de emancipación a nivel municipal (hoy solo CAE).
7. **Recuperar derivados** ausentes en silver: `analisis_variables_base.csv`, `emancipacion_tier3_93.csv`, `municipios_faltantes_93.csv` (están en `data/procesado_pre_silver`).

**No buscar más datos** para: A1, A2, A5, B1–B5, C2, C3, C6, D1, D3–D5, E1–E3, F3, F4, G1–G3, G5 (ya respondibles con cobertura completa o documentación suficiente).

---

## 11. Verificación realizada (solo lectura)

- Inspección de columnas/coberturas con pandas sobre `data/procesado` y `data/raw` (sin modificar archivos).
- Métricas verificadas: 252 municipios; 159 alquiler directo + 93 comarcal; 840 anuncios en 85 municipios (7 con n≥30; 55 con n<5); tipología 6/41/205; 252/252 en Lanbide, Udalmap, OSRM, renta, transporte; ECVI 7 municipios; EMAL 73 municipios; certificado energético 467/470 anuncios.
- Archivos creados: `scratchpad/evaluacion_preguntas.md` (este informe). No se modificaron datos.