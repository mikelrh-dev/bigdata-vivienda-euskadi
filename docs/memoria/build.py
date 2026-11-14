#!/usr/bin/env python3
"""Gestión de la memoria: cifras, tokens y exportación.

Uso:
    python docs/memoria/build.py --refresh   # recalcula _cifras.json desde Mongo/CSV
    python docs/memoria/build.py --check     # valida tokens, figuras y metadatos
    python docs/memoria/build.py --build     # genera memoria.md + DOCX + HTML
    python docs/memoria/build.py --pdf       # genera memoria.pdf con Chrome
    python docs/memoria/build.py --all       # refresh + build + pdf

Regla: los capítulos no teclean cifras. Usan {{clave}} y build.py las resuelve
desde _cifras.json. Las claves infra.* y verif.* son manuales y se conservan
entre refrescos; el resto se recalcula.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEM = Path(__file__).resolve().parent

VINTAGE = ROOT / "config" / "vintage_figuras.yaml"
CIFRAS = MEM / "_cifras.json"
CIFRAS_MD = MEM / "_cifras.md"
DOC = MEM / "_documento.json"
FIG = MEM / "figuras"
RES = ROOT / "data" / "resultados"
ANEXO = RES / "anexo"
FACTS_SRC = ROOT / "vaultVivienda" / "notebooklm" / "NB04-BDA-Mongo" / "_facts.json"

# Municipios oficiales de 2024 con esfuerzo superior al 35 %, en el orden en
# que se publican (descendente). No es una lista de "municipios interesantes"
# ni un top-N elegido a mano: es el corte por umbral de
# `pipeline_top_municipios_por_esfuerzo`, y `_validate` lo recalcula desde el
# CSV. Con top-12 el 12.º (Portugalete 35,65) quedaba a 0,03 pp de Lezo
# (35,62), un corte que la precision publicada no sostiene; con el umbral
# entran los dos y el margen del corte es de 0,45 pp (Irun 35,44 / Urduliz
# 34,99).
UMBRAL_RANKING_2024 = 35.0
RANKING_2024 = (
    "barakaldo", "donostia", "sestao", "bilbao", "erandio", "pasaia",
    "lasarte_oria", "errenteria", "astigarraga", "basauri", "santurtzi",
    "portugalete", "lezo", "irun",
)

TOKEN_RE = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")
META_RE = re.compile(
    r"<!--\s*cap:\s*(\d+)\s*\|\s*titulo:\s*(.+?)\s*\|\s*"
    r"criterios:\s*(.+?)\s*\|\s*estado:\s*(.+?)\s*-->"
)
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")

CHROME_CANDIDATES = (
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
)

MANUAL_DEFAULT = {
    "infra.hdfs_objetos": (353, "int", "GETCONTENTSUMMARY /data/raw · 2026-11-13"),
    "infra.hdfs_bytes": (895597901, "int", "GETCONTENTSUMMARY /data/raw · 2026-11-13"),
    "infra.kafka_topic": ("vivienda_euskadi", "str", "KafkaAdminClient.describe_topics · 2026-11-13"),
    "infra.kafka_particiones": (1, "int", "KafkaAdminClient.describe_topics · 2026-11-13"),
    "infra.kafka_factor_replicacion": (1, "int", "KafkaAdminClient.describe_topics · 2026-11-13"),
    "verif.tests_passed": (293, "int", "pytest -q tests · 2026-11-14"),
    "verif.tests_skipped": (2, "int", "pytest -q tests · 2026-11-14"),
    "verif.tests_collected": (295, "int", "pytest -q tests · 2026-11-14"),
    "verif.gobernanza_cabeceras": (53, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
    "verif.gobernanza_ids": (49, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
    "verif.gobernanza_scripts": (47, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
    "verif.gobernanza_dag": (40, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
    "verif.deck_checks": (41, "int", "scripts/verificar_cifras_deck.py · 2026-11-13"),
}

GROUP_LABELS = {
    "mongo": "MongoDB",
    "datos": "Datos y análisis",
    "gold": "Gold",
    "raw": "Raw",
    "silver": "Silver",
    "infra": "Infraestructura (manual)",
    "verif": "Verificación (manual)",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fmt(valor, formato: str = "str") -> str:
    """Formato español: miles con punto y decimales con coma."""
    if formato == "int":
        return f"{int(valor):,}".replace(",", ".")
    if formato in ("1d", "2d"):
        decimales = int(formato[0])
        return f"{float(valor):,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(valor)


def _facts() -> dict:
    if not FACTS_SRC.exists():
        raise SystemExit(
            f"No existe {FACTS_SRC}.\n"
            "Genera el acta con 'python scripts/nb_acta_mongo.py' o ajusta FACTS_SRC."
        )
    return _load_json(FACTS_SRC)


def _docs(facts: dict, name: str) -> int | None:
    for col in facts.get("collections", []):
        if col.get("name") == name:
            return int(col.get("docs", 0))
    return None


def _vpo_sin_dato(default: int = 406) -> int:
    try:
        sys.path.insert(0, str(ROOT))
        from storage.mongo import get_db  # noqa: WPS433 (import deliberado y opcional)

        return int(
            get_db()["etxebide_promociones"].count_documents(
                {
                    "$or": [
                        {"NumViviendas": {"$exists": False}},
                        {"NumViviendas": None},
                        {"NumViviendas": ""},
                    ]
                }
            )
        )
    except Exception:
        return default


def _csv(name: str):
    import pandas as pd

    return pd.read_csv(RES / name, encoding="utf-8-sig")


def refresh() -> None:
    """Recalcula las cifras automáticas y conserva las manuales."""
    facts = _facts()
    prev = _load_json(CIFRAS).get("cifras", {}) if CIFRAS.exists() else {}
    c: dict[str, dict] = {}

    def add(key: str, valor, formato: str, fuente: str) -> None:
        c[key] = {"valor": valor, "formato": formato, "fuente": fuente}

    # --- MongoDB ---------------------------------------------------------
    add("mongo.vivas", facts["collections_live"], "int", "_facts.json · collections_live")
    add("mongo.backup", facts["collections_backup"], "int", "_facts.json · collections_backup")
    add("mongo.total", facts["collections_total"], "int", "_facts.json · collections_total")
    add("mongo.indices_definidos", len(facts["defined_indexes"]), "int", "_facts.json · defined_indexes")
    add(
        "mongo.indices_creados",
        len(facts["defined_indexes"]) - len(facts["defined_indexes_missing"]),
        "int",
        "_facts.json · defined_indexes - defined_indexes_missing",
    )
    add("mongo.pipelines", len(facts["pipelines"]["ordered"]), "int", "_facts.json · pipelines.ordered")
    add("mongo.pipelines_total", len(facts["pipelines"]["defined"]), "int", "_facts.json · pipelines.defined")
    add(
        "mongo.pipelines_fuera_orden",
        len(facts["pipelines"]["outside_order"]),
        "int",
        "_facts.json · pipelines.outside_order",
    )
    add("mongo.csv_salidas", len(facts["pipelines"]["csv_outputs"]), "int", "_facts.json · pipelines.csv_outputs")

    hab = _docs(facts, "anuncios_habitaciones_unificados")
    if hab is not None:
        add("mongo.habitaciones", hab, "int", "_facts.json · anuncios_habitaciones_unificados.docs")
    for nombre, key in (
        ("municipios", "mongo.municipios_docs"),
        ("anuncios", "mongo.anuncios_docs"),
        ("certificados_energeticos", "mongo.certificados_docs"),
        ("vpo_municipal", "mongo.vpo_municipal_docs"),
        ("esfuerzo_mercado_2026", "mongo.esfuerzo_2026_docs"),
    ):
        docs = _docs(facts, nombre)
        if docs is not None:
            add(key, docs, "int", f"_facts.json · {nombre}.docs")

    # --- Esfuerzo y oferta ----------------------------------------------
    e = _csv("mongo_esfuerzo_por_municipio.csv")
    of = e[e["tiene_alquiler_oficial"].astype(str).str.lower().isin(["true", "1"])]
    med_of = float(of["esfuerzo_joven_pct_18_34"].median())
    med_idw = float(e["esfuerzo_joven_pct_18_34"].median())
    sobre30_of = int((of["esfuerzo_joven_pct_18_34"] > 30).sum())
    sobre30_idw = int((e["esfuerzo_joven_pct_18_34"] > 30).sum())

    add("datos.alquiler_oficial", len(of), "int", "mongo_esfuerzo_por_municipio.csv · tiene_alquiler_oficial")
    add(
        "datos.alquiler_imputado",
        len(e) - len(of),
        "int",
        "mongo_esfuerzo_por_municipio.csv · 252 - oficiales",
    )
    add("datos.municipios", len(e), "int", "mongo_esfuerzo_por_municipio.csv · filas")
    add("datos.esfuerzo_mediana_oficial", med_of, "2d", "mediana de esfuerzo_joven_pct_18_34 · oficiales")
    add("datos.esfuerzo_oficial_sobre30", sobre30_of, "int", "esfuerzo_joven_pct_18_34 > 30 · oficiales")
    add(
        "datos.esfuerzo_oficial_sobre30_pct",
        sobre30_of / len(of) * 100,
        "2d",
        "sobre30 / oficiales * 100",
    )
    add("datos.esfuerzo_mediana_idw", med_idw, "2d", "mediana de esfuerzo_joven_pct_18_34 · 252 municipios")
    add("datos.esfuerzo_idw_sobre30", sobre30_idw, "int", "esfuerzo_joven_pct_18_34 > 30 · 252 municipios")
    add(
        "datos.idw_suma_sobre30",
        sobre30_idw - sobre30_of,
        "int",
        "municipios que la imputacion empuja por encima del 30 % (47 - 40)",
    )
    add(
        "datos.esfuerzo_idw_sobre30_pct",
        sobre30_idw / len(e) * 100,
        "2d",
        "sobre30 / 252 * 100",
    )

    add("datos.anuncios_total", int(e["n_anuncios"].sum()), "int", "mongo_esfuerzo_por_municipio.csv · n_anuncios")
    add("datos.anuncios_larga", int(e["n_larga_estancia"].sum()), "int", "n_larga_estancia")
    add("datos.anuncios_temporal", int(e["n_temporal"].sum()), "int", "n_temporal")
    add("datos.anuncios_municipios", int((e["n_anuncios"] > 0).sum()), "int", "municipios con n_anuncios > 0")
    add(
        "datos.anuncios_larga_municipios",
        int((e["n_larga_estancia"] > 0).sum()),
        "int",
        "municipios con n_larga_estancia > 0",
    )
    add(
        "datos.anuncios_temporal_municipios",
        int((e["n_temporal"] > 0).sum()),
        "int",
        "municipios con n_temporal > 0",
    )
    add("datos.anuncios_sin", int((e["n_anuncios"] == 0).sum()), "int", "municipios sin anuncio")
    add(
        "datos.precio_observable",
        int(e["precio_medio_eur"].notna().sum()),
        "int",
        "precio_medio_eur no nulo",
    )

    t = _csv("mongo_tier_confianza.csv")
    t["codigo_ine"] = t["codigo_ine"].astype(str).str.zfill(5)
    tier_por_codigo = dict(zip(t["codigo_ine"], t["tier"]))
    vc = t["tier"].value_counts()
    for letra in ("A", "B", "C", "D"):
        add(f"datos.tier_{letra.lower()}", int(vc.get(letra, 0)), "int", f"mongo_tier_confianza.csv · tier {letra}")
    add(
        "datos.tier_ab",
        int(vc.get("A", 0) + vc.get("B", 0)),
        "int",
        "mongo_tier_confianza.csv · A + B",
    )
    add(
        "datos.n_precio_positivo",
        int((e["n_precio"] > 0).sum()),
        "int",
        "mongo_esfuerzo_por_municipio.csv · n_precio > 0",
    )
    add(
        "datos.precio_sin_muestra",
        int(e["precio_medio_eur"].notna().sum()) - int((e["n_precio"] > 0).sum()),
        "int",
        "precio_medio_eur no nulo con n_precio = 0 (Tier C/D)",
    )

    h = _csv("mongo_habitaciones_por_municipio.csv")
    add("datos.habitaciones_municipios", len(h), "int", "mongo_habitaciones_por_municipio.csv · filas")

    # Habitaciones (HAB-02). La seccion "compartir vivienda" mezcla habitaciones
    # con pisos enteros, asi que el pipeline descarta el anuncio cuyo precio
    # alcanza el alquiler mediano de vivienda del municipio (`_hab_tope_stages`)
    # y `n_precio` pasa a contar solo los utilizables.
    utilizables = int(h["n_precio"].sum())
    descartados = int(h["n_descartados_precio"].sum())
    add(
        "datos.habitaciones_utilizables",
        utilizables,
        "int",
        "mongo_habitaciones_por_municipio.csv · suma de n_precio (plausibles)",
    )
    add(
        "datos.habitaciones_descartados",
        descartados,
        "int",
        "mongo_habitaciones_por_municipio.csv · suma de n_descartados_precio",
    )
    add(
        "datos.habitaciones_descartados_pct",
        descartados / (descartados + utilizables) * 100,
        "1d",
        "n_descartados_precio / anuncios con precio (mongo_habitaciones_por_municipio.csv)",
    )

    # Mediana global sobre precios individuales: al silver se le aplica el mismo
    # tope municipal que al pipeline, para no publicar un corte y calcular otro.
    import pandas as pd

    precios_hab = pd.read_csv(
        ROOT / "data" / "procesado" / "anuncios_habitaciones_unificados.csv",
        encoding="utf-8-sig",
        dtype={"codigo_ine": str},
    )
    precios_hab["precio_eur"] = pd.to_numeric(precios_hab["precio_eur"], errors="coerce")
    tope_por_municipio = dict(
        zip(h["codigo_ine"].astype(str).str.zfill(5), h["tope_alquiler_eur_mes"])
    )
    precios_hab["_tope"] = precios_hab["codigo_ine"].str.zfill(5).map(tope_por_municipio)
    precios_ok = precios_hab.loc[
        precios_hab["precio_eur"] < precios_hab["_tope"], "precio_eur"
    ].dropna()
    mediana_hab = float(precios_ok.median())
    add(
        "datos.habitaciones_mediana_global",
        mediana_hab,
        "int",
        "mediana de los precios plausibles (anuncios_habitaciones_unificados.csv + tope municipal)",
    )
    add(
        "datos.habitaciones_precio_max_bruto",
        float(precios_hab["precio_eur"].max()),
        "int",
        "anuncios_habitaciones_unificados.csv · precio_eur maximo de la coleccion bruta",
    )

    # Salario joven 2026 ajustado: misma fuente y estadistico que la capa 2026.
    mercado_2026 = pd.read_csv(
        ROOT / "data" / "procesado" / "esfuerzo_mercado_2026.csv", encoding="utf-8-sig"
    )
    salario_2026 = float(mercado_2026["salario_joven_2026_ajustado_18_34_eur_mes"].median())
    add(
        "datos.habitaciones_esfuerzo_global",
        mediana_hab / salario_2026 * 100,
        "1d",
        "mediana de habitacion plausible / salario joven 2026 ajustado",
    )

    for clave, municipio in (
        ("bilbao", "Bilbao"),
        ("donostia", "Donostia"),
        ("barakaldo", "Barakaldo"),
        ("vitoria", "Vitoria"),
        ("getxo", "Getxo"),
    ):
        fila = h[h["municipio"].astype(str).str.startswith(municipio)].iloc[0]
        mediana = float(fila["mediana_precio_eur"])
        add(
            f"datos.habitaciones_{clave}_mediana",
            mediana,
            "int",
            f"mongo_habitaciones_por_municipio.csv · mediana_precio_eur de {municipio}",
        )
        # Mismo denominador que la capa 2026 (salario joven ajustado), para que
        # el esfuerzo de habitacion y el de piso entero se puedan leer juntos.
        add(
            f"datos.habitaciones_{clave}_n",
            int(fila["n_precio"]),
            "int",
            f"mongo_habitaciones_por_municipio.csv · n_precio de {municipio}",
        )
        add(
            f"datos.habitaciones_{clave}_esfuerzo",
            mediana / salario_2026 * 100,
            "1d",
            f"mediana de {municipio} / salario joven 2026 ajustado",
        )
        if clave in ("bilbao", "donostia"):
            tope = float(fila["tope_alquiler_eur_mes"])
            add(
                f"datos.habitaciones_{clave}_tope",
                tope,
                "int",
                f"mongo_habitaciones_por_municipio.csv · tope_alquiler_eur_mes de {municipio} (alquiler mediano de vivienda)",
            )
            add(
                f"datos.habitaciones_{clave}_ahorro_pct",
                (1 - mediana / tope) * 100,
                "1d",
                f"1 - mediana_precio_eur / tope_alquiler_eur_mes de {municipio}",
            )

    modal = _csv("mongo_modalidades.csv")
    larga = modal[modal["modalidad"] == "larga_estancia"].iloc[0]
    temporal = modal[modal["modalidad"] == "temporal"].iloc[0]
    add(
        "datos.modalidad_mediana_eur_mes",
        float(larga["mediana_precio_eur"]),
        "int",
        "mongo_modalidades.csv · mediana_precio_eur de larga_estancia",
    )
    add(
        "datos.modalidad_larga_eur_m2",
        float(larga["mediana_eur_m2"]),
        "2d",
        "mongo_modalidades.csv · mediana_eur_m2 de larga_estancia",
    )
    add(
        "datos.modalidad_temporal_eur_m2",
        float(temporal["mediana_eur_m2"]),
        "2d",
        "mongo_modalidades.csv · mediana_eur_m2 de temporal",
    )
    add(
        "datos.modalidad_temporal_sobrecoste_pct",
        (float(temporal["mediana_eur_m2"]) / float(larga["mediana_eur_m2"]) - 1) * 100,
        "1d",
        "temporal / larga - 1 en mediana_eur_m2",
    )
    add(
        "datos.modalidad_larga_superficie",
        float(larga["mediana_superficie_m2"]),
        "int",
        "mongo_modalidades.csv · mediana_superficie_m2 de larga_estancia",
    )
    add(
        "datos.modalidad_temporal_superficie",
        float(temporal["mediana_superficie_m2"]),
        "int",
        "mongo_modalidades.csv · mediana_superficie_m2 de temporal",
    )

    add(
        "datos.vpo_promociones",
        _docs(facts, "etxebide_promociones") or 406,
        "int",
        "_facts.json · etxebide_promociones.docs",
    )
    add(
        "datos.vpo_sin_dato",
        _vpo_sin_dato(),
        "int",
        "etxebide_promociones · NumViviendas ausente o nulo",
    )

    # --- Municipios clave (Tier A/B de 2026 y corte >=35 % de 2024) --------
    e5 = e.copy()
    e5["_id5"] = e5["_id"].astype(str).str.zfill(5)
    # Slugs con token de esfuerzo: los siete Tier A/B de 2026 (comparacion de
    # oferta) mas los oficiales de 2024 que sostienen la tabla de §6.2.
    clave = {
        "barakaldo": "48013",
        "donostia": "20069",
        "sestao": "48084",
        "bilbao": "48020",
        "erandio": "48902",
        "pasaia": "20064",
        "lasarte_oria": "20902",
        "errenteria": "20067",
        "astigarraga": "20903",
        "basauri": "48015",
        "santurtzi": "48082",
        "portugalete": "48078",
        "lezo": "20053",
        "irun": "20045",
        "getxo": "48044",
        "vitoria": "01059",
    }
    for slug, code in clave.items():
        fila = e5[e5["_id5"] == code].iloc[0]
        add(
            f"datos.mun_{slug}_esfuerzo",
            float(fila["esfuerzo_joven_pct_18_34"]),
            "2d",
            f"mongo_esfuerzo_por_municipio.csv · {code}",
        )
        if slug in RANKING_2024:
            add(
                f"datos.mun_{slug}_alquiler",
                float(fila["cuantia_alquiler_mes"]),
                "int",
                f"mongo_esfuerzo_por_municipio.csv · {code} · cuantia_alquiler_mes",
            )
            # Cobertura 2026 de la tabla de 2024: el total de anuncios y su Tier.
            # No es la muestra comparable de §6.5 (Bilbao 204 aqui, 68 alli).
            add(
                f"datos.mun_{slug}_n_cobertura",
                int(fila["n_anuncios"]),
                "int",
                f"mongo_esfuerzo_por_municipio.csv · {code} · n_anuncios",
            )
            add(
                f"datos.mun_{slug}_tier_cobertura",
                str(tier_por_codigo.get(code, "s/t")),
                "str",
                f"mongo_tier_confianza.csv · {code} · tier",
            )

    # Tabla de la capa 2026 (§6.5): los cuatro Tier A con su muestra y su
    # esfuerzo de oferta. El `n` es el de anuncios válidos de larga estancia,
    # no el del Tier (Bilbao 68 frente a 204): ver el pie de la figura 6.10.
    comp = _csv("comparacion_esfuerzo_2024_2026.csv")
    comp["codigo_ine"] = comp["codigo_ine"].astype(str).str.zfill(5)
    for slug in ("bilbao", "donostia", "getxo", "vitoria"):
        fila = comp[comp["codigo_ine"] == clave[slug]].iloc[0]
        add(
            f"datos.mun_{slug}_n_2026",
            int(float(fila["n_anuncios_2026"])),
            "int",
            f"comparacion_esfuerzo_2024_2026.csv · {clave[slug]} · n_anuncios_2026",
        )
        add(
            f"datos.mun_{slug}_esfuerzo_2026",
            float(fila["esfuerzo_2026_base_salario_pct_18_34"]),
            "2d",
            f"comparacion_esfuerzo_2024_2026.csv · {clave[slug]} · esfuerzo 2026 base salario",
        )
        add(
            f"datos.mun_{slug}_precio_2026",
            float(fila["precio_mediana_anuncio_2026_eur_mes"]),
            "2d",
            f"comparacion_esfuerzo_2024_2026.csv · {clave[slug]} · precio mediano 2026",
        )

    # --- Cobertura de la capa 2026 ----------------------------------------
    # La cobertura se mide en población joven, no en municipios: 50 de 252
    # municipios son el 71 % de la población 18-34, y por eso la capa se lee.
    cob = _csv("cobertura_representatividad_2026.csv")
    cob_m = {str(f["metrica"]): f["valor"] for f in cob.to_dict("records")}
    add(
        "datos.cobertura_municipios_pct",
        float(cob_m["pct_municipios_cubiertos"]),
        "2d",
        "cobertura_representatividad_2026.csv · pct_municipios_cubiertos",
    )
    add(
        "datos.cobertura_poblacion_pct",
        float(cob_m["pct_poblacion_18_34_cubierta"]),
        "2d",
        "cobertura_representatividad_2026.csv · pct_poblacion_18_34_cubierta",
    )
    add(
        "datos.cobertura_poblacion",
        int(float(cob_m["poblacion_18_34_cubierta"])),
        "int",
        "cobertura_representatividad_2026.csv · poblacion_18_34_cubierta",
    )
    add(
        "datos.cobertura_anuncios_n30_pct",
        float(cob_m["pct_anuncios_en_municipios_n_mayor_igual_30"]),
        "2d",
        "cobertura_representatividad_2026.csv · pct_anuncios_en_municipios_n_mayor_igual_30",
    )
    add(
        "datos.sesgo_superficie_anuncios",
        float(cob_m["superficie_mediana_anuncios"]),
        "1d",
        "cobertura_representatividad_2026.csv · superficie_mediana_anuncios",
    )
    add(
        "datos.sesgo_superficie_oficial",
        float(cob_m["superficie_mediana_oficial_2024"]),
        "1d",
        "cobertura_representatividad_2026.csv · superficie_mediana_oficial_2024",
    )

    # Diferencia de NIVEL 2024 -> 2026 (no variación temporal): mediana de los
    # municipios con muestra suficiente para que la comparación signifique algo.
    br = _csv("brecha_esfuerzo_2024_2026.csv")
    brechas = []
    for fila in br.to_dict("records"):
        try:
            n_fila = float(fila.get("n_anuncios_2026") or 0)
            valor = float(fila.get("brecha_pp_18_34"))
        except (TypeError, ValueError):
            continue
        if n_fila >= 5:
            brechas.append(valor)
    brechas.sort()
    if brechas:
        medio = len(brechas) // 2
        mediana_brecha = (
            brechas[medio]
            if len(brechas) % 2
            else (brechas[medio - 1] + brechas[medio]) / 2
        )
        add(
            "datos.brecha_mediana_n5",
            mediana_brecha,
            "1d",
            "brecha_esfuerzo_2024_2026.csv · mediana de brecha_pp_18_34 con n>=5",
        )
        add(
            "datos.brecha_municipios_n5",
            len(brechas),
            "int",
            "brecha_esfuerzo_2024_2026.csv · municipios con n>=5",
        )

    # --- Capa 2026 --------------------------------------------------------
    r26 = _csv("comparacion_esfuerzo_2024_2026_resumen.csv").set_index("metrica")
    for key, metrica, etiqueta in (
        ("datos.esfuerzo_2024_canonico", "esfuerzo_2024_canonico_pct_18_34", "2024 canónico"),
        ("datos.esfuerzo_2024_salario", "esfuerzo_2024_base_salario_pct_18_34", "2024 base salario"),
        ("datos.esfuerzo_2026_salario", "esfuerzo_2026_base_salario_pct_18_34", "2026 base salario"),
        ("datos.esfuerzo_2026_renta", "esfuerzo_2026_base_renta2024_pct_18_34", "2026 base renta 2024"),
    ):
        add(
            key,
            float(r26.loc[metrica, "mediana"]),
            "2d",
            f"comparacion_esfuerzo_2024_2026_resumen.csv · {etiqueta}",
        )
    add(
        "datos.municipios_2026",
        int(r26.loc["esfuerzo_2026_base_salario_pct_18_34", "n_municipios"]),
        "int",
        "comparacion_esfuerzo_2024_2026_resumen.csv · n_municipios",
    )
    add(
        "datos.anuncios_2026",
        int(r26.loc["esfuerzo_2026_base_salario_pct_18_34", "n_anuncios"]),
        "int",
        "comparacion_esfuerzo_2024_2026_resumen.csv · n_anuncios",
    )

    t26 = _csv("esfuerzo_por_tipo_nivel_anuncio_2026.csv").set_index("tipo_de_vivienda")
    for key, tipo in (("1_2", "1-2 hab"), ("3", "3 hab"), ("4", "4+ hab")):
        add(
            f"datos.esfuerzo_2026_tipo_{key}",
            float(t26.loc[tipo, "esfuerzo_mediana_anuncios_pct_18_34"]),
            "2d",
            f"esfuerzo_por_tipo_nivel_anuncio_2026.csv · {tipo}",
        )
        add(
            f"datos.anuncios_2026_tipo_{key}",
            int(t26.loc[tipo, "n_anuncios"]),
            "int",
            f"esfuerzo_por_tipo_nivel_anuncio_2026.csv · {tipo}",
        )

    # --- Ficheros --------------------------------------------------------
    raw = [p for p in (ROOT / "data" / "raw").rglob("*") if p.is_file()]
    add("raw.disco", len(raw), "int", "find data/raw -type f")
    add("raw.visibles", len([p for p in raw if not p.name.startswith(".")]), "int", "find data/raw -type f -not -name '.*'")
    manifest = ROOT / "docs" / "raw_manifest_sha256.txt"
    add("raw.manifest", len(manifest.read_text(encoding="utf-8").splitlines()), "int", "docs/raw_manifest_sha256.txt · líneas")

    silver_manifest = ROOT / "data" / "procesado" / "manifest_sha256.txt"
    add(
        "silver.manifest",
        len(silver_manifest.read_text(encoding="utf-8").splitlines()),
        "int",
        "data/procesado/manifest_sha256.txt · líneas",
    )
    add(
        "silver.disco",
        len([p for p in (ROOT / "data" / "procesado").rglob("*") if p.is_file()]),
        "int",
        "find data/procesado -type f",
    )

    add("gold.csv", len(list(RES.glob("*.csv"))), "int", "data/resultados/*.csv")
    add("gold.png", len(list(RES.glob("*.png"))), "int", "data/resultados/*.png")
    add("gold.anexo_png", len(list(ANEXO.glob("*.png"))), "int", "data/resultados/anexo/*.png")
    add("gold.artefactos", len(list(RES.glob("*.csv"))) + len(list(RES.glob("*.png"))), "int", "CSV + PNG de la raíz")

    # --- Manuales (se conservan si ya existen) ---------------------------
    for key, (valor, formato, fuente) in MANUAL_DEFAULT.items():
        if key in prev:
            c[key] = prev[key]
        else:
            c[key] = {"valor": valor, "formato": formato, "fuente": fuente}

    payload = {
        "_meta": {
            "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "fuente_mongo": str(FACTS_SRC.relative_to(ROOT)).replace("\\", "/"),
            "fuente_datos": "data/resultados/*.csv",
            "nota": (
                "Las claves infra.* y verif.* son manuales y se conservan entre refrescos; "
                "el resto se recalcula. No editar las claves automáticas."
            ),
        },
        "cifras": dict(sorted(c.items())),
    }
    _write_json(CIFRAS, payload)
    _write_cifras_md(payload)
    print(f"OK  {CIFRAS.relative_to(ROOT)}  ({len(c)} claves)")
    print(f"OK  {CIFRAS_MD.relative_to(ROOT)}")


def _write_cifras_md(payload: dict) -> None:
    meta = payload["_meta"]
    cifras = payload["cifras"]
    groups: dict[str, list[tuple[str, dict]]] = {}
    for key, value in cifras.items():
        groups.setdefault(key.split(".")[0], []).append((key, value))

    lines = [
        "# Cifras vigentes",
        "",
        f"Generado: `{meta['generado_utc']}` · Fuente: `{meta['fuente_mongo']}` + `data/resultados/`.",
        "",
        "> No editar a mano: se regenera con `python docs/memoria/build.py --refresh`.",
        "",
    ]
    for group in ("mongo", "datos", "gold", "raw", "silver", "infra", "verif"):
        if group not in groups:
            continue
        lines += [f"## {GROUP_LABELS.get(group, group)}", "", "| Clave | Valor | Fuente |", "|---|---:|---|"]
        for key, value in groups[group]:
            lines.append(f"| `{key}` | {fmt(value['valor'], value.get('formato', 'str'))} | {value.get('fuente', '')} |")
        lines.append("")
    CIFRAS_MD.write_text("\n".join(lines), encoding="utf-8")


def _chapters() -> list[tuple[Path, dict, str]]:
    files = sorted(MEM.glob("[0-9][0-9]-*.md")) + [MEM / "anexos.md"]
    out: list[tuple[Path, dict, str]] = []
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        match = META_RE.search(text)
        if not match:
            out.append((path, {"cap": 999, "titulo": path.stem, "criterios": "", "estado": "sin metadatos"}, text))
            continue
        out.append(
            (
                path,
                {
                    "cap": int(match.group(1)),
                    "titulo": match.group(2),
                    "criterios": match.group(3),
                    "estado": match.group(4),
                },
                text,
            )
        )
    out.sort(key=lambda item: item[1]["cap"])
    return out


def _check_ranking_2024(errors: list[str]) -> None:
    """La tabla de §6.2 debe ser el corte >=35 % oficial, en orden descendente.

    Protege el error que motivo rehacerla: elegir municipios por la muestra de
    2026 (Barakaldo quedaba fuera siendo el maximo de 2024), dejarlos en un
    orden que no es el del ranking, o cortar por longitud cuando el corte por
    umbral es el que se sostiene.
    """
    ruta = RES / "mongo_esfuerzo_por_municipio.csv"
    if not ruta.exists():
        errors.append(f"Falta {ruta.name}: no se puede verificar §6.2")
        return
    oficiales = sorted(
        (
            float(fila["esfuerzo_joven_pct_18_34"])
            for fila in _csv("mongo_esfuerzo_por_municipio.csv").to_dict("records")
            if str(fila.get("tiene_alquiler_oficial")) == "True"
            and fila.get("esfuerzo_joven_pct_18_34") not in (None, "")
        ),
        reverse=True,
    )
    esperado = [round(v, 2) for v in oficiales if v >= UMBRAL_RANKING_2024]
    cap = next((t for _, meta, t in _chapters() if meta.get("cap") == 6), "")
    # La tabla del ranking se reconoce por sus dos columnas (alquiler y
    # esfuerzo del mismo municipio): la tabla de la capa 2026 tambien lleva el
    # esfuerzo de 2024, pero no el alquiler oficial.
    filas = re.findall(
        r"^\|\s*[^|]+\|.*\{\{datos\.mun_(\w+)_alquiler\}\}.*\{\{datos\.mun_\1_esfuerzo\}\}",
        cap,
        re.M,
    )
    if tuple(filas) != RANKING_2024:
        errors.append(
            "06-resultados.md: la tabla de §6.2 no coincide con los municipios "
            f"oficiales de 2024 por encima del {UMBRAL_RANKING_2024:g} % "
            f"({' '.join(filas) or 'sin filas'})"
        )
        return
    cifras = _load_json(CIFRAS)["cifras"] if CIFRAS.exists() else {}
    real = [round(float(cifras[f"datos.mun_{slug}_esfuerzo"]["valor"]), 2)
            for slug in filas if f"datos.mun_{slug}_esfuerzo" in cifras]
    if real != esperado:
        errors.append(
            "06-resultados.md: §6.2 no está en el orden del ranking oficial de "
            f"2024 ({real} vs {esperado})"
        )


def _check_figuras_gold(errors: list[str]) -> None:
    """Las figuras de `figuras/` deben ser copia exacta de su origen en gold.

    El documento embebe copias, no el gold: sin esta comprobación se puede
    publicar un PDF con la versión anterior de una figura aunque el gold ya
    esté regenerado (pasó con H1 al rehacer el ranking de 2024).
    """
    import hashlib

    import yaml

    cfg = yaml.safe_load(VINTAGE.read_text(encoding="utf-8")) or {}
    for destino, origen_rel in (cfg.get("sincronizacion") or {}).get("memoria", {}).items():
        copia, origen = FIG / destino, ROOT / str(origen_rel)
        if not copia.exists():
            errors.append(f"figuras/{destino}: falta la copia para la memoria")
            continue
        if not origen.exists():
            errors.append(f"figuras/{destino}: falta el origen {origen_rel}")
            continue
        if hashlib.sha256(copia.read_bytes()).digest() != hashlib.sha256(
            origen.read_bytes()
        ).digest():
            errors.append(
                f"figuras/{destino}: no coincide con {origen_rel} "
                "(ejecuta scripts/sincronizar_figuras.py)"
            )


def _validate() -> list[str]:
    errors: list[str] = []
    if not CIFRAS.exists():
        return [f"Falta {CIFRAS.name}. Ejecuta --refresh."]
    cifras = _load_json(CIFRAS)["cifras"]
    chapters = _chapters()
    if not chapters:
        errors.append("No hay capítulos [0-9][0-9]-*.md")

    for path, meta, text in chapters:
        if meta["estado"] == "sin metadatos":
            errors.append(f"{path.name}: falta el comentario <!-- cap: ... -->")
            continue
        for token in TOKEN_RE.finditer(text):
            key = token.group(1)
            if key not in cifras:
                errors.append(f"{path.name}: token desconocido {{{{{key}}}}}")
        for img in IMG_RE.finditer(text):
            target = (MEM / img.group(1)).resolve()
            if not target.exists():
                errors.append(f"{path.name}: figura ausente {img.group(1)}")
        for marca in ("TODO", "TBD"):
            if marca in text:
                errors.append(f"{path.name}: contiene {marca}")

    if not DOC.exists():
        errors.append(f"Falta {DOC.name}")

    _check_ranking_2024(errors)
    _check_figuras_gold(errors)

    # Tokens declarados pero no usados: aviso, no error.
    used = {m.group(1) for _, _, text in chapters for m in TOKEN_RE.finditer(text)}
    unused = sorted(set(cifras) - used)
    if unused:
        print(f"AVISO  {len(unused)} cifras sin usar en los capítulos (normal en borrador).")

    return errors


def check() -> int:
    errors = _validate()
    if errors:
        print(f"FALLO  {len(errors)} problema(s):")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"OK  {len(_chapters())} capítulos · tokens y figuras resueltos")
    return 0


def _resolve(text: str, cifras: dict, errors: list[str], origen: str) -> str:
    def repl(match: re.Match) -> str:
        key = match.group(1)
        if key not in cifras:
            errors.append(f"{origen}: token desconocido {{{{{key}}}}}")
            return match.group(0)
        value = cifras[key]
        return fmt(value["valor"], value.get("formato", "str"))

    return TOKEN_RE.sub(repl, text)


def build() -> int:
    # Orden reproducible: gold -> sync -> documento. La sincronizacion va
    # ANTES de validar: si no, una figura regenerada bloquea la construccion en
    # vez de arreglarla, porque el gate detecta la copia vieja y nadie la copia.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from analysis.vintage_figuras import sincronizar

    sincronizar(verbose=False)

    errors = _validate()
    if errors:
        print(f"FALLO  no se construye: {len(errors)} problema(s)")
        for error in errors:
            print(f"  - {error}")
        return 1

    doc = _load_json(DOC)
    cifras = _load_json(CIFRAS)["cifras"]
    chapters = _chapters()
    title = doc["titulo"].replace('"', '\\"')
    subtitle = doc["subtitulo"].replace('"', '\\"')
    author = doc["autor"].replace('"', '\\"')

    front = (
        "---\n"
        f'title: "{title}"\n'
        f'subtitle: "{subtitle}"\n'
        f'author: "{author}"\n'
        f'date: "{doc["fecha"]}"\n'
        f'lang: {doc.get("idioma", "es")}\n'
        "---"
    )
    parts = [
        front,
        "<!-- GENERADO por docs/memoria/build.py. No editar a mano. -->",
        "> Cifras verificadas el "
        f"{doc['fecha']}. Fuente única: `docs/memoria/_cifras.json`.",
        "# Índice",
    ]
    parts.append("\n".join(f"{meta['cap']}. {meta['titulo']}" for _, meta, _ in chapters))
    parts.append(
        _resolve(
            "## Resumen\n\n"
            "El esfuerzo mediano en los {{datos.alquiler_oficial}} municipios con alquiler oficial "
            "es {{datos.esfuerzo_mediana_oficial}} %, pero {{datos.esfuerzo_oficial_sobre30}} "
            "({{datos.esfuerzo_oficial_sobre30_pct}} %) superan el 30 % de la renta. La evidencia "
            "sólida se limita a {{datos.tier_a}} municipios (Tier A de 2026); el Tier B, con 11 a 19 "
            "anuncios, queda como indicativo. Su esfuerzo de 2024 va "
            "de {{datos.mun_getxo_esfuerzo}} % en Getxo a {{datos.mun_donostia_esfuerzo}} % en Donostia; "
            "el máximo de la capa oficial es Barakaldo, {{datos.mun_barakaldo_esfuerzo}} %, que en 2026 "
            "no tiene muestra suficiente. "
            "La capa 2026, con {{datos.municipios_2026}} municipios y {{datos.anuncios_2026}} anuncios, "
            "da una mediana de {{datos.esfuerzo_2026_salario}} % con salario ajustado y "
            "{{datos.esfuerzo_2026_renta}} % con renta 2024; no es comparable con 2024 porque cambia "
            "la fuente del numerador. Las dos capas se presentan por separado, los municipios sin dato "
            "se declaran y la oferta de anuncios no sustituye al alquiler oficial.",
            cifras,
            errors,
            "resumen",
        )
    )

    for index, (path, meta, text) in enumerate(chapters):
        match = META_RE.search(text)
        body = text[match.end() :].lstrip("\n") if match else text
        body = _resolve(body, cifras, errors, path.name)
        if index > 0:
            parts.append('```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```')
        parts.append(body)

    memoria = "\n\n".join(parts).rstrip() + "\n"
    (MEM / "memoria.md").write_text(memoria, encoding="utf-8")
    print("OK  docs/memoria/memoria.md")

    reference = MEM / "reference.docx"
    if not reference.exists():
        with reference.open("wb") as handle:
            subprocess.run(
                ["pandoc", "--print-default-data-file", "reference.docx"],
                stdout=handle,
                check=True,
            )

    subprocess.run(
        ["pandoc", "memoria.md", "-o", "memoria.docx", f"--reference-doc={reference.name}"],
        cwd=MEM,
        check=True,
    )
    print("OK  docs/memoria/memoria.docx")

    subprocess.run(
        [
            "pandoc",
            "memoria.md",
            "-o",
            "memoria.html",
            "--standalone",
            "--css=estilo.css",
            "--metadata",
            f"title={doc['titulo']}",
        ],
        cwd=MEM,
        check=True,
    )
    print("OK  docs/memoria/memoria.html")

    if errors:
        print(f"FALLO  {len(errors)} token(s) sin resolver")
        for error in errors:
            print(f"  - {error}")
        return 1
    return 0


def pdf() -> int:
    html = MEM / "memoria.html"
    if not html.exists():
        print("FALLO  falta memoria.html. Ejecuta --build.")
        return 1
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    if chrome is None:
        print("FALLO  no encuentro Chrome en las rutas habituales.")
        return 1
    target = MEM / "memoria.pdf"
    subprocess.run(
        [
            str(chrome),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={target}",
            html.resolve().as_uri(),
        ],
        check=True,
    )
    print(f"OK  {target.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="recalcula _cifras.json")
    parser.add_argument("--check", action="store_true", help="valida tokens, figuras y metadatos")
    parser.add_argument("--build", action="store_true", help="genera memoria.md, DOCX y HTML")
    parser.add_argument("--pdf", action="store_true", help="genera memoria.pdf con Chrome")
    parser.add_argument("--all", action="store_true", help="refresh + build + pdf")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return 0

    if args.all:
        refresh()
        code = build()
        return code if code else pdf()

    if args.refresh:
        refresh()
    code = 0
    if args.check:
        code = max(code, check())
    if args.build:
        code = max(code, build())
    if args.pdf:
        code = max(code, pdf())
    return code


if __name__ == "__main__":
    raise SystemExit(main())
