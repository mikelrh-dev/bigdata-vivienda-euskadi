# Guion — Presentación v3 (22 diapositivas + 8 backups)

**Duración objetivo:** 17:30 · **Recorte a 12:00** al final.
**Público:** tribunal SBD + BDA (perfil técnico, poco tiempo, mucha pregunta).
**Idioma:** castellano. **Formato:** 16:9 fijo, offline, sin dependencias.
**Regla de oro:** primero la respuesta, después cómo se calculó. Cada cifra lleva su
artefacto. Ninguna cifra de este guion se teclea a mano: sale de `data/resultados/*.csv`,
de `data/procesado/esfuerzo_mercado_2026.csv` o de Mongo.

> **Cifras congeladas (2026-11-13).** Si algo cambia, se regenera el CSV antes de tocar
> la diapositiva. Cifras vigentes: **355 entradas de manifiesto SHA** · **352 canónicos +
> 3 legado** · **353 objetos en HDFS** (352 + 1 manifiesto) · **183 silver** · **55 gold**
> (24 CSV + 31 PNG) · **17 colecciones vivas + 15 backup = 32** · **25 índices** ·
> **295 tests** (293 pasan, 2 skipped) · **287 anuncios válidos en 50 municipios** ·
> **78,6 % municipal** · **87,3 % de anuncio** · **1.350 € mediana de medianas
> municipales** · **1.500 € mediana de anuncios** · **1.719 € salario joven ajustado**.

> **Dos unidades, siempre declaradas.** El **78,6 %** es la mediana de las 50 medianas
> municipales. El **87,3 %** es la mediana de los 287 anuncios individuales. El **84,4 %**
> es la mediana de anuncios **sin RealtyAPI** (212 anuncios), no la global. No se mezclan.

---

## Estructura y tiempos

| # | Diapositiva | Inicio | Fin | Acto |
|---|---|---|---:|---|
| 1 | La pregunta | 0:00 | 0:30 | Apertura |
| 2 | La respuesta en dos capas | 0:30 | 1:50 | Apertura |
| 3 | Cómo se mide | 1:50 | 2:40 | 2024, el ancla |
| 4 | De dónde sale el 2024 | 2:40 | 3:40 | 2024, el ancla |
| 5 | El mapa de 2024 | 3:40 | 4:30 | 2024, el ancla |
| 6 | El reparto de 2024 | 4:30 | 5:20 | 2024, el ancla |
| 7 | Qué aguanta el ancla | 5:20 | 6:20 | 2024, el ancla |
| 8 | De dónde sale el 2026 | 6:20 | 6:55 | 2026, la oferta |
| 9 | El resultado de 2026 | 6:55 | 7:40 | 2026, la oferta |
| 10 | Compartir: habitación vs piso | 7:40 | 8:20 | 2026, la oferta |
| 11 | Los cuatro municipios robustos | 8:20 | 9:20 | 2026, la oferta |
| 12 | Esfuerzo por tipología | 9:20 | 9:40 | 2026, la oferta |
| 13 | Diferencia de nivel 2024 vs 2026 | 9:40 | 10:10 | 2026, la oferta |
| 14 | Arquitectura: ingesta, Kafka, HDFS y medallion | 10:10 | 11:10 | Cómo se construyó |
| 15 | Mongo I: modelado documental | 11:10 | 12:05 | Cómo se construyó |
| 16 | Mongo II: CRUD y consultas | 12:05 | 12:55 | Cómo se construyó |
| 17 | Mongo III: aggregation e índices | 12:55 | 13:45 | Cómo se construyó |
| 18 | Consistencia e idempotencia | 13:45 | 14:30 | Cómo se construyó |
| 19 | Calidad y quality gate | 14:30 | 15:20 | Cómo se construyó |
| 20 | Síntesis: qué dicen juntas las dos capas | 15:20 | 16:10 | Límites y cierre |
| 21 | Lo que sostenemos y lo que no | 16:10 | 17:15 | Límites y cierre |
| 22 | Cierre | 17:15 | 17:30 | Límites y cierre |

La charla son dos historias separadas —primero 2024 oficial, después 2026 de oferta— y
solo al final se explica cómo se construyó. La 11 es el puente: la única tabla donde las
dos capas se tocan, y va **después** del embudo para que el precio no aparezca sin muestra.
Límites y cierre van al final, no en medio.

---

# Acto 0 — Apertura

## D1 · La pregunta (0:00–0:30)

- **Mensaje:** el reto no es Mongo, es una pregunta con consecuencias.
- **En pantalla:** solo la pregunta, grande. «¿Puede una persona joven independizarse en
  Euskadi con su salario?» Pie: «Registro oficial 2024 + oferta publicada 2026 · 252 municipios».
- **Gráfica:** ninguna.
- **Evidencia:** —
- **Rúbrica:** apertura de C18.
- **Nota oral:** «Nos pidieron demostrar con datos reales en qué municipios de Euskadi una
  persona joven puede emanciparse. No empezamos por la base de datos: empezamos por la
  respuesta, y luego enseñamos cómo la hemos calculado para que puedan desmontarla.»
- **Transición:** «La respuesta cabe en ochenta segundos, pero tiene dos capas.»

## D2 · La respuesta en dos capas (0:30–1:50)

- **Mensaje:** en la mayoría del territorio se va justo; en las capitales, no; y el mercado
  de entrada de 2026 es otra barrera, no una evolución de la anterior.
- **En pantalla (dos bloques, cuatro cifras cada uno):**
  - **Capa oficial 2024 · Eustat/INE:** 26,61 % mediana (159 municipios) · 40/159 superan
    el 30 % · Bilbao 37,69 % · Donostia 38,17 %.
  - **Capa de oferta 2026 · portales:** 78,6 % mediana municipal (50 municipios) · 87,3 %
    mediana de los 287 anuncios · 1.500 € alquiler mediano publicado · 1.719 € salario
    joven ajustado.
- **Nota narrativa:** «No son una serie temporal: son dos fotografías distintas. Primero
  auditamos el ancla oficial de 2024; después, el pulso real de la oferta en 2026.»
