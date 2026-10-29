"""Enriquece conectividad GTFS: expediciones diarias, tren/metro, paradas por 1000 hab."""
from __future__ import annotations
import csv, json, os, zipfile, datetime

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")
GTFS_DIR = os.path.join(RAW, "gtfs")

def point_in_ring(lon, lat, ring):
    # ray casting
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def point_in_polygon(lon, lat, geom):
    gtype = geom["type"]
    coords = geom["coordinates"]
    if gtype == "Polygon":
        if not point_in_ring(lon, lat, coords[0]):
            return False
        for hole in coords[1:]:
            if point_in_ring(lon, lat, hole):
                return False
        return True
    if gtype == "MultiPolygon":
        for poly in coords:
            if point_in_polygon(lon, lat, {"type": "Polygon", "coordinates": poly}):
                return True
        return False
    return False

def load_geojson_municipios():
    g = json.load(open(os.path.join(RAW, "municipios_euskadi.geojson"), encoding="utf-8"))
    features = g["datos"]["features"]
    munis = []
    for f in features:
        munis.append({
            "codigo_ine": f["properties"]["codigo_ine"],
            "nombre": f["properties"]["nombre"],
            "geom": f["geometry"],
        })
    return munis

def stop_to_municipio(lon, lat, munis):
    for m in munis:
        if point_in_polygon(lon, lat, m["geom"]):
            return m["codigo_ine"]
    return None

def parse_date(s):
    return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:]))

def service_active_on(trip_id, calendar, calendar_dates, target_date):
    # calendar: dict trip_id -> list of (start, end, days bitmask)
    # calendar_dates: dict trip_id -> set of dates with exception_type
    # returns True if service runs on target_date
    # We'll precompute active service_ids for target_date
    pass

def main():
    os.makedirs(OUT, exist_ok=True)
    munis = load_geojson_municipios()
    # population from udalmap indicadores adicionales (poblacion_total)
    pop_map = {}
    try:
        import pandas as pd
        ud = pd.read_csv(os.path.join(RAW, "udalmap_indicadores_adicionales.csv"))
        for _, row in ud.iterrows():
            ci = str(row["codigo_ine"]).strip().zfill(5) if pd.notna(row["codigo_ine"]) else None
            if ci:
                pop_map[ci] = row.get("poblacion_total", None)
    except Exception:
        pass

    # day of reference: 2026-10-26 (Monday)
    ref_date = datetime.date(2026, 10, 26)
    ref_str = ref_date.strftime("%Y%m%d")

    # aggregate per municipio
    agg = {}  # codigo_ine -> {expediciones: set of trip_ids, n_paradas: int, operadores: set}
    for ci in [m["codigo_ine"] for m in munis]:
        agg[ci] = {"trips": set(), "n_paradas": 0, "operadores": set()}

    tren_operadores = {"metro_bilbao", "euskotren", "renfe_cercanias"}

    for zip_name in sorted(os.listdir(GTFS_DIR)):
        if not zip_name.endswith(".zip"):
            continue
        op_name = zip_name.replace(".zip", "")
        zpath = os.path.join(GTFS_DIR, zip_name)
        with zipfile.ZipFile(zpath) as z:
            # read stops
            stops = {}
            with z.open("stops.txt") as f:
                reader = csv.DictReader(f.read().decode("utf-8").splitlines())
                for row in reader:
                    try:
                        lat = float(row["stop_lat"])
                        lon = float(row["stop_lon"])
                    except (ValueError, KeyError):
                        continue
                    stops[row["stop_id"]] = (lon, lat)
            # map stops to municipio
            stop_muni = {}
            for sid, (lon, lat) in stops.items():
                ci = stop_to_municipio(lon, lat, munis)
                if ci:
                    stop_muni[sid] = ci
                    agg[ci]["n_paradas"] += 1
                    agg[ci]["operadores"].add(op_name)
            # read calendar and calendar_dates
            calendar = {}  # service_id -> (start, end, days)
            calendar_dates = {}  # service_id -> {date: exception_type}
            if "calendar.txt" in z.namelist():
                with z.open("calendar.txt") as f:
                    reader = csv.DictReader(f.read().decode("utf-8").splitlines())
                    for row in reader:
                        row = {k.strip(): v for k, v in row.items()}
                        sid = row["service_id"]
                        start = parse_date(row["start_date"])
                        end = parse_date(row["end_date"])
                        days = [int(row["monday"]), int(row["tuesday"]), int(row["wednesday"]),
                                int(row["thursday"]), int(row["friday"]), int(row["saturday"]), int(row["sunday"])]
                        calendar[sid] = (start, end, days)
            if "calendar_dates.txt" in z.namelist():
                with z.open("calendar_dates.txt") as f:
                    reader = csv.DictReader(f.read().decode("utf-8").splitlines())
                    for row in reader:
                        row = {k.strip(): v for k, v in row.items()}
                        sid = row["service_id"]
                        d = parse_date(row["date"])
                        et = int(row["exception_type"])
                        calendar_dates.setdefault(sid, {})[d] = et
            # determine active service_ids for ref_date
            active_services = set()
            for sid, (start, end, days) in calendar.items():
                if start <= ref_date <= end:
                    wd = ref_date.weekday()  # Monday=0
                    if days[wd] == 1:
                        active_services.add(sid)
            for sid, excs in calendar_dates.items():
                if ref_date in excs:
                    if excs[ref_date] == 1:
                        active_services.add(sid)
                    elif excs[ref_date] == 2:
                        active_services.discard(sid)
            # read trips
            trip_service = {}
            if "trips.txt" in z.namelist():
                with z.open("trips.txt") as f:
                    reader = csv.DictReader(f.read().decode("utf-8").splitlines())
                    for row in reader:
                        row = {k.strip(): v for k, v in row.items()}
                        trip_service[row["trip_id"]] = row["service_id"]
            # read stop_times and count trips per municipio
            if "stop_times.txt" in z.namelist():
                with z.open("stop_times.txt") as f:
                    reader = csv.DictReader(f.read().decode("utf-8").splitlines())
                    seen_trips = set()
                    for row in reader:
                        row = {k.strip(): v for k, v in row.items()}
                        tid = row["trip_id"]
                        sid = stop_muni.get(row["stop_id"])
                        if sid is None:
                            continue
                        svc = trip_service.get(tid)
                        if svc not in active_services:
                            continue
                        if tid not in seen_trips:
                            seen_trips.add(tid)
                            agg[sid]["trips"].add(tid)

    # build output
    rows = []
    for m in munis:
        ci = m["codigo_ine"]
        a = agg[ci]
        n_paradas = a["n_paradas"]
        exp = len(a["trips"])
        tiene_tren = any(op in tren_operadores for op in a["operadores"])
        pop = pop_map.get(ci)
        paradas_1000 = (n_paradas / (pop / 1000)) if (pop and pop > 0) else None
        rows.append({
            "codigo_ine": ci,
            "nombre": m["nombre"],
            "n_paradas": n_paradas,
            "expediciones_dia": exp,
            "tiene_tren_metro": tiene_tren,
            "operadores": ",".join(sorted(a["operadores"])),
            "paradas_por_1000_hab": round(paradas_1000, 2) if paradas_1000 is not None else None,
        })
    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "transporte_paradas_municipio_enriquecido.csv"), index=False)
    print("GTFS enriquecido:", len(df), "municipios")
    print("Municipios con expediciones>0:", (df["expediciones_dia"] > 0).sum())
    print("Municipios con tren/metro:", df["tiene_tren_metro"].sum())

if __name__ == "__main__":
    main()
