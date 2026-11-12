# Guion — Presentación v2 (híbrida: datos + ingeniería)

**Duración objetivo:** 17:45 (21 diapositivas) · **Recorte a 12:00** al final.
**Público:** tribunal SBD + BDA (perfil técnico, poco tiempo, mucha pregunta).
**Idioma:** castellano. **Formato:** 16:9 fijo, offline, sin dependencias.
**Regla de oro:** primero la respuesta, después cómo se calculó. Cada cifra lleva su
artefacto. Ninguna cifra de este guion se teclea a mano: todas salen de
`data/resultados/*.csv` o de Mongo.

> **Cifras congeladas (2026-11-12).** Si algo cambia, se regenera el CSV antes de tocar
> la diapositiva. Las cifras obsoletas que **no** se usan: 182 silver, 277 tests, 54/65/40,
> 62/252 con precio, 79,3 % de mediana 2026 (corte viejo de 52 municipios).
> Cifras vigentes: **355 raw** · **185 silver** · **53/53 gold** · **287 tests**
> (285 passed, 2 skipped) · **287 anuncios válidos en 50 municipios** · **78,6 %**.

---

## Estructura y tiempos

| # | Diapositiva | Inicio | Fin | Acto |
|---|---|---|---:|---|
| 1 | La pregunta | 0:00 | 0:30 | Apertura |
| 2 | La respuesta en 30 s (solo 2024) | 0:30 | 1:50 | Apertura |
| 3 | Cómo se mide | 1:50 | 2:40 | 2024, el ancla |
| 4 | De dónde sale el 2024 | 2:40 | 3:50 | 2024, el ancla |
| 5 | El mapa de 2024 | 3:50 | 4:45 | 2024, el ancla |
| 6 | El reparto de 2024 | 4:45 | 5:45 | 2024, el ancla |
| 7 | Qué aguanta el ancla | 5:45 | 6:45 | 2024, el ancla |
| 8 | Los cuatro robustos (puente) | 6:45 | 7:45 | 2026, la oferta |
| 9 | De dónde sale el 2026 | 7:45 | 8:20 | 2026, la oferta |
| 10 | El resultado de la capa 2026 | 8:20 | 9:00 | 2026, la oferta |
| 11 | Cobertura de la capa 2026 | 9:00 | 9:25 | 2026, la oferta |
| 12 | Validación: SERPAVI y portales | 9:25 | 9:55 | 2026, la oferta |
| 13 | Esfuerzo por tipología | 9:55 | 10:25 | 2026, la oferta |
| 14 | Diferencia de nivel 2024 vs 2026 | 10:25 | 11:00 | 2026, la oferta |
| 15 | Dos mapas 2026 | 11:00 | 11:25 | 2026, la oferta |
| 16 | Capas, gold y una orden | 11:25 | 12:30 | Cómo se construyó |
| 17 | Modelo Mongo y contenido | 12:30 | 13:30 | Cómo se construyó |
| 18 | Aggregation, índices y CRUD | 13:30 | 14:30 | Cómo se construyó |
| 19 | Pruebas | 14:30 | 15:30 | Cómo se construyó |
| 20 | Límites | 15:30 | 16:45 | Límites y cierre |
| 21 | Cierre | 16:45 | 17:00 | Límites y cierre |

La charla son dos historias separadas —primero 2024 oficial, después 2026 de oferta— y
solo al final se explica cómo se construyó. La 8 es el puente: la única tabla donde las
dos capas se tocan. Límites (20) y cierre (21) van al final, no en medio.

---

# Acto 0 — Apertura

## D1 · La pregunta (0:00–0:30)

- **Mensaje:** el reto no es Mongo, es una pregunta con consecuencias.
- **En pantalla:** solo la pregunta, grande. «¿Puede una persona joven independizarse
  en Euskadi con su salario?» Pie: «Datos reales · 2024-2026 · 252 municipios».
- **Gráfica:** ninguna.
- **Evidencia:** —
- **Rúbrica:** apertura de C18.
- **Nota oral:** «Nos pidieron demostrar con datos reales en qué municipios de Euskadi
  una persona joven puede emanciparse. No vamos a empezar por la base de datos: vamos a
  empezar por la respuesta, y luego enseñamos cómo la hemos calculado para que puedan
  desmontarla si quieren.»
- **Transición:** «La respuesta cabe en treinta segundos.»

---

## D2 · La respuesta en 30 segundos (0:30–1:50)

- **Mensaje:** en la mayoría del territorio se va justo; en las dos capitales grandes,
  no; y en 188 municipios no podemos afirmarlo.
- **En pantalla (4 cifras, no más):**
  - **26,61 %** mediana del esfuerzo joven 18-34 (159 municipios con alquiler oficial)
  - **40 de 159** superan el 30 % (25,2 %)
  - **Bilbao 37,69 % · Donostia 38,17 %**
  - **188** municipios sin anuncio: «sin dato», no «asequible»
- **Gráfica:** ninguna (cuatro números grandes).
- **Evidencia:** `data/resultados/mongo_esfuerzo_por_municipio.csv`.
- **Rúbrica:** C18, C17.
- **Nota oral:** «El indicador es el estándar de emancipación: el alquiler anual dividido
  por la renta joven estimada. La mediana se lleva el 26,6 %. En 40 de los 159 municipios
  con dato se pasa del 30 %. En Bilbao y Donostia se roza el 38 %, y ahí la respuesta es
  no. En 188 municipios no hay anuncios: decimos “no lo sabemos”, que no es lo mismo que
  “es barato”.»
