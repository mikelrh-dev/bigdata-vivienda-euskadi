# Presentación de resultados — Especificación

**Capacidad:** `presentacion-de-resultados`
**Estado:** Hecho, alineado con RA4 v2
**Criterios cubiertos:** rúbrica v2 SBD-RA4 Procesamiento, análisis y
preparación de resultados (datos heterogéneos, automatización del análisis,
indicadores, respuesta al reto, preparación para visualización)
**Contrato:** `../contrato-reto/spec.md`
**Fuente primaria PDF:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (rúbrica v2, SBD RA4, peso 40 % en PDF línea 115, tabla en PDF líneas 113-123)
**Fuente primaria docx:** `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` (§13 preguntas analíticas, §14 entregables; evaluación separada, no pesos v2)

---

## Purpose

Procesar datos heterogéneos procedentes de 2 o más fuentes, ejecutar
automáticamente los análisis principales con PyMongo, calcular indicadores
de vivienda y emancipación, preparar automáticamente conjuntos de resultados
para su representación, y responder a la pregunta del reto comparando
municipios con conclusiones vinculadas a indicadores calculados en MongoDB.

## Trazabilidad de fuentes (cotejo 2026-11-05)

Fuente primaria: `brief/RETO 1Evaluacion SBD-BDAv2.pdf`, SBD RA4
*Procesamiento, análisis y preparación de resultados*, peso 40 % en PDF
línea 115. La tabla RA4 está en PDF líneas 113-123. El cotejo es contra el
nivel 10 (columna *10 puntos*) de esa tabla, línea por línea (ver notas tras
cada requisito en este spec). Sin diferencias literales en los 5 criterios
RA4; las diferencias aparentes son los endurecimientos propios marcados
como extensión propia.

| Criterio RA4 (PDF) | PDF línea | Requisito en este spec |
|---|---|---|
| Datos heterogéneos | 119 | `DATOS-HETEROGENEOS-01` |
| Automatización del análisis | 120 | `AUTOMATIZACION-ANALISIS-01` |
| Indicadores | 121 | `INDICADORES-01` |
| Respuesta al reto | 122 | `CONCLUSION-01` |
| Preparación para visualización | 123 | `PREPARACION-VISUALIZACION-01` |

Fuente complementaria: `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`,
§13 *Preguntas analíticas que debería poder responder el sistema*
(docx líneas 178-187) y §14 *Entregables específicos de MongoDB*
(docx líneas 188-208). Son evaluación separada Tema 8, no pesos v2. El mapa
trazable §13–§14 está al final de este spec: §13 → `CONCLUSION-01`,
§14 → `ENTREGABLES-01` (en `../contrato-reto/spec.md`) y requisitos de
este spec.

Extensiones propias: las prohibiciones P-01 a P-08, el canónico 18–34 y
`CARGA-SEGURA` siguen vigentes como extensión propia del proyecto. No son
requisito v2 ni pesos Tema 8. En este spec, los endurecimientos más
estrictos que el PDF (reproducibilidad desde MongoDB, nunca tecleado a
mano, regeneración que reproduce lo mismo) quedan marcados como *extensión
propia más estricta que el PDF*, sin borrarlos. SHALL solo donde el
proyecto ya cumple; SHOULD donde hoy no cumple (tensión/paro en silver).

---

## Requirements

### Requirement: DATOS-HETEROGENEOS-01 — Datos heterogéneos

El sistema SHALL integrar datos procedentes de fuentes con estructuras
diferentes y SHALL adaptarlos mediante Python/PyMongo (nivel 10 de la rúbrica
v2). Para el nivel 7, SHALL utilizar al menos arrays, documentos anidados o
datos con estructuras diferentes.

> Cotejo PDF (2026-11-05): PDF línea 119, columna *10 puntos* literal:
> «Integra datos procedentes de fuentes con estructuras diferentes y los
> adapta mediante Python/PyMongo». Sin diferencias literales. El nivel 7
> del spec corresponde a PDF línea 119, columna *7 puntos*.

#### Scenario: Estructuras diferentes — nivel 7

- GIVEN fuentes con estructuras diferentes
- WHEN se cargan los datos
- THEN el sistema utiliza arrays, documentos anidados o estructuras
  diferentes sin perder información esencial

