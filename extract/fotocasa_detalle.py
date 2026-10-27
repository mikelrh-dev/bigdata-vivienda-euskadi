"""V1: enriquece los 470 anuncios con la ficha de detalle (lento, sin proxy).

Por cada url_detalle descarga la ficha (1 peticion, delay 2s) y extrae:
  planta, antiguedad, orientacion, estado_conservacion, cert_energetico,
  descripcion_completa, fecha_publicacion, distrito/zona exactos,
  coordenadas exactas, n_imagenes.
Re-ejecutable: salta los ids ya presentes en anuncios_fotocasa_detalle.json.
Fusiona columnas planas en anuncios_fotocasa.csv/.json (aditivo).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402
log = get_logger("fotocasa_detalle")
JSON_RE = re.compile(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', re.S)

def _parse_detalle(html: str) -> dict | None:
    for m in JSON_RE.finditer(html):
        try:
            d = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if "realEstate" in d and isinstance(d["realEstate"], dict):
            return d["realEstate"]
    return None

def _extraer(re: dict) -> dict:
    feat = re.get("features") or {}
    addr = re.get("address") or {}
    coords = re.get("coordinates") or {}
    other = re.get("otherFeatures") or {}
    return {
        "planta": feat.get("floor"),
        "antiguedad_cod": feat.get("antiquity"),
        "orientacion_cod": feat.get("orientation"),
        "estado_conservacion_cod": feat.get("conservationState"),
        "cert_energetico": re.get("energyCertificate"),
        "superficie_detalle_m2": feat.get("surface"),
        "habitaciones_detalle": feat.get("rooms"),
        "banos_detalle": feat.get("bathrooms"),
        "descripcion_completa": (re.get("descriptions") or {}).get("es-ES"),
        "fecha_publicacion_detalle": ((re.get("date") or {}).get("timestamp")),
        "distrito_detalle": (addr.get("district") or "").strip() or None,
        "zona_detalle": (addr.get("cityZone") or addr.get("upperLevel") or "").strip() or None,
        "latitud_detalle": coords.get("latitude"),
        "longitud_detalle": coords.get("longitude"),
        "n_imagenes_detalle": len(re.get("multimedia") or []),
        "es_temporal_detalle": re.get("isTemporaryRental"),
        "extras_detalle": sorted(str(v) for v in other.values() if v),
    }

def main() -> int:
    base = json.loads((RAW_DIR / "anuncios_fotocasa.json").read_text(encoding="utf-8"))
    meta = base.get("metadata", {})
    anuncios = base.get("datos", base)
    det_path = RAW_DIR / "anuncios_fotocasa_detalle.json"
    detalle = json.loads(det_path.read_text(encoding="utf-8")).get("datos", []) if det_path.exists() else []
    hechos = {d["id_anuncio"] for d in detalle}
    pendientes = [a for a in anuncios if a.get("url_detalle") and a.get("id_anuncio") not in hechos]
    log.info("Detalle: %d hechos, %d pendientes de %d", len(hechos), len(pendientes), len(anuncios))
    cliente = Cliente("fotocasa_detalle", delay=2.0, reintentos=2)
    nuevos_ok, fallos = 0, 0
    for i, a in enumerate(pendientes, 1):
        try:
            html = cliente.get(a["url_detalle"]).text
            re_ = _parse_detalle(html)
            if not re_:
                fallos += 1
                continue
            d = {"id_anuncio": a["id_anuncio"], "codigo_ine": a.get("codigo_ine"),
                 "anio_fuente": 2026, **_extraer(re_)}
            detalle.append(d)
            nuevos_ok += 1
        except Exception as exc:  # noqa: BLE001
            fallos += 1
            log.warning("Fallo %s: %s", a.get("id_anuncio"), str(exc)[:100])
        if i % 50 == 0:
            log.info("Progreso %d/%d (ok=%d fallos=%d)", i, len(pendientes), nuevos_ok, fallos)
            guardar_json(det_path, detalle, metadata={"fuente": "Fotocasa fichas detalle",
                         "n_fichas": len(detalle)})
    guardar_json(det_path, detalle, metadata={"fuente": "Fotocasa fichas detalle (V1)",
                 "fecha": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                 "n_fichas": len(detalle), "fallos": fallos})
    # fusion plana aditiva en el json principal + csv
    idx = {d["id_anuncio"]: d for d in detalle}
    for a in anuncios:
        d = idx.get(a.get("id_anuncio"))
        if d:
            for k in ("planta", "cert_energetico", "distrito_detalle", "zona_detalle",
                      "latitud_detalle", "longitud_detalle", "es_temporal_detalle"):
                a.setdefault(k, d.get(k))
    guardar_json(RAW_DIR / "anuncios_fotocasa.json", anuncios,
                 metadata={**meta, "v1_detalle": f"{len(detalle)} fichas"})
    import csv
    df_cols = ["codigo_ine", "nombre_canonico", "anio_fuente", "id_anuncio", "precio_eur",
               "municipio", "provincia", "codigo_postal", "barrio", "distrito_detalle", "zona_detalle",
               "latitud_detalle", "longitud_detalle", "superficie_m2", "habitaciones", "banos",
               "planta", "cert_energetico", "alquiler_temporal", "es_temporal_detalle",
               "tipo_inmueble", "profesional", "publicado", "url_detalle"]
    with open(RAW_DIR / "anuncios_fotocasa.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=df_cols, extrasaction="ignore")
        w.writeheader(); w.writerows(anuncios)
    log.info("V1: %d fichas detalle, %d fallos. CSV+JSON fusionados.", len(detalle), fallos)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
