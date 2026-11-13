<!-- cap: 2 | titulo: Arquitectura de datos | criterios: C1, C2, C3, C4 | estado: borrador -->
# 2. Arquitectura de datos

> **Objetivo.** Explicar el recorrido del dato desde la fuente hasta el análisis y por qué hay dos ramas sobre los mismos originales.

## 2.1 Dos ramas sobre los mismos ficheros

El sistema tiene una rama de conservación y una rama analítica. La primera copia los originales a HDFS y simula la llegada de anuncios con Kafka. La segunda limpia, cruza y carga en MongoDB para analizar. Las dos parten del mismo raw inmutable: ningún dato se corrige antes de conservarse.

La separación es deliberada. Si la transformación cambia, el original sigue disponible para reprocesar; si el clúster falla, el análisis puede continuar en local. Esa es la diferencia entre un pipeline reproducible y una secuencia de scripts que se pisan.

## 2.2 Cinco capas

| Capa | Qué contiene | Dónde vive |
|---|---|---|
| Fuentes | API y scraping de 13 familias de datos | `extract/` |
| Raw | Original inmutable con SHA-256 y `.FROZEN` | `data/raw/` |
| Silver | CSV normalizados a `codigo_ine` | `data/procesado/` |
| MongoDB | Colecciones de análisis y pipelines | `vivienda_euskadi` |
| Gold | CSV y PNG listos para el informe | `data/resultados/` |

El manifiesto de raw tiene {{raw.manifest}} entradas; en disco hay {{raw.disco}} ficheros, de los que {{raw.visibles}} son visibles. HDFS conserva {{infra.hdfs_objetos}} objetos. Las tres cifras no son intercambiables y se explican en el capítulo 7.

## 2.3 La rama de conservación

El productor lee el manifiesto SHA, publica en el topic `{{infra.kafka_topic}}` y el consumidor escribe en HDFS. El topic tiene {{infra.kafka_particiones}} partición y factor de replicación {{infra.kafka_factor_replicacion}}. La recuperación se demuestra pidiendo un fichero por su SHA y comparando tamaño y hash.

## 2.4 La rama analítica

Silver se carga en {{mongo.vivas}} colecciones vivas con `replace_collection`, de forma que una recarga no duplica documentos. Los pipelines de agregación calculan los indicadores y escriben {{mongo.csv_salidas}} CSV en gold. El resultado final son {{gold.artefactos}} artefactos ({{gold.csv}} CSV y {{gold.png}} PNG).

## 2.5 Una excepción declarada: HDFS solo raw

HDFS conserva los originales, no silver ni gold. Es una decisión expresa de la profesora y el documento la presenta como excepción, no como olvido. La consecuencia es que la reproducibilidad del análisis se apoya en el manifiesto y en los scripts, no en una copia distribuida de los intermedios.

<!-- Figura 2.1: diagrama de dos ramas y cinco capas. Se genera en HTML/CSS y se rasteriza con Chrome. -->