- **Transición:** «¿Y cómo se mide eso?»

---

# Acto 1 — 2024, el ancla oficial

## D3 · Cómo se mide (1:50–2:40)

- **Mensaje:** el indicador no es nuestro; lo que aportamos es hacerlo municipal y decir
  dónde no se puede calcular.
- **En pantalla (fórmula grande):**
  `esfuerzo = (alquiler mensual × 12) / renta joven estimada 18-34 × 100`
  - mediana, no media (los alquileres tienen outliers)
  - umbral 30 % (literatura de emancipación)
  - **18-34 es el canónico**; 16-29 queda **legacy**, no se usa para concluir
- **Gráfica:** ninguna.
- **Evidencia:** `analysis/mongo_aggregations.py` → `pipeline_indicadores_municipio`.
- **Rúbrica:** C17, JOVEN-18-34.
- **Nota oral:** «La renta joven no existe publicada por municipio y edad. La estimamos con
  las bandas de Eustat 18-19, 20-24, 25-29 y 30-34, ponderando por anchura, y la aplicamos
  a la renta municipal. Es un proxy, y lo decimos: no es un salario. El 16-29 antiguo da
  42,9 % de mediana y no es comparable; está en la base como legacy y no sostiene ninguna
  conclusión.»
- **Transición:** «¿De dónde sale ese alquiler oficial?»

---

## D4 · De dónde sale el 2024 (2:40–3:50)

- **Mensaje:** el ancla de 2024 es oficial y municipal, pero no cubre todo: 159 municipios
  con alquiler Eustat, 93 imputados y 188 sin ningún anuncio (101 de ellos sí con alquiler
  oficial). El hueco se enseña, y se distingue «sin anuncio» de «sin dato».
- **En pantalla:**
  - **159** con alquiler oficial Eustat · **93** imputados IDW (solo sensibilidad)
  - **4** Tier A (muestra ≥30) · **188** Tier D (sin anuncio; 101 de esos 188 con alquiler oficial)
  - **355** ficheros originales · **352** canónicos en HDFS · **13** familias de fuentes
  - Eustat alquiler · INE renta joven · Lanbide/Udalmap paro · Etxebide 5.040 solicitudes y 406 promociones
- **Gráfica:** `g4_distribucion_anuncios.png` (anuncios 2026, la cola larga; el pie lo fecha).
- **Evidencia:** `config/fuentes.yaml`, `docs/raw_manifest_sha256.txt`, `mongo_tier_confianza.csv`.
- **Rúbrica:** C1, C5, C6, C15.
- **Nota oral:** «De dónde sale esto: Eustat nos da el alquiler municipal, el INE la renta
  joven, Lanbide y Udalmap el paro, y Etxebide la demanda. En total, 355 ficheros originales
  y 352 canónicos con SHA. Pero el ancla tiene agujeros y los enseñamos: 159 municipios tienen
  alquiler oficial, 93 van imputados por IDW y solo los usamos para sensibilidad, y 188 no
  tienen ningún anuncio — aunque 101 de esos 188 sí tienen alquiler oficial: sin anuncio no
  es sin dato. Y fíjate en la cola larga del gráfico, que son anuncios de 2026: casi todos los
  municipios tienen cero, uno o dos; por eso exigimos 30 para sostener una mediana.»
- **Transición:** «Con eso, el mapa.»

---

## D5 · El mapa de 2024 (3:50–4:45)

- **Mensaje:** el esfuerzo tiene geografía: capitales y costa arriba; interior y sur, abajo.
- **En pantalla:** coroplético municipal, 159 oficiales (color) + 93 IDW imputado (trama) con
  leyenda propia; escala 20,3–30 % y el color saturado por encima de 30 %.
- **Gráfica:** `mapa_coroplastico_esfuerzo_18_34.png`.
- **Evidencia:** figura generada desde `mongo_esfuerzo_por_municipio.csv`.
- **Rúbrica:** C19, C18.
- **Nota oral:** «Cada municipio con alquiler oficial, coloreado por esfuerzo; la trama es el
  IDW comarcal, que no es dato y por eso va rayado y aparte en la leyenda. No hace falta leer
  nombres: Bilbao, Donostia y el corredor del Nervión están en la banda alta; el interior de
  Álava y amplias zonas rurales, por debajo del 30 %. Y el rojo se corta a los 30: los 40 que
  lo superan comparten el mismo tono, no son todos iguales.»
- **Transición:** «¿Cuántos quedan a cada lado del umbral?»

---

## D6 · El reparto de 2024 (4:45–5:45)

- **Mensaje:** no es un problema de cuatro municipios: 40 de 159 pasan del 30 %, y 14 se
  van por encima del 35 %.
- **En pantalla (cifras grandes):**
  - **119** por debajo del 30 %
  - **26** entre 30 % y 35 %
  - **14** por encima del 35 %
  - **40/159** por encima del 30 % (25,2 %)
  - 93 IDW aparte, solo sensibilidad
