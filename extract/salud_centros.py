"""Extracción de centros de salud, ambulatorios y hospitales públicos de Euskadi.

Descarga el directorio de centros de salud (JSON) de Open Data Euskadi y lo
normaliza añadiendo codigo_ine por centro (mapeo nombre de municipio).

Salida: data/raw/salud_centros.csv y .json
"""
from __future__ import annotations

import csv
import json
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("salud_centros")

URL = (
    "https://opendata.euskadi.eus/contenidos/ds_localizaciones/"
    "centros_salud_en_euskadi/opendata/centros-salud.json"
)


def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s


def _cargar_dim() -> tuple[dict[str, dict], dict[str, str]]:
    dim_path = RAW_DIR / "dim_municipios.json"
    if not dim_path.exists():
        raise FileNotFoundError("Falta dim_municipios.json. Ejecuta transform/dim_municipios.py primero.")
    data = json.loads(dim_path.read_text(encoding="utf-8"))
    registros = data.get("datos", data) if isinstance(data, dict) else data

    by_code = {r["codigo_ine"]: r for r in registros}

    # Mapa nombre normalizado -> codigo_ine (incluye variantes)
    name2code: dict[str, str] = {}
    for r in registros:
        name2code[_norm(r["nombre_canonico"])] = r["codigo_ine"]
        for v in r.get("variantes", []) or []:
            name2code[_norm(v)] = r["codigo_ine"]
    return by_code, name2code


def _resolver_codigo(municipio: str, provincia: str, name2code: dict[str, str], by_code: dict[str, dict]) -> str | None:
    nm = _norm(municipio)
    if nm in name2code:
        return name2code[nm]
    # intentar con provincia como pista (desambiguar nombres repetidos)
    candidatos = [c for c, r in by_code.items() if _norm(r.get("nombre_canonico", "")) == nm]
    if len(candidatos) == 1:
        return candidatos[0]
    # coincidencia parcial
    for k, v in name2code.items():
        if nm and (nm in k or k in nm):
            return v
    return None


def main() -> int:
    import requests

    log.info("Descargando directorio de centros de salud...")
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    datos_raw = r.json()
    log.info("Registros descargados: %d", len(datos_raw))

    by_code, name2code = _cargar_dim()

    registros_out = []
    for fila in datos_raw:
        municipio = (fila.get("Municipio") or "").strip()
        provincia = (fila.get("Provincia") or "").strip()
        codigo_ine = _resolver_codigo(municipio, provincia, name2code, by_code)
        if not codigo_ine:
            log.warning("Centro sin codigo_ine: %s (%s)", fila.get("Nombre"), municipio)

        registros_out.append(
            {
                "codigo_ine": codigo_ine,
                "nombre_centro": (fila.get("Nombre") or "").strip(),
                "tipo_centro": (fila.get("Tipodecentro") or "").strip(),
                "alias": (fila.get("Aliasdelcentro") or "").strip(),
                "osi": (fila.get("OSI") or "").strip(),
                "latitud": (fila.get("LATWGS84") or "").strip(),
                "longitud": (fila.get("LONWGS84") or "").strip(),
                "direccion": (fila.get("Direccion") or "").strip(),
                "municipio_nombre": municipio,
                "codigo_postal": (fila.get("Codigopostal") or "").strip(),
                "provincia": provincia,
                "anio_fuente": 2026,
            }
        )

    columnas = list(registros_out[0].keys()) if registros_out else []
    destino_csv = RAW_DIR / "salud_centros.csv"
    with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(registros_out)
    log.info("CSV -> %s (%d centros)", destino_csv.name, len(registros_out))

    guardar_json(
        RAW_DIR / "salud_centros.json",
        registros_out,
        metadata={
            "fuente": "Open Data Euskadi - Centros de salud, ambulatorios y hospitales públicos",
            "url": URL,
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_centros": len(registros_out),
            "n_municipios_cubiertos": len({r["codigo_ine"] for r in registros_out if r["codigo_ine"]}),
            "n_sin_codigo_ine": sum(1 for r in registros_out if not r["codigo_ine"]),
        },
    )
    log.info(
        "JSON -> salud_centros.json (%d centros, %d municipios)",
        len(registros_out),
        len({r["codigo_ine"] for r in registros_out if r["codigo_ine"]}),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
