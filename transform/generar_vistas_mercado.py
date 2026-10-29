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
    data = json.loads((PROC / "anuncios_unificados.json").read_text(encoding="utf-8"))
    regs = data if isinstance(data, list) else data.get("datos", [])
    filas = []
    for r in regs:
        flat = _flatten_unificado(r)
        if flat["modalidad"] == "temporal":
            continue
        if flat["modalidad"] == "habitacion":
            continue
        filas.append(flat)
    out = PROC / "anuncios_vivienda_residencial.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS_RESIDENCIAL, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    return len(filas)


def _normalizar_habitacion_fotocasa(reg: dict) -> dict:
    return {
        "portal": "fotocasa",
        "codigo_ine": reg.get("codigo_ine"),
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
        "codigo_ine": reg.get("codigo_ine"),
        "municipio": reg.get("municipio_busqueda"),
        "precio_eur": reg.get("precio_eur"),
        "superficie_m2": reg.get("superficie_m2"),
        "habitaciones": reg.get("habitaciones"),
        "url_detalle": reg.get("url_detalle"),
        "titulo": reg.get("titulo"),
        "subtitulo": reg.get("subtitulo"),
    }


def generar_habitaciones() -> int:
    filas = []
    # Fotocasa
    p = RAW / "anuncios_fotocasa_habitaciones.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        regs = d.get("datos", d) if isinstance(d, dict) else d
        for r in regs:
            filas.append(_normalizar_habitacion_fotocasa(r))
    # Pisos
    p = RAW / "anuncios_pisos_habitaciones.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        regs = d.get("datos", d) if isinstance(d, dict) else d
        for r in regs:
            filas.append(_normalizar_habitacion_pisos(r))
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
