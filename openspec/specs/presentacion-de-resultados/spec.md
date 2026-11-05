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

### Requirement: INDICADORES-01 — Cinco indicadores con pipeline Mongo verdadero o silver justificado

El sistema SHALL calcular 5 indicadores con pipeline Mongo verdadero para
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
- WHEN se resumen los resultados en `docs/matriz_indicadores.md`
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

El sistema SHALL redactar en `docs/guion_defensa.md` un guion Tema 8 de 1
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

- GIVEN `docs/guion_defensa.md`
- WHEN se revisa el guion Tema 8
- THEN tiene 1 página con embedding, índices, atomicidad y HDFS centro + Kafka pid 1832
- AND constan los 10 criterios y las lagunas documentadas

#### Scenario: 16-29 marcado legacy

- GIVEN el guion Tema 8 y la matriz O1-O4
- WHEN aparece el rango 16-29
- THEN está marcado legacy y el canónico es 18-34
- AND ninguna conclusión usa 16-29 como rango canónico

### Requirement: RESPUESTA-01 — Respuesta comparativa de 4 robustos con matriz O1-O4

El sistema SHALL compare 4 municipios robustos —Bilbao 173, Donostia 113,
Getxo 40, Vitoria-Gasteiz 39 anuncios— con paro Lanbide no nulo o silver
justificado, y SHALL documentar la matriz O1-O4 en
`docs/conclusiones_municipios.md` con mediana 26,61 (oficial 18-34) y 25,2%
sobre 30. La matriz SHALL advertir que Getxo 40 vs Vitoria-Gasteiz 39 difiere
en 1 anuncio y MUST NOT leerse como ranking firme entre esos dos. La
comparativa SHALL registrarse en `docs/trazabilidad_vm.md` (Fecha/Objetivo/
Máquina/Comando/Salida/Conclusión) y MUST NOT tocar `data/raw` ni raw HDFS,
ni crear carpeta nueva, ni subir procesado.

#### Scenario: Cuatro robustos con paro no nulo

- GIVEN los 4 robustos Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39
- WHEN se genera la comparativa en `docs/conclusiones_municipios.md`
- THEN el paro Lanbide no es nulo o consta justificación silver
- AND la salida está trazada en `docs/trazabilidad_vm.md`

#### Scenario: Matriz O1-O4 con advertencia Getxo/Vitoria

- GIVEN la matriz O1-O4 con mediana 26,61 y 25,2% sobre 30
- WHEN se lee la comparación Getxo 40 vs Vitoria-Gasteiz 39
- THEN figura la advertencia de 1 anuncio de diferencia
- AND NO se presenta como ranking firme

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
