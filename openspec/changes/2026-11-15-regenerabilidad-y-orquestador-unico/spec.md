# Spec: regenerabilidad completa y orquestador único

**Fecha:** 2026-11-15 · **Rama:** `fix/regeneracion-procesado-resultados`

## 1. Objetivo

Que cualquier artefacto derivado de `data/raw` pueda reconstruirse con comandos propios del repo,
que la cobertura de Mongo sea total y que exista una prueba ejecutable de que la cadena produce
siempre lo mismo.

## 2. Requisitos

### REQ-REG-01 — Cobertura total de Mongo

`load_all()` SHALL cargar las 17 colecciones vivas, incluidas
`anuncios_habitaciones_unificados` y `anuncios_habitaciones_unificados_bigdata`, ambas desde
`data/procesado/anuncios_habitaciones_unificados.csv` (201 documentos, 200 con precio).
La colección de habitaciones SHALL conservar `precio_eur` como `Decimal128` y `codigo_ine` como
string de 5 dígitos, igual que el estado verificado.

**Escenario:** tras `load_all()`, el conjunto de claves devuelto SHALL ser igual al de
`list_collection_names()` sin sufijos `__backup`/`__staging`.

### REQ-REG-02 — El pipeline nº 11 no puede degradar en silencio

`exportar_habitaciones_csv` SHALL fallar con error explícito si
`pipeline_habitaciones_por_municipio` devuelve una lista vacía, en lugar de escribir un CSV con
solo cabecera.

**Escenario:** con la colección de habitaciones ausente, el script SHALL salir distinto de 0 y
nombrar la colección que falta.

### REQ-REG-03 — Orquestador único

`scripts/run_pipeline.py` SHALL aceptar `--fase full`, que expande a `silver, quality, mongo, gold`
en ese orden. La fase `mongo` SHALL seguir exigiendo `--allow-mongo-write`.
`--fase all` SHALL mantener su comportamiento actual (sin Mongo).

**Escenario:** `--fase full --dry-run` SHALL listar las cuatro fases en orden y marcar `mongo`
como destructiva; sin `--allow-mongo-write` SHALL salir 2 sin ejecutar nada.

### REQ-REG-04 — Prueba de reproducibilidad

`scripts/verificar_reproducibilidad.py` SHALL comprobar, sin escribir fuera de un temporal:

1. **raw** — 355 SHA contra `docs/raw_manifest_sha256.txt`.
2. **DAG** — toda entrada y salida `data/procesado` del registro de `transform/run_all.py` tiene
   productor declarado (sin ficheros hechos a mano).
3. **colecciones** — las vivas de Mongo son exactamente las que carga `load_all`.
4. **gold** — dos pasadas de `run_analisis_mongo.py` en un directorio temporal producen la misma
   huella, igual a `docs/baseline_gold_sha256.json`.

Códigos de salida: `0` OK, `1` fallo con detalle, `2` no verificable (sin Mongo o sin raw).

**Escenario:** sin Mongo alcanzable, SHALL salir 2 indicando «no verificable», nunca 0.

## 3. Comandos

```bash
.venv/Scripts/python.exe scripts/run_pipeline.py --fase full --dry-run
.venv/Scripts/python.exe scripts/verificar_reproducibilidad.py
.venv/Scripts/python.exe -m pytest tests -q
```

## 4. Boundaries

- **Always:** leer antes de escribir; no tocar `data/raw`; no borrar colecciones desde los checks.
- **Ask first:** cambiar el esquema silver, unificar las dos colecciones de habitaciones.
- **Never:** hacer pasar el check con Mongo vacío; subir procesado a HDFS; tocar datos para forzar
  un resultado.
