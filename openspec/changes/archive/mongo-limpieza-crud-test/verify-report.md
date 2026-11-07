# Verification Report: mongo-limpieza-crud-test

## Veredicto

PASS — 25 passed, 0 skipped, exit code 0. Sin commit, cambios sin commitear.

## Comandos y evidencia

| Comando | Resultado |
|---------|-----------|
| .venv/Scripts/python.exe -m pytest tests/test_mongo.py::test_clean_mongo tests/test_mongo.py::test_crud_demo -v | 2 passed, exit code 0 |
| .venv/Scripts/python.exe -m pytest tests/test_mongo.py -q | 25 passed in 0.73s, exit code 0, 0 skipped |

## Cobertura de requisitos

| Requisito | Escenario | Evidencia | Estado |
|-----------|-----------|-----------|--------|
| PYMONGO-01 | Los tests no mutan prod y no se saltan | test_clean_mongo y test_crud_demo corren sin skip; conteo productivo antes y después igual | PASS |
| PYMONGO-01 | Los métodos y contadores se demuestran | test_crud_demo aserta inserted_id, update_one matched_count y modified_count, find_one_and_update, bulk_write deleted_count, delete_one y delete_many | PASS |
| PYMONGO-01 | Los resultados se comprueban | test_clean_mongo verifica códigos, tipos y recuento tras cada operación | PASS |
| LIMPIEZA-CRUD-TEST-01 | Limpieza con contadores sobre temporal | canonicalize matched_count 3 y modified_count 2; mark_nulls 1 y 2; resolve_duplicates deleted 1; convert_types matched_count 1; códigos finales 01001 y 20069 | PASS |
| LIMPIEZA-CRUD-TEST-01 | CRUD con contadores sobre temporal | count_find 3, remaining 1, _demo_crud eliminada al terminar | PASS |
| LIMPIEZA-01 y TRANSFORM-01 | 4 operaciones con nulos, duplicados y tipos | Las 4 funciones reales ejecutadas y asertadas sobre la temporal | PASS |

## Diseño

El patch de clean_mongo.get_collection hacia get_test_db se aplica solo dentro del contexto _clean_mongo_on_test_db, con drop previo y en finally. No se modificó storage/clean_mongo.py, storage/load_mongo.py, docs/modelo_mongodb.md, tests/test_mongo_geo.py ni analysis/.

## Issues

- WARNING: storage/clean_mongo.py::_counter lee upserted_count, atributo que PyMongo no expone en UpdateResult (usa did_upsert y upserted_id); el contador de upsert siempre vale 0. El test aserta matched_count 0 del upsert y la inserción queda probada por delete_many 2. No se corrigió por estar fuera del alcance de este cambio.
- El diff contra HEAD de tests/test_mongo.py incluye cambios previos de la sesión (rangos en test_conteos); el cambio propio son las líneas 145-229.

## Ficheros

tests/test_mongo.py líneas 145-163 helper, 166-210 test_clean_mongo, 213-229 test_crud_demo. Artefactos en openspec/changes/mongo-limpieza-crud-test/: proposal.md, specs/mongodb-y-analisis/spec.md, design.md, tasks.md, verify-report.md.
