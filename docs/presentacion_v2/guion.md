# Guion — Presentación v2 (híbrida: datos + ingeniería)

**Duración objetivo:** 13:30 (15 diapositivas) · **Recorte a 12:00** al final.
**Público:** tribunal SBD + BDA (perfil técnico, poco tiempo, mucha pregunta).
**Idioma:** castellano. **Formato:** 16:9 fijo, offline, sin dependencias.
**Regla de oro:** primero la respuesta, después cómo se calculó. Cada cifra lleva su
artefacto. Ninguna cifra de este guion se teclea a mano: todas salen de
`data/resultados/*.csv` o de Mongo.

> **Cifras congeladas (2026-11-11).** Si algo cambia, se regenera el CSV antes de tocar
> la diapositiva. Las cifras obsoletas que **no** se usan: 188 silver, 235 tests,
> 54/65/40, 1716/2465/1536/1406 € de precio medio, 62/252 con precio.

---

## Estructura y tiempos

| # | Diapositiva | Inicio | Fin | Acto |
|---|---|---|---:|---|
| 1 | La pregunta | 0:00 | 0:30 | A. Respuesta |
| 2 | La respuesta en 30 segundos | 0:30 | 2:00 | A. Respuesta |
| 3 | De dónde salen y cuánto hay | 2:00 | 3:10 | B. Datos |
| 4 | Qué podemos afirmar | 3:10 | 4:20 | B. Datos |
| 5 | Cómo se mide | 4:20 | 5:15 | B. Datos |
| 6 | El mapa | 5:15 | 6:15 | C. Detalle |
| 7 | El reparto | 6:15 | 7:15 | C. Detalle |
| 8 | Los 4 robustos | 7:15 | 8:45 | C. Detalle |
| 9 | Incertidumbre y hallazgos | 8:45 | 10:00 | C. Detalle |
| 10 | Arquitectura | 10:00 | 11:00 | D. Ingeniería |
| 11 | Pipeline y limpieza | 11:00 | 12:00 | D. Ingeniería |
| 12 | Modelo Mongo | 12:00 | 12:45 | D. Ingeniería |
| 13 | Aggregation, índices, CRUD | 12:45 | 13:30 | D. Ingeniería |
| 14 | Pruebas | 13:30 | 14:30 | E. Cierre |
| 15 | Límites y cierre | 14:30 | 15:30 | E. Cierre |

Los tiempos suman 15:30 con colchón; en ensayo hay que entrar en **13:30** (las
diapositivas 3, 4 y 9 son las que se estiran).

---

# Acto A — La respuesta

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

## D2 · La respuesta en 30 segundos (0:30–2:00)

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
- **Transición:** «¿De dónde salen esos 159 y esos 594 anuncios?»

---

# Acto B — Los datos que obtuvimos

## D3 · De dónde salen y cuánto hay (2:00–3:10)

- **Mensaje:** no es una fuente ni una tabla: son 12 familias de fuentes, 41 extractores
  y 356 ficheros originales que se pueden reconstruir.
- **En pantalla:**
  - 12 grupos de fuentes · 41 extractores Python (API + scraping)
  - **356** ficheros raw → **352** canónicos en HDFS (manifest 354 SHA)
  - **843 anuncios crudos → 594 vigentes**: dedup cross-portal + **45 en cuarentena**
    fuera de Euskadi
  - Tipos: 129 CSV · 101 HTML · 61 JSON · 49 ZIP · 6 XLSX · 2 GeoJSON
