<!-- cap: 3 | titulo: Cómo se construyó | criterios: C5, C6, C7, C8 | estado: borrador -->
# 3. Cómo se construyó

> **Objetivo.** Describir el pipeline que va de la fuente al gold y demostrar que se puede ejecutar sin tocar MongoDB a mano.

## 3.1 Extracción y manifiesto

La extracción combina API y scraping. Cada fichero se guarda con su SHA-256 en `docs/raw_manifest_sha256.txt` y se marca con `.FROZEN`; a partir de ahí es inmutable. El manifiesto es la lista de verdad de lo que se descargó y permite detectar un fichero alterado sin abrir su contenido.

## 3.2 El DAG y las fases

`python scripts/run_pipeline.py` ejecuta el DAG de {{verif.gobernanza_dag}} nodos por fases: `extract`, `raw`, `silver`, `mongo`, `quality` y `gold`. Cada fase termina con una verificación; si falla, el pipeline se detiene en vez de propagar un dato mal formado. La misma orden se usa en local y en la demostración.

## 3.3 Silver: normalizar sin perder el original

Silver convierte {{silver.manifest}} ficheros de entrada en CSV con `codigo_ine` como clave. Aquí se tratan nulos, duplicados y tipos: fechas como fecha, importes como número, códigos como cadena de cinco dígitos. El original no se toca; si una regla cambia, se regenera silver desde raw.

## 3.4 Carga idempotente

La carga usa `replace_collection`: construye la colección en una temporal y la intercambia al final. Una segunda ejecución deja el mismo estado que la primera, sin duplicados ni documentos a medias. Es la respuesta práctica a la consistencia: no hace falta una transacción multi-documento si cada colección se reemplaza de forma atómica.

## 3.5 Gold

Los pipelines de agregación escriben {{mongo.csv_salidas}} CSV y los scripts de figuras generan {{gold.png}} PNG. Gold es la única capa que el informe consume; no se dibuja directamente desde Mongo para que una figura se pueda reproducir sin conexión.

## 3.6 Reproducibilidad

Un clon del repositorio, con el entorno y el manifiesto, puede repetir la extracción, la carga y el análisis. La comprobación es doble: `--check` valida el estado declarado y los tests cubren las reglas de transformación. El capítulo 8 recoge los comandos y el resultado esperado.
