# Decisión WP-16: `dim_municipios.*` en raw como universo versionado

**Fecha:** 2026-11-01. **Estado:** aceptada.

## Contexto

`data/raw/dim_municipios.csv/json` (252 municipios) convive con datos
observados en el raw congelado y es leído por 9 extractores
(`09_fotocasa_dirigido`, `10_scraping_faltantes`,
`19_udalmap_indicadores_adicionales`, `educacion_centros`,
`entity_resolution`, `euskadi_geo`, `ine_atlas_renta`, `salud_centros`,
`udalmap_empleo`) como universo de referencia para el scraping.

## Decisión

Se declara **universo versionado, no dato observado**:

- `dim_municipios.*` en raw es la foto congelada del universo 252
  (generada por `transform/dim_municipios.py` a partir de Eustat + variantes
  de nombre) y los extractores la usan solo como lista de objetivos,
  nunca como medición.
- La tabla de trabajo vive en `data/procesado/dim_municipios.csv`
  (enriquecida por `aplicar_cobertura_mercado.py` con `n_anuncios_raw`,
  `n_anuncios` post-dedup y `tipologia_mercado`).
- No se mueve el fichero raw (está en el manifest SHA 314 y bajo
  `.FROZEN`); moverlo invalidaría la cadena de custodia por un beneficio
  puramente taxonómico.

## Consecuencias

- La dirección del flujo se mantiene: extractores leen universo (raw),
  transformaciones escriben silver (procesado). Ningún extractor escribe
  resultados en raw.
- Si el universo cambia (p. ej. 253 municipios), se congela
  `universo_252.v2` con acta en vez de editar el existente.
- Revisar esta decisión solo si algún extractor pasa a depender de
  columnas de medición de `dim_municipios` (hoy solo usan
  `codigo_ine`/`nombre_canonico`/población).
