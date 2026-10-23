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

## Estructura

```
BigDataReto/
├── config/fuentes.yaml      URLs, IDs de tablas y cobertura verificada
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
| 0. Entorno y VM | ⚠️ venv creado; Docker y VM pendientes |
| 1. Extracción | ✅ Hecha (scripts 01–06 funcionan) |
| 2. Kafka | ⬜ Pendiente (VM) |
| 3. MongoDB modelado | ⬜ Pendiente |
| 4. Limpieza | ⬜ Pendiente |
| 5. Aggregation Pipeline | ⬜ Pendiente |
| 6. Visualización e informe | ⬜ Pendiente |
