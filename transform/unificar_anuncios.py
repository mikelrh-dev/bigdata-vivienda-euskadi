"""Unifica anuncios de Fotocasa, Pisos y RealtyAPI en esquema único para MongoDB."""
from __future__ import annotations
import json, os, glob as _glob
import pandas as pd
from muni_resolve import resolver_codigo

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

REQUIRED_KEYS = ("precio_eur", "municipio")


def load_json(name):
    with open(os.path.join(RAW, name), encoding="utf-8") as f:
        payload = json.load(f)
    if isinstance(payload, dict) and "datos" in payload:
        return payload["datos"]
    return payload


def load_payload(name):
    with open(os.path.join(RAW, name), encoding="utf-8") as f:
        return json.load(f)


def _es_lote_valido(path, payload):
    """Schema guard para lotes dirigidos append-only."""
    if not isinstance(payload, dict):
        print("Schema guard: payload no es dict ->", path)
        return None
    datos = payload.get("datos")
    if not isinstance(datos, list):
        print("Schema guard: 'datos' no es lista ->", path)
        return None
    meta = payload.get("metadata", {})
    if "n_anuncios" in meta and meta["n_anuncios"] != len(datos):
        print(f"Schema guard: metadata.n_anuncios={meta['n_anuncios']} != len(datos)={len(datos)} ->", path)
    for it in datos[:5]:
        if not isinstance(it, dict):
            print("Schema guard: registro no-dict ->", path)
            return None
        if not any(k in it for k in ("precio_eur", "municipio", "municipio_busqueda")):
            print("Schema guard: claves básicas ausentes ->", path)
            return None
    return datos

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
        ci, canon = resolver_codigo(it.get("municipio"), it.get("codigo_ine"))
        if ci is None:
            continue
        recs.append({
            "id_anuncio": it.get("id_anuncio"),
            "portal": "fotocasa",
            "modalidad": modalidad(it, "fotocasa"),
            "precio_eur": it.get("precio_eur"),
            "superficie_m2": it.get("superficie_m2"),
            "habitaciones": it.get("habitaciones"),
            "banos": it.get("banos"),
            "titulo": it.get("titulo"),
            "subtitulo": it.get("subtitulo"),
            "ubicacion": {
                "codigo_ine": ci,
                "municipio": canon,
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
        ci, canon = resolver_codigo(it.get("municipio_busqueda") or it.get("nombre_canonico_resuelto"), it.get("codigo_ine"))
        if ci is None:
            continue
        recs.append({
            "id_anuncio": it.get("id_anuncio"),
            "portal": "pisos",
            "modalidad": modalidad(it, "pisos"),
            "precio_eur": it.get("precio_eur"),
            "superficie_m2": it.get("superficie_m2"),
            "habitaciones": it.get("habitaciones"),
            "banos": it.get("banos"),
            "titulo": it.get("titulo"),
            "subtitulo": it.get("subtitulo"),
            "ubicacion": {
                "codigo_ine": ci,
                "municipio": canon,
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
        ci, canon = resolver_codigo(it.get("municipio"), it.get("codigo_ine") if "codigo_ine" in it else None)
        if ci is None:
            continue
        recs.append({
            "id_anuncio": it.get("id_anuncio"),
            "portal": "realtyapi",
            "modalidad": modalidad(it, "realtyapi"),
            "precio_eur": it.get("precio_eur"),
            "superficie_m2": it.get("superficie_m2"),
            "habitaciones": it.get("habitaciones"),
            "banos": it.get("banos"),
            "titulo": it.get("titulo"),
            "subtitulo": it.get("subtitulo"),
            "ubicacion": {
                "codigo_ine": ci,
                "municipio": canon,
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
    fc = load_json("anuncios_fotocasa_enriquecido_geo.json")
    pis = load_json("anuncios_pisos_enriquecido_geo.json")
    ra = load_json("anuncios_realtyapi.json")
    recs = []
    recs += transform_fotocasa(fc)
    recs += transform_pisos(pis)
    recs += transform_realtyapi(ra)
    # Integrar lotes dirigidos (append-only) con schema guard
    import glob as _glob
    for pattern, transform_fn, etiqueta in [
        ("anuncios_pisos_dirigido_*.json", transform_pisos, "pisos"),
        ("anuncios_fotocasa_dirigido_*.json", transform_fotocasa, "fotocasa"),
        ("anuncios_faltantes_fotocasa_*.json", transform_fotocasa, "fotocasa"),
        ("anuncios_faltantes_pisos_*.json", transform_pisos, "pisos"),
    ]:
        for path in sorted(_glob.glob(os.path.join(RAW, pattern))):
            base = os.path.basename(path)
            try:
                payload = load_payload(base)
            except Exception as e:
                print(f"Aviso: no se pudo leer {base}: {e}")
                continue
            datos = _es_lote_valido(path, payload)
            if datos is None:
                print(f"Schema guard: lote saltado -> {base}")
                continue
            nuevos = transform_fn(datos)
            recs += nuevos
            print(f"Integrado lote {etiqueta}: {base} -> {len(datos)} registros, {len(nuevos)} transformados")
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
        # flag outlier de superficie (no se borra el valor)
        sup = r.get("superficie_m2")
        try:
            supf = float(sup) if sup is not None else None
        except (ValueError, TypeError):
            supf = None
        r["es_outlier_superficie"] = bool(supf is not None and (supf < 10 or supf > 500))
    with open(os.path.join(OUT, "anuncios_unificados.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    pd.DataFrame([{
        "id_anuncio": r["id_anuncio"],
        "portal": r["portal"],
        "modalidad": r["modalidad"],
        "precio_eur": r["precio_eur"],
        "superficie_m2": r["superficie_m2"],
        "habitaciones": r["habitaciones"],
        "es_outlier_superficie": r["es_outlier_superficie"],
        "codigo_ine": r["ubicacion"]["codigo_ine"],
        "municipio": r["ubicacion"]["municipio"],
        "titulo": r.get("titulo"),
        "subtitulo": r.get("subtitulo"),
        "equipamiento": ",".join(r["equipamiento"]),
    } for r in recs]).to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False)
    print("Anuncios unificados:", len(recs))

if __name__ == "__main__":
    main()
