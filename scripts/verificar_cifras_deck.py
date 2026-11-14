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

    # ---------- Modalidades y embudo 2026 (B5/D8) ----------
    mod = pd.read_csv(RES / "mongo_modalidades.csv", encoding="utf-8-sig")
    mod = mod.set_index("modalidad")
    sup_t = float(mod.loc["temporal", "mediana_superficie_m2"])
    sup_l = float(mod.loc["larga_estancia", "mediana_superficie_m2"])
    m2_t = float(mod.loc["temporal", "mediana_eur_m2"])
    m2_l = float(mod.loc["larga_estancia", "mediana_eur_m2"])
    add("B5 superficie temporal", f"{es(sup_t, 0)} m²")
    add("B5 superficie larga", f"{es(sup_l, 0)} m²")
    add("B5 €/m2", f"{es(m2_t, 2)} vs {es(m2_l, 2)}")
    add("B5 +13,7 %", f"+{es((m2_t / m2_l - 1) * 100)} %")
    add("D8 piso temporal", "piso completo · temporal")
    add("D8 habitaciones aparte", "habitación · colección aparte")
    add("D8 297 con precio", "297 con precio")

    # Composicion de los 795 productos de oferta 2026 (594 vivienda + 201 habitaciones).
    n_larga = int(mod.loc["larga_estancia", "n"])
    n_temp = int(mod.loc["temporal", "n"])
    n_hab = len(pd.read_csv(PROC / "anuncios_habitaciones_unificados.csv", encoding="utf-8-sig"))
    n_795 = n_larga + n_temp + n_hab
    add("D8 % piso larga", f"{es(n_larga / n_795 * 100, 0)} %")
    add("D8 % piso temporal", f"{es(n_temp / n_795 * 100, 0)} %")
    add("D8 % habitacion", f"{es(n_hab / n_795 * 100, 0)} %")
    add("D8 % 287 sobre 795", f"{es(int(mercado['n_anuncios_2026'].sum()) / n_795 * 100, 0)} %")

    # ---------- Habitaciones (B4) ----------
    # El deck publica el conjunto plausible: al silver se le aplica el mismo
    # tope municipal que el pipeline (`mongo_aggregations._hab_tope_stages`),
    # leido del gold y no tecleado.
    hab_gold = pd.read_csv(
        RES / "mongo_habitaciones_por_municipio.csv",
        encoding="utf-8-sig",
        dtype={"codigo_ine": str},
    )
    hab = pd.read_csv(
        PROC / "anuncios_habitaciones_unificados.csv",
        encoding="utf-8-sig",
        dtype={"codigo_ine": str},
    )
    hab["precio_eur"] = pd.to_numeric(hab["precio_eur"], errors="coerce")
    tope_hab = dict(zip(hab_gold["codigo_ine"].str.zfill(5), hab_gold["tope_alquiler_eur_mes"]))
    hab["_tope"] = hab["codigo_ine"].str.zfill(5).map(tope_hab)
    con_precio = hab["precio_eur"].dropna()
    hp = hab.loc[hab["precio_eur"] < hab["_tope"], "precio_eur"].dropna()
    add(
        "B4 utilizables",
        f"quedan {len(hp)}. Se descartan {len(con_precio) - len(hp)} pisos enteros "
        f"({es((1 - len(hp) / len(con_precio)) * 100, 0)} %)",
    )
    add("B4 mediana global", f"{es(hp.median(), 0)} €")
    add("B4 87% <=700", f"{es((hp <= 700).mean() * 100, 0)} %")
    add("B4 esfuerzo global", f"{es(hp.median() / salario * 100)} %")
    # Slide 10: el conjunto plausible y su comparacion con el piso entero de 2026.
    add(
        "habitacion utilizables",
        f"<b>{len(hp)}</b> utilizables de los <b>{len(con_precio)}</b> con precio",
        raw=True,
    )
    add(
        "habitacion descartados",
        f"<b>{len(con_precio) - len(hp)}</b> pisos enteros",
        raw=True,
    )
    add("habitacion mediana y salario", f"{es(hp.median(), 0)} € sobre {es(salario, 0)} €")
    for municipio, etiqueta, clave in (
        ("Donostia - San Sebastián", "Donostia", "donostia"),
        ("Bilbao", "Bilbao", "bilbao"),
    ):
        fila = hab_gold.loc[hab_gold["municipio"] == municipio].iloc[0]
        med = float(fila["mediana_precio_eur"])
        add(f"B4 esfuerzo {etiqueta}", f"{es(med / salario * 100)} %")
        add(f"B4 n {etiqueta}", f"{etiqueta} ({int(fila['n_precio'])})")
        add(f"B4 tope {etiqueta}", f"más que el piso típico")

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

    # ---------- Ranking 2024 (slide 07) ----------
    cmp = pd.read_csv(
        RES / "comparacion_esfuerzo_2024_2026.csv", encoding="utf-8-sig", dtype={"codigo_ine": str}
    )
    ranking = {str(r["nombre_canonico"]): r for _, r in cmp.iterrows()}
    for nombre, etiqueta in (
        ("Barakaldo", "Barakaldo"),
        ("Donostia / San Sebastián", "Donostia"),
        ("Sestao", "Sestao"),
    ):
        fila = ranking[nombre]
        # El simbolo va en un `unit` span (38,5<span>%</span>) o en texto (38,2 %):
        # se comprueba la cifra sola, que es la que viene del CSV.
        add(
            f"{etiqueta} esfuerzo 2024",
            es(fila["esfuerzo_2024_canonico_pct_18_34"]),
        )
        add(
            f"{etiqueta} alquiler 2024",
            f"{es(fila['cuantia_media_eur_mes_mediana'], 0)} €",
        )
    add("ranking 14 filas", f"<b>14</b> que pasan del 35 %", raw=True)

    # ---------- VPO (slide 10) ----------
    vpo_term = pd.read_csv(
        RES / "mongo_vpo_terminadas_por_municipio.csv", encoding="utf-8-sig"
    )
    add("VPO municipios con dato", f"{len(vpo_term)} municipios con dato")
    add(
        "VPO municipios en cero",
        f"{int((vpo_term['vpo_terminadas_por_mil'] == 0).sum())} en cero",
    )
    vpo_prom = pd.read_csv(RES / "mongo_vpo_por_municipio.csv", encoding="utf-8-sig")
    add("VPO promociones", f"{int(vpo_prom['n_promociones'].sum())}</b>, en {vpo_prom['codigo_ine'].nunique()} municipios", raw=True)
    add("VPO sin viviendas", f"{int(vpo_prom['n_promociones'].sum())} de {int(vpo_prom['n_promociones'].sum())}", raw=True)
    # Serie Udalmap: la fila CAE resume Euskadi; el CSV llega en formato ancho.
    wide = pd.read_csv(
        ROOT / "data" / "raw" / "udalmap_vpo_terminadas.csv",
        encoding="latin-1",
        sep=";",
        header=None,
    )
    cae = wide[wide[0].astype(str).str.strip() == "CAE"].iloc[0]
    serie = dict(zip([str(x) for x in wide.iloc[3, 2:].tolist()], cae[2:].tolist()))
    for anio in ("2024", "2011"):
        add(
            f"VPO CAE {anio}",
            f"{es(float(str(serie[anio]).replace(',', '.')), 1)} ‰",
        )

    # ---------- Validacion SERPAVI (slide 7) ----------
    # Solo los municipios con alquiler oficial en ambos registros: incluir la
    # fila sin oficial movia Spearman de 0,988 a 0,979.
    ser = pd.read_csv(RES / "validacion_alquiler_2024_serpavi.csv", encoding="utf-8-sig")
    ser = ser[ser["tiene_alquiler_oficial"].astype(str).str.lower() == "true"]
    ser = ser.dropna(subset=["eustat_eur_m2", "serpavi_eur_m2"])
    add("SERPAVI ratio", f"{es((ser['serpavi_eur_m2'] / ser['eustat_eur_m2']).median(), 3)}")
    add(
        "SERPAVI spearman",
        f"{es(ser[['eustat_eur_m2', 'serpavi_eur_m2']].corr(method='spearman').iloc[0, 1], 3)}",
    )
    add(
        "SERPAVI dentro 25",
        f"{int((ser['diff_eur_m2'].abs() / ser['eustat_eur_m2'] <= 0.25).sum())}/{len(ser)}",
    )

    # ---------- Tier A (nota de la slide 11) ----------
    tier = pd.read_csv(RES / "mongo_tier_confianza.csv", encoding="utf-8-sig")
    ns_tier_a = tier[tier["tier"] == "A"].sort_values("n_anuncios", ascending=False)["n_anuncios"]
    add("tier A n", "/".join(str(int(x)) for x in ns_tier_a))

    # ---------- Contexto de la tabla (slide 11) ----------
    modal = pd.read_csv(RES / "mongo_modalidades.csv", encoding="utf-8-sig")
    n_mod = {str(r["modalidad"]): int(r["n"]) for _, r in modal.iterrows()}
    n_2026 = n_mod["larga_estancia"] + n_mod["temporal"]
    # La 11 se reconstruyo con la figura de los cuatro: el contexto del embudo
    # va en una linea de texto, no en tres cifras grandes.
    add("contexto 594", f"{n_2026} anuncios de 2026")
    add("contexto 287", f"{len(v)} válidos")
    n_cuatro = int(
        mercado.loc[
            mercado["codigo_ine"].isin(["48020", "20069", "48044", "01059"]),
            _col(mercado, "n_precio"),
        ].sum()
    )
    add("contexto cuatro municipios", f"reúnen {n_cuatro}")
    add("contexto resto", f"{len(v) - n_cuatro} válidos")
    cob_pob = pd.read_csv(RES / "cobertura_representatividad_2026.csv", encoding="utf-8-sig")
    add(
        "cobertura poblacion",
        f"{es(float(cob_pob.loc[cob_pob['metrica'] == 'pct_poblacion_18_34_cubierta', 'valor'].iloc[0]))} %",
    )
    tier_conteo = tier.groupby("tier").size().to_dict()
    add(
        "tier conteos",
        "A {} , B {} , C {} , D {}".format(
            tier_conteo.get("A"), tier_conteo.get("B"), tier_conteo.get("C"), tier_conteo.get("D")
        ).replace(" ,", ","),
    )

    resumen = pd.read_csv(RES / "comparacion_esfuerzo_2024_2026_resumen.csv", encoding="utf-8-sig")
    for metrica in ("esfuerzo_2024_base_salario_pct_18_34", "esfuerzo_2026_base_renta2024_pct_18_34"):
        val = float(resumen[resumen["metrica"] == metrica].iloc[0]["mediana"])
        add(metrica.split("_")[1] + " base comun", f"{es(val)} %")

    # ---------- Diferencia de nivel (slide 15): solo municipios con muestra ----------
    brecha = pd.read_csv(RES / "brecha_esfuerzo_2024_2026.csv", encoding="utf-8-sig")
    cob_brecha = pd.read_csv(RES / "cobertura_representatividad_2026.csv", encoding="utf-8-sig")
    b5 = brecha[brecha["n_anuncios_2026"] >= 5]
    add("brecha municipios n5", f"solo los {len(b5)} municipios con n")
    med_b5 = es(float(b5["brecha_pp_18_34"].median()))
    add("brecha mediana n5", f"{med_b5} puntos")
    add("brecha mediana n5 (cifra)", f'>{med_b5}<span class="unit">pp</span>', raw=True)
    add("brecha minimo", f"{es(float(b5['brecha_pp_18_34'].min()))} pp")
    add("brecha maximo", f"{es(float(b5['brecha_pp_18_34'].max()))} pp")
    add(
        "brecha superficie anuncio",
        f"{es(float(_fila(cob_brecha, 'superficie_mediana_anuncios')))} m² de anuncio",
    )
    add(
        "brecha superficie oficial",
        f"{es(float(_fila(cob_brecha, 'superficie_mediana_oficial_2024')))} m² del registrado",
    )

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
    add("tests", "295 tests")
    add("tests pasan", "293 pasan")

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
        ("B5 92,5", "92,5 m²"),
        ("B5 +23,2", "+23,2 %"),
        ("D8 268 habitaciones", "268 habitaciones"),
        ("B4 640", "640 €"),
        ("B4 1.200 habitaciones", "1.200 €"),
        ("B4 69,8", "69,8 %"),
        ("B4 37,2", "37,2 %"),
        ("287 tests", "287 tests"),
        ("54/54", "54/54"),
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
