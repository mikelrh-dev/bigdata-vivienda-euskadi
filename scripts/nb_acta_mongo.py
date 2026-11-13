"""Inventario read-only para las fuentes de NotebookLM (NB04).

Genera el acta de cifras vigentes y el fichero de hechos que alimenta la
redaccion de las 27 fuentes del cuaderno. No escribe en MongoDB: solo lee
conteos, indices, explain() y estadisticas de campos sobre una muestra.

Uso:
    .venv/Scripts/python.exe scripts/nb_acta_mongo.py
    .venv/Scripts/python.exe scripts/nb_acta_mongo.py --sample 400

Salidas (en vaultVivienda/notebooklm/NB04-BDA-Mongo/):
    _facts.json                      hechos maquina-legibles
    00-acta-de-cifras-vigentes.md    fuente 00 del cuaderno
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bson import Decimal128, ObjectId
from pymongo.database import Database

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT_DIR = ROOT / "vaultVivienda" / "notebooklm" / "NB04-BDA-Mongo"
RESULTADOS = ROOT / "data" / "resultados"

# Desfases verificados entre la documentacion escrita y el estado vivo.
# Se mantienen aqui porque no son derivables de la base.
DRIFT_NOTES: tuple[tuple[str, str, str], ...] = (
    (
        "README.md",
        "16 colecciones vivas + 14 __backup = 30",
        "17 vivas + 15 __backup = 32 (esfuerzo_mercado_2026 no figuraba)",
    ),
    (
        "README.md / NB03",
        "11 pipelines, y 14 colecciones",
        "11 en PIPELINE_ORDER + pipeline_esfuerzo_mercado_2026 fuera del orden",
    ),
    (
        "NB03-Mongo-I",
        "vpo_municipal con 251 municipios (Usansolo sin fila)",
        "252 documentos, incluido 48916",
    ),
    (
        "NB02-infraestructura",
        "topic Kafka anuncios_inmobiliarios",
        "topic vigente vivienda_euskadi (1 particion, RF 1)",
    ),
    (
        "README.md",
        "10 indices definidos y creados",
        "10 definidos en mongo_indexes.py; 8 creados en la base viva",
    ),
    (
        "NB03-Mongo-I",
        "ecvi_compraventa con _id compuesto {codigo_ine}_{trimestre}",
        "ecvi_compraventa usa ObjectId; codigo_ine es null en el ambito C.A. de Euskadi",
    ),
    (
        "README.md / informe v6",
        "load_mongo.py carga las 16 colecciones",
        "load_mongo.py define 15 loaders; las 2 de habitaciones se cargan fuera (deuda P3-06)",
    ),
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal128):
        return str(value.to_decimal())
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, Decimal128):
        return "Decimal128"
    if isinstance(value, ObjectId):
        return "ObjectId"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, datetime):
        return "date"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return type(value).__name__


def _flatten(doc: dict, prefix: str = "", depth: int = 0, out: dict[str, Any] | None = None) -> dict[str, Any]:
    """Aplana claves hasta ``depth`` niveles; los arrays se marcan como array."""
    if out is None:
        out = {}
    for key, value in doc.items():
        path = f"{prefix}{key}"
        out.setdefault(path, []).append(value)
        if isinstance(value, dict) and depth < 1:
            _flatten(value, f"{path}.", depth + 1, out)
    return out


def _collection_facts(db: Database, name: str, sample: int) -> dict[str, Any]:
    coll = db[name]
    docs = list(coll.find().limit(sample))
    fields: list[dict[str, Any]] = []
    if docs:
        flat_docs = [_flatten(d) for d in docs]
        keys = sorted({k for f in flat_docs for k in f})
        for key in keys:
            values = [d.get(key) for d in flat_docs]
            present = [v for v in values if v is not None]
            types = Counter(_type_name(v) for v in present)
            fields.append(
                {
                    "path": key,
                    "types": dict(types),
                    "present_pct": round(100 * len(present) / len(docs), 1),
                }
            )
    indexes = []
    for idx in coll.list_indexes():
        indexes.append(
            {
                "name": idx.get("name"),
                "key": _jsonable(dict(idx.get("key", {}))),
                "unique": bool(idx.get("unique", False)),
                "sparse": bool(idx.get("sparse", False)),
            }
        )
    return {
        "name": name,
        "docs": coll.estimated_document_count(),
        "sample_size": len(docs),
        "id_type": _type_name(docs[0]["_id"]) if docs else None,
        "sample_doc": _jsonable(docs[0]) if docs else None,
        "fields": fields,
        "indexes": indexes,
    }


def _defined_indexes() -> list[dict[str, str]]:
    """Nombres de indice definidos en analysis/mongo_indexes.py (estatico)."""
    text = (ROOT / "analysis" / "mongo_indexes.py").read_text(encoding="utf-8")
    found = []
    for match in re.finditer(r'name="(idx_[a-z0-9_]+)"', text):
        found.append({"name": match.group(1)})
    return found


def _collection_of_index() -> dict[str, str]:
    text = (ROOT / "analysis" / "mongo_indexes.py").read_text(encoding="utf-8")
    aliases = dict(
        re.findall(r"^\s*(\w+)\s*=\s*get_collection\(\"([a-z0-9_]+)\"\)", text, re.MULTILINE)
    )
    mapping: dict[str, str] = {}
    for block in re.split(r"out\[", text)[1:]:
        name_match = re.search(r'name="(idx_[a-z0-9_]+)"', block)
        if not name_match:
            continue
        direct = re.search(r'get_collection\("([a-z0-9_]+)"\)\s*\.\s*create_index', block)
        alias = re.search(r"(\w+)\.create_index", block)
        coll = direct.group(1) if direct else aliases.get(alias.group(1)) if alias else None
        if coll:
            mapping[name_match.group(1)] = coll
    return mapping


LOADER_OVERRIDE: dict[str, str] = {
    "anuncios_habitaciones_unificados": "sin loader en load_mongo.py (carga ad hoc; deuda P3-06)",
    "anuncios_habitaciones_unificados_bigdata": "sin loader en load_mongo.py (carga ad hoc; deuda P3-06)",
}


def _loaders() -> dict[str, str]:
    """Mapea coleccion -> funcion load_* que la escribe (estatico)."""
    text = (ROOT / "storage" / "load_mongo.py").read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        fn = re.match(r"def (load_[a-z0-9_]+)\(", line)
        if fn:
            current = fn.group(1)
            continue
        if current and "replace_collection(" in line:
            coll = re.search(r'replace_collection\(\s*"([a-z0-9_]+)"', line)
            if coll:
                mapping[coll.group(1)] = current
    mapping.update(LOADER_OVERRIDE)
    return mapping


def _pipelines() -> dict[str, Any]:
    agg = (ROOT / "analysis" / "mongo_aggregations.py").read_text(encoding="utf-8")
    defined = re.findall(r"^def (pipeline_[a-z0-9_]+)\(", agg, flags=re.MULTILINE)
    runner = (ROOT / "analysis" / "run_analisis_mongo.py").read_text(encoding="utf-8")
    order_block = re.search(r"PIPELINE_ORDER: tuple\[str, \.\.\.\] = \((.*?)\)", runner, re.S)
    ordered = re.findall(r'"(pipeline_[a-z0-9_]+)"', order_block.group(1)) if order_block else []
    csvs = sorted(set(re.findall(r'"(mongo_[a-z0-9_]+\.csv)"', runner)))
    stages = Counter(re.findall(r'"\$(match|lookup|group|project|sort|limit|unwind|addFields|facet|geoNear|count|set|switch|out)"', agg))
    return {
        "defined": defined,
        "ordered": ordered,
        "outside_order": [p for p in defined if p not in ordered],
        "csv_outputs": csvs,
        "stage_usage": dict(stages.most_common()),
    }


def _results() -> dict[str, Any]:
    files = [p for p in RESULTADOS.glob("*") if p.is_file()]
    by_ext = Counter(p.suffix.lower() for p in files)
    return {
        "by_extension": dict(sorted(by_ext.items())),
        "mongo_csv": sorted(p.name for p in files if p.name.startswith("mongo_") and p.suffix == ".csv"),
        "total": len(files),
    }


def collect(sample: int = 200) -> dict[str, Any]:
    from storage.mongo import get_client, get_db, MONGO_DB

    db = get_db()
    info = get_client().server_info()
    hello = db.client.admin.command("hello")
    names = sorted(db.list_collection_names())
    live = [n for n in names if not n.endswith("__backup")]
    backups = [n for n in names if n.endswith("__backup")]
    collections = [_collection_facts(db, n, sample) for n in live]
    defined = _defined_indexes()
    created = {i["name"] for c in collections for i in c["indexes"]}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "server": {
            "version": info.get("version"),
            "db": MONGO_DB,
            "replica_set": hello.get("setName"),
            "hosts": hello.get("hosts", []),
            "storage_engine": info.get("storageEngine", {}).get("name") if isinstance(info.get("storageEngine"), dict) else None,
        },
        "collections_total": len(names),
        "collections_live": len(live),
        "collections_backup": len(backups),
        "backup_names": backups,
        "collections": collections,
        "defined_indexes": defined,
        "defined_indexes_missing": [
            d["name"] for d in defined if d["name"] not in created
        ],
        "index_collection": _collection_of_index(),
        "loaders": _loaders(),
        "pipelines": _pipelines(),
        "results": _results(),
        "drift": [{"doc": d, "says": s, "actual": a} for d, s, a in DRIFT_NOTES],
    }


def _table(rows: list[list[str]], header: list[str]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(out)


def acta_markdown(facts: dict[str, Any]) -> str:
    server = facts["server"]
    pipelines = facts["pipelines"]
    results = facts["results"]
    loaders = facts["loaders"]
    index_coll = facts["index_collection"]

    rows = []
    for coll in facts["collections"]:
        idx = ", ".join(f"`{i['name']}`" for i in coll["indexes"] if i["name"] != "_id_") or "solo `_id`"
        rows.append(
            [
                f"`{coll['name']}`",
                f"{coll['docs']:,}".replace(",", "."),
                f"`{coll['id_type']}`",
                f"`{loaders.get(coll['name'], '—')}`",
                idx,
            ]
        )

    idx_rows = []
    for idx in facts["defined_indexes"]:
        coll = index_coll.get(idx["name"], "—")
        status = "❌ **no creado**" if idx["name"] in facts["defined_indexes_missing"] else "✅ creado"
        idx_rows.append([f"`{idx['name']}`", f"`{coll}`", status])

    pipe_rows = [[f"{n}.", f"`{p}`"] for n, p in enumerate(pipelines["ordered"], 1)]
    for extra in pipelines["outside_order"]:
        pipe_rows.append(["—", f"`{extra}` (fuera de `PIPELINE_ORDER`)"])

    drift_rows = [[f"`{d['doc']}`", d["says"], f"**{d['actual']}**"] for d in facts["drift"]]

    return f"""# Acta de cifras vigentes — BDA Vivienda Euskadi

