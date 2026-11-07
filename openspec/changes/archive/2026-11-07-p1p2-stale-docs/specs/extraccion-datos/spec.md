# extraccion-datos — Delta

## Purpose

Alinear `scripts/verificar_fase_datos.py` a la verdad v5 (594/843) y documentar los ceros de paro conocidos, sin re-ejecutar pipelines. Estado: propuesta (delta desde base Desplegada).

## ADDED Requirements

### Requirement: VERIFICACION-01 — Gate FAIL 06/07 y huella

El sistema SHALL actualizar `scripts/verificar_fase_datos.py`: el check 06 SHALL esperar `594/843` (`n_anuncios`/`n_anuncios_raw`) en `dim_municipios.csv`, no `759/843`. El check 07 SHALL listar como FAIL conocido los ceros de paro con valor no nulo —Aramaio 0.28, Gaintza 1.45, Usansolo 3.26 (`paro_registrado_cero=True` con `tasa_paro_lanbide_pct` no nulo)— y SHALL NOT enmascararlos como PASS. Cuando el resto de checks alcanza PASS, el gate SHALL emitir huella verificable (SHA-256) de los artefactos comprobados.

Guardarraíles: sin Docker; HDFS solo raw 352; Kafka→HDFS, nunca Kafka→Mongo; sin imputar comarcal/IDW como municipal.

#### Scenario: FAIL 06 con verdad v5

- GIVEN `dim_municipios.csv` con sumas 594/843
- WHEN corre `python scripts/verificar_fase_datos.py`
- THEN el check se nombra `06 n_anuncios 594/843`, PASS con `real=594`
- AND `grep -c "759/843" scripts/verificar_fase_datos.py` → `0`

#### Scenario: FAIL 07 lista los ceros conocidos

- GIVEN `udalmap_empleo_corregido.csv` con Aramaio 0.28, Gaintza 1.45, Usansolo 3.26
- WHEN corre el gate
- THEN `FAIL 07` los nombra como casos conocidos
- AND ningún caso figura como PASS ni se imputa valor comarcal

#### Scenario: PASS genera huella

- GIVEN todos los demás checks en PASS
- WHEN termina el gate
- THEN imprime `RESULTADO` y huella SHA-256 reproducible de los artefactos verificados
