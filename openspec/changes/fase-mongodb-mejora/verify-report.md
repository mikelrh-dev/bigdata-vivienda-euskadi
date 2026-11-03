# Verify Report: fase-mongodb-mejora

Fecha: 2026-11-03

Comandos:
- `.venv/Scripts/python.exe -m storage.load_mongo` -> OK (10 colecciones)
- `.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q` -> 18 passed
- `.venv/Scripts/python.exe -m pytest -q` -> 102 passed

Verificado:
- `_id` homogéneo en municipios/alquiler/indicadores.
- `tiene_alquiler_oficial` derivado (>=150 True).
- `idw_vecinos` texto.
- Colecciones huérfanas cargadas (ECVI, Udalmap, OSRM, emancipación, Etxebide).
- Agregación extendida y tests.

Resultado: PASS.

Actualización 2026-11-03 (carga nuevas colecciones raw):
- udalmap_extendido: 252
- etxebide_promociones: 406
- Recarga Mongo OK; tests/test_mongo.py: 18 passed.