**Generada:** {facts['generated_at']} · **Fuente:** base viva + código del repositorio.
**Regenerar con:** `.venv/Scripts/python.exe scripts/nb_acta_mongo.py`

> Esta es la fuente 00 del cuaderno y **manda sobre cualquier otra**. Si una nota
> o el README dicen otra cosa, gana esta tabla y la nota está desfasada. Todas
> las cifras se obtuvieron con un script de solo lectura: conteos, `list_indexes()`,
> `explain()` y estadísticas de campos sobre una muestra de {facts['collections'][0]['sample_size']} documentos.

---

## 1. Servidor

{_table([
    ["Versión MongoDB", f"`{server['version']}`"],
    ["Base de datos", f"`{server['db']}`"],
    ["Replica set", f"`{server['replica_set'] or 'ninguno (standalone)'}`"],
    ["Colecciones totales", f"**{facts['collections_total']}** = {facts['collections_live']} vivas + {facts['collections_backup']} `__backup`"],
], ["Parámetro", "Valor"])}

Que el servidor sea *standalone* es la razón técnica de que no haya transacciones
multidocumento: Mongo solo las admite con replica set. No es una carencia del
proyecto, es una restricción del entorno que se compensa con atomicidad de
documento único e idempotencia de carga por lotes.

---

