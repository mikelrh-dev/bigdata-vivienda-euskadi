"""Advanced MongoDB queries for vivienda_euskadi."""

from __future__ import annotations

from typing import Any

from bson.decimal128 import Decimal128

from storage.mongo import get_collection, zfill_ine


def _money(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal128):
        return value
    try:
        return Decimal128(str(value))
    except Exception:
        return value


def _cursor_to_list(cursor) -> list[dict[str, Any]]:
    return list(cursor)


# ---------------------------------------------------------------------------
# Anuncios
# ---------------------------------------------------------------------------

def anuncios_por_municipio(
    codigo_ine: str,
    modalidad: str | None = None,
    precio_min: Any = None,
    precio_max: Any = None,
    equipamiento: Any = None,
    limit: int = 100,
    skip: int = 0,
    sort_field: str = "precio_eur",
    descending: bool = False,
) -> list[dict[str, Any]]:
    """Filter anuncios by nested ubicacion.codigo_ine plus optional conditions."""
    code = zfill_ine(codigo_ine)
    filtro: dict[str, Any] = {"ubicacion.codigo_ine": code}
    if modalidad is not None:
        filtro["modalidad"] = modalidad
    if precio_min is not None or precio_max is not None:
        rango: dict[str, Any] = {}
        if precio_min is not None:
            rango["$gte"] = _money(precio_min)
        if precio_max is not None:
            rango["$lte"] = _money(precio_max)
        filtro["precio_eur"] = rango
    if equipamiento is not None:
        if isinstance(equipamiento, (list, tuple, set)):
            filtro["equipamiento"] = {"$in": list(equipamiento)}
        else:
            filtro["equipamiento"] = equipamiento
    cursor = get_collection("anuncios").find(filtro)
    if sort_field:
        cursor = cursor.sort(sort_field, -1 if descending else 1)
    if skip:
        cursor = cursor.skip(skip)
    if limit is not None:
        cursor = cursor.limit(limit)
    return _cursor_to_list(cursor)


def anuncios_por_codigo_ine(*a, **k):
    return anuncios_por_municipio(*a, **k)


def find_anuncios_por_municipio(*a, **k):
    return anuncios_por_municipio(*a, **k)


def query_anuncios_por_municipio(*a, **k):
    return anuncios_por_municipio(*a, **k)


def dot_notation_municipio(codigo_ine: str, limit: int = 50) -> list[dict[str, Any]]:
    """Dot notation over embedded document."""
    code = zfill_ine(codigo_ine)
    return _cursor_to_list(
        get_collection("anuncios")
        .find({"ubicacion.codigo_ine": code}, {"_id": 0, "portal": 1, "modalidad": 1,
                                              "precio_eur": 1, "ubicacion.municipio": 1,
                                              "ubicacion.codigo_ine": 1})
        .limit(limit)
    )


def anuncios_con_equipamiento(item: str, limit: int = 100) -> list[dict[str, Any]]:
    """Array contains element."""
    return _cursor_to_list(
        get_collection("anuncios").find({"equipamiento": item}).limit(limit)
    )


def anuncios_array_contains(item: str, limit: int = 100):
    return anuncios_con_equipamiento(item, limit)


def anuncios_array_all(items: list[str], limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("anuncios").find({"equipamiento": {"$all": list(items)}}).limit(limit)
    )


def anuncios_array_elemmatch(cond: Any, limit: int = 100) -> list[dict[str, Any]]:
    if not isinstance(cond, dict):
        cond = {"$eq": cond}
    return _cursor_to_list(
        get_collection("anuncios").find({"equipamiento": {"$elemMatch": cond}}).limit(limit)
    )


def anuncios_array_size(n: int, limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("anuncios").find({"equipamiento": {"$size": n}}).limit(limit)
    )


def anuncios_exists(field: str, exists: bool = True, limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("anuncios").find({field: {"$exists": exists}}).limit(limit)
    )


def anuncios_type(field: str, bson_type: Any, limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("anuncios").find({field: {"$type": bson_type}}).limit(limit)
    )


def anuncios_regex(field: str, pattern: str, options: str = "i", limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("anuncios")
        .find({field: {"$regex": pattern, "$options": options}})
        .limit(limit)
    )


def anuncios_comparacion(field: str, op: str, value: Any, limit: int = 100) -> list[dict[str, Any]]:
    ops = {"gt": "$gt", "gte": "$gte", "lt": "$lt", "lte": "$lte", "ne": "$ne",
           "eq": "$eq", "in": "$in", "nin": "$nin"}
    if op not in ops:
        raise ValueError(f"op desconocido: {op}")
    v = value
    if "precio" in field and not isinstance(value, (list, tuple, set)):
        v = _money(value)
    if isinstance(value, (list, tuple, set)) and "precio" in field:
        v = [_money(x) for x in value]
    return _cursor_to_list(
        get_collection("anuncios").find({field: {ops[op]: v}}).limit(limit)
    )


