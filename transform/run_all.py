"""Orquestador de transformaciones (silver) del pipeline de vivienda Euskadi.

Ejecuta los scripts de ``transform/`` en orden topológico de dependencias,
aislando los fallos de cada uno (un script que falle no aborta los demás) y
generando un manifest de ejecución con timestamp, estado y duración.

Uso:
    python transform/run_all.py
    python transform/run_all.py --group resultados
    python transform/run_all.py --check   # solo verifica staleness (mtime inputs vs outputs)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
TRANSFORM_DIR = PROJECT_ROOT / "transform"
PROCESADO_DIR = PROJECT_ROOT / "data" / "procesado"
RESULTADOS_DIR = PROJECT_ROOT / "data" / "resultados"

# Orden topológico de transformaciones (grupos de dependencia).
# Cada grupo se ejecuta secuencialmente; dentro de un grupo, los scripts
# son independientes y se ejecutan en orden alfabético.
TRANSFORM_GROUPS: list[tuple[str, list[str]]] = [
    ("normalizacion", [
        "normalizar_json_crudos.py",
    ]),
    ("limpieza_base", [
        "limpiar_ecvi.py",
        "limpiar_eustat_demografia.py",
        "corregir_empleo.py",
    ]),
    ("dim_municipios", [
        "dim_municipios.py",
    ]),
    ("unificacion", [
        "unificar_anuncios.py",
        "generar_fingerprint.py",
        "filtrar_outliers.py",
    ]),
    ("enriquecimiento", [
        "enriquecer_gtfs_conectividad.py",
        "enriquecer_codigo_ine.py",
        "enriquecer_equipamiento_realtyapi.py",
        "generar_cert_energetico_municipal.py",
        "generar_cert_energetico_moda_municipio.py",
    ]),
    ("analisis", [
        "calcular_renta_joven.py",
        "calcular_tension_social.py",
        "imputar_nulos_fuentes.py",
        "generar_mercado_area_funcional.py",
    ]),
    ("resultados", [
        "generar_dashboard_visual.py",
        "generar_dashboard_completo.py",
        "generar_mapa_esquema.py",
        "auditar_lagunas_silver.py",
    ]),
]


def _run_script(script: Path) -> tuple[int, float]:
    """Ejecuta un script y retorna (returncode, duracion_segundos)."""
    inicio = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        rc = proc.returncode
        if proc.stdout:
            for linea in proc.stdout.strip().splitlines()[-5:]:
                print(f"    {linea}")
        if rc != 0 and proc.stderr:
            for linea in proc.stderr.strip().splitlines()[-8:]:
                print(f"    ERR: {linea}")
    except Exception as exc:
        print(f"    EXCEPCION: {exc}")
        rc = 1
    duracion = time.monotonic() - inicio
    return rc, duracion


def _check_staleness() -> None:
    """Verifica si algún output de procesado es más antiguo que sus inputs."""
    print("=== STALENESS CHECK ===")
    # Heurística: comparar mtime de procesado vs raw
    raw_mtime = 0.0
    if (PROJECT_ROOT / "data" / "raw").exists():
        for p in (PROJECT_ROOT / "data" / "raw").rglob("*"):
            if p.is_file():
                raw_mtime = max(raw_mtime, p.stat().st_mtime)
    proc_mtime = 0.0
    if PROCESADO_DIR.exists():
        for p in PROCESADO_DIR.iterdir():
            if p.is_file():
                proc_mtime = max(proc_mtime, p.stat().st_mtime)
    if raw_mtime > 0 and proc_mtime > 0:
        if raw_mtime > proc_mtime:
            print(f"  WARNING: raw más reciente que procesado (raw={raw_mtime:.0f}, proc={proc_mtime:.0f})")
        else:
            print(f"  OK: procesado actualizado (proc={proc_mtime:.0f} >= raw={raw_mtime:.0f})")
    else:
        print("  No se pudo verificar (directorios vacíos)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Orquestador de transformaciones (silver).")
    parser.add_argument("--group", type=str, default=None,
                        help="Ejecutar solo un grupo específico.")
    parser.add_argument("--check", action="store_true",
                        help="Solo verificar staleness, no ejecutar.")
    args = parser.parse_args()

    if args.check:
        _check_staleness()
        return 0

    groups = TRANSFORM_GROUPS
    if args.group:
        groups = [(g, s) for g, s in TRANSFORM_GROUPS if g == args.group]
        if not groups:
            print(f"Grupo '{args.group}' no encontrado. Disponibles: {[g for g, _ in TRANSFORM_GROUPS]}")
            return 1

    print(f"=== TRANSFORM RUN ALL ({len(groups)} grupos) ===")
    print(f"Python: {sys.executable}")
    print(f"Root: {PROJECT_ROOT}")
    print()

    total_fallos = 0
    total_scripts = 0
    inicio_total = time.monotonic()

    for grupo, scripts in groups:
        print(f"--- Grupo: {grupo} ({len(scripts)} scripts) ---")
        for nombre in scripts:
            script = TRANSFORM_DIR / nombre
            if not script.exists():
                print(f"  SKIP (no existe): {nombre}")
                continue
            total_scripts += 1
            print(f"  ▶ {nombre}")
            rc, dur = _run_script(script)
            estado = "OK" if rc == 0 else "FAIL"
            print(f"    → {estado} ({dur:.1f}s)")
            if rc != 0:
                total_fallos += 1
        print()

    duracion_total = time.monotonic() - inicio_total
    print(f"=== RESUMEN: {total_scripts} scripts, {total_fallos} fallos, {duracion_total:.1f}s ===")
    return 0 if total_fallos == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
