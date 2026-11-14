"""Copia las figuras de gold al deck y a la memoria segun el contrato.

Destinos y origenes los declara `config/vintage_figuras.yaml`
(`sincronizacion.deck` y `sincronizacion.memoria`). Existe porque las copias
se hacian a mano y ya se habian quedado atras: H2, H8 y P en el deck, y
`fig-tier.png` / `fig-oficial-vs-anuncios.png` en la memoria.

No genera figuras: solo copia las que ya existen. Idempotente.

Uso:
    python scripts/sincronizar_figuras.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.vintage_figuras import sincronizar  # noqa: E402


def main() -> int:
    escritas = sincronizar()
    for ruta in escritas:
        print(f"OK  {ruta.relative_to(ROOT)}")
    if not escritas:
        print("AVISO: no habia figuras que copiar (revisa data/resultados)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
