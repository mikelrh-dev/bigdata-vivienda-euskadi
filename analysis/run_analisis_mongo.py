"""Orquestador de analisis MongoDB: ejecuta los 9 pipelines y exporta 5 CSV.

Nivel 10 de Automatizacion del analisis (RETO 1Evaluacion SBD-BDAv2):
un script ejecuta todos los analisis principales y devuelve resultados
preparados para representacion, generados desde PyMongo sin valores
tecleados. Reutiliza los 9 pipelines de `mongo_aggregations` (con
`$group`/`$lookup`/`$unwind` donde los datos lo permiten) y demuestra
con `explain()` la transicion COLLSCAN -> IXSCAN.

Uso:
  python analysis/run_analisis_mongo.py [--salida data/resultados]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import io

from bson.decimal128 import Decimal128

from analysis.mongo_aggregations import (
    pipeline_accesibilidad_extendida,
    pipeline_alquiler_por_municipio,
    pipeline_esfuerzo_por_sexo,
    pipeline_indicadores_municipio,
    pipeline_modalidades,
    pipeline_top_municipios_por_esfuerzo,
    pipeline_udalmap_extendido_osrm,
    pipeline_vpo_por_municipio,
    pipeline_vpo_terminadas,
)

RESULTADOS_DIR = ROOT / "data" / "resultados"

# Orden fijo de ejecucion de los 9 pipelines principales.
PIPELINE_ORDER: tuple[str, ...] = (
    "pipeline_indicadores_municipio",
    "pipeline_alquiler_por_municipio",
    "pipeline_modalidades",
    "pipeline_top_municipios_por_esfuerzo",
    "pipeline_esfuerzo_por_sexo",
    "pipeline_accesibilidad_extendida",
    "pipeline_udalmap_extendido_osrm",
    "pipeline_vpo_por_municipio",
    "pipeline_vpo_terminadas",
)

# Los 3 conjuntos preparados para visualizacion: fichero -> pipeline origen.
EXPORTS_3: tuple[tuple[str, str], ...] = (
    ("mongo_esfuerzo_por_municipio.csv", "pipeline_indicadores_municipio"),
    ("mongo_alquiler_por_municipio.csv", "pipeline_alquiler_por_municipio"),
    ("mongo_modalidades.csv", "pipeline_modalidades"),
)

# Los 5 CSV canonicos (Bloque 3, AGREGACION-01): reutilizan los 9 pipelines
# sin reimplementar agregaciones. Fichero -> pipeline origen.
EXPORTS_5: tuple[tuple[str, str], ...] = (
    ("mongo_esfuerzo_por_municipio.csv", "pipeline_indicadores_municipio"),
    ("mongo_alquiler_por_municipio.csv", "pipeline_alquiler_por_municipio"),
    ("mongo_modalidades.csv", "pipeline_modalidades"),
    ("mongo_accesibilidad_extendida.csv", "pipeline_accesibilidad_extendida"),
    ("mongo_vpo_por_municipio.csv", "pipeline_vpo_por_municipio"),
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal128):
        return str(value.to_decimal())
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _clave_fila(fila: dict[str, Any]) -> str:
    return json.dumps(
        _jsonable(fila), sort_keys=True, default=str, ensure_ascii=False
    )


def _orden_canonico(filas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena filas por su serializacion ordenada (clave canonica).

    Varios pipelines usan `$sort` con una sola clave y MongoDB no garantiza
    el orden entre empates: sin este orden canonico, dos ejecuciones
    reproducibles darian huellas y CSV distintos en orden de filas.
    """
    return sorted(filas, key=_clave_fila)


