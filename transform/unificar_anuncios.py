"""Unifica anuncios de Fotocasa, Pisos y RealtyAPI en esquema único para MongoDB."""
from __future__ import annotations
import json, os, glob as _glob, hashlib
import pandas as pd
from muni_resolve import resolver_codigo

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

REQUIRED_KEYS = ("precio_eur", "municipio")


def _property_fingerprint(rec):
    """Huella determinista de una propiedad (misma logica que generar_fingerprint)."""
    ubic = rec.get("ubicacion") or {}
    ci = ubic.get("codigo_ine")
    if ci is None:
        ci = ""
    sup = rec.get("superficie_m2")
    hab = rec.get("habitaciones")
    precio = rec.get("precio_eur")
    try:
        sup_r = round(float(sup) / 5) * 5 if sup is not None else 0
    except (ValueError, TypeError):
        sup_r = 0
    try:
        precio_r = round(float(precio) / 50) * 50 if precio is not None else 0
    except (ValueError, TypeError):
        precio_r = 0
    hab_r = hab if hab is not None else 0
    key = f"{ci}|{sup_r}|{hab_r}|{precio_r}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


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
    fc_recs = transform_fotocasa(fc)
    for r in fc_recs:
        r["_source_order"] = 0
    recs += fc_recs
    pis_recs = transform_pisos(pis)
    for r in pis_recs:
        r["_source_order"] = 1
    recs += pis_recs
    ra_recs = transform_realtyapi(ra)
    for r in ra_recs:
        r["_source_order"] = 2
    recs += ra_recs
    # Integrar lotes dirigidos (append-only) con schema guard
    import glob as _glob
    lot_specs = [
        ("anuncios_pisos_dirigido_*.json", transform_pisos, "pisos"),
        ("anuncios_fotocasa_dirigido_*.json", transform_fotocasa, "fotocasa"),
        ("anuncios_faltantes_fotocasa_*.json", transform_fotocasa, "fotocasa"),
        ("anuncios_faltantes_pisos_*.json", transform_pisos, "pisos"),
    ]
    lot_files = []
    for pattern, transform_fn, etiqueta in lot_specs:
        for path in _glob.glob(os.path.join(RAW, pattern)):
            lot_files.append((pattern, transform_fn, etiqueta, path))
    lot_files.sort(key=lambda x: os.path.basename(x[3]))
    for lot_idx, (pattern, transform_fn, etiqueta, path) in enumerate(lot_files):
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
        for r in nuevos:
            r["_source_order"] = 10 + lot_idx
        recs += nuevos
        print(f"Integrado lote {etiqueta}: {base} -> {len(datos)} registros, {len(nuevos)} transformados")
    # Calcular property_fingerprint para cada registro (consumo cross-portal)
    for r in recs:
        r["_fingerprint"] = _property_fingerprint(r)

    # Dedup determinista por portal + id_anuncio
    recs_sorted = sorted(recs, key=lambda r: (r.get("_source_order", 99), r.get("portal") or "", r.get("id_anuncio") or ""))
    seen = set()
    deduped = []
    duplicados = []
    for r in recs_sorted:
        key = (r.get("portal"), r.get("id_anuncio"))
        if key in seen:
            duplicados.append({"portal": r.get("portal"), "id_anuncio": r.get("id_anuncio"),
                             "source_order": r.get("_source_order"), "tipo": "portal_id"})
            continue
        seen.add(key)
        deduped.append(r)
    recs = deduped
    print(f"Anuncios tras dedup portal+id: {len(recs)} (eliminados: {len(duplicados)})")

    # Dedup cross-portal por property_fingerprint (marcar duplicados)
    recs_sorted_fp = sorted(recs, key=lambda r: (r.get("_source_order", 99), r.get("portal") or "", r.get("id_anuncio") or ""))
    seen_fp = set()
    deduped_fp = []
    duplicados_fp = []
    for r in recs_sorted_fp:
        fp = r.get("_fingerprint")
        if fp in seen_fp:
            duplicados_fp.append({"portal": r.get("portal"), "id_anuncio": r.get("id_anuncio"),
                                 "fingerprint": fp, "source_order": r.get("_source_order"), "tipo": "fingerprint"})
            continue
        seen_fp.add(fp)
        deduped_fp.append(r)
    recs = deduped_fp
    duplicados = duplicados + duplicados_fp
    print(f"Anuncios tras dedup fingerprint: {len(recs)} (eliminados cross-portal: {len(duplicados_fp)})")

    import json as _json
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "dedup_report.json"), "w", encoding="utf-8") as fh:
        _json.dump({"total": len(recs_sorted), "unicos": len(recs),
                    "eliminados": len(duplicados), "duplicados": duplicados}, fh,
                   ensure_ascii=False, indent=2)
    for r in recs:
        r["property_fingerprint"] = r.pop("_fingerprint", None)
        r.pop("_source_order", None)
    recs.sort(key=lambda r: (r.get("portal") or "", r.get("id_anuncio") or ""))
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
    # Cuarentena estricta Silver Maestro: integridad referencial + anomalías
    before_q = len(recs)
    dropped = {"codigo_ine_null": 0, "codigo_ine_no_dim": 0, "superficie_lt_10": 0, "pm2_gt_100": 0}
    dim_path = os.path.join(OUT, "dim_municipios.csv")
    if not os.path.exists(dim_path):
        dim_path = os.path.join(RAW, "dim_municipios.csv")
    _dim = pd.read_csv(dim_path, dtype=str, encoding="utf-8-sig")
    valid_codes = set(_dim["codigo_ine"].astype(str).str.strip().str.zfill(5))
    cleaned = []
    for r in recs:
        ci = r["ubicacion"].get("codigo_ine")
        if ci is None:
            dropped["codigo_ine_null"] += 1
            continue
        ci_norm = str(ci).strip()
        if ci_norm.isdigit():
            ci_norm = ci_norm.zfill(5)
        if ci_norm not in valid_codes:
            dropped["codigo_ine_no_dim"] += 1
            continue
        sup = r.get("superficie_m2")
        price = r.get("precio_eur")
        try:
            supf = float(sup) if sup is not None else None
        except (ValueError, TypeError):
            supf = None
        try:
            pf = float(price) if price is not None else None
        except (ValueError, TypeError):
            pf = None
        if supf is not None and supf < 10:
            dropped["superficie_lt_10"] += 1
            continue
        if supf is not None and supf > 0 and pf is not None and (pf / supf) > 100:
            dropped["pm2_gt_100"] += 1
            continue
        cleaned.append(r)
    recs = cleaned
    print("Anuncios antes de cuarentena:", before_q)
    print("Anuncios tras cuarentena:", len(recs))
    print("Descartados cuarentena:", before_q - len(recs), dropped)
    with open(os.path.join(OUT, "anuncios_unificados.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    _df = pd.DataFrame([{
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
        "property_fingerprint": r.get("property_fingerprint"),
    } for r in recs])
    _df["codigo_ine"] = _df["codigo_ine"].astype(str).str.strip().str.zfill(5)
    _df.to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False, encoding="utf-8-sig")
    print("Anuncios unificados:", len(recs))

if __name__ == "__main__":
    main()
