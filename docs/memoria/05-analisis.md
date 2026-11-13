<!-- cap: 5 | titulo: Análisis e indicadores | criterios: C11, C12, C13, C16 | estado: borrador -->
# 5. Análisis e indicadores

> **Objetivo.** Explicar qué se calcula, con qué etapas de agregación y cómo se comprueba que el índice se usa.

## 5.1 Los cinco indicadores

| Indicador | Qué mide | Fuentes |
|---|---|---|
| Esfuerzo joven | Porcentaje de renta destinado a alquiler | Renta, alquiler oficial, anuncios |
| Tier de confianza | Cuánta evidencia sostiene el dato municipal | Cobertura y tamaño de muestra |
| Modalidad | Larga estancia frente a temporal | Anuncios |
| VPO | Promociones protegidas por estado | Etxebide |
| Habitaciones | Oferta de habitaciones y precio | Anuncios |

Cada indicador tiene fórmula, fuente y límite documentados. El esfuerzo es el principal; los demás explican por qué un municipio no se puede rankear con la misma confianza que otro.

## 5.2 Pipelines

Hay {{mongo.pipelines}} pipelines en orden y {{mongo.pipelines_fuera_orden}} fuera del orden principal, {{mongo.pipelines_total}} en total. Los pipelines escriben {{mongo.csv_salidas}} CSV en gold. El orden importa: un pipeline que depende de otro no puede ejecutarse antes.

Las etapas usadas incluyen `$match`, `$group`, `$lookup`, `$unwind`, `$project`, `$sort` y `$facet`. `$lookup` cruza anuncios con municipios; `$unwind` abre los arrays de equipamiento e histórico; `$facet` permite varias salidas en una sola pasada.

## 5.3 Consultas

Las consultas cubren igualdad, comparación, operadores lógicos, proyección, ordenación, arrays y campos anidados. Dos ejemplos del reto: municipios con esfuerzo superior al 30 % y más de un anuncio; anuncios de larga estancia en un territorio con precio por metro cuadrado por debajo de la mediana.

## 5.4 Índices y `explain`

La comprobación es explícita: se ejecuta la consulta sin índice y con índice, y se comparan `COLLSCAN` frente a `IXSCAN` y `totalDocsExamined`. El capítulo 8 recoge el comando. La conclusión no es “hay un índice”, sino “el índice reduce los documentos examinados para esta consulta concreta”.
