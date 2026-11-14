# Spec: superficie por modalidad y embudo 2026

**Fecha:** 2026-11-13 · **Rama:** `fix/regeneracion-procesado-resultados`

## 1. Objetivo

Que B5 pueda explicar el tamaño de la vivienda con una cifra que salga de gold y use la misma base que el €/m². Que D8 no confunda los 268 alquileres temporales con las 201 habitaciones.

## 2. Contrato de datos

`pipeline_modalidades` devuelve, por modalidad:

| Campo | Regla |
|---|---|
| `n_superficie` | anuncios con `precio_eur` no nulo y `superficie_m2` en [10, 500] |
| `mediana_superficie_m2` | mediana de `superficie_m2` sobre esa misma base, `floor(n/2)` |
| `n_eur_m2` | ya existente; misma base |
| `mediana_eur_m2` | ya existente; misma base |

Invariante: `n_superficie == n_eur_m2`.

Valores esperados con la captura 2026:

| Modalidad | n | n_precio | n_superficie | Mediana superficie | Mediana €/m² |
|---|---:|---:|---:|---:|---:|
| larga_estancia | 326 | 297 | 290 | 90,0 m² | 16,67 |
| temporal | 268 | 264 | 261 | 80,0 m² | 18,95 |

## 3. Contrato de presentación

- B5: “Misma mediana mensual (1.500 €), pero el temporal es más pequeño: **80 m² vs 90 m²**”.
- B5: “Por m², el temporal es **+13,7 %** en el total (18,95 vs 16,67 €/m²)”.
- B5 NO usa “92,5 m²” ni “+23,2 %”.
- D8: “**326** vivienda completa (**297** con precio; **29** sin precio) + **268** temporales (**264** con precio)”.
- D8: “**201 habitaciones** en **9 municipios**, colección aparte; no entran en el 594”.
- D8 NO usa “268 habitaciones”.

## 4. Comandos

```bash
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe -m pytest tests/test_mongo.py tests/test_mongo_orquestador.py -q
.venv/Scripts/python.exe scripts/verificar_cifras_deck.py
```

Exportación del PDF:

```bash
chrome --headless=new --no-pdf-header-footer \
  --print-to-pdf=docs/presentacion_v2/presentacion_v2.pdf \
  file:///.../docs/presentacion_v2/index.html
```

## 5. Estructura

```
analysis/mongo_aggregations.py      → pipeline_modalidades
analysis/run_analisis_mongo.py      → exportación existente (sin cambios)
tests/test_mongo.py                 → campos y rango
tests/test_mongo_orquestador.py     → cabecera e invariante
scripts/verificar_cifras_deck.py    → checks B5/D8 y prohibiciones
docs/presentacion_v2/index.html     → B5 + D8
docs/presentacion_v2/guion.md       → B5 + D8
```

## 6. Criterios de éxito

- [ ] `mongo_modalidades.csv` tiene 2 filas y 9 columnas.
- [ ] `mediana_superficie_m2` da 90/80 y `n_superficie == n_eur_m2` (290/261).
- [ ] El deck no contiene `92,5 m²`, `+23,2 %` ni `268 habitaciones`.
- [ ] El deck contiene `80 m² vs 90 m²`, `268 temporales`, `201 habitaciones en colección aparte` y `297 con precio`.
- [ ] Tests y verificador pasan; PDF con 30 páginas.

## 7. Boundaries

- **Always:** mantener gold en 53 artefactos; no tocar silver; no inventar habitaciones temporales.
- **Ask first:** recargar Mongo, cambiar el esquema silver, promover B4.
- **Never:** borrar gold, reescribir silver, commit/push sin petición.
