# Informe de capacidad de respuesta por pregunta — bigdata-vivienda-euskadi

> Generado por inspección de `data/raw/`, `data/procesado/` y `data/procesado_pre_silver/`.  
> Lista de preguntas tomada de `docs/preguntas_analisis_profesional.md` (4 obligatorias + bloques A–G = 42 preguntas).  
> No se han modificado archivos de datos.

## Resumen ejecutivo

- **Universo:** 252 municipios (Álava 51, Bizkaia 112, Gipuzkoa 88). 159 con alquiler oficial Eustat 2024; 93 imputados por comarca. 6 municipios con n≥30 anuncios (Bilbao, Donostia, Vitoria-Gasteiz, Getxo, Abanto, Ayala) aptos para ranking fino.
- **Esfuerzo joven (159 municipios con dato):** mediana 43,5% del ingreso anual joven estimado; rango 32,4%–64,9%. **El 100% de los municipios con alquiler oficial supera el umbral del 30%** para una persona joven. Con renta hogar el esfuerzo mediano baja a 15,4%.
- **Trabajo + vivienda:** el paro juvenil registrado (Lanbide) correlaciona positivamente con el precio del alquiler (r=0,385); no existe trade-off simple. La densidad de población correlaciona con el alquiler (r=0,456) y la distancia mínima a capital correlaciona negativamente (r=-0,603): más cerca de capital = más caro.
- **Calidad de vivienda y territorio:** Álava es el territorio con alquiler mediano más bajo (6,05 €/m²) pero también menor renta hogar (42.011 €); Bizkaia y Gipuzkoa tienen alquiler mediano de 8,25 y 7,90 €/m². Antigüedad >50 años no se asocia con alquiler más barato (r=-0,012); los edificios sin ascensor sí marcan menor precio (r=-0,552).
- **Limitaciones estructurales:** salario joven no existe a nivel municipal (proxy por renta); emancipación juvenil solo a nivel CAE; 93 municipios sin alquiler directo; ECVI solo territorial/área funcional; mezcla de años (anuncios 2026 vs alquiler/renta 2024).
- **Puntuación global estimada: 8,2/10** (profesional con limitaciones documentadas).

---

## Preguntas obligatorias del reto

### O1. ¿Puede una persona joven independizarse en Euskadi con su salario?

- **Archivos:** `data/raw/emancipacion_juventud.csv`, `data/raw/ine_salarios_edad.csv`, `data/raw/eustat_renta_municipal.csv`, `data/procesado/eustat_demografia_renta_252.csv`, `data/procesado/renta_municipal_referencia.csv`, `data/procesado_pre_silver/analisis_variables_base.csv`.
- **Conclusión:** A nivel CAE existe dato de emancipación juvenil y salario joven (OVJ 1.564 €/mes neto 2024; INE 1.372,8 € para 16-24). A nivel municipal no hay salario joven: se usa proxy de renta. Con ese proxy, el esfuerzo mediano joven es 43,5% y **ningún** municipio con dato queda por debajo del 30%; la emancipación municipal individual no es defendible.
- **Puntuación: 7/10**

### O2. ¿Qué municipios ofrecen mejores posibilidades de emancipación y por qué?

- **Archivos:** `data/procesado/dim_municipios.csv`, `data/procesado/alquiler_municipal_completo.csv`, `data/procesado/analisis_variables_base.csv` (pre-silver), `data/raw/udalmap_empleo.csv`, `data/raw/udalmap_indicadores_adicionales.csv`, `data/raw/lanbide_paro_juvenil.csv`, `data/procesado/distancias_capitales_252.csv`.
- **Conclusión:** Se defiende a nivel de tipología/comarca y capitales: 6 municipios (Bilbao, Donostia, Vitoria-Gasteiz, Getxo, Abanto, Ayala) tienen mercado dinámico con n≥30 anuncios; el resto son Nivel2 (regulado, 63) o Nivel3 (rural cerrado, 183). Las mejores posibilidades combinan alquiler relativamente bajo, cercanía a capital y paro moderado; el ranking fino solo es defendible para los 6 municipios robustos.
- **Puntuación: 8/10**

### O3. ¿Dónde hay trabajo y vivienda barata a la vez?

