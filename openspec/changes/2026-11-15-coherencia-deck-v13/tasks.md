# Tasks — coherencia deck/memoria v13

## A. Texto (sin datos ni gold)

- [x] A1 · `index.html`: 295→300 y 293→298 en las tres apariciones (756, 774, 808).
- [x] A1 · `guion.md`: 295/293→300/298 en las cuatro apariciones (14, 624, 652, 665).
- [x] A1 · `README.md` de deck: `Gold pasa a 53/53` → 55/55.
- [x] A2 · `index.html:884` y `guion.md:670`: declarar «159 con alquiler oficial».
- [x] A3 · `guion.md`: nota de indicadores derivados (columnas equivalentes + 2,552×).
- [x] A4 · `index.html`: nota «la tabla suma 277» junto al desglose por tipo.
- [x] A5 · `guion.md` (B8) e `index.html` (B2): Nivel 4/54/194 vs Tier 4/3/57/188 ortogonales.
- [x] A6 · `index.html` (B2): HDFS «solo raw» (el guion ya lo declara en 464 y 634).
- [x] A7 · `README.md` deck: ratio 0,976→0,977 y Spearman 0,979→0,988 con subconjunto.

## B. Memoria (por token)

- [x] B1 · `_cifras.json`: `verif.tests_collected` 300, `tests_passed` 298, `deck_checks` 120,
      fechas 2026-11-15.
- [x] B2 · `build.py`: mismos valores por defecto (líneas 71-78).
- [x] B3 · `build.py --build` y `--pdf`.

## C. Guardarraíl

- [x] C1 · `verificar_cifras_deck.py`: check del conteo de tests vía `pytest --collect-only`.

## D. Verificación

- [x] D1 · `verificar_cifras_deck.py` → 120/120 + nuevo check OK.
- [x] D2 · `docs/memoria/build.py --check` → OK.
- [x] D3 · `grep -rn "295 tests\|293 pasan\|115/115\|53/53"` → 0 coincidencias.
- [x] D4 · `pytest tests` → 298 passed, 2 skipped.
- [x] D5 · PDF de deck: 32 páginas y contiene 300/298, no 295/293.
- [x] D6 · PDF de memoria: contiene 298/300.
- [x] D7 · Ensayo de demo: `run_analisis_mongo.py --salida <temp> --sin-sync-deck` → huella
      `983fa53f…`.