- **Evidencia:** `mongo_esfuerzo_por_municipio.csv`, `esfuerzo_mercado_2026.csv`.
- **Rúbrica:** C18, C17.
- **Nota oral:** «El indicador es el estándar de emancipación: el alquiler anual dividido
  por la renta joven estimada. La mediana oficial de 2024 se lleva el 26,6 % y 40 de los
  159 municipios con dato pasan del 30 %. En Bilbao y Donostia se roza el 38 %. En 2026
  cambiamos de fuente: no es alquiler efectivo, es precio de anuncio. La mediana municipal
  da 78,6 %, pero la mediana de los 287 anuncios es 87,3 %. Esa diferencia no es un error:
  es la diferencia entre medir municipios y medir anuncios. Y no la voy a esconder.»
- **Transición:** «¿Cómo se mide eso?»

---

# Acto 1 — 2024, el ancla oficial

## D3 · Cómo se mide (1:50–2:40)

- **Mensaje:** el indicador no es nuestro; lo que aportamos es hacerlo municipal y decir
  dónde no se puede calcular.
- **En pantalla (fórmula grande):**
  `esfuerzo = (alquiler mensual × 12) / renta joven estimada 18-34 × 100`
  - mediana, no media (los alquileres tienen outliers)
  - umbral 30 % (literatura de emancipación; 35-40 % es exclusión efectiva)
  - **18-34 es el canónico**; 16-29 queda **legacy** (42,9 % de mediana, no comparable)
- **Gráfica:** ninguna.
- **Evidencia:** `analysis/mongo_aggregations.py` → `pipeline_indicadores_municipio`.
- **Rúbrica:** C17, JOVEN-18-34.
- **Nota oral:** «La renta joven no existe publicada por municipio y edad. La estimamos con
  las bandas de Eustat 18-19, 20-24, 25-29 y 30-34, ponderando por anchura, y la aplicamos
  a la renta municipal. Es un proxy, y lo decimos: no es un salario. El 16-29 antiguo da
  42,9 % de mediana y no es comparable; está en la base como legacy y no sostiene ninguna
  conclusión.»
- **Transición:** «¿De dónde sale ese alquiler oficial?»

## D4 · De dónde sale el 2024 (2:40–3:40)

- **Mensaje:** el ancla de 2024 es oficial y municipal, pero no cubre todo: 159 municipios
  con alquiler Eustat y 93 imputados por IDW que solo usamos para sensibilidad.
- **En pantalla:**
  - **159** con alquiler oficial Eustat · **93** imputados IDW (solo sensibilidad)
  - **13** familias de fuentes · **355** entradas de manifiesto SHA (**352 canónicos + 3 legado**)
  - **353** objetos en HDFS (**352 canónicos + 1 manifiesto**)
  - Eustat alquiler · INE renta joven · Lanbide/Udalmap paro · Etxebide 5.040 solicitudes y 406 promociones
- **Gráfica:** `H11_imputacion_oficial_idw_por_TH.png` (2024: oficial vs IDW por
  territorio; el IDW va separado y rayado).
- **Evidencia:** `config/fuentes.yaml`, `docs/raw_manifest_sha256.txt`, `mongo_tier_confianza.csv`.
- **Rúbrica:** C1, C5, C6, C15.
- **Nota oral:** «Eustat nos da el alquiler municipal, el INE la renta joven, Lanbide y
  Udalmap el paro, y Etxebide la demanda. En total, 355 entradas de manifiesto y 352
  canónicos con SHA. El ancla tiene agujeros y los enseñamos: 159 municipios tienen
  alquiler oficial y 93 van imputados por IDW, que solo usamos para sensibilidad. El
  gráfico separa las dos cosas: color para el dato oficial, trama para el IDW. No se
  mezclan en el indicador.»
- **Transición:** «Con eso, el mapa.»

## D5 · El mapa de 2024 (3:40–4:30)

- **Mensaje:** el esfuerzo tiene geografía: capitales y costa arriba; interior y sur, abajo.
- **En pantalla:** coroplético municipal, 159 oficiales (color) + 93 IDW (trama) con
  leyenda propia; escala 20,3–30 % y el color saturado por encima de 30 %.
- **Gráfica:** `mapa_coroplastico_esfuerzo_18_34.png` (esfuerzo 2024).
- **Evidencia:** figura generada desde `mongo_esfuerzo_por_municipio.csv`.
- **Rúbrica:** C19, C18.
- **Nota oral:** «Cada municipio con alquiler oficial, coloreado por esfuerzo; la trama es
  el IDW comarcal, que no es dato y por eso va rayado y aparte en la leyenda. No hace falta
  leer nombres: Bilbao, Donostia y el corredor del Nervión están en la banda alta; el
  interior de Álava y amplias zonas rurales, por debajo del 30 %. Y el rojo se corta a los
  30: los 40 que lo superan comparten el mismo tono, no son todos iguales.»
- **Transición:** «¿Cuántos quedan a cada lado del umbral?»

## D6 · El reparto de 2024 (4:30–5:20)

- **Mensaje:** no es un problema de cuatro municipios: 40 de 159 pasan del 30 %, y 14 se
  van por encima del 35 %.
- **En pantalla (cifras grandes):**
  - **119** por debajo del 30 % · **26** entre 30 % y 35 % · **14** por encima del 35 %
  - **40/159** por encima del 30 % (25,2 %)
  - Con IDW: mediana 25,37 % y **47/252** por encima del 30 %
- **Gráfica:** `hist_esfuerzo_18_34_umbral30.png` (esfuerzo 2024).
- **Evidencia:** `mongo_esfuerzo_por_municipio.csv`, `sensibilidad_idw.csv`.
- **Rúbrica:** C16, C19.
- **Nota oral:** «Tres cuartas partes del territorio con dato están por debajo del 30 %,
  pero una de cada cuatro lo supera, y hay 14 municipios por encima del 35 %. Con el IDW
  la mediana baja a 25,37 % y los que superan el 30 % son 47 de 252: el titular aguanta,
  la lista cambia.»
- **Transición:** «¿Y cuánto de esto es incertidumbre?»

## D7 · Qué aguanta el ancla (5:20–6:20)

- **Mensaje:** el alquiler oficial aguanta el contraste con SERPAVI; los intervalos de los
  cuatro robustos se solapan, así que defendemos el umbral, no un podio.
