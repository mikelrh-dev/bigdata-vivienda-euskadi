"""Extracción de centros docentes no universitarios de Euskadi (Open Data Euskadi).

Descarga el directorio de centros docentes (CSV, codificación latin-1) y lo
normaliza añadiendo codigo_ine por centro (mapeo territorio + código municipal).

Salida: data/raw/educacion_centros.csv y .json
"""
from __future__ import annotations

import csv
import io
import json
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("educacion_centros")

URL = (
    "https://opendata.euskadi.eus/contenidos/ds_localizaciones/"
    "centros_docentes_no_universit/es_euskadi/adjuntos/dirgennouniv.csv"
)

TERRITORIO_A_PROVINCIA = {
    "ARABA/ÁLAVA": "01",
    "BIZKAIA": "48",
    "GIPUZKOA": "20",
}


def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s


def _cargar_dim() -> dict[str, dict]:
    dim_path = RAW_DIR / "dim_municipios.json"
    if not dim_path.exists():
        raise FileNotFoundError("Falta dim_municipios.json. Ejecuta transform/dim_municipios.py primero.")
    data = json.loads(dim_path.read_text(encoding="utf-8"))
    registros = data.get("datos", data) if isinstance(data, dict) else data
    return {r["codigo_ine"]: r for r in registros}


def main() -> int:
    import requests

    log.info("Descargando directorio de centros docentes...")
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    texto = r.content.decode("latin-1")
    reader = csv.DictReader(io.StringIO(texto), delimiter=";")
    filas_raw = list(reader)
    log.info("Filas descargadas: %d", len(filas_raw))

    dim = _cargar_dim()

    registros_out = []
    for fila in filas_raw:
        territorio = (fila.get("DTERRC") or "").strip().upper()
        # normalizar acentos para la clave
        territorio_norm = _norm(territorio).upper()
        # buscar provincia en mapa (con y sin acentos)
        prov = None
        for k, v in TERRITORIO_A_PROVINCIA.items():
            if _norm(k).upper() == territorio_norm:
                prov = v
                break
        muni = (fila.get("MUNI") or "").strip().zfill(3)
        codigo_ine = (prov + muni) if prov else None
        if codigo_ine not in dim:
            log.warning("Centro sin codigo_ine: %s (%s)", fila.get("NOM"), territorio)
            codigo_ine = None

        registros_out.append(
            {
                "codigo_ine": codigo_ine,
                "nombre_centro": (fila.get("NOM") or "").strip(),
                "nombre_centro_eu": (fila.get("NOME") or "").strip(),
                "tipo_centro": (fila.get("DGENRC") or "").strip(),
                "tipo_centro_eu": (fila.get("DGENRE") or "").strip(),
                "genero": (fila.get("GENR") or "").strip(),
                "municipio_codigo": muni,
                "municipio_nombre": (fila.get("DMUNIC") or "").strip(),
                "territorio": territorio,
                "dependencia": (fila.get("DEPE") or "").strip(),
                "titularidad": (fila.get("DTITUC") or "").strip(),
                "direccion": (fila.get("DOMI") or "").strip(),
                "codigo_postal": (fila.get("CPOS") or "").strip(),
                "telefono": (fila.get("TEL1") or "").strip(),
                "fax": (fila.get("TFAX") or "").strip(),
                "email": (fila.get("EMAIL") or "").strip(),
                "web": (fila.get("PAGINA") or "").strip(),
                "coord_x_utm30": (fila.get("COOR_X") or "").strip(),
                "coord_y_utm30": (fila.get("COOR_Y") or "").strip(),
                "anio_fuente": 2026,
            }
        )

    # Guardar CSV
    columnas = list(registros_out[0].keys()) if registros_out else []
    destino_csv = RAW_DIR / "educacion_centros.csv"
    with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(registros_out)
    log.info("CSV -> %s (%d centros)", destino_csv.name, len(registros_out))

    # Guardar JSON
    guardar_json(
        RAW_DIR / "educacion_centros.json",
        registros_out,
        metadata={
            "fuente": "Open Data Euskadi - Centros docentes no universitarios",
            "url": URL,
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_centros": len(registros_out),
            "n_municipios_cubiertos": len({r["codigo_ine"] for r in registros_out if r["codigo_ine"]}),
            "n_sin_codigo_ine": sum(1 for r in registros_out if not r["codigo_ine"]),
        },
    )
    log.info(
        "JSON -> educacion_centros.json (%d centros, %d municipios)",
        len(registros_out),
        len({r["codigo_ine"] for r in registros_out if r["codigo_ine"]}),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
