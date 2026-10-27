"""Completa alquiler_municipal.csv para los 93 municipios sin dato oficial
agregando a nivel de comarca (media de los municipios con dato).

Genera: data/procesado/alquiler_municipal_completo.csv

Los municipios con dato original mantienen nivel_geografico='municipal'.
Los completados tienen nivel_geografico='comarcal'.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("completar_alquiler_comarca")

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "procesado"
PROC_DIR.mkdir(parents=True, exist_ok=True)


def _cargar_dim() -> dict[str, dict]:
    dim = json.loads((RAW_DIR / "dim_municipios.json").read_text(encoding="utf-8"))
    regs = dim.get("datos", dim) if isinstance(dim, dict) else dim
    return {r["codigo_ine"]: r for r in regs}


def _cargar_distancias() -> dict[str, str]:
    """codigo_ine -> comarca."""
    import csv as _csv
    result = {}
    with (RAW_DIR / "distancias_capitales.csv").open(encoding="utf-8-sig") as fh:
        for row in _csv.DictReader(fh):
            result[row["codigo_ine"]] = row.get("comarca", "")
    return result


def _cargar_alquiler() -> dict[str, dict]:
    """municipio (normalizado) -> fila de alquiler (primer distrito)."""
    result = {}
    with (RAW_DIR / "alquiler_municipal.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            muni = row["municipio"].strip()
            if muni not in result:
                result[muni] = row
    return result


def _normalizar_nombre(nombre: str) -> str:
    return nombre.strip().lower()


def main() -> int:
    dim = _cargar_dim()
    dist = _cargar_distancias()
    alquiler = _cargar_alquiler()

    # Mapa nombre_canonico -> codigo_ine
    nombre_a_codigo = {r["nombre_canonico"]: c for c, r in dim.items()}

    # Calcular media de alquiler por comarca (solo municipios con dato)
    comarca_valores: dict[str, list[dict]] = {}
    for codigo, info in dim.items():
        nombre = info["nombre_canonico"]
        row = alquiler.get(nombre)
        if row is None:
            continue
        comarca = dist.get(codigo, "")
        comarca_valores.setdefault(comarca, []).append(row)

    comarca_media: dict[str, dict] = {}
    for comarca, rows in comarca_valores.items():
        if not rows:
            continue
        # Media de las columnas numéricas
        cols = [k for k in rows[0].keys() if k not in ("territorio", "municipio", "distrito")]
        media = {}
        for col in cols:
            vals = []
            for r in rows:
                try:
                    vals.append(float(r[col]))
                except (ValueError, TypeError):
                    pass
            media[col] = round(sum(vals) / len(vals), 2) if vals else None
        comarca_media[comarca] = media

    # Generar lista completa de 252 municipios
    salida = []
    for codigo in sorted(dim.keys()):
        info = dim[codigo]
        nombre = info["nombre_canonico"]
        territorio = info.get("territorio", "")
        comarca = dist.get(codigo, "")
        row = alquiler.get(nombre)
        if row is not None:
            fila = dict(row)
            fila["codigo_ine"] = codigo
            fila["nivel_geografico"] = "municipal"
            salida.append(fila)
        else:
            # Agregar a comarca
            media = comarca_media.get(comarca, {})
            fila = {"territorio": territorio, "municipio": nombre, "distrito": "00 (comarcal)"}
            fila["codigo_ine"] = codigo
            for col in (row.keys() if row else []):
                if col not in ("territorio", "municipio", "distrito"):
                    fila[col] = media.get(col)
            if not row:
                # columnas por defecto
                for col in ["renta_media_eur_m2_media", "renta_media_eur_m2_mediana", "renta_media_eur_m2_p25", "renta_media_eur_m2_p75",
                            "cuantia_media_eur_mes_media", "cuantia_media_eur_mes_mediana", "cuantia_media_eur_mes_p25", "cuantia_media_eur_mes_p75",
                            "superficie_media_m2_media", "superficie_media_m2_mediana", "superficie_media_m2_p25", "superficie_media_m2_p75"]:
                    fila[col] = media.get(col)
            fila["nivel_geografico"] = "comarcal"
            salida.append(fila)

    # Guardar CSV
    columnas = ["codigo_ine", "territorio", "municipio", "distrito", "nivel_geografico"] + \
               [k for k in salida[0].keys() if k not in ("codigo_ine", "territorio", "municipio", "distrito", "nivel_geografico")]
    ruta_csv = PROC_DIR / "alquiler_municipal_completo.csv"
    with ruta_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(salida)

    n_municipal = sum(1 for r in salida if r.get("nivel_geografico") == "municipal")
    n_comarcal = sum(1 for r in salida if r.get("nivel_geografico") == "comarcal")
    log.info("alquiler_municipal_completo: %d municipios (%d municipal, %d comarcal)",
             len(salida), n_municipal, n_comarcal)
    log.info("CSV -> %s", ruta_csv.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
