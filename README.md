# BigDataReto — ¿Dónde pueden vivir los jóvenes en Euskadi?

Reto intermodal de **SBD + BDA**. Pipeline de datos en Python que analiza
la accesibilidad de la vivienda para la población joven en Euskadi.

## Arquitectura

```
Fuentes (API + scraping)
   → HDFS (originales)
   → Kafka (VM Ubuntu Server)
   → MongoDB (Docker)
   → PyMongo (limpieza)
   → Aggregation Pipeline (indicadores)
   → Gráficos + informe
```

Ver `plan/PLAN.md` para el plan completo y `plan/arquitectura.md` para el
esquema detallado.

## Contrato de requisitos (OpenSpec)

La implementación está atada a la rúbrica del reto. El contrato vive en
`openspec/` y **manda sobre el código**:

| Fichero | Contenido |
|---|---|
| `openspec/specs/contrato-reto/spec.md` | **La verdad.** Rúbrica transcrita literal + 18 requisitos + prohibiciones |
| `openspec/specs/extraccion-datos/spec.md` | Extracción API y scraping, formato, salarios |
| `openspec/specs/almacenamiento-y-streaming/spec.md` | HDFS, Kafka, integración |
| `openspec/specs/mongodb-y-analisis/spec.md` | Modelado, PyMongo, consultas, agregación, limpieza |
| `openspec/specs/presentacion-de-resultados/spec.md` | Gráficos, datos, presentación, interpretación |
| `openspec/config.yaml` | Contexto, reglas y la regla `contract_first` |
| `openspec/project.md` | Objetivo, stack, layout y fuentes |

**Regla de oro:** antes de escribir código, se lee
`openspec/specs/contrato-reto/spec.md`. Un criterio solo se marca como
cubierto cuando se puede verificar.

## Estructura

```
BigDataReto/
├── openspec/specs/{capability}/spec.md   contrato por dominio
├── tests/test_contrato.py        verificación del contrato
├── config/fuentes.yaml                   URLs, IDs de tablas y cobertura verificada
├── extract/                 Scripts de extracción (API + scraping)
├── storage/                 HDFS, Kafka, MongoDB (PyMongo)
├── transform/               Limpieza y enriquecimiento
├── analysis/                Aggregation Pipeline e indicadores
├── visualization/           Gráficos
├── notebooks/               Informe de resultados
├── data/raw/                Datos originales (generados)
├── plan/                    Planificación
└── docs/                    Documentación
```

## Puesta en marcha

### 1. Entorno Python (venv dedicado)

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

### 2. Extracción de datos (no necesita Docker ni la VM)

```bash
.venv/Scripts/python.exe extract/01_eustat_api.py        # Eustat bankupx
.venv/Scripts/python.exe extract/02_eustat_alquiler.py   # Alquiler municipal
.venv/Scripts/python.exe extract/03_euskadi_emancipacion.py
.venv/Scripts/python.exe extract/04_b5m_geo.py
.venv/Scripts/python.exe extract/05_fotocasa_scraper.py  # Scraping
.venv/Scripts/python.exe extract/06_ine_api.py           # INE wstempus
```

Salida en `data/raw/`.

### 2b. Verificar contra el contrato

```bash
.venv/Scripts/python.exe -m pytest tests -q
```

11 tests comprueban los escenarios del contrato que son verificables con
datos reales. Un `xfail` significa que un criterio sigue abierto.

### 3. Infraestructura (pendiente de completar)

- **Docker Compose** en Windows: HDFS + MongoDB
- **Kafka** en la VM Ubuntu Server (modo KRaft, puerto 9092)

### 4. Carga y análisis (pendiente)

```bash
.venv/Scripts/python.exe storage/hdfs_utils.py
.venv/Scripts/python.exe storage/kafka_producer.py
.venv/Scripts/python.exe storage/kafka_consumer.py
.venv/Scripts/python.exe analysis/pipeline_agregaciones.py
```

## Fuentes de datos

Todas verificadas en octubre de 2026.

| Fuente | Tipo | Registro | Cobertura |
|---|---|---|---|
| Eustat bankupx API | API JSON | No | Población, renta, PIB, tenencia por municipio |
| Eustat ExtractorBlob | CSV/XLSX | No | Alquiler municipal (€/m², €/mes, m²) |
| INE wstempus API | API JSON | No | Población, hogares, precios de compraventa |
| euskadi.eus | CSV | No | Emancipación juvenil (16 indicadores) |
| b5m Gipuzkoa | API JSON | No | Límites municipales, distancias |
| Catastro INSPIRE | WFS/WMS | No | Parcelas, antigüedad (opcional) |
| Fotocasa | Scraping | No | ~480 anuncios reales de alquiler |
| Idealista Search API | API oficial | **Sí** (aprobación) | Opcional, si se concede |

> **Nota:** la API del INE no publica el alquiler por municipio en
> Euskadi (régimen foral): el valor viene a `null`. Para el alquiler se
> usa Eustat, que sí lo publica.

## Datos generados (última ejecución)

| Fichero | Contenido |
|---|---|
| `eustat_poblacion_edad.json/csv` | 89.424 filas |
| `eustat_renta_municipal.json/csv` | 98.532 filas |
| `eustat_renta_edad.json/csv` | 6.426 filas |
| `eustat_pib_municipal.json/csv` | 13.248 filas |
| `eustat_tenencia.json/csv` | 4.416 filas |
| `alquiler_municipal.csv` | 253 registros, 159 municipios |
| `anuncios_fotocasa.json/csv` | 480 anuncios únicos, 57 municipios |
| `emancipacion_juventud.csv` | 867 filas |
| `ine_*.json/csv` | 5 tablas (69301, 69302, 69303, 69323, 69330) |
| `municipios_gipuzkoa.geojson` | 126 polígonos municipales |
| `distancias_municipios.json` | 180.488 pares de distancias |

## Estado del proyecto

| Fase | Estado |
|---|---|
| 0. Entorno y VM | ⚠️ venv, Docker Desktop y contrato OK; VM pendiente |
| 1. Extracción | ✅ Hecha (scripts 01–06, 127 MB en `data/raw/`) |
| 1b. Salarios (INE EPA) | ⬜ Abierto — el contrato lo marca como pendiente |
| 2. Kafka | ⬜ |
| 3. MongoDB modelado | ⬜ |
| 4. Limpieza | ⬜ |
| 5. Aggregation Pipeline | ⬜ |
| 6. Visualización e informe | ⬜ |