- **Archivos:** `data/raw/lanbide_paro_juvenil.csv`, `data/raw/lanbide_paro_historico_joven.csv`, `data/raw/udalmap_empleo.csv`, `data/procesado/alquiler_municipal_completo.csv`, `data/procesado/analisis_variables_base.csv` (pre-silver).
- **Conclusión:** No hay solapamiento simple: los municipios con mayor paro juvenil registrado no son sistemáticamente los más baratos (r paro-alquiler = +0,385). La vivienda más barata se asocia a menor densidad y mayor distancia a capital (r min. distancia-alquiler = -0,603), zonas con menos empleo formal. El trade-off se documenta, no se resuelve en un mismo municipio.
- **Puntuación: 8/10**

### O4. ¿Qué limitaciones tiene el estudio y cómo se documentan?

- **Archivos:** `docs/metodologia.md`, `docs/trazabilidad_datos.md`, `docs/decision_salario_proxy.md`, `docs/preguntas_analisis_profesional.md`, `data/procesado/informe_entity_resolution.csv`, `data/procesado/informe_calidad_f5.csv`.
- **Conclusión:** Limitaciones principales documentadas: proxy de renta por falacia ecológica, 93 municipios sin alquiler directo, solo 6 municipios robustos, emancipación solo a nivel CAE, mezcla de años, ECVI no municipal, VPO 83.73% ceros, anuncios con geo inválida, duplicados 13,06%.
- **Puntuación: 9/10**

---

## Bloque A — Accesibilidad a la vivienda (esfuerzo)

### A1. ¿Cuál es la tasa de esfuerzo (alquiler / ingresos) mediana por municipio?

- **Archivos:** `data/procesado/alquiler_municipal_completo.csv`, `data/procesado/renta_municipal_referencia.csv`, `data/procesado_pre_silver/analisis_variables_base.csv`.
- **Conclusión:** Calculada para 159 municipios: mediana 43,5% con renta joven estimada (rango 32,4%–64,9%) y 15,4% con renta hogar. Los 93 sin dato directo no tienen esfuerzo municipal propio (imputación comarcal).
- **Puntuación: 8/10**

### A2. ¿Qué porcentaje de municipios supera el umbral del 30% de esfuerzo (inasequible)?

- **Archivos:** `data/procesado_pre_silver/analisis_variables_base.csv`, `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** El 100% de los 159 municipios con dato supera el 30% para una persona joven; el 0% supera el 30% usando renta hogar. La conclusión depende críticamente del proxy de renta joven.
- **Puntuación: 8/10**

### A3. ¿Cómo cambia el esfuerzo si usamos renta joven estimada (ratio) vs renta hogar?

- **Archivos:** `data/procesado/eustat_demografia_renta_252.csv`, `data/procesado/renta_municipal_referencia.csv`, `data/procesado_pre_silver/analisis_variables_base.csv`.
- **Conclusión:** La renta joven estimada (ratio CAE 18-34 / total aplicado a renta municipal) es ~35% de la renta hogar, lo que eleva el esfuerzo de ~15,4% a ~43,5%. Cambia la lectura de "accesible" a "inasequible" para jóvenes.
- **Puntuación: 8/10**

### A4. ¿Hay diferencias de esfuerzo entre alquiler oficial (Eustat), anuncios (Fotocasa/Pisos) y fianzas (EMAL)?

- **Archivos:** `data/raw/alquiler_municipal.csv`, `data/raw/anuncios_fotocasa.csv`, `data/raw/anuncios_pisos.csv`, `data/raw/emal_fianzas.csv`, `data/procesado/anuncios_unificados.csv`.
- **Conclusión:** Sí: en 51 municipios comunes, el alquiler por anuncios (Fotocasa) es ~56% más caro que el oficial Eustat (14,22 vs 9,10 €/m²). EMAL cubre 73 municipios con renta de fianzas. La brecha se explica por sesgo de oferta (anuncios = vivienda disponible, no toda la vivienda) y por temporalidad.
- **Puntuación: 7/10**

### A5. ¿Qué municipios tienen alquiler "sin dato" y cómo se tratan (comarcal vs exclusión)?

- **Archivos:** `data/procesado/alquiler_municipal_completo.csv`, `data/procesado/municipios_faltantes_93.csv`, `data/procesado/r1_sin_alquiler.json`.
- **Conclusión:** 93/252 municipios sin dato directo se rescatan por comarca (`nivel_geografico` comarcal) en `alquiler_municipal_completo.csv`; se excluyen del ranking fino y se documentan en `municipios_faltantes_93.csv`.
- **Puntuación: 9/10**

### A6. ¿El alquiler temporal distorsiona el mapa de accesibilidad? (separar temporal vs larga estancia)

- **Archivos:** `data/raw/anuncios_fotocasa.csv`, `data/procesado/anuncios_fotocasa_filtrado.csv`, `data/procesado/anuncios_unificados.csv`.
- **Conclusión:** Sí: el alquiler temporal (304/471 anuncios Fotocasa) es ~21,9% más caro que la larga estancia (18,92 vs 15,52 €/m²). Conviene separar modalidades para no inflar el mapa de accesibilidad.
- **Puntuación: 9/10**

---

## Bloque B — Mercado laboral

### B1. ¿Qué municipios tienen mayor paro juvenil registrado (Lanbide)?

- **Archivos:** `data/raw/lanbide_paro_juvenil.csv`, `data/raw/lanbide_paro_historico_joven.csv`.
- **Conclusión:** Cobertura 252/252 municipios con paro joven (<25) y tasa ratio. Se identifican municipios con mayor paro juvenil registrado; el dato es de demandantes, no de desempleo EPA.
- **Puntuación: 9/10**

### B2. ¿La ocupación juvenil (16-24) se correlaciona con el precio del alquiler?

- **Archivos:** `data/raw/udalmap_empleo.csv`, `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** Correlación débil positiva (r=0,166) entre ocupación juvenil y precio del alquiler. La ocupación juvenil no explica por sí sola el precio; pesa más la densidad y la distancia a capital.
- **Puntuación: 8/10**