- **Gráfica:** `g4_distribucion_anuncios.png` — cola larga de anuncios por municipio.
- **Evidencia:** `config/fuentes.yaml`, `extract/`, `data/raw`, `docs/raw_manifest_sha256.txt`.
- **Rúbrica:** C1, C5, C15, C6.
- **Nota oral:** «Esto no es un CSV de clase. Son APIs de Eustat e INE, scraping de
  Fotocasa y Pisos, Open Data de Euskadi, Etxebide, Lanbide, Udalmap, GTFS y OSRM. De 843
  anuncios crudos quedan 594: quitamos duplicados entre portales y mandamos 45 a cuarentena
  porque estaban fuera de Euskadi. La distribución de la derecha es la razón de todo lo que
  viene después: la mayoría de municipios tiene cero, uno o dos anuncios.»
- **Transición:** «Con eso, ¿qué se puede afirmar y qué no?»

## D4 · Qué podemos afirmar (3:10–4:20)

- **Mensaje:** el dato bueno es el oficial; el resto es contexto, y lo decimos con
  nombres.
- **En pantalla:**
  - **159** municipios con alquiler oficial Eustat · **93** imputados por IDW
  - Tier de confianza: **A 4 · B 3 · C 57 · D 188**
  - **64/252** con anuncio · **201** anuncios de habitación en 9 municipios
  - **5.040** solicitudes Etxebide · **406** promociones · **60/252** con precio de anuncio
- **Gráficas:** `H2_tier_confianza_ABCD.png` + `H11_imputacion_oficial_idw_por_TH.png`.
- **Evidencia:** `mongo_tier_confianza.csv`, `mongo_esfuerzo_por_municipio.csv`.
- **Rúbrica:** C6, C8, C15, C19.
- **Nota oral:** «Aquí está la honestidad del proyecto. Solo 159 municipios tienen alquiler
  oficial; 93 los completamos por IDW y solo valen para sensibilidad. El Tier mide cuánta
  muestra hay: 4 municipios con 30 o más anuncios, 3 entre 10 y 29, 57 con menos de 10 y
  188 sin ninguno. El precio del anuncio solo es observable en 60 de 252: donde no hay,
  no imputamos.»
- **Transición:** «Y el indicador, ¿cómo se construye?»

## D5 · Cómo se mide (4:20–5:15)

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
- **Transición:** «Veamos dónde aprieta.»

---

# Acto C — La respuesta en detalle

## D6 · El mapa (5:15–6:15)

- **Mensaje:** el esfuerzo tiene geografía: capitales y costa arriba; interior y sur, abajo.
- **En pantalla:** coroplético municipal, 159 oficiales, escala 20-40 %, leyenda con el 30 %.
- **Gráfica:** `mapa_coroplastico_esfuerzo_18_34.png`.
- **Evidencia:** figura generada desde `mongo_esfuerzo_por_municipio.csv`.
- **Rúbrica:** C19, C18.
- **Nota oral:** «Cada municipio con alquiler oficial, coloreado por esfuerzo. No hace falta
  leer nombres: Bilbao, Donostia y el corredor del Nervión están en la banda alta; el interior
  de Álava y amplias zonas rurales, por debajo del 30 %. Ojo: el gris es “sin dato”, no cero.»
- **Transición:** «¿Cuántos quedan a cada lado del umbral?»

## D7 · El reparto (6:15–7:15)

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
- **Transición:** «Pero solo cuatro aguantan una comparación firme.»

## D8 · Los 4 robustos (7:15–8:45)

- **Mensaje:** cuatro municipios sostienen el ranking; el orden 3º/4º es frágil y lo decimos.
- **En pantalla (tabla):**

| Municipio | n | Esfuerzo 18-34 | Precio medio | Paro Lanbide |
|---|---:|---:|---:|---:|
| Bilbao | 204 | 37,69 % | 1.704,96 € | 9,71 % |
| Donostia / San Sebastián | 126 | 38,17 % | 2.247,82 € | 5,82 % |
| Getxo | 50 | 28,60 % | 1.578,21 € | 6,40 % |
| Vitoria-Gasteiz | 39 | 33,37 % | 1.408,08 € | 8,89 % |

  - Getxo vs Vitoria: **11 anuncios** de diferencia → sin ranking firme 3º/4º
  - **Barakaldo 38,50 % con n=6** → el ranking sin `n≥30` es una trampa