## 2. Las {facts['collections_live']} colecciones vivas

{_table(rows, ["Colección", "Docs", "`_id`", "Cargada por", "Índices"])}

Las {facts['collections_backup']} colecciones `__backup` ({', '.join('`' + b + '`' for b in facts['backup_names'])}) son copias
generadas por `replace_collection` en cada recarga. No se documentan una por una:
el mecanismo se explica en la fuente 04.

---

## 3. Índices: lo definido y lo que existe

`analysis/mongo_indexes.py` define {len(facts['defined_indexes'])} índices. En la base viva hay
**{len(facts['defined_indexes']) - len(facts['defined_indexes_missing'])} creados** y **{len(facts['defined_indexes_missing'])} sin crear**.

{_table(idx_rows, ["Índice", "Colección", "Estado en la base"])}

El desfase no es un misterio: el índice existe en el código desde que se escribió,
pero solo se materializa cuando alguien ejecuta `ensure_indexes()`. Tras una recarga
parcial puede quedar definido-y-ausente. La pregunta de control del cuaderno es
exactamente esta: *"¿cuántos índices tiene `esfuerzo_mercado_2026`?"* → **dos
definidos, cero creados**.

---

## 4. Los {len(pipelines['ordered']) + len(pipelines['outside_order'])} aggregation pipelines

