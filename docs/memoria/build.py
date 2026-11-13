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

CIFRAS = MEM / "_cifras.json"
CIFRAS_MD = MEM / "_cifras.md"
DOC = MEM / "_documento.json"
FIG = MEM / "figuras"
RES = ROOT / "data" / "resultados"
ANEXO = RES / "anexo"
FACTS_SRC = ROOT / "vaultVivienda" / "notebooklm" / "NB04-BDA-Mongo" / "_facts.json"

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
    "verif.tests_passed": (285, "int", "pytest -q tests · 2026-11-13"),
    "verif.tests_skipped": (2, "int", "pytest -q tests · 2026-11-13"),
    "verif.tests_collected": (287, "int", "pytest -q tests · 2026-11-13"),
    "verif.gobernanza_cabeceras": (53, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
    "verif.gobernanza_ids": (49, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
    "verif.gobernanza_scripts": (47, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
    "verif.gobernanza_dag": (40, "int", "scripts/verificar_gobernanza.py · 2026-11-13"),
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
    import pandas as pd

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
    vc = t["tier"].value_counts()
    for letra in ("A", "B", "C", "D"):
        add(f"datos.tier_{letra.lower()}", int(vc.get(letra, 0)), "int", f"mongo_tier_confianza.csv · tier {letra}")

    h = _csv("mongo_habitaciones_por_municipio.csv")
    add("datos.habitaciones_municipios", len(h), "int", "mongo_habitaciones_por_municipio.csv · filas")

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

    parts = [
        "<!-- GENERADO por docs/memoria/build.py. No editar a mano. -->",
        "---",
        f'title: "{title}"',
        f'subtitle: "{subtitle}"',
        f'author: "{author}"',
        f'date: "{doc["fecha"]}"',
        f'lang: {doc.get("idioma", "es")}',
        "---",
        "",
        "> Cifras verificadas el "
        f"{doc['fecha']}. Fuente única: `docs/memoria/_cifras.json`.",
        "",
        "# Índice",
        "",
    ]
    for _, meta, _ in chapters:
        parts.append(f"{meta['cap']}. {meta['titulo']}")
    parts.append("")

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
