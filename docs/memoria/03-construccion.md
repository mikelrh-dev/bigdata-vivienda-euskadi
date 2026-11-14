<!-- cap: 3 | titulo: Cómo se construyó | criterios: C5, C6, C7, C8 | estado: borrador -->
# 3. Cómo se construyó

> El capítulo describe el pipeline que va de la fuente al gold y comprueba que se puede ejecutar sin tocar MongoDB a mano.

## 3.1 Extracción y manifiesto

La extracción combina API, scraping y descargas Open Data. Cada fichero se guarda con su SHA-256 en `docs/raw_manifest_sha256.txt` y se marca con `.FROZEN`; a partir de ahí es inmutable. El manifiesto registra lo que se descargó y permite detectar un fichero alterado sin abrir su contenido. Hoy tiene {{raw.manifest}} entradas y `extract/generar_manifest.py --verify` las comprueba con 0 errores.

## 3.2 El orquestador y las fases

`python scripts/run_pipeline.py` encadena cuatro fases: `silver`, `quality`, `mongo` y `gold`. La fase `mongo` es destructiva y exige `--allow-mongo-write`; `--fase all` ejecuta silver, quality y gold, nunca mongo. `--dry-run` lista los pasos y `--strict` convierte los avisos en fallo. Si un paso devuelve un código distinto de 0, la fase se aborta y no se propaga un dato mal formado.

La extracción y el volcado a HDFS quedan fuera de este orquestador: se ejecutan con sus scripts y su propio control. El DAG de {{verif.gobernanza_dag}} nodos vive en `transform/run_all.py` y corresponde a la fase silver; el orquestador lo invoca como un paso, no lo replica.

| Fase | Comando | Salida |
|---|---|---|
| silver | `transform/run_all.py` | {{silver.manifest}} CSV en `data/procesado` |
| quality | `normalizar_metadata` + manifiestos | sidecars y manifiesto SHA |
| mongo | `scripts/run_mongo_pipeline.py` (opt-in) | {{mongo.vivas}} colecciones |
| gold | `capa_2026` + análisis + figuras | {{gold.artefactos}} artefactos |

## 3.3 Silver: normalizar sin perder el original

Silver convierte {{silver.manifest}} ficheros de entrada en CSV con `codigo_ine` como clave. Aquí se tratan nulos, duplicados y tipos: fechas como fecha, importes como número, códigos como cadena de cinco dígitos. El original no se toca; si una regla cambia, se regenera silver desde raw.

## 3.4 Limpieza con PyMongo

La limpieza es una fase con operaciones verificables. `canonicalize_codigo_ine` normaliza el código en `anuncios`, `alquiler`, `indicadores` y el resto de colecciones con `update_many`. `mark_nulls` marca los ausentes y `$unset` retira los centinelas. `resolve_duplicates` agrupa por `(portal, id_anuncio)` y por `property_fingerprint`, y borra todos los documentos del grupo menos uno; en alquiler usa `(codigo_ine, distrito, nivel, metodo)`. `convert_types` convierte precios de texto a `Decimal128`, habitaciones a entero y booleanos a `bool` con `$convert`.

## 3.5 Carga idempotente

La carga usa `replace_collection`: construye la colección en `__staging`, copia la anterior a `__backup` con `$out` y renombra la staging. Una segunda ejecución deja el mismo estado que la primera, sin duplicados ni documentos a medias. Los {{mongo.backup}} backup que aparecen en el inventario son la huella de ese mecanismo, no colecciones de trabajo.

## 3.6 Gold y una laguna declarada

Los pipelines de agregación escriben {{mongo.csv_salidas}} CSV y los scripts de figuras generan {{gold.png}} PNG. Gold es la única capa que el informe consume; no se dibuja directamente desde Mongo para que una figura se pueda reproducir sin conexión.

Cada figura declara su año con un sello en la esquina inferior derecha, y el mismo texto se repite en el pie de la figura. El sello no se coloca a ojo: antes de escribir el PNG, el generador reserva una franja inferior del lienzo y mide la caja del sello contra la de todos los textos visibles. El recuento de solapes queda en los metadatos del PNG y `scripts/verificar_vintage_figuras.py` falla si alguno no es cero, de modo que una figura nueva no puede publicarse pisando una etiqueta.

Queda una laguna: `transform/run_all.py --check` señala que falta `auditoria_lagunas_silver.csv`. No se regeneró porque añadiría un artefacto más al gold y obligaría a rehacer las cuentas del deck. Se declara aquí y en el capítulo 8.
