# Proposal: 2026-11-13-modalidades-superficie

## Intent

B5 afirma **80 vs 92,5 m²**, pero las dos cifras no salen de la misma base: 80 es la mediana temporal con precio y superficie válidos; 92,5 es la mediana de las 322 viviendas largas con superficie, incluidas 4 de más de 500 m². Con el mismo filtro, la larga es **90 m²**. El dato no está en `mongo_modalidades.csv` y el deck no puede verificarlo.

## Scope

### In Scope

- Añadir `n_superficie` y `mediana_superficie_m2` a `pipeline_modalidades`, calculados sobre la misma base que `n_eur_m2` (precio no nulo y superficie 10–500 m²).
- Tests de agregación y de cabecera/exportación.
- Regenerar `data/resultados/mongo_modalidades.csv`.
- Corregir B5 (80 m² vs 90 m²) y D8 (268 temporales; 201 habitaciones aparte) en `index.html` y `guion.md`.
- Ampliar `scripts/verificar_cifras_deck.py` y reexportar el PDF.

### Out of Scope

- Cambios en silver.
- Modalidad temporal dentro de las 201 habitaciones.
- Loader de habitaciones o promoción de B4.
- Sincronización automática de assets del deck.
- Commit o push.

## Capabilities

### Modified Capabilities

- `mongodb-y-analisis`: `pipeline_modalidades` SHALL devolver `n_superficie` y `mediana_superficie_m2` sobre la misma base que `n_eur_m2`; `n_superficie` SHALL ser igual a `n_eur_m2`.
- `presentacion-de-resultados`: B5 SHALL usar 80 m² vs 90 m² y SHALL NOT usar 92,5 m²; D8 SHALL separar los 268 temporales de las 201 habitaciones.

## Approach

1. Añadir la lista `_superficies` al `$group`, filtrar nulos y calcular mediana con `floor(n/2)`.
2. Exponer los campos en el `$project`; el exportador ya usa la unión de claves.
3. Regenerar gold con `analysis/run_analisis_mongo.py`.
4. Corregir B5 y D8; añadir checks al verificador.
5. Exportar PDF y registrar evidencia.

## Success Criteria

- [ ] `mongo_modalidades.csv`: 2 filas, 9 columnas, `n_superficie == n_eur_m2`, medianas 90/80.
- [ ] `index.html` contiene `80 m² vs 90 m²`, `268 temporales`, `201 habitaciones en colección aparte` y `297 con precio`.
- [ ] `index.html` no contiene `92,5 m²`, `+23,2 %` ni `268 habitaciones`.
- [ ] `tests/test_mongo.py` y `tests/test_mongo_orquestador.py` pasan.
- [ ] `scripts/verificar_cifras_deck.py` pasa.
- [ ] PDF reexportado con 30 páginas.

## Rollback Plan

Revertir los cambios de `analysis/mongo_aggregations.py`, tests, deck y verificador; regenerar gold de nuevo. No se toca silver ni Mongo (solo agregación read-only).