#### Scenario: Integración y adaptación de fuentes heterogéneas — nivel 10

- GIVEN al menos 2 fuentes con estructuras diferentes
- WHEN se integran los datos
- THEN Python/PyMongo adapta cada estructura a un modelo común
- AND la adaptación es reproducible con un script y no es manual

### Requirement: AUTOMATIZACION-ANALISIS-01 — Automatización del análisis

El sistema SHALL ejecutar automáticamente todos los análisis principales y
SHALL devolver resultados preparados para su representación (nivel 10 de la
rúbrica v2). Para el nivel 7, SHALL disponer de un script PyMongo que
ejecute consultas y agregaciones.

> Cotejo PDF (2026-11-05): PDF línea 120, columna *10 puntos* literal:
> «Un script ejecuta automáticamente todos los análisis principales y
> devuelve resultados preparados para su representación». Sin diferencias
> literales. El nivel 7 del spec corresponde a PDF línea 120, columna
> *7 puntos*.

#### Scenario: Script PyMongo ejecuta el análisis — nivel 7

- GIVEN los datos cargados en MongoDB
- WHEN se ejecuta el script PyMongo
- THEN las consultas y agregaciones principales se ejecutan sin intervención
  manual

#### Scenario: Automatización completa — nivel 10

- GIVEN los datos cargados en MongoDB
- WHEN se ejecuta el script de análisis
- THEN todos los análisis principales se ejecutan automáticamente
- AND los resultados devueltos quedan preparados para su representación
- AND repetir la ejecución reproduce los mismos resultados

### Requirement: INDICADORES-01 — Cinco indicadores distintos non-legacy (esfuerzo 18-34, tensión, paro, precio m2, VPO terminadas)

El sistema SHALL calcular 5 indicadores distintos non-legacy (esfuerzo_16_29 archivado, no cuenta) con pipeline Mongo verdadero para
tensión social y paro Lanbide, o SHALL declararlos silver con justificación
documentada y sin inventar valores. SHALL preservar `metodo_imputacion` y
MUST NOT aplicar `fillna` mediana sin flag `is_imputed`. Los CSV canónicos
con huella SHALL ser 253 y 253 filas y 3 automáticos (regenerables).
(Previously: 5 indicadores con 2+ fuentes y reproducibilidad desde MongoDB,
y tensión/paro en SHOULD por silver según `auditoria_lagunas_silver.csv`.)

#### Scenario: Pipeline verdadero o silver justificado

- GIVEN los 5 indicadores con tensión social y paro Lanbide
- WHEN se ejecutan las pipelines sobre MongoDB
- THEN existen pipelines Mongo reales o justificación silver documentada
- AND `metodo_imputacion` se preserva en la salida
- AND todo `fillna` mediana lleva flag `is_imputed`

#### Scenario: CSV canónicos con huella

- GIVEN los 5 indicadores calculados
- WHEN se resumen los resultados en `openspec/archive/2026-11-10-docs/matriz_indicadores.md`
- THEN constan los CSV 253 y 253 filas y 3 automáticos con huella
- AND regenerar reproduce los mismos resultados

### Requirement: PREPARACION-VISUALIZACION-01 — Tres conjuntos automáticos para representar

El sistema SHALL generar mediante PyMongo datos utilizables para gráficos
(nivel 7 de la rúbrica v2) y, para el nivel 10, SHALL generar
automáticamente mediante PyMongo al menos 3 conjuntos de resultados
diferentes preparados para representar. Los valores SHALL proceder de
consultas PyMongo, nunca de números tecleados a mano.

> Cotejo PDF (2026-11-05): PDF línea 123, columna *10 puntos* literal:
> «Genera automáticamente mediante PyMongo al menos 3 conjuntos de
> resultados diferentes preparados para representar». Sin diferencias
> literales.

> Extensión propia más estricta que el PDF: «nunca de números tecleados a
> mano» y «regenerar ... reproduce los mismos resultados». El PDF (línea
> 123) solo dice «Genera automáticamente mediante PyMongo al menos 3
> conjuntos ... preparados para representar»; no detalla la prohibición de
> tecleado ni la reproducibilidad de la regeneración. Se conserva sin borrar
> como endurecimiento propio (prohibición P-05 + reproducibilidad del
> orquestador `analysis/run_analisis_mongo.py`), verificado por
> `tests/test_mongo_orquestador.py`. No es requisito v2.