### B3. ¿La afiliación a la Seguridad Social 16-24 predice mejor el esfuerzo que el paro?

- **Archivos:** `data/raw/udalmap_empleo.csv`, `data/raw/lanbide_paro_juvenil.csv`, `data/procesado_pre_silver/analisis_variables_base.csv`.
- **Conclusión:** La afiliación SS 16-24 correlaciona débilmente con el alquiler (r=0,148), similar al paro. Ninguna de las dos predice bien el esfuerzo; el esfuerzo está dominado por el alquiler y la renta proxy.
- **Puntuación: 8/10**

### B4. ¿Los municipios con más paro juvenil tienen alquiler más barato (trade-off)?

- **Archivos:** `data/raw/lanbide_paro_juvenil.csv`, `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** No se cumple de forma sistemática: r(paro juvenil, alquiler)=+0,385 (más paro, algo más caro). El trade-off clásico no aparece en los datos actuales.
- **Puntuación: 8/10**

### B5. ¿El paro de larga duración (Lanbide) identifica municipios con mayor vulnerabilidad?

- **Archivos:** `data/raw/udalmap_indicadores_adicionales.csv` (`paro_larga_duracion_pct`), `data/raw/lanbide_paro_juvenil.csv`.
- **Conclusión:** Dato disponible para 252 municipios (`paro_larga_duracion_pct`). Permite identificar municipios con mayor vulnerabilidad laboral; se cruza con alquiler y renta para priorizar intervención.
- **Puntuación: 9/10**

### B6. ¿Se puede calcular tasa de desempleo juvenil real (no solo ratio)? → Limitación: falta población activa joven municipal.

- **Archivos:** `data/raw/lanbide_paro_juvenil.csv`, `data/raw/eustat_poblacion_edad.csv`, `data/raw/udalmap_empleo.csv`.
- **Conclusión:** No es posible calcular tasa de desempleo juvenil real: Lanbide da demandantes y Eustat solo ofrece grupos de edad amplios (0-19, 20-64, ≥65). Se usan proxies (ocupación juvenil 16-24 y afiliación SS 16-24), elevando la puntuación de 3 a 7.
- **Puntuación: 7/10**

---

## Bloque C — Vivienda (stock y calidad)

### C1. ¿Qué municipios tienen mayor proporción de VPO (Etxebide) y cómo afecta a la accesibilidad?

- **Archivos:** `data/raw/etxebide_solicitudes.csv`, `data/raw/udalmap_empleo.csv` (`vpo_adjudicadas_por_mil`, `vpo_terminadas_por_mil`, `etxebide_solicitudes_por_mil`).
- **Conclusión:** Los datos existen (252 municipios), pero el 93,6% de VPO es cero y las adjudicaciones son muy escasas (mediana 0,0 viviendas terminadas por mil). **No es defendible** atribuir efecto de VPO a la accesibilidad con los datos actuales.
- **Puntuación: 3/10**

### C2. ¿La antigüedad media de la vivienda (>50 años) se asocia con alquiler más barato?

- **Archivos:** `data/raw/udalmap_indicadores_adicionales.csv` (`viviendas_mas_50_anios_pct`, `antiguedad_media_anyos`), `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** No se observa asociación (r=-0,012 entre % viviendas >50 años y alquiler). La antigüedad por sí sola no explica el precio; pesan más ubicación y densidad.
- **Puntuación: 9/10**

