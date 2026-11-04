# Presentación de resultados — Especificación

**Capacidad:** `presentacion-de-resultados`
**Estado:** Hecho, alineado con RA4 v2
**Criterios cubiertos:** rúbrica v2 SBD-RA4 Procesamiento, análisis y
preparación de resultados (datos heterogéneos, automatización del análisis,
indicadores, respuesta al reto, preparación para visualización)
**Contrato:** `../contrato-reto/spec.md`

---

## Purpose

Procesar datos heterogéneos procedentes de 2 o más fuentes, ejecutar
automáticamente los análisis principales con PyMongo, calcular indicadores
de vivienda y emancipación, preparar automáticamente conjuntos de resultados
para su representación, y responder a la pregunta del reto comparando
municipios con conclusiones vinculadas a indicadores calculados en MongoDB.

---

## Requirements

### Requirement: DATOS-HETEROGENEOS-01 — Datos heterogéneos

El sistema SHALL integrar datos procedentes de fuentes con estructuras
diferentes y SHALL adaptarlos mediante Python/PyMongo (nivel 10 de la rúbrica
v2). Para el nivel 7, SHALL utilizar al menos arrays, documentos anidados o
datos con estructuras diferentes.

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

### Requirement: INDICADORES-01 — Cinco indicadores con 2 o más fuentes

El sistema SHALL calcular al menos 3 indicadores relacionados con
vivienda/emancipación (nivel 7 de la rúbrica v2) y, para el nivel 10, SHALL
calcular al menos 5 indicadores combinando información procedente de 2 o más
fuentes.

#### Scenario: Al menos 3 indicadores — nivel 7

- GIVEN los datos de vivienda y emancipación cargados
- WHEN se calculan los indicadores
- THEN existen al menos 3 indicadores definidos y calculados

#### Scenario: Al menos 5 indicadores con 2 o más fuentes — nivel 10

- GIVEN al menos 2 fuentes de datos diferentes
- WHEN se calculan los indicadores
- THEN existen al menos 5 indicadores
- AND cada indicador combina información de al menos 2 fuentes
- AND cada indicador es reproducible desde MongoDB

### Requirement: PREPARACION-VISUALIZACION-01 — Tres conjuntos automáticos para representar

El sistema SHALL generar mediante PyMongo datos utilizables para gráficos
(nivel 7 de la rúbrica v2) y, para el nivel 10, SHALL generar
automáticamente mediante PyMongo al menos 3 conjuntos de resultados
diferentes preparados para representar. Los valores SHALL proceder de
consultas PyMongo, nunca de números tecleados a mano.

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

### Requirement: CONCLUSION-01 — Respuesta al reto: 3 municipios vinculados a indicadores

El sistema SHALL obtener conclusiones para al menos 2 municipios o zonas
(nivel 7 de la rúbrica v2) y, para el nivel 10, SHALL comparar al menos 3
municipios o zonas, con cada conclusión vinculada a un indicador calculado con
MongoDB. SHALL explicar por qué cada municipio ofrece mejores o peores
posibilidades de emancipación para una persona joven, respaldándose en los
datos analizados.

#### Scenario: Conclusiones para 2 municipios — nivel 7

- GIVEN los indicadores calculados
- WHEN se redacta la conclusión
- THEN se obtienen conclusiones para al menos 2 municipios o zonas

#### Scenario: Comparación de 3 municipios vinculada a indicadores — nivel 10

- GIVEN los indicadores calculados con MongoDB
- WHEN se redacta la conclusión
- THEN se comparan al menos 3 municipios o zonas
- AND cada conclusión está vinculada a un indicador calculado con MongoDB
- AND cada afirmación cita el indicador y su valor
- AND se explica el porqué

#### Scenario: La conclusión no exagera

- GIVEN un municipio con pocos anuncios
- WHEN aparece en la comparación
- THEN se advierte la limitación del tamaño de muestra
