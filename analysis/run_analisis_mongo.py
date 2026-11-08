"""Orquestador de analisis MongoDB: ejecuta los 11 pipelines y exporta 8 CSV.

Nivel 10 de Automatizacion del analisis (RETO 1Evaluacion SBD-BDAv2):
un script ejecuta todos los analisis principales y devuelve resultados
preparados para representacion, generados desde PyMongo sin valores
tecleados. Reutiliza los 11 pipelines de `mongo_aggregations` (con
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
    pipeline_habitaciones_por_municipio,
    pipeline_indicadores_municipio,
    pipeline_modalidades,
    pipeline_tier_por_municipio,
    pipeline_top_municipios_por_esfuerzo,
    pipeline_udalmap_extendido_osrm,
    pipeline_vpo_por_municipio,
    pipeline_vpo_terminadas,
)

RESULTADOS_DIR = ROOT / "data" / "resultados"

# Orden fijo de ejecucion de los 11 pipelines principales.
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
    "pipeline_tier_por_municipio",
    "pipeline_habitaciones_por_municipio",
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

# 6º CSV: VPO terminadas ‰ (indicador 5 non-legacy, INDICADORES-01).
# Euskadi Open Data 73 + población dim_municipios, campo común codigo_ine.
EXPORT_VPO_TERMINADAS: tuple[str, str] = (
    "mongo_vpo_terminadas_por_municipio.csv",
    "pipeline_vpo_terminadas",
)
# 7º CSV (CONCLUSION-02): tier A/B/C/D derivado solo de n_anuncios (252 filas).
EXPORT_TIER_CONFANZA: tuple[str, str] = (
    "mongo_tier_confianza.csv",
    "pipeline_tier_por_municipio",
)
# Los 5 canonicos + tier = 6 CSV canonicos de AGREGACION-01.
EXPORTS_6: tuple[tuple[str, str], ...] = EXPORTS_5 + (EXPORT_TIER_CONFANZA,)
# Compatibilidad: el 6º CSV historico era VPO terminadas; se mantiene como
# exportacion adicional (EXPORT_VPO_TERMINADAS) para no perder el indicador.
EXPORTS_7: tuple[tuple[str, str], ...] = EXPORTS_6 + (EXPORT_VPO_TERMINADAS,)
# 8º CSV (HAB-01): habitaciones por municipio (9 filas, pipeline nº 11).
EXPORT_HABITACIONES: tuple[str, str] = (
    "mongo_habitaciones_por_municipio.csv",
    "pipeline_habitaciones_por_municipio",
)
CSV_POR_PIPELINE: tuple[tuple[str, str], ...] = EXPORTS_7 + (EXPORT_HABITACIONES,)
EXPORTS_8: tuple[tuple[str, str], ...] = CSV_POR_PIPELINE


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


def exportar_seis_csv(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Escribe los 6 CSV canonicos (AGT-01): 5 + `mongo_tier_confianza.csv`.

    `EXPORTS_6` = `EXPORTS_5` + `EXPORT_TIER_CONFANZA`
    (`mongo_tier_confianza.csv` desde `pipeline_tier_por_municipio`,
    252 filas). `exportar_cinco_csv` se mantiene por compatibilidad (5).
    VPO terminadas se escribe con `exportar_vpo_terminadas_csv` (adicional,
    no cuenta en los 6 canonicos).
    """
    return exportar_csv(resultados, out_dir, EXPORTS_6)


