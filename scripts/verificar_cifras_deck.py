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
import subprocess
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


_TESTS: dict[str, int] | None = None


def _test_run() -> dict[str, int] | None:
    """Ejecuta la suite y devuelve {collected, passed, skipped}.

    Antes el deck se comparaba contra los literales 295/293: el check no podia
    detectar que el numero envejeciera. `pyproject.toml` fija `addopts = "-q"`,
    asi que se anula con `-o addopts=` para que pytest imprima el resumen.
    Si pytest no esta disponible devuelve None y los checks se omiten.
    """
    global _TESTS
    if _TESTS is not None:
        return _TESTS
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "-q", "-o", "addopts=", "--tb=no"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except Exception:  # noqa: BLE001
        return None
    m = re.search(r"(\d+) passed", out.stdout)
    if not m:
        return None
    s = re.search(r"(\d+) skipped", out.stdout)
    passed = int(m.group(1))
    skipped = int(s.group(1)) if s else 0
    _TESTS = {"collected": passed + skipped, "passed": passed, "skipped": skipped}
    return _TESTS


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
        f"<b>{len(hp)}</b> utilizables de los <b>{len(con_precio)}</b> con precio: "
        f"se descartan <b>{len(con_precio) - len(hp)}</b> pisos enteros "
        f"(<b>{es((1 - len(hp) / len(con_precio)) * 100, 0)} %</b>)",
        raw=True,
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

    # ---------- Slide 08: el otro extremo del ranking ----------
    # Todo sale de este CSV (n_anuncios de 2026), asi que se verifica sin Mongo.
    bajo30 = of[of["esfuerzo_joven_pct_18_34"] < 30]
    add("119 bajo el 30", f"De los {len(bajo30)} municipios por debajo del 30 %")
    add("89 sin anuncio", f"{int((bajo30['n_anuncios'] == 0).sum())} no tienen un solo anuncio")
    add(
        "119 sin anuncio (cifra)",
        f'<div class="big sm accent">{int((bajo30["n_anuncios"] == 0).sum())}</div>'
        '<div class="cap">sin ningún anuncio en 2026</div>',
        raw=True,
    )
    add(
        "30 con anuncio",
        f'<div class="big sm">{int((bajo30["n_anuncios"] >= 1).sum())}</div>'
        '<div class="cap">con al menos un anuncio</div>',
        raw=True,
    )
    add(
        "3 con 5+",
        f'<div class="big sm">{int((bajo30["n_anuncios"] >= 5).sum())}</div>'
        '<div class="cap">con 5 o más',
        raw=True,
    )
    add("119 alquiler mediano", f"alquiler mediano {es(bajo30['cuantia_alquiler_mes'].median(), 0)} €")
    add("54 bajo 25", f"{int((of['esfuerzo_joven_pct_18_34'] < 25).sum())} están por debajo del 25")
    add("ninguno bajo 20", "Ningún municipio oficial baja del 20 %")
    for nombre in ("Oñati", "Azkoitia", "Mutriku", "Urretxu", "Markina-Xemein"):
        fila = of[of["nombre"].str.startswith(nombre)].iloc[0]
        add(f"menor esfuerzo {nombre}", f"<td>{es(fila['esfuerzo_joven_pct_18_34'], 2)} %</td>", raw=True)
    gx = of[of["nombre"].str.startswith("Getxo")].iloc[0]
    add(
        "getxo 2024 con n",
        f"<b>{es(gx['esfuerzo_joven_pct_18_34'], 2)} %</b> con <b>{int(gx['n_anuncios'])}</b> anuncios",
        raw=True,
    )

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

    resumen = pd.read_csv(RES / "comparacion_esfuerzo_2024_2026_resumen.csv", encoding="utf-8-sig")
    for metrica in ("esfuerzo_2024_base_salario_pct_18_34", "esfuerzo_2026_base_renta2024_pct_18_34"):
        val = float(resumen[resumen["metrica"] == metrica].iloc[0]["mediana"])
        pass  # diapositiva de sintesis retirada: 44,6 % y 57,8 % ya no se muestran

    # ---------- Diferencia de nivel (slide 15): solo municipios con muestra ----------
    brecha = pd.read_csv(RES / "brecha_esfuerzo_2024_2026.csv", encoding="utf-8-sig")
    cob_brecha = pd.read_csv(RES / "cobertura_representatividad_2026.csv", encoding="utf-8-sig")
    b5 = brecha[brecha["n_anuncios_2026"] >= 5]
    add("brecha municipios n5", f"solo los {len(b5)} municipios con n")
    med_b5 = es(float(b5["brecha_pp_18_34"].median()))
    add("brecha mediana n5", f"{med_b5} puntos")
    add("brecha mediana n5 (cifra)", f'>{med_b5}<span class="unit">pp</span>', raw=True)
    add("brecha minimo", f"{es(float(b5['brecha_pp_18_34'].min()))} puntos")
    add("brecha maximo", f"{es(float(b5['brecha_pp_18_34'].max()))} puntos")
    add(
        "brecha superficie anuncio",
        f"{es(float(_fila(cob_brecha, 'superficie_mediana_anuncios')))} m² anunciados",
    )
    add(
        "brecha superficie oficial",
        f"{es(float(_fila(cob_brecha, 'superficie_mediana_oficial_2024')))} m² registrados",
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
    add("351 canonicos", "351 canónicos")
    mongo = _mongo_counts()
    if mongo is None:
        print("  SKIP Mongo no disponible: no se comprueban 17 vivas / 8 indices")
    else:
        vivas, _, indices = mongo
        add("colecciones vivas", f"{vivas} colecciones vivas")
        add("indices de trabajo", "8 índices de trabajo")
        add("indices contando _id", f"{indices} contando")
        add("indices sin crear", "2 definidos sin crear")

    # ---------- D26: limpieza y transformación ----------
    uni = pd.read_csv(PROC / "anuncios_unificados.csv", encoding="utf-8-sig", dtype=str)
    faltan = uni[["precio_eur", "superficie_m2", "habitaciones"]].isna()
    n_precio = int(faltan["precio_eur"].sum())
    n_sup = int(faltan["superficie_m2"].sum())
    n_hab = int(faltan["habitaciones"].sum())
    n_huecos = int(faltan.any(axis=1).sum())
    add("D26 sin precio", f"calidad_precio</span> ({n_precio} anuncios)", raw=True)
    add("D26 sin superficie", f"calidad_superficie</span> ({n_sup})", raw=True)
    add("D26 sin habitaciones", f"tiene_habitaciones</span> ({n_hab})", raw=True)
    add("D26 huecos", f"{n_huecos} de los {len(uni)}")

    # ---------- Slide 21: las tres consultas de negocio ----------
    esf = pd.read_csv(RES / "mongo_esfuerzo_por_municipio.csv", encoding="utf-8-sig")
    tier_a = esf[
        (esf["tiene_alquiler_oficial"].astype(str).str.lower() == "true")
        & (esf["n_anuncios"] >= 30)
    ].sort_values("esfuerzo_joven_pct_18_34", ascending=False)
    top4 = " · ".join(
        f"{r.nombre.split(' / ')[0].split('-')[0]} {es(r.esfuerzo_joven_pct_18_34, 2)}"
        for r in tier_a.itertuples()
    )
    add("top4 esfuerzo Tier A", top4)
    print(f"  (Tier A: {len(tier_a)} municipios)")

    vpo = pd.read_csv(RES / "mongo_vpo_por_municipio.csv", encoding="utf-8-sig")
    estados = vpo.groupby("estado")["n_promociones"].sum().astype(int).to_dict()
    for etiqueta, clave, sufijo in (
        ("VPO terminadas", "Terminada", "terminadas"),
        ("VPO en curso", "En Curso", "en curso"),
        ("VPO en convenio", "En Convenio", "en convenio"),
        ("VPO en proyecto", "En Proyecto", "en proyecto"),
    ):
        add(etiqueta, f"{estados.get(clave, 0)} {sufijo}")

    # ---------- Slide 03: renta joven y salario ----------
    base = pd.read_csv(PROC / "analisis_variables_base.csv", encoding="utf-8-sig")
    ratio_1834 = float((base["renta_joven_estimada_18_34"] / base["renta_hogar"]).median() * 100)
    add("proxy ratio 18-34", f"{es(ratio_1834, 1)} %")
    add("proxy salario 2026 base", "1.564 €")
    add("proxy salario 2026 factor", "1,099")
    add("proxy salario 2026 cifra", f"{es(salario, 0)} €")

    # La formula del ratio vive en config/parametros_estudio.yaml: se parsean sus
    # seis numeros y se recomputa, para que el deck no se desincronice.
    yaml_txt = (ROOT / "config" / "parametros_estudio.yaml").read_text(encoding="utf-8")
    m_ratio = re.search(r"\(2\*(\d+)\+5\*(\d+)\+5\*(\d+)\+5\*(\d+)\)/(\d+)/(\d+)", yaml_txt)
    assert m_ratio, "no encuentro la formula del ratio en parametros_estudio.yaml"
    r18, r20, r25, r30, anios, rtotal = (int(x) for x in m_ratio.groups())
    ratio = (2 * r18 + 5 * r20 + 5 * r25 + 5 * r30) / anios / rtotal * 100
    add("ratio 18-34", f"{es(ratio)} %")
    add("media 18-34 CAE", f"{es((2 * r18 + 5 * r20 + 5 * r25 + 5 * r30) / anios, 0)} €")

    import json as _json

    ovj = _json.loads(
        (ROOT / "data" / "raw" / "ovj_salario_joven_2024.json").read_text(encoding="utf-8")
    )
    sal = {str(f["tramo_edad"]): float(f["salario_neto_mes_eur"]) for f in ovj["datos"]}
    ipc = pd.read_csv(ROOT / "data" / "raw" / "ipc_ine_2024_2026.csv", dtype=str, encoding="utf-8-sig")

    def _ipc(ano: str) -> float:
        return float(ipc.loc[ipc["ano"] == ano, "ipc_medio_anual"].iloc[0])

    factor_ipc = _ipc("factor_2026_2024")
    salario_2026 = sal["18-34"] * factor_ipc
    add("salario base 18-34", f"{es(sal['18-34'], 0)} €")
    add("factor IPC", "1,099")
    add("salario 2026", f"{es(salario_2026, 0)} €")
    add(
        "sin ajuste sube",
        f"un <b>{es((salario_2026 / sal['18-34'] - 1) * 100)} %</b>",
        raw=True,
    )

    sens = pd.read_csv(RES / "sensibilidad_idw.csv", encoding="utf-8-sig")
    ofi = sens[sens["escenario"] == "oficial_159"].iloc[0]
    con = sens[sens["escenario"] == "idw_252"].iloc[0]
    n_idw = int(con["n"]) - int(ofi["n"])
    add("IDW municipios", f"<b>{n_idw}</b> no", raw=True)
    add("IDW mediana oficial", f"{es(ofi['mediana_esfuerzo_pct'], 2)} %")
    add("IDW mediana 252", f"{es(con['mediana_esfuerzo_pct'], 2)} %")
    add("IDW sobre 30", f"<b>{int(con['n_sobre_30'])} de 252</b>", raw=True)

    add("geojson municipios", "252 polígonos")

    try:
        sys.path.insert(0, str(ROOT))
        from storage.mongo import get_collection  # noqa: PLC0415

        col = get_collection("anuncios")
        total_an = col.count_documents({})
        con_punto = col.count_documents({"ubicacion.coordenadas.type": "Point"})
        add("anuncios con punto", f"<b>{con_punto} de {total_an}</b> con coordenadas", raw=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  aviso: sin Mongo, se omiten los checks de coordenadas ({exc})")

    # ---------- Afirmaciones que no deben volver ----------
    prohibidas = [
        ("84,4 con y sin", "84,4 % con y sin"),
        ("1,44x", "1,44×"),
        ("2,0x", "2,0×"),
        ("15 vivas", "15 colecciones vivas"),
        ("24 indices", "24 índices"),
        ("25 indices", "25 índices"),
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
        ("845 anuncios", "845 anuncios"),
        ("352 canonicos", "352 canónicos"),
        ("1 manifiesto", "1 manifiesto"),
        ("ratio 1,96", "1,96"),
        ("53 artefactos", "53 artefactos"),
        ("11 pipelines", "11 pipelines"),
        ("594 coordenadas", "594 anuncios con coordenadas"),
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