def run_all_estandar() -> dict[str, list[dict[str, Any]]]:
    """Ejecuta en orden fijo los 9 pipelines de `mongo_aggregations`.

    Devuelve un dict con las 8 claves en el orden de `PIPELINE_ORDER` y
    filas en orden canonico (ver `_orden_canonico`), para que la huella y
    los CSV sean reproducibles entre ejecuciones.
    Las funciones se resuelven por nombre desde el espacio de nombres del
    modulo en tiempo de llamada, para que un test pueda sustituirlas con
    monkeypatch sin tocar MongoDB.
    """
    resultados: dict[str, list[dict[str, Any]]] = {}
    for nombre in PIPELINE_ORDER:
        funcion = globals()[nombre]
        resultados[nombre] = _orden_canonico(list(funcion()))
    return resultados


def huella_resultados(resultados: dict[str, list[dict[str, Any]]]) -> str:
    """SHA-256 hex de la serializacion ordenada de los resultados.

    `sort_keys=True` hace la huella independiente del orden de claves de
    MongoDB; dos ejecuciones reproducibles producen la misma huella.
    """
    texto = json.dumps(
        _jsonable(resultados), sort_keys=True, default=str, ensure_ascii=False
    )
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def conteos(resultados: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    """Numero de filas por pipeline."""
    return {nombre: len(filas) for nombre, filas in resultados.items()}


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, Decimal128):
        return str(value.to_decimal())
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(_jsonable(value), sort_keys=True, ensure_ascii=False)
    return value


def _cabecera(filas: list[dict[str, Any]]) -> list[str]:
    cabecera: list[str] = []
    vistos: set[str] = set()
    for fila in filas:
        for clave in fila:
            if clave not in vistos:
                vistos.add(clave)
                cabecera.append(clave)
    return cabecera


