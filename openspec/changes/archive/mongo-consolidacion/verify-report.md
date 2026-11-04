# Verify Report: mongo-consolidacion

Fecha: 2026-11-03

Comandos:
- `.venv/Scripts/python.exe -m storage.load_mongo` -> OK (13 colecciones, certificados 252)
- `.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q` -> 23 passed
- `.venv/Scripts/python.exe -m pytest -q` -> 107 passed

Verificado:
- `certificados_energeticos` 252 con `_id=codigo_ine`, distribucion A-G cuadra con `n_certificados`.
- `etxebide_promociones` 406 con `codigo_ine` derivado >=95%, indice `idx_promo_ine_estado_tipo` COLLSCAN->IXSCAN.
- `clean_mongo` extendido a 8 colecciones + `tiene_codigo_ine`/`calidad_cert`.
- `pipeline_accesibilidad_extendida` ejecuta aggregate (fix), + `pipeline_vpo_por_municipio` (322 grupos) y `pipeline_udalmap_extendido_osrm`.
- `modelo_mongodb.md` 13 colecciones, `informe_capacidad_mongo.md` reclasifica C5/D2/C1/B5/C3/C6/D5/E1-E3/D3 a directa, F5/G4 a parcial (31/10/1).

Deuda: Udalmap 10-15 y Padron joven quedan fuera (valor marginal / opcional). G6 sigue no responde.

Resultado: PASS.
