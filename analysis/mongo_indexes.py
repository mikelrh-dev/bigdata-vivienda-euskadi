"""Index creation and explain() demonstrations for vivienda_euskadi."""

from __future__ import annotations

from typing import Any

from bson.decimal128 import Decimal128

from storage.mongo import get_collection, zfill_ine


def _winning_stage(plan: Any) -> str:
    if not isinstance(plan, dict):
        return str(plan)
    stage = plan.get("stage")
    if stage in {"COLLSCAN", "IXSCAN"}:
        return stage
    # recurse
    for key in ("inputStage", "innerStage", "outerStage"):
        if key in plan:
            found = _winning_stage(plan[key])
            if found in {"COLLSCAN", "IXSCAN"}:
                return found
    # search nested arrays/dicts
    for v in plan.values():
        if isinstance(v, dict):
            found = _winning_stage(v)
            if found in {"COLLSCAN", "IXSCAN"}:
                return found
        elif isinstance(v, list):
            for item in v:
                found = _winning_stage(item)
                if found in {"COLLSCAN", "IXSCAN"}:
                    return found
    return stage or "UNKNOWN"


def _explain(coll, filtro: dict[str, Any]) -> dict[str, Any]:
    db = coll.database
    exp = db.command("explain", {"find": coll.name, "filter": filtro}, verbosity="executionStats")
    stats = exp.get("executionStats", {})
    plan = exp.get("queryPlanner", {}).get("winningPlan", {})
    stage = _winning_stage(plan)
    if stage not in {"COLLSCAN", "IXSCAN"}:
        # fallback to executionStages top-level stage
        stage = exp.get("executionStats", {}).get("executionStages", {}).get("stage", stage)
    return {
        "stage": stage,
        "nReturned": stats.get("nReturned"),
        "totalDocsExamined": stats.get("totalDocsExamined"),
        "totalKeysExamined": stats.get("totalKeysExamined"),
        "executionTimeMillis": stats.get("executionTimeMillis"),
    }


def ensure_indexes() -> dict[str, Any]:
    an = get_collection("anuncios")
    mun = get_collection("municipios")
    al = get_collection("alquiler_municipal")
    out = {}
    out["anuncios_compound"] = str(an.create_index(
        [("ubicacion.codigo_ine", 1), ("modalidad", 1), ("precio_eur", 1)],
        name="idx_anuncios_ine_modalidad_precio",
    ))
    out["anuncios_geo"] = str(an.create_index(
        [("ubicacion.coordenadas", "2dsphere")], name="idx_anuncios_geo", sparse=True,
    ))
    out["anuncios_portal_id"] = str(an.create_index(
        [("portal", 1), ("id_anuncio", 1)], unique=True, name="idx_anuncios_portal_id",
    ))
    out["anuncios_equipamiento"] = str(an.create_index(
        [("equipamiento", 1)], name="idx_anuncios_equipamiento",
    ))
    out["municipios_territorio_nombre"] = str(mun.create_index(
        [("territorio", 1), ("nombre_canonico", 1)], name="idx_municipios_territorio_nombre",
    ))
    out["alquiler_codigo_distrito_seccion"] = str(al.create_index(
        [("codigo_ine", 1), ("distrito", 1), ("nivel_geografico", 1)],
        name="idx_alquiler_ine_distrito_nivel",
    ))
    return out


def drop_demo_index() -> None:
    an = get_collection("anuncios")
    try:
        an.drop_index("idx_anuncios_ine_modalidad_precio")
    except Exception:
        pass


def explain_before_after(codigo_ine: str = "48001", modalidad: str = "larga_estancia",
                         precio_max: Any = 1000) -> dict[str, Any]:
    """Drop index, explain (COLLSCAN), create index, explain (IXSCAN)."""
    an = get_collection("anuncios")
    code = zfill_ine(codigo_ine)
    precio = precio_max
    if not isinstance(precio, Decimal128):
        try:
            precio = Decimal128(str(precio))
        except Exception:
            pass
    filtro = {
        "ubicacion.codigo_ine": code,
        "modalidad": modalidad,
        "precio_eur": {"$lte": precio},
    }
    # before: ensure index absent
    drop_demo_index()
    before = _explain(an, filtro)
    # create
    an.create_index(
        [("ubicacion.codigo_ine", 1), ("modalidad", 1), ("precio_eur", 1)],
        name="idx_anuncios_ine_modalidad_precio",
    )
    after = _explain(an, filtro)
    return {"filtro": filtro, "before": before, "after": after}


def index_report() -> dict[str, Any]:
    an = get_collection("anuncios")
    return {
        "indexes": [i["name"] for i in an.list_indexes()],
        "explain": explain_before_after(),
    }


def run_all() -> dict[str, Any]:
    print(ensure_indexes())
    res = explain_before_after()
    print(res)
    return res


# Generic aliases
crear_indices = ensure_indexes
run_indexes = run_all

if __name__ == "__main__":
    run_all()