- **Gráfica:** `hist_esfuerzo_18_34_umbral30.png`.
- **Evidencia:** CSV oficial.
- **Rúbrica:** C16, C19.
- **Nota oral:** «Tres cuartas partes del territorio con dato están por debajo del 30 %,
  pero una de cada cuatro lo supera, y hay 14 municipios por encima del 35 %. Con el IDW la
  mediana baja a 25,37 % y los que superan el 30 % son 47 de 252: el titular aguanta, la
  lista cambia.»
- **Transición:** «¿Y cuánto de esto es incertidumbre?»

---

## D7 · Qué aguanta el ancla (5:45–6:45)

- **Mensaje:** el titular aguanta la incertidumbre; dos hallazgos laterales cambian la
  lectura: temporal≠larga y la demanda social no sigue al precio.
- **En pantalla:**
  - Bootstrap 95 %: Bilbao 33,75–40,95 · Getxo 27,54–31,77 · Donostia 32,4–45,8 (se solapan).
    El ancho mide dispersión de **precios de anuncio 2026** sobre el nivel 2024, y el n≥30 son
    anuncios: no es un intervalo del estimador Eustat.
  - IDW 93: mediana 23,38 %; global 252: 25,37 %
  - Temporal y larga: misma **mediana mensual (1.500 €)**, pero el temporal es más
    pequeño (80 vs 92,5 m²). **Por m², el temporal es +23,2 % en Fotocasa** (+13,7 % en el total)
  - Tensión Etxebide (solicitudes por mil) vs esfuerzo: no es una recta
- **Gráficas:** `H8b_modalidad_mediana_eur_m2.png` + `H10_tension_vs_esfuerzo.png`.
- **Evidencia:** `bootstrap_robustos.csv`, `sensibilidad_idw.csv`, `mongo_tier_confianza.csv`.
- **Rúbrica:** C16, C17, C18.
- **Nota oral:** «Con bootstrap, los intervalos de Bilbao, Getxo y Donostia se solapan: no
  hay orden firme entre ellos. Y ojo a lo que mide ese intervalo: el nivel es Eustat 2024, el
  ancho es cuánto se movería si cambiara la muestra de precios de 2026; no es el error del
  dato oficial, que es un registro, no una encuesta. El IDW baja la mediana un punto y cuarto en el global
  (a 25,37 %; 23,38 % solo imputados), pero no cambia el
  titular. Dos cosas que descubrimos por el camino: los anuncios temporales no son más caros
  al mes, sino por metro cuadrado — 18,95 frente a 16,67 €/m² en el total, un 13,7 %, y frente
  a 15,38 en Fotocasa, un 23,2 % — porque el piso temporal es más pequeño (80 frente a 92,5 m²);
  por eso no se mezclan. Y la demanda social no va en línea recta con el precio,
  hay municipios con mucha lista de espera y alquiler moderado.»
- **Transición:** «Y con eso, ¿qué municipios aguantan una comparación firme?»

---

# Acto 2 — 2026, la capa de oferta

## D8 · Los cuatro robustos (6:45–7:45)

- **Mensaje:** cuatro municipios sostienen el ranking; el orden 3º/4º es frágil y lo decimos.
- **En pantalla (tabla):**

| Municipio | n 2026 | Esfuerzo 18-34 (2024) | Precio mediana anuncio (2026) | Paro general (2024, 16-64) |
|---|---:|---:|---:|---:|
| Bilbao | 68 | 37,69 % | 1.687,50 € | 9,71 % |
| Donostia / San Sebastián | 58 | 38,17 % | 2.000,00 € | 5,82 % |
| Getxo | 39 | 28,60 % | 1.350,00 € | 6,40 % |
| Vitoria-Gasteiz | 37 | 33,37 % | 1.300,00 € | 8,89 % |

  - Getxo vs Vitoria: **2 anuncios** de diferencia → sin ranking firme 3º/4º
  - **Barakaldo: n=2** → cualquier mediana municipal es ruido, no ranking
  - **Vintages distintos:** el esfuerzo usa alquiler oficial 2024; el precio es asking 2026; el paro es Udalmap 2024 general 16-64
  - **Mismo universo que D8** (287 anuncios filtrados): antes D9 usaba 594 sin filtrar y convivían dos `n` para la misma ciudad
- **Gráfica:** `O_ranking_bloqueado_n30.png` (IC y resto en gris).
- **Evidencia:** `esfuerzo_mercado_2026.csv`, `comparativa_3_municipios_mongo.csv`, `pipeline_indicadores_municipio`.
- **Rúbrica:** C18 (núcleo), C17.
- **Nota oral:** «Bilbao y Donostia están en el 38 % con la muestra más grande. Getxo está
  por debajo del 30 % pero por 1,4 puntos, y solo tiene 11 anuncios más que Vitoria: no
  convertimos eso en un podio. Barakaldo saldría el primero del ranking de esfuerzo con
  38,5 %, y tiene seis anuncios: por eso el umbral de 30. Lo que sí decimos: en Bilbao la
  tensión es precio más paro; en Donostia es precio puro, con el paro más bajo.»
- **Transición:** «Esa tabla cruza dos capas. ¿De dónde sale el precio de 2026?»

---

## D9 · De dónde sale el 2026 (7:45–8:20)

- **Mensaje:** la capa 2026 no es un número mágico: son 287 anuncios de tres portales,
  después de descartar más de la mitad de lo capturado.