- **En pantalla (dos columnas):**
  - **Izquierda (SERPAVI 2024):** ratio **0,976** · Spearman **0,979** · **99,4 %** de los
    159 municipios dentro de ±25 %. Mini-tabla €/m²·mes: Bilbao 11,60/11,51 · Donostia
    14,90/13,99 · Getxo 11,40/11,34.
  - **Derecha (bootstrap):** Bilbao 33,75–40,95 · Getxo 27,54–31,77 · Donostia 32,4–45,8.
    Se solapan: no hay orden firme entre ellos. **Qué mide:** el nivel es Eustat 2024 y el
    ancho es dispersión de precios de anuncio 2026; **no** es el error del estimador Eustat.
- **Gráfica:** `O_ranking_bloqueado_n30.png` (esfuerzo 2024; la muestra n≥30 sí es 2026).
- **Evidencia:** `validacion_alquiler_2024_serpavi.csv`, `bootstrap_robustos.csv`.
- **Rúbrica:** C8, C19, C18.
- **Nota oral:** «La pregunta incómoda es si el alquiler oficial está maquillado. Lo
  contrastamos con otra fuente independiente: las declaraciones de renta de alquiler de
  SERPAVI. La mediana de la ratio es 0,976 y el Spearman 0,979; el 99,4 % de los 159
  municipios cae dentro del ±25 %. Ojo con lo que prueba: valida el alquiler registrado de
  2024, no el precio de anuncio de 2026. Y con bootstrap, los intervalos de Bilbao, Getxo
  y Donostia se solapan: no hay orden firme. El ancho mide dispersión de precios de 2026
  sobre el nivel de 2024, no el error de Eustat, que es un registro, no una encuesta.»
- **Transición:** «Y con eso, ¿qué municipios aguantan una comparación firme?»

---

# Acto 2 — 2026, la capa de oferta

## D8 · De dónde sale el 2026 (6:20–6:55)- **Mensaje:** la capa 2026 no es un número mágico: son 287 anuncios de tres portales.
  Y lo que no entra no es descarte: es **otro producto**.
- **En pantalla:**
  - **845** crudos → **594** vigentes (dedup entre portales y 45 en cuarentena fuera de Euskadi)
    → **326** vivienda completa (**297** con precio; **29** sin precio) + **268** temporales (**264** con precio)
    → **287** válidos
  - Composición de los **795** productos de oferta 2026 (594 + 201): **41 %** piso larga
    (**326**) · **34 %** piso temporal (**268**) · **25 %** habitación (**201**). Los 287
    válidos son el **36 %** del total.
  - **201 habitaciones** en **9 municipios**, colección aparte; no entran en el 594.
  - 10 excluidos por el propio pipeline (900 m², 9.500 €) · 2 municipios
    caen a 0 anuncios (Amorebieta-Etxano, Laguardia): el mapa pasa de 52 a 50
  - Por portal (mediana): Fotocasa 152 · 1.432 € · 15,36 €/m² | Pisos 60 · 1.500 € · 16,67 |
    RealtyAPI 75 · 1.690 € · 19,43
- **Gráfica:** ninguna; tabla de portales.
- **Evidencia:** `data/resultados/validacion_portales_2026.csv`, `transform/_anuncios_2026.py`.
- **Rúbrica:** C1, C5, C15.- **Nota oral:** «El 2026 sale de tres portales: Fotocasa, Pisos y RealtyAPI. De 845
  anuncios crudos quedan 594 vigentes después de quitar duplicados y 45 en cuarentena
  fuera de Euskadi; 326 son vivienda completa, 297 con precio y 29 sin precio. De los 297
  descartamos 10 que el propio pipeline había marcado como imposibles —pisos de 900  metros, alquileres de 9.500 euros—. Quedan 287. Y aquí ya se ve un problema: RealtyAPI
  es un 26 % más caro por metro cuadrado que Fotocasa. No son tres cámaras iguales, y por
  eso lo medimos antes de mezclarlo.»
- **Nota oral (composición):** «Y ojo con lo que no entra: de los 594 vigentes, 268 son
  temporales, y aparte hay 201 habitaciones. No es que hayamos perdido dos tercios de los
  anuncios: es que dos tercios de lo capturado son otro producto. Lo que no podemos es
  usar el temporal como sustituto de la vivienda de larga estancia.»
- **Transición:** «Con esa muestra, el resultado.»

## D9 · El resultado de 2026 (6:55–7:40)

- **Mensaje:** la mediana municipal es 78,6 %, pero la mediana de los 287 anuncios es
  87,3 %; el 98,3 % de los anuncios supera el 30 % del salario joven.
- **En pantalla:**
  - **78,6 %** mediana de las 50 medianas municipales
  - **87,3 %** mediana de los **287 anuncios** individuales
  - **1.500 €** precio mediano del anuncio · **1.719 €** salario joven 18-34 ajustado 2026
  - **98,3 %** de los 287 anuncios supera el 30 %
  - Caja warn: 43 de los 50 municipios tienen n<5; solo 4 tienen n≥30. El 78,6 % se
    defiende como nivel agregado, **no como mapa municipal**. Los 50/252 cubren el 71,2 %
    de los jóvenes y el 70,4 % de los anuncios está en cuatro.
- **Gráfica:** `M26_hist_esfuerzo_mercado.png` (esfuerzo 2026).
- **Evidencia:** `data/procesado/esfuerzo_mercado_2026.csv`, `validacion_portales_2026.csv`.
- **Rúbrica:** C17, C19.
- **Nota oral:** «Esta es la capa de oferta. Limpiamos los diez anuncios que nuestro propio
  pipeline ya había marcado como inválidos y quedan 287 anuncios en 50 municipios. El
  98,3 % supera el 30 % del salario neto joven. La mediana municipal da 78,6 %, pero no la
  vendo como un dato sólido: 43 de los 50 municipios tienen menos de cinco anuncios y no
  admiten mediana. La mediana de los 287 anuncios individuales es 87,3 %, y esa es la
  cifra que mejor describe el mercado publicado. Los 50 municipios cubren el 71,2 % de la
  población joven, así que la cobertura es defendible aunque el mapa tenga huecos.»
- **Transición:** «Antes de seguir: ¿a quién representa esta capa?»

## D10 · Compartir: habitación vs piso (7:40–8:20)

- **Mensaje:** compartir baja el esfuerzo a un tercio, pero no por debajo del umbral: es
  alivio, no solución.
