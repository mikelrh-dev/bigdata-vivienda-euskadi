# Verify Report: 2026-11-13-modalidades-superficie

## Resultado

**Pasa.** El gold expone la superficie por modalidad en la misma base que el €/m², el deck usa 80/90 y D8 separa temporales de habitaciones.

## Evidencia ejecutada

### 1. Agregación y exportación

```bash
.venv/Scripts/python.exe -m py_compile analysis/mongo_aggregations.py \
  tests/test_mongo.py tests/test_mongo_orquestador.py scripts/verificar_cifras_deck.py
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
```

- `PY_COMPILE_OK`.
- `run_analisis_mongo.py`: exit 0.
- Dos ejecuciones con la misma huella: `e90498a0caa1a0674bf32a2b03a027d51c9707df426bc841c0c3ca99397a5cfc`.
- `reproducibilidad: ok`.
- `mongo_modalidades.csv`: 2 filas × 9 columnas.
- `larga_estancia`: `n=326`, `n_precio=297`, `n_superficie=290`, mediana superficie `90,0`, `n_eur_m2=290`, mediana €/m² `16,6667`.
- `temporal`: `n=268`, `n_precio=264`, `n_superficie=261`, mediana superficie `80,0`, `n_eur_m2=261`, mediana €/m² `18,9474`.
- Invariante: `n_superficie == n_eur_m2` en ambas filas.

### 2. Tests

```bash
.venv/Scripts/python.exe -m pytest tests/test_mongo.py tests/test_mongo_orquestador.py -q
.venv/Scripts/python.exe -m pytest tests -q
```

- Tests específicos: **27 passed**, exit 0.
- Suite completa: **exit 0**, con **2 skipped**.
- `git diff --check`: exit 0.

### 3. Deck

```bash
.venv/Scripts/python.exe scripts/verificar_cifras_deck.py
```

- **54/54 comprobaciones pasan**, exit 0.
- Nuevos checks B5: `80 m²`, `90 m²`, `18,95 vs 16,67`, `+13,7 %`.
- Nuevos checks D8: `268 temporales`, `201 habitaciones en colección aparte`, `297 con precio`.
- Prohibiciones: `92,5 m²`, `+23,2 %`, `268 habitaciones`.

### 4. PDF

```bash
chrome --headless=new --no-pdf-header-footer \
  --print-to-pdf=docs/presentacion_v2/presentacion_v2.pdf \
  file:///.../docs/presentacion_v2/index.html
```

- Chrome exit 0.
- `presentacion_v2.pdf`: **30 páginas**, 1.485.815 bytes.
- Texto extraído contiene: `80 m² vs 90 m²`, `268 temporales`, `201 habitaciones`, `297 con precio`.

## Archivos modificados

- `analysis/mongo_aggregations.py` — `n_superficie` y `mediana_superficie_m2`.
- `tests/test_mongo.py` — campos, rango e invariante.
- `tests/test_mongo_orquestador.py` — cabecera e invariante en CSV.
- `scripts/verificar_cifras_deck.py` — checks B5/D8 y prohibiciones.
- `docs/presentacion_v2/index.html` — B5 y D8.
- `docs/presentacion_v2/guion.md` — B5, D8 y nota oral.
- `docs/presentacion_v2/README.md` — H8b y número de checks.
- `data/resultados/README.md` — descripción de `mongo_modalidades.csv`.
- `docs/presentacion_v2/presentacion_v2.pdf` — reexportado.

## Limitaciones

- No se toca silver.
- B4 sigue siendo 201 habitaciones en 9 municipios; no se añade modalidad temporal a habitaciones.
- No se añade loader de habitaciones: la reproducibilidad desde cero de B4 sigue pendiente.
- Las copias de `H6`/`H8b` en `docs/presentacion_v2/assets` siguen siendo manuales; este cambio no añade sincronización de assets.
- `data/resultados/mongo_modalidades.csv` es un artefacto generado e ignorado por git; el cambio de código y el deck sí quedan versionables.
- No se hace commit ni push.