- **Gráfica:** `O_ranking_bloqueado_n30.png` (IC y resto en gris).
- **Evidencia:** `comparativa_3_municipios_mongo.csv`, `pipeline_indicadores_municipio`.
- **Rúbrica:** C18 (núcleo), C17.
- **Nota oral:** «Bilbao y Donostia están en el 38 % con la muestra más grande. Getxo está
  por debajo del 30 % pero por 1,4 puntos, y solo tiene 11 anuncios más que Vitoria: no
  convertimos eso en un podio. Barakaldo saldría el primero del ranking de esfuerzo con
  38,5 %, y tiene seis anuncios: por eso el umbral de 30. Lo que sí decimos: en Bilbao la
  tensión es precio más paro; en Donostia es precio puro, con el paro más bajo.»
- **Transición:** «¿Y cuánto de esto es incertidumbre?»

## D9 · Incertidumbre y hallazgos laterales (8:45–10:00)

- **Mensaje:** el titular aguanta la incertidumbre; dos hallazgos laterales cambian la
  lectura: temporal≠larga y la demanda social no sigue al precio.
- **En pantalla:**
  - Bootstrap 95 %: Bilbao 33,75–40,95 · Getxo 27,54–31,77 · Donostia 32,4–45,8 (se solapan)
  - IDW 93: mediana 23,38 %; global 252: 25,37 %
  - Temporal y larga: misma **mediana mensual (1.500 €)**, pero el temporal es más
    pequeño (80 vs 92,5 m²). **Por m², el temporal es +23,2 % en Fotocasa** (+13,7 % en el total)
  - Tensión Etxebide (solicitudes por mil) vs esfuerzo: no es una recta
- **Gráficas:** `H8b_modalidad_mediana_eur_m2.png` + `H10_tension_vs_esfuerzo.png`.
- **Evidencia:** `bootstrap_robustos.csv`, `sensibilidad_idw.csv`, `mongo_tier_confianza.csv`.
- **Rúbrica:** C16, C17, C18.
- **Nota oral:** «Con bootstrap, los intervalos de Bilbao, Getxo y Donostia se solapan: no
  hay orden firme entre ellos. El IDW baja la mediana dos puntos y medio, pero no cambia el
  titular. Dos cosas que descubrimos por el camino: los anuncios temporales no son más caros
  al mes, sino por metro cuadrado — 18,95 frente a 16,67 €/m² en el total, un 13,7 %, y frente
  a 15,38 en Fotocasa, un 23,2 % — porque el piso temporal es más pequeño (80 frente a 92,5 m²);
  por eso no se mezclan. Y la demanda social no va en línea recta con el precio,
  hay municipios con mucha lista de espera y alquiler moderado.»
- **Transición:** «Hasta aquí la respuesta. Ahora, cómo se calcula y cómo se demuestra.»

---

# Acto D — Cómo se calculó

## D10 · Arquitectura (10:00–11:00)

- **Mensaje:** dos ramas sobre los mismos originales: una analítica (Mongo) y una de
  conservación (Kafka→HDFS); nunca Kafka→Mongo.
- **En pantalla (diagrama de 6 cajas):**
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
- **Transición:** «¿Y cómo se pasa de 356 ficheros a un indicador?»

## D11 · Pipeline y limpieza (11:00–12:00)

- **Mensaje:** una orden reconstruye todo, y la limpieza es explícita: nulos marcados,
  duplicados resueltos, tipos convertidos.
- **En pantalla:**
  - 41 extractores · **44 scripts** transform · **38 nodos** en el DAG
  - Limpieza PyMongo: `canonicalize_codigo_ine`, `mark_nulls`, `resolve_duplicates`,
    `convert_types` (+ `clean_obsolete_fields`)
  - **182/182** silver y **53/53** gold reconstruidos desde cero, byte a byte
  - `python scripts/run_pipeline.py --fase silver,quality,gold`
