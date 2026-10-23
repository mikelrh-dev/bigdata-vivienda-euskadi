# Presentación de resultados — Especificación

**Capacidad:** `presentacion-de-resultados`
**Estado:** Pendiente
**Criterios cubiertos:** SBD-RA4 Gráficos (10), Datos utilizados (10),
Presentación (10), Interpretación (10), resultado final del reto
**Contrato:** `../contrato-reto/spec.md`

---

## Purpose

Presentar los resultados con gráficos adecuados a los datos, generados
directamente desde consultas PyMongo, con títulos, unidades y leyendas, que
faciliten comparar municipios y permitan concluir cuáles ofrecen mejores
posibilidades de emancipación y por qué.

---

## Requirements

### Requirement: GRAFICOS-01 — Tres tipos adecuados a los datos

El sistema SHALL presentar al menos tres tipos de gráfico, cada uno adecuado al
tipo de dato que representa.

#### Scenario: Cada tipo encaja con su dato

- GIVEN datos categóricos y datos continuos
- WHEN se eligen los gráficos
- THEN un ranking usa barras
- AND una relación entre dos variables usa dispersión
- AND una distribución usa caja y bigotes
- AND una variable geográfica usa mapa

### Requirement: DATOS-PYMONGO-01 — Gráficos desde consultas PyMongo

Cada gráfico SHALL generarse directamente a partir de una consulta PyMongo,
nunca con valores tecleados.

#### Scenario: El dato llega del pipeline

- GIVEN una agregación sobre MongoDB
- WHEN se genera un gráfico
- THEN sus valores salen del resultado de la consulta
- AND no hay ningún número escrito a mano en el código del gráfico

#### Scenario: Repetir reproduce

- GIVEN los mismos datos
- WHEN se regenera el gráfico
- THEN el resultado es idéntico

### Requirement: PRESENTACION-01 — Títulos, unidades, leyendas, comparación

Cada gráfico SHALL llevar título, unidades y leyendas cuando proceda, y SHALL
facilitar la comparación entre municipios.

#### Scenario: El gráfico se entiende solo

- GIVEN un gráfico en el informe
- WHEN se lee sin contexto
- THEN tiene título, eje con unidades y leyenda
- AND permite comparar dos municipios cualesquiera

### Requirement: INTERPRETACION-01 — Relaciona y explica

El informe SHALL explicar al menos tres resultados relevantes y SHALL relacionar
los resultados con sus implicaciones.

#### Scenario: Se explican resultados, no solo se describen

- GIVEN los indicadores calculados
- WHEN se redacta el informe
- THEN al menos tres hallazgos se explican con su causa
- AND se indica su implicación

### Requirement: CONCLUSION-01 — Municipios y por qué, con datos

El sistema SHALL concluir qué municipios ofrecen mejores posibilidades de
emancipación para una persona joven, y SHALL explicar por qué, respaldándose en
los datos analizados.

#### Scenario: La conclusión cita el dato

- GIVEN el ranking calculado
- WHEN se escribe la conclusión
- THEN nombra municipios concretos
- AND cada afirmación se respalda en un indicador calculado
- AND se explica el porqué

#### Scenario: La conclusión no exagera

- GIVEN un municipio con pocos anuncios
- WHEN aparece en el ranking
- THEN se advierte la limitación del tamaño de muestra
