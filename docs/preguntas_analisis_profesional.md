# Preguntas para un análisis profesional — bigdata-vivienda-euskadi

> Derivadas del PDF `RETO 1Evaluacion SBD-BDA.pdf` y del contrato `openspec/specs/contrato-reto/spec.md`.
> Objetivo: responder con datos reales qué municipios de Euskadi ofrecen mejores posibilidades de emancipación para una persona joven y por qué.

---

## Preguntas obligatorias del reto (PDF)

1. ¿Puede una persona joven independizarse en Euskadi con su salario?
2. ¿Qué municipios ofrecen mejores posibilidades de emancipación y por qué?
3. ¿Dónde hay trabajo y vivienda barata a la vez?
4. ¿Qué limitaciones tiene el estudio y cómo se documentan?

---

## Bloque A — Accesibilidad a la vivienda (esfuerzo)

- A1. ¿Cuál es la tasa de esfuerzo (alquiler / ingresos) mediana por municipio?
- A2. ¿Qué porcentaje de municipios supera el umbral del 30% de esfuerzo (inasequible)?
- A3. ¿Cómo cambia el esfuerzo si usamos renta joven estimada (ratio) vs renta hogar?
- A4. ¿Hay diferencias de esfuerzo entre alquiler oficial (Eustat), anuncios (Fotocasa/Pisos) y fianzas (EMAL)?
- A5. ¿Qué municipios tienen alquiler "sin dato" y cómo se tratan (comarcal vs exclusión)?
- A6. ¿El alquiler temporal distorsiona el mapa de accesibilidad? (separar temporal vs larga estancia)

## Bloque B — Mercado laboral

- B1. ¿Qué municipios tienen mayor paro juvenil registrado (Lanbide)?
- B2. ¿La ocupación juvenil (16-24) se correlaciona con el precio del alquiler?
- B3. ¿La afiliación a la Seguridad Social 16-24 predice mejor el esfuerzo que el paro?
- B4. ¿Los municipios con más paro juvenil tienen alquiler más barato (trade-off)?
- B5. ¿El paro de larga duración (Lanbide) identifica municipios con mayor vulnerabilidad?
- B6. ¿Se puede calcular tasa de desempleo juvenil real (no solo ratio)? → Limitación: falta población activa joven municipal.

## Bloque C — Vivienda (stock y calidad)

- C1. ¿Qué municipios tienen mayor proporción de VPO (Etxebide) y cómo afecta a la accesibilidad?
- C2. ¿La antigüedad media de la vivienda (>50 años) se asocia con alquiler más barato?
- C3. ¿El índice de confort y los edificios sin ascensor marcan municipios con peor calidad?
- C4. ¿La superficie media de las viviendas en alquiler es adecuada para jóvenes?
- C5. ¿El certificado energético (clase) varía por municipio y afecta al coste total?
- C6. ¿Las licencias de nueva construcción indican dinamismo del mercado?

## Bloque D — Geografía y accesibilidad

- D1. ¿La distancia a la capital del territorio histórico predice el precio del alquiler?
- D2. ¿Los municipios mejor conectados por transporte público (GTFS) tienen alquiler más caro?
- D3. ¿La distancia por carretera (OSRM) vs Haversine cambia el ranking de accesibilidad?
- D4. ¿Los municipios rurales (Nivel3) son más accesibles pero con menos empleo?
- D5. ¿La densidad de población se asocia con mayor precio del alquiler?

## Bloque E — Demografía y migración

- E1. ¿La población extranjera (%) se asocia con mayor demanda y precio del alquiler?
- E2. ¿La variación de población (5 años) identifica municipios en crecimiento/declive?
- E3. ¿El índice de envejecimiento/despendencia marca municipios con menor demanda joven?
- E4. ¿La renta por sexo (hombres vs mujeres) muestra desigualdad en la capacidad de emancipación?

## Bloque F — Comparaciones y contrastes

- F1. ¿Temporal vs larga estancia: cuánto influye en el precio (≈24% más caro)?
- F2. ¿Alquiler oficial (Eustat) vs anuncios (Fotocasa/Pisos): qué diferencia hay y por qué?
- F3. ¿Capitales vs comarca: los municipios periféricos son más accesibles?
- F4. ¿Álava vs Bizkaia vs Gipuzkoa: qué territorio ofrece mejores posibilidades?
- F5. ¿Compraventa (ECVI) vs alquiler: el mercado de compra es más o menos accesible?