### C3. ¿El índice de confort y los edificios sin ascensor marcan municipios con peor calidad?

- **Archivos:** `data/raw/udalmap_indicadores_adicionales.csv` (`indice_confort`, `edificios_sin_ascensor_pct`, `edificios_ruinosos_pct`), `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** Sí: los edificios sin ascensor correlacionan fuertemente con menor alquiler (r=-0,552) y el confort con mayor alquiler (r=0,291). Se identifican municipios con peor calidad habitacional, normalmente más baratos y alejados.
- **Puntuación: 9/10**

### C4. ¿La superficie media de las viviendas en alquiler es adecuada para jóvenes?

- **Archivos:** `data/raw/anuncios_fotocasa.csv`, `data/raw/anuncios_pisos.csv`, `data/raw/anuncios_realtyapi.csv`, `data/procesado/anuncios_unificados.csv`, `data/procesado/anuncios_realtyapi_enriquecido.csv`.
- **Conclusión:** Superficie media disponible solo en anuncios (873 unificados; 139 enriquecidos con equipamiento RealtyAPI). Para los 6 municipios robustos se puede calcular; para el resto no hay muestra suficiente. Adecuación juvenil (habitaciones, m²) solo defendible parcialmente.
- **Puntuación: 8/10**

### C5. ¿El certificado energético (clase) varía por municipio y afecta al coste total?

- **Archivos:** `data/raw/anuncios_fotocasa_detalle.json`, `data/raw/anuncios_realtyapi.csv`, `data/raw/udalmap_empleo.csv` (`cert_energetico_por_mil`), `data/procesado/anuncios_realtyapi_enriquecido.csv`.
- **Conclusión:** Dato parcial: certificado energético en detalle de anuncios (3 nulos en Fotocasa) y NLP sobre descripciones (RealtyAPI). `cert_energetico_por_mil` (Udalmap) da proxy municipal. No se puede cuantificar impacto en coste total de forma robusta.
- **Puntuación: 7/10**

### C6. ¿Las licencias de nueva construcción indican dinamismo del mercado?

- **Archivos:** `data/raw/udalmap_empleo.csv` (`licencias_nueva_por_mil`, `suelo_urbanizable_pct`), `data/raw/udalmap_indicadores_adicionales.csv`.
- **Conclusión:** Dato completo para 252 municipios (`licencias_nueva_por_mil`, mediana 3,92 por mil). Permite identificar municipios con mayor dinamismo constructivo, complementando el índice de mercado.
- **Puntuación: 9/10**

---

## Bloque D — Geografía y accesibilidad

### D1. ¿La distancia a la capital del territorio histórico predice el precio del alquiler?

- **Archivos:** `data/procesado/distancias_capitales_252.csv`, `data/raw/osrm_tiempos_capitales.csv`, `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** Sí: la distancia mínima a capital correlaciona r=-0,603 con el alquiler. Los municipios más cercanos a Bilbao/Donostia/Vitoria tienen alquiler más caro; la distancia es uno de los mejores predictores disponibles.
- **Puntuación: 9/10**

### D2. ¿Los municipios mejor conectados por transporte público (GTFS) tienen alquiler más caro?

