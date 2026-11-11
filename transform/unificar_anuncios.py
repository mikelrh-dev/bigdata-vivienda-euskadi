"""Unifica anuncios de Fotocasa, Pisos y RealtyAPI en esquema único para MongoDB."""
from __future__ import annotations
import json, os, sys, glob as _glob, hashlib
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import PROCESADO_DIR, RAW_DIR  # noqa: E402
from muni_resolve import resolver_codigo, resolver_pisos_por_texto

RAW = str(RAW_DIR)
OUT = str(PROCESADO_DIR)

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


def _habitaciones_int(v):
    """M1 OUTLIER-01: habitaciones a entero (2,5 -> 2); None si no numerico."""
    try:
        return int(float(v)) if v is not None and str(v).strip() not in ("", "nan", "None") else None
    except (ValueError, TypeError):
        return None


def deduplicar_fingerprint(recs):
    """M6 DEDUP-01: dedup dura cross-portal por property_fingerprint.

    El primer anuncio de cada huella (orden determinista por
    _source_order/portal/id_anuncio) conserva; el resto se descarta con
    motivo `duplicado_fingerprint`. Devuelve (conservados, descartados).
    """
    recs_sorted = sorted(recs, key=lambda r: (r.get("_source_order", 99), r.get("portal") or "", r.get("id_anuncio") or ""))
    seen = set()
    conservados = []
    descartados = []
    for r in recs_sorted:
        fp = r.get("_fingerprint")
        if fp in seen:
            descartados.append({"portal": r.get("portal"), "id_anuncio": r.get("id_anuncio"),
                                "fingerprint": fp, "source_order": r.get("_source_order"), "tipo": "fingerprint"})
            continue
        seen.add(fp)
        conservados.append(r)
    return conservados, descartados


def load_json(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
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

def equipamiento_realtyapi(item):
    # RealtyAPI trae exterior (bool) + descripcion ES/EN; el equipamiento
    # silver se deriva de ahi (exterior/balcon/interior/parking/planta_baja).
    eq = set()
    if item.get("exterior") is True:
        eq.add("exterior")
    desc = str(item.get("descripcion") or "").lower()
    if "balcon" in desc or "balcony" in desc:
        eq.add("balcon")
    if "interior" in desc:
        eq.add("interior")
    if "parking" in desc or "garage" in desc:
        eq.add("parking")
    planta = str(item.get("planta") or "").strip().lower()
    if planta in ("bj", "0", "baja", "pb"):
        eq.add("planta_baja")
    if str(item.get("tipo_inmueble") or "").lower() == "duplex":
        eq.add("duplex")
    return sorted(eq)

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
            "historico_precios": [],
            "auditoria": {
                "es_outlier_iqr": None,
                "precio_m2_calc": None,
            },
            "geo_invalida": False,
        })
    return recs

def transform_pisos(items):
    # PISOS-01/EXTRACCION-01: subtitulo/titulo manda; el campo de busqueda NUNCA
    # como ubicacion. Fuera de Euskadi / sin texto -> geo_invalida=True +
    # cuarentena reversible (excluido de dim_municipios y conteos L1/L2).
    recs = []
    for it in items:
        ci, canon, origen, motivo = resolver_pisos_por_texto(
            it.get("subtitulo"), it.get("titulo"), it.get("codigo_ine"))
        es_cuarentena = ci is None
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
            "origen_resolucion": origen,
            "motivo_cuarentena": motivo if es_cuarentena else None,
            "es_busqueda_no_ubicacion": True,
            "ubicacion": {
                "codigo_ine": ci,
                "municipio": canon,
                "provincia": None,
                "barrio": None,
                "distrito": None,
                "coordenadas": None,
            },
            "equipamiento": [],
            "historico_precios": [],
            "auditoria": {
                "es_outlier_iqr": None,
                "precio_m2_calc": None,
            },
            "geo_invalida": True if es_cuarentena else False,
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
            "equipamiento": equipamiento_realtyapi(it),
            "historico_precios": [],
            "auditoria": {
                "es_outlier_iqr": None,
                "precio_m2_calc": None,
            },
            "geo_invalida": False,
        })
    return recs

