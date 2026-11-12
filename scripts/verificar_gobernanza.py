"""Guarda de gobernanza: cifras canónicas e IDs únicos (solo lectura).

Comprueba lo que la auditoría dejó fijado (v6 2026-11-08, valores reales
contados con Python):
- Cabeceras de requisito con ID único (las 4 `chart_*` sin ID numérico).
- 44 scripts en transform/ y 38 nodos en el DAG.
- Manifiesto silver == ficheros en disco (menos los 3 de control).
- 0 variables de entorno usadas sin declarar en .env.example.
- 11 pipelines en PIPELINE_ORDER.

Uso: .venv/Scripts/python.exe scripts/verificar_gobernanza.py
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ERRORES: list[str] = []


def check(nombre: str, ok: bool, detalle: str) -> None:
    print(("OK   " if ok else "FALLA") + f" {nombre}: {detalle}")
    if not ok:
        ERRORES.append(nombre)


def requisitos() -> tuple[list[str], int]:
    """Devuelve (IDs canónicos, nº de cabeceras `### Requirement:`)."""
    ids: list[str] = []
    cabeceras = 0
    for spec in sorted((ROOT / "openspec" / "specs").glob("*/spec.md")):
        for line in spec.read_text(encoding="utf-8").splitlines():
            if line.startswith("### Requirement:"):
                cabeceras += 1
                match = re.search(r"([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{2})", line)
                if match:
                    ids.append(match.group(1))
    return ids, cabeceras


def main() -> int:
    ids, cabeceras = requisitos()
    # La invariante util es que no haya IDs repetidos ni cabeceras sin ID; el
    # total cambia cada vez que crece un spec y no debe ser una foto fija.
    check("requisitos", len(ids) == len(set(ids)) and len(ids) >= cabeceras - 4,
          f"{cabeceras} cabeceras, {len(ids)} con ID canónico, {len(set(ids))} únicos")

    transform = sorted((ROOT / "transform").glob("*.py"))
    tree = ast.parse((ROOT / "transform" / "run_all.py").read_text(encoding="utf-8-sig"))
    dag = 0
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "SCRIPTS":
            dag = len(node.value.keys)
    # 47 incluye la libreria _anuncios_2026.py; 40 = 38 previos + los dos
    # consumidores de la capa 2026 declarados en el DAG (antes fuera de el).
    check("transform", len(transform) == 47 and dag == 40,
          f"{len(transform)} scripts, {dag} nodos DAG")

    # Se compara contra disco en vez de contra un literal: el manifiesto tiene
    # que ser exactamente el inventario de la capa, no una foto de un dia.
    proc = ROOT / "data" / "procesado"
    silver = proc / "manifest_sha256.txt"
    entradas = {line.split("  ", 1)[1].strip().replace("\\", "/")
                for line in silver.read_text(encoding="utf-8").splitlines() if line.strip()}
    control = {"manifest_sha256.txt", "run_manifest.json", ".gitkeep",
               "_meta/ingestion_manifest.json"}
    en_disco = {str(p.relative_to(proc)).replace("\\", "/")
                for p in proc.rglob("*") if p.is_file()} - control
    detalle = f"{len(entradas)} entradas, {len(en_disco)} ficheros de datos"
    if en_disco - entradas:
        detalle += f"; sin hashear: {sorted(en_disco - entradas)[:3]}"
    if entradas - en_disco:
        detalle += f"; hasheados que no existen: {sorted(entradas - en_disco)[:3]}"
    check("silver", entradas == en_disco, detalle)

    usadas: set[str] = set()
    for carpeta in ("extract", "transform", "storage", "analysis", "scripts"):
        for py in (ROOT / carpeta).rglob("*.py"):
            texto = py.read_text(encoding="utf-8", errors="ignore")
            usadas.update(re.findall(r"getenv\(['\"]([A-Z0-9_]+)['\"]", texto))
            usadas.update(re.findall(r"environ\[['\"]([A-Z0-9_]+)['\"]", texto))
            usadas.update(re.findall(r"environ\.get\(\s*['\"]([A-Z0-9_]+)['\"]", texto))
    declaradas = set(re.findall(r"^([A-Z0-9_]+)=", (ROOT / ".env.example").read_text(encoding="utf-8"), re.M))
    faltan = sorted(usadas - declaradas - {"PYTHONPATH"})
    check("env", not faltan, f"sin declarar: {faltan or 'ninguna'}")

    texto = (ROOT / "analysis" / "run_analisis_mongo.py").read_text(encoding="utf-8")
    bloque = re.search(r"PIPELINE_ORDER[^=]*=\s*\((.*?)\)", texto, re.S)
    pipelines = len(re.findall(r'"pipeline_[a-z_]+"', bloque.group(1))) if bloque else 0
    check("pipelines", pipelines == 11, f"{pipelines} pipelines en PIPELINE_ORDER")

    print(f"\n{'TODO OK' if not ERRORES else 'FALLOS: ' + ', '.join(ERRORES)}")
    return 0 if not ERRORES else 1


if __name__ == "__main__":
    sys.exit(main())