- **En pantalla:**
  - **31,7 %** esfuerzo mediano de una habitación (545 € sobre 1.719 €)
  - **140 de 200** anuncios con precio utilizables: **60** pisos enteros colados (**30 %**)
    se descartan si superan el alquiler mediano del municipio
  - Bilbao **33,7 %** (580 €) frente al **98,2 %** del piso entero; Donostia **34,9 %**
    (600 €) frente al **116,4 %**
  - Caja warn: solo Bilbao pasa de 30 habitaciones; Getxo (5) y Vitoria (11) van
    indicativos; Barakaldo (10) no tiene piso comparable en 2026
- **Gráfica:** `H6b_esfuerzo_habitacion_vs_piso.png` (dos barras por municipio, mismo salario).
- **Evidencia:** `mongo_habitaciones_por_municipio.csv`, `esfuerzo_mercado_2026.csv`.
- **Rúbrica:** C15, C19.
- **Nota oral:** «La sección de compartir no trae solo habitaciones: 60 de los 200 anuncios
  con precio eran pisos enteros, y los quitamos con una regla explícita, no a ojo. Con los
  140 que quedan, la habitación mediana son 545 euros, el 31,7 % del salario joven. En
  Bilbao, 580 euros frente a los 850 del piso entero: el esfuerzo pasa del 98 % al 33,7 %.
  Sigue por encima del 30 %, así que compartir alivia el problema, no lo resuelve. Y la
  muestra manda: solo Bilbao pasa de 30 habitaciones; Getxo y Vitoria son indicativos.»
- **Transición:** «Si compartir no resuelve, ¿qué municipios aguantan la comparación?»

## D11 · Los cuatro municipios robustos (8:05–9:05)

- **Mensaje:** cuatro municipios sostienen la comparación; el orden 3º/4º es frágil y lo decimos.
- **En pantalla (tabla, cada columna fechada):**

| Municipio | n comparable | Esfuerzo 2024 | Precio 2026 | Esfuerzo 2026 | Paro 2024 |
|---|---:|---:|---:|---:|---:|
| Bilbao | 68 | 37,69 % | 1.687,50 € | 98,19 % | 9,71 % |
| Donostia / San Sebastián | 58 | 38,17 % | 2.000,00 € | 116,37 % | 5,82 % |
| Getxo | 39 | 28,60 % | 1.350,00 € | 78,55 % | 6,40 % |
| Vitoria-Gasteiz | 37 | 33,37 % | 1.300,00 € | 75,64 % | 8,89 % |

  - Getxo vs Vitoria: **2 anuncios comparables** de diferencia (39 frente a 37; el Tier A
    suma 50 frente a 39) → sin ranking firme 3º/4º
  - **Barakaldo: n=2** → cualquier mediana municipal es ruido, no ranking
  - **Vintages distintos:** esfuerzo 2024 = alquiler oficial; precio y esfuerzo 2026 =
    anuncio; paro = Udalmap 2024 general 16-64
- **Gráfica:** `O_ranking_bloqueado_n30.png` (esfuerzo 2024 con muestra 2026; IC y resto en gris).
- **Evidencia:** `esfuerzo_mercado_2026.csv`, `comparativa_3_municipios_mongo.csv`,
  `pipeline_indicadores_municipio`.
- **Rúbrica:** C18 (núcleo), C17.
- **Nota oral:** «Bilbao y Donostia están en el 38 % con la muestra más grande. Getxo está
  por debajo del 30 % pero por 1,4 puntos, y solo tiene 11 anuncios más que Vitoria: no
  convertimos eso en un podio. Barakaldo, con dos anuncios, no se lee como ranking. Lo que
  sí decimos: en Bilbao la tensión es precio más paro; en Donostia es precio puro, con el
  paro más bajo, y el esfuerzo de anuncio se va al 116 % del salario. Y ojo: cada columna
  viene de una capa distinta. Esta es la única tabla donde las dos capas se tocan.»
- **Transición:** «¿Y dentro de esa capa, todos los pisos pesan igual?»

## D12 · Esfuerzo por tipología (9:05–9:35)

- **Mensaje:** el esfuerzo de mercado 2026 no es homogéneo: las viviendas de 4+ habitaciones
  suben a 116 %, frente a 78,6 % en las de 1-2.
- **En pantalla:**
  - **1-2 hab:** 78,6 % (n=123; IC95 % 72,7–87,3)
  - **3 hab:** 82,0 % (n=94; IC95 % 78,5–87,3)
  - **4+ hab:** 116,4 % (n=60; IC95 % 110,5–128,0)
  - Mediana a nivel de anuncio. El CSV municipal conserva el ponderado (80,4 / 85,2 /
    120,1): los dos estimadores se publican.
- **Gráfica:** `M26_esfuerzo_por_tipo.png` (anuncios 2026).
- **Evidencia:** `esfuerzo_por_tipo_nivel_anuncio_2026.csv`.
- **Rúbrica:** C8, C17.
- **Nota oral:** «Desglosamos el esfuerzo por tamaño de vivienda, siempre con los anuncios
  ya filtrados. La vivienda de 1-2 habitaciones pide un 78,6 % del salario joven; la de 3,
  un 82,0 %; y la de 4 o más, un 116,4 %. Son medianas de anuncios, no medias de medianas
  municipales: si se ponderara por municipio saldría 80,4 / 85,2 / 120,1, y publicamos las
  dos para que se vea el efecto del estimador. Con 60 anuncios en el tramo alto, es un
  patrón, no una mediana municipal.»
- **Transición:** «¿Y cómo se compara cada municipio con su propio punto de partida?»

## D13 · Diferencia de nivel 2024 vs 2026 (9:35–10:10)

- **Mensaje:** la diferencia es de NIVEL, no temporal: cambia el numerador (anuncio vs
  registrado) y el denominador. Cuando se igualan ambos, el salto real es menor.
- **En pantalla:**
  - Misma muestra y mismo denominador: **44,6 %** (2024 base salario) → **78,6 %** (2026)
  - Con denominador canónico (renta joven 2024): **57,8 %** → el resto es denominador, no precio
  - El precio de oferta multiplica por **1,88×** el alquiler registrado 2024 en el mismo
    municipio (**1,41×** en €/m²)
  - Extremos: **+122,6 pp con n=1**; bajan **Barakaldo (−15,2)**, **Basauri (−12,8)**,
    **Eibar (−1,7)**, los tres con n≤2; en el gráfico van en gris. Solo Donostia en color (n=58).
