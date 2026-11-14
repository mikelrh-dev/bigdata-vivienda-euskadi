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

## 5.2 Los proxys, uno a uno

El indicador necesita dos números que no están publicados: lo que gana una persona joven en cada municipio y el alquiler donde Eustat no publica. Los dos se construyen, y cómo se construyen forma parte del resultado.

| Proxy | Cómo se construye | Fuente | Qué se pierde |
|---|---|---|---|
| Renta joven 18-34 | renta neta media por hogar × {{metodo.ratio_18_34_pct}} %, el ratio 18-34 de la CAE ponderado por la anchura de cada tramo (dos años para 18-19 y cinco para cada uno de los tres siguientes) | INE Atlas de la Renta 2024 y Eustat renta por edad | es renta de hogar, no salario individual; el ratio es autonómico |
| Salario de 2026 | salario neto joven de 2024 que publica el OVJ, actualizado con el IPC medio del INE ({{metodo.ipc_2024}} en 2024 y {{metodo.ipc_2026}} en 2026), que deja {{metodo.salario_2026}} € al mes | OVJ (Irekia) e INE | constante autonómica: no permite ordenar municipios por salario |
| Alquiler de los 93 | IDW con los {{metodo.idw_vecinos}} municipios oficiales más cercanos y peso 1/d², con d haversine entre centroides | Eustat alquiler y centroides municipales | no es precio observado: nunca entra en la conclusión |
| Accesibilidad | minutos de conducción reales a la capital, municipio a municipio | OSRM sobre OpenStreetMap | no mide transporte público ni el viaje real de cada persona |

La renta municipal está completa en los {{datos.municipios}} municipios, con renta de hogar del Atlas del INE y renta personal de Eustat en la misma fila. El denominador del esfuerzo es siempre renta de hogar por ratio, nunca renta personal: las dos familias que calcula el pipeline —la fiscal, sobre renta personal, y la salarial— quedan en el CSV como columnas de contraste y no alimentan el indicador canónico.

El salario, en cambio, es una sola cifra para toda la comunidad. Por eso el orden municipal lo mueve la renta y no el salario, y por eso el escalón entre los municipios industriales de la ría y los de renta alta se lee con la renta: el salario es el mismo en Sestao y en Getxo.

El alquiler imputado existe para medir cuánto depende el resultado de él, no para publicarlo: con los 252 municipios la mediana del esfuerzo es {{datos.esfuerzo_mediana_idw}} % y con los {{datos.alquiler_oficial}} oficiales, {{datos.esfuerzo_mediana_oficial}} %. La cifra que se defiende es siempre la segunda.

Los minutos a la capital no se interpolan: se piden a OSRM para cada municipio y se guardan con el resto de la capa. La distancia en línea recta solo se usa en el IDW, donde lo que importa es la proximidad y no el viaje.

## 5.3 Pipelines

Hay {{mongo.pipelines}} pipelines en orden y {{mongo.pipelines_fuera_orden}} fuera del orden principal, {{mongo.pipelines_total}} en total. Los pipelines escriben {{mongo.csv_salidas}} CSV en gold. El orden importa: un pipeline que depende de otro no puede ejecutarse antes.

Las etapas usadas en el código son `$match` (16), `$lookup` (17), `$unwind` (5), `$group` (4), `$project` (12), `$sort` (12), `$limit` (12) y `$addFields` (34). `$lookup` cruza anuncios con municipios; `$unwind` abre los arrays de equipamiento e histórico; `$group` resume por municipio. No se usa `$facet`: no hace falta para las preguntas del reto y añadiría una etapa que el código no necesita.

## 5.4 Un pipeline, paso a paso

`pipeline_indicadores_municipio` empieza en `municipios` ({{datos.municipios}} documentos), hace `$lookup` a `anuncios` por `ubicacion.codigo_ine`, filtra anuncios con `precio_m2` válido y superficie entre 10 y 500 m², ordena los precios por m² y calcula la mediana winsorizada al percentil 1–99. El `precio_medio_eur` excluye los valores fuera de 1,5·IQR por municipio. La mediana cruda no se usa para conclusiones.

`pipeline_tier_por_municipio` deriva el tier solo de `n_anuncios`: A ≥30, B 10–29, C 1–9, D 0. En C y D, `n_precio`, mínimo, máximo y mediana se ponen a cero o nulo por diseño: hay precio, pero no muestra suficiente para publicarlo como estadística municipal.

## 5.5 Índices y `explain`

La comprobación es explícita. El filtro es `ubicacion.codigo_ine = "20069"`, `modalidad = "larga_estancia"` y `precio_eur ≤ 1000`. Antes, forzando `hint={"$natural": 1}`, el plan es `COLLSCAN`: 1 documento devuelto y 594 examinados. Después, con el índice ESR, es `IXSCAN`: 1 documento devuelto, 1 examinado y 1 clave leída. El índice evita examinar 593 documentos que no cumplen el filtro.

El mismo patrón se aplica a `etxebide_promociones` con `explain_promo_before_after("48020")`. El comando es `python analysis/mongo_indexes.py` y es de solo lectura.
