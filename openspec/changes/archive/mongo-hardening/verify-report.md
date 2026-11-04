# Verify Report: mongo-hardening

Fecha: 2026-11-04

Comandos (solo lectura salvo loaders/tests):
- `.venv/Scripts/python.exe -m storage.load_mongo` -> 13 colecciones OK
- `.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q` -> 24 passed
- `.venv/Scripts/python.exe -m pytest -q` -> 108 passed
- NaN audit: 0 en municipios/indicadores/alquiler
- `clean_all` keys: 13 (12 + emancipacion count)

Verificado:
- to_float nan->None, canonicalize zfill Python (sin $toString).
- loads sin ventana vacia (docs list + drop+insert solo si docs).
- provenance en base (municipios/anuncios/alquiler/indicadores + 3 nuevas).
- pipeline_top/indicador con $sort/$limit/$match en Mongo.
- informe 31/11/0, recomendaciones actualizadas.

Deuda: provenance 6/13 restantes, derivados sexo E4, archivar change + limpiar data/backup (no hecho por alcance git).

Resultado: PASS.