- **Gráfica:** `M26_brecha_2024_2026.png` (2024 → 2026: 15 mayores diferencias; gris = n<5, no concluyente).
- **Evidencia:** `brecha_esfuerzo_2024_2026.csv`, `comparacion_esfuerzo_2024_2026_resumen.csv`,
  `calibrar_premium_oferta.py`.
- **Rúbrica:** C8, C17.
- **Nota oral:** «Aquí está el punto delicado y lo digo antes de que lo pregunten: esta
  diferencia no es una serie temporal. A la izquierda, alquiler registrado de Eustat; a la
  derecha, precio de oferta de un anuncio. Si igualamos muestra y denominador, el esfuerzo
  pasa del 44,6 % al 78,6 %. Si además usamos el denominador canónico —la renta joven—, el
  anuncio da 57,8 %. Es decir: buena parte del salto es cambio de metro, no subida de
  precio. Lo que sí podemos afirmar es el nivel: el precio de oferta multiplica por 1,88 el
  alquiler registrado en el mismo municipio, y por 1,41 en €/m². Los extremos son de un
  anuncio: no los leo como tendencia.»
- **Transición:** «Con esto cerramos las dos historias. Ahora, cómo se construyó.»

---

# Acto 3 — Cómo se construyó

## D14 · Arquitectura: ingesta, Kafka, HDFS y medallion (10:10–11:10)

- **Mensaje:** dos ramas sobre los mismos originales: una analítica (raw → silver → Mongo →
  gold) y una de conservación (raw → Kafka → HDFS); nunca Kafka → Mongo.
- **En pantalla (cinco cajas + rama inferior):**
  - `01 Fuentes`: 13 familias (API + scraping)
  - `02 Raw inmutable`: 355 entradas SHA + `.FROZEN` (352 canónicos + 3 legado)
  - `03 Silver`: 183 ficheros (42 CSV normalizados a `codigo_ine` de 5 dígitos)
  - `04 Mongo`: 17 colecciones vivas con PyMongo
  - `05 Gold`: 53 artefactos (24 CSV + 29 PNG)
  - Comando: `python scripts/run_pipeline.py --fase silver,quality,gold` · 40 nodos en el DAG
  - **Conservación:** productor lee manifiesto SHA → topic `vivienda_euskadi` → consumidor
    `hdfs_centro` → **353 objetos** (352 canónicos + 1 manifiesto)
  - **Estado real (2026-11-12):** el NameNode responde y el inventario da 353 objetos;
    `OPEN` falla por DNS del datanode; Kafka acepta TCP pero no entrega metadata. La última
    evidencia funcional es v8: 352/352, lag 0. No se afirma como revalidado hoy.
  - **Excepción declarada:** HDFS custodia solo la capa Raw; Silver y Gold se procesan en
    local por indicación expresa de la profesora.
- **Footer:** `scripts/run_pipeline.py · storage/kafka_hdfs_uploader.py` | `C1-C4 · C7`.
- **Rúbrica:** C1, C2, C3, C4, C7, ENTREGABLES-01, ARQUITECTURA-01.
- **Nota oral:** «Hay dos caminos sobre los mismos ficheros. El analítico: original
  inmutable, silver, Mongo y pipelines. El de conservación: el manifiesto con SHA viaja por
  Kafka y un consumidor sube a HDFS lo que aún no está. Kafka no escribe en Mongo: la
  integración se hace por `codigo_ine`. Y una excepción firmada: los procesados no se suben
  a HDFS; solo los 352 originales más el manifiesto. Hoy el clúster responde al inventario,
  pero la lectura de un fichero falla por DNS del datanode; no voy a decir que la he
  revalidado hoy. La evidencia funcional es la de v8: 352/352, lag 0.»
- **Transición:** «¿Por qué Mongo y no un CSV?»

## D15 · Mongo I: modelado documental (11:10–12:05)

- **Mensaje:** lo que se lee junto se embebe; lo que crece sin límite se referencia por la
  clave natural `codigo_ine`.
- **En pantalla (dos columnas):**
  - **Embedding en `municipios` (252):** `demografia{}`, `empleo{}`, `demanda_social{}`,
    `vivienda_contexto{}`, `transporte{}`. Se leen juntos, cambian poco.
  - **Referencing en `anuncios` (594):** colección propia, `ubicacion.codigo_ine` →
    `municipios._id`. Arrays acotados: `equipamiento[]` e `historico_precios[]`.
  - **Clave natural:** el `_id` de `municipios` **es** el código de 5 dígitos (`"48020"`),
    no un ObjectId. No hay un campo `codigo_ine` duplicado en `municipios`: el `_id` ya lo
    es. Así la relación se ve y no se duplica.
  - **Tipos BSON:** `Decimal128` para dinero, `int32` para conteos, `Date` ISO para fechas,
    `GeoJSON + 2dsphere` para consultas espaciales.
- **Esquema real (derecha):**
  ```json
  // Colección: municipios (252)
  {
    "_id": "48020",                 // codigo_ine
    "nombre_canonico": "Bilbao",
    "territorio": "Bizkaia",
    "demografia": {
      "poblacion_18_34_est": 73987,
      "renta_joven_estimada_18_34": 27063.9
    },
    "empleo": { "tasa_paro_lanbide_pct": 9.71 },
    "demanda_social": { "etxebide_solicitudes_por_mil_2024": 84.98 }
  }

  // Colección: anuncios (594) -> ubicacion.codigo_ine: "48020"
  ```
- **Footer:** `openspec/archive/2026-11-10-docs/modelo_mongodb.md · storage/mongo.py` | `C9 · C6 · T1`.
- **Rúbrica:** C9, C6, T1.
- **Nota oral:** «La decisión es por patrón de acceso: el municipio se lee entero y cambia
  poco, así que va embebido. Los anuncios crecen cada día y se consultan por municipio, así
  que se referencian. No embebemos anuncios dentro del municipio: duplicaría datos y
  rompería el límite de 16 MB. Y una precisión que importa: el `_id` del municipio no es un
  ObjectId, es el código INE de cinco dígitos; por eso `ubicacion.codigo_ine` apunta a
  `municipios._id` y la relación es una clave natural, no un puntero opaco.»
- **Transición:** «Y con eso, consultas y agregaciones.»

## D16 · Mongo II: CRUD y consultas (12:05–12:55)

- **Mensaje:** 30 consultas útiles y CRUD completo, con comprobación por código; nada se
  edita a mano en Mongo.
