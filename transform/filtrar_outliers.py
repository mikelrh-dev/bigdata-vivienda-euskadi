"""Filtrado heuristico de outliers en anuncios de alquiler (Fotocasa + Pisos.com).

Marca (no elimina) anuncios con valores fuera de rango razonable:
  - precio_m2 < 3 o > 50  -> outlier = true
  - superficie_m2 < 10 o > 500 -> outlier = true

Genera:
  - data/procesado/anuncios_fotocasa_filtrado.json / .csv
  - data/procesado/anuncios_pisos_filtrado.json / .csv

Los originales en data/raw/ no se modifican.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

# Añadir extract/ al path para importar _common
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("filtrar_outliers")

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "procesado"
PROC_DIR.mkdir(parents=True, exist_ok=True)

# Umbrales configurables
PRECIO_M2_MIN = 3.0
PRECIO_M2_MAX = 50.0
SUPERFICIE_MIN = 10.0
SUPERFICIE_MAX = 500.0


def _cargar_anuncios(nombre_json: str) -> list[dict]:
    ruta = RAW_DIR / nombre_json
    if not ruta.exists():
        log.warning("No existe %s, se omite.", ruta)
        return []
    data = json.loads(ruta.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for key in ("datos", "anuncios", "registros"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # fallback: buscar primera lista
        for v in data.values():
            if isinstance(v, list):
                return v
    if isinstance(data, list):
        return data
    return []


def _calcular_precio_m2(anuncio: dict) -> float | None:
    precio = anuncio.get("precio_eur") or anuncio.get("precio") or anuncio.get("precio_mensual")
    superficie = anuncio.get("superficie_m2") or anuncio.get("superficie")
    if precio is None or superficie is None:
        return None
    try:
        p = float(precio)
        s = float(superficie)
    except (ValueError, TypeError):
        return None
    if s <= 0:
        return None
    return round(p / s, 2)


def _filtrar(anuncios: list[dict]) -> list[dict]:
    resultado = []
    for a in anuncios:
        copia = dict(a)
        precio_m2 = _calcular_precio_m2(copia)
        if precio_m2 is not None:
            copia["precio_m2_calculado"] = precio_m2
        else:
            copia["precio_m2_calculado"] = copia.get("precio_m2")

        outlier = False
        motivos = []

        pm2 = copia.get("precio_m2_calculado")
        if pm2 is not None:
            if pm2 < PRECIO_M2_MIN:
                outlier = True
                motivos.append("precio_m2_bajo")
            if pm2 > PRECIO_M2_MAX:
                outlier = True
                motivos.append("precio_m2_alto")

        sup = copia.get("superficie_m2") or copia.get("superficie")
        if sup is not None:
            try:
                s = float(sup)
                if s < SUPERFICIE_MIN:
                    outlier = True
                    motivos.append("superficie_baja")
                if s > SUPERFICIE_MAX:
                    outlier = True
                    motivos.append("superficie_alta")
            except (ValueError, TypeError):
                pass

        copia["outlier"] = outlier
        copia["motivo_outlier"] = ";".join(motivos) if motivos else ""
        resultado.append(copia)
    return resultado


def _guardar(nombre_base: str, anuncios: list[dict]) -> None:
    if not anuncios:
        log.warning("Sin anuncios para %s, se omite guardado.", nombre_base)
        return
    # JSON
    ruta_json = PROC_DIR / f"{nombre_base}_filtrado.json"
    guardar_json(
        ruta_json,
        anuncios,
        metadata={
            "fuente": f"filtrado heuristico de {nombre_base}",
            "fecha": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            "n_total": len(anuncios),
            "n_outliers": sum(1 for a in anuncios if a.get("outlier")),
            "umbrales": {
                "precio_m2_min": PRECIO_M2_MIN,
                "precio_m2_max": PRECIO_M2_MAX,
                "superficie_min": SUPERFICIE_MIN,
                "superficie_max": SUPERFICIE_MAX,
            },
        },
    )
    # CSV
    ruta_csv = PROC_DIR / f"{nombre_base}_filtrado.csv"
    columnas = list(anuncios[0].keys())
    with ruta_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(anuncios)
    log.info("CSV -> %s (%d)", ruta_csv.name, len(anuncios))


def main() -> int:
    for nombre_json, nombre_base in [
        ("anuncios_fotocasa.json", "anuncios_fotocasa"),
        ("anuncios_pisos.json", "anuncios_pisos"),
    ]:
        anuncios = _cargar_anuncios(nombre_json)
        if not anuncios:
            continue
        filtrados = _filtrar(anuncios)
        n_out = sum(1 for a in filtrados if a.get("outlier"))
        log.info("%s: %d anuncios, %d outliers", nombre_base, len(filtrados), n_out)
        _guardar(nombre_base, filtrados)

    log.info("P1a completado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