- **En pantalla:**
  - **843** crudos → **594** vigentes (dedup entre portales y 45 en cuarentena fuera de Euskadi)
    → **326** con precio → **287** válidos
  - 10 excluidos por el propio pipeline (900 m², 9.500 €) · 29 sin precio · 2 municipios caen
    a 0 anuncios (Amorebieta-Etxano, Laguardia): el mapa pasa de 52 a 50
  - Por portal (mediana): fotocasa 152 · 1.432 € · 15,36 €/m² | pisos 60 · 1.500 € · 16,67 |
    realtyapi 75 · 1.690 € · 19,43
- **Gráfica:** ninguna; tabla de portales.
- **Evidencia:** `data/resultados/validacion_portales_2026.csv`, `transform/_anuncios_2026.py`.
- **Rúbrica:** C1, C5, C15.
- **Nota oral:** «El 2026 sale de tres portales: fotocasa, pisos y realtyapi. De 843 anuncios
  crudos quedan 594 vigentes después de quitar duplicados y 45 en cuarentena fuera de Euskadi;
  326 tienen precio, y de esos descartamos 10 que el propio pipeline había marcado como
  imposibles —pisos de 900 metros, alquileres de 9.500 euros— y 29 sin precio. Quedan 287.
  Y aquí ya se ve un problema: realtyapi es un 26 % más caro por metro cuadrado que fotocasa.
  No son tres cámaras iguales, y por eso lo medimos antes de mezclarlo.»
- **Transición:** «Con esa muestra, el resultado.»

---

## D10 · El resultado de la capa 2026 (8:20–9:00)

- **Mensaje:** con la muestra limpia, el 98,3 % de los anuncios 2026 supera el 30 % del salario joven; la mediana municipal es 78,6 %, pero solo 4 municipios tienen muestra suficiente para sostenerla.
- **En pantalla:**
  - **78,6 %** mediana esfuerzo mercado 2026 (50 municipios con anuncio)
  - **1.350 €** precio mediana anuncio 2026 · **1.719 €** salario joven 18-34 ajustado 2026 (OVJ 2024 × IPC INE 1,099)
  - **98,3 %** de los **287 anuncios** supera el 30 % (10 anuncios excluidos por el propio pipeline)
  - **Banda 57,8 % – 86,3 %** según el denominador (renta joven 2024 / sin ajuste)
  - Cobertura: **71,2 % de la población 18-34**; **4 municipios con n≥10** concentran el 70,4 % de los anuncios
- **Gráfica:** `M26_ic_esfuerzo.png` (IC95 % bootstrap; solo n≥5)
- **Evidencia:** `data/procesado/esfuerzo_mercado_2026.csv`, `transform/calcular_esfuerzo_mercado_2026.py`, `analysis/cobertura_representatividad_2026.py`.
- **Rúbrica:** C17, C19.
- **Nota oral:** «Esta es la capa de oferta. Limpiamos los diez anuncios que nuestro propio pipeline ya había marcado como inválidos —pisos de 900 m², alquileres de 9.500 €— y quedan 287 anuncios en 50 municipios. El 98,3 % supera el 30 % del salario neto joven. La mediana municipal da 78,6 %, pero no la vendemos como un dato sólido: 43 de los 50 municipios tienen menos de cinco anuncios y no admiten mediana. Solo Bilbao, Donostia, Getxo y Vitoria tienen muestra; ahí sí hay intervalo, y el límite inferior de Donostia ya está en el 96 % del salario. Los 50  municipios cubren el 71,2 % de la población joven, así que la cobertura es defendible aunque el mapa tenga huecos. Un aviso más, que prefiero dar yo: los anuncios vienen de tres portales y realtyapi tiene un 26 % más de €/m². Quitar realtyapi mueve Donostia 23 puntos y deja la mediana global igual: está calculado y publicado en `validacion_portales_2026.csv`, no escondido.»
- **Transición:** «Antes de seguir: ¿a quién representa esta capa?»

---

## D11 · Cobertura de la capa 2026 (9:00–9:25)

- **Mensaje:** la capa 2026 no cubre el mapa entero, cubre dos tercios de la población joven;
  el resto es ausencia de dato, no baratura. Sin esta diapositiva, el 78,6 % parece nacional.
- **En pantalla:**
  - **50 de 252** municipios con anuncio válido
  - **71,2 %** de la población 18-34
  - **70,4 %** de los anuncios se concentra en 4 municipios (n≥10)
  - **43 municipios con n<5**: sin mediana publicada
- **Gráfica:** `M26_cobertura.png` (% de población cubierta por territorio y total).
- **Evidencia:** `data/resultados/cobertura_representatividad_2026.csv`,
  `analysis/cobertura_representatividad_2026.py`.
- **Rúbrica:** C16, C19.
- **Nota oral:** «Antes de que nadie lo pregunte: esta capa no cubre los 252 municipios,
  cubre 50. Pero no son 50 cualesquiera: son el 71,2 % de la población de 18 a 34 años. Y de
  los 287 anuncios, 202 están en cuatro municipios. Por eso el 78,6 % se puede defender como
  nivel y no como mapa: en los 43 municipios con menos de cinco anuncios no publicamos
  mediana. El gris del mapa es falta de dato, no un precio bueno.»
- **Transición:** «Y si alguien desconfía del anuncio como fuente...»

---

