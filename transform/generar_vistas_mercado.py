"""Genera vistas analíticas segregadas a partir del dataset unificado.

No modifica data/raw/. Produce:
- data/procesado/anuncios_vivienda_residencial.csv  (modalidad != temporal)
- data/procesado/anuncios_habitaciones_unificados.csv (modalidad habitacion + raw habitaciones)
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "procesado"
RAW = ROOT / "data" / "raw"


def _valid_codes() -> set:
    """Códigos INE presentes en dim_municipios (cuarentena Silver)."""
    for base in (PROC, RAW):
        p = base / "dim_municipios.csv"
        if p.exists():
            with p.open(encoding="utf-8-sig", newline="") as fh:
                return {str(r.get("codigo_ine", "")).strip().zfill(5)
                        for r in csv.DictReader(fh)
                        if r.get("codigo_ine")}
    return set()


def _dim_provincia() -> dict:
    for base in (PROC, RAW):
        p = base / "dim_municipios.csv"
        if p.exists():
            out = {}
            with p.open(encoding="utf-8-sig", newline="") as fh:
                for r in csv.DictReader(fh):
                    code = str(r.get("codigo_ine", "")).strip().zfill(5)
                    if code:
                        out[code] = r.get("territorio")
            return out
    return {}


def _norm_code(v):
    if v is None:
        return None
    s = str(v).strip()
    if s.isdigit():
        s = s.zfill(5)
    return s or None


def _to_bool(v):
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in {"true", "1", "yes", "si", "sí"}:
        return True
    if s in {"false", "0", "no", "", "none", "null"}:
        return False
    return v

COLS_RESIDENCIAL = [
    "portal", "modalidad", "codigo_ine", "municipio", "provincia",
    "precio_eur", "superficie_m2", "habitaciones", "banos",
    "alquiler_temporal", "es_outlier_superficie", "url_detalle",
    "titulo", "subtitulo",
]

COLS_HABITACIONES = [
    "portal", "codigo_ine", "municipio", "precio_eur", "superficie_m2",
    "habitaciones", "url_detalle", "titulo", "subtitulo",
]


def _flatten_unificado(reg: dict) -> dict:
    ub = reg.get("ubicacion") or {}
    return {
        "portal": reg.get("portal"),
        "modalidad": reg.get("modalidad"),
        "codigo_ine": ub.get("codigo_ine"),
        "municipio": ub.get("municipio"),
        "provincia": ub.get("provincia"),
        "precio_eur": reg.get("precio_eur"),
        "superficie_m2": reg.get("superficie_m2"),
        "habitaciones": reg.get("habitaciones"),
        "banos": reg.get("banos"),
        "alquiler_temporal": reg.get("modalidad") == "temporal",
        "es_outlier_superficie": reg.get("es_outlier_superficie"),
        "url_detalle": reg.get("auditoria", {}).get("url_detalle") if isinstance(reg.get("auditoria"), dict) else None,
        "titulo": reg.get("titulo"),
        "subtitulo": reg.get("subtitulo"),
    }


def generar_residencial() -> int:
    # Lee el CSV limpio de T1 (cuarentena ya aplicada).
    src = PROC / "anuncios_unificados.csv"
    valid = _valid_codes()
    provincias = _dim_provincia()
    filas = []
    with src.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            modalidad = (r.get("modalidad") or "").strip()
            if modalidad == "temporal":
                continue
            if modalidad == "habitacion":
                continue
            code = _norm_code(r.get("codigo_ine"))
            if code is None or (valid and code not in valid):
                continue
            filas.append({
                "portal": r.get("portal"),
                "modalidad": modalidad,
                "codigo_ine": code,
                "municipio": r.get("municipio"),
                "provincia": provincias.get(code, r.get("provincia")),
                "precio_eur": r.get("precio_eur"),
                "superficie_m2": r.get("superficie_m2"),
                "habitaciones": r.get("habitaciones"),
                "banos": r.get("banos"),
                "alquiler_temporal": modalidad == "temporal",
                "es_outlier_superficie": _to_bool(r.get("es_outlier_superficie")),
                "url_detalle": r.get("url_detalle"),
                "titulo": r.get("titulo"),
                "subtitulo": r.get("subtitulo"),
            })
    out = PROC / "anuncios_vivienda_residencial.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS_RESIDENCIAL, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    return len(filas)


def _normalizar_habitacion_fotocasa(reg: dict) -> dict:
    return {
        "portal": "fotocasa",
        "codigo_ine": _norm_code(reg.get("codigo_ine")),
        "municipio": reg.get("municipio"),
        "precio_eur": reg.get("precio_eur"),
        "superficie_m2": reg.get("superficie_m2"),
        "habitaciones": reg.get("habitaciones"),
        "url_detalle": reg.get("url_detalle"),
        "titulo": reg.get("titulo"),
        "subtitulo": reg.get("subtitulo"),
    }


def _normalizar_habitacion_pisos(reg: dict) -> dict:
    return {
        "portal": "pisos",
        "codigo_ine": _norm_code(reg.get("codigo_ine")),
        "municipio": reg.get("municipio_busqueda"),
        "precio_eur": reg.get("precio_eur"),
        "superficie_m2": reg.get("superficie_m2"),
        "habitaciones": reg.get("habitaciones"),
        "url_detalle": reg.get("url_detalle"),
        "titulo": reg.get("titulo"),
        "subtitulo": reg.get("subtitulo"),
    }


def generar_habitaciones() -> int:
    valid = _valid_codes()
    filas = []
    # Fotocasa
    p = RAW / "anuncios_fotocasa_habitaciones.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        regs = d.get("datos", d) if isinstance(d, dict) else d
        for r in regs:
            f = _normalizar_habitacion_fotocasa(r)
            if valid and f["codigo_ine"] not in valid:
                continue
            filas.append(f)
    # Pisos
    p = RAW / "anuncios_pisos_habitaciones.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        regs = d.get("datos", d) if isinstance(d, dict) else d
        for r in regs:
            f = _normalizar_habitacion_pisos(r)
            if valid and f["codigo_ine"] not in valid:
                continue
            filas.append(f)
    # Dedup by (portal, url_detalle or precio+municipio)
    vistos = set()
    unicos = []
    for f in filas:
        clave = (f["portal"], f.get("url_detalle") or f"{f.get('municipio')}_{f.get('precio_eur')}")
        if clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(f)
    out = PROC / "anuncios_habitaciones_unificados.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS_HABITACIONES, extrasaction="ignore")
        w.writeheader()
        w.writerows(unicos)
    return len(unicos)


def main() -> int:
    n_res = generar_residencial()
    n_hab = generar_habitaciones()
    print(f"Residencial: {n_res} | Habitaciones: {n_hab}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