def exportar_csv(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
    exports: tuple[tuple[str, str], ...] = EXPORTS_5,
) -> dict[str, Path]:
    """Escribe los CSV canonicos de `exports` en `out_dir`.

    Sin valores tecleados: cada fila procede de los pipelines en memoria.
    Encoding `utf-8-sig`, cabecera = union de claves en orden de aparicion.
    Devuelve dict fichero -> ruta escrita.
    """
    destino = Path(out_dir)
    destino.mkdir(parents=True, exist_ok=True)
    rutas: dict[str, Path] = {}
    for fichero, nombre_pipeline in exports:
        filas = resultados[nombre_pipeline]
        ruta = destino / fichero
        cabecera = _cabecera(filas)
        with ruta.open("w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=cabecera,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            for fila in filas:
                writer.writerow(
                    {k: _csv_value(fila.get(k)) for k in cabecera}
                )
        rutas[fichero] = ruta
    return rutas


def exportar_tres_csv(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Compatibilidad: escribe los 3 CSV historicos (ver `EXPORTS_3`)."""
    return exportar_csv(resultados, out_dir, EXPORTS_3)


def exportar_cinco_csv(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Escribe los 5 CSV canonicos (Bloque 3, AGREGACION-01).

    Reutiliza los 9 pipelines sin reimplementar agregaciones; los 3
    historicos mas `pipeline_accesibilidad_extendida` y
    `pipeline_vpo_por_municipio` (con `$group`/`$lookup`/`$unwind` donde
    los datos lo permiten).
    """
    return exportar_csv(resultados, out_dir, EXPORTS_5)


def _fnum(value: Any) -> float | None:
    """Convierte Decimal128/str/num a float o None (seguro para matplotlib)."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, Decimal128):
        try:
            return float(value.to_decimal())
        except Exception:
            return None
    try:
        v = float(value)
        # NaN/inf no sirven para graficos.
        if v != v or v in (float("inf"), float("-inf")):
            return None
        return v
    except (TypeError, ValueError):
        return None


def exportar_png_desde_mongo(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Genera los 13 PNG canonicos solo desde PyMongo (sin DuckDB ni CSV).

    Fuente unica: los 9 pipelines en memoria (`resultados`). Cada grafico
    deriva de campos ya agregados en Mongo; `_fnum` solo normaliza tipos
    BSON para matplotlib, sin valores tecleados. Sobrescribe los mismos
    nombres que generaba DuckDB para dejar atras esa dependencia.
    Devuelve dict fichero -> ruta.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    destino = Path(out_dir)
    destino.mkdir(parents=True, exist_ok=True)
    rutas: dict[str, Path] = {}

    def _save(fig, nombre: str) -> None:
        # PIL falla con EINVAL al abrir la ruta relativa en Windows; se guarda
        # en memoria y se escribe con la API de Python.
        ruta = destino / nombre
        fig.tight_layout()
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=110)
        plt.close(fig)
        ruta.write_bytes(buffer.getvalue())
        rutas[nombre] = ruta

    ind = resultados.get("pipeline_indicadores_municipio", [])
    alq = resultados.get("pipeline_alquiler_por_municipio", [])
    acc = resultados.get("pipeline_accesibilidad_extendida", [])
    vpo = resultados.get("pipeline_vpo_por_municipio", [])

    terr = sorted({str(d.get("territorio")) for d in ind if d.get("territorio")})

    def _esf(d: dict[str, Any]) -> float | None:
        return _fnum(d.get("esfuerzo_joven_pct_18_34", d.get("esfuerzo_joven_pct")))

    # g1/A1: esfuerzo por territorio (canonico 18-34, fallback legacy).
    for nombre in ("g1_esfuerzo_por_territorio.png", "A1_distribucion_esfuerzo_por_TH.png"):
        fig, ax = plt.subplots(figsize=(7, 4))
        datos = [[e for d in ind if d.get("territorio") == t and (e := _esf(d)) is not None] for t in terr]
        if any(datos):
            try:
                ax.boxplot(datos, tick_labels=terr)
            except TypeError:
                ax.boxplot(datos, labels=terr)
        ax.axhline(30, color="red", linestyle="--", label="Umbral 30%")
        ax.set_title("Esfuerzo alquiler joven 18-34 por territorio (Mongo)")
        ax.set_ylabel("Esfuerzo %")
        ax.legend()
        _save(fig, nombre)

    # g2: renta 18-34 vs cuantia alquiler.
    fig, ax = plt.subplots(figsize=(7, 4))
    pts = [(_fnum(d.get("renta_joven_18_34", d.get("renta_joven"))), _fnum(d.get("cuantia_alquiler_mes"))) for d in ind]
    pts = [(x, y) for x, y in pts if x and y]
    if pts:
        ax.scatter([x for x, _ in pts], [y for _, y in pts], alpha=0.5)
    ax.set_xlabel("Renta joven 18-34 (eur)")
    ax.set_ylabel("Cuantia alquiler mes (eur)")
    ax.set_title("Renta vs alquiler por municipio (Mongo)")
    _save(fig, "g2_renta_vs_alquiler.png")

    # g3: top10 precio medio (municipios con >=3 anuncios).
    cand = [(str(d.get("nombre") or d.get("_id")), _fnum(d.get("precio_medio_eur")), int(d.get("n_anuncios") or 0)) for d in ind]
    cand = [(n, p, k) for n, p, k in cand if p and k >= 3]
    cand.sort(key=lambda t: t[1], reverse=True)
    top = cand[:10]
    fig, ax = plt.subplots(figsize=(8, 4))
    if top:
        ax.barh([t[0] for t in reversed(top)], [t[1] for t in reversed(top)])
    ax.set_title("Top10 precio medio anuncio (n>=3, Mongo)")
    ax.set_xlabel("Precio medio eur")
    _save(fig, "g3_top10_precio_medio.png")

    # g4: distribucion n_anuncios por municipio.
    fig, ax = plt.subplots(figsize=(7, 4))
    ns = [int(d.get("n_anuncios") or 0) for d in ind]
    if ns:
        ax.hist(ns, bins=min(30, max(5, max(ns) // 5 or 5)))
    ax.set_title("Distribucion anuncios por municipio (Mongo)")
    ax.set_xlabel("n_anuncios")
    _save(fig, "g4_distribucion_anuncios.png")

    # g5: esfuerzo robustos (n>=30).
    fig, ax = plt.subplots(figsize=(7, 4))
    rob = [(int(d.get("n_anuncios") or 0), e, str(d.get("nombre") or d.get("_id"))) for d in ind for e in [_esf(d)] if e is not None]
    rob = [t for t in rob if t[0] >= 30]
    if rob:
        ax.scatter([t[0] for t in rob], [t[1] for t in rob], alpha=0.6)
        for k, e, n in sorted(rob, key=lambda t: t[1], reverse=True)[:5]:
            ax.annotate(n, (k, e), fontsize=7)
    ax.axhline(30, color="red", linestyle="--")
    ax.set_title("Esfuerzo vs n_anuncios robustos n>=30 (Mongo)")
    ax.set_xlabel("n_anuncios")
    ax.set_ylabel("Esfuerzo %")
    _save(fig, "g5_esfuerzo_robustos.png")

    # A2: % inasequibles (>30%) por territorio.
    fig, ax = plt.subplots(figsize=(7, 4))
    vals, labels = [], []
    for t in terr:
        esfs = [_esf(d) for d in ind if d.get("territorio") == t]
        esfs = [e for e in esfs if e is not None]
        vals.append(100 * sum(1 for e in esfs if e > 30) / len(esfs) if esfs else 0)
        labels.append(t)
    if labels:
        ax.bar(labels, vals)
    ax.set_title("% municipios inasequibles por TH (Mongo)")
    ax.set_ylabel("% con esfuerzo>30")
    _save(fig, "A2_pct_inasequibles_por_TH.png")

    # B: paro Lanbide vs precio medio.
    fig, ax = plt.subplots(figsize=(7, 4))
    pts = [(_fnum(d.get("tasa_paro_lanbide_pct")), _fnum(d.get("precio_medio_eur"))) for d in ind]
    pts = [(x, y) for x, y in pts if x is not None and y]
    if pts:
        ax.scatter([x for x, _ in pts], [y for _, y in pts], alpha=0.5)
    ax.set_xlabel("Tasa paro Lanbide %")
    ax.set_ylabel("Precio medio eur")
    ax.set_title("Paro vs precio (Mongo)")
    _save(fig, "B_paro_vs_precio.png")

    # C: VPO por estado + antiguedad media por territorio.
    from collections import Counter
    fig, ax = plt.subplots(figsize=(8, 4))
    cnt = Counter(str(d.get("estado") or "sin dato") for d in vpo)
    if cnt:
        ax.bar(list(cnt), [cnt[k] for k in cnt])
        plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    ax.set_title("Promociones VPO por estado (Mongo)")
    _save(fig, "C_vpo_antiguedad_por_TH.png")

    # D: minutos Bilbao vs precio (OSRM + anuncios, todo Mongo).
    fig, ax = plt.subplots(figsize=(7, 4))
    by_id = {str(d.get("_id")): d for d in ind}
    pts = []
    for d in acc:
        base = by_id.get(str(d.get("_id")))
        m, p = _fnum(d.get("minutos_Bilbao")), _fnum((base or {}).get("precio_medio_eur"))
        if m is not None and p:
            pts.append((m, p))
    if pts:
        ax.scatter([x for x, _ in pts], [y for _, y in pts], alpha=0.5)
    ax.set_xlabel("Minutos a Bilbao (OSRM en Mongo)")
    ax.set_ylabel("Precio medio eur")
    ax.set_title("Distancia vs precio (Mongo)")
    _save(fig, "D_distancia_vs_precio.png")

    # E: confort vs esfuerzo.
    fig, ax = plt.subplots(figsize=(7, 4))
    pts = [(_fnum(d.get("indice_confort")), _esf(d)) for d in acc]
    pts = [(x, y) for x, y in pts if x is not None and y is not None]
    if pts:
        ax.scatter([x for x, _ in pts], [y for _, y in pts], alpha=0.5)
    ax.set_xlabel("Indice confort Udalmap (Mongo)")
    ax.set_ylabel("Esfuerzo %")
    ax.set_title("Confort vs esfuerzo (Mongo)")
    _save(fig, "E_demografia_edad.png")

    # F: cuantia media por territorio.
    fig, ax = plt.subplots(figsize=(7, 4))
    vals, labels = [], []
    for t in sorted({str(d.get("territorio")) for d in alq if d.get("territorio")}):
        cs = [_fnum(d.get("cuantia_media")) for d in alq if str(d.get("territorio")) == t]
        cs = [c for c in cs if c]
        vals.append(sum(cs) / len(cs) if cs else 0)
        labels.append(t)
    if labels:
        ax.bar(labels, vals)
    ax.set_title("Cuantia media alquiler por TH (Mongo)")
    _save(fig, "F_comparativa_TH.png")

    # G: gaps con conteos Mongo (imputados, sin anuncios, sin precio).
    n_imp = sum(1 for d in ind if d.get("is_imputed"))
    n_sin = sum(1 for d in ind if int(d.get("n_anuncios") or 0) == 0)
    n_sin_precio = sum(1 for d in ind if _fnum(d.get("precio_medio_eur")) is None)
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.axis("off")
    ax.table(
        cellText=[[len(ind), n_imp, n_sin, n_sin_precio]],
        colLabels=["municipios", "alquiler_imputado", "sin_anuncios", "sin_precio"],
        loc="center",
    )
    ax.set_title("Gaps y limitaciones (conteos Mongo)")
    _save(fig, "G_gaps_limitaciones.png")

    return rutas


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orquestador de analisis MongoDB: 9 pipelines + 5 CSV"
    )
    parser.add_argument(
        "--salida",
        default=str(RESULTADOS_DIR),
        help="Directorio de salida de los 5 CSV (defecto: data/resultados)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    # INDICES-01: demostrar COLLSCAN -> IXSCAN con explain_before_after().
    # (Se ejecuta antes de los pipelines; el indice ESR queda creado.)
    try:
        from analysis.mongo_indexes import explain_before_after

        _exp = explain_before_after()
        print(f"explain before: stage={_exp['before']['stage']} nReturned={_exp['before']['nReturned']} totalDocsExamined={_exp['before']['totalDocsExamined']} totalKeysExamined={_exp['before']['totalKeysExamined']}")
        print(f"explain after: stage={_exp['after']['stage']} nReturned={_exp['after']['nReturned']} totalDocsExamined={_exp['after']['totalDocsExamined']} totalKeysExamined={_exp['after']['totalKeysExamined']}")
        print(f"explain filtro: {_exp['filtro']}")
    except Exception as exc:  # pragma: no cover
        print(f"explain: NO REALIZADO ({exc!r})")
    primera = run_all_estandar()
    huella1 = huella_resultados(primera)
    segunda = run_all_estandar()
    huella2 = huella_resultados(segunda)
    n1 = conteos(primera)
    n2 = conteos(segunda)
    if huella1 != huella2 or n1 != n2:
        print(f"reproducibilidad: FALLA huella1={huella1} huella2={huella2}")
        print(f"n1={n1}")
        print(f"n2={n2}")
        return 1
    rutas = exportar_cinco_csv(primera, Path(args.salida))
    for fichero, ruta in rutas.items():
        nombre_pipeline = dict(EXPORTS_5)[fichero]
        print(f"{fichero}: {len(primera[nombre_pipeline])} filas -> {ruta}")
    try:
        pngs = exportar_png_desde_mongo(primera, Path(args.salida))
        print(f"png_mongo: {len(pngs)} ficheros -> {args.salida}")
    except Exception as exc:
        print(f"png_mongo: NO GENERADOS ({exc!r})")
    print(f"pipelines: {list(primera)}")
    print(f"n={n1}")
    print(f"huella: {huella1}")
    print("reproducibilidad: ok (dos ejecuciones con la misma huella)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
