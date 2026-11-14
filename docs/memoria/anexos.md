<!-- cap: 9 | titulo: Anexos | criterios: Trazabilidad | estado: borrador -->
# 9. Anexos

## A. Glosario

| Término | Definición |
|---|---|
| `codigo_ine` | Código oficial de cinco dígitos que identifica un municipio |
| Raw | Copia inmutable del original, con SHA-256 y `.FROZEN` |
| Silver | CSV normalizado y cruzado por `codigo_ine` |
| Gold | CSV y PNG listos para el informe |
| Tier | Nivel de confianza A/B/C/D según cobertura y muestra |
| IDW | Interpolación por distancia inversa para municipios sin alquiler oficial |
| Esfuerzo | Porcentaje de la renta que consume el alquiler |

## B. Fragmentos de código

**Carga idempotente** (`storage/mongo.py:152`). La colección se construye en staging, la anterior se copia a backup y el rename publica el resultado de una vez.

```python
def replace_collection(name, docs):
    db = get_db()
    staging = f"{name}__staging"
    backup = f"{name}__backup"
    db[staging].drop()
    db[staging].insert_many(docs)
    if name in db.list_collection_names():
        db[backup].drop()
        db[name].aggregate([{"$out": backup}])
    db[staging].rename(name, dropTarget=True)
    return len(docs)
```

**Explain antes/después** (`analysis/mongo_indexes.py:125`). El `hint` fuerza el barrido completo; la segunda llamada usa el índice ESR.

```python
filtro = {
    "ubicacion.codigo_ine": "20069",
    "modalidad": "larga_estancia",
    "precio_eur": {"$lte": Decimal128("1000")},
}
antes = _explain(an, filtro, hint={"$natural": 1})  # COLLSCAN 594
despues = _explain(an, filtro)                     # IXSCAN 1
```

**CRUD y comprobación** (`storage/clean_mongo.py:311`). Las cuatro operaciones se ejecutan sobre una colección temporal que se borra al final.

```python
coll.insert_one({"nombre": "demo", "precio": 100})
coll.find_one({"nombre": "demo"}, {"_id": 0})
coll.update_one({"nombre": "demo"}, {"$set": {"precio": 120}, "$inc": {"visitas": 1}})
coll.delete_one({"nombre": "x"})
```

**Tier y `n_precio`** (`analysis/mongo_aggregations.py:658`). El tier sale solo de `n_anuncios`; en C y D el precio municipal se anula por diseño.

```python
{"$addFields": {
    "tier": _tier_expr(),  # A >=30, B 10-29, C 1-9, D 0
    "n_precio": {"$cond": [{"$in": ["$tier", ["A", "B"]]}, "$_n_precio", 0]},
}}
```
