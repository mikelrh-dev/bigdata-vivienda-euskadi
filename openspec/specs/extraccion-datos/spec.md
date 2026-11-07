# Extracción de datos — Especificación

**Capacidad:** `extraccion-datos`
**Estado:** Desplegada
**Criterios cubiertos:** BDA-RA1 Extracción (10), BDA formato JSON/CSV,
objetivo 2 (salarios/población), requisito "todo en Python"
**Contrato:** `../contrato-reto/spec.md`
**Fuente de verdad:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` — cotejo 2026-11-05 (objetivos 1-2, líneas 21-22; requisitos BDA líneas 33-36 y requisito Python línea 47; BDA RA1 líneas 72-79; entregable 2 línea 54)

---

## Purpose

Recoger datos reales de vivienda en alquiler en Euskadi mediante **API y
scraping**, más información complementaria (salarios, población e indicadores),
y guardarlos en formato JSON o CSV, todo en Python.

Las fuentes concretas citadas (Eustat, INE, Fotocasa, euskadi.eus, b5m) son
la instancia de este proyecto; el reto exige automatizar una API y un
scraping, no unas fuentes fijas ni un esquema universal.
_Evidencia PDF (sin requisitos nuevos):_ objetivo 1 «Recopilar datos reales
sobre precios de alquiler o compraventa mediante API y web scraping» (PDF
línea 21); objetivo 2 «Obtener información complementaria sobre salarios,
población u otros indicadores que consideréis relevantes» (PDF línea 22);
requisito BDA «Extracción de datos mediante API y scraping» (PDF línea 33) y
«Gestión de datos en formato JSON o CSV» (PDF línea 36); requisito «Todos los
programas desarrollados deberán estar escritos en Python» (PDF línea 47).
Extraído bruto: respuesta original junto con forma parseada (EXTRACCION-01) y
ficheros originales para HDFS (entregable 2, PDF línea 54).

---

## Requirements

### Requirement: EXTRACCION-01 — Automatiza una API y scraping

El sistema SHALL obtener los precios del alquiler automatizando **a la vez**
una API y un scraping, y SHALL guardar la respuesta original junto con la forma
parseada.
_Trazabilidad PDF (cotejo 2026-11-05):_ objetivo 1 (PDF línea 21), requisito
BDA (PDF línea 33) y criterio BDA RA1 Extracción, 10 puntos «Automatiza API y
scraping» (PDF línea 76, tabla líneas 72-79). Extraído bruto: respuesta
original + forma parseada (entregable 2, PDF línea 54, para HDFS).

#### Scenario: La API del proyecto responde datos completos (instancia: Eustat/INE)

- GIVEN la API de Eustat (`bankupx`) y el INE (`wstempus`) en esta instancia
- WHEN se ejecutan los scripts de extracción
- THEN cada tabla se descarga completa y se guarda en `data/raw/`
- AND el número de filas se registra en el log

#### Scenario: El scraping del proyecto produce anuncios reales (instancia: Fotocasa)

- GIVEN las tres provincias (Álava, Bizkaia, Gipuzkoa)
- WHEN se ejecuta el scraper
- THEN se obtienen anuncios únicos con precio, municipio y superficie
- AND el HTML crudo se conserva para poder reparsear sin repetir la descarga

### Requirement: EXTRACCION-02 — No hay fuente única

El sistema SHALL combinar al menos tres fuentes independientes de forma que
ninguna sea insustituible.
_Trazabilidad PDF (cotejo 2026-11-05):_ objetivos 1-2 (PDF líneas 21-22) y
requisito BDA (PDF línea 33). Las tres fuentes son instancia del proyecto
para garantizar datos reales sin fuente única; el PDF exige API y scraping
(2 vías) con fuentes reales, no un número fijo de fuentes.

#### Scenario: Las fuentes son independientes

- GIVEN Eustat, INE, euskadi.eus, b5m y Fotocasa
- WHEN una fuente deja de responder
- THEN las demás siguen aportando datos
- AND el fallo queda registrado sin abortar la extracción completa

### Requirement: FORMATO-01 — JSON o CSV

Todo dato extraído SHALL guardarse en JSON o CSV, con metadatos de fuente,
fecha y número de registros.
_Trazabilidad PDF (cotejo 2026-11-05):_ requisito BDA «Gestión de datos en
formato JSON o CSV» (PDF línea 36).

#### Scenario: Todo dato es JSON o CSV

- GIVEN cualquier fuente del contrato
- WHEN se guarda
- THEN el fichero es JSON o CSV válido
- AND su nombre indica la fuente y el contenido

### Requirement: COMPLEMENTARIOS-01 — Salarios, población y paro Lanbide 252/252 (M5)

El sistema SHALL incluir información complementaria de **salarios**, población
y al menos otro indicador relevante.
_Trazabilidad PDF (cotejo 2026-11-05):_ objetivo 2 «Obtener información
complementaria sobre salarios, población u otros indicadores que consideréis
relevantes» (PDF línea 22). Extraído bruto: salario real (INE EPA /
Observatorio, no simulado) y población municipal con código INE.

El sistema SHALL completar `tasa_paro_lanbide_pct` para los tres municipios que faltaban (01003/20037/48916) ejecutando los extractores Lanbide 18 y 21 y el paso `corregir_empleo`, hasta alcanzar 252/252 municipios. Para el paro municipal SHALL NOT imputar valores comarcales ni IDW: el dato es oficial Lanbide normalizado o es nulo con motivo documentado. `metodo_imputacion` SHALL ser `oficial` y `is_imputed` SHALL ser `false` en el 100 % de las filas de paro.

#### Scenario: El salario está presente y es real

- GIVEN que Eustat no publica salario municipal por edad
- WHEN se incorpora el salario
- THEN proviene del INE (EPA, salario medio por grupo de edad) o del dato
  oficial del Observatorio Vasco de la Juventud
- AND el valor NO se simula ni se inventa

#### Scenario: La población por municipio está disponible

- GIVEN la tabla de población de Eustat
- WHEN se extrae
- THEN cada municipio tiene su población y su código INE

#### Scenario: Paro completo tras extractores 18/21

- GIVEN paro Lanbide en 249/252 municipios con 01003/20037/48916 nulos
- WHEN se ejecuta `python extract/18_lanbide.py && python extract/21_lanbide.py && python transform/corregir_empleo.py`
- THEN `tasa_paro_lanbide_pct` es no nulo en 252/252 municipios
- AND `python -m storage.load_mongo` carga `udalmap` con `is_imputed=false` en paro: salida `252 filas, 252 oficiales, 0 imputadas`

#### Scenario: Municipio sin fuente oficial no inventa paro

- GIVEN un municipio donde Lanbide 18/21 no devuelve registro y no hay normalizado
- WHEN se completa el paro
- THEN `tasa_paro_lanbide_pct=None`, `metodo_imputacion=ninguno`, `is_imputed=false`
- AND `grep -c "is_imputed.*true" data/resultados/udalmap_paro.csv` = 0 (salida: 0)

### Requirement: PYTHON-01 — Todo en Python

Todos los programas SHALL estar escritos en Python y SHALL ser ejecutables
desde un venv dedicado.
_Trazabilidad PDF (cotejo 2026-11-05):_ «Debéis desarrollar una solución
utilizando Python» (PDF línea 19) y «Todos los programas desarrollados
deberán estar escritos en Python» (PDF línea 47).

#### Scenario: Un script reproduce una fuente

- GIVEN un script de extracción
- WHEN se ejecuta con el Python del proyecto
- THEN descarga y guarda los datos
- AND puede repetirse sin romperse

### Requirement: GATE-JOIN-01 — Nueva fuente con join previo

El sistema MUST NOT crear un extractor nuevo sin antes ejecutar un join real contra dim_municipios 252. La validación SHALL contar municipios alcanzados, filas y códigos INE de 5 dígitos. Solo una cobertura documentada alta autoriza el extractor.
_Trazabilidad (cotejo 2026-11-05):_ extensión propia del proyecto (guardia de calidad para nuevas fuentes), sin cita directa en PDF. No es criterio v2 ni peso Tema 8. Se mantiene como guardia de extraído bruto: provenance (fuente, url, fecha, n_registros, sha256) y manifest regenerado.

#### Scenario: Fuente con cobertura insuficiente no entra

- GIVEN una fuente candidata sin join
- WHEN se evalúa su alta
- THEN el sistema la marca baja
- AND no se crea extractor ni carga en Mongo

#### Scenario: Fuente con cobertura alta entra con provenance

- GIVEN una fuente con municipios alcanzados documentados
- WHEN se aprueba el extractor
- THEN el raw guarda fuente, url, fecha, n_registros y sha256
- AND el manifest se regenera

### Requirement: EXTRACCION-03 — Ubicación real desde subtítulo/título (pisos, extensión 2026-11-07)

El sistema SHALL conservar subtítulo y título al extraer (`extract/08_pisos_scraper.py`) con `es_busqueda_no_ubicacion=True`, y SHALL resolver el municipio SOLO por coincidencia textual en subtítulo/título contra variantes de `dim_municipios` + gazetteer barrio→municipio (`transform/muni_resolve.py`). `codigo_ine` SHALL NOT propagarse sin coincidencia textual. Lo no resuelto SHALL ir a fallback detalle o cuarentena (PISOS-02). Sin Docker; HDFS solo raw; Kafka→HDFS, nunca Kafka→Mongo.

_Reconciliación archive (2026-11-07):_ el universo pitch citaba 245 pisos (baseline 187/245 por `municipio_busqueda`). El universo raw real es 263 filas en `anuncios_pisos_dirigido.csv` (235 en enriquecido); tras dedup/filtros/fingerprint el silver `anuncios_unificados.csv` conserva 87 pisos + 45 en `cuarentena_pisos.csv` = 132 trazables. El 0 por `municipio_busqueda` se verifica con `grep -n municipio_busqueda transform/unificar_anuncios.py` (solo línea 64, filtro de validez) y `resolver_codigo(None,'48020')==(None,None)`.

#### Scenario: Pisos re-resueltos con evidencia textual

- GIVEN raw pisos con subtítulo «Piso en Santutxu, Bilbao»
- WHEN se ejecuta `transform/unificar_anuncios.py` (`transform_pisos`)
- THEN `ubicacion.municipio=Bilbao` vía gazetteer y `origen_resolucion=subtitulo`

#### Scenario: Código sin texto no vale

- GIVEN anuncio con `codigo_ine` pero sin municipio en subtítulo/título
- WHEN se resuelve
- THEN no se asigna municipio y pasa a cuarentena motivada

### Requirement: PISOS-01 — Evidencia y orden de resolución

El sistema SHALL aplicar en orden: (1) subtítulo, (2) título, (3) gazetteer, (4) fallback detalle, (5) cuarentena. `municipio_busqueda` SHALL NOT usarse como ubicación en ningún paso.

#### Scenario: Orden verificable

- GIVEN anuncio con subtítulo ambiguo («Santutxu» sin municipio)
- WHEN corre `python transform/unificar_anuncios.py`
- THEN resuelve por gazetteer a Bilbao con `origen_resolucion=gazetteer`
- AND `pytest tests/test_pisos_ubicacion_real.py -q` → `15 passed, 1 skipped` (16 collected; el 245 del delta era conteo pitch, no tests)

### Requirement: PISOS-02 — Cuarentena geo_invalida

El sistema SHALL marcar `geo_invalida=True` y cuarentena reversible a todo piso fuera de `dim_municipios`/Euskadi o sin subtítulo. SHALL NOT tocar Eustat/Lanbide. Raw sigue solo en HDFS; Kafka→HDFS, nunca Kafka→Mongo; sin Docker.

| Caso | Resultado |
|---|---|
| Subtítulo ambiguo | gazetteer o cuarentena, nunca búsqueda |
| Fuera de Euskadi | `geo_invalida=True`, reversible |
| Sin subtítulo | fallback detalle o cuarentena |

#### Scenario: Fuera de Euskadi en cuarentena

- GIVEN subtítulo «Piso en Madrid»
- WHEN se resuelve
- THEN `geo_invalida=True`, excluido de `dim_municipios` y conteos L1/L2
- AND `wc -l data/procesado/cuarentena_pisos.csv` = 46 (45 datos + cabecera, todos `fuera_de_euskadi`)

### Requirement: OUTLIER-01 — Limpieza dura de outliers en extracción (M1)

El sistema SHALL filtrar `precio_m2` al rango [3, 50] €/m² y `superficie_m2` al rango [10, 500] m² en `transform/filtrar_outliers.py` y `transform/generar_anuncios_residencial_filtrado.py`. SHALL excluir del `precio_medio` los valores fuera del rango intercuartílico (IQR) aunque ya estén dentro de [3, 50], y SHALL castear `habitaciones` a entero. `precio_m2` y `superficie_m2` fuera de rango SHALL descartarse con motivo, nunca recortarse ni winsorizarse en esta capa (la winsorización de mediana vive en AGREGACION-01 de `mongodb-y-analisis`). Cada exclusión se SHALL contar por motivo y publicarse en el log de filtrado.

#### Scenario: Filtro de rangos y exclusión IQR

- GIVEN un anuncio con `precio_m2=0,16` y otro con `precio_m2=83,33` y otro con `habitaciones=2,5`
- WHEN corre `python transform/generar_anuncios_residencial_filtrado.py`
- THEN el primero y el segundo se excluyen con motivo `precio_m2_fuera_3_50`, el tercero entra con `habitaciones=2` entero
- AND `python transform/filtrar_outliers.py` emite salida: `excluidos_precio_m2=2, excluidos_superficie=0, excluidos_iqr_precio_medio=N, habitaciones_int=100%`

#### Scenario: Precio dentro de rango pero fuera de IQR no entra en la media

- GIVEN precio `precio_m2` dentro de [3, 50] pero por encima de Q3+1,5·IQR
- WHEN se calcula el precio medio municipal
- THEN esa observación se excluye del precio medio y queda contada como `iqr_excluido`
- AND `grep -c iqr_excluido log_filtrado.txt` ≥ 1 (salida: N ≥ 1)

### Requirement: DEDUP-01 — Dedup dura por `property_fingerprint` (M6)

El sistema SHALL deduplicar en `transform/unificar_anuncios.py` por `property_fingerprint` (generado en `transform/generar_fingerprint.py`): el primer anuncio de cada huella conserva, el resto se descarta con motivo `duplicado_fingerprint`. SHALL NOT sobrevivir ningún duplicado cross-portal en la salida unificada. El conteo de descartados por fingerprint SHALL registrarse en el log y ser verificable con `pytest tests -q`.

#### Scenario: Duplicado cross-portal eliminado

- GIVEN dos anuncios de portales distintos con idéntico `property_fingerprint` (misma vivienda)
- WHEN corre `python transform/unificar_anuncios.py`
- THEN en `data/procesado/anuncios_unificados.csv` hay 1 sola fila con ese fingerprint y el descartado lleva motivo `duplicado_fingerprint`
- AND `python -c "import pandas as pd; d=pd.read_csv('data/procesado/anuncios_unificados.csv'); print(d['property_fingerprint'].duplicated().sum())"` → salida: `0`

#### Scenario: Sin duplicados tras la carga

- GIVEN la salida unificada sin duplicados
- WHEN se carga con `python -m storage.load_mongo`
- THEN `anuncios` en Mongo no contiene dos documentos con el mismo fingerprint
- AND `pytest tests -q` sigue en verde con el test de dedup incluido

### Requirement: VERIFICACION-01 — Gate FAIL 06/07 y huella

El sistema SHALL actualizar `scripts/verificar_fase_datos.py`: el check 06 SHALL esperar `594/843` (`n_anuncios`/`n_anuncios_raw`) en `dim_municipios.csv`, no `759/843`. El check 07 SHALL listar como FAIL conocido los ceros de paro con valor no nulo —Aramaio 0.28, Gaintza 1.45, Usansolo 3.26 (`paro_registrado_cero=True` con `tasa_paro_lanbide_pct` no nulo)— y SHALL NOT enmascararlos como PASS. Cuando el resto de checks alcanza PASS, el gate SHALL emitir huella verificable (SHA-256 de los artefactos comprobados) e imprimir `RESULTADO` distinguiendo PENDIENTE de OK mientras persista el FAIL conocido.

Guardarraíles: sin Docker; HDFS solo raw 352; Kafka→HDFS, nunca Kafka→Mongo; sin imputar comarcal/IDW como municipal.

_Reconciliación archive (2026-11-07):_ check 17 alias verificado: `354 ingestion local; 352 raw en HDFS` — conteo local de ingestión (354) distinto del canónico HDFS raw (352). Puerta final: 06 PASS `594/843 real=594`, 07 FAIL conocido con los 3 ceros (no enmascarados, sin imputación), huella SHA-256 reproducible impresa (ver archive-report).

#### Scenario: FAIL 06 con verdad v5

- GIVEN `dim_municipios.csv` con sumas 594/843
- WHEN corre `python scripts/verificar_fase_datos.py`
- THEN el check se nombra `06 n_anuncios 594/843`, PASS con `real=594`
- AND `grep -c "759/843" scripts/verificar_fase_datos.py` → `0`

#### Scenario: FAIL 07 lista los ceros conocidos

- GIVEN `udalmap_empleo_corregido.csv` con Aramaio 0.28, Gaintza 1.45, Usansolo 3.26
- WHEN corre el gate
- THEN `FAIL 07` los nombra como casos conocidos
- AND ningún caso figura como PASS ni se imputa valor comarcal

#### Scenario: PASS genera huella

- GIVEN todos los demás checks en PASS
- WHEN termina el gate
- THEN imprime `RESULTADO` y huella SHA-256 reproducible de los artefactos verificados

---

## Evidencia PDF (objetivos, requisitos, extraído bruto — sin SHALL nuevos)
- **Objetivo 1** (PDF línea 21): «Recopilar datos reales sobre precios de
  alquiler o compraventa mediante API y web scraping». Evidencia para
  EXTRACCION-01 y EXTRACCION-02.
- **Objetivo 2** (PDF línea 22): «Obtener información complementaria sobre
  salarios, población u otros indicadores que consideréis relevantes».
  Evidencia para COMPLEMENTARIOS-01.
- **Requisitos BDA** (PDF líneas 33-36): «Extracción de datos mediante API y
  scraping» (PDF línea 33) y «Gestión de datos en formato JSON o CSV»
  (PDF línea 36). Evidencia para EXTRACCION-01 y FORMATO-01.
- **Requisito Python** (PDF línea 47): «Todos los programas desarrollados
  deberán estar escritos en Python» (con PDF línea 19). Evidencia para
  PYTHON-01.
- **Extraído bruto**: respuesta original + forma parseada (EXTRACCION-01) y
  ficheros originales para HDFS (entregable 2, PDF línea 54). GATE-JOIN-01
  garantiza provenance y cobertura previa al extraído bruto nuevo.
- **Nota de fuentes**: las fuentes concretas citadas (Eustat, INE, Fotocasa,
  euskadi.eus, b5m) son la instancia de este proyecto; el reto exige
  automatizar una API y un scraping con datos reales, no unas fuentes fijas
  ni un esquema universal. Se mantiene la nota original del Purpose.

## Mapa trazable PDF → requisito
| Requisito | PDF (líneas) | Criterio rubric / evidencia | Estado (2026-11-05) |
|---|---|---|---|
| EXTRACCION-01 | Objetivo 1 línea 21; requisito BDA línea 33; BDA RA1 línea 76 (líneas 72-79); entregable 2 línea 54 | BDA RA1 Extracción 10 pts «Automatiza API y scraping»; extraído bruto (original + parseada) | SHALL acreditado; fuentes = instancia (Eustat/INE API, Fotocasa scraping). |
| EXTRACCION-02 | Objetivos 1-2 líneas 21-22; requisito BDA línea 33 | Sin fuente única: 3+ fuentes independientes (instancia del proyecto) | SHALL acreditado (5 fuentes reales); el PDF no fija número de fuentes. |
| FORMATO-01 | Requisito BDA línea 36 | «Gestión de datos en formato JSON o CSV» | SHALL acreditado: JSON/CSV con fuente, fecha y n_registros. |
| COMPLEMENTARIOS-01 | Objetivo 2 línea 22 | «Obtener información complementaria sobre salarios, población u otros indicadores» | SHALL acreditado: salarios reales (INE EPA / Observatorio), población municipal con código INE. |
| PYTHON-01 | Líneas 19 y 47 | «Utilizando Python» / «Todos los programas ... escritos en Python» | SHALL acreditado: scripts Python en venv dedicado. |
| GATE-JOIN-01 | Sin cita directa PDF | Extensión propia: join previo contra dim_municipios 252 + provenance | Guardia de calidad (MUST NOT); no es criterio v2 ni peso Tema 8. |
