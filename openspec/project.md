# Proyecto: bigdata-vivienda-euskadi — ¿Dónde pueden vivir los jóvenes en Euskadi?

_Bootstrap SDD: objetivo, stack, layout, fuentes y estado. El contrato
de requisitos está en `specs/contrato-reto/spec.md`._

**Estado:** Extracción completada. Infraestructura (HDFS, Kafka, MongoDB) y
análisis pendientes.
**Fecha:** 2026-10-23

---

## Objetivo

Responder con **datos reales** qué municipios de Euskadi ofrecen mejores
posibilidades de emancipación para una persona joven, y explicar por qué.

Fuente de verdad de la evaluación: el PDF `RETO 1Evaluacion SBD-BDA.pdf`
(rúbrica y requisitos transcritos en `specs/contrato-reto/spec.md`).

Plan de implementación por fases: `openspec/plan/fases.md` (planificado, no
iniciado salvo la Fase 0).

## Stack

| Pieza | Tecnología | Estado |
|---|---|---|
| Lenguaje | Python 3.12 (`.venv`) | ✅ |
| Extracción | `requests`, `beautifulsoup4`, `lxml` | ✅ |
| Almacenamiento | HDFS (Docker Desktop) | ⬜ |
| Streaming | Apache Kafka (VM Ubuntu Server, KRaft) | ⬜ |
| Base de datos | MongoDB (Docker Desktop) + PyMongo | ⬜ |
| Análisis | Aggregation Pipeline de MongoDB | ⬜ |
| Visualización | matplotlib, seaborn | ⬜ |
| Contrato | OpenSpec (`openspec/`) | ✅ |

## Recorrido de los datos

```
Fuentes (API + scraping) → HDFS (originales) → Kafka (VM) → MongoDB
                         → PyMongo (limpieza) → Aggregation Pipeline
                         → gráficos + informe
```

## Layout

```
.
├── openspec/specs/{capability}/spec.md   contrato por dominio
├── config/fuentes.yaml                   URLs, IDs y cobertura verificada
├── extract/                              extracción (API + scraping)
├── storage/                              HDFS, Kafka, MongoDB
├── transform/                            limpieza y enriquecimiento
├── analysis/                             agregación e indicadores
├── visualization/                        gráficos
├── notebooks/                            informe
├── tests/                                verificación del contrato
├── data/{raw,procesado,resultados}       datos generados
└── plan/PLAN.md                          planificación
```

## Fuentes (verificadas 2026-10-23)

| Fuente | Tipo | Registro | Cobertura |
|---|---|---|---|
| Eustat bankupx | API JSON | No | 5 tablas, 122.466 filas |
| Eustat ExtractorBlob | CSV/XLSX | No | Alquiler municipal, 159 municipios |
| INE wstempus | API JSON | No | 5 tablas; alquiler a `null` en Euskadi |
| euskadi.eus | CSV | No | Emancipación juvenil, 867 filas |
| b5m Gipuzkoa | API JSON | No | Límites municipales y distancias |
| Fotocasa | Scraping | No | 480 anuncios únicos, 57 municipios |
| Idealista Search API | API oficial | **Sí** | Opcional, pendiente de aprobación |

## Estado por fase

| Fase | Estado |
|---|---|
| 0. Entorno y VM | ⚠️ venv y Docker Desktop OK; VM pendiente |
| 1. Extracción | ✅ scripts 01–06, 127 MB en `data/raw/` |
| 2. Kafka | ⬜ |
| 3. MongoDB (modelado, PyMongo, consultas) | ⬜ |
| 4. Limpieza y transformación | ⬜ |
| 5. Aggregation Pipeline | ⬜ |
| 6. Visualización e informe | ⬜ |

## Reglas del contrato

1. `specs/contrato-reto/spec.md` es la verdad. Si el código y el contrato
   discrepan, manda el contrato (o se cambia el contrato antes).
2. Ninguna sesión empieza a escribir código sin haber leído ese fichero.
3. Cada criterio de la rúbrica tiene un requisito y un escenario.
4. Un criterio solo se marca como cubierto cuando se puede verificar.