def main():
    os.makedirs(OUT, exist_ok=True)
    fc = load_json("anuncios_fotocasa_enriquecido.json")
    pis = load_json("anuncios_pisos_enriquecido.json")
    ra = load_json("anuncios_realtyapi_enriquecido.json")
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

    # Dedup cross-portal por property_fingerprint (M6 DEDUP-01, dura):
    # el primero de cada huella conserva; resto -> duplicado_fingerprint.
    recs, duplicados_fp = deduplicar_fingerprint(recs)
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
    # Cuarentena estricta Silver Maestro + cuarentena reversible pisos.
    # PISOS-02: pisos fuera de Euskadi / sin texto -> geo_invalida=True y
    # cuarentena_pisos.csv (reversible, excluido de n_anuncios y L1/L2).
    before_q = len(recs)
    dropped = {"codigo_ine_null": 0, "codigo_ine_no_dim": 0, "superficie_lt_10": 0, "pm2_gt_100": 0}
    dim_path = os.path.join(OUT, "dim_municipios.csv")
    _dim = pd.read_csv(dim_path, dtype=str, encoding="utf-8-sig")
    valid_codes = set(_dim["codigo_ine"].astype(str).str.strip().str.zfill(5))
    cleaned = []
    cuarentena = []
    for r in recs:
        ci = r["ubicacion"].get("codigo_ine")
        if ci is None:
            dropped["codigo_ine_null"] += 1
            if r.get("portal") == "pisos":
                r["geo_invalida"] = True
                cuarentena.append(r)
            continue
        ci_norm = str(ci).strip()
        if ci_norm.isdigit():
            ci_norm = ci_norm.zfill(5)
        if ci_norm not in valid_codes:
            dropped["codigo_ine_no_dim"] += 1
            if r.get("portal") == "pisos":
                r["geo_invalida"] = True
                r["motivo_cuarentena"] = r.get("motivo_cuarentena") or "fuera_de_euskadi"
                cuarentena.append(r)
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
    # Cuarentena reversible pisos: nunca se borra el anuncio.
    if cuarentena:
        _qdf = pd.DataFrame([{
            "id_anuncio": r["id_anuncio"],
            "portal": r["portal"],
            "titulo": r.get("titulo"),
            "subtitulo": r.get("subtitulo"),
            "origen_resolucion": r.get("origen_resolucion"),
            "motivo_cuarentena": r.get("motivo_cuarentena"),
            "geo_invalida": r.get("geo_invalida"),
            "precio_eur": r.get("precio_eur"),
            "superficie_m2": r.get("superficie_m2"),
            "es_busqueda_no_ubicacion": r.get("es_busqueda_no_ubicacion"),
        } for r in cuarentena])
        _qdf.to_csv(os.path.join(OUT, "cuarentena_pisos.csv"), index=False, encoding="utf-8-sig")
        with open(os.path.join(OUT, "cuarentena_pisos.json"), "w", encoding="utf-8") as _qf:
            json.dump(cuarentena, _qf, ensure_ascii=False, indent=2)
    else:
        _qdf = pd.DataFrame()
        try:
            if os.path.exists(os.path.join(OUT, "cuarentena_pisos.csv")):
                os.remove(os.path.join(OUT, "cuarentena_pisos.csv"))
            if os.path.exists(os.path.join(OUT, "cuarentena_pisos.json")):
                os.remove(os.path.join(OUT, "cuarentena_pisos.json"))
        except OSError:
            pass
    print("Cuarentena pisos (reversible):", len(cuarentena))
    # M1 OUTLIER-01: habitaciones siempre entera en la salida (2,5 -> 2).
    # OJO: se castea DESPUES del fingerprint/dedup para no alterar huellas.
    for r in recs:
        r["habitaciones"] = _habitaciones_int(r.get("habitaciones"))
    # A1: precio_m2 + flag IQR (advisory, no borra). Rellena `auditoria`.
    for r in recs:
        try:
            pf = float(r.get("precio_eur")) if r.get("precio_eur") is not None else None
        except (ValueError, TypeError):
            pf = None
        try:
            sf = float(r.get("superficie_m2")) if r.get("superficie_m2") is not None else None
        except (ValueError, TypeError):
            sf = None
        r["auditoria"]["precio_m2_calc"] = round(pf / sf, 2) if (pf and sf and sf > 0) else None
        r["auditoria"]["es_outlier_iqr"] = False
        if pf is None:
            r["auditoria"]["motivo_precio_nulo"] = ("geo_aproximada" if r.get("geo_invalida")
                                                      else "origen_sin_precio")
    _pm2 = pd.Series([r["auditoria"]["precio_m2_calc"] for r in recs
                       if r["auditoria"]["precio_m2_calc"] is not None], dtype=float)
    if len(_pm2) >= 4:
        _q1, _q3 = float(_pm2.quantile(0.25)), float(_pm2.quantile(0.75))
        _iqr = _q3 - _q1
        _lo, _hi = round(_q1 - 1.5 * _iqr, 2), round(_q3 + 1.5 * _iqr, 2)
        for r in recs:
            v = r["auditoria"]["precio_m2_calc"]
            if v is not None:
                r["auditoria"]["es_outlier_iqr"] = bool(v < _lo or v > _hi)
        print(f"IQR precio_m2: Q1={_q1:.2f} Q3={_q3:.2f} bounds=[{_lo}, {_hi}] "
              f"flags={sum(1 for r in recs if r['auditoria']['es_outlier_iqr'])}")
    else:
        print("IQR precio_m2: muestra insuficiente, sin flags")
    # M1 OUTLIER-01: anotaciones canonical propagadas sin reintroducir fuera
    # de rango (no se borra el anuncio; precio_m2 valido vive en Mongo).
    for r in recs:
        pm2 = r["auditoria"]["precio_m2_calc"]
        sup = r.get("superficie_m2")
        try:
            supf = float(sup) if sup is not None else None
        except (ValueError, TypeError):
            supf = None
        pm2_fuera = bool(pm2 is not None and (pm2 < 3 or pm2 > 50))
        sup_fuera = bool(supf is not None and (supf < 10 or supf > 500))
        iqr_ex = bool(r["auditoria"]["es_outlier_iqr"] and not pm2_fuera)
        r["precio_m2_fuera_3_50"] = pm2_fuera
        r["superficie_fuera_10_500"] = sup_fuera
        r["iqr_excluido"] = iqr_ex
        mot = []
        if pm2_fuera:
            mot.append("precio_m2_fuera_3_50")
        if sup_fuera:
            mot.append("superficie_fuera_10_500")
        if iqr_ex:
            mot.append("iqr_excluido")
        r["motivo_exclusion"] = ";".join(mot) if mot else ""
    print(f"excluidos_precio_m2={sum(1 for r in recs if r['precio_m2_fuera_3_50'])}, "
          f"excluidos_superficie={sum(1 for r in recs if r['superficie_fuera_10_500'])}, "
          f"excluidos_iqr_precio_medio={sum(1 for r in recs if r['iqr_excluido'])}, "
          "habitaciones_int=100%")
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
        "precio_m2_calc": r["auditoria"]["precio_m2_calc"],
        "es_outlier_iqr": r["auditoria"]["es_outlier_iqr"],
        "codigo_ine": r["ubicacion"]["codigo_ine"],
        "municipio": r["ubicacion"]["municipio"],
        "titulo": r.get("titulo"),
        "subtitulo": r.get("subtitulo"),
        "origen_resolucion": r.get("origen_resolucion"),
        "geo_invalida": r.get("geo_invalida"),
        "equipamiento": ",".join(r["equipamiento"]),
        "property_fingerprint": r.get("property_fingerprint"),
        "motivo_exclusion": r.get("motivo_exclusion", ""),
        "precio_m2_fuera_3_50": r.get("precio_m2_fuera_3_50", False),
        "superficie_fuera_10_500": r.get("superficie_fuera_10_500", False),
        "iqr_excluido": r.get("iqr_excluido", False),
    } for r in recs])
    _df["codigo_ine"] = _df["codigo_ine"].astype(str).str.strip().str.zfill(5)
    _df.to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False, encoding="utf-8-sig")
    print("Anuncios unificados:", len(recs))

if __name__ == "__main__":
    main()