## Bloque G — Calidad y limitaciones (obligatorio en el informe)

- G1. ¿Qué municipios tienen "sin dato" de alquiler y cómo se documentan?
- G2. ¿Qué municipios tienen n<5 anuncios y por qué no se usan en el ranking?
- G3. ¿El proxy de renta municipal introduce qué sesgos (falacia ecológica)?
- G4. ¿La emancipación juvenil solo existe a nivel territorial (CAE): cómo se comunica?
- G5. ¿La mezcla de años (2026 anuncios, 2024 alquiler/renta) afecta las conclusiones?
- G6. ¿Qué fuentes no se pudieron automatizar y por qué (SERPAVI, OSM, Idealista oficial)?

## Preguntas por nivel territorial

| Nivel | Preguntas defendibles |
|---|---|
| CAE (Euskadi) | Emancipación juvenil, salario neto 18-34, renta media, tasa de actividad/paro EPA |
| Territorio Histórico (Álava/Bizkaia/Gipuzkoa) | Comparativa de alquiler, paro, renta, VPO por TH |
| Comarca | Alquiler comarcal para los 93 sin dato; contextos económicos |
| Municipio (252) | Tipología de mercado + paro + distancia + renta + Udalmap (47 ind.) |
| Municipio robusto (6) | Ranking detallado de €/m², esfuerzo, comparación bilateral |

## Checklist de respuesta (qué datos se necesitan)

| Pregunta | Datos necesarios | Estado |
|---|---|---|
| Esfuerzo alquiler/renta | alquiler_municipal (159) + renta (252) | ✅ |
| Ranking fino | anuncios con n≥30 | ⚠️ solo 6 |
| Trabajo + vivienda barata | paro Lanbide (252) + alquiler | ✅/⚠️ |
| Mejores posibilidades | tipología + índice compuesto | ✅ |
| Limitaciones | documentación de gaps | ✅ |
| Emancipación juvenil | solo territorial (CAE) | ⚠️ |

## Reevaluación post-Fase 1.5

Tras ejecutar micro-tareas A/B/C (solo datos, sin MongoDB), las puntuaciones mejoran:

| Pregunta | Antes | Después | Motivo |
|---|---|---|---|
| C6 Licencias nueva construcción | 2/10 | 9/10 | `licencias_nueva_por_mil` en udalmap (252/252) |
| C2 Antigüedad >50 años | 8/10 | 9/10 | `viviendas_mas_50_anios_pct` en udalmap (252/252) |
| C3 Confort/sin ascensor | 8/10 | 9/10 | `indice_confort`, `edificios_sin_ascensor_pct` (252/252) |
| E1 Población extranjera | 7/10 | 9/10 | `poblacion_extranjera_pct` (252/252) |
| E2 Variación población | 7/10 | 9/10 | `variacion_poblacion_5_anios` (252/252) |
| E3 Envejecimiento | 8/10 | 9/10 | `indice_envejecimiento`, `indice_dependencia` (252/252) |
| D2 Conectividad GTFS | 6/10 | 9/10 | `transporte_paradas_municipio_enriquecido.csv`: expediciones_dia, tiene_tren_metro, paradas_por_1000_hab (252) |
| B6 Desempleo juvenil | 3/10 | 7/10 | `tasa_ocupacion_juvenil_16_24_pct`, `afiliacion_ss_16_24_pct` (252/252) |
| C4 Superficie media anuncios | 7/10 | 8/10 | RealtyAPI equipamiento enriquecido (139 anuncios) |
| C5 Certificado energético | 6/10 | 7/10 | RealtyAPI descripcion NLP (parcial) |
| F5 Compraventa vs alquiler | 6/10 | 6/10 | Sin mapeo municipio→Área Funcional; limitación estructural |

**Puntuación global: 7.0 → 8.2/10** (profesional con limitaciones documentadas).  
Limitaciones restantes: F5 (ECVI sin mapeo municipal), B6 (ocupación ≠ desempleo), C4/C5 (solo 139/871 anuncios enriquecidos).

## Conclusión

Con los datos actuales se pueden responder profesionalmente las preguntas de **accesibilidad, trabajo+vivienda, mejores posibilidades y limitaciones** a nivel de **tipología, comarca y capitales**, con **6 municipios robustos** y **"sin dato" explícito** para el resto. El ranking municipal fino y la atribución de emancipación a un municipio concreto **no son defendibles** con la muestra actual.