#### Scenario: Datos utilizables para gráficos — nivel 7

- GIVEN una agregación sobre MongoDB
- WHEN se genera el conjunto de resultados
- THEN los datos quedan utilizables directamente para representar

#### Scenario: Al menos 3 conjuntos automáticos diferentes — nivel 10

- GIVEN los análisis principales ejecutados
- WHEN el script PyMongo termina
- THEN existen al menos 3 conjuntos de resultados diferentes
- AND cada conjunto queda preparado para su representación
- AND ningún valor procede de un número escrito a mano
- AND regenerar los conjuntos reproduce los mismos resultados

### Requirement: CONCLUSION-01 — Guion Tema 8 de 1 página con 10 criterios y lagunas

El sistema SHALL redactar en `openspec/archive/2026-11-10-docs/guion_defensa.md` un guion Tema 8 de 1
página centrado en embedding, índices y atomicidad, con la cadena offline
HDFS centro + Kafka pid 1832. SHALL documentar los 10 criterios y las lagunas,
y MUST NOT dejar 16-29 sin marcar: 16-29 SHALL marcarse legacy y el canónico
es 18-34. La cadena offline SHALL limitarse a lectura de HDFS centro y MUST
NOT tocar `data/raw` ni raw HDFS, ni crear carpeta nueva, ni subir procesado;
prod intacta por defecto (solo lectura o test con
`MONGO_ALLOW_DESTRUCTIVE=1`).
(Previously: comparación de 3 municipios vinculada a indicadores, con
advertencia de muestra pequeña.)

#### Scenario: Guion de 1 página con cadena actual

- GIVEN `openspec/archive/2026-11-10-docs/guion_defensa.md`
- WHEN se revisa el guion Tema 8
- THEN tiene 1 página con embedding, índices, atomicidad y HDFS centro + Kafka pid 1832
- AND constan los 10 criterios y las lagunas documentadas

#### Scenario: 16-29 marcado legacy

- GIVEN el guion Tema 8 y la matriz O1-O4
- WHEN aparece el rango 16-29
- THEN está marcado legacy y el canónico es 18-34
- AND ninguna conclusión usa 16-29 como rango canónico

### Requirement: RESPUESTA-01 — Respuesta comparativa de 4 robustos con matriz O1-O4

El sistema SHALL compare 4 municipios robustos —Bilbao 204, Donostia 126,
Getxo 50, Vitoria-Gasteiz 39 anuncios (valores reales post re-resolución
2026-11-07; el baseline pre-change era 173/113/40/39)— con paro Lanbide no nulo o silver
justificado, y SHALL documentar la matriz O1-O4 en
`openspec/archive/2026-11-10-docs/conclusiones_municipios.md` con mediana 26,61 (oficial 18-34) y 25,2%
sobre 30. La matriz SHALL advertir que Getxo 50 vs Vitoria-Gasteiz 39 difiere
en 11 anuncios y MUST NOT leerse como ranking firme entre esos dos. La
comparativa SHALL registrarse en `openspec/archive/2026-11-10-docs/trazabilidad_vm.md` (Fecha/Objetivo/
Máquina/Comando/Salida/Conclusión) y MUST NOT tocar `data/raw` ni raw HDFS,
ni crear carpeta nueva, ni subir procesado.

#### Scenario: Cuatro robustos con paro no nulo

- GIVEN los 4 robustos Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39
- WHEN se genera la comparativa en `openspec/archive/2026-11-10-docs/conclusiones_municipios.md`
- THEN el paro Lanbide no es nulo o consta justificación silver
- AND la salida está trazada en `openspec/archive/2026-11-10-docs/trazabilidad_vm.md`

#### Scenario: Matriz O1-O4 con advertencia Getxo/Vitoria

- GIVEN la matriz O1-O4 con mediana 26,61 y 25,2% sobre 30
- WHEN se lee la comparación Getxo 50 vs Vitoria-Gasteiz 39
- THEN figura la advertencia de 11 anuncios de diferencia
- AND NO se presenta como ranking firme

