<!-- cap: 7 | titulo: Dificultades y decisiones | criterios: Todos | estado: borrador -->
# 7. Dificultades y decisiones

> **Objetivo.** Anticipar las preguntas difíciles: qué falló, qué se decidió y qué coste tiene cada decisión.

## 7.1 Tabla de decisiones

| Dificultad | Decisión | Evidencia | Coste declarado |
|---|---|---|---|
| Solo {{datos.anuncios_municipios}} de {{datos.municipios}} municipios tienen anuncio y {{datos.precio_observable}} tienen precio | Ranking principal con alquiler oficial; anuncios como capa aparte | `mongo_esfuerzo_por_municipio.csv` | No se rankean 252 municipios |
| No hay salario juvenil municipal | Renta media como proxy, declarada | `renta_joven_18_34` | Falacia ecológica posible |
| Anuncios 2026 y renta/alquiler 2024 | Dos capas separadas, sin resta | `M26_*` y `mongo_*` | No hay serie temporal |
| {{datos.precio_observable}} municipios con precio medio, pero solo 7 con `n_precio > 0` | Gating por Tier C/D; `n_precio` se interpreta como muestra mínima | `mongo_tier_confianza.csv` | El precio medio no es comparable en todos |
| {{raw.disco}} ficheros en disco, {{raw.manifest}} en manifiesto y {{infra.hdfs_objetos}} en HDFS | Tres inventarios con propósito distinto | manifiestos y `GETCONTENTSUMMARY` | Hay que explicar la diferencia |
| HDFS solo conserva raw | Excepción expresa de la profesora | brief del reto | Silver y gold no están en HDFS |
| El `OPEN` de HDFS falló por DNS del datanode | Recuperación por SHA en local; se fecha la verificación | `hdfs_recuperacion_un_fichero.py` | El estado del clúster puede cambiar |
| El topic antiguo `anuncios_inmobiliarios` sigue existiendo | No se borra: el clúster es compartido y sería destructivo | `describe_topics` | 1.420 mensajes de prueba conviven con el topic vigente |
| Dos colecciones de habitaciones con {{mongo.habitaciones}} documentos cada una | Se declara la deuda; no se borra sin confirmar | `_facts.json` | Duplicado silencioso si no se documenta |
| {{datos.vpo_sin_dato}} de {{datos.vpo_promociones}} promociones sin `NumViviendas` | VPO como flujo, no como stock | `etxebide_promociones` | No se puede contar viviendas disponibles |

## 7.2 Cobertura y proxy

La cobertura es la dificultad principal. Un municipio sin anuncio no es un municipio barato: es un municipio sin evidencia. La renta media tampoco es el salario de una persona joven; se usa porque es el dato municipal disponible y se declara como proxy.

## 7.3 Infraestructura

El estado del clúster cambió durante el proyecto. Lo que un día fallaba por DNS del datanode hoy responde a la recuperación por SHA; lo que se afirma en el documento lleva fecha. La regla es no presentar como revalidado hoy lo que se verificó ayer.

## 7.4 Deuda declarada

La deuda no se esconde: dos índices 2026 sin crear, dos colecciones de habitaciones duplicadas, un topic legacy y un pipeline fuera del orden principal. Ninguna de esas deudas impide responder a la pregunta, pero todas cambian lo que se puede afirmar sobre rendimiento y consistencia.
