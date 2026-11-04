# Spec: PyMongo profesional — PYMONGO-PRO-01 (delta)

## Objective

Detallar los escenarios comprobables del requisito PYMONGO-PRO-01 ya
declarado en `openspec/specs/mongodb-y-analisis/spec.md` (líneas 339-344):
conexión reutilizable con URI configurable, fallback y ObjectId validado.

## Tech Stack

Python 3.12 (.venv), PyMongo 4.x, pytest. Sin dependencias nuevas.

## Commands

```bash
.venv/Scripts/python.exe -m pytest tests/test_mongo_pymongo_pro.py tests/test_mongo_geo.py -q
```

## ADDED Requirements

### Requirement: PYMONGO-PRO-01 — URI configurable con fallback

El sistema SHALL construir el MongoClient desde MONGO_URI cuando esté
definida y no vacía, y SHALL caer a MongoClient(MONGO_HOST, MONGO_PORT) en
caso contrario. La URI se lee en tiempo de llamada, no cacheada en import.

#### Scenario: URI configurada
- GIVEN MONGO_URI definida con una URI falsa de test
- WHEN se llama a get_client()
- THEN MongoClient se invoca con esa URI y serverSelectionTimeoutMS=5000
- AND get_mongo_uri() devuelve la URI

#### Scenario: Fallback sin URI
- GIVEN MONGO_URI ausente tras monkeypatch.delenv
- WHEN se llama a get_client()
- THEN MongoClient se invoca con MONGO_HOST y MONGO_PORT
- AND get_mongo_uri() devuelve None

### Requirement: PYMONGO-PRO-01 — ObjectId validado en anuncios

El sistema SHALL exponer is_objectid / to_objectid reutilizables para
validar y convertir identificadores ObjectId, y los documentos de anuncios
SHALL llevar _id de tipo ObjectId.

#### Scenario: Anuncios con ObjectId en vivo
- GIVEN MongoDB responde al ping
- WHEN se lee un documento de anuncios
- THEN su _id es instancia de ObjectId
- AND is_objectid(_id) es True, is_objectid(str(_id)) es True
- AND to_objectid(str(_id)) reproduce el _id

#### Scenario: Rechazo de valores no válidos
- GIVEN un valor que no es ObjectId ni string de 24 hex
- WHEN se evalúa is_objectid
- THEN devuelve False

## Success Criteria

1. Los dos tests de tests/test_mongo_pymongo_pro.py pasan.
2. test_mongo_geo.py sigue en verde (sin regresión en GeoJSON).
3. El comando de verificación reporta exit 0.