El sistema SHALL corregir la cifra stale 759 a 594 (post re-resolución + cuarentena) en los cuatro documentos: `openspec/archive/2026-11-10-docs/datos_finales_conclusiones_2026-11-05.md`, `openspec/archive/2026-11-10-docs/informe_final.md`, `data/resultados/README.md` y `docs/presentacion/index.html`. La recarga real es 594 anuncios con 188 municipios en cero (Tier D) y Bilbao 204 como máximo; esas tres cifras (594/188/204) SHALL aparecer unidas en cada uno de los cuatro documentos, con la nota «759 era el pre-change». Ningún documento SHALL afirmar 759 como cifra vigente tras el cambio. La verificación SHALL hacerse con `grep` por documento.

#### Scenario: Los cuatro documentos dicen 594, no 759

- GIVEN Mongo recargado con `anuncios=594` vía `python -m storage.load_mongo`
- WHEN se verifican los cuatro documentos con `grep -c "594"`
- THEN cada uno contiene 594/188/204 y no contiene 759 como total vigente (`grep -c "759" openspec/archive/2026-11-10-docs/informe_final.md` → salida: `0`, salvo nota histórica «759 era el pre-change»)
- AND `pytest tests -q` sigue en verde tras la sincronización

### Requirement: CONCLUSION-02 — Tiers A/B/C/D, conciliación 62/252 vs n_precio=7 y ranking n>=30 (M2/M3, extensión 2026-11-07, sustituye L1/L2/L3)

El sistema SHALL clasificar municipios por `n_anuncios` post re-resolución y SHALL NOT presentar ranking municipal 1-16 ni imputar precio comarcal/IDW. Tier A (n≥30): Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39 — comparación fuerte con ranking firme. Tier B (10-29): Sopela 19, Zarautz 15, Santurtzi 11 — solo indicativo, separando temporal vs larga estancia, con min-max + mediana y `n_precio`. Tier C (1-9): sin precio municipal, solo conteo. Tier D (0): sin dato, con contexto oficial cuando exista. Precio observable solo en 62/252 municipios con anuncio real.
(Previously: niveles L1/L2/L3 con L3 1-9/0 sin dato.)

El sistema SHALL documentar en `data/resultados/README.md` la tabla de conciliación: 62/252 municipios con precio observable real (post re-resolución) frente a `n_precio=7` del tier agregado — los 7 son exclusivamente los municipios A+B robustos (4 Tier A + 3 Tier B) que sí publican precio municipal tras suprimir C/D; los C/D con precio no se publican. README SHALL mostrar ambas cifras juntas con esta explicación, sin esconder ninguna. El sistema MUST NOT presentar ranking, top-10 ni ordenación de esfuerzo o precios con municipios de `n_anuncios<30`: Barakaldo (`n=6`) SHALL NOT ranking verse por encima de Donostia (`n=126`) ni de ningún Tier A. Los municipios Tier C/D con `n<30` SHALL mostrarse como «n insuficiente» (con su `n` visible), nunca ocultarse ni ordenarse.

| Tier | n_anuncios | Nº | Tratamiento |
|---|---|---|---|
| A | ≥30 | 4 | fuerte |
| B | 10-29 | 3 | indicativo, temporal ≠ larga, con min-max + mediana + `n_precio` |
| C | 1-9 | 57 | sin precio municipal, solo conteo |
| D | 0 | 188 | sin dato, + contexto oficial |

#### Scenario: Ranking firme solo Tier A

- GIVEN los 4 Tier A con n≥30
- WHEN corre `python analysis/run_analisis_mongo.py` desde Mongo
- THEN `openspec/archive/2026-11-10-docs/conclusiones_municipios.md` compara solo Tier A con `n_anuncios` real
- AND salida: 13 PNG + 6 CSV, sin valores tecleados a mano

#### Scenario: Tier B separa modalidades

- GIVEN Sopela 19, Zarautz 15, Santurtzi 11
- WHEN se agregan indicadores
- THEN cada Tier B lleva min-max + mediana + `n_precio_temporal` y `n_precio_larga` por separado
- AND prohibido promediar temporal + larga; no hay ranking 1-16

