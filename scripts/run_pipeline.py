"""Orquestador de reconstruccion de capas: silver -> quality -> [mongo] -> gold.

Un solo comando para volver a poblar `data/procesado` y `data/resultados` desde
`data/raw` sin tocar raw ni encadenar pasos a mano.

Fases:
  silver   transform/run_all.py (DAG de 34 nodos)
  quality  normalizar_metadata + ingestion_manifest + manifest --write
  mongo    scripts/run_mongo_pipeline.py  (DESTRUCTIVO: exige --allow-mongo-write)
  gold     run_analisis_mongo + comparativa_mongo + sensibilidad + figuras

`--fase all` = silver,quality,gold. Nunca incluye mongo.

Uso:
  python scripts/run_pipeline.py --fase silver,quality
  python scripts/run_pipeline.py --fase all --dry-run
  python scripts/run_pipeline.py --fase gold
  python scripts/run_pipeline.py --fase mongo --allow-mongo-write
  python scripts/run_pipeline.py --check
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "procesado"
RES_DIR = ROOT / "data" / "resultados"

# Codigos de salida del orquestador (ver openspec/.../spec.md).
EXIT_OK = 0
EXIT_FALLO = 1
EXIT_PREFLIGHT = 2


@dataclass(frozen=True)
class Paso:
    """Un comando del pipeline.

    ``tolerar_rc`` recoge los codigos que no abortan la fase. Solo lo usa
    ``normalizar_metadata``: devuelve 1 cuando hay raw sin metadata completa,
    pero escribe todos los sidecars igualmente. Se reporta como AVISO.
    """

    nombre: str
    args: tuple[str, ...]
    tolerar_rc: tuple[int, ...] = (0,)
    aviso_por: str = ""

    @property
    def ruta(self) -> Path:
        return ROOT / self.args[0]


@dataclass
class Resultado:
    paso: str
    rc: int
    estado: str  # OK | AVISO | FAIL
    segundos: float = 0.0
    detalle: str = ""


@dataclass
class Fase:
    nombre: str
    pasos: tuple[Paso, ...]
    destructiva: bool = False
    resumen: list[Resultado] = field(default_factory=list)


def _py(script: str, *extra: str) -> tuple[str, ...]:
    return (script, *extra)


FASES: dict[str, Fase] = {
    "silver": Fase("silver", (Paso("run_all", _py("transform/run_all.py")),)),
    "quality": Fase("quality", (
        Paso(
            "normalizar_metadata",
            _py("extract/normalizar_metadata.py"),
            tolerar_rc=(0, 1),
            aviso_por="metadata incompleta en raw (los sidecars se escriben igualmente)",
        ),
        Paso("generar_ingestion_manifest", _py("extract/generar_ingestion_manifest.py")),
        Paso("generar_manifest", _py("extract/generar_manifest.py", "--write")),
    )),
    "mongo": Fase(
        "mongo",
        (Paso("run_mongo_pipeline", _py("scripts/run_mongo_pipeline.py")),),
        destructiva=True,
    ),
    "gold": Fase("gold", (
        Paso("run_analisis_mongo", _py("analysis/run_analisis_mongo.py")),
        Paso("comparativa_mongo", _py("analysis/comparativa_mongo.py")),
        Paso("sensibilidad", _py("analysis/sensibilidad.py")),
        Paso("generar_figuras_N", _py("transform/generar_figuras_N.py")),
    )),
}

# `all` deja fuera mongo a proposito: la carga borra e inserta en produccion.
FASES_ALL = ("silver", "quality", "gold")


def resolver_fases(nombres: list[str]) -> list[Fase]:
    """Expande 'all' y valida nombres. Lanza ValueError si algo no existe."""
    elegidas: list[str] = []
    for nombre in nombres:
        if nombre == "all":
            elegidas.extend(FASES_ALL)
        else:
            elegidas.append(nombre)
    desconocidas = [n for n in elegidas if n not in FASES]
    if desconocidas:
        raise ValueError(
            f"Fase(s) desconocida(s): {', '.join(desconocidas)}. "
            f"Disponibles: all, {', '.join(FASES)}"
        )
    vistas: list[Fase] = []
    vistas_nombres: set[str] = set()
    for nombre in elegidas:
        if nombre in vistas_nombres:
            continue
        vistas_nombres.add(nombre)
        vistas.append(FASES[nombre])
    return vistas


def preflight(verificar_hash: bool) -> int:
    """Comprueba el terreno antes de ejecutar. Devuelve EXIT_OK o el codigo de fallo."""
    # Solo raw es requisito: procesado/resultados son las salidas a reconstruir.
    if not RAW_DIR.is_dir():
        print("[preflight] FALTA data/raw: sin materia prima no hay reconstruccion")
        return EXIT_PREFLIGHT
    if not any(RAW_DIR.iterdir()):
        print("[preflight] data/raw esta vacia: no hay nada que reconstruir")
        return EXIT_PREFLIGHT
    if verificar_hash:
        print("[preflight] verificando hashes de raw contra docs/raw_manifest_sha256.txt ...")
        rc = _ejecutar(Paso("verificar_manifest", _py("extract/generar_manifest.py", "--verify")), silencioso=False)
        if rc not in (0,):
            print(f"[preflight] FALLO: manifest no coincide (rc={rc}). "
                  "No se ejecuta nada; revisa data/raw o regenera con quality.")
            return EXIT_PREFLIGHT
    return EXIT_OK


def _ejecutar(paso: Paso, silencioso: bool = False) -> int:
    """Ejecuta un paso como subproceso (UTF-8) y devuelve su rc."""
    env = dict(os.environ, PYTHONUTF8="1")
    argv = [sys.executable, *paso.args]
    if not silencioso:
        print(f"    $ {' '.join(paso.args)}")
    try:
        proc = subprocess.run(
            argv,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        print(f"    EXCEPCION: {exc}", file=sys.stderr)
        return 127
    salida = (proc.stdout or "").strip()
    error = (proc.stderr or "").strip()
    if salida:
        for linea in salida.splitlines()[-5:]:
            print(f"    {linea}")
    if proc.returncode != 0 and error:
        for linea in error.splitlines()[-6:]:
            print(f"    ERR: {linea}", file=sys.stderr)
    return proc.returncode


def _clasificar(paso: Paso, rc: int) -> str:
    if rc == 0:
        return "OK"
    if rc in paso.tolerar_rc:
        return "AVISO"
    return "FAIL"


def _resumen(fases: list[Fase]) -> int:
    resultados = [r for f in fases for r in f.resumen]
    print("\n=== RESUMEN ===")
    for r in resultados:
        detalle = f"  {r.detalle}" if r.detalle else ""
        print(f"  [{r.estado:<5}] {r.paso:<26} rc={r.rc:<3} {r.segundos:6.1f}s{detalle}")
    fallos = [r for r in resultados if r.estado == "FAIL"]
    avisos = [r for r in resultados if r.estado == "AVISO"]
    print(f"  {len(resultados) - len(fallos) - len(avisos)} OK, "
          f"{len(avisos)} aviso(s), {len(fallos)} fallo(s)")
    return len(fallos)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruye data/procesado y data/resultados por fases")
    parser.add_argument("--fase", action="append", default=None,
                        help="Fase(s) a ejecutar: silver, quality, mongo, gold, all "
                             "(repetible o separado por comas). Por defecto: all")
    parser.add_argument("--dry-run", action="store_true",
                        help="Lista los pasos y su orden, sin ejecutar")
    parser.add_argument("--check", action="store_true",
                        help="Solo preflight: verifica hashes de raw y sale")
    parser.add_argument("--strict", action="store_true",
                        help="Trata los AVISO como fallo (rc=1)")
    parser.add_argument("--allow-mongo-write", action="store_true",
                        help="Autoriza la fase mongo (borra e inserta en Mongo)")
    args = parser.parse_args(argv)

    nombres: list[str] = []
    for valor in (args.fase or ["all"]):
        nombres.extend(p.strip() for p in valor.split(",") if p.strip())
    try:
        fases = resolver_fases(nombres)
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return EXIT_PREFLIGHT

    if args.check:
        return preflight(verificar_hash=True)

    rc = preflight(verificar_hash=False)
    if rc != EXIT_OK:
        return rc

    if any(f.destructiva for f in fases) and not args.allow_mongo_write:
        print("[error] La fase mongo borra e inserta en MongoDB. "
              "Repite con --allow-mongo-write si es lo que quieres.",
              file=sys.stderr)
        return EXIT_PREFLIGHT

    print(f"=== PLAN ({', '.join(f.nombre for f in fases)}) ===")
    for fase in fases:
        etiqueta = " (DESTRUCTIVA)" if fase.destructiva else ""
        print(f"  {fase.nombre}{etiqueta}")
        for paso in fase.pasos:
            print(f"    - {paso.nombre}: {' '.join(paso.args)}")

    if args.dry_run:
        return EXIT_OK

    for destino in (PROC_DIR, RES_DIR):
        if not destino.is_dir():
            destino.mkdir(parents=True, exist_ok=True)
            print(f"[preflight] creado {destino.relative_to(ROOT)}")

    for fase in fases:  # FASES es global: no arrastrar resumenes previos
        fase.resumen.clear()

    inicio_global = time.monotonic()
    for fase in fases:
        print(f"\n=== FASE {fase.nombre} ===")
        for paso in fase.pasos:
            inicio = time.monotonic()
            rc = _ejecutar(paso)
            segundos = time.monotonic() - inicio
            estado = _clasificar(paso, rc)
            detalle = paso.aviso_por if estado == "AVISO" else ""
            fase.resumen.append(Resultado(paso.nombre, rc, estado, segundos, detalle))
            print(f"  [{estado}] {paso.nombre} (rc={rc}, {segundos:.1f}s)")
            if estado == "FAIL":
                print(f"\n  Fase {fase.nombre} abortada en {paso.nombre}.")
                print(f"  Tiempo total: {time.monotonic() - inicio_global:.1f}s")
                _resumen(fases)
                return EXIT_FALLO

    print(f"\nTiempo total: {time.monotonic() - inicio_global:.1f}s")
    fallos = _resumen(fases)
    if fallos:
        return EXIT_FALLO
    if args.strict and any(r.estado == "AVISO" for f in fases for r in f.resumen):
        print("  --strict: los avisos cuentan como fallo")
        return EXIT_FALLO
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
