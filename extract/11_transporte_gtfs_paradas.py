"""Descarga GTFS de operadores clave y cuenta paradas por municipio.

Fuentes (Moveuskadi / Open Data Euskadi):
  - Índice GTFS: https://opendata.euskadi.eus/transport/moveuskadi/data-index-gtfs.json
  - Feeds por operador (Metro Bilbao, Euskotren, RENFE Cercanías, Bizkaibus,
    Tuvisa, Dbus y los principales de Lurraldebus).

Genera:
  - data/raw/transporte_paradas_municipio.csv
  - data/raw/transporte_paradas_municipio.json

Uso:
  python extract/11_transporte_gtfs_paradas.py
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("transporte_gtfs_paradas")

# ─── Operadores clave seleccionados ────────────────────────────────────────────
# (nombre, slug, url)
OPERADORES: list[tuple[str, str, str]] = [
    ("Metro Bilbao", "metro_bilbao",
     "https://opendata.euskadi.eus/transport/moveuskadi/metro_bilbao/gtfs_metro_bilbao.zip"),
    ("Euskotren", "euskotren",
     "https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip"),
    ("RENFE Cercanías", "renfe_cercanias",
     "https://opendata.euskadi.eus/transport/moveuskadi/renfe_cercanias/gtfs_renfe_cercanias.zip"),
    ("Bizkaibus", "bizkaibus",
     "https://opendata.euskadi.eus/transport/moveuskadi/bizkaibus/gtfs_bizkaibus.zip"),
    ("Tuvisa", "tuvisa",
     "https://opendata.euskadi.eus/transport/moveuskadi/tuvisa/gtfs_tuvisa.zip"),
    ("Dbus", "dbus",
     "https://opendata.euskadi.eus/transport/moveuskadi/dbus/gtfs_dbus.zip"),
    # Lurraldebus (principales)
    ("Lurraldebus - Ekialdebus", "lurraldebus_ekialdebus",
     "https://opendata.euskadi.eus/transport/moveuskadi/lurraldebus/ekialdebus/gtfs_ekialdebus.zip"),
    ("Lurraldebus - Guipuzkoana", "lurraldebus_guipuzkoana",
     "https://opendata.euskadi.eus/transport/moveuskadi/lurraldebus/guipuzkoana/gtfs_guipuzkoana.zip"),
    ("Lurraldebus - Pesa", "lurraldebus_pesa",
     "https://opendata.euskadi.eus/transport/moveuskadi/lurraldebus/pesa/gtfs_pesa.zip"),
    ("Lurraldebus - TbH", "lurraldebus_tbh",
     "https://opendata.euskadi.eus/transport/moveuskadi/lurraldebus/tbh/gtfs_tbh.zip"),
    ("Lurraldebus - Euskotren bus", "lurraldebus_euskotren_bus",
     "https://opendata.euskadi.eus/transport/moveuskadi/lurraldebus/euskotren_bus/gtfs_euskotren_bus.zip"),
    ("Lurraldebus - Goierrialdea", "lurraldebus_goierrialdea",
     "https://opendata.euskadi.eus/transport/moveuskadi/lurraldebus/goierrialdea/gtfs_goierrialdea.zip"),
    ("Lurraldebus - Tolosaldea", "lurraldebus_tolosaldea",
     "https://opendata.euskadi.eus/transport/moveuskadi/lurraldebus/tolosaldea/gtfs_tolosaldea.zip"),
]

GTFS_DIR = RAW_DIR / "gtfs"
GEOJSON_PATH = RAW_DIR / "municipios_euskadi.geojson"


# ─── shapely (opcional) ───────────────────────────────────────────────────────
try:
    from shapely.geometry import Point, shape  # type: ignore

    HAS_SHAPELY = True
except Exception:  # noqa: BLE001
    Point = None  # type: ignore
    shape = None  # type: ignore
    HAS_SHAPELY = False


def _norm(text) -> str:
    if text is None:
        return ""
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return " ".join(s.split())


def _aliases(nombre: str) -> list[str]:
    out = set()
    for part in str(nombre).split("/"):
        part = part.strip()
        if part:
            out.add(_norm(part))
    out.add(_norm(nombre))
    # quitar vacíos
    return [a for a in out if a]


def cargar_municipios() -> list[dict]:
    raw = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
    fc = raw.get("datos", raw) if isinstance(raw, dict) else raw
    features = fc.get("features", []) if isinstance(fc, dict) else []

    vistos: set = set()
    municipios: list[dict] = []
    for f in features:
        props = f.get("properties", {}) or {}
        codigo = props.get("codigo_ine")
        if codigo in vistos:
            continue
        vistos.add(codigo)
        nombre_muni = props.get("nombre")
        m = {
            "codigo_ine": codigo,
            "nombre": nombre_muni,
            "territorio": props.get("territorio"),
            "geometry": f.get("geometry"),
            "aliases": _aliases(nombre_muni if nombre_muni is not None else ""),
        }
        if HAS_SHAPELY and m["geometry"]:
            try:
                m["geom"] = shape(m["geometry"])  # type: ignore[misc]
            except Exception:  # noqa: BLE001
                m["geom"] = None
        else:
            m["geom"] = None
        municipios.append(m)
    return municipios


def municipio_por_punto(lat: float, lon: float, municipios: list[dict]) -> dict | None:
    if not HAS_SHAPELY:
        return None
    pt = Point(lon, lat)  # type: ignore[misc]
    for m in municipios:
        geom = m.get("geom")
        if geom is not None and (geom.contains(pt) or geom.covers(pt)):
            return m
    return None


def municipio_por_nombre(stop_name: str, municipios: list[dict]) -> dict | None:
    ns = _norm(stop_name)
    if not ns:
        return None
    candidatos: list[dict] = []
    for m in municipios:
        for alias in m["aliases"]:
            if alias and (alias in ns or ns in alias):
                candidatos.append(m)
                break
    if not candidatos:
        return None
    if len(candidatos) == 1:
        return candidatos[0]
    # elegir el alias más largo (más específico)
    best = None
    best_len = 0
    for m in candidatos:
        for alias in m["aliases"]:
            if alias and (alias in ns or ns in alias) and len(alias) > best_len:
                best_len = len(alias)
                best = m
    return best


def extraer_stops(zip_path: Path) -> list[dict]:
    filas: list[dict] = []
    with zipfile.ZipFile(zip_path) as zf:
        stops_name = None
        for name in zf.namelist():
            if name.lower().endswith("stops.txt"):
                stops_name = name
                break
        if stops_name is None:
            raise FileNotFoundError("stops.txt no encontrado en el ZIP")
        with zf.open(stops_name) as fh:
            texto = io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")
            reader = csv.DictReader(texto)
            for row in reader:
                filas.append(row)
    return filas


def main() -> int:
    cliente = Cliente("transporte_gtfs", delay=0.5)
    GTFS_DIR.mkdir(parents=True, exist_ok=True)

    municipios = cargar_municipios()
    log.info(
        "Municipios cargados: %d | shapely=%s",
        len(municipios), HAS_SHAPELY,
    )

    # estado de agregación
    conteos: dict = {}
    for m in municipios:
        conteos[m["codigo_ine"]] = {
            "codigo_ine": m["codigo_ine"],
            "municipio": m["nombre"],
            "territorio": m["territorio"],
            "n_paradas": 0,
            "operadores": set(),
        }

    total_stops = 0
    total_asignadas = 0
    total_sin_asignar = 0
    resumen_ops: dict[str, dict] = {}

    for nombre_op, slug, url in OPERADORES:
        zip_dest = GTFS_DIR / f"{slug}.zip"
        try:
            cliente.descargar(url, zip_dest)
        except Exception as exc:  # noqa: BLE001
            log.error("Descarga fallida %s: %s", nombre_op, exc)
            resumen_ops[nombre_op] = {"error": str(exc), "stops": 0, "asignadas": 0}
            continue

        try:
            filas = extraer_stops(zip_dest)
        except Exception as exc:  # noqa: BLE001
            log.error("Error leyendo stops.txt %s: %s", nombre_op, exc)
            resumen_ops[nombre_op] = {"error": str(exc), "stops": 0, "asignadas": 0}
            continue

        n_ops = 0
        n_asig = 0
        for row in filas:
            lat_raw = (row.get("stop_lat") or "").strip()
            lon_raw = (row.get("stop_lon") or "").strip()
            if not lat_raw or not lon_raw:
                continue
            try:
                lat = float(lat_raw)
                lon = float(lon_raw)
            except ValueError:
                continue
            n_ops += 1
            total_stops += 1

            muni = None
            if HAS_SHAPELY:
                muni = municipio_por_punto(lat, lon, municipios)
            if muni is None:
                muni = municipio_por_nombre(row.get("stop_name", ""), municipios)

            if muni is None:
                total_sin_asignar += 1
                continue
            codigo = muni["codigo_ine"]
            if codigo not in conteos:
                continue
            conteos[codigo]["n_paradas"] += 1
            conteos[codigo]["operadores"].add(nombre_op)
            n_asig += 1
            total_asignadas += 1

        resumen_ops[nombre_op] = {
            "stops": n_ops,
            "asignadas": n_asig,
        }
        log.info(
            "%s: %d paradas leídas, %d asignadas", nombre_op, n_ops, n_asig,
        )

    # ─── salida ──────────────────────────────────────────────────────────────
    filas_salida = []
    for c in conteos.values():
        filas_salida.append(
            {
                "codigo_ine": c["codigo_ine"],
                "municipio": c["municipio"],
                "territorio": c["territorio"],
                "n_paradas": c["n_paradas"],
                "n_operadores": len(c["operadores"]),
                "operadores": "; ".join(sorted(c["operadores"])),
            }
        )

    # ordenar por n_paradas desc, luego nombre
    filas_salida.sort(key=lambda r: (-r["n_paradas"], str(r["municipio"])))

    csv_path = RAW_DIR / "transporte_paradas_municipio.csv"
    import pandas as pd  # noqa: E402

    df = pd.DataFrame(
        filas_salida,
        columns=[
            "codigo_ine", "municipio", "territorio", "n_paradas",
            "n_operadores", "operadores",
        ],
    )
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    log.info("CSV -> %s (%d municipios)", csv_path.name, len(df))

    metadata = {
        "fuente": "Moveuskadi / Open Data Euskadi (GTFS por operador)",
        "metodo_asignacion": "point-in-polygon (shapely)" if HAS_SHAPELY else "por nombre de stop",
        "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
        "n_operadores": len(OPERADORES),
        "n_municipios": len(filas_salida),
        "total_stops_leidos": total_stops,
        "total_stops_asignados": total_asignadas,
        "total_stops_sin_asignar": total_sin_asignar,
        "resumen_operadores": resumen_ops,
    }
    json_path = RAW_DIR / "transporte_paradas_municipio.json"
    guardar_json(json_path, filas_salida, metadata=metadata)
    log.info("JSON -> %s", json_path.name)

    log.info(
        "Resumen: %d stops leídos, %d asignados, %d sin asignar",
        total_stops, total_asignadas, total_sin_asignar,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