#### Scenario: Edge Tier C/D sin precio municipal

- GIVEN municipio Tier C (1-9) o Tier D (0)
- WHEN se genera la tabla
- THEN figura «sin dato» con solo conteo, sin precio municipal y sin ranking
- AND Tier D añade contexto oficial sin conclusión de precio

#### Scenario: Conciliación 62 vs 7 publicada en README

- GIVEN resultados regenerados por `python analysis/run_analisis_mongo.py`
- WHEN se lee `data/resultados/README.md`
- THEN consta «62/252 con precio observable» y «`n_precio=7` = A+B robusto (4 A + 3 B); C/D suprimidas» en la misma tabla
- AND `grep -n "62/252" data/resultados/README.md` → salida: ≥ 1 línea; `grep -n "n_precio=7" data/resultados/README.md` → salida: ≥ 1 línea

#### Scenario: Ranking bloqueado para `n<30`

- GIVEN el ranking de esfuerzo con Barakaldo `n=6` y Donostia `n=126`
- WHEN corre `python analysis/run_analisis_mongo.py` y se genera el ranking
- THEN Barakaldo figura como «n insuficiente» (n=6 visible) y no ordena por encima de Donostia; el top-10 solo contiene `n>=30`
- AND `python -c "import pandas as pd; d=pd.read_csv('data/resultados/ranking_esfuerzo.csv'); print(d['n_anuncios'].min())"` → salida: `>= 30` (nunca 6)

### Requirement: PISOS-05 — Esfuerzo contextual, frase literal

El esfuerzo municipal SHALL citarse literalmente «252 contextual sobre 159» y SHALL NOT leerse como estimación oficial donde `n_anuncios<30`. Todo valor SHALL venir de Mongo (nunca tecleado a mano).
(Previously: frase «252 contextual sobre 159 oficiales».)

#### Scenario: Frase literal en conclusiones

- GIVEN `esfuerzo_joven_pct_18_34` en 252 municipios
- WHEN se revisa `openspec/archive/2026-11-10-docs/conclusiones_municipios.md`
- THEN consta «252 contextual sobre 159»
- AND `grep -c "252 contextual sobre 159" openspec/archive/2026-11-10-docs/conclusiones_municipios.md` ≥ 1

#### Scenario: Edge 0-9 anuncios

- GIVEN municipio con 0-9 anuncios
- WHEN se genera la tabla
- THEN figura «sin dato» y no entra en mediana ni comparativa

### Requirement: chart_tierB_range — Barras Tier B con min-max y mediana (2026-11-07)

El sistema SHALL generar `chart_tierB_range` en `build_presentacion.py` con 3 barras —Sopela 19, Zarautz 15, Santurtzi 11— leyendo `mongo_tier_confianza.csv`. Cada barra SHALL mostrar min-max y la mediana temporal vs larga por separado, con `n_precio_temporal` y `n_precio_larga` visibles, y la etiqueta `indicativo` (no ranking firme). MUST NOT promediar temporal + larga.

#### Scenario: Tres barras con rango y doble mediana

- GIVEN `mongo_tier_confianza.csv` con 252 filas
- WHEN corre `build_presentacion.py`
- THEN `index.html` y `presentacion.pdf` contienen 3 barras (19/15/11) con min-max y mediana temporal vs larga
- AND cada mediana va acompañada de su `n_precio`

### Requirement: chart_mapa_tier — Coroplético 4 niveles y capas (2026-11-07, aligerado + dedupe)

El sistema SHALL generar `chart_mapa_tier` como SVG desde `municipios_euskadi_252.geojson`, con join estricto por `codigo_ine` y 4 cromas A/B/C/D. MUST dibujar las capas oficial 159 / IDW 93 / contexto 252 con `metodo_imputacion` e `is_imputed`, y el texto literal `252 contextual sobre 159`. Si falta un `codigo_ine`, el municipio SHALL quedar nulo, sin inventar geometría ni precio.

El sistema SHALL aligerar `chart_mapa_tier.svg` con utilidades de simplificación hasta <2 MB, SHALL eliminar el duplicado g1/A1 y SHALL NOT cambiar la clasificación 252/252 A/B/C/D. Guardarraíles: sin Docker; HDFS solo raw 352; Kafka→HDFS, no Mongo; sin imputar comarcal.
(Previously: SVG ~5.9 MB sin límite de peso ni dedupe.)

