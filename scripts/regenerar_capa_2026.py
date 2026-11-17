"""Regenera la capa 2026 de datos en orden, desde silver, con un solo comando.

No toca `data/raw` ni `extract/`. Asume que el silver ya existe (si no,
`python transform/run_all.py` lo reconstruye desde raw; desde esta version los
dos scripts de 2026 estan declarados en el DAG).

Pasos, en orden estricto (fail-fast: el primero que falla detiene la cadena):

  1. transform/calcular_esfuerzo_mercado_2026.py
  2. transform/calcular_esfuerzo_mercado_2026_por_tipo.py
  3. analysis/esfuerzo_por_tipo_nivel_anuncio.py
  4. analysis/calibrar_premium_oferta.py
  5. analysis/comparar_esfuerzo_2024_2026_misma_base.py
  6. analysis/calcular_brecha_esfuerzo_2024_2026.py
  7. analysis/cobertura_representatividad_2026.py
  8. analysis/validar_alquiler_serpavi.py
  9. analysis/validar_portales_2026.py
 10. visuals/mapa_esfuerzo_mercado_2026.py
 11. visuals/graficos_esfuerzo_mercado_2026.py

Los assets del deck NO se generan aquí: dependen de `mongo_tier_confianza.csv`
(gold de Mongo) y se generan en el paso `assets_presentacion` de
`scripts/run_pipeline.py --fase gold`, después de `run_analisis_mongo`.

Al final imprime el SHA-256 de cada salida para poder comparar ejecuciones.

Uso:
    python scripts/regenerar_capa_2026.py
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROC = PROJECT_ROOT / "data" / "procesado"
RES = PROJECT_ROOT / "data" / "resultados"

PASOS: list[str] = [
    "transform/calcular_esfuerzo_mercado_2026.py",
    "transform/calcular_esfuerzo_mercado_2026_por_tipo.py",
    "analysis/esfuerzo_por_tipo_nivel_anuncio.py",
    "analysis/calibrar_premium_oferta.py",
    "analysis/comparar_esfuerzo_2024_2026_misma_base.py",
    "analysis/calcular_brecha_esfuerzo_2024_2026.py",
    "analysis/cobertura_representatividad_2026.py",
    "analysis/validar_alquiler_serpavi.py",
    "analysis/validar_portales_2026.py",
    "visuals/mapa_esfuerzo_mercado_2026.py",
    "visuals/graficos_esfuerzo_mercado_2026.py",
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
    RES / "mapa_coropletico_2026.png",
    RES / "mapa_cobertura_2026.png",
    RES / "barras_esfuerzo_top20.png",
    RES / "hist_esfuerzo.png",
    RES / "barras_territorio.png",
    RES / "scatter_precio_vs_esfuerzo.png",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    for i, script in enumerate(PASOS, start=1):
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
