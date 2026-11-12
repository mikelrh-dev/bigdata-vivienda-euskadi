"""Index creation and explain() demonstrations for vivienda_euskadi."""

from __future__ import annotations

from typing import Any

import logging
from decimal import InvalidOperation

from bson.decimal128 import Decimal128

from storage.mongo import get_collection, zfill_ine

logger = logging.getLogger(__name__)


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


def _explain(coll, filtro: dict[str, Any],
             hint: dict[str, Any] | None = None) -> dict[str, Any]:
    """Explain read-only; ``hint`` permite forzar un plan (p. ej. $natural)."""
    db = coll.database
    cmd: dict[str, Any] = {"find": coll.name, "filter": filtro}
    if hint is not None:
        cmd["hint"] = hint
    exp = db.command("explain", cmd, verbosity="executionStats")
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
    out["promociones_codigo_estado_tipo"] = str(get_collection("etxebide_promociones").create_index(
        [("codigo_ine", 1), ("estado_obra", 1), ("tipologia", 1)],
        name="idx_promo_ine_estado_tipo",
    ))
    out["certificados_moda"] = str(get_collection("certificados_energeticos").create_index(
        [("cert_moda", 1)], name="idx_cert_moda",
    ))
    out["esfuerzo_mercado_2026_esfuerzo"] = str(get_collection("esfuerzo_mercado_2026").create_index(
        [("esfuerzo_mercado_2026_pct_18_34", 1)], name="idx_esfuerzo_2026_pct_18_34",
    ))
    out["esfuerzo_mercado_2026_territorio_nombre"] = str(get_collection("esfuerzo_mercado_2026").create_index(
        [("territorio", 1), ("nombre_canonico", 1)], name="idx_esfuerzo_2026_ter_nombre",
    ))
    return out


def explain_before_after(codigo_ine: str = "20069", modalidad: str = "larga_estancia",
                         precio_max: Any = 1000) -> dict[str, Any]:
    """Explain read-only COLLSCAN -> IXSCAN sin mutar la base productiva.

    El "antes" fuerza COLLSCAN con ``hint={"$natural": 1}`` (barrido completo,
    sin dropear el índice); el "después" usa el índice ESR presente, sin
    recrearlo. Filtro canónico ``20069`` (1 doc); ``48020`` -> 8; ``48001`` -> 0.
    """
    an = get_collection("anuncios")
    code = zfill_ine(codigo_ine)
    precio = precio_max
    if not isinstance(precio, Decimal128):
        try:
            precio = Decimal128(str(precio))
        except (TypeError, ValueError, InvalidOperation) as exc:
            logger.warning("explain_before_after: precio no numérico %r (%s)", precio, exc)
    filtro = {
        "ubicacion.codigo_ine": code,
        "modalidad": modalidad,
        "precio_eur": {"$lte": precio},
    }
    before = _explain(an, filtro, hint={"$natural": 1})
    after = _explain(an, filtro)
    return {"filtro": filtro, "before": before, "after": after}


def explain_promo_before_after(codigo_ine: str = "48020") -> dict[str, Any]:
    """Explain read-only para etxebide_promociones por municipio.

    El "antes" fuerza COLLSCAN con ``hint={"$natural": 1}``; el "después" usa
    el índice ``idx_promo_ine_estado_tipo`` presente. No dropea ni crea índices.
    """
    coll = get_collection("etxebide_promociones")
    code = zfill_ine(codigo_ine)
    filtro = {"codigo_ine": code}
    before = _explain(coll, filtro, hint={"$natural": 1})
    after = _explain(coll, filtro)
    return {"filtro": filtro, "before": before, "after": after}


def index_report() -> dict[str, Any]:
    """Estado read-only de índices y explains (no muta prod)."""
    an = get_collection("anuncios")
    return {
        "indexes": [i["name"] for i in an.list_indexes()],
        "explain": explain_before_after(),
        "explain_promo": explain_promo_before_after(),
    }


def run_all() -> dict[str, Any]:
    """Demo read-only del explain: no crea ni dropea índices en prod."""
    res = explain_before_after()
    print(res)
    return res


# Generic aliases
crear_indices = ensure_indexes
run_indexes = run_all

if __name__ == "__main__":
    run_all()