_Reconciliación archive (2026-11-07):_ tras dedupe g1/A1 quedan 12 PNG únicos de 13 nombres emitidos (g1 byte-idéntico a A1 eliminado sin renumerar; A1 canónico). SVG final <2 MB con 252/252, Tier A4/B3/C57/D188, oficial 159 / IDW 93 / contexto 252 y `252 contextual sobre 159` — ver archive-report.

#### Scenario: Mapa 252/252 con capas etiquetadas

- GIVEN `municipios_euskadi_252.geojson` con 252 features
- WHEN corre `build_presentacion.py`
- THEN el SVG colorea 252/252 municipios A/B/C/D con capas 159/93/252
- AND consta el texto `252 contextual sobre 159`

#### Scenario: Mapa <2 MB sin duplicado g1/A1

- GIVEN el SVG regenerado (<2 MB)
- WHEN se mide y se busca g1/A1
- THEN un solo g1 (A1 canónico), 12 PNG únicos (13 emitidos) y 252/252 intacto

### Requirement: chart_effort_vs_n — Burbuja solo Tier A (2026-11-07)

El sistema SHALL generar `chart_effort_vs_n` (X `n_anuncios`, Y `esfuerzo_joven_pct_18_34`, tamaño `n_precio`) con solo los 4 Tier A (`n >= 30`). El resto SHALL aparecer en banda `n_insuficiente` sin ordenación. MUST NOT mostrar ranking 1-16, MUST NOT imputar precios ni tocar Docker/HDFS/Kafka.

#### Scenario: Burbuja con 4 puntos y banda insuficiente

- GIVEN `mongo_esfuerzo_por_municipio.csv`
- WHEN corre `build_presentacion.py`
- THEN la burbuja contiene exactamente 4 puntos Tier A con ejes X/Y y tamaño `n_precio`
- AND `n < 30` figura en banda `n_insuficiente` sin ranking

#### Scenario: Sin valores inventados

- GIVEN los CSV generados por `run_analisis_mongo.py`
- WHEN se regenera la presentación
- THEN ningún gráfico usa literales y `pytest tests -q` sigue verde

### Requirement: BOOTSTRAP-01 — `n_larga_solo_vivienda` ≠ Tier

El sistema SHALL documentar que el bootstrap usa `n_larga_solo_vivienda` 67/60/39/37 (Bilbao/Donostia/Getxo/Vitoria-Gasteiz), distinto del `n_anuncios` Tier 204/126/50/39. SHALL constar IC95 Bilbao 33.75–40.95 y Getxo 27.54–31.77. Los dos `n` SHALL NOT intercambiarse en textos ni gráficos.

#### Scenario: Bootstrap con su propio n

- GIVEN `data/resultados/bootstrap_robustos.csv`
- WHEN se lee
- THEN `n_anuncios_larga_vivienda` es 67/60/39/37, IC95 Bilbao 33.75–40.95 y Getxo 27.54–31.77
- AND el texto distingue ese `n` del Tier 204/126/50/39

### Requirement: DOCS-01 — 759→594 y frase ortogonal

El sistema SHALL corregir 759→594 en el docstring de `decor_trama` (`docs/presentacion/build_presentacion.py:218`) y en `docs/presentacion/README.md:62` (trama). SHALL constar la frase ortogonal: Nivel es tipología (`4/54/194`) y Tier es confianza por `n_anuncios` (`4/3/57/188`); son ejes ortogonales, no intercambiables.

#### Scenario: Textos en 594 con frase ortogonal

- GIVEN ambos ficheros
- WHEN se verifican con `grep`
- THEN `grep -c "594"` ≥ 1 en cada uno y 759 no figura como cifra vigente
- AND consta la frase ortogonal Nivel 4/54/194 vs Tier 4/3/57/188

### Requirement: chart_habitaciones_medianas — Barras residencia vs habitaciones