## D12 · Validación: SERPAVI y portales (9:25–9:55)

- **Mensaje:** el alquiler oficial 2024 no está infrainflado: las declaraciones fiscales de
  alquiler (SERPAVI) y Eustat coinciden municipio a municipio.
- **En pantalla:**
  - **ratio 0,976** SERPAVI/Eustat (mediana) · **Spearman 0,979**
  - **99,4 %** de los 159 municipios con declaración dentro de ±25 %
  - Tabla: Bilbao 11,60 / 11,51 · Donostia 14,90 / 13,99 · Getxo 11,40 / 11,34 ·
    Vitoria 9,90 / 9,21 · Barakaldo 11,10 / 10,47 (€/m² y mes, 2024)
- **Evidencia:** `data/resultados/validacion_alquiler_2024_serpavi.csv`,
  `analysis/validar_alquiler_serpavi.py`.
- **Rúbrica:** C19, C17.
- **Nota oral:** «La pregunta incómoda es si el alquiler oficial está maquillado. Lo
  contrastamos con otra fuente independiente: las declaraciones de renta de alquiler de
  SERPAVI. La mediana de la ratio es 0,976 y el Spearman 0,979; el 99,4 % de los 159
  municipios cae dentro del ±25 %. Ojo con lo que prueba y lo que no: valida el alquiler
  registrado de 2024, no el precio de anuncio de 2026. Si el oficial estuviera infrainflado,
  la diferencia con 2026 sería todavía mayor: el sesgo iría en contra nuestra, no a favor.»
- **Transición:** «Y dentro de esa capa, no todos los pisos pesan igual.»

---

## D13 · Esfuerzo por tipología (9:55–10:25)

- **Mensaje:** el esfuerzo de mercado 2026 no es homogéneo: las viviendas de 4+ habitaciones
  suben a 120 %, frente a 80 % en las de 1-2.
- **En pantalla:**
  - **1-2 hab:** 78,6 % (n=123 anuncios; IC95 % 72,7–87,3)
  - **3 hab:** 82,0 % (n=94; IC95 % 78,5–87,3)
  - **4+ hab:** 116,4 % (n=60; IC95 % 110,5–128,0)
  - Mediana a nivel de anuncio, pct 18-34. El CSV municipal conserva el ponderado
    (80,4 / 85,2 / 120,1): los dos estimadores se publican
- **Gráfica:** `M26_esfuerzo_por_tipo.png`.
- **Evidencia:** `data/procesado/esfuerzo_mercado_2026_por_tipo.csv`,
  `transform/calcular_esfuerzo_mercado_2026_por_tipo.py`.
- **Rúbrica:** C8.
- **Nota oral:** «Desglosamos el esfuerzo por tamaño de vivienda, siempre con los anuncios ya
  filtrados. La vivienda de 1-2 habitaciones pide un 78,6 % del salario joven; la de 3, un
  82,0 %; y la de 4 o más, un 116,4 %. Son medianas de anuncios, no medias de medianas
  municipales: si se ponderara por municipio saldría 80,4 / 85,2 / 120,1, y publicamos las
  dos para que se vea el efecto del estimador. Con 60 anuncios en el tramo alto, es un
  patrón, no una mediana municipal.»
- **Transición:** «¿Y cómo se compara cada municipio con su propio punto de partida en 2024?»

---

## D14 · Diferencia de nivel 2024 vs 2026 (10:25–11:00)

- **Mensaje:** la diferencia es de NIVEL, no temporal: cambia el numerador (anuncio vs
  registrado) y el denominador. Cuando se igualan ambos, el salto real es mucho menor.
- **En pantalla:**
  - Misma muestra y mismo denominador: **44,6 %** (2024 oficial) → **78,6 %** (2026 oferta)
  - Con denominador canónico (renta joven 2024): **57,8 %** → el resto es denominador, no precio
  - Precio de oferta **2,0×** el alquiler registrado 2024 en el mismo municipio (**1,44×** en €/m²)
  - Extremos: **+122,6 pp con n=1** (Ibarrangelu, Mendata); bajan **Barakaldo (−15,2)**, **Basauri (−12,8)**, **Eibar (−1,7)**, los tres con n≤2
- **Gráfica:** `M26_brecha_2024_2026.png` (15 mayores diferencias; **gris = n<5**, no concluyente).
- **Evidencia:** `data/procesado/brecha_esfuerzo_2024_2026.csv`,
  `analysis/calcular_brecha_esfuerzo_2024_2026.py`,
  `analysis/comparar_esfuerzo_2024_2026_misma_base.py`,
  `analysis/calibrar_premium_oferta.py`.
- **Rúbrica:** C8.
- **Nota oral:** «Aquí está el punto delicado y lo decimos antes de que lo pregunten: esta
  diferencia no es una serie temporal. A la izquierda, alquiler registrado de Eustat; a la
  derecha, precio de oferta de un anuncio. Si igualamos muestra y denominador, el esfuerzo pasa
  del 44,6 % al 78,6 %. Si además usamos el denominador canónico —la renta joven—, el anuncio
  da 57,8 %. Es decir: buena parte del salto es cambio de metro, no subida de precio. Lo que sí
  podemos afirmar es el nivel: el precio de oferta duplica el alquiler registrado en el mismo
  municipio. Y los extremos son de un anuncio: no los leemos como tendencia; en el gráfico
  van en gris y solo Donostia sale en color, que es la única con muestra.»