def exportar_vpo_terminadas_csv(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Escribe el CSV adicional VPO terminadas (indicador 5 non-legacy)."""
    return exportar_csv(resultados, out_dir, (EXPORT_VPO_TERMINADAS,))


def exportar_habitaciones_csv(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Escribe `mongo_habitaciones_por_municipio.csv` (9 filas, pipeline nº 11)."""
    return exportar_csv(resultados, out_dir, (EXPORT_HABITACIONES,))


RANKEABLE_ESTADO = "rankeable"
N_INSUFICIENTE_ESTADO = "n_insuficiente"


def exportar_extras(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Capas M7 + paro M5 + ranking M3 (desde pipelines en memoria).

    - `capa_oficial.csv` (159): metodo_imputacion=oficial, is_imputed=false.
    - `capa_idw.csv` (93): metodo_imputacion=idw, is_imputed=true.
    - `capa_contexto.csv` (252): metodo_imputacion=contexto, is_imputed=true.
    - `udalmap_paro.csv` (252): metodo_imputacion=oficial/ninguno,
      is_imputed=false siempre (paro sin imputacion).
    - `ranking_esfuerzo.csv`: solo n_anuncios>=30 (M3 CONCLUSION-01); el
      resto es «n_insuficiente» y no ordena. Barakaldo (n=6) nunca ranking
      por encima de Donostia (n=126) ni de ningun Tier A.
    """
    destino = Path(out_dir)
    destino.mkdir(parents=True, exist_ok=True)
    ind = resultados.get("pipeline_indicadores_municipio", [])

    def _esf(d: dict[str, Any]) -> Any:
        v = d.get("esfuerzo_joven_pct_18_34")
        return v if v is not None else d.get("esfuerzo_joven_pct")

    def _metodo(d: dict[str, Any]) -> str | None:
        m = d.get("metodo_imputacion")
        if m is None:
            return None
        s = str(m)
        return "idw" if s.startswith("IDW") else s

    capa_oficial, capa_idw, capa_contexto, paro, ranking = [], [], [], [], []
    for d in ind:
        code = str(d.get("_id"))
        met = _metodo(d)
        if met == "oficial":
            capa_oficial.append({
                "codigo_ine": code, "municipio": d.get("nombre"),
                "territorio": d.get("territorio"),
                "cuantia_alquiler_mes": d.get("cuantia_alquiler_mes"),
                "renta_m2_alquiler": d.get("renta_m2_alquiler"),
                "metodo_imputacion": "oficial", "is_imputed": False,
            })
        elif met == "idw":
            capa_idw.append({
                "codigo_ine": code, "municipio": d.get("nombre"),
                "territorio": d.get("territorio"),
                "cuantia_alquiler_mes": d.get("cuantia_alquiler_mes"),
                "renta_m2_alquiler": d.get("renta_m2_alquiler"),
                "metodo_imputacion": "idw", "is_imputed": True,
            })
        capa_contexto.append({
            "codigo_ine": code, "municipio": d.get("nombre"),
            "territorio": d.get("territorio"),
            "renta_m2_contexto": d.get("renta_m2_alquiler"),
            "cuantia_contexto": d.get("cuantia_alquiler_mes"),
            "metodo_origen": met, "metodo_imputacion": "contexto",
            "is_imputed": True,
        })
        tasa = d.get("tasa_paro_lanbide_pct")
        paro.append({
            "codigo_ine": code, "municipio": d.get("nombre"),
            "territorio": d.get("territorio"), "tasa_paro_lanbide_pct": tasa,
            "metodo_imputacion": "oficial" if tasa is not None else "ninguno",
            "is_imputed": False,
        })

    cand = [(str(d.get("nombre") or d.get("_id")), str(d.get("_id")),
             d.get("territorio"), int(d.get("n_anuncios") or 0), _esf(d),
             d.get("esfuerzo_joven_pct_18_34"), d.get("esfuerzo_joven_pct_16_29"))
            for d in ind]
    cand = [c for c in cand if c[3] >= 30 and c[4] is not None]
    cand.sort(key=lambda t: float(t[4]), reverse=True)
    for nombre, code, terr, n, _e, e18, e16 in cand[:10]:
        ranking.append({
            "codigo_ine": code, "municipio": nombre, "territorio": terr,
            "n_anuncios": n, "esfuerzo_joven_pct_18_34": e18,
            "esfuerzo_joven_pct_16_29": e16, "estado": RANKEABLE_ESTADO,
        })

    rutas: dict[str, Path] = {}
    for fichero, filas in (("capa_oficial.csv", capa_oficial),
                           ("capa_idw.csv", capa_idw),
                           ("capa_contexto.csv", capa_contexto),
                           ("udalmap_paro.csv", paro),
                           ("ranking_esfuerzo.csv", ranking)):
        ruta = destino / fichero
        cabecera = _cabecera(filas)
        with ruta.open("w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=cabecera, extrasaction="ignore",
                                    lineterminator="\n")
            writer.writeheader()
            for fila in filas:
                writer.writerow({k: _csv_value(fila.get(k)) for k in cabecera})
        rutas[fichero] = ruta
    return rutas


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
    """Genera los 32 PNG desde PyMongo (sin DuckDB ni CSV).

    Fuente unica: los 11 pipelines en memoria (`resultados`). 13
    ficheros previos (12 figuras unicas A1,A2,B,C,D,E,F,G,g2,g3,g4,g5
    + g1 duplicado byte-identico de A1) + 19 nuevos (H1-H13, I,J,K,L,
    O,P) sin datos nuevos = 32 ficheros, 31 figuras unicas. Cada
    grafico deriva de campos ya agregados en Mongo; `_fnum` solo
    normaliza tipos BSON para matplotlib, sin valores tecleados.
    Sobrescribe los mismos nombres que generaba DuckDB para dejar atras
    esa dependencia. Si una serie esta vacia o falta un campo, se guarda
    una figura honesta con el motivo (nunca datos inventados).
    Devuelve dict fichero -> ruta.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    destino = Path(out_dir)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "anexo").mkdir(parents=True, exist_ok=True)
    rutas: dict[str, Path] = {}

    # Figuras relegadas a anexo (no evidencia principal): se siguen
    # generando para trazabilidad pero se escriben en data/resultados/anexo/.
    # No borrar: mover sin pérdida.
    ANEXO_PNG = frozenset({
        "g1_esfuerzo_por_territorio.png",  # duplica A1 byte-idéntica
        "H4_esfuerzo_18_34_vs_16_29.png",  # auditoría canónico vs legacy
        "G_gaps_limitaciones.png",  # tabla, no gráfico
        "I_modalidad_temporal_vs_larga.png",  # mezcla unidades; ver H8
        "H9_modalidades_larga_vs_temporal.png",  # duplicada; conservar H8
        "K_vpo_terminadas_vs_esfuerzo.png",  # duplica H5/H10
        "L_confort_accesibilidad_vs_esfuerzo.png",  # duplica H7
        "H12_vpo_promociones_estado_tipologia.png",  # duplica C_vpo_por_estado
    })

    def _save(fig, nombre: str) -> None:
        # PIL falla con EINVAL al abrir la ruta relativa en Windows; se guarda
        # en memoria y se escribe con la API de Python.
        ruta = (destino / "anexo" / nombre) if nombre in ANEXO_PNG else (destino / nombre)
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

    # ANEXO+g1: esfuerzo por Territorio Histórico (TH) (g1 duplica A1 byte-idéntica -> anexo/).
    for nombre in ("g1_esfuerzo_por_territorio.png", "A1_distribucion_esfuerzo_por_TH.png"):
        fig, ax = plt.subplots(figsize=(7, 4))
        datos = [[e for d in ind if d.get("territorio") == t and (e := _esf(d)) is not None] for t in terr]
        if any(datos):
            try:
                ax.boxplot(datos, tick_labels=terr)
            except TypeError:
                ax.boxplot(datos, labels=terr)
        ax.axhline(30, color="red", linestyle="--", label="Umbral 30%")
        ax.set_title("Esfuerzo alquiler joven 18-34 por Territorio Histórico (TH) (Mongo)")
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
    ax.set_title("% municipios inasequibles por Territorio Histórico (TH) (Mongo)")
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

    # C: VPO por estado (nombre histórico C_vpo_antiguedad_por_TH.png renombrado
    # a C_vpo_por_estado.png: el contenido real es Promociones VPO por estado,
    # no antigüedad por TH. Ver data/resultados/README.md.
    from collections import Counter
    fig, ax = plt.subplots(figsize=(8, 4))
    cnt = Counter(str(d.get("estado") or "sin dato") for d in vpo)
    if cnt:
        ax.bar(list(cnt), [cnt[k] for k in cnt])
        plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    ax.set_title("Promociones VPO por estado (Mongo)")
    _save(fig, "C_vpo_por_estado.png")

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

    # E: confort vs esfuerzo (nombre histórico E_demografia_edad.png
    # renombrado a E_confort_vs_esfuerzo.png: el contenido real es
    # confort vs esfuerzo, no demografía por edad).
    fig, ax = plt.subplots(figsize=(7, 4))
    pts = [(_fnum(d.get("indice_confort")), _esf(d)) for d in acc]
    pts = [(x, y) for x, y in pts if x is not None and y is not None]
    if pts:
        ax.scatter([x for x, _ in pts], [y for _, y in pts], alpha=0.5)
    ax.set_xlabel("Indice confort Udalmap (Mongo)")
    ax.set_ylabel("Esfuerzo %")
    ax.set_title("Confort vs esfuerzo (Mongo)")
    _save(fig, "E_confort_vs_esfuerzo.png")

    # F: cuantia media por Territorio Histórico (TH), €/mes (cuantía).
    fig, ax = plt.subplots(figsize=(7, 4))
    vals, labels = [], []
    for t in sorted({str(d.get("territorio")) for d in alq if d.get("territorio")}):
        cs = [_fnum(d.get("cuantia_media")) for d in alq if str(d.get("territorio")) == t]
        cs = [c for c in cs if c]
        vals.append(sum(cs) / len(cs) if cs else 0)
        labels.append(t)
    if labels:
        ax.bar(labels, vals)
    ax.set_title("Cuantia media alquiler por Territorio Histórico (TH) — €/mes (Mongo)")
    _save(fig, "F_comparativa_TH.png")

    # ANEXO: G gaps (tabla, no gráfico) — se escribe en anexo/.
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

    # ------------------------------------------------------------------
    # Nuevas figuras H1-H13, I,J,K,L, O,P (sin datos nuevos: solo lea
    # pipelines ya calculados en `resultados`). Si una serie esta vacia
    # o un campo falta, se guarda una figura honesta sin datos inventados.
    # ------------------------------------------------------------------
    mod = resultados.get("pipeline_modalidades", [])
    top = resultados.get("pipeline_top_municipios_por_esfuerzo", [])
    sexo = resultados.get("pipeline_esfuerzo_por_sexo", [])
    tier_rows = resultados.get("pipeline_tier_por_municipio", [])
    hab = resultados.get("pipeline_habitaciones_por_municipio", [])
    vpo_term = resultados.get("pipeline_vpo_terminadas", [])
    udal_osrm = resultados.get("pipeline_udalmap_extendido_osrm", [])

    def _honest(nombre: str, titulo: str, nota: str) -> None:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.axis("off")
        ax.set_title(titulo)
        ax.text(0.5, 0.5, nota, ha="center", va="center", fontsize=8,
                transform=ax.transAxes, wrap=True)
        _save(fig, nombre)
        print(f"{nombre}: SIN DATOS ({nota[:80]})")

    def _med_lista(vals: list[float]) -> tuple[float | None, float | None, float | None]:
        """Mediana + Q1/Q3 (interpolacion lineal, sin numpy)."""
        if not vals:
            return None, None, None
        s = sorted(vals)

        def _pct(p: float) -> float:
            if len(s) == 1:
                return s[0]
            pos = p * (len(s) - 1)
            lo = int(pos)
            hi = min(lo + 1, len(s) - 1)
            frac = pos - lo
            return s[lo] * (1 - frac) + s[hi] * frac

        return _pct(0.5), _pct(0.25), _pct(0.75)

    def _metodo_ind(d: dict[str, Any]) -> str | None:
        m = d.get("metodo_imputacion")
        if m is None:
            return None
        s = str(m)
        return "idw" if s.startswith("IDW") else s

    # H1: ranking esfuerzo 18-34 Tier A n>=30 (pipeline_top_municipios_por_esfuerzo).
    h1 = []
    for d in top:
        e = _fnum(d.get("esfuerzo_joven_pct_18_34"))
        if e is not None:
            h1.append((str(d.get("nombre") or d.get("_id")), e, int(d.get("n_anuncios") or 0)))
    h1.sort(key=lambda t: t[1])
    if h1:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh([r[0] for r in h1], [r[1] for r in h1], color="#0072B2")
        for i, (_n, _e, _k) in enumerate(h1):
            ax.text(_e, i, f" {_e:.1f}% (n={_k})", va="center", fontsize=7)
        ax.axvline(30, color="#D55E00", linestyle="--", label="Umbral 30%")
        ax.set_xlim(0, max(r[1] for r in h1) * 1.35)
        ax.set_xlabel("Esfuerzo alquiler joven 18-34 % (canonico)")
        ax.set_title("H1 Ranking esfuerzo 18-34 - Tier A n>=30 (Mongo)")
        ax.legend()
        _save(fig, "H1_ranking_esfuerzo_18_34.png")
    else:
        _honest("H1_ranking_esfuerzo_18_34.png",
                "H1 Ranking esfuerzo 18-34 (sin datos)",
                "pipeline_top_municipios_por_esfuerzo vacio")

    # H2: distribucion Tier A/B/C/D + lista Tier A/B con n.
    # Layout expandido (sin corte de barra D ni caja A/B truncada):
    # panel superior de barras con margen superior + panel inferior
    # con lista A/B; etiquetas unificadas a Territorio Histórico (TH).
    from collections import Counter as _Counter
    cnt_tier = _Counter(str(d.get("tier")) for d in tier_rows) if tier_rows else _Counter()
    ab = [(str(d.get("nombre") or d.get("_id")), int(d.get("n_anuncios") or 0), str(d.get("tier")))
          for d in tier_rows if str(d.get("tier")) in ("A", "B")]
    ab.sort(key=lambda t: -t[1])
    if cnt_tier:
        orden = ["A", "B", "C", "D"]
        presentes = [t for t in orden if t in cnt_tier]
        vals_h2 = [cnt_tier.get(t, 0) for t in presentes]
        import textwrap as _textwrap
        fig, (ax, ax_ab) = plt.subplots(2, 1, figsize=(10, 6.5), gridspec_kw={"height_ratios": [3, 1]})
        bares = ax.bar(presentes, vals_h2, color=["#0072B2", "#5BA3D0", "#999999", "#D55E00"])
        for i, t in enumerate(presentes):
            ax.text(i, vals_h2[i] + max(vals_h2) * 0.02, str(vals_h2[i]), ha="center", va="bottom", fontsize=10)
        ax.set_ylim(0, max(vals_h2) * 1.25)
        ax.set_xlabel("Tier de confianza (conteo de municipios)")
        ax.set_ylabel("Municipios")
        ax.set_title("H2 Tier confianza A/B/C/D + n (Mongo) — Municipios por Tier (252)")
        ax.grid(axis="y", alpha=0.3)
        ax_ab.axis("off")
        texto_ab = "; ".join(f"{n} ({ti}, n={k})" for n, k, ti in ab) or "sin Tier A/B"
        envuelto = _textwrap.fill(f"Tier A/B ({len(ab)}): {texto_ab}", width=140)
        ax_ab.set_title("Municipios Tier A/B con n_anuncios", fontsize=10)
        ax_ab.text(0.0, 0.55, envuelto, ha="left", va="center", fontsize=8, wrap=True,
                   bbox=dict(fc="white", ec="#CCCCCC", boxstyle="round,pad=0.4"))
        fig.suptitle("H2 Tier confianza A/B/C/D por Territorio Histórico (TH) — A4/B3/C57/D188", fontsize=11)
        _save(fig, "H2_tier_confianza_ABCD.png")
    else:
        _honest("H2_tier_confianza_ABCD.png", "H2 Tier (sin datos)",
                "pipeline_tier_por_municipio vacio")

    # H3: dumbbell esfuerzo por sexo (top 20 por brecha mujeres-hombres).
    h3 = []
    for d in sexo:
        fh, fm = _fnum(d.get("esfuerzo_alquiler_hombres_pct")), _fnum(d.get("esfuerzo_alquiler_mujeres_pct"))
        if fh is not None and fm is not None:
            h3.append((str(d.get("nombre") or d.get("_id")), fh, fm, fm - fh))
    h3.sort(key=lambda t: t[3], reverse=True)
    h3 = h3[:20][::-1]
    if h3:
        fig, ax = plt.subplots(figsize=(8, 5))
        for i, (n, fh, fm, brecha) in enumerate(h3):
            ax.plot([fh, fm], [i, i], color="#888888", linewidth=2)
            ax.scatter([fh], [i], color="#0072B2", zorder=3)
            ax.scatter([fm], [i], color="#D55E00", zorder=3)
            ax.text(fm, i, f" +{brecha:.1f}pp", va="center", fontsize=6)
        ax.set_yticks(range(len(h3)))
        ax.set_yticklabels([t[0] for t in h3], fontsize=7)
        ax.scatter([], [], color="#0072B2", label="Hombres")
        ax.scatter([], [], color="#D55E00", label="Mujeres")
        ax.set_xlabel("Esfuerzo alquiler %")
        ax.set_title("H3 Esfuerzo por sexo - top20 brecha (Mongo)")
        ax.legend()
        _save(fig, "H3_esfuerzo_por_sexo.png")
    else:
        _honest("H3_esfuerzo_por_sexo.png", "H3 Esfuerzo por sexo (sin datos)",
                "pipeline_esfuerzo_por_sexo vacio")

    # ANEXO: H4 auditoría canónico 18-34 vs legacy 16-29 (ver ANEXO_PNG).
    pts4 = []
    for d in ind:
        x, y = _fnum(d.get("esfuerzo_joven_pct_18_34")), _fnum(d.get("esfuerzo_joven_pct_16_29", d.get("esfuerzo_joven_pct")))
        if x is not None and y is not None:
            pts4.append((x, y))
    if pts4:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter([x for x, _ in pts4], [y for _, y in pts4], alpha=0.5)
        lo = min(min(x for x, _ in pts4), min(y for _, y in pts4))
        hi = max(max(x for x, _ in pts4), max(y for _, y in pts4))
        ax.plot([lo, hi], [lo, hi], color="#D55E00", linestyle="--", label="Igualdad")
        ax.set_xlabel("Esfuerzo 18-34 canonico %")
        ax.set_ylabel("Esfuerzo 16-29 legacy %")
        ax.set_title("H4 Esfuerzo 18-34 vs 16-29 (Mongo)")
        ax.legend()
        _save(fig, "H4_esfuerzo_18_34_vs_16_29.png")
    else:
        _honest("H4_esfuerzo_18_34_vs_16_29.png", "H4 Canonico vs legacy (sin datos)",
                "sin pares 18-34/16-29 en pipeline_indicadores_municipio")

    # H5: VPO terminadas por mil (Top15 + histograma, ceros anotados).
    vals5 = sorted([(_fnum(d.get("vpo_terminadas_por_mil")) or 0.0) for d in vpo_term])
    top5 = sorted(vpo_term, key=lambda d: _fnum(d.get("vpo_terminadas_por_mil")) or 0, reverse=True)[:15]
    n_ceros5 = sum(1 for v in vals5 if v == 0)
    if top5 and vals5:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        noms = [str(d.get("municipio") or d.get("codigo_ine")) for d in reversed(top5)]
        vls = [(_fnum(d.get("vpo_terminadas_por_mil")) or 0.0) for d in reversed(top5)]
        ax1.barh(noms, vls, color="#0072B2")
        ax1.set_xlabel("VPO terminadas por mil")
        ax1.set_title("Top15")
        ax2.hist(vals5, bins=min(30, max(5, len(vals5) // 10)))
        ax2.set_xlabel("VPO terminadas por mil")
        ax2.set_ylabel("Municipios")
        fig.suptitle(f"H5 VPO terminadas por mil (Mongo) - {n_ceros5} municipios en 0")
        _save(fig, "H5_vpo_terminadas_por_mil.png")
    else:
        _honest("H5_vpo_terminadas_por_mil.png", "H5 VPO terminadas (sin datos)",
                "pipeline_vpo_terminadas vacio")

    # H6: habitaciones mediana/min-max (9 filas, outlier anotado).
    h6 = []
    for d in hab:
        h6.append((str(d.get("municipio") or d.get("codigo_ine")),
                   _fnum(d.get("min_precio_eur")), _fnum(d.get("mediana_precio_eur")),
                   _fnum(d.get("max_precio_eur"))))
    h6 = [t for t in h6 if t[1] is not None and t[2] is not None and t[3] is not None]
    h6.sort(key=lambda t: t[2])
    max6 = max([t[3] for t in h6], default=0)
    if h6:
        fig, ax = plt.subplots(figsize=(8, 4))
        for i, (n, mn, md, mx) in enumerate(h6):
            ax.plot([mn, mx], [i, i], color="#999999", linewidth=2)
            ax.scatter([md], [i], color="#0072B2", zorder=3)
        ax.set_yticks(range(len(h6)))
        ax.set_yticklabels([t[0] for t in h6], fontsize=7)
        ax.set_xscale("log")
        ax.set_xlabel("EUR (escala log; punto = mediana, raya = min-max)")
        nota_out = f" outlier max {max6:,.0f} EUR" if max6 > 20000 else ""
        ax.set_title(f"H6 Habitaciones mediana/min-max (Mongo) -{nota_out}")
        _save(fig, "H6_habitaciones_mediana_rango.png")
    else:
        _honest("H6_habitaciones_mediana_rango.png", "H6 Habitaciones (sin datos)",
                "pipeline_habitaciones_por_municipio vacio")

    # H7: minutos OSRM a Bilbao/Vitoria vs esfuerzo 18-34.
    by_id_esf = {str(d.get("_id")): _esf(d) for d in ind}
    pts7b, pts7v = [], []
    for d in udal_osrm:
        code = str(d.get("_id"))
        e = by_id_esf.get(code)
        if e is None:
            continue
        osrm = d.get("osrm") or {}
        mb = _fnum(osrm.get("minutos_Bilbao"))
        mv = _fnum(osrm.get("minutos_Vitoria-Gasteiz", osrm.get("minutos_Vitoria")))
        if mb is not None:
            pts7b.append((mb, e))
        if mv is not None:
            pts7v.append((mv, e))
    if pts7b or pts7v:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        if pts7b:
            ax1.scatter([x for x, _ in pts7b], [y for _, y in pts7b], alpha=0.5)
        ax1.set_xlabel("Minutos a Bilbao (OSRM)")
        ax1.set_ylabel("Esfuerzo 18-34 %")
        ax1.set_title("Bilbao")
        if pts7v:
            ax2.scatter([x for x, _ in pts7v], [y for _, y in pts7v], alpha=0.5)
        ax2.set_xlabel("Minutos a Vitoria-Gasteiz (OSRM)")
        ax2.set_title("Vitoria-Gasteiz")
        fig.suptitle("H7 Accesibilidad (OSRM) vs esfuerzo (Mongo)")
        _save(fig, "H7_accesibilidad_tiempo_capital.png")
    else:
        _honest("H7_accesibilidad_tiempo_capital.png", "H7 Accesibilidad (sin datos)",
                "sin minutos OSRM o sin esfuerzo en udalmap_osrm")

    # H8: mediana temporal vs larga solo Tier A/B.
    tier_ab = [d for d in tier_rows if str(d.get("tier")) in ("A", "B")]
    if tier_ab:
        noms = [str(d.get("nombre") or d.get("codigo_ine")) for d in tier_ab]
        mt = [_fnum(d.get("mediana_precio_temporal")) or 0 for d in tier_ab]
        ml = [_fnum(d.get("mediana_precio_larga")) or 0 for d in tier_ab]
        import numpy as _np
        x = _np.arange(len(noms))
        w = 0.35
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.bar(x - w / 2, mt, w, label="Temporal")
        ax.bar(x + w / 2, ml, w, label="Larga estancia")
        ax.set_xticks(x)
        ax.set_xticklabels(noms, rotation=20, ha="right")
        ax.set_ylabel("Mediana precio €/mes")
        ax.set_title("H8 Mediana temporal vs larga - Tier A/B (Mongo)")
        ax.legend()
        _save(fig, "H8_tier_mediana_temporal_vs_larga.png")
    else:
        _honest("H8_tier_mediana_temporal_vs_larga.png", "H8 Tier mediana (sin datos)",
                "sin Tier A/B en pipeline_tier_por_municipio")

    # ANEXO: H9 modalidades larga vs temporal (duplicada; conservar H8).
    modc = {str(d.get("modalidad")): (int(d.get("n") or 0), _fnum(d.get("precio_medio"))) for d in mod}
    if modc:
        keys = list(modc)
        ns = [modc[k][0] for k in keys]
        pm = [modc[k][1] or 0 for k in keys]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        ax1.pie(ns, labels=[f"{k}\n{v} EUR" for k, v in zip(keys, pm)], autopct="%1.0f%%")
        ax2.bar(keys, pm, color=["#0072B2", "#D55E00"][:len(keys)])
        ax2.set_ylabel("Precio medio EUR")
        fig.suptitle("H9 Modalidades larga vs temporal (Mongo)")
        _save(fig, "H9_modalidades_larga_vs_temporal.png")
    else:
        _honest("H9_modalidades_larga_vs_temporal.png", "H9 Modalidades (sin datos)",
                "pipeline_modalidades vacio")

    # H10: tension (etxebide por mil) vs esfuerzo 18-34, color categoria.
    pts10 = []
    for d in ind:
        x, y = _fnum(d.get("etxebide_solicitudes_por_mil")), _esf(d)
        if x is not None and y is not None:
            pts10.append((x, y, str(d.get("tension_categoria") or "sin dato")))
    if pts10:
        fig, ax = plt.subplots(figsize=(7, 4))
        for cat, col in (("alta", "#D55E00"), ("media", "#E69F00"), ("baja", "#0072B2")):
            xs = [x for x, _, c in pts10 if c == cat]
            ys = [y for _, y, c in pts10 if c == cat]
            if xs:
                ax.scatter(xs, ys, label=cat, alpha=0.5, color=col)
        ax.set_xlabel("Etxebide solicitudes por mil")
        ax.set_ylabel("Esfuerzo 18-34 %")
        ax.set_title("H10 Tension etxebide vs esfuerzo (Mongo)")
        ax.legend()
        _save(fig, "H10_tension_vs_esfuerzo.png")
    else:
        _honest("H10_tension_vs_esfuerzo.png", "H10 Tension vs esfuerzo (sin datos)",
                "sin tension/etxebide en pipeline_indicadores_municipio")

    # H11: imputacion oficial vs IDW apiladas por TH.
    por_th = {}
    for d in ind:
        t = str(d.get("territorio") or "sin dato")
        m = _metodo_ind(d)
        por_th.setdefault(t, {"oficial": 0, "idw": 0, "resto": 0})
        if m == "oficial":
            por_th[t]["oficial"] += 1
        elif m == "idw":
            por_th[t]["idw"] += 1
        else:
            por_th[t]["resto"] += 1
    if por_th:
        ths = sorted(por_th)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(ths, [por_th[t]["oficial"] for t in ths], label="oficial")
        ax.bar(ths, [por_th[t]["idw"] for t in ths], bottom=[por_th[t]["oficial"] for t in ths], label="IDW")
        ax.set_ylabel("Municipios")
        ax.set_title("H11 Imputacion oficial vs IDW por Territorio Histórico (TH) (Mongo)")
        ax.legend()
        _save(fig, "H11_imputacion_oficial_idw_por_TH.png")
    else:
        _honest("H11_imputacion_oficial_idw_por_TH.png", "H11 Imputacion (sin datos)",
                "pipeline_indicadores_municipio vacio")

    # ANEXO: H12 VPO promociones estado/tipología (duplica C_vpo_por_estado).
    cnt_est = _Counter(str(d.get("estado") or "sin dato") for d in vpo) if vpo else _Counter()
    cnt_tip = _Counter(str(d.get("tipologia") or "sin dato") for d in vpo) if vpo else _Counter()
    if cnt_est:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        ax1.bar(list(cnt_est), list(cnt_est.values()))
        ax1.set_title("Por estado")
        top_tip = cnt_tip.most_common(10)
        ax2.bar([k for k, _ in top_tip], [v for _, v in top_tip])
        ax2.set_title("Tipologia (top10)")
        plt.setp(ax2.get_xticklabels(), rotation=30, ha="right")
        fig.suptitle("H12 VPO promociones estado/tipologia (Mongo) - viviendas sin dato (null)")
        _save(fig, "H12_vpo_promociones_estado_tipologia.png")
    else:
        _honest("H12_vpo_promociones_estado_tipologia.png", "H12 VPO (sin datos)",
                "pipeline_vpo_por_municipio vacio")

    # H13: histograma mediana precio m2 winsorizada p1-99.
    vals13 = [_fnum(d.get("mediana_precio_m2_winsorizada")) for d in ind]
    vals13 = [v for v in vals13 if v is not None]
    if vals13:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(vals13, bins=min(30, max(5, len(vals13) // 5)))
        ax.set_xlabel("Mediana precio EUR/m2 winsorizada p1-99")
        ax.set_ylabel("Municipios")
        ax.set_title(f"H13 Mediana precio m2 winsorizada (Mongo, n={len(vals13)})")
        _save(fig, "H13_mediana_precio_m2_winsorizada.png")
    else:
        _honest("H13_mediana_precio_m2_winsorizada.png", "H13 Winsorizada (sin datos)",
                "sin mediana_precio_m2_winsorizada en indicadores")

    # ANEXO: I precio por modalidad (mezcla unidades; ver H8; €/mes vs €/m2).
    # Los pipelines no exponen EUR/m2 por modalidad (solo mediana global
    # winsorizada): el titulo lo declara honestamente.
    I_medianas, I_quartiles = {}, {}
    for mod_name in ("larga_estancia", "temporal"):
        campo = "mediana_precio_larga" if mod_name == "larga_estancia" else "mediana_precio_temporal"
        vals = [_fnum(d.get(campo)) for d in tier_ab]
        vals = [v for v in vals if v is not None]
        I_medianas[mod_name] = _med_lista(vals)
    if modc and any(v[0] is not None for v in I_medianas.values()):
        etiquetas = ["larga_estancia", "temporal"]
        fig, ax = plt.subplots(figsize=(8, 4))
        x = list(range(len(etiquetas)))
        medias = [(modc.get(m, (0, 0))[1] or 0) for m in etiquetas]
        ax.bar(x, medias, label="Precio medio (anuncios)", color="#0072B2")
        for i, m in enumerate(etiquetas):
            med, q1, q3 = I_medianas.get(m, (None, None, None))
            if med is not None:
                ax.scatter([i], [med], color="#D55E00", zorder=5, marker="D",
                           label="Mediana municipal Tier A/B" if i == 0 else None)
                if q1 is not None and q3 is not None:
                    ax.plot([i, i], [q1, q3], color="#D55E00", linewidth=2)
        ax.set_xticks(x)
        ax.set_xticklabels(etiquetas)
        ax.set_ylabel("EUR")
        ax.set_title("I Modalidad temporal vs larga (Mongo) - EUR/m2 por modalidad no disponible en pipelines")
        ax.legend()
        _save(fig, "I_modalidad_temporal_vs_larga.png")
    else:
        _honest("I_modalidad_temporal_vs_larga.png", "I Modalidad (sin datos)",
                "sin modalidades o sin medianas Tier A/B")

    # J: n_anuncios vs mediana temporal/larga, color tier (solo Tier A/B).
    ptsJ_t, ptsJ_l = [], []
    for d in tier_ab:
        n = int(d.get("n_anuncios") or 0)
        t = str(d.get("tier"))
        mt2, ml2 = _fnum(d.get("mediana_precio_temporal")), _fnum(d.get("mediana_precio_larga"))
        if mt2 is not None:
            ptsJ_t.append((n, mt2, t))
        if ml2 is not None:
            ptsJ_l.append((n, ml2, t))
    if ptsJ_t or ptsJ_l:
        fig, ax = plt.subplots(figsize=(7, 4))
        for _n, _m, _t in ptsJ_t:
            ax.scatter(_n, _m, marker="o", color="#0072B2" if _t == "A" else "#5BA3D0",
                       label="Temporal " + _t if _t in ("A", "B") else None)
        for _n, _m, _t in ptsJ_l:
            ax.scatter(_n, _m, marker="s", color="#D55E00" if _t == "A" else "#E69F00",
                       label="Larga " + _t if _t in ("A", "B") else None)
        ax.set_xscale("log")
        ax.set_xlabel("n_anuncios (log, Tier A/B)")
        ax.set_ylabel("Mediana precio €/mes")
        ax.set_title("J Tier confianza vs precio (Mongo, solo Tier A/B con precio municipal)")
        ax.legend()
        _save(fig, "J_tier_confianza_vs_precio.png")
    else:
        _honest("J_tier_confianza_vs_precio.png", "J Tier vs precio (sin datos)",
                "sin Tier A/B con mediana en tier")

    # ANEXO: K VPO terminadas ‰ vs esfuerzo (duplica H5/H10).
    ptsK = []
    for d in vpo_term:
        code = str(d.get("codigo_ine"))
        e = by_id_esf.get(code)
        v = _fnum(d.get("vpo_terminadas_por_mil"))
        if e is not None and v is not None:
            ptsK.append((v, e))
    if ptsK:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter([x for x, _ in ptsK], [y for _, y in ptsK], alpha=0.5)
        ax.set_xlabel("VPO terminadas por mil")
        ax.set_ylabel("Esfuerzo 18-34 %")
        ax.set_title("K VPO terminadas vs esfuerzo (Mongo)")
        _save(fig, "K_vpo_terminadas_vs_esfuerzo.png")
    else:
        _honest("K_vpo_terminadas_vs_esfuerzo.png", "K VPO vs esfuerzo (sin datos)",
                "sin join vpo_terminadas-esfuerzo")

    # ANEXO: L confort + minutos vs esfuerzo (duplica H7).
    ptsL1, ptsL2 = [], []
    for d in acc:
        e = _esf(d)
        if e is None:
            continue
        c = _fnum(d.get("indice_confort"))
        if c is not None:
            ptsL1.append((c, e))
        t = _fnum(d.get("tiempo_acceso_capital_th", d.get("minutos_Bilbao")))
        if t is not None:
            ptsL2.append((t, e))
    if ptsL1 or ptsL2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        if ptsL1:
            ax1.scatter([x for x, _ in ptsL1], [y for _, y in ptsL1], alpha=0.5)
            ax1.set_xlabel("Indice confort")
            ax1.set_ylabel("Esfuerzo %")
            ax1.set_title("Confort")
        if ptsL2:
            ax2.scatter([x for x, _ in ptsL2], [y for _, y in ptsL2], alpha=0.5)
            ax2.set_xlabel("Minutos a capital (Udalmap/OSRM)")
            ax2.set_title("Minutos a capital")
        fig.suptitle("L Confort + accesibilidad vs esfuerzo (Mongo)")
        _save(fig, "L_confort_accesibilidad_vs_esfuerzo.png")
    else:
        _honest("L_confort_accesibilidad_vs_esfuerzo.png", "L Confort vs esfuerzo (sin datos)",
                "sin confort/tiempo a capital en accesibilidad")

    # O: ranking bloqueado n>=30 (IC bootstrap si existe el CSV; resto gris).
    ic_map: dict[str, tuple[float, float]] = {}
    try:
        ruta_boot = destino / "bootstrap_robustos.csv"
        if ruta_boot.exists():
            import csv as _csv
            with ruta_boot.open(newline="", encoding="utf-8-sig") as fh:
                for fila in _csv.DictReader(fh):
                    nom = str(fila.get("municipio") or "")
                    try:
                        lo = float(fila.get("ic95_inf"))
                        hi = float(fila.get("ic95_sup"))
                    except (TypeError, ValueError):
                        continue
                    ic_map[nom] = (lo, hi)
    except Exception as exc:
        print(f"O bootstrap: no leido ({exc!r})")
    o_rank = [(str(d.get("nombre") or d.get("_id")), _fnum(d.get("esfuerzo_joven_pct_18_34")),
               int(d.get("n_anuncios") or 0)) for d in top]
    o_rank = [t for t in o_rank if t[1] is not None]
    o_gris = [(_fnum(d.get("esfuerzo_joven_pct_18_34")), int(d.get("n_anuncios") or 0))
              for d in ind if int(d.get("n_anuncios") or 0) < 30]
    o_gris = [(e, n) for e, n in o_gris if e is not None]
    if o_rank:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [1, 1.4]})
        rr = list(reversed(o_rank))
        ax1.barh([t[0] for t in rr], [t[1] for t in rr], color="#0072B2")
        for i, (n, e, k) in enumerate(rr):
            ic = ic_map.get(n)
            if ic is not None:
                ax1.errorbar(e, i, xerr=[[e - ic[0]], [ic[1] - e]], fmt="none", color="black", capsize=3)
        ax1.axvline(30, color="#D55E00", linestyle="--")
        ax1.set_xlabel("Esfuerzo 18-34 %")
        ax1.set_title(f"Rankeables n>=30 ({len(o_rank)})" + (" + IC95 bootstrap" if ic_map else " - IC pendiente"))
        if o_gris:
            ax2.scatter([n for _, n in o_gris], [e for e, _ in o_gris], color="#999999", alpha=0.4, s=10)
        ax2.set_xlabel("n_anuncios (<30, n_insuficiente)")
        ax2.set_ylabel("Esfuerzo 18-34 %")
        ax2.set_title(f"Resto gris n_insuficiente ({len(o_gris)})")
        fig.suptitle("O Ranking bloqueado n>=30 (Mongo)")
        _save(fig, "O_ranking_bloqueado_n30.png")
    else:
        _honest("O_ranking_bloqueado_n30.png", "O Ranking bloqueado (sin datos)",
                "pipeline_top_municipios_por_esfuerzo vacio")

    # P: cuantia mediana oficial vs anuncios por TH (con n y cobertura).
    import statistics as _statistics
    p_of, p_an = {}, {}
    for d in ind:
        t = str(d.get("territorio") or "sin dato")
        if _metodo_ind(d) == "oficial":
            c = _fnum(d.get("cuantia_alquiler_mes"))
            if c is not None:
                p_of.setdefault(t, []).append(c)
        pm = _fnum(d.get("precio_medio_eur"))
        if pm is not None:
            p_an.setdefault(t, []).append(pm)
    thsP = sorted(set(p_of) | set(p_an))
    if thsP:
        fig, ax = plt.subplots(figsize=(8, 4))
        x = list(range(len(thsP)))
        med_of = [_statistics.median(p_of[t]) if p_of.get(t) else 0 for t in thsP]
        med_an = [_statistics.median(p_an[t]) if p_an.get(t) else 0 for t in thsP]
        w = 0.35
        ax.bar([i - w / 2 for i in x], med_of, w, label="Cuantia oficial €/mes (mediana)")
        ax.bar([i + w / 2 for i in x], med_an, w, label="Anuncios precio medio €/mes (mediana)")
        for i, t in enumerate(thsP):
            ax.text(i, max(med_of[i], med_an[i]) * 1.02,
                    f"n_of={len(p_of.get(t, []))} n_an={len(p_an.get(t, []))}",
                    ha="center", fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels(thsP)
        ax.set_ylabel("€/mes")
        ax.set_title("P Cuantia oficial vs anuncios por Territorio Histórico (TH) — €/mes (Mongo, n y cobertura)")
        ax.legend()
        _save(fig, "P_oficial_vs_anuncios_por_TH.png")
    else:
        _honest("P_oficial_vs_anuncios_por_TH.png", "P Oficial vs anuncios (sin datos)",
                "sin cuantia oficial o sin precio medio en indicadores")

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
    rutas = exportar_seis_csv(primera, Path(args.salida))
    for fichero, ruta in rutas.items():
        nombre_pipeline = dict(EXPORTS_6)[fichero]
        print(f"{fichero}: {len(primera[nombre_pipeline])} filas -> {ruta}")
    try:
        rutas_vpo = exportar_vpo_terminadas_csv(primera, Path(args.salida))
        for fichero, ruta in rutas_vpo.items():
            print(f"{fichero}: {len(primera['pipeline_vpo_terminadas'])} filas -> {ruta}")
    except Exception as exc:
        print(f"vpo_terminadas: NO GENERADO ({exc!r})")
    try:
        rutas_hab = exportar_habitaciones_csv(primera, Path(args.salida))
        for fichero, ruta in rutas_hab.items():
            print(f"{fichero}: {len(primera['pipeline_habitaciones_por_municipio'])} filas -> {ruta}")
    except Exception as exc:
        print(f"habitaciones: NO GENERADO ({exc!r})")
    try:
        pngs = exportar_png_desde_mongo(primera, Path(args.salida))
        print(f"png_mongo: {len(pngs)} ficheros -> {args.salida}")
    except Exception as exc:
        print(f"png_mongo: NO GENERADOS ({exc!r})")
    try:
        extras = exportar_extras(primera, Path(args.salida))
        for fichero, ruta in extras.items():
            print(f"{fichero}: {sum(1 for _ in open(ruta, encoding='utf-8-sig')) - 1} filas -> {ruta}")
    except Exception as exc:
        print(f"extras: NO GENERADOS ({exc!r})")
    print(f"pipelines: {list(primera)}")
    print(f"n={n1}")
    print(f"huella: {huella1}")
    print("reproducibilidad: ok (dos ejecuciones con la misma huella)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
