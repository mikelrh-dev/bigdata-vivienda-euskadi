# Extrae correspondencia municipio -> area funcional desde GeoEuskadi.
# Descarga shapefile de areas funcionales, lee geojson de municipios,
# calcula centroide de cada municipio y asigna area funcional por point-in-polygon.
# Salida: data/raw/areas_funcionales_municipios.csv (nueva fuente raw).

import json
import os
import urllib.request
import zipfile
from pathlib import Path

import shapefile
from pyproj import Transformer

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
TMP = Path(os.environ.get("TMPDIR", "/tmp")) / "geo_areas"
TMP.mkdir(parents=True, exist_ok=True)

URL = "https://www.geo.euskadi.eus/cartografia/DatosDescarga/Limites/AREAS_FUNCIONALES_5000_ETRS89.zip"
ZIP_PATH = TMP / "areas.zip"
EXTRACT_DIR = TMP

if not ZIP_PATH.exists():
    urllib.request.urlretrieve(URL, ZIP_PATH)

with zipfile.ZipFile(ZIP_PATH) as z:
    z.extractall(EXTRACT_DIR)

SHP = EXTRACT_DIR / "AREAS_FUNCIONALES_5000_ETRS89"


def point_in_polygon(px, py, poly):
    """Ray casting. poly = list of (x,y)."""
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def shape_to_polygons(shp_rec):
    """Convierte un shape de pyshp a lista de poligonos (cada uno lista de (x,y))."""
    polys = []
    if shp_rec.shapeType == shapefile.POLYGON or shp_rec.shapeType == shapefile.POLYGONZ:
        # parts
        parts = list(shp_rec.parts) + [len(shp_rec.points)]
        for i in range(len(parts) - 1):
            ring = shp_rec.points[parts[i]:parts[i + 1]]
            polys.append(ring)
    return polys


# Leer areas funcionales
reader = shapefile.Reader(str(SHP))
areas = []
for rec, shp in zip(reader.records(), reader.shapes()):
    name = rec["A_FUNC_CAS"]
    code = rec["COD_AFUNC"]
    polys = shape_to_polygons(shp)
    areas.append({"name": name, "code": code, "polys": polys})

# Leer municipios geojson
geo = json.load(open(RAW / "municipios_euskadi.geojson", encoding="utf-8"))
features = geo["datos"]["features"]

rows = []
for feat in features:
    props = feat["properties"]
    code_ine = props["codigo_ine"]
    nombre = props["nombre"]
    geom = feat["geometry"]
    # calcular centroide (promedio de todos los puntos)
    coords = []
    if geom["type"] == "Polygon":
        for ring in geom["coordinates"]:
            coords.extend(ring)
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            for ring in poly:
                coords.extend(ring)
    if not coords:
        continue
    cx = sum(c[0] for c in coords) / len(coords)
    cy = sum(c[1] for c in coords) / len(coords)
    # convertir lon/lat (WGS84) a UTM 30 ETRS89 (metros)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
    cx_utm, cy_utm = transformer.transform(cx, cy)

    # asignar area funcional
    assigned = None
    for area in areas:
        for poly in area["polys"]:
            if point_in_polygon(cx_utm, cy_utm, poly):
                assigned = area
                break
        if assigned:
            break
    # fallback manual para municipios no asignados (exclaves/frontera)
    overrides = {
        "01022": ("RIOJA ALAVESA", 10),
        "01028": ("RIOJA ALAVESA", 10),
        "01033": ("RIOJA ALAVESA", 10),
        "48051": ("ENCARTACIONES", 2),
    }
    if assigned is None and code_ine in overrides:
        name, c = overrides[code_ine]
        assigned = {"name": name, "code": c}

    rows.append({
        "codigo_ine": str(code_ine).zfill(5),
        "nombre": nombre,
        "area_funcional": assigned["name"] if assigned else None,
        "cod_area_funcional": assigned["code"] if assigned else None,
    })

import csv
dest = RAW / "areas_funcionales_municipios.csv"
with open(dest, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["codigo_ine", "nombre", "area_funcional", "cod_area_funcional"])
    w.writeheader()
    w.writerows(rows)

print("Generado " + str(dest) + ": " + str(len(rows)) + " filas")
# resumen
from collections import Counter
print(Counter(r["area_funcional"] for r in rows))
unassigned = [r for r in rows if r["area_funcional"] is None]
print("sin asignar:", len(unassigned))
if unassigned:
    print(unassigned[:5])
