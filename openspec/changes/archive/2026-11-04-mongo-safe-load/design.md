# Design: mongo-safe-load

## Decisiones

- Patrón staging + backup + rename en `storage/mongo.py::replace_collection(name, docs)`. Se prefiere a upsert masivo para no cambiar la semántica de los 11 loaders con drop: mantiene idempotencia por reemplazo completo, pero sin ventana vacía.
- `replace_collection` aborta con 0 si docs está vacío. Los loaders que ya verificaban docs vacíos pasan a delegar en el helper; los que hacían drop antes de construir también.
- Backup con `db[name].aggregate([{"$out": name__backup}])` previa al rename. Volumen por colección máximo 5040 docs, acotado. Una sola generación de respaldo, sobrescrita en cada carga.
- Índices: el loader no los gestiona hoy. Tras el swap los índices desaparecen, como hoy tras drop. `load_all` llamará a `ensure_indexes` si está disponible, con import diferido para evitar ciclos. Si falla, la carga de datos ya ocurrió y se reporta en el log.
- zfill: normalizar con `int(float(text))` cuando text se parsea como entero con decimales ".0" o cuando value es float/int. Los valores no numéricos mantienen el comportamiento actual (devolver el texto).
- Tests: guarda con `pytest.mark.skipif` por variable de entorno, no monkeypatch de conexión. Simple y explícito; la creación de una base de test efímera queda fuera de alcance.

## Alternativas descartadas

- Transacción multidocumento: no disponible en un standalone local sin replica set; el swap con rename es suficiente.
- Upsert por _id en los 11 loaders: requeriría claves estables en colecciones sin _id homogéneo y cambiaría el contrato de conteos.
