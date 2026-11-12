"""Comprueba que las cifras que enseña el deck siguen saliendo de los CSV gold.

Motivo: `docs/presentacion_v2/index.html` es el unico artefacto escrito a mano, y ya se
quedo una vez con el corte viejo (79,3 % / 52 municipios) mientras los CSV ya daban
78,6 % / 50 municipios. Esto lo detecta en un segundo, sin abrir el navegador.

No escribe nada. Uso:

    python scripts/verificar_cifras_deck.py
"""

from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "presentacion_v2" / "index.html"
PROC = ROOT / "data" / "procesado"
RES = ROOT / "data" / "resultados"


def _col(df: pd.DataFrame, *needles: str) -> str:
    for c in df.columns:
        if all(n in c for n in needles):
            return c
    raise SystemExit(f"no encuentro columna con {needles} en {list(df.columns)}")


def es(x: float, dec: int = 1) -> str:
    """78.55 -> '78,6' (mitad hacia arriba) · 1350 -> '1.350'."""
    q = Decimal(repr(round(float(x), 6))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    s = f"{q:,.{dec}f}"
    return s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def _fila(df: pd.DataFrame, metrica: str) -> float:
    f = df[df["metrica"] == metrica]
    if f.empty:
        raise SystemExit(f"falta la metrica {metrica} en el CSV de cobertura")
    return float(f.iloc[0]["valor"])


def main() -> int:
    html = DECK.read_text(encoding="utf-8")
    plano = re.sub(r"<[^>]+>", "", html)  # asi '50<span>/252</span>' se lee '50/252'
    checks: list[tuple[str, str, bool]] = []

    mercado = pd.read_csv(PROC / "esfuerzo_mercado_2026.csv", encoding="utf-8-sig")
    ef = _col(mercado, "esfuerzo_mercado", "18_34")
    pr = _col(mercado, "precio_mediana", "eur_mes")
    serie = mercado[ef].dropna()

    checks += [
        ("mediana esfuerzo 2026", es(serie.median()), serie.median() > 70),
        ("precio mediana 2026", es(mercado[pr].median(), 0), True),
        ("municipios con anuncio", f"{len(serie)}/252", len(serie) == 50),
        ("anuncios validos", f"{int(mercado['n_anuncios_2026'].sum())} anuncios", True),
    ]

    tipo = pd.read_csv(RES / "esfuerzo_por_tipo_nivel_anuncio_2026.csv", encoding="utf-8-sig")
    for _, r in tipo.iterrows():
        etiqueta = r["tipo_de_vivienda"]
        checks.append((f"tipo {etiqueta}", f"{es(r['esfuerzo_mediana_anuncios_pct_18_34'])} %", True))
        checks.append((f"n {etiqueta}", f"<td>{int(r['n_anuncios'])}</td>", True))

    resumen = pd.read_csv(RES / "comparacion_esfuerzo_2024_2026_resumen.csv", encoding="utf-8-sig")
    for metrica in ("esfuerzo_2024_base_salario_pct_18_34", "esfuerzo_2026_base_renta2024_pct_18_34"):
        v = float(resumen[resumen["metrica"] == metrica].iloc[0]["mediana"])
        checks.append((metrica.split("_")[1] + " base comun", f"{es(v)} %", True))

    # Tier D = sin anuncio, pero con alquiler oficial en la mayoria: el deck lo dice.
    tierd = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", encoding="utf-8-sig")
    oficial = tierd["tiene_alquiler_oficial"].astype(str).str.lower().isin(["true", "1"])
    n_tierd_of = int(((tierd["tier"] == "D") & oficial).sum())
    checks.append(("Tier D con alquiler oficial", f"{n_tierd_of} con alquiler oficial", n_tierd_of > 0))

    cob = pd.read_csv(RES / "cobertura_representatividad_2026.csv", encoding="utf-8-sig")
    checks += [
        ("cobertura poblacion 18-34", es(_fila(cob, "pct_poblacion_18_34_cubierta")), True),
        ("anuncios usados", f"{int(_fila(cob, 'anuncios_usados'))}", True),
        ("4 municipios n>=10", es(_fila(cob, "pct_anuncios_en_municipios_n_mayor_igual_10")), True),
    ]

    # Las medianas por portal salen del desglose de _anuncios_2026.py, no de un CSV:
    # aqui solo se vigila que el literal siga siendo el que se publico en el guion.
    checks += [("portal fotocasa EUR/mes", "1.432 €", True),
               ("portal realtyapi EUR/m2", "19,43", True)]

    raw = len((ROOT / "docs" / "raw_manifest_sha256.txt").read_text(encoding="utf-8").splitlines())
    silver = len((PROC / "manifest_sha256.txt").read_text(encoding="utf-8").splitlines())
    checks += [("raw SHA", f">{raw}<", True), ("silver", f">{silver}<", True),
               ("tests", "287 tests", True)]

    print(f"Deck: {DECK.relative_to(ROOT)}")
    fallos = 0
    for etiqueta, aguja, _guard in checks:
        where = html if aguja.startswith("<") or aguja.startswith(">") else plano
        ok = aguja in where
        fallos += 0 if ok else 1
        print(f"  {'OK   ' if ok else 'FALLA'} {etiqueta:<30} {aguja}")

    print(f"\n{len(checks) - fallos}/{len(checks)} cifras coinciden")
    if fallos:
        print("Revisa index.html: hay literales que ya no salen de los CSV gold.")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