- **Gráfica:** ninguna (diagrama de fases + dos checks).
- **Evidencia:** `scripts/run_pipeline.py`, `storage/clean_mongo.py`, manifests.
- **Rúbrica:** C1, C7, C8, C15 (núcleo del 46,7 %).
- **Nota oral:** «La automatización no es un script: es un DAG con dependencias. Cada fichero
  de silver tiene un productor declarado o no existe. Los nulos se marcan, no se rellenan;
  los duplicados se resuelven por portal+id y por huella; los tipos se convierten, incluido
  el `codigo_ine` a cinco dígitos. Y se puede reconstruir de cero: lo hicimos, 182 ficheros
  y 52 artefactos idénticos.»
- **Transición:** «¿Por qué Mongo y no un CSV?»

## D12 · Modelo Mongo (12:00–12:45)

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

## D13 · Aggregation, índices y CRUD (12:45–13:30)

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

# Acto E — Pruebas y cierre

## D14 · Pruebas (13:30–14:30)

- **Mensaje:** no es una demo: es un sistema que se reconstruye y que falla cuando debe.
- **En pantalla:**
  - **262 tests** (2 skipped) · gobernanza **TODO OK** (44/38/182/11)
  - Gate offline: 354 raw SHA + 182 silver + 14 colecciones + lag 0
  - Rebuild: **182/182** silver y **53/53** gold byte-idénticos
  - **FAIL 07 conocido y visible**: paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26
- **Gráfica:** ninguna (4 checks en verde + 1 en ámbar).
- **Evidencia:** `pytest`, `verificar_gobernanza.py`, `gate_extremo_a_extremo.py --offline`,
  `verificar_fase_datos.py`.
- **Rúbrica:** C8, C16, T6, P-08.
- **Nota oral:** «Tenemos 262 tests. El gate verifica los 354 SHA del raw y los 182 ficheros
  de silver. Reconstruimos la capa entera desde cero y sale idéntica. Y hay un check que
  falla a propósito: tres municipios con paro cero en el INE y tasa no nula en Lanbide.
  Preferimos enseñarlo en rojo antes que imputarlo para que salga verde.»
- **Transición:** «Y hasta aquí lo que sostenemos.»

## D15 · Límites y cierre (14:30–15:30)

- **Mensaje:** sabemos qué afirmamos, qué no y qué nos tumbaría.
- **En pantalla (dos columnas):**
  - **Sostenemos:** 4 robustos con n≥30; 40/159 >30 %; Bilbao/Donostia ~38 %
  - **No sostenemos:** ranking fino fuera de Tier A; emancipación municipal (solo CAE);
    precio donde no hay anuncio; procesados en HDFS
  - **Excepción:** HDFS solo raw (352), procesados en local
  - Frase final: «En la mayoría del territorio, justo; en las capitales, no; y en 188
    municipios no lo sabemos.»
- **Gráfica:** ninguna.
- **Evidencia:** este guion, `openspec/audit/v10_2026-11-11/auditoria_rubrica_v10.md`.
- **Rúbrica:** C18, C19, P-05.
- **Nota oral:** «Nos tumbaría una fuente independiente que, con n≥30 y la misma ventana,
  moviera más de un 10 % el precio de Bilbao, Donostia, Getxo o Vitoria. Nos tumbaría
  encontrar un piso de los 45 en cuarentena que sí estuviera en Euskadi; la cuarentena es
  reversible. Y no defendemos emancipación municipal: solo tenemos CAE. Con más datos,
  lo primero sería subir la muestra de los 57 Tier C y separar temporal de larga en todo.»
- **Cierre:** «Gracias. Abrimos el código y los datos.»

---

# Backup (solo si preguntan)

