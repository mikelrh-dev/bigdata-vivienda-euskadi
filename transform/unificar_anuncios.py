"""Unifica anuncios de Fotocasa, Pisos y RealtyAPI en esquema único para MongoDB."""
from __future__ import annotations
import json, os
import pandas as pd

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

def load_json(name):
    with open(os.path.join(RAW, name), encoding="utf-8") as f:
        return json.load(f)["datos"]

def equipamiento_fotocasa(item):
    eq = []
    for k in ["ascensor", "terraza", "parking", "trastero", "calefaccion"]:
        if item.get(k) is True or str(item.get(k)).lower() == "true":
            eq.append(k)
    return eq

def modalidad(item, portal):
    if portal == "fotocasa":
        if item.get("alquiler_temporal") is True or str(item.get("alquiler_temporal")).lower() == "true":
            return "temporal"
    ti = str(item.get("tipo_inmueble", "")).lower()
    if "habitacion" in ti or "habitación" in ti:
        return "habitacion"
    return "larga_estancia"

def transform_fotocasa(items):
    recs = []
    for it in items:
        lat = it.get("latitud")
        lon = it.get("longitud")
        coords = None
        if lat is not None and lon is not None:
            try:
                coords = {"type": "Point", "coordinates": [float(lon), float(lat)]}
            except (ValueError, TypeError):
                coords = None
        recs.append({
            "id_anuncio": it.get("id_anuncio"),
            "portal": "fotocasa",
            "modalidad": modalidad(it, "fotocasa"),
            "precio_eur": it.get("precio_eur"),
            "superficie_m2": it.get("superficie_m2"),
            "habitaciones": it.get("habitaciones"),
            "banos": it.get("banos"),
            "ubicacion": {
                "codigo_ine": it.get("codigo_ine"),
                "municipio": it.get("municipio"),
                "provincia": it.get("provincia"),
                "barrio": it.get("barrio"),
                "distrito": it.get("distrito"),
                "coordenadas": coords,
            },
            "equipamiento": equipamiento_fotocasa(it),
            "auditoria": {
                "es_outlier_iqr": None,
                "precio_m2_calc": None,
            },
            "geo_invalida": False,
        })
    return recs

def transform_pisos(items):
    recs = []
    for it in items:
        recs.append({
            "id_anuncio": it.get("id_anuncio"),
            "portal": "pisos",
            "modalidad": modalidad(it, "pisos"),
            "precio_eur": it.get("precio_eur"),
            "superficie_m2": it.get("superficie_m2"),
            "habitaciones": it.get("habitaciones"),
            "banos": it.get("banos"),
            "ubicacion": {
                "codigo_ine": it.get("codigo_ine"),
                "municipio": it.get("municipio_busqueda") or it.get("nombre_canonico_resuelto"),
                "provincia": None,
                "barrio": None,
                "distrito": None,
                "coordenadas": None,
            },
            "equipamiento": [],
            "auditoria": {
                "es_outlier_iqr": None,
                "precio_m2_calc": None,
            },
            "geo_invalida": True,
        })
    return recs

def transform_realtyapi(items):
    recs = []
    for it in items:
        lat = it.get("latitud")
        lon = it.get("longitud")
        coords = None
        if lat is not None and lon is not None:
            try:
                coords = {"type": "Point", "coordinates": [float(lon), float(lat)]}
            except (ValueError, TypeError):
                coords = None
        recs.append({
            "id_anuncio": it.get("id_anuncio"),
            "portal": "realtyapi",
            "modalidad": modalidad(it, "realtyapi"),
            "precio_eur": it.get("precio_eur"),
            "superficie_m2": it.get("superficie_m2"),
            "habitaciones": it.get("habitaciones"),
            "banos": it.get("banos"),
            "ubicacion": {
                "codigo_ine": it.get("codigo_ine") if "codigo_ine" in it else None,
                "municipio": it.get("municipio"),
                "provincia": it.get("provincia"),
                "barrio": it.get("barrio"),
                "distrito": it.get("distrito"),
                "coordenadas": coords,
            },
            "equipamiento": [],
            "auditoria": {
                "es_outlier_iqr": None,
                "precio_m2_calc": None,
            },
            "geo_invalida": False,
        })
    return recs

def main():
    os.makedirs(OUT, exist_ok=True)
    import glob as _glob
    fc = load_json("anuncios_fotocasa_enriquecido_geo.json")
    pis = load_json("anuncios_pisos_enriquecido_geo.json")
    ra = load_json("anuncios_realtyapi.json")
    recs = []
    recs += transform_fotocasa(fc)
    recs += transform_pisos(pis)
    recs += transform_realtyapi(ra)
    # Integrar lotes dirigidos (append-only) si existen
    for path in sorted(_glob.glob(os.path.join(RAW, "anuncios_pisos_dirigido_*.json"))):
        try:
            items = load_json(os.path.basename(path))
            recs += transform_pisos(items)
            print("Integrado lote dirigido:", os.path.basename(path), len(items))
        except Exception as e:
            print("Aviso: no se pudo integrar", path, e)
    # Deduplicar por portal + id_anuncio (mantener primero)
    seen = set()
    deduped = []
    for r in recs:
        key = (r.get("portal"), r.get("id_anuncio"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    recs = deduped
    print("Anuncios tras dedup:", len(recs))
    for r in recs:
        ci = r["ubicacion"].get("codigo_ine")
        if ci is not None:
            s = str(ci).strip()
            if s.isdigit():
                r["ubicacion"]["codigo_ine"] = s.zfill(5)
            else:
                r["ubicacion"]["codigo_ine"] = s if s else None
    with open(os.path.join(OUT, "anuncios_unificados.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    pd.DataFrame([{
        "id_anuncio": r["id_anuncio"],
        "portal": r["portal"],
        "modalidad": r["modalidad"],
        "precio_eur": r["precio_eur"],
        "superficie_m2": r["superficie_m2"],
        "codigo_ine": r["ubicacion"]["codigo_ine"],
        "municipio": r["ubicacion"]["municipio"],
        "equipamiento": ",".join(r["equipamiento"]),
    } for r in recs]).to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False)
    print("Anuncios unificados:", len(recs))

if __name__ == "__main__":
    main()
