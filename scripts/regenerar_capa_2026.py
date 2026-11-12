"""Regenera la capa 2026 completa en orden, desde silver, con un solo comando.

No toca `data/raw` ni `extract/`. Asume que el silver ya existe (si no,
`python transform/run_all.py` lo reconstruye desde raw; desde esta version los
dos scripts de 2026 estan declarados en el DAG).

Pasos, en orden estricto (fail-fast: el primero que falla detiene la cadena):

  1. transform/calcular_esfuerzo_mercado_2026.py
  2. transform/calcular_esfuerzo_mercado_2026_por_tipo.py
  3. analysis/calibrar_premium_oferta.py
  4. analysis/comparar_esfuerzo_2024_2026_misma_base.py
  5. analysis/calcular_brecha_esfuerzo_2024_2026.py
  6. analysis/cobertura_representatividad_2026.py
  7. analysis/validar_alquiler_serpavi.py
  8. visuals/mapa_esfuerzo_mercado_2026.py
  9. visuals/graficos_esfuerzo_mercado_2026.py
 10. visuals/assets_presentacion_esfuerzo_mercado_2026.py

Al final imprime el SHA-256 de cada salida para poder comparar ejecuciones.

Uso:
    python scripts/regenerar_capa_2026.py
    python scripts/regenerar_capa_2026.py --sin-presentacion   # omite el paso 10
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROC = PROJECT_ROOT / "data" / "procesado"
RES = PROJECT_ROOT / "data" / "resultados"
ASSETS = PROJECT_ROOT / "docs" / "presentacion_v2" / "assets"

PASOS: list[tuple[str, bool]] = [
    ("transform/calcular_esfuerzo_mercado_2026.py", False),
    ("transform/calcular_esfuerzo_mercado_2026_por_tipo.py", False),
    ("analysis/esfuerzo_por_tipo_nivel_anuncio.py", False),
    ("analysis/calibrar_premium_oferta.py", False),
    ("analysis/comparar_esfuerzo_2024_2026_misma_base.py", False),
    ("analysis/calcular_brecha_esfuerzo_2024_2026.py", False),
    ("analysis/cobertura_representatividad_2026.py", False),
    ("analysis/validar_alquiler_serpavi.py", False),
    ("analysis/validar_portales_2026.py", False),
    ("visuals/mapa_esfuerzo_mercado_2026.py", False),
    ("visuals/graficos_esfuerzo_mercado_2026.py", False),
    ("visuals/assets_presentacion_esfuerzo_mercado_2026.py", True),  # presentacion
]

SALIDAS = [
    PROC / "esfuerzo_mercado_2026.csv",
    PROC / "esfuerzo_mercado_2026_por_tipo.csv",
    RES / "esfuerzo_por_tipo_nivel_anuncio_2026.csv",
    RES / "premium_oferta_2026.csv",
    RES / "comparacion_esfuerzo_2024_2026.csv",
    RES / "comparacion_esfuerzo_2024_2026_resumen.csv",
    RES / "brecha_esfuerzo_2024_2026.csv",
    RES / "cobertura_representatividad_2026.csv",
    RES / "validacion_alquiler_2024_serpavi.csv",
    RES / "validacion_portales_2026.csv",
    ASSETS / "M26_mapa_cobertura.png",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Regenera la capa 2026 completa.")
    ap.add_argument("--sin-presentacion", action="store_true",
                    help="Omite la generacion de assets de la presentacion.")
    args = ap.parse_args()

    for i, (script, es_presentacion) in enumerate(PASOS, start=1):
        if es_presentacion and args.sin_presentacion:
            print(f"[{i}/{len(PASOS)}] OMITIDO por --sin-presentacion: {script}")
            continue
        ruta = PROJECT_ROOT / script
        if not ruta.exists():
            print(f"FALLO: no existe {script}")
            return 1
        print(f"[{i}/{len(PASOS)}] {script}")
        resultado = subprocess.run([sys.executable, script], cwd=PROJECT_ROOT)
        if resultado.returncode != 0:
            print(f"FALLO en {script} (exit {resultado.returncode}); cadena detenida.")
            return resultado.returncode

    print("\nSHA-256 de las salidas:")
    for salida in SALIDAS:
        if salida.exists():
            print(f"  {_sha256(salida)[:16]}  {salida.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  (falta)            {salida.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
