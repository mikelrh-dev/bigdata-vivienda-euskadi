"""F3: distancias Haversine 252x252 + capitales 252 + GeoJSON 252 (local, sin red).

1. distancias_capitales.csv 259 -> distancias_capitales_252.csv (filtro dim + dedup).
2. Matriz Haversine 252x252 desde centroides -> distancias_haversine_252.csv
   (origen_codigo, destino_codigo, km). Cubre Alava/Bizkaia sin B5M.
3. municipios_euskadi.geojson 259 features -> 252 (filtro dim), re-export UTF-8.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from _common import RAW_DIR, get_logger  # noqa: E402
log = get_logger("f3_dist")

def _hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlon/2)**2
    return round(2*R*math.asin(math.sqrt(a)), 2)

def main() -> int:
    import pandas as pd
    dim = pd.read_csv(RAW_DIR / "dim_municipios.csv", dtype=str)
    dim_cods = set(dim["codigo_ine"].str.zfill(5))

    # 1. capitales
    dc = pd.read_csv(RAW_DIR / "distancias_capitales.csv", dtype={"codigo_ine": str})
    dc["codigo_ine"] = dc["codigo_ine"].str.zfill(5)
    n_raw = len(dc)
    extras = sorted(set(dc["codigo_ine"]) - dim_cods)
    dc252 = dc[dc["codigo_ine"].isin(dim_cods)].drop_duplicates("codigo_ine", keep="first")
    dc252.to_csv(RAW_DIR / "distancias_capitales_252.csv", index=False, encoding="utf-8-sig")
    log.info("capitales: %d -> %d (extras fuera dim: %s)", n_raw, len(dc252), extras)

    # 2. haversine 252x252
    base = dc252.dropna(subset=["centroide_lat", "centroide_lon"])
    coords = {r.codigo_ine: (float(r.centroide_lat), float(r.centroide_lon)) for r in base.itertuples()}
    cods = sorted(dim_cods)
    faltan = [c for c in cods if c not in coords]
    filas = []
    for i, a in enumerate(cods):
        if a not in coords:
            continue
        for b in cods[i+1:]:
            if b not in coords:
                continue
            km = _hav(*coords[a], *coords[b])
            filas.append((a, b, km))
            filas.append((b, a, km))
        filas.append((a, a, 0.0))
    hav = pd.DataFrame(filas, columns=["origen_codigo", "destino_codigo", "km_haversine"])
    hav.to_csv(RAW_DIR / "distancias_haversine_252.csv", index=False, encoding="utf-8-sig")
    log.info("haversine: %d pares (%d municipios con centroide; sin centroide: %s)",
             len(hav), len(coords), faltan)

    # 3. geojson -> 252
    ruta_geo = RAW_DIR / "municipios_euskadi.geojson"
    data = json.loads(ruta_geo.read_text(encoding="utf-8"))
    fc = data.get("datos", data)
    feats = fc["features"]
    n_feat = len(feats)
    feats252 = [f for f in feats if str(f["properties"].get("codigo_ine")).zfill(5) in dim_cods]
    # dedup por codigo
    vistos, unicos = set(), []
    for f in feats252:
        c = str(f["properties"].get("codigo_ine")).zfill(5)
        if c not in vistos:
            vistos.add(c)
            unicos.append(f)
    fc["features"] = unicos
    out = {"metadata": {**(data.get("metadata", {})),
                        "f3_nota": "filtrado a 252 dim_municipios, UTF-8, EPSG:4326",
                        "n_municipios": len(unicos)},
           "datos": fc} if "datos" in data else fc
    ruta_geo.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    log.info("geojson: %d -> %d features", n_feat, len(unicos))
    assert len(unicos) == 252, f"geo debe quedar en 252, hay {len(unicos)}"
    assert len(dc252) == 252
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