| # | Tema | Qué enseñar |
|---|---|---|
| B1 | Modelado Tema 8 | Las 7 preguntas del docx con respuesta y la decisión embedding/referencing |
| B2 | Transacciones / sharding | Atómica de documento, por qué no replica set, shard key candidata `codigo_ine` |
| B3 | CRUD y consultas | `demo_crud_operations` + 30 consultas (dot notation, `$elemMatch`, `$and`) |
| B4 | Hashes y conteos | 354/182/52 · 594/252 · 4/3/57/188 · 16+14 colecciones |
| B5 | HDFS/Kafka | Evidencia v8, 352 canónicos, topic `vivienda_euskadi`, lag 0, por qué no se revalida hoy |
| B6 | Habitaciones | `H6_habitaciones_mediana_rango.png`; solo Bilbao 96 y Donostia 66 firmes |
| B7 | Oficial vs anuncios | `P_oficial_vs_anuncios_por_TH.png`; divergencia por territorio |
| B8 | VPO | `C_vpo_por_estado.png`; 406 promociones, 251/252 con flujo terminadas |

---

# Mapa de rúbrica → diapositiva

| Criterio | Diapositivas |
|---|---|
| C1 Extracción API+scraping | 3, 11 |
| C2 HDFS | 10, 15, B5 |
| C3 Kafka | 10, B5 |
| C4 Integración | 10, 14 |
| C5 Fuentes + campo común | 3, 12 |
| C6 2+ colecciones + relación | 4, 12 |
| C7 Limpieza | 11 |
| C8 Automatización | 11, 14 |
| C9 Modelado justificado | 12, B1 |
| C10 CRUD | 13, B3 |
| C11 Consultas | 13, B3 |
| C12 Aggregation | 13 |
| C13 Índices/explain | 13 |
| C14 Consistencia | 13, B2 |
| C15 Heterogéneos | 3, 11 |
| C16 Automatización análisis | 4, 7, 14 |
| C17 Indicadores | 4, 5, 8 |
| C18 Respuesta | 1, 2, 6, 7, 8, 15 |
| C19 Visualización | 4, 6, 7, 9 |
| T1–T7 | 12, 13, 14, B1–B3 |

---

# Producción

## Gráficas: origen y destino

| Diapositiva | Figura | Fuente |
|---|---|---|
| D3 | `g4_distribucion_anuncios.png` | Mongo `indicadores` |
| D4 | `H2_tier_confianza_ABCD.png` | `mongo_tier_confianza.csv` |
| D4 | `H11_imputacion_oficial_idw_por_TH.png` | Mongo `indicadores` |
| D6 | `mapa_coroplastico_esfuerzo_18_34.png` | `mongo_esfuerzo_por_municipio.csv` |
| D7 | `hist_esfuerzo_18_34_umbral30.png` | idem |
| D8 | `O_ranking_bloqueado_n30.png` | idem + bootstrap |
| D9 | `H8b_modalidad_mediana_eur_m2.png` | `mongo_modalidades.csv` |
| D9 | `H10_tension_vs_esfuerzo.png` | Mongo `indicadores` |

Todas están ya en `data/resultados/`. Si se regeneran, se hace con
`python analysis/run_analisis_mongo.py` y se vuelven a comprobar los SHA.

## Reglas de puesta en escena

- **Una cifra por diapositiva** como titular; el resto, apoyo.
- **Nunca** decir «Docker», «759», «188 silver», «54/65/40» ni «62/252».
- Decir «no lo sabemos» siempre que aparezca gris.
- Si falla la red: no hay demo en vivo; se enseña la captura del gate.
- Acentos, `ñ`, `€`, `‰` y `≥` revisados en HTML y PDF.

## Recorte a 12 minutos

1. Fusionar D12 y D13 en una sola diapositiva técnica (modelo + explain).
2. Bajar D9 a 40 s (solo bootstrap; `H8b`/`H10` pasan a backup).
3. D3 y D4 a 50 s cada una.
