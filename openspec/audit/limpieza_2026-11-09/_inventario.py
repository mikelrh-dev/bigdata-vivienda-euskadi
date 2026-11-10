from __future__ import annotations

import collections
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(".")
OUT = Path("openspec/audit/limpieza_2026-11-09")
OUT.mkdir(parents=True, exist_ok=True)
EXCLUDE = {".git", ".venv", "__pycache__", ".pytest_cache"}
TRACKED = set(subprocess.check_output(["git", "ls-files"], text=True, encoding="utf-8").splitlines())
TEXT_EXT = {".py", ".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".html",
            ".ipynb", ".toml", ".ini", ".cfg", ".sql", ".sh", ".ps1", ".bat",
            ".example", ".lock", ""}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duckdb_lines(path: Path) -> list[str]:
    if path.suffix.lower() not in TEXT_EXT or path.stat().st_size > 3_000_000:
        return []
    if path.as_posix() in {".env", "api.txt"}:
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    return [str(i) for i, line in enumerate(lines, 1) if "duckdb" in line.lower()]


OVERRIDES = {
    "scripts/launch_duckdb_ui.py": ("residuo_duckdb", "borrar", "lanzador local de DuckDB UI, ignorado y sin referencias"),
    "transform/auditoria_duckdb.py": ("residuo_duckdb", "archivar_o_borrar", "auditoria one-off; escribe en scratchpad y esta fuera del DAG"),
    "transform/generar_dashboard_visual.py": ("residuo_duckdb", "archivar_o_borrar", "sustituido por exportar_png_desde_mongo; README aun lo invoca"),
    "transform/generar_dashboard_completo.py": ("residuo_duckdb", "archivar_o_borrar", "sustituido por exportar_png_desde_mongo; conserva literales antiguos"),
    "scripts/validar_fuentes_nuevas.py": ("residuo_activo", "migrar_o_archivar", "validacion one-off que importa DuckDB; test en suite y dependencia no declarada"),
    "tests/test_fuentes_validacion.py": ("residuo_activo", "borrar_o_reescribir", "ejecuta validar_fuentes_nuevas; mantiene DuckDB como dependencia oculta"),
    "requirements-legacy.txt": ("legacy_deliberado", "conservar_mientras_haya_legacy", "DuckDB separado del requirements activo"),
    "transform/run_all.py": ("editar", "editar", "EXCLUIDOS cita auditoria_duckdb y los dos dashboards"),
    "README.md": ("editar", "editar", "paso 5 invoca dashboards DuckDB; cita cifra historica"),
    "analysis/run_analisis_mongo.py": ("editar", "editar_opcional", "docstring historico menciona DuckDB"),
    "docs/guion_defensa.md": ("editar", "editar_opcional", "menciona cifra historica de DuckDB"),
    "docs/pendiente_duckdb_pymongo_2026-11-05.md": ("documento_resuelto", "mover_a_archive", "deuda resuelta en 2026-11-05, fuera de archive"),
    "docs/README.md": ("editar", "editar", "describe G_gaps como tabla literal del generador legacy"),
    "docs/auditoria_10_10_SDD_2026-11-05.md": ("revisar", "revisar", "documento historico que cita el generador legacy"),
    "docs/analisis_vault_vs_rubrica.md": ("revisar", "revisar", "analisis que cita generadores legacy"),
    "scratchpad/sha1.txt": ("duplicado", "borrar", "duplicado byte a byte de sha2.txt; sin referencias"),
    "scratchpad/sha2.txt": ("duplicado", "borrar", "duplicado byte a byte de sha1.txt; sin referencias"),
    "scratchpad/build_mapa.py": ("scratch", "borrar", "prototipo local; sustituido por transform/generar_mapa_esquema.py"),
    "scratchpad/check_mapa.py": ("scratch", "borrar", "comprobacion one-off sin referencias"),
    "scratchpad/check_mapa2.py": ("scratch", "borrar", "comprobacion one-off sin referencias"),
    "scratchpad/prototipo_pisos_ubicacion.py": ("scratch", "archivar_o_borrar", "prototipo superado por el flujo transform/test"),
    "scratchpad/mapa_norm.json": ("scratch", "borrar", "salida intermedia del prototipo; ignorada"),
    "logs/raw_guard_audit.log": ("generado", "borrar_local", "log regenerable e ignorado"),
    "notebooks/Kafka_Ejercicio.ipynb": ("residuo_ejercicio", "archivar_o_borrar", "ejercicio de pedidos HDFS/Kafka ajeno al proyecto"),
}


