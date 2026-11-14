<!-- cap: 7 | titulo: Dificultades y decisiones | criterios: Todos | estado: borrador -->
# 7. Dificultades y decisiones

> El capítulo anticipa las preguntas difíciles: qué falló, qué se decidió y qué coste tiene cada decisión.

## 7.1 Tabla de decisiones

| Dificultad | Decisión | Evidencia | Coste declarado |
|---|---|---|---|
| Solo {{datos.anuncios_municipios}} de {{datos.municipios}} municipios tienen anuncio y {{datos.precio_observable}} tienen precio | Ranking principal con alquiler oficial; anuncios como capa aparte | `mongo_esfuerzo_por_municipio.csv` | No se rankean 252 municipios |
| {{datos.precio_observable}} municipios con precio, pero solo {{datos.n_precio_positivo}} con `n_precio > 0` | Gating Tier A/B; en C/D el precio queda a nulo por diseño | `pipeline_tier_por_municipio` | {{datos.precio_sin_muestra}} municipios con precio no publican estadística |
| No hay salario juvenil municipal | Renta media como proxy, declarada | `renta_joven_18_34` | Falacia ecológica posible |
| Anuncios 2026 y renta/alquiler 2024 | Dos capas separadas, sin resta | `M26_*` y `mongo_*` | No hay serie temporal |
| {{raw.disco}} ficheros en disco, {{raw.manifest}} en manifiesto y {{infra.hdfs_objetos}} en HDFS | Tres inventarios con propósito distinto | manifiestos y `GETCONTENTSUMMARY` | Hay que explicar la diferencia |
| HDFS solo conserva raw | Requisito del alcance del reto | brief del reto | Silver y gold no están en HDFS |
| El `OPEN` de HDFS falló por DNS del datanode el 12-11 | Recuperación por SHA y verificación fechada | `hdfs_recuperacion_un_fichero.py` | El 13-11 devuelve `HDFS_REC OK`; el estado puede cambiar |
| Kafka no entregaba metadata el 12-11 | Evidencia v8 y tests offline; no se afirma revalidación | `KafkaAdminClient` y tests | El 13-11 el topic responde; se fecha |
| El topic antiguo `anuncios_inmobiliarios` sigue existiendo | No se borra: el clúster es compartido y sería destructivo | `describe_topics` | 1.420 mensajes de prueba conviven con el topic vigente |
| Dos colecciones de habitaciones con {{mongo.habitaciones}} documentos cada una | Se declara la deuda; no se borra sin confirmar | `_facts.json` | Duplicado silencioso si no se documenta |
| {{datos.vpo_sin_dato}} de {{datos.vpo_promociones}} promociones sin `NumViviendas` | VPO como flujo, no como stock | `etxebide_promociones` | No se puede contar viviendas disponibles |
| Dos índices 2026 definidos pero no creados | Se declaran; no se crean en una demo sin ventana | `mongo_indexes.py` | El pipeline 2026 no está optimizado |
| Falta `auditoria_lagunas_silver.csv` | No se regenera para no mover el gold de 53 a 54 | `transform/run_all.py --check` | Queda una comprobación en rojo |

## 7.2 Cobertura y proxy

La cobertura es la dificultad principal. Un municipio sin anuncio no es un municipio barato: es un municipio sin evidencia. La renta media tampoco es el salario de una persona joven; se usa porque es el dato municipal disponible y se declara como proxy.

El precio medio se calcula para {{datos.precio_observable}} municipios, pero solo {{datos.n_precio_positivo}} lo publican con muestra. Los {{datos.precio_sin_muestra}} restantes son Tier C/D: el pipeline les pone `n_precio = 0` y deja mínimo, máximo y mediana a nulo. La regla evita presentar una mediana de dos anuncios como precio municipal.

## 7.3 Infraestructura

El estado del clúster cambió durante el proyecto. El 12-11 el `OPEN` de HDFS fallaba por DNS del datanode y Kafka no entregaba metadata; el 13-11 la recuperación por SHA devuelve `HDFS_REC OK SHA_TAMANO_IGUALES` y el topic responde con una partición y factor de replicación 1. Cada comprobación lleva su fecha; una avería de red no se convierte en una afirmación sobre el código.

## 7.4 Deuda declarada

Quedan cinco deudas: dos índices 2026 sin crear, dos colecciones de habitaciones duplicadas, un topic legacy, un pipeline fuera del orden principal y una comprobación de silver en rojo. Ninguna impide responder a la pregunta, pero todas cambian lo que se puede afirmar sobre rendimiento y consistencia.