- **En pantalla (dos columnas):**
  - **CRUD:** `insert_one/many`, `find`, `update_one`, `find_one_and_update`, `upsert`,
    `$unset`, `$rename`, `$pull`, `bulk_write`, `delete_one/many`. Cada operación comprueba
    `inserted_id`, `matched_count`, `modified_count` o `deleted_count`.
  - **30 consultas:** dot notation, `$all`, `$elemMatch`, `$size`, `$exists`, `$type`,
    regex, comparación, `$and/$or`, proyección, `sort/limit`, paginación.
  - **Ejemplo real:** una consulta con campo anidado, array, dos condiciones, proyección y
    orden.
- **Código (derecha):**
  ```python
  db.anuncios.find(
      {
          "ubicacion.codigo_ine": "48020",
          "equipamiento": {"$all": ["ascensor", "terraza"]},
          "precio_eur": {"$lte": 1200},
      },
      {"_id": 0, "precio_eur": 1, "ubicacion.municipio": 1},
  ).sort({"precio_eur": 1}).limit(5)
  ```
- **Footer:** `analysis/mongo_queries.py · storage/clean_mongo.py` | `C10 · C11 · T2`.
- **Rúbrica:** C10, C11, T2.
- **Nota oral:** «Las consultas responden preguntas, no son ejercicios: esfuerzo,
  accesibilidad, VPO, habitaciones. Esta de la derecha tiene todo lo que pide la rúbrica:
  campo anidado, array con `$all`, dos condiciones, proyección, orden y límite. El CRUD se
  comprueba por código: no basta con lanzar el update, miramos `matched_count` y
  `modified_count`. Y la carga es staging, backup y rename atómico: nadie edita a mano en
  Mongo.»
- **Transición:** «¿Y cómo sabemos que el índice se usa?»

## D17 · Mongo III: aggregation e índices (12:55–13:45)

- **Mensaje:** 11 pipelines con 8 etapas; un índice convierte 594 documentos examinados en 1.
- **En pantalla (dos columnas):**
  - **Izquierda:** 11 pipelines; 8 etapas (`$match`, `$group`, `$lookup`, `$unwind`,
    `$project`, `$sort`, `$limit`, `$addFields`); `$lookup` cruza `anuncios` y
    `municipios` por `codigo_ine`; `$group` calcula medianas y conteos.
  - **Derecha (explain):**

| Filtro `20069` + larga + ≤1.000 € | Docs | Claves |
|---|---:|---:|
| Sin índice · COLLSCAN | 594 | 0 |
| Con ESR · IXSCAN | 1 | 1 |

  - Índice `{ubicacion.codigo_ine: 1, modalidad: 1, precio_eur: 1}`; orden ESR: igualdad,
    orden, rango. **25 índices** en total; 5 en `anuncios` (ESR, `2dsphere`, único
    `(portal, id_anuncio)`, multikey `equipamiento`).
- **Footer:** `analysis/mongo_aggregations.py · mongo_indexes.py` | `C12 · C13 · T3 · T4`.
- **Rúbrica:** C12, C13, T3, T4.
- **Nota oral:** «Los pipelines responden preguntas, no son ejercicios: esfuerzo, VPO,
  accesibilidad, habitaciones. El de la derecha es el mismo filtro con y sin índice: antes
  Mongo examina 594 documentos, después 1. El orden ESR importa: igualdad por municipio,
  orden por modalidad, rango por precio. Y no forzamos una transacción que el modelo no
  necesita: la atomicidad de un documento y el índice único ya garantizan la idempotencia.»
- **Transición:** «¿Cómo sabemos que no está roto?»

## D18 · Consistencia e idempotencia (13:45–14:30)

- **Mensaje:** consistencia sin sobreingeniería: atomicidad de documento, tres barreras de
  idempotencia y una shard key razonada, no implementada.
- **En pantalla (tres bloques):**
  1. **Atomicidad de documento:** en MongoDB standalone, cada escritura sobre un documento
     es atómica por diseño. No forzamos transacciones multidocumento (exigirían Replica
     Set) porque el modelo embebido evita actualizar varias colecciones en una operación
     crítica.
  2. **Idempotencia en 3 barreras:** (a) descarte en ingesta por hash SHA-256; (b) índice
     único compuesto `(portal, id_anuncio)`; (c) `update_one(..., upsert=True)` + carga
     atómica por `renameCollection`. Re-ejecutar el pipeline 10 veces produce exactamente
     los mismos 594 documentos.
  3. **Sharding futuro:** a escala actual (594 anuncios / 252 municipios) un nodo standalone
     sobra; si escalara a nivel estatal con histórico diario, la shard key óptima sería
     `{ubicacion.codigo_ine: 1, _id: 1}` (alta cardinalidad y aislamiento geográfico).
- **Footer:** `storage/mongo.py · tests/test_mongo_consistencia.py` | `C14 · T5`.
- **Rúbrica:** C14, T5.
- **Nota oral:** «No forzamos una transacción que el modelo no necesita. La atomicidad de
  un documento y el índice único ya nos dan la idempotencia. Tenemos tres barreras: el hash
  en la ingesta, el único por portal e id, y el upsert con rename atómico. Re-ejecutar el
  pipeline diez veces deja los mismos 594 documentos. Y si esto escalara a nivel estatal,
  la shard key sería el código INE más el `_id`, no el `_id` solo.»
- **Transición:** «¿Y cómo sabemos que el dato no miente?»

## D19 · Calidad y quality gate (14:30–15:20)

- **Mensaje:** no es una demo: es un sistema que se reconstruye y que falla cuando debe.
- **En pantalla (cuatro KPIs + caja warn):**
  - **287** tests (285 pasan, 2 skipped)
  - **355** SHA del raw verificados
  - **183/183** silver validados en esquema y tipos
  - **55/55** gold reproducibles byte a byte
  - **FAIL 07, visible:** Aramaio 0,28 · Gaintza 1,45 · Usansolo 3,26 — paro cero en el
    INE con tasa no nula en Lanbide. Preferimos enseñarlo en rojo antes que imputarlo para
    que salga verde.