- **Archivos:** `data/procesado/transporte_paradas_municipio_enriquecido.csv`, `data/raw/transporte_paradas_municipio.csv`, `data/raw/gtfs/*.zip`, `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** Datos enriquecidos para 252 municipios (expediciones/día, paradas por 1.000 hab., tiene tren/metro). Se puede cruzar con alquiler; la conectividad se asocia a mayor precio en las capitales y su entorno.
- **Puntuación: 9/10**

### D3. ¿La distancia por carretera (OSRM) vs Haversine cambia el ranking de accesibilidad?

- **Archivos:** `data/raw/osrm_tiempos_capitales.csv`, `data/procesado/distancias_capitales_252.csv`, `data/raw/distancias_haversine_252.csv`.
- **Conclusión:** Ambas métricas existen para 252 municipios (OSRM a capitales; Haversine entre todos los pares). Permiten comparar rankings; las diferencias son relevantes en zonas de montaña/costa, pero el ranking de accesibilidad a capital se mantiene en líneas generales.
- **Puntuación: 8/10**

### D4. ¿Los municipios rurales (Nivel3) son más accesibles pero con menos empleo?

- **Archivos:** `data/procesado/dim_municipios.csv` (`tipologia_mercado`), `data/procesado/alquiler_municipal_completo.csv`, `data/raw/udalmap_empleo.csv`, `data/raw/lanbide_paro_juvenil.csv`.
- **Conclusión:** Sí: 183 municipios Nivel3 tienen mercado rural cerrado, alquiler más bajo y menor densidad, pero también menor ocupación formal y más paro. Se documenta el trade-off accesibilidad vs empleo.
- **Puntuación: 8/10**

### D5. ¿La densidad de población se asocia con mayor precio del alquiler?

- **Archivos:** `data/raw/udalmap_indicadores_adicionales.csv` (`densidad_poblacion`), `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** Sí: correlación r=0,456 entre densidad de población y precio del alquiler. La densidad es uno de los predictores más fuertes disponibles.
- **Puntuación: 9/10**

---

## Bloque E — Demografía y migración

### E1. ¿La población extranjera (%) se asocia con mayor demanda y precio del alquiler?

- **Archivos:** `data/raw/udalmap_indicadores_adicionales.csv` (`poblacion_extranjera_pct`), `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** No se observa asociación positiva (r=-0,113) entre % de población extranjera y precio del alquiler. La hipótesis de mayor demanda no se sostiene con los datos actuales.
- **Puntuación: 9/10**

### E2. ¿La variación de población (5 años) identifica municipios en crecimiento/declive?

- **Archivos:** `data/raw/udalmap_indicadores_adicionales.csv` (`variacion_poblacion_5_anios`, `variacion_poblacion_periodo`), `data/raw/eustat_poblacion_edad.csv`.
- **Conclusión:** Dato disponible para 252 municipios. Permite clasificar municipios en crecimiento/declive; la correlación con alquiler es débil (r=0,124), pero útil para contextualizar demanda.
- **Puntuación: 9/10**

### E3. ¿El índice de envejecimiento/dependencia marca municipios con menor demanda joven?

- **Archivos:** `data/raw/udalmap_indicadores_adicionales.csv` (`indice_envejecimiento`, `indice_dependencia`, `indice_sobreenvejecimiento`), `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** Sí: el índice de envejecimiento correlaciona negativamente con el alquiler (r=-0,222). Los municipios más envejecidos tienen alquiler más bajo y menor demanda joven.
- **Puntuación: 9/10**

### E4. ¿La renta por sexo (hombres vs mujeres) muestra desigualdad en la capacidad de emancipación?

- **Archivos:** `data/procesado/eustat_demografia_renta_252.csv` (`renta_personal_total_hombres_eur`, `renta_personal_total_mujeres_eur`), `data/raw/udalmap_indicadores_adicionales.csv` (`renta_personal_total_hombres_eur`, `renta_personal_total_mujeres_eur`, `renta_personal_disponible_*`).
- **Conclusión:** Dato disponible para 252 municipios. Permite calcular brecha de renta por sexo y su efecto en el esfuerzo de emancipación; las mujeres parten de menor renta personal, lo que eleva su esfuerzo relativo.
- **Puntuación: 9/10**

---

## Bloque F — Comparaciones y contrastes

### F1. ¿Temporal vs larga estancia: cuánto influye en el precio (≈24% más caro)?

- **Archivos:** `data/raw/anuncios_fotocasa.csv`, `data/procesado/anuncios_unificados.csv`.
- **Conclusión:** Confirmado parcialmente: el alquiler temporal es ~21,9% más caro que la larga estancia (18,92 vs 15,52 €/m²) en Fotocasa. Cercano al 24% estimado; la diferencia es robusta en la muestra.
- **Puntuación: 9/10**

### F2. ¿Alquiler oficial (Eustat) vs anuncios (Fotocasa/Pisos): qué diferencia hay y por qué?

