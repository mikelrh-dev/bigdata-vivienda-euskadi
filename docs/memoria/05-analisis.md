<!-- cap: 5 | titulo: Análisis e indicadores | criterios: C11, C12, C13, C16 | estado: borrador -->
# 5. Análisis e indicadores

> El capítulo explica qué se calcula, con qué etapas de agregación y cómo se comprueba que el índice se usa.

## 5.1 Los cinco indicadores

| Indicador | Qué mide | Fuentes |
|---|---|---|
| Esfuerzo joven | Porcentaje de renta destinado a alquiler | Renta, alquiler oficial, anuncios |
| Tier de confianza | Cuánta evidencia sostiene el dato municipal | Cobertura y muestra |
| Modalidad | Larga estancia frente a temporal | Anuncios |
| VPO | Promociones protegidas por estado | Etxebide |
| Habitaciones | Oferta de habitaciones y precio | Anuncios |

Cada indicador tiene fórmula, fuente y límite documentados. El esfuerzo es el principal; los demás explican por qué un municipio no se puede rankear con la misma confianza que otro.

## 5.2 Pipelines

Hay {{mongo.pipelines}} pipelines en orden y {{mongo.pipelines_fuera_orden}} fuera del orden principal, {{mongo.pipelines_total}} en total. Los pipelines escriben {{mongo.csv_salidas}} CSV en gold. El orden importa: un pipeline que depende de otro no puede ejecutarse antes.

Las etapas usadas en el código son `$match` (16), `$lookup` (17), `$unwind` (5), `$group` (4), `$project` (12), `$sort` (12) y `$addFields` (34). `$lookup` cruza anuncios con municipios; `$unwind` abre los arrays de equipamiento e histórico; `$group` resume por municipio. No se usa `$facet`: no hace falta para las preguntas del reto y añadiría una etapa que el código no necesita.

## 5.3 Un pipeline, paso a paso

`pipeline_indicadores_municipio` empieza en `municipios` ({{datos.municipios}} documentos), hace `$lookup` a `anuncios` por `ubicacion.codigo_ine`, filtra anuncios con `precio_m2` válido y superficie entre 10 y 500 m², ordena los precios por m² y calcula la mediana winsorizada al percentil 1–99. El `precio_medio_eur` excluye los valores fuera de 1,5·IQR por municipio. La mediana cruda no se usa para conclusiones.

`pipeline_tier_por_municipio` deriva el tier solo de `n_anuncios`: A ≥30, B 10–29, C 1–9, D 0. En C y D, `n_precio`, mínimo, máximo y mediana se ponen a cero o nulo por diseño: hay precio, pero no muestra suficiente para publicarlo como estadística municipal.

## 5.4 Índices y `explain`

La comprobación es explícita. El filtro es `ubicacion.codigo_ine = "20069"`, `modalidad = "larga_estancia"` y `precio_eur ≤ 1000`. Antes, forzando `hint={"$natural": 1}`, el plan es `COLLSCAN`: 1 documento devuelto y 594 examinados. Después, con el índice ESR, es `IXSCAN`: 1 documento devuelto, 1 examinado y 1 clave leída. El índice evita examinar 593 documentos que no cumplen el filtro.

El mismo patrón se aplica a `etxebide_promociones` con `explain_promo_before_after("48020")`. El comando es `python analysis/mongo_indexes.py` y es de solo lectura.