- **Footer:** `pytest · verificar_gobernanza.py · gate_extremo_a_extremo.py --offline` | `C8 · C16 · P-08`.
- **Rúbrica:** C8, C16, P-08.
- **Nota oral:** «Tenemos 295 tests: 293 pasan y 2 se saltan. El gate verifica las 355
  entradas SHA del raw y los 183 ficheros de silver. Reconstruimos la capa entera desde
  cero y salen 55 artefactos idénticos. Y hay un check que falla a propósito: tres
  municipios con paro cero en el INE y tasa no nula en Lanbide. Preferimos enseñarlo en
  rojo antes que imputarlo para que salga verde.»
- **Transición:** «Y hasta aquí lo que sostenemos.»

---

# Acto 4 — Límites y cierre

## D20 · Síntesis: qué dicen juntas las dos capas (15:20–16:10)

- **Mensaje:** las dos capas no se restan; se leen juntas. Una dice dónde es estructural,
  la otra cuánto cuesta entrar hoy.
- **En pantalla (tabla de 4 filas):**

| Dimensión | Capa oficial 2024 | Capa de oferta 2026 | Lectura conjunta |
|---|---|---|---|
| Cobertura | 159 oficiales + 93 IDW | 50 municipios (71,2 % de jóvenes) | 188 Tier D sin anuncio: sin dato, no asequible |
| Alquiler mediano | 708 € en los 50 (p25–p75: 620–744) | 1.350 € mediana de medianas · 1.500 € mediana de anuncios | La oferta nueva multiplica por 1,88 |
| Esfuerzo 18-34 | 26,61 % (40/159 > 30 %) | 78,6 % municipal · 87,3 % anuncio | En capitales, 75–116 %: inviable en solitario |
| Uso analítico | Diagnóstico estructural | Barrera de acceso actual | No se restan como serie temporal |

- **Footer:** `comparacion_esfuerzo_2024_2026_resumen.csv` | `C17 · C18`.
- **Rúbrica:** C17, C18, C19.
- **Nota oral:** «Estas dos capas no se restan. Una dice dónde el esfuerzo es estructural;
  la otra, cuánto cuesta entrar hoy. En los mismos 50 municipios, el esfuerzo pasa del
  44,6 % al 78,6 % si igualamos el denominador; con el denominador canónico, el anuncio da
  57,8 %. Y el nivel de precio se multiplica por 1,88. Lo que no podemos decir es que haya
  subido un 34 %: son fuentes distintas.»
- **Transición:** «¿Qué sostenemos y qué nos tumbaría?»

## D21 · Lo que sostenemos y lo que no (16:10–17:15)

- **Mensaje:** sabemos qué afirmamos, qué no y qué nos tumbaría.
- **En pantalla (dos columnas):**
  - **Sostenemos:** 4 municipios con n≥30 y su esfuerzo; 40/159 > 30 %; Bilbao/Donostia
    ~38 % en 2024 y 98/116 % en 2026; el 87,3 % como nivel de la capa 2026, no como mapa.
  - **No sostenemos:** ranking fino fuera de Tier A; emancipación municipal (solo CAE);
    precio donde no hay anuncio; serie temporal 2024 → 2026 (son capas distintas).
- **Caja warn:** «Nos tumbaría: una fuente independiente con n≥30 que, en la misma ventana,
  mueva más de un 10 % el precio de Bilbao, Donostia, Getxo o Vitoria; o encontrar un piso
  de los 45 en cuarentena que sí esté en Euskadi.»
- **Nota:** excepción declarada: HDFS solo raw (352 canónicos + 1 manifiesto); procesados en
  local por indicación de la profesora. Con más datos, lo primero sería subir la muestra de
  los 57 Tier C y separar temporal de larga.
- **Footer:** `openspec/audit/v11_2026-11-12/auditoria_completa_v11.md` | `C18 · C19 · P-05`.
- **Rúbrica:** C18, C19, P-05.
- **Nota oral:** «Nos tumbaría una fuente independiente que, con n≥30 y la misma ventana,
  moviera más de un 10 % el precio de Bilbao, Donostia, Getxo o Vitoria. Nos tumbaría
  encontrar un piso de los 45 en cuarentena que sí estuviera en Euskadi; la cuarentena es
  reversible. Y no defendemos emancipación municipal: solo tenemos CAE. Con más datos, lo
  primero sería subir la muestra de los 57 Tier C y separar temporal de larga en todo.»
- **Transición:** «Una frase y abrimos preguntas.»

## D22 · Cierre (17:15–17:30)

- **Mensaje:** cerrar con la misma frase del principio, sin añadir nada nuevo.
- **En pantalla:** «En la mayoría del territorio, justo; en las capitales, no; en el mercado
  de entrada actual, prohibitivo; y en 188 municipios no lo sabemos.» + «Gracias. Abrimos el
  código, los datos y el CSV de cada cifra.»
- **Footer:** `Repositorio · 355 raw · 353 HDFS · 183 silver · 17 colecciones · 55 gold · 295 tests` | `C18 · C19`.
- **Rúbrica:** C18, C19.
- **Nota oral:** «Y hasta aquí. En la mayoría del territorio, justo; en las capitales, no;
  en el mercado de entrada actual, prohibitivo; y en 188 municipios no lo sabemos. Gracias;
  abrimos el código y los datos.»

---

# Backup (solo si preguntan)

| # | Tema | Qué enseñar |
|---|---|---|
| B1 | Modelado Tema 8 | Las 7 preguntas con respuesta y la decisión embedding/referencing |
| B2 | Conteos auditados | 355 manifiesto / 353 HDFS / 183 silver / 54 gold / 17+15 colecciones / 25 índices / 295 tests |
| B3 | HDFS y Kafka | Inventario 353 y estado real de hoy; evidencia v8; recuperación pendiente de DNS y `--out` |
| B4 | Habitaciones | `H6_habitaciones_mediana_rango.png`; 201 anuncios en 9 municipios (25 % de los 795 productos 2026), 140 utilizables tras descartar 60 pisos enteros (30 %); filtro precio < alquiler mediano de vivienda del municipio; ranking n≥10 (Donostia 600, Bilbao 580; Vitoria/Barakaldo indicativos); mediana global 545 €; 87 % ≤700 €; esfuerzo 31,7 % (Donostia 34,9 %, Bilbao 33,7 %); comparación 580 vs 850 € y 600 vs 995 € de piso entero |
| B5 | Modalidades | `H8b_modalidad_mediana_eur_m2.png`; misma mediana mensual (1.500 €), distinto €/m² (18,95 vs 16,67; 80 vs 90 m²); sobre los 594 vigentes (326 larga + 268 temporal) |
| B6 | VPO | `H5_vpo_terminadas_por_mil.png`; VPO terminada 2020-2024 (Udalmap 73, 2024), 251/252 municipios, stock no público; el registro de 406 promociones da estado, no fechas |
| B6b | VPO, serie | `S_serie_vpo_2004_2024.png`; Euskadi 11,5 ‰ en 2011 → 2,7 ‰ en 2024; ventana móvil de 5 años; Araba/Álava en panel propio con su escala (40,1 ‰ en 2011, 3,8 ‰ en 2024) |
| B7 | Oficial vs anuncios | `P_oficial_vs_anuncios_por_TH.png`; ratio 1,96 y Spearman 0,18: no comparable |
| B8 | Dos mapas 2026 | `M26_mapa_coropletico_2026.png` + `M26_mapa_cobertura.png`; gris = sin dato |