- **Transición:** «Y para cerrar el detalle, el mapa de todo esto en 2026.»

---

## D15 · Dos mapas 2026 (11:00–11:25)

- **Mensaje:** el esfuerzo de mercado 2026 tiene geografía, y la cobertura también. El gris es
  ausencia de anuncio, nunca cero.
- **En pantalla:** dos mapas —esfuerzo (trama = n<5) y cobertura (n de anuncios)—; 50 municipios
  = 71,2 % de la población 18-34.
- **Gráfica:** `M26_mapa_coropletico_2026.png` y `M26_mapa_cobertura.png`.
- **Evidencia:** `data/procesado/esfuerzo_mercado_2026.csv`,
  `visuals/mapa_esfuerzo_mercado_2026.py`.
- **Rúbrica:** C8.
- **Nota oral:** «El mapa cierra la capa de enriquecimiento. Cada municipio con anuncio va
  coloreado por su esfuerzo de mercado 2026; el gris es municipio sin anuncio, que no es lo
  mismo que cero. Las capitales y el corredor del Nervión vuelven a la banda alta; el interior
  y el rural, por debajo. Es la misma geografía del esfuerzo canónico, leída sobre precio de
  oferta publicada en vez de alquiler efectivo.»
- **Transición:** «Con esto cerramos las dos historias. Ahora, cómo se construyó.»

---

# Acto 3 — Cómo se construyó

## D16 · Capas, gold y una orden (11:25–12:30)

- **Mensaje:** dos ramas sobre los mismos originales: una analítica (Mongo) y una de
  conservación (Kafka→HDFS); nunca Kafka→Mongo.
- **En pantalla (cinco cajas + rama de conservación):**
  `Fuentes → raw inmutable → silver → Mongo local → 11 pipelines → CSV/PNG`
  y en paralelo `raw → Kafka (manifiesto SHA) → HDFS` (solo raw).
- **Claves honestas:** 352 canónicos en HDFS · **procesados en local por indicación de la
  profesora** · centro no alcanzable hoy · Mongo local sin Docker.
- **Evidencia:** `storage/kafka_hdfs_uploader.py`, `scripts/hdfs_recuperacion_un_fichero.py`,
  `openspec/audit/v8_2026-11-09/evidencia/vivo/hdfs.json`.
- **Rúbrica:** C2, C3, C4, ENTREGABLES-01, ARQUITECTURA-01.
- **Nota oral:** «Hay dos caminos sobre los mismos ficheros. El analítico: original inmutable,
  silver, Mongo y pipelines. El de conservación: el manifiesto con SHA viaja por Kafka y un
  consumidor sube a HDFS lo que aún no está. Kafka no escribe en Mongo: la integración se
  hace por `codigo_ine`. Y una excepción firmada: los procesados no se suben a HDFS; solo los
  352 originales, con recuperación por SHA.»
- **Transición:** «¿Y dónde vive todo eso? En Mongo.»

### La orden

- **Mensaje:** una orden reconstruye todo, y la limpieza es explícita: nulos marcados,
  duplicados resueltos, tipos convertidos.
- **En pantalla:**
  - 13 familias de fuentes · **47 scripts** transform · **40 nodos** en el DAG
  - Limpieza PyMongo: `canonicalize_codigo_ine`, `mark_nulls`, `resolve_duplicates`,
    `convert_types` (+ `clean_obsolete_fields`)
  - **185/185** silver y **53/53** gold reconstruidos desde cero, byte a byte
  - `python scripts/run_pipeline.py --fase silver,quality,gold`
- **Gráfica:** ninguna (diagrama de fases + dos checks).
- **Evidencia:** `scripts/run_pipeline.py`, `storage/clean_mongo.py`, manifests.
- **Rúbrica:** C1, C7, C8, C15 (núcleo del 46,7 %).
- **Nota oral:** «La automatización no es un script: es un DAG con dependencias. Cada fichero
  de silver tiene un productor declarado o no existe. Los nulos se marcan, no se rellenan;
  los duplicados se resuelven por portal+id y por huella; los tipos se convierten, incluido
  el `codigo_ine` a cinco dígitos. Y se puede reconstruir de cero: lo hicimos, 185 ficheros
  y 53 artefactos idénticos.»
- **Transición:** «¿Por qué Mongo y no un CSV?»

---

## D17 · Modelo Mongo y contenido (12:30–13:30)

- **Mensaje:** lo que se lee junto se embebe; lo que crece sin límite se referencia por
  `codigo_ine`.
- **En pantalla:**
  - `municipios`: embebe `demografia`, `empleo`, `demanda_social` (se consultan juntos,
  cambian poco)
  - `anuncios`: `ubicacion{}`, `equipamiento[]`, `historico_precios[]` + referencia
  `ubicacion.codigo_ine → municipios._id`
  - 16 colecciones vivas + 14 `__backup`
- **Gráfica:** ninguna (esquema de 3 cajas).
- **Evidencia:** `openspec/archive/2026-11-10-docs/modelo_mongodb.md`.
- **Rúbrica:** C9, C6, T1.
- **Nota oral:** «La decisión es por patrón de acceso: el municipio se lee entero y cambia
  poco, así que va embebido. Los anuncios crecen cada día y se consultan por municipio, así
  que se referencian. No embebemos anuncios dentro del municipio: duplicaría datos y
  rompería el límite de 16 MB.»
