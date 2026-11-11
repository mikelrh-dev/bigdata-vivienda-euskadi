# Vivienda y emancipación juvenil en Euskadi

Proyecto del reto SBD+BDA: integra datos públicos y anuncios de vivienda para
analizar alquiler, renta, empleo y accesibilidad municipal en Euskadi.

## Estructura

```text
analysis/    consultas MongoDB, aggregation pipelines e informes exportables
config/      catálogo de fuentes y parámetros del estudio
data/        datos raw, procesados y resultados locales
extract/     extracción de fuentes y orquestador de ingesta
scripts/     entrypoints y verificaciones auxiliares
storage/     carga MongoDB e integración HDFS/Kafka
tests/       pruebas automatizadas
transform/   limpieza, normalización y enriquecimiento de datos
brief/       enunciado y material de la asignatura
```

## Requisitos y configuración

- Python 3.12; dependencias en `requirements.txt`.
- MongoDB local para carga y análisis (`localhost:27017` por defecto).
- HDFS y Kafka del centro solo para ejecutar esos tramos; requieren conectividad
  y configuración válida.

En Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`requirements.txt` es la lista que se usa para instalar las dependencias.
`pyproject.toml` conserva metadatos básicos y configuración de pytest; el
proyecto no usa `uv` ni mantiene un lockfile de uv.

`.env` es opcional para Mongo local, que por defecto usa `localhost:27017`.
Si creas el fichero, parte de `.env.example` y configura solo lo que vayas a
usar. Las variables Mongo (`MONGO_HOST`, `MONGO_PORT`, `MONGO_DB`) afectan al
flujo local; `MONGO_URI` permite sustituir host/puerto. Las variables HDFS y
Kafka son específicas del clúster académico. `REALTYAPI_KEY` solo hace falta
para ese extractor opcional. No publiques `.env` ni credenciales.

`config/parametros_estudio.yaml` define umbrales y parámetros que usan los
scripts de análisis visual. `config/fuentes.yaml` es un inventario de referencia
de fuentes; los extractores mantienen su lógica de acceso en `extract/` y no lo
cargan actualmente como configuración ejecutable.

## Flujo principal

Los datos ya presentes en `data/` permiten trabajar sin volver a descargar las
fuentes. La extracción completa es una operación de red y no hace falta
repetirla para cada ejecución del resto del pipeline.

```text
fuentes → extract/ → data/raw/ → transform/ → data/procesado/
                                           → MongoDB → analysis/ → data/resultados/
data/raw/ → Kafka → HDFS (rama de almacenamiento, independiente de MongoDB)
```

### 1. Extracción (solo cuando se quiera actualizar raw)

```powershell
.\.venv\Scripts\python.exe extract/main_ingest.py
```

Ejecuta extractores con acceso a fuentes externas. Para validar los hashes del
raw existente sin volver a descargar datos:

```powershell
.\.venv\Scripts\python.exe extract/main_ingest.py --mode replay-raw
```

### 2. Transformación

```powershell
.\.venv\Scripts\python.exe transform/run_all.py
```

El orquestador genera datos derivados en `data/procesado/`. `--dry-run` muestra
el orden de ejecución y `--group <grupo>` ejecuta solo un grupo.

### 3. MongoDB y análisis

**Atención:** la carga batch reemplaza colecciones de la base configurada. Revisa
`.env` y confirma el destino antes de ejecutarla.

```powershell
.\.venv\Scripts\python.exe -m scripts.run_mongo_pipeline
.\.venv\Scripts\python.exe analysis/run_analisis_mongo.py
```

El análisis consulta MongoDB y exporta CSV/figuras a `data/resultados/`.

### 4. Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

Las pruebas offline no demuestran disponibilidad actual de HDFS, Kafka ni
MongoDB remoto. Los comandos que usan esos servicios requieren configurarlos y
validarlos por separado. Algunos utilitarios auxiliares de auditoría usan
DuckDB, que no forma parte del flujo principal ni de `requirements.txt`; si los
necesitas, instala esa dependencia aparte con `python -m pip install duckdb`.

## Big Data: HDFS y Kafka

La cadena de manifiestos raw está implementada en `storage/kafka_raw_producer.py`
y `storage/kafka_hdfs_uploader.py`. Requiere Kafka y HDFS accesibles y las
variables correspondientes de `.env`. Hay además una variante experimental de
eventos JSON de anuncios en `storage/kafka_anuncio_producer.py` y
`storage/kafka_anuncio_consumer.py`; su consumidor escribe en la base de test,
no en la colección productiva.

## Datos y configuración del estudio

- `data/raw/`: capturas originales; no es una salida regenerable del transform.
- `data/procesado/`: resultados derivados de la transformación.
- `data/resultados/`: salidas de análisis. Puede estar vacía en un checkout
  limpio; los artefactos se generan localmente.
- `config/fuentes.yaml`: URLs, identificadores y notas de fuentes.
- `config/parametros_estudio.yaml`: umbrales, fórmulas y vintages del estudio.

## Alcance y limitaciones

El análisis municipal depende de la cobertura de las fuentes. La renta municipal
se usa como proxy de capacidad económica juvenil, no como salario observado de
cada joven; parte del alquiler oficial se completa a nivel comarcal. Los
resultados deben interpretarse junto con esas limitaciones y con el periodo de
cada fuente.