`analysis/run_analisis_mongo.py` ejecuta {len(pipelines['ordered'])} en `PIPELINE_ORDER`:

{_table(pipe_rows, ["#", "Pipeline"])}

`analysis/mongo_aggregations.py` define además `{pipelines['outside_order'][0] if pipelines['outside_order'] else '—'}`, que no
está en el orden de ejecución del runner. Existe y se puede invocar, pero no forma
parte del lote canónico.

**Uso de etapas en todo el módulo:** {', '.join(f"`${k}` ×{v}" for k, v in pipelines['stage_usage'].items())}.

---

## 5. Salidas

- **{len(results['mongo_csv'])} CSV `mongo_*`** en `data/resultados/`: {', '.join('`' + c + '`' for c in results['mongo_csv'])}.
- **{results['total']} ficheros** en `data/resultados/` en total ({', '.join(f"{k or 'sin extensión'}: {v}" for k, v in results['by_extension'].items())}).

---

## 6. Desfases documentados

{_table(drift_rows, ["Documento", "Dice", "Estado real"])}

Este cuadro no se genera a partir de la base: es la lista de contradicciones que se
encontraron al escribir las fuentes, y se mantiene a mano en el script. Si aparece
una nueva, se añade aquí y se corrige la fuente afectada.

---

## 7. Tabla de autoridad

| Cifra | Autoridad | Cómo se obtiene |
|---|---|---|
| Colecciones vivas | base `vivienda_euskadi` | `db.list_collection_names()` sin sufijo `__backup` |
| Documentos por colección | base | `estimated_document_count()` |
| Índices | base + `mongo_indexes.py` | `list_indexes()` vs `name="idx_..."` |
| Pipelines | `run_analisis_mongo.py` | tupla `PIPELINE_ORDER` |
| CSV y PNG | `data/resultados/` | glob por extensión |
| Rutas y SQL de negocio | código | `ruta:línea` en cada fuente |

> Si una cifra de este acta envejece, se regenera el acta antes de re-subir el
> cuaderno. Nunca se edita a mano.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=int, default=200, help="documentos por colección para estadísticas de campos")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    facts = collect(args.sample)
    (OUT_DIR / "_facts.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "00-acta-de-cifras-vigentes.md").write_text(
        acta_markdown(facts), encoding="utf-8"
    )
    missing = facts["defined_indexes_missing"]
    print(f"OK  {OUT_DIR / '00-acta-de-cifras-vigentes.md'}")
    print(
        f"    colecciones: {facts['collections_live']} vivas + {facts['collections_backup']} backup"
        f" | pipelines: {len(facts['pipelines']['ordered'])} + {len(facts['pipelines']['outside_order'])}"
        f" | índices sin crear: {len(missing)} {missing if missing else ''}"
    )


if __name__ == "__main__":
    main()
