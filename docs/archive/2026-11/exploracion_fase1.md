# Exploración de viabilidad — Plan de Fase 1 (Mongo/Kafka/HDFS)

> Solo lectura. No se han modificado datos, colecciones ni archivos de `data/`.

## 1. Resumen ejecutivo

- **MongoDB está operativo** en `localhost:27017` (mongod nativo, v9.0.2), BD `vivienda_euskadi` con 4 colecciones cargadas (`municipios` 252, `anuncios` 759, `alquiler_municipal` 252, `indicadores` 252). `pytest` completo: **101 passed**.
- **Kafka es viable**: broker remoto `10.22.87.215:9092` responde (puerto abierto) y `kafka-python-ng==2.2.3` ya está instalado en `.venv`.
- **HDFS es viable por vía remota**: NameNode `10.22.87.215:50070` responde y WebHDFS (`/webhdfs/v1`) devuelve `LISTSTATUS`. No hay librería `hdfs`/`confluent_kafka` instalada; HDFS puede implementarse con `requests` contra WebHDFS.
- **Docker daemon NO está en ejecución** en Windows, por lo que el plan local de `docker-compose` (HDFS+Mongo en Docker) no es usable tal cual; conviene usar el cluster remoto ya disponible (o arrancar Docker Desktop si se quiere local).
- **Java** disponible (8 y 22). **WSL** instalado pero parado; no hay Kafka/Hadoop instalados en WSL.

Conclusión global: **la Fase 1 es viable con viabilidad Media-Alta**, siempre que se use el cluster remoto para Kafka/HDFS y se eviten transacciones multi-documento (Mongo standalone sin replica set).

## 2. Infraestructura verificada

| Componente | Estado | Evidencia |
|---|---|---|
| MongoDB | ✅ Disponible | `ping()` True; versión 9.0.2; BD `vivienda_euskadi` |
| Replica set / transacciones | ❌ No disponible | `not running with --replSet` (standalone) |
| Kafka broker | ✅ Alcanzable | TCP `10.22.87.215:9092` abierto |
| `kafka-python-ng` | ✅ Instalado | `.venv`, versión 2.2.3 |
| HDFS NameNode | ✅ Alcanzable | HTTP `10.22.87.215:50070` → 200 |
| WebHDFS | ✅ Funcional | `LISTSTATUS` devuelve directorios |
| Librería `hdfs` | ❌ No instalada | `ModuleNotFoundError` |
| Librería `confluent_kafka` | ❌ No instalada | `ModuleNotFoundError` |
| Docker daemon | ❌ Parado | pipe `dockerDesktopLinuxEngine` no encontrado |
| Hadoop/Kafka locales | ❌ No instalados | sin `hdfs`, `hadoop`, `kafka-topics` |
| Java | ✅ Disponible | 1.8.0_202 y 22.0.2 |

## 3. Estado actual del repo (relevantes)

- `storage/mongo.py`, `storage/load_mongo.py`, `storage/clean_mongo.py`: implementados.
- `analysis/mongo_queries.py`, `analysis/mongo_aggregations.py`, `analysis/mongo_indexes.py`: implementados y testeados.
- `tests/test_mongo.py`: 17 tests en verde; suite completa 101 passed.
- No existen `storage/hdfs_utils.py`, `storage/kafka_producer.py`, `storage/kafka_consumer.py`.
- `docs/modelo_mongodb.md`, `docs/informe_capacidad_mongo.md`: ya identifican mejoras pendientes (`_id`, `idw_vecinos`, `tiene_alquiler_oficial`, datos huérfanos).

## 4. Viabilidad por item

### 4.1 Kafka productor/consumidor
- **Viabilidad: Alta**
- **Estado actual:** no implementado; broker remoto y librería disponibles.
- **Dependencias:** Mongo disponible; silver `anuncios_unificados.csv/json`; topic configurable en `.env`.
- **Riesgos:** conectividad intermitente Windows↔VM; permisos del broker; diseño de esquema JSON; idempotencia del consumidor; offsets y reintentos.
- **Esfuerzo estimado:** 2–3 días.

### 4.2 Validación/transformación a Mongo
- **Viabilidad: Alta**
- **Estado actual:** `clean_mongo.py` ya implementa canonicalización, marcado de nulos, deduplicación, conversión de tipos y CRUD demo; tests en verde.
- **Dependencias:** colecciones cargadas; silver estable.
- **Riesgos:** ampliar transformaciones a nuevas colecciones huérfanas; reproducibilidad tras recargas.
- **Esfuerzo estimado:** 0,5–1 día para extender/verificar; base ya hecha.

### 4.3 Integración HDFS upload/recovery
- **Viabilidad: Media**
- **Estado actual:** no implementado; NameNode remoto accesible por WebHDFS.
- **Dependencias:** WebHDFS disponible; permisos de escritura en el directorio remoto; datos raw/procesado.
- **Riesgos:** cluster compartido (cuotas/permisos); ausencia de librería `hdfs`; necesidad de implementar cliente REST; prueba de recuperación byte-a-byte.
- **Esfuerzo estimado:** 2–3 días.