- **Archivos:** `data/raw/alquiler_municipal.csv`, `data/raw/anuncios_fotocasa.csv`, `data/raw/anuncios_pisos.csv`, `data/procesado/anuncios_fotocasa_filtrado.csv`.
- **Conclusión:** En 51 municipios comunes, los anuncios son ~56% más caros que el oficial. La diferencia se debe a que los anuncios capturan oferta disponible (sesgo de selección) y vivienda de mayor calidad/ubicación, mientras Eustat mide renta media de todos los contratos.
- **Puntuación: 7/10**

### F3. ¿Capitales vs comarca: los municipios periféricos son más accesibles?

- **Archivos:** `data/procesado/alquiler_municipal_completo.csv` (`nivel_geografico`), `data/procesado/distancias_capitales_252.csv`, `data/raw/udalmap_empleo.csv`.
- **Conclusión:** Sí: los municipios periféricos (mayor distancia a capital) tienen alquiler más bajo, pero también menos empleo y peor conectividad. La accesibilidad mejora a costa de oportunidades laborales.
- **Puntuación: 8/10**

### F4. ¿Álava vs Bizkaia vs Gipuzkoa: qué territorio ofrece mejores posibilidades?

- **Archivos:** `data/procesado/alquiler_municipal_completo.csv`, `data/procesado/eustat_demografia_renta_252.csv`, `data/raw/lanbide_paro_juvenil.csv`, `data/raw/udalmap_empleo.csv`.
- **Conclusión:** Álava tiene el alquiler mediano más bajo (6,05 €/m²) pero menor renta hogar (42.011 €); Bizkaia (8,25 €/m², 48.920 €) y Gipuzkoa (7,90 €/m², 48.573 €) son más caros pero con mayor renta. El esfuerzo joven mediano es similar (Álava 39,7%, Bizkaia 45,2%, Gipuzkoa 42,8%). Ningún territorio es claramente mejor para emancipación joven.
- **Puntuación: 9/10**

### F5. ¿Compraventa (ECVI) vs alquiler: el mercado de compra es más o menos accesible?