- **Transición:** «Y con eso, consultas y agregaciones.»

---

## D18 · Aggregation, índices y CRUD (13:30–14:30)

- **Mensaje:** 11 pipelines con 8 etapas; un índice convierte 594 documentos examinados en 1.
- **En pantalla (dos mitades):**
  - Izquierda: **11 pipelines**, 8 etapas (`$match`, `$group`, `$lookup`, `$unwind`,
    `$project`, `$sort`, `$limit`, `$addFields`); 30 consultas; CRUD completo con asserts
  - Derecha: `COLLSCAN 594 → IXSCAN 1`, filtro `20069` + larga + ≤1000, índice ESR
    `{ubicacion.codigo_ine, modalidad, precio_eur}`
  - Atomicidad de documento (upsert + índice único); transacción multidocumento justificada
    como innecesaria en standalone
- **Gráfica:** captura del explain (o tabla de 2 filas: antes/después).
- **Evidencia:** `analysis/mongo_aggregations.py`, `analysis/mongo_indexes.py`,
  `analysis/mongo_queries.py`, `storage/clean_mongo.py`.
- **Rúbrica:** C10, C11, C12, C13, C14, T2-T5.
- **Nota oral:** «Los pipelines responden preguntas, no son ejercicios: esfuerzo, VPO,
  accesibilidad, habitaciones. El de la derecha es el mismo filtro con y sin índice: antes
  Mongo examina 594 documentos, después 1. El orden ESR importa: igualdad por municipio,
  orden por modalidad, rango por precio. Y no forzamos una transacción que el modelo no
  necesita: la atomicidad de un documento y el índice único ya garantizan la idempotencia.»
- **Transición:** «¿Cómo sabemos que no está roto?»

---

## D19 · Pruebas (14:30–15:30)

- **Mensaje:** no es una demo: es un sistema que se reconstruye y que falla cuando debe.
- **En pantalla:**
  - **287 tests** (2 skipped) · gobernanza **TODO OK** (47/40/185/15)
  - Gate offline: 355 raw SHA + 185 silver + 15 colecciones + lag 0
  - Rebuild: **183/183** silver y **53/53** gold byte-idénticos
  - **FAIL 07 conocido y visible**: paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26
- **Gráfica:** ninguna (4 checks en verde + 1 en ámbar).
- **Evidencia:** `pytest`, `verificar_gobernanza.py`, `gate_extremo_a_extremo.py --offline`,
  `verificar_fase_datos.py`.
- **Rúbrica:** C8, C16, T6, P-08.
- **Nota oral:** «Tenemos 287 tests. El gate verifica los 355 SHA del raw y los 185 ficheros
  de silver. Reconstruimos la capa entera desde cero y sale idéntica. Y hay un check que
  falla a propósito: tres municipios con paro cero en el INE y tasa no nula en Lanbide.
  Preferimos enseñarlo en rojo antes que imputarlo para que salga verde.»
- **Transición:** «Y hasta aquí lo que sostenemos.»

---

# Acto 4 — Límites y cierre

## D20 · Límites (15:30–16:45)

- **Mensaje:** sabemos qué afirmamos, qué no y qué nos tumbaría.
- **En pantalla (dos columnas):**
  - **Sostenemos:** 4 robustos con n≥30 y su intervalo; 40/159 > 30 %; Bilbao/Donostia ~38 %;
    el 78,6 % como nivel de la capa 2026, no como mapa
  - **No sostenemos:** ranking fino fuera de Tier A; emancipación municipal (solo CAE); precio
    donde no hay anuncio; serie temporal 2024→2026 (son capas distintas)
  - **Nos tumbaría:** fuente independiente con n≥30 que mueva >10 % el precio de Bilbao,
    Donostia, Getxo o Vitoria; un piso de los 45 en cuarentena que sí esté en Euskadi
  - **Excepción declarada:** HDFS solo raw (352); procesados en local por indicación de la profesora
- **Gráfica:** ninguna.
- **Evidencia:** `openspec/audit/v10_2026-11-11/auditoria_rubrica_v10.md`.
- **Rúbrica:** C18, C19, P-05.
- **Nota oral:** «Nos tumbaría una fuente independiente que, con n≥30 y la misma ventana,
  moviera más de un 10 % el precio de Bilbao, Donostia, Getxo o Vitoria. Nos tumbaría encontrar
  un piso de los 45 en cuarentena que sí estuviera en Euskadi; la cuarentena es reversible.
  Y no defendemos emancipación municipal: solo tenemos CAE. Con más datos, lo primero sería
  subir la muestra de los 57 Tier C y separar temporal de larga en todo.»
- **Transición:** «Una frase y abrimos preguntas.»

---

## D21 · Cierre (16:45–17:00)

- **Mensaje:** cerrar con la misma frase del principio, sin añadir nada nuevo.
- **En pantalla:** «En la mayoría del territorio, justo; en las capitales, no; y en 188
  municipios no lo sabemos.» + «Gracias. Abrimos el código, los datos y el CSV de cada cifra.»