### 4.4 Refactor `load_mongo.py` (`_id` codigo_ine, `idw_vecinos`, `tiene_alquiler_oficial`)
- **Viabilidad: Alta**
- **Estado actual:** `_id` ya es `codigo_ine` en `municipios`, pero `alquiler_municipal` e `indicadores` usan `ObjectId` + `codigo_ine`; `idw_vecinos` se convierte con `to_int` (incorrecto, es texto); `tiene_alquiler_oficial` viene mal en silver (`False` generalizado).
- **Dependencias:** Mongo; silver; actualizar agregaciones/consultas/tests.
- **Riesgos:** romper joins existentes y tests; migración/recreación de colecciones; derivar `tiene_alquiler_oficial` desde `metodo_imputacion='oficial'` o `nivel_geografico='municipal'`.
- **Esfuerzo estimado:** 1–2 días.

### 4.5 Carga de datos huérfanos
- **Viabilidad: Media**
- **Estado actual:** existen muchos procesados no cargados (ECVI, emancipación, Udalmap, OSRM, certificados, educación, salud, etxebide, distancias, transporte).
- **Dependencias:** refactor de `_id`; diseño de colecciones; mapeo `municipio_area_funcional_ecvi`.
- **Riesgos:** esquemas heterogéneos; cobertura parcial por municipio; volumen y mantenimiento de loaders; claves territoriales inconsistentes.
- **Esfuerzo estimado:** 3–5 días.

### 4.6 Pipelines analíticos
- **Viabilidad: Alta**
- **Estado actual:** `pipeline_indicadores_municipio` usa ≥4 etapas (`$match`, `$lookup`, `$addFields`, `$project`, `$sort`) y hay pipelines adicionales.
- **Dependencias:** colecciones cargadas y limpias; joins por `codigo_ine`.
- **Riesgos:** rendimiento con `$lookup`; datos sparse; interpretación de indicadores con imputación comarcal.
- **Esfuerzo estimado:** 1–2 días para ampliar a nuevos campos/colecciones.

### 4.7 Índices con `explain()`
- **Viabilidad: Alta**
- **Estado actual:** `mongo_indexes.py` ya crea índices y demuestra `COLLSCAN` → `IXSCAN` con `explain("executionStats")`.
- **Dependencias:** consultas reales y datos cargados.
- **Riesgos:** índices no justificados por carga real; mediciones no reproducibles si se borran índices en producción.
- **Esfuerzo estimado:** 0,5–1 día para consolidar y documentar.

## 5. Dependencias clave

- Kafka productor/consumidor depende de: Mongo disponible, upserts idempotentes, esquema de anuncios.
- HDFS upload/recovery depende de: permisos WebHDFS, datos raw/procesado estables.
- Carga de huérfanos depende de: refactor `_id` codigo_ine.
- Pipelines analíticos dependen de: carga y limpieza completas.
- Índices dependen de: patrones de consulta finales.
- Transacciones multi-documento: **no disponibles** en Mongo standalone; mantener atomicidad documental o arrancar Mongo con `--replSet` si se quiere demostrar transacciones.

## 6. Riesgos principales

1. **Infraestructura remota compartida** (Kafka/HDFS): disponibilidad, permisos y cuotas no garantizados.
2. **Docker local parado**: el plan `docker-compose` local no es ejecutable sin arrancar Docker Desktop.
3. **Inconsistencia de `_id`** entre colecciones: complica `$lookup` y upserts del consumidor Kafka.
4. **`idw_vecinos` mal tipado**: actualmente `to_int`, pero es texto con vecinos/distancias.
5. **`tiene_alquiler_oficial` incorrecto** en silver: afecta a filtros y métricas.
6. **Datos huérfanos**: amplían alcance y pueden introducir esquemas inconsistentes.
7. **No sobrescribir crudos/procesados**: toda carga debe ser idempotente en Mongo, no modificar `data/`.

## 7. Orden recomendado

1. **Refactor `load_mongo.py`** (`_id` codigo_ine, `idw_vecinos`, `tiene_alquiler_oficial`) + actualizar tests/agregaciones.
2. **Carga de datos huérfanos** (ECVI, emancipación, Udalmap, OSRM, certificados, etc.) con `_id` homogéneo.
3. **Extender validación/transformación Mongo** (`clean_mongo.py`) a nuevas colecciones.
4. **Pipelines analíticos** sobre colecciones ampliadas.
5. **Índices + explain** cuando los patrones de consulta estén cerrados.
6. **HDFS upload/recovery** (WebHDFS) en paralelo, con configuración remota.
7. **Kafka productor/consumidor** al final o en paralelo, integrando con upserts Mongo.

## 8. Bloqueadores / decisiones abiertas

- Confirmar usuario/permisos en HDFS remoto (`/user/...`) y cuota disponible.
- Confirmar topic Kafka y permisos de creación/consumo en el broker remoto.
- Decidir si se arranca Docker Desktop para HDFS/Mongo local o se mantiene el cluster remoto.
- Decidir si se quiere demostrar transacciones: requiere Mongo con `--replSet`.
- Confirmar con el profesor el tratamiento de `tiene_alquiler_oficial` y `idw_vecinos`.

## 9. Nota de alcance

Este informe es de exploración técnica. No se han ejecutado cargas, no se han modificado colecciones ni archivos de datos, y no se ha alterado el código del repositorio.
