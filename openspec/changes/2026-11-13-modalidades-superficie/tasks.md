# Tasks: 2026-11-13-modalidades-superficie

## Phase 1: Gold

- [x] 1.1 Añadir `n_superficie` y `mediana_superficie_m2` a `pipeline_modalidades` sobre la base de `n_eur_m2`.
  - Verify: `mongo_modalidades.csv` 2 filas, 9 columnas, 90/80, `n_superficie == n_eur_m2`.
- [x] 1.2 Ampliar `tests/test_mongo.py` y `tests/test_mongo_orquestador.py`.
  - Verify: `.venv/Scripts/python.exe -m pytest tests/test_mongo.py tests/test_mongo_orquestador.py -q`.

## Phase 2: Presentación

- [x] 2.1 B5: `80 m² vs 90 m²`; retirar `92,5 m²` y `+23,2 %`.
- [x] 2.2 D8: 326 = 297 con precio + 29 sin precio; 268 temporales; 201 habitaciones aparte.
- [x] 2.3 Ampliar `scripts/verificar_cifras_deck.py` con B5, D8 y prohibiciones.
  - Verify: `.venv/Scripts/python.exe scripts/verificar_cifras_deck.py`.

## Phase 3: Cierre

- [x] 3.1 Exportar `presentacion_v2.pdf` y comprobar 30 páginas.
- [x] 3.2 Escribir `verify-report.md` con comandos y resultados.