def classify(path: Path, duck: list[str]) -> tuple[str, str, str]:
    rel = path.as_posix()
    if rel in OVERRIDES:
        return OVERRIDES[rel]
    if rel in {".env", "api.txt"}:
        return "secreto", "conservar", "sensible e ignorado; no se ha leido"
    if rel.startswith("data/raw/"):
        return "dato_raw", "conservar", "raw inmutable"
    if rel.startswith("data/"):
        return "dato", "conservar", "dato de trabajo, no residuo"
    if rel.startswith(("archive/", "docs/archive/", "openspec/changes/archive/")):
        return "legacy", "conservar", "dentro de legacy/archivo"
    if rel.startswith("openspec/audit/"):
        return "historico", "conservar", "evidencia de auditorias"
    if rel.startswith("vaultVivienda/"):
        return "fuera_repo", "conservar", "vault ignorado, fuera de alcance"
    if rel.startswith(("graphify-out/", ".atl/", ".freebuff/")):
        return "generado_herramienta", "borrar_local_opcional", "cache o metadato de herramienta"
    if rel.startswith(("demo-kpi/.hyperframes/", "demo-mapa/.hyperframes/",
                       "demo-kpi/renders/", "demo-mapa/renders/")) or rel in {
                           "demo-kpi/out.mp4", "demo-mapa/out.mp4"}:
        return "generado_demo", "borrar_local_opcional", "render local ignorado; GIF/WebP versionados se conservan"
    if rel.startswith("docs/presentacion/") and path.name.startswith("preview_"):
        return "generado", "borrar_local_opcional", "preview ignorada"
    if rel.startswith("scratchpad/backup_t3prev/"):
        return "backup_historico", "archivar", "backup previo a T3, sin uso runtime"
    if rel.startswith("scratchpad/p1-1_backup_2026-11-07/"):
        return "backup_historico", "archivar", "backup silver citado en cambio archivado"
    if rel.startswith("scratchpad/"):
        return "scratch", "revisar", "zona de trabajo local"
    if duck:
        return "referencia_duckdb", "revisar", "menciona DuckDB; decidir historico o activo"
    if path.suffix == ".py":
        return "codigo", "conservar", "codigo sin indicios"
    if path.suffix == ".md":
        return "documento", "conservar", "documento sin indicios"
    return "otro", "conservar", "sin indicios"


rows = []
hashes: dict[str, list[str]] = collections.defaultdict(list)
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or any(part in EXCLUDE for part in path.parts):
        continue
    rel = path.as_posix()
    digest = sha(path)
    duck = duckdb_lines(path)
    kind, verdict, action = classify(path, duck)
    rows.append({
        "path": rel,
        "bytes": path.stat().st_size,
        "sha256": digest,
        "ext": path.suffix.lower(),
        "tracked": "si" if rel in TRACKED else "no",
        "area": rel.split("/")[0],
        "duckdb_hits": len(duck),
        "duckdb_lines": ";".join(duck),
        "kind": kind,
        "verdict": verdict,
        "action": action,
        "reason": action,
    })
    hashes[digest].append(rel)

fields = ["path", "bytes", "sha256", "ext", "tracked", "area", "duckdb_hits",
          "duckdb_lines", "kind", "verdict", "action", "reason"]
with (OUT / "inventario_archivo_por_archivo.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

candidates = [row for row in rows if row["verdict"] != "conservar"]
with (OUT / "candidatos_limpieza.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(candidates)

summary = {
    "files": len(rows),
    "tracked": sum(row["tracked"] == "si" for row in rows),
    "untracked": sum(row["tracked"] == "no" for row in rows),
    "bytes": sum(row["bytes"] for row in rows),
    "verdicts": dict(collections.Counter(row["verdict"] for row in rows)),
    "kinds": dict(collections.Counter(row["kind"] for row in rows)),
    "duckdb_rows": sum(row["duckdb_hits"] > 0 for row in rows),
    "candidates": len(candidates),
    "candidate_bytes": sum(row["bytes"] for row in candidates),
    "duplicate_groups": sum(1 for paths in hashes.values() if len(paths) > 1),
    "duplicates": [paths for paths in hashes.values() if len(paths) > 1],
}
(OUT / "resumen_inventario.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "duplicates"}, ensure_ascii=False, indent=2))
for paths in summary["duplicates"]:
    if any(p.startswith(("scratchpad/", "notebooks/")) for p in paths):
        print("DUP", paths)