El sistema SHALL generar `chart_habitaciones_medianas` en `docs/presentacion/build_presentacion.py` desde `mongo_habitaciones_por_municipio.csv` + `mongo_tier_confianza.csv` (valores Mongo, nunca tecleados). Por municipio dibujará tres series separadas — residencia temporal, residencia larga, habitaciones — nunca agregadas ni promediadas. Cada barra de habitaciones SHALL mostrar mediana con min-max y `n_precio` visible. Solo Bilbao (96) y Donostia (66) con `n_precio >= 30` sostienen comparación firme; el resto (`n_precio`: Vitoria 12, Barakaldo 11, Getxo 8, Irun 3, Errenteria 2, Durango 1, Eibar 1; Durango `n`=2) SHALL etiquetarse `indicativo`/`n_insuficiente`, sin ranking ni imputación comarcal/IDW. Sin Docker; HDFS solo raw (352); Kafka → HDFS, nunca Kafka → Mongo.

_Reconciliación archive (2026-11-08):_ delta listaba Durango 2; en `n_precio` es 1 (`n`=2, un anuncio sin precio no imputado). Solo Bilbao/Donostia firmes verificadas en SVG (`firme solo Bilbao (96) y Donostia (66)`) — ver archive-report P1-1._

#### Scenario: Tres series con n_precio visible

- GIVEN `mongo_habitaciones_por_municipio.csv` con 9 filas
- WHEN corre `build_presentacion.py`
- THEN `chart_habitaciones_medianas` aparece en `index.html` y PDF con residencia temporal, larga y habitaciones por separado
- AND cada mediana lleva su `n_precio` y min-max

#### Scenario: Solo Bilbao y Donostia firmes

- GIVEN Bilbao 96 y Donostia 66
- WHEN se lee el gráfico
- THEN la comparación residencia vs habitaciones se presenta como firme
- AND el resto figura `indicativo`, sin ordenación ni ranking

#### Scenario: Eibar indicativo sin imputación

- GIVEN Eibar con `n_precio = 1`
- WHEN se renderiza su barra
- THEN muestra mediana + min-max + `n_precio` con etiqueta `indicativo`
- AND no hay valor imputado ni ranking

## Mapa trazable docx §13–§14 (Tema 8, evaluación separada)

<!-- Trazabilidad docx: §13 Preguntas analíticas (docx líneas 178-187) → CONCLUSION-01; §14 Entregables (docx líneas 188-208) → ENTREGABLES-01 en contrato-reto/spec.md. Pesos docx §16 no se suman a v2. Tensión/paro en silver queda en SHOULD, no SHALL (ver nota final). -->

Sin requisitos nuevos. Cada pregunta y entregable del docx se mapea a un
requisito ya existente en este spec o en `../contrato-reto/spec.md`. SHALL
solo donde el proyecto ya cumple. SHOULD donde hoy no cumple según revisión
(tensión/paro en silver).

### §13 Preguntas analíticas (docx líneas 178-187) → `CONCLUSION-01`

| # | Pregunta analítica docx §13 | Mapea a | Fuerza |
|---|---|---|---|
| Q1 | ¿Qué municipios presentan una relación más favorable entre ingresos y coste de vivienda? (docx línea 180) | `CONCLUSION-01` + `INDICADORES-01` (`esfuerzo_joven_pct_18_34`, canónico 18–34) | SHALL (ya cumple) |
| Q2 | ¿Qué porcentaje del salario se destinaría al alquiler o a la compra en distintos escenarios? (docx línea 181) | `CONCLUSION-01` + `INDICADORES-01` | SHALL (ya cumple) |
| Q3 | ¿Cómo cambia la accesibilidad según características de la vivienda? (docx línea 182) | `CONCLUSION-01` + `AUTOMATIZACION-ANALISIS-01` | SHALL (ya cumple) |
| Q4 | ¿Existen diferencias relevantes entre municipios o territorios? (docx línea 183) | `CONCLUSION-01` (comparación de 3 municipios/zonas vinculada a indicadores) | SHALL (ya cumple) |
| Q5 | ¿Qué variables parecen relacionarse con una mayor o menor posibilidad de emancipación? (docx línea 184) | `CONCLUSION-01` + `INDICADORES-01` + `COMPLEMENTARIOS-01` | SHOULD para tensión/paro (ver nota) |
| Q6 | ¿Cómo cambian los resultados si se filtra por un perfil concreto de persona joven? (docx línea 185) | `CONCLUSION-01` + `AUTOMATIZACION-ANALISIS-01` | SHALL (ya cumple) |
| Q7 | ¿Qué limitaciones tienen los datos y cómo afectan a las conclusiones? (docx líneas 186-187) | `CONCLUSION-01` (escenario «La conclusión no exagera»: advertencia de muestra y limitaciones) | SHALL (ya cumple) |

