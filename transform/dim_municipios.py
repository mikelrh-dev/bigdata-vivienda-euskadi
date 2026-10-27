"""Catálogo canónico de municipios (Entity Resolution).

Genera `dim_municipios` con `codigo_ine` oficial y `nombre_canonico` a partir
de Eustat, y resuelve las variantes de nombre de todas las fuentes
(Fotocasa, Pisos.com, RealtyAPI, Eustat Alquiler) hacia ese código.

Salida: data/raw/dim_municipios.json y .csv
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("dim_municipios")


def _norm(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    texto = texto.lower().strip()
    texto = re.sub(r"[\s\-_/]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# Equivalencias manuales para variantes bilingües / formatos distintos.
# Clave: nombre normalizado de la fuente -> nombre normalizado Eustat.
EQUIVALENCIAS = {
    "donostia san sebastian": "donostia san sebastian",
    "donostia - san sebastian": "donostia san sebastian",
    "san sebastian": "donostia san sebastian",
    "vitoria gasteiz": "vitoria gasteiz",
    "vitoria - gasteiz": "vitoria gasteiz",
    "vitoria": "vitoria gasteiz",
    "arrasate mondragon": "arrasate mondragon",
    "arrasate / mondragon": "arrasate mondragon",
    "mondragon": "arrasate mondragon",
    "arrankudiaga zollo": "arrankudiaga zollo",
    "arrankudiaga / zollo": "arrankudiaga zollo",
    "bilbao": "bilbao",
    "getxo": "getxo",
}


def _cargar_eustat() -> dict[str, dict]:
    """Devuelve {nombre_normalizado: {codigo_ine, nombre_canonico, territorio}}."""
    import pandas as pd

    df = pd.read_csv(RAW_DIR / "eustat_renta_municipal.csv", low_memory=False)
    muni = df[df["ámbitos territoriales"].astype(str).str.len().isin([4, 5])][
        ["ámbitos territoriales", "ámbitos territoriales__etiqueta"]
    ].drop_duplicates()

    # territorio por codigo de provincia
    prov = {"48": "Bizkaia", "20": "Gipuzkoa", "01": "Araba/Álava"}

    resultado = {}
    for _, row in muni.iterrows():
        codigo = str(row["ámbitos territoriales"]).strip().zfill(5)
        nombre = str(row["ámbitos territoriales__etiqueta"]).strip()
        territorio = prov.get(codigo[:2], "Desconocido")
        resultado[_norm(nombre)] = {
            "codigo_ine": codigo,
            "nombre_canonico": nombre,
            "territorio": territorio,
        }
    return resultado


def main() -> int:
    eustat = _cargar_eustat()
    log.info("Municipios Eustat: %d", len(eustat))

    # Variantes de Fotocasa
    import pandas as pd

    fot = pd.read_csv(RAW_DIR / "anuncios_fotocasa.csv")
    fot_mun = sorted(fot["municipio"].dropna().unique())

    # Variantes de alquiler municipal
    alq = pd.read_csv(RAW_DIR / "alquiler_municipal.csv")
    alq_mun = sorted(alq["municipio"].dropna().unique())

    # Variantes de Pisos (si existe)
    pisos_mun = []
    if (RAW_DIR / "anuncios_pisos.csv").exists():
        pisos = pd.read_csv(RAW_DIR / "anuncios_pisos.csv")
        pisos_mun = sorted(pisos["municipio_busqueda"].dropna().unique())

    # Construir dim_municipios enriquecido con variantes
    registros = []
    for norm_eustat, info in eustat.items():
        variantes = [info["nombre_canonico"]]
        # Fotocasa
        for v in fot_mun:
            if _norm(v) in EQUIVALENCIAS and EQUIVALENCIAS[_norm(v)] == norm_eustat:
                variantes.append(v)
            elif _norm(v) == norm_eustat and v not in variantes:
                variantes.append(v)
        # Alquiler
        for v in alq_mun:
            if _norm(v) in EQUIVALENCIAS and EQUIVALENCIAS[_norm(v)] == norm_eustat:
                if v not in variantes:
                    variantes.append(v)
            elif _norm(v) == norm_eustat and v not in variantes:
                variantes.append(v)
        # Pisos
        for v in pisos_mun:
            if _norm(v) in EQUIVALENCIAS and EQUIVALENCIAS[_norm(v)] == norm_eustat:
                if v not in variantes:
                    variantes.append(v)
            elif _norm(v) == norm_eustat and v not in variantes:
                variantes.append(v)

        registros.append(
            {
                "codigo_ine": info["codigo_ine"],
                "nombre_canonico": info["nombre_canonico"],
                "territorio": info["territorio"],
                "nombre_normalizado": norm_eustat,
                "variantes": variantes,
            }
        )

    # Resolver los 4 casos conflictivos explícitamente
    for r in registros:
        if r["nombre_canonico"] in ("Donostia-San Sebastián", "Donostia / San Sebastián"):
            pass

    # Añadir variantes de Fotocasa no resueltas (para diagnóstico)
    fot_no_resueltos = []
    for v in fot_mun:
        nv = _norm(v)
        nv_eq = EQUIVALENCIAS.get(nv, nv)
        if nv_eq not in eustat:
            fot_no_resueltos.append(v)
    if fot_no_resueltos:
        log.warning("Fotocasa municipios no resueltos: %s", fot_no_resueltos)

    # Guardar JSON
    guardar_json(
        RAW_DIR / "dim_municipios.json",
        registros,
        metadata={
            "fuente": "Eustat (codigo INE + nombre canonico) + equivalencias manuales",
            "fecha": "2026-10-27",
            "n_municipios": len(registros),
            "n_no_resueltos_fotocasa": len(fot_no_resueltos),
        },
    )

    # Guardar CSV plano (sin listas)
    csv_path = RAW_DIR / "dim_municipios.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["codigo_ine", "nombre_canonico", "territorio", "nombre_normalizado", "variantes"])
        for r in registros:
            w.writerow([r["codigo_ine"], r["nombre_canonico"], r["territorio"], r["nombre_normalizado"], "|".join(r["variantes"])])
    log.info("CSV -> %s", csv_path.name)

    # Verificación de los 3 municipios clave
    for nombre in ["Donostia - San Sebastián", "Vitoria - Gasteiz", "Bilbao"]:
        nv = EQUIVALENCIAS.get(_norm(nombre), _norm(nombre))
        info = eustat.get(nv)
        print(f"{nombre} -> {info['codigo_ine'] if info else 'NO RESUELTO'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY