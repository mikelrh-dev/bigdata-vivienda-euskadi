"""Comprueba que las cifras que enseña el deck siguen saliendo de los CSV gold.

Motivo: `docs/presentacion_v2/index.html` es el unico artefacto escrito a mano, y ya se
quedo una vez con el corte viejo (79,3 % / 52 municipios) mientras los CSV ya daban
78,6 % / 50 municipios. En la v3 se anaden las comprobaciones que faltaban: la unidad
del 78,6 % frente al 87,3 % de los anuncios, el 1.350 € de medianas municipales frente
al 1.500 € de anuncios, el 1,88x, y los conteos 17/25/53.

No escribe nada. Uso:

    python scripts/verificar_cifras_deck.py
"""

from __future__ import annotations

import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs" / "presentacion_v2" / "index.html"
PROC = ROOT / "data" / "procesado"
RES = ROOT / "data" / "resultados"

sys.path.insert(0, str(ROOT / "transform"))
from _anuncios_2026 import cargar_anuncios_2026  # noqa: E402


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


def _mongo_counts() -> tuple[int, int, int] | None:
    """(vivas, backup, indices) leidos de Mongo; None si no esta disponible."""
    try:
        from pymongo import MongoClient

        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGO_DB", "vivienda_euskadi")
        client = MongoClient(uri, serverSelectionTimeoutMS=1500)
        db = client[db_name]
        names = db.list_collection_names()
        vivas = [n for n in names if "__backup" not in n]
        backup = [n for n in names if "__backup" in n]
        indices = sum(len(list(db[n].list_indexes())) for n in vivas)
        return len(vivas), len(backup), indices
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    html = DECK.read_text(encoding="utf-8")
    plano = re.sub(r"<[^>]+>", "", html)  # asi '50<span>/252</span>' se lee '50/252'
    checks: list[tuple[str, str, bool, bool]] = []

    def add(label: str, needle: str, ok: bool = True, raw: bool = False) -> None:
        checks.append((label, needle, ok, raw))

    # ---------- 2026: municipio vs anuncio ----------
    mercado = pd.read_csv(PROC / "esfuerzo_mercado_2026.csv", encoding="utf-8-sig", dtype={"codigo_ine": str})
    ef = _col(mercado, "esfuerzo_mercado", "18_34")
    pr = _col(mercado, "precio_mediana", "eur_mes")
    sal_col = _col(mercado, "salario_joven_2026", "18_34")
    serie = mercado[ef].dropna()
    med_mun = float(serie.median())
    precio_mun = float(mercado[pr].median())
    salario = float(mercado[sal_col].median())

    df, _meta = cargar_anuncios_2026()
    v = df[df["anuncio_valido"]].dropna(subset=["precio_eur"]).copy()
    esfuerzo_anuncio = v["precio_eur"] / salario * 100
    med_anuncio = float(esfuerzo_anuncio.median())
    med_sin_realty = float(esfuerzo_anuncio[v["portal"] != "realtyapi"].median())
    precio_anuncio = float(v["precio_eur"].median())
    pct_30 = float((esfuerzo_anuncio > 30).mean() * 100)

    add("mediana municipal 2026", f"{es(med_mun)} %")
    add("mediana anuncio 2026", f"{es(med_anuncio)} %")
    add("mediana sin realtyapi", f"{es(med_sin_realty)} %")
    add("precio mediana municipal", f"{es(precio_mun, 0)} €")
    add("precio mediana anuncio", f"{es(precio_anuncio, 0)} €")
    add("salario joven 2026", f"{es(salario, 0)} €")
    add("anuncios > 30 %", f"{es(pct_30)} %")
    add("municipios con anuncio", f"{len(serie)}/252")
    add("anuncios validos", f"{int(mercado['n_anuncios_2026'].sum())} anuncios")

    # ---------- Tipologia ----------
    tipo = pd.read_csv(RES / "esfuerzo_por_tipo_nivel_anuncio_2026.csv", encoding="utf-8-sig")
    for _, r in tipo.iterrows():
        etiqueta = r["tipo_de_vivienda"]
        add(f"tipo {etiqueta}", f"{es(r['esfuerzo_mediana_anuncios_pct_18_34'])} %")
        add(f"n {etiqueta}", f"<td>{int(r['n_anuncios'])}</td>", raw=True)

    # ---------- 2024 oficial ----------
    mun = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", encoding="utf-8-sig")
    of = mun[mun["metodo_imputacion"] == "oficial"]
    med24 = float(of["esfuerzo_joven_pct_18_34"].median())
    add("mediana oficial 2024", f"{es(med24, 2)} %")
    add("40 de 159", f"{int((of['esfuerzo_joven_pct_18_34'] > 30).sum())} de 159")
    add("47 de 252", f"{int((mun['esfuerzo_joven_pct_18_34'] > 30).sum())} de 252")

    resumen = pd.read_csv(RES / "comparacion_esfuerzo_2024_2026_resumen.csv", encoding="utf-8-sig")
    for metrica in ("esfuerzo_2024_base_salario_pct_18_34", "esfuerzo_2026_base_renta2024_pct_18_34"):
        val = float(resumen[resumen["metrica"] == metrica].iloc[0]["mediana"])
        add(metrica.split("_")[1] + " base comun", f"{es(val)} %")

    alq = pd.read_csv(RES / "mongo_alquiler_por_municipio.csv", encoding="utf-8-sig", dtype={"_id": str})
    alq["codigo_ine"] = alq["_id"].str.zfill(5)
    base = mercado[mercado["n_anuncios_2026"] > 0][["codigo_ine", pr, _col(mercado, "mediana_m2")]]
    j = base.merge(alq[["codigo_ine", "cuantia_media", "renta_m2_media"]], on="codigo_ine")
    ratio = float((j[pr] / j["cuantia_media"]).median())
    ratio_m2 = float((j[_col(mercado, "mediana_m2")] / j["renta_m2_media"]).median())
    add("ratio precio 2026/2024", f"{es(ratio, 2)}×")
    add("ratio €/m2 2026/2024", f"{es(ratio_m2, 2)}×")

    # ---------- Cobertura ----------
    cob = pd.read_csv(RES / "cobertura_representatividad_2026.csv", encoding="utf-8-sig")
    add("cobertura poblacion 18-34", f"{es(_fila(cob, 'pct_poblacion_18_34_cubierta'))} %")
    add("4 municipios n>=10", f"{es(_fila(cob, 'pct_anuncios_en_municipios_n_mayor_igual_10'))} %")

    # ---------- Sistema ----------
    raw = len((ROOT / "docs" / "raw_manifest_sha256.txt").read_text(encoding="utf-8").splitlines())
    silver = len((PROC / "manifest_sha256.txt").read_text(encoding="utf-8").splitlines())
    gold = len(list(RES.glob("*.csv"))) + len(list(RES.glob("*.png")))
    add("raw manifest", f"{raw} SHA")
    add("silver", f"{silver}/183")
    add("gold", f"{gold}/{gold}")
    add("353 HDFS", "353 objetos")
    add("352 canonicos", "352 canónicos")
    add("tests", "287 tests")
    add("tests pasan", "285 pasan")

    mongo = _mongo_counts()
    if mongo is None:
        print("  SKIP Mongo no disponible: no se comprueban 17 vivas / 25 indices")
    else:
        vivas, backup, indices = mongo
        add("colecciones vivas", f"{vivas} colecciones vivas")
        add("colecciones backup", f"{backup} backup")
        add("indices", f"{indices} índices")

    # ---------- Afirmaciones que no deben volver ----------
    prohibidas = [
        ("84,4 con y sin", "84,4 % con y sin"),
        ("1,44x", "1,44×"),
        ("2,0x", "2,0×"),
        ("15 vivas", "15 colecciones vivas"),
        ("24 indices", "24 índices"),
        ("63 gold", "63/63"),
        ("63 artefactos", "63 artefactos"),
        ("corrida real OK", "corrida real OK"),
        ("municipios.codigo_ine", "municipios.codigo_ine"),
        ("compartir 3-4", "compartir un piso de 3-4"),
    ]
    for etiqueta, aguja in prohibidas:
        add(f"prohibido: {etiqueta}", aguja, ok=False)

    print(f"Deck: {DECK.relative_to(ROOT)}")
    fallos = 0
    for etiqueta, aguja, esperado, raw_mode in checks:
        where = html if raw_mode or aguja.startswith("<") else plano
        presente = aguja in where
        ok = presente if esperado else not presente
        fallos += 0 if ok else 1
        estado = "OK   " if ok else "FALLA"
        print(f"  {estado} {etiqueta:<32} {aguja}")

    print(f"\n{len(checks) - fallos}/{len(checks)} comprobaciones pasan")
    if fallos:
        print("Revisa index.html: hay literales que ya no salen de los CSV gold o afirmaciones retiradas.")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