> **Nota disciplina SHALL/SHOULD (§13):** las preguntas Q1–Q4 y Q6–Q7 se
> satisfacen con el SHALL actual de `CONCLUSION-01` (comparación de 3
> municipios vinculada a indicadores calculados con MongoDB, con porqué y
> limitaciones). La pregunta Q5 sobre variables de emancipación —en
> particular tensión y paro— **no se eleva a SHALL** porque la revisión
> señala tensión/paro en silver como no cerrado (`data/resultados/auditoria_lagunas_silver.csv`:
> `tasa_paro_lanbide_pct` con 3 nulos y `tasa_desempleo_juvenil_real_pct`
> con 53 nulos en `analisis_variables_base.csv` / `dim_municipios_enriquecido.csv`).
> Sigue en SHOULD según `../contrato-reto/spec.md` (líneas 241-244): el
> sistema SHOULD completar el avión de tensión/paro en silver. El canónico
> 18–34 sigue siendo extensión propia.

### §14 Entregables específicos de MongoDB (docx líneas 188-208) → `ENTREGABLES-01`

`ENTREGABLES-01` vive en `../contrato-reto/spec.md` (Entregables y
demostración). La tabla siguiente no crea un nuevo `ENTREGABLES` en este
spec; referencia el existente y distribuye los 9 entregables entre los
requisitos de este spec y los de otros specs.

| Entregable docx §14 (líneas 191-208) | Contenido docx | Requisito en este spec |
|---|---|---|
| Base de datos (línea 191-192) | Colecciones MongoDB con datos reales tratados | `DATOS-HETEROGENEOS-01` + `INDICADORES-01` |
| Código Python (líneas 193-194) | Carga, limpieza, consultas, agregaciones y demás operaciones PyMongo | `DATOS-HETEROGENEOS-01` + `AUTOMATIZACION-ANALISIS-01` |
| Modelo (líneas 195-196) | Esquema de colecciones y justificación de decisiones | `DATOS-HETEROGENEOS-01` (estructurales) |
| Consultas (líneas 197-198) | Batería de consultas relevantes | `AUTOMATIZACION-ANALISIS-01` |
| Pipelines (líneas 199-200) | Aggregations para indicadores y conclusiones | `INDICADORES-01` + `AUTOMATIZACION-ANALISIS-01` |
| Rendimiento (líneas 201-202) | Índices creados y evidencia de explain() antes/después | Referencia a `INDICES-01` en `mongodb-y-analisis`; sin duplicar SHALL aquí |
| Consistencia (líneas 203-204) | Decisión razonada sobre atomicidad/transacciones | Referencia a `TRANSACCIONES-01` en `mongodb-y-analisis`; sin duplicar SHALL aquí |
| README (líneas 205-206) | Instrucciones para ejecutar y reproducir la parte MongoDB | `AUTOMATIZACION-ANALISIS-01` + `PREPARACION-VISUALIZACION-01` (reproducibilidad) |
| Defensa técnica (líneas 207-208) | Explicación oral de decisiones, resultados y limitaciones | `CONCLUSION-01` + `ENTREGABLES-01` en `contrato-reto` |

> **Disciplina §14:** `ENTREGABLES-01` en `../contrato-reto/spec.md` SHALL
> aportar evidencias 1-10, entregables de la sección 14, integración de temas
> de la sección 15 y checklist de la sección 17. Este spec no sube ningún
> SHALL nuevo: Rendimiento y Consistencia siguen mapeados a
> `mongodb-y-analisis`, y la reproducibilidad de README/Pipelines se
> apoya en las extensiones propias ya marcadas (`INDICADORES-01` reproducible
> desde MongoDB; `PREPARACION-VISUALIZACION-01` sin tecleado y regenerable),
> no en nuevos SHALL de tensión/paro.