def anuncios_logica_and(conditions: list[dict[str, Any]], limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("anuncios").find({"$and": conditions}).limit(limit)
    )


def anuncios_logica_or(conditions: list[dict[str, Any]], limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("anuncios").find({"$or": conditions}).limit(limit)
    )


def anuncios_proyeccion(campos: list[str], limit: int = 20, filtro: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    proj = {c: 1 for c in campos}
    proj["_id"] = 0
    q = filtro or {}
    return _cursor_to_list(get_collection("anuncios").find(q, proj).limit(limit))


def anuncios_ordenar_limitar(sort_field: str, limit: int = 20, descending: bool = True,
                            filtro: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    q = filtro or {}
    return _cursor_to_list(
        get_collection("anuncios").find(q).sort(sort_field, -1 if descending else 1).limit(limit)
    )


def anuncios_paginacion(skip: int, limit: int, filtro: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    q = filtro or {}
    return _cursor_to_list(get_collection("anuncios").find(q).skip(skip).limit(limit))


def anuncios_distinct(field: str) -> list[Any]:
    return get_collection("anuncios").distinct(field)


# ---------------------------------------------------------------------------
# Municipios
# ---------------------------------------------------------------------------

def municipios_por_territorio(territorio: str, limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("municipios").find({"territorio": territorio}).limit(limit)
    )


def municipios_regex_nombre(pattern: str, limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("municipios")
        .find({"nombre_canonico": {"$regex": pattern, "$options": "i"}})
        .limit(limit)
    )


def municipios_por_capital(capital: str, limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("municipios").find({"vivienda_contexto.capital_mas_cercana": capital}).limit(limit)
    )


# ---------------------------------------------------------------------------
# Alquiler
# ---------------------------------------------------------------------------

def alquiler_por_codigo(codigo_ine: str, limit: int = 100) -> list[dict[str, Any]]:
    code = zfill_ine(codigo_ine)
    return _cursor_to_list(get_collection("alquiler_municipal").find({"codigo_ine": code}).limit(limit))


def alquiler_por_nivel(nivel: str, limit: int = 100) -> list[dict[str, Any]]:
    return _cursor_to_list(
        get_collection("alquiler_municipal").find({"nivel_geografico": nivel}).limit(limit)
    )


# ---------------------------------------------------------------------------
# Existence / type summaries used by tests
# ---------------------------------------------------------------------------

def resumen_exists_type() -> dict[str, Any]:
    an = get_collection("anuncios")
    return {
        "total_anuncios": an.count_documents({}),
        "con_superficie": an.count_documents({"superficie_m2": {"$exists": True, "$ne": None}}),
        "sin_superficie": an.count_documents({"superficie_m2": None}),
        "precio_decimal": an.count_documents({"precio_eur": {"$type": "decimal"}}),
        "precio_null": an.count_documents({"precio_eur": None}),
        "coordenadas_exists": an.count_documents({"ubicacion.coordenadas": {"$exists": True}}),
        "barrio_exists": an.count_documents({"ubicacion.barrio": {"$exists": True}}),
    }


def busqueda_avanzada_demo() -> dict[str, Any]:
    code = "48001"  # Abadino
    return {
        "por_municipio": len(anuncios_por_municipio(code)),
        "dot_notation": len(dot_notation_municipio(code)),
        "equipamiento_exterior": len(anuncios_con_equipamiento("exterior")),
        "exists_superficie": len(anuncios_exists("superficie_m2", True)),
        "type_precio_decimal": len(anuncios_type("precio_eur", "decimal")),
        "regex_municipio_vitoria": len(anuncios_regex("ubicacion.municipio", "vitoria")),
        "proyeccion": len(anuncios_proyeccion(["portal", "modalidad", "precio_eur"], limit=5)),
        "ordenado": len(anuncios_ordenar_limitar("precio_eur", limit=5)),
        "paginacion": len(anuncios_paginacion(0, 5)),
    }


def run_all() -> dict[str, Any]:
    import pprint
    res = busqueda_avanzada_demo()
    pprint.pprint(res)
    return res


# Aliases for likely external names
query_anuncios_por_municipio_dot = dot_notation_municipio
find_anuncios_equipamiento = anuncios_con_equipamiento
query_exists = anuncios_exists
query_type = anuncios_type
query_regex = anuncios_regex
query_proyeccion = anuncios_proyeccion
query_sort_limit = anuncios_ordenar_limitar

# Generic aliases
anuncios_por_municipio_nested = anuncios_por_municipio
anuncios_filtro_anidado = anuncios_por_municipio

# Generic aliases
consultas = busqueda_avanzada_demo
run_queries = run_all
run_all_queries = run_all

if __name__ == "__main__":
    run_all()
