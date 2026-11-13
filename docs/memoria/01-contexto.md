<!-- cap: 1 | titulo: Contexto y pregunta | criterios: C17, C18 | estado: borrador -->
# 1. Contexto y pregunta

> **Objetivo.** Delimitar la pregunta, la unidad de análisis y las dos capas de datos que el proyecto mantiene separadas.

## 1.1 El reto

La pregunta de partida es si una persona joven puede independizarse en Euskadi con su salario. El proyecto la traduce a un indicador comparable: el porcentaje de la renta joven que se consume en alquiler. Un municipio es una respuesta mejor cuanto menor es ese esfuerzo, pero solo si el dato existe y es comparable con el de los demás.

La respuesta no es un listado de municipios baratos. Es una lectura territorial del esfuerzo, con tres cautelas: la renta es un proxy, el alquiler oficial no cubre todos los municipios y la oferta de anuncios no representa el parque completo.

## 1.2 La unidad de análisis

Todo el pipeline converge en el código INE de cinco dígitos. Es la clave natural de `municipios`, el nexo con los anuncios y la unidad de los {{datos.municipios}} municipios de Euskadi. Usar una sola clave evita el problema clásico de los cruces por nombre: dos municipios con el mismo topónimo en territorios distintos, o un nombre con tilde frente a otro sin ella.

## 1.3 Dos capas que no se restan

La capa 2024 mide esfuerzo con alquiler oficial en {{datos.alquiler_oficial}} municipios y se completa por interpolación (IDW) en los {{datos.alquiler_imputado}} restantes. La capa 2026 mide oferta de mercado con {{datos.anuncios_total}} anuncios. Son dos fotografías con fuentes distintas y no forman una serie temporal: se presentan por separado y no se restan.

## 1.4 Qué no responde el proyecto

No estima el salario municipal de la población joven, no mide la calidad de la vivienda y no sustituye un trabajo de campo. Cuando el dato no existe, el documento lo declara; no rellena el hueco con una estimación presentada como observación.
