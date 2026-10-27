"""Extrae renta disponible por hogar a nivel municipal desde el INE Atlas de la Renta.

Fuente: INE Atlas de Distribucion de Renta de los Hogares (ADRH), tabla 30824.
Descarga en streaming el CSV completo (~392 MB) y filtra municipios de Euskadi.

Genera:
  - data/raw/ine_atlas_renta.json / .csv  (51 municipios faltantes en Eustat)
  - data/raw/renta_municipal_completa.json / .csv  (252 municipios: 201 Eustat + 51 Atlas)

Campos añadidos: renta_atlas, anio_renta, renta_origen
Los 201 municipios de Eustat NO se sobrescriben.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("ine_atlas_renta")

URL_CSV = "https://www.ine.es/jaxiT3/files/t/es/csv_bd/30824.csv"
INDICADOR = "Renta neta media por hogar"

# Códigos INE de provincias de Euskadi
PROVINCIAS_EUSKADI = {"01", "20", "48"}


def _cargar_dim() -> dict:
    ruta = RAW_DIR / "dim_municipios.json"
    if not ruta.exists():
        log.error("Falta dim_municipios.json. Ejecuta transform/dim_municipios.py primero.")
        sys.exit(1)
    data = json.loads(ruta.read_text(encoding="utf-8"))
    regs = data.get("datos", data) if isinstance(data, dict) else data
    return {r["codigo_ine"]: r["nombre_canonico"] for r in regs}


def _cargar_eustat() -> dict:
    ruta = RAW_DIR / "eustat_renta_municipal.json"
    if not ruta.exists():
        log.warning("No existe eustat_renta_municipal.json. Se procesa solo Atlas.")
        return {}
    data = json.loads(ruta.read_text(encoding="utf-8"))
    filas = data.get("datos", {}).get("filas", [])
    renta_col = None
    for k in (filas[0].keys() if filas else []):
        if "euros" in k.lower():
            renta_col = k
            break
    result = {}
    for r in filas:
        cod = r.get("ámbitos territoriales", "")
        if not re.fullmatch(r"\d{5}", str(cod)) or str(cod)[:2] not in PROVINCIAS_EUSKADI:
            continue
        if r.get("tipo de renta") != "100" or r.get("sexo") != "10":
            continue
        if r.get("periodo") != "2024":
            continue
        val = r.get(renta_col)
        if val in (None, "", "..", ":", "n.d."):
            continue
        try:
            renta_val = float(str(val).replace(".", "").replace(",", "."))
        except ValueError:
            continue
        result[str(cod).zfill(5)] = {
            "nombre": r.get("ámbitos territoriales__etiqueta", ""),
            "renta_eustat": renta_val,
            "anio": 2024,
        }
    return result


def main() -> int:
    dim = _cargar_dim()
    eustat = _cargar_eustat()

    # Municipios de Euskadi que ya tienen renta en Eustat
    eustat_codigos = set(eustat.keys())
    # Todos los municipios de Euskadi (252)
    todos_codigos = set(dim.keys())

    # Atlas: renta por codigo_ine (solo el año mas reciente)
    atlas: dict[str, dict] = {}
    log.info("Descargando CSV del INE Atlas (streaming)...")
    import requests

    r = requests.get(URL_CSV, timeout=300, stream=True)
    r.raise_for_status()

    import gzip, io
    gz = gzip.GzipFile(fileobj=r.raw)
    text_stream = io.TextIOWrapper(gz, encoding="utf-8-sig")
    reader = csv.reader(text_stream, delimiter="\t")
    header = next(reader, None)
    log.info("Cabecera: %s", header)

    anio_max = 0
    n_filas = 0
    n_euskadi = 0
    for row in reader:
        if len(row) < 6:
            continue
        n_filas += 1
        municipio_col = row[0].strip()
        distrito = row[1].strip()
        seccion = row[2].strip()
        indicador = row[3].strip()
        periodo = row[4].strip()
        total = row[5].strip()

        # Solo nivel municipal (sin distrito ni seccion)
        if distrito or seccion:
            continue

        # Extraer codigo INE
        m = re.match(r"^(\d{5})\s", municipio_col)
        if not m:
            continue
        codigo = m.group(1)
        if codigo[:2] not in PROVINCIAS_EUSKADI:
            continue

        if indicador != INDICADOR:
            continue

        # Solo el año mas reciente
        try:
            anio = int(periodo)
        except ValueError:
            continue
        if anio < anio_max:
            continue
        if anio > anio_max:
            anio_max = anio
            # limpiar atlas si encontramos año mayor
            atlas.clear()

        if total in ("", "..", ":", "n.d.", "N/A"):
            continue
        try:
            valor = float(total.replace(".", "").replace(",", "."))
        except ValueError:
            continue

        atlas[codigo] = {
            "codigo_ine": codigo,
            "nombre_canonico": dim.get(codigo, municipio_col.split(" ", 1)[-1].strip()),
            "renta_atlas": round(valor, 2),
            "anio_renta": anio,
            "renta_origen": "INE_Atlas",
        }
        n_euskadi += 1

    log.info("Filas procesadas: %d | Municipios Euskadi con Atlas: %d | Año max: %d", n_filas, len(atlas), anio_max)

    # Guardar Atlas (todos los municipios de Euskadi, como fuente independiente)
    registros_atlas = sorted(atlas.values(), key=lambda x: x["codigo_ine"])
    guardar_json(
        RAW_DIR / "ine_atlas_renta.json",
        registros_atlas,
        metadata={
            "fuente": "INE Atlas de Distribucion de Renta de los Hogares (ADRH), tabla 30824",
            "indicador": INDICADOR,
            "crs": None,
            "fecha_conversion": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            "n_registros": len(registros_atlas),
            "anio_renta": anio_max,
            "cobertura": "252 municipios de Euskadi (fuente independiente para validacion cruzada)",
            "nota": "Eustat ya cubre 252/252 municipios; Atlas se usa como fuente independiente (EXTRACCION-02)",
        },
    )

    # CSV
    csv_path = RAW_DIR / "ine_atlas_renta.csv"
    columnas = ["codigo_ine", "nombre_canonico", "renta_atlas", "anio_renta", "renta_origen"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(registros_atlas)
    log.info("CSV -> %s (%d)", csv_path.name, len(registros_atlas))

    # Guardar renta_municipal_completa.json (252: Eustat + Atlas)
    completa = []
    for cod, nombre in sorted(dim.items()):
        a = atlas.get(cod)
        e = eustat.get(cod)
        if e:
            completa.append({
                "codigo_ine": cod,
                "nombre_canonico": nombre,
                "renta_atlas": a["renta_atlas"] if a else None,
                "anio_renta": e.get("anio"),
                "renta_origen": "Eustat",
                "renta_eustat": e.get("renta_eustat"),
                "anio_fuente": 2024,
            })
        elif a:
            completa.append({
                "codigo_ine": cod,
                "nombre_canonico": nombre,
                "renta_atlas": a["renta_atlas"],
                "anio_renta": a["anio_renta"],
                "renta_origen": "INE_Atlas",
                "renta_eustat": None,
                "anio_fuente": 2022,
            })
        else:
            completa.append({
                "codigo_ine": cod,
                "nombre_canonico": nombre,
                "renta_atlas": None,
                "anio_renta": None,
                "renta_origen": None,
                "renta_eustat": None,
                "anio_fuente": None,
            })

    guardar_json(
        RAW_DIR / "renta_municipal_completa.json",
        completa,
        metadata={
            "fuente": "Eustat (201) + INE Atlas ADRH (51)",
            "fecha_conversion": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            "n_registros": len(completa),
            "n_eustat": len(eustat_codigos),
            "n_atlas": len(atlas),
            "n_sin_renta": sum(1 for c in completa if c["renta_origen"] is None),
        },
    )
    csv_path2 = RAW_DIR / "renta_municipal_completa.csv"
    columnas2 = ["codigo_ine", "nombre_canonico", "renta_atlas", "anio_renta", "renta_origen", "renta_eustat", "anio_fuente"]
    with csv_path2.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas2)
        w.writeheader()
        w.writerows(completa)
    log.info("CSV -> %s (%d)", csv_path2.name, len(completa))

    log.info("P0 completado: %d municipios con renta (Eustat %d + Atlas %d)", len(completa), len(eustat_codigos), len(atlas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY