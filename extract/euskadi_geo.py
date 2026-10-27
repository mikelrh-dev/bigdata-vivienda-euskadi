"""Descarga y convierte la cartografia municipal de Euskadi a GeoJSON (EPSG:4326).

Genera:
  - data/raw/municipios_euskadi.geojson  (251+ poligonos, lat/lon)
  - data/raw/distancias_capitales.csv    (Haversine a las 3 capitales + comarca)
"""
from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json

log = get_logger("euskadi_geo")

SHP = RAW_DIR / "shp_euskadi" / "MUNICIPIOS_5000_ETRS89.shp"

CAPITALES = {
    "Bilbao": (43.2630, -2.9350),
    "Donostia": (43.3183, -1.9812),
    "Vitoria-Gasteiz": (42.8467, -2.6716),
}


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def main() -> int:
    import shapefile
    from pyproj import Transformer

    if not SHP.exists():
        log.error("Falta el SHP. Descarga MUNICIPIOS_5000_ETRS89.zip en data/raw/.")
        return 1

    transformer = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)

    sf = shapefile.Reader(str(SHP))
    field_names = [f[0] for f in sf.fields[1:]]

    shapes = sf.shapes()
    records = sf.records()

    features = []
    municipios = []

    for idx, shp in enumerate(shapes):
        rec = records[idx]
        attrs = dict(zip(field_names, rec))

        codigo_ine = str(attrs.get("EUSTAT", "")).strip().zfill(5)
        nombre = str(attrs.get("NOMBRE_TOP", "")).strip()
        territorio = str(attrs.get("TERRITORIO", "")).strip()
        comarca = str(attrs.get("COMARCA", "")).strip()

        geometry = None
        if shp.shapeType in (5, 15, 25):
            parts = shp.parts if shp.parts else [0]
            coords = []
            for pi in range(len(parts)):
                start = parts[pi]
                end = parts[pi + 1] if pi + 1 < len(parts) else len(shp.points)
                ring = []
                for pt in shp.points[start:end]:
                    lon, lat = transformer.transform(pt[0], pt[1])
                    ring.append([round(lon, 6), round(lat, 6)])
                if ring:
                    coords.append(ring)
            if len(coords) == 1:
                geometry = {"type": "Polygon", "coordinates": coords}
            elif len(coords) > 1:
                geometry = {"type": "MultiPolygon", "coordinates": [coords]}

        feature = {
            "type": "Feature",
            "properties": {
                "codigo_ine": codigo_ine,
                "nombre": nombre,
                "territorio": territorio,
                "comarca": comarca,
            },
            "geometry": geometry,
        }
        features.append(feature)

        cen_lat, cen_lon = None, None
        if geometry and geometry.get("coordinates"):
            pts = []
            if geometry["type"] == "Polygon":
                for ring in geometry["coordinates"]:
                    pts.extend(ring)
            else:
                for poly in geometry["coordinates"]:
                    for ring in poly:
                        pts.extend(ring)
            if pts:
                lons = [p[0] for p in pts]
                lats = [p[1] for p in pts]
                cen_lon = sum(lons) / len(lons)
                cen_lat = sum(lats) / len(lats)

        dists = {}
        if cen_lat is not None:
            for cap, (clat, clon) in CAPITALES.items():
                dists[cap] = round(_haversine(cen_lat, cen_lon, clat, clon), 2)
            capital_cercana = min(dists, key=lambda k: dists[k])
        else:
            capital_cercana = None

        municipios.append(
            {
                "codigo_ine": codigo_ine,
                "nombre": nombre,
                "territorio": territorio,
                "comarca": comarca,
                "centroide_lat": round(cen_lat, 6) if cen_lat else None,
                "centroide_lon": round(cen_lon, 6) if cen_lon else None,
                "dist_bilbao_km": dists.get("Bilbao"),
                "dist_donostia_km": dists.get("Donostia"),
                "dist_vitoria_km": dists.get("Vitoria-Gasteiz"),
                "capital_mas_cercana": capital_cercana,
            }
        )

    geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": features,
    }

    guardar_json(RAW_DIR / "municipios_euskadi.geojson", geojson, metadata={
        "fuente": "Open Data Euskadi (MUNICIPIOS_5000_ETRS89.shp)",
        "crs": "EPSG:4326 (WGS84)",
        "fecha_conversion": datetime.now().isoformat(timespec="seconds"),
        "n_municipios": len(features),
    })

    comarcas = {}
    for m in municipios:
        comarcas.setdefault(m["comarca"], []).append(m)
    comarca_centroid = {}
    for com, ms in comarcas.items():
        lats = [x["centroide_lat"] for x in ms if x["centroide_lat"]]
        lons = [x["centroide_lon"] for x in ms if x["centroide_lon"]]
        if lats:
            comarca_centroid[com] = (sum(lats) / len(lats), sum(lons) / len(lons))

    for m in municipios:
        cc = comarca_centroid.get(m["comarca"])
        if cc and m["centroide_lat"]:
            m["dist_centroide_comarca_km"] = round(_haversine(m["centroide_lat"], m["centroide_lon"], cc[0], cc[1]), 2)
        else:
            m["dist_centroide_comarca_km"] = None

    csv_path = RAW_DIR / "distancias_capitales.csv"
    columnas = ["codigo_ine", "nombre", "territorio", "comarca", "centroide_lat", "centroide_lon",
                "dist_bilbao_km", "dist_donostia_km", "dist_vitoria_km", "capital_mas_cercana",
                "dist_centroide_comarca_km"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(municipios)
    log.info("CSV -> %s (%d municipios)", csv_path.name, len(municipios))

    log.info("Municipios procesados: %d", len(municipios))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