---

# Mapa de rúbrica → diapositiva

| Criterio | Diapositivas |
|---|---|
| C1 Extracción API + scraping | 4, 8, 14 |
| C2 HDFS | 14, B3 |
| C3 Kafka | 14, B3 |
| C4 Integración | 14, 17 |
| C5 Fuentes + campo común | 4, 8 |
| C6 2+ colecciones + relación | 4, 15 |
| C7 Limpieza | 14, 16 |
| C8 Automatización | 9, 10, 13, 19 |
| C9 Modelado justificado | 15, B1 |
| C10 CRUD | 16, B2 |
| C11 Consultas | 16, B2 |
| C12 Aggregation | 17 |
| C13 Índices/explain | 17 |
| C14 Consistencia | 18 |
| C15 Heterogéneos | 4, 8, B4, B5, B7 |
| C16 Automatización análisis | 7, 10, 19 |
| C17 Indicadores | 2, 3, 7, 9, 12, 20, B7 |
| C18 Respuesta | 2, 5, 6, 11, 20 |
| C19 Visualización | 5, 6, 10, 11, 13, 20, B8 |
| T1–T7 | 15, 16, 17, 18, 19, B1–B3 |

---

# Producción

## Gráficas: origen y destino

El vintage de cada figura lo declara `config/vintage_figuras.yaml` y el PNG lo
lleva impreso abajo a la derecha, además de en el pie de la diapositiva.

| Diapositiva | Figura | Vintage | Fuente |
|---|---|---|---|
| 04 | `H11_imputacion_oficial_idw_por_TH.png` | 2024 | `mongo_alquiler_por_municipio.csv` |
| 05 | `mapa_coroplastico_esfuerzo_18_34.png` | 2024 | `mongo_esfuerzo_por_municipio.csv` |
| 06 | `hist_esfuerzo_18_34_umbral30.png` | 2024 | idem |
| 07 | `O_ranking_bloqueado_n30.png` | 2024 (muestra 2026) | idem + bootstrap |
| 09 | `M26_hist_esfuerzo_mercado.png` + `M26_cobertura.png` | 2026 | `esfuerzo_mercado_2026.csv` · `cobertura_representatividad_2026.csv` |
| 10 | `H6b_esfuerzo_habitacion_vs_piso.png` | 2026 | `mongo_habitaciones_por_municipio.csv` + `esfuerzo_mercado_2026.csv` |
| 12 | `M26_esfuerzo_por_tipo.png` | 2026 | `esfuerzo_por_tipo_nivel_anuncio_2026.csv` |
| 13 | `M26_brecha_2024_2026.png` | 2024 → 2026 | `brecha_esfuerzo_2024_2026.csv` |
| B4 | `H6_habitaciones_mediana_rango.png` | 2026 | `mongo_habitaciones_por_municipio.csv` + precios de habitaciones + salario joven 2026 (Mongo) |
| B5 | `H8b_modalidad_mediana_eur_m2.png` | 2026 | `mongo_modalidades.csv` |
| B6 | `H5_vpo_terminadas_por_mil.png` | flujo 2020-2024 | `mongo_vpo_terminadas_por_municipio.csv` |
| B6b | `S_serie_vpo_2004_2024.png` | flujo 2004-2024 (ventana 5 años) | `data/raw/udalmap_vpo_terminadas.csv` |
| B7 | `P_oficial_vs_anuncios_por_TH.png` | 2024 + 2026, no comparable | `mongo_alquiler_por_municipio.csv` |
| B8 | `M26_mapa_coropletico_2026.png` + `M26_mapa_cobertura.png` | 2026 | `esfuerzo_mercado_2026.csv` |

## Reglas de puesta en escena

- **Una cifra por diapositiva** como titular; el resto, apoyo.
- **Cada figura lleva su año** (sello en el PNG y pie): 2024 oficial, 2026 oferta.
  Si es mixta, se dice «no comparable» en voz alta; nunca se presenta como serie.
- **Nunca** decir «Docker», «759», «182 silver», «54/65/40», «62/252», «84,4 % con y sin»,
  «2,0×», «15 colecciones vivas», «24 índices», «63/63», «287 tests», «54/54» ni
  «corrida real OK».
- Decir «no lo sabemos» siempre que aparezca gris.
- Distinguir siempre: **78,6 % municipal** · **87,3 % anuncio** · **1.350 € mediana de
  medianas** · **1.500 € mediana de anuncios**.
- HDFS: **353 objetos de inventario**; recuperación pendiente de DNS y `--out`; evidencia
  funcional v8 para Kafka. No afirmar como revalidado hoy.
- Si falla la red: no hay demo en vivo; se enseña la captura del gate y el JSON de evidencia.

## Recorte a 12 minutos

1. Fusionar 15 y 16 (modelo + CRUD) en una sola diapositiva técnica.
2. Fusionar 17 y 18 (aggregation + consistencia) en otra.
3. Bajar 7 a 40 s (solo SERPAVI; bootstrap a backup).
4. 4 y 10 a 40 s cada una.
5. 12 y 13 a 20 s cada una, o citarlas de palabra.
6. Mantener 2, 9, 11, 14, 19, 21 y 22.

## Comprobar que el deck no se ha desincronizado

```
python scripts/verificar_cifras_deck.py
```

Lee `index.html`, calcula las cifras desde los CSV y falla si alguna no coincide o si
reaparece una afirmación retirada. Se ejecuta antes de exportar el PDF.