- **Gráfica:** ninguna.
- **Evidencia:** repositorio completo (355 raw · 185 silver · 53 gold · 287 tests).
- **Rúbrica:** C18, C19.
- **Nota oral:** «Y hasta aquí. En la mayoría del territorio, justo; en las capitales, no; y en
  188 municipios no lo sabemos. Gracias; abrimos el código y los datos.»

---

# Backup (solo si preguntan)

| # | Tema | Qué enseñar |
|---|---|---|
| B1 | Modelado Tema 8 | Las 7 preguntas con respuesta y la decisión embedding/referencing |
| B2 | Transacciones / sharding | Atómica de documento, por qué no replica set, shard key `codigo_ine` |
| B3 | CRUD y consultas | `demo_crud_operations` + 30 consultas (dot notation, `$elemMatch`, `$and`) |
| B4 | Hashes y conteos | 355/185/53 · 594/252 · 4/3/57/188 · 15 colecciones · 287/50 |
| B5 | HDFS/Kafka | Evidencia v8, 352 canónicos, topic `vivienda_euskadi`, lag 0, por qué no se revalida hoy |
| B6 | Habitaciones | `H6_habitaciones_mediana_rango.png`; solo Bilbao 96 y Donostia 66 firmes |
| B7 | Oficial vs anuncios | `P_oficial_vs_anuncios_por_TH.png`; divergencia por territorio |
| B8 | VPO | `C_vpo_por_estado.png`; 406 promociones, 251/252 con flujo terminadas |
| B9 | Modalidades | `H8b_modalidad_mediana_eur_m2.png`; mismo alquiler mensual, distinto €/m² |

---

# Mapa de rúbrica → diapositiva

| Criterio | Diapositivas |
|---|---|
| C1 Extracción API+scraping | 4, 9, 16 |
| C2 HDFS | 16, B5 |
| C3 Kafka | 16, B5 |
| C4 Integración | 16, 18 |
| C5 Fuentes + campo común | 4, 9 |
| C6 2+ colecciones + relación | 4, 17 |
| C7 Limpieza | 16, 18 |
| C8 Automatización | 14, 16, 18, 19 |
| C9 Modelado justificado | 17, B1 |
| C10 CRUD | 18, B3 |
| C11 Consultas | 18, B3 |
| C12 Aggregation | 18 |
| C13 Índices/explain | 18 |
| C14 Consistencia | 18, B2 |
| C15 Heterogéneos | 4, 9, B6, B7 |
| C16 Automatización análisis | 7, 11, 19 |
| C17 Indicadores | 2, 3, 7, 10, 12, B7 |
| C18 Respuesta | 2, 5, 6, 7, 8, 20 |
| C19 Visualización | 5, 6, 11, 12, 20 |
| T1–T7 | 17, 18, B1–B3 |

---

# Producción

## Gráficas: origen y destino

| Diapositiva | Figura | Fuente |
|---|---|---|
| 04 | `g4_distribucion_anuncios.png` | Mongo `indicadores` |
| 05 | `mapa_coroplastico_esfuerzo_18_34.png` | `mongo_esfuerzo_por_municipio.csv` |
| 06 | `hist_esfuerzo_18_34_umbral30.png` | idem |
| 07 | `O_ranking_bloqueado_n30.png` | idem + bootstrap |
| 10 | `M26_hist_esfuerzo_mercado.png` | `esfuerzo_mercado_2026.csv` |
| 11 | `M26_cobertura.png` | `cobertura_representatividad_2026.csv` |
| 13 | `M26_esfuerzo_por_tipo.png` | `esfuerzo_por_tipo_nivel_anuncio_2026.csv` |
| 14 | `M26_brecha_2024_2026.png` | `brecha_esfuerzo_2024_2026.csv` |
| 15 | `M26_mapa_coropletico_2026.png` + `M26_mapa_cobertura.png` | `esfuerzo_mercado_2026.csv` |
| B6 | `H6_habitaciones_mediana_rango.png` | `mongo_habitaciones_por_municipio.csv` |
| B7 | `P_oficial_vs_anuncios_por_TH.png` | `mongo_alquiler_por_municipio.csv` |
| B8 | `C_vpo_por_estado.png` | `mongo_vpo_por_municipio.csv` |
| B9 | `H8b_modalidad_mediana_eur_m2.png` | `mongo_modalidades.csv` |

Todas están en `data/resultados/` o en `assets/`. El bloque 2026 se regenera con
`python scripts/regenerar_capa_2026.py`; el resto con `analysis/run_analisis_mongo.py`.

## Reglas de puesta en escena

- **Una cifra por diapositiva** como titular; el resto, apoyo.
- **Nunca** decir «Docker», «759», «182 silver», «54/65/40» ni «62/252».
- Decir «no lo sabemos» siempre que aparezca gris.
- Si falla la red: no hay demo en vivo; se enseña la captura del gate.
- Acentos, `ñ`, `€`, `‰` y `≥` revisados en HTML y PDF.

## Recorte a 12 minutos

1. Fusionar 17 y 18 en una sola diapositiva técnica (modelo + explain).
2. Bajar 7 a 40 s (solo bootstrap; `O_ranking` pasa a backup).
3. 4 y 9 a 50 s cada una.
4. 11 y 12 a 15 s cada una: el mensaje cabe en «cubre el 71,2 % de los jóvenes y el alquiler
   oficial se sostiene»; si sobran, se citan de palabra y no se enseñan.