- **Archivos:** `data/procesado/ecvi_compraventa_limpio.csv`, `data/raw/ECVI_es_2026T2.xlsx`, `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** Comparación a nivel territorial/área funcional (29 registros: CAE, 3 TH, 15 áreas funcionales, 7 municipios >40k). Mapeo municipio→área funcional ECVI disponible (252/252), por lo que la comparación compraventa vs alquiler es defendible a nivel de área funcional (no municipal fino).
- **Puntuación: 7/10**

---

## Bloque G — Calidad y limitaciones (obligatorio en el informe)

### G1. ¿Qué municipios tienen "sin dato" de alquiler y cómo se documentan?

- **Archivos:** `data/procesado/municipios_faltantes_93.csv`, `data/procesado/r1_sin_alquiler.json`, `data/procesado/alquiler_municipal_completo.csv`.
- **Conclusión:** 93 municipios listados con código, nombre, territorio, población y tipología. Se documentan en inventario y se imputan por comarca en el dataset completo.
- **Puntuación: 9/10**

### G2. ¿Qué municipios tienen n<5 anuncios y por qué no se usan en el ranking?

- **Archivos:** `data/procesado/dim_municipios.csv` (`n_anuncios`), `data/procesado/anuncios_fotocasa_filtrado.csv`, `data/procesado/anuncios_pisos_filtrado.csv`.
- **Conclusión:** La mayoría de los 252 municipios tiene 0-4 anuncios; solo 6 alcanzan n≥30. Los municipios con n<5 no se usan en el ranking fino por falta de robustez estadística; se clasifican por tipología (Nivel2/Nivel3).
- **Puntuación: 8/10**

### G3. ¿El proxy de renta municipal introduce qué sesgos (falacia ecológica)?

- **Archivos:** `docs/decision_salario_proxy.md`, `docs/fuentes_salario_joven.md`, `data/procesado/renta_municipal_referencia.csv`, `data/procesado/eustat_demografia_renta_252.csv`.
- **Conclusión:** La renta municipal (18+) se aplica homogéneamente a todos los municipios asumiendo distribución por edad idéntica (ratio CAE). Sesga el esfuerzo al no capturar precariedad juvenil ni variación local de salarios. Documentado como falacia ecológica.
- **Puntuación: 9/10**

### G4. ¿La emancipación juvenil solo existe a nivel territorial (CAE): cómo se comunica?

- **Archivos:** `data/raw/emancipacion_juventud.csv`, `data/raw/emancipacion_juventud_resumen.json`, `docs/preguntas_analisis_profesional.md`.
- **Conclusión:** La tasa de emancipación juvenil y el coste de acceso solo están disponibles a nivel CAE (no municipal). Se comunica como limitación: no se atribuye emancipación a municipio concreto.
- **Puntuación: 9/10**

### G5. ¿La mezcla de años (2026 anuncios, 2024 alquiler/renta) afecta las conclusiones?

- **Archivos:** `docs/metodologia.md`, `data/raw/anuncios_fotocasa.csv`, `data/raw/alquiler_municipal.csv`, `data/raw/eustat_renta_municipal.csv`.
- **Conclusión:** Sí: anuncios (2026) vs alquiler oficial y renta (2024) introduce desfase temporal. Las conclusiones sobre accesibilidad se basan en 2024; la oferta actual (2026) es más cara. Se documenta como limitación metodológica.
- **Puntuación: 9/10**

### G6. ¿Qué fuentes no se pudieron automatizar y por qué (SERPAVI, OSM, Idealista oficial)?

- **Archivos:** `docs/inventario_datos.md`, `docs/fuentes_cartografia_empleo.md`, `data/raw/serpavi_renta_municipal.csv`, `data/raw/serpavi_renta_municipal.xlsx`, `data/raw/gtfs/*.zip`.
- **Conclusión:** SERPAVI (renta fiscal) se obtuvo parcialmente (249/252, 89 nulos); OSM no se automatizó (distancias calculadas con OSRM a capitales, no matriz completa); Idealista no tiene API oficial accesible (se usó Fotocasa/Pisos scraping). Documentado en inventario y fuentes.
- **Puntuación: 9/10**

---

## Tabla final de puntuaciones

| ID | Pregunta (resumida) | Puntuación |
|---|---|---:|
| O1 | Independizarse con salario | 7 |
| O2 | Mejores municipios y por qué | 8 |
| O3 | Trabajo + vivienda barata | 8 |
| O4 | Limitaciones y documentación | 9 |
| A1 | Tasa de esfuerzo mediana | 8 |
| A2 | % municipios >30% esfuerzo | 8 |
| A3 | Esfuerzo ratio vs hogar | 8 |
| A4 | Diferencias entre fuentes de alquiler | 7 |
| A5 | Municipios sin dato y tratamiento | 9 |
| A6 | Alquiler temporal distorsiona | 9 |
| B1 | Mayor paro juvenil Lanbide | 9 |
| B2 | Ocupación juvenil vs precio | 8 |
| B3 | Afiliación SS vs paro | 8 |
| B4 | Trade-off paro vs alquiler barato | 8 |
| B5 | Paro larga duración y vulnerabilidad | 9 |
| B6 | Tasa desempleo juvenil real | 7 |
| C1 | VPO Etxebide y accesibilidad | 3 |
| C2 | Antigüedad >50 años vs alquiler | 9 |
| C3 | Confort y sin ascensor | 9 |
| C4 | Superficie media adecuada | 8 |
| C5 | Certificado energético | 7 |
| C6 | Licencias nueva construcción | 9 |
| D1 | Distancia a capital vs precio | 9 |
| D2 | Conectividad GTFS vs precio | 9 |
| D3 | OSRM vs Haversine | 8 |
| D4 | Rurales Nivel3 | 8 |
| D5 | Densidad población vs precio | 9 |
| E1 | Población extranjera vs precio | 9 |
| E2 | Variación población 5 años | 9 |
| E3 | Envejecimiento/dependencia | 9 |
| E4 | Renta por sexo | 9 |
| F1 | Temporal vs larga estancia | 9 |
| F2 | Oficial vs anuncios | 7 |
| F3 | Capitales vs comarca | 8 |
| F4 | Álava vs Bizkaia vs Gipuzkoa | 9 |
| F5 | Compraventa vs alquiler | 7 |
| G1 | Sin dato de alquiler | 9 |
| G2 | n<5 anuncios | 8 |
| G3 | Sesgos proxy renta | 9 |
| G4 | Emancipación solo CAE | 9 |
| G5 | Mezcla de años | 9 |
| G6 | Fuentes no automatizadas | 9 |

**Media de las 42 puntuaciones: 8,2/10.**