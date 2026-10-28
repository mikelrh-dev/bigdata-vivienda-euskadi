"""Descarga y parseo de EMAL (fianzas de alquiler) y Etxebide (solicitudes).

Fuentes Open Data Euskadi:
  - EMAL: XLSX con tablas por municipio/territorio/distrito/barrio.
  - Etxebide: CSV (indicador 86) con solicitudes por municipio y año.

Salida:
  - data/raw/emal_fianzas.csv / .json
  - data/raw/etxebide_solicitudes.csv / .json
"""

from __future__ import annotations

import csv
import io
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("opendata_bizilagun_etxebide")

URL_EMAL = (
    "https://opendata.euskadi.eus/contenidos/estadistica/"
    "122417_emal_tablas_estad/opendata/EMAL.-Barrios-Municipios.-2016-2025_es.xlsx"
)
URL_ETXEBIDE = (
    "https://opendata.euskadi.eus/contenidos/estadistica/"
    "udalmap_indicador_86/es_def/adjuntos/indicator.csv"
)


# ─── Utilidades de limpieza ─────────────────────────────────────────
def _str_or_none(valor) -> str | None:
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    texto = str(valor).strip()
    return texto if texto and texto.lower() not in {"nan", "none"} else None


def _a_entero(valor) -> int | None:
    # Soporte directo para tipos numéricos de pandas/numpy y Excel.
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(valor, "item"):
        try:
            valor = valor.item()
        except (TypeError, ValueError, AttributeError):
            pass
    if isinstance(valor, bool):
        return int(valor)
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        if math.isnan(valor):
            return None
        return int(valor) if float(valor).is_integer() else int(round(valor))

    texto = _str_or_none(valor)
    if texto is None:
        return None
    if texto in {"-", "..", ""}:
        return None
    texto = texto.replace(".", "").replace(",", ".")
    try:
        numero = float(texto)
    except ValueError:
        return None
    if math.isnan(numero):
        return None
    return int(numero) if float(numero).is_integer() else int(round(numero))


def _a_numero(valor) -> float | None:
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(valor, "item"):
        try:
            valor = valor.item()
        except (TypeError, ValueError, AttributeError):
            pass
    if isinstance(valor, bool):
        return float(valor)
    if isinstance(valor, (int, float)):
        numero = float(valor)
        return None if math.isnan(numero) else numero

    texto = _str_or_none(valor)
    if texto is None:
        return None
    if texto in {"-", "..", ""}:
        return None
    texto = texto.replace(".", "").replace(",", ".")
    try:
        numero = float(texto)
    except ValueError:
        return None
    return None if math.isnan(numero) else numero


def _limpiar_registros(registros: list[dict]) -> list[dict]:
    limpios = []
    for fila in registros:
        nueva = {}
        for clave, valor in fila.items():
            if isinstance(valor, float) and math.isnan(valor):
                nueva[clave] = None
            else:
                nueva[clave] = valor
        limpios.append(nueva)
    return limpios


# ─── EMAL (XLSX) ────────────────────────────────────────────────────
def parsear_emal(ruta_xlsx: Path) -> tuple[list[int], list[dict]]:
    """Parsea las tablas anuales municipales T2.1/T2.2/T2.3 (fianzas y renta)."""
    specs = [
        ("T2.1", "fianzas", True),
        ("T2.2", "renta_media_eur_mes", False),
        ("T2.3", "renta_media_eur_m2_mes", False),
    ]

    parseado: dict[str, tuple[list[int], dict[str, dict]]] = {}
    for hoja, _metrica, entero in specs:
        df = pd.read_excel(ruta_xlsx, sheet_name=hoja, header=None, engine="openpyxl")

        # Años disponibles (fila 1, columnas 2..11)
        anios: list[int | None] = []
        for columna in range(2, 12):
            anios.append(_a_entero(df.iloc[1, columna]))

        por_codigo: dict[str, dict] = {}
        for _, fila in df.iterrows():
            codigo = _str_or_none(fila.iloc[0])
            if codigo is None or not re.fullmatch(r"\d{5}", codigo):
                continue
            nombre = _str_or_none(fila.iloc[1])
            valores: dict[int, int | float | None] = {}
            for idx, anio in enumerate(anios):
                if anio is None:
                    continue
                valores[anio] = (
                    _a_entero(fila.iloc[2 + idx])
                    if entero
                    else _a_numero(fila.iloc[2 + idx])
                )
            por_codigo[codigo] = {
                "municipio": nombre,
                "valores": valores,
                "vigentes_2024": _a_entero(fila.iloc[13]),
                "vigentes_2025": _a_entero(fila.iloc[14]),
            }
        parseado[hoja] = (anios, por_codigo)

    anios = parseado["T2.1"][0]
    anios = [a for a in anios if a is not None]

    codigos = sorted(
        set().union(*(set(info[1].keys()) for info in parseado.values()))
    )
    nombres = {}
    for _hoja, _metrica, _entero in specs:
        for codigo, info in parseado[_hoja][1].items():
            if info.get("municipio"):
                nombres[codigo] = info["municipio"]

    registros: list[dict] = []
    for codigo in codigos:
        info_fianzas = parseado["T2.1"][1].get(codigo, {})
        info_renta = parseado["T2.2"][1].get(codigo, {})
        info_m2 = parseado["T2.3"][1].get(codigo, {})
        for anio in anios:
            registros.append(
                {
                    "codigo_ine": codigo,
                    "municipio": nombres.get(codigo),
                    "anio": anio,
                    "fianzas": info_fianzas.get("valores", {}).get(anio),
                    "renta_media_eur_mes": info_renta.get("valores", {}).get(anio),
                    "renta_media_eur_m2_mes": info_m2.get("valores", {}).get(anio),
                    "alquileres_vigentes_2024": info_fianzas.get("vigentes_2024"),
                    "alquileres_vigentes_2025": info_fianzas.get("vigentes_2025"),
                    "ambito": "municipios_mas_5000",
                }
            )
    return anios, _limpiar_registros(registros)


# ─── Etxebide (CSV) ──────────────────────────────────────────────────
def parsear_etxebide(texto: str) -> list[dict]:
    """Extrae la sección 'Detalle por municipios' y la convierte a formato largo."""
    lineas = texto.splitlines()
    inicio = None
    for i, linea in enumerate(lineas):
        if linea.strip().lower().startswith("detalle por municipios"):
            inicio = i
            break
    if inicio is None:
        raise ValueError("No se encontró la sección 'Detalle por municipios'")

    j = inicio + 1
    while j < len(lineas) and not lineas[j].strip():
        j += 1
    if j >= len(lineas):
        raise ValueError("Cabecera de municipios no encontrada")
    cabecera = lineas[j].strip()

    datos_lineas: list[str] = []
    k = j + 1
    while k < len(lineas) and lineas[k].strip() != "":
        datos_lineas.append(lineas[k])
        k += 1
    if not datos_lineas:
        raise ValueError("Sin filas de municipios en Etxebide")

    csv_texto = cabecera + "\n" + "\n".join(datos_lineas)
    df = pd.read_csv(
        io.StringIO(csv_texto),
        sep=";",
        decimal=",",
        thousands=".",
        dtype={0: str, 1: str},
    )
    df.columns = [str(c).strip() for c in df.columns]
    columnas = list(df.columns)
    df = df.rename(columns={columnas[0]: "codigo_ine", columnas[1]: "municipio"})

    columnas_anio = [c for c in df.columns if re.fullmatch(r"\d{4}", c)]
    largo = df.melt(
        id_vars=["codigo_ine", "municipio"],
        value_vars=columnas_anio,
        var_name="anio",
        value_name="etxebide_solicitudes_por_mil",
    )
    largo["codigo_ine"] = largo["codigo_ine"].str.strip().str.zfill(5)
    largo["municipio"] = largo["municipio"].str.strip()
    largo["anio"] = largo["anio"].astype(int)
    largo["etxebide_solicitudes_por_mil"] = pd.to_numeric(
        largo["etxebide_solicitudes_por_mil"], errors="coerce"
    )

    registros: list[dict] = []
    for fila in largo.to_dict(orient="records"):
        valor = fila["etxebide_solicitudes_por_mil"]
        registros.append(
            {
                "codigo_ine": fila["codigo_ine"],
                "municipio": fila["municipio"],
                "anio": int(fila["anio"]),
                "etxebide_solicitudes_por_mil": (
                    None if (isinstance(valor, float) and math.isnan(valor)) else float(valor)
                ),
            }
        )
    return _limpiar_registros(registros)


def _escribir_csv(destino: Path, registros: list[dict], columnas: list[str]) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8-sig") as fh:
        escritor = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        for fila in registros:
            escritor.writerow({c: ("" if fila.get(c) is None else fila.get(c)) for c in columnas})


def main() -> int:
    cliente = Cliente("opendata_bizilagun_etxebide", delay=1.0)

    # ── EMAL ─────────────────────────────────────────────────────────
    ruta_xlsx = RAW_DIR / "emal_barrios_municipios_2016_2025.xlsx"
    cliente.descargar(URL_EMAL, ruta_xlsx)
    _anios, registros_emal = parsear_emal(ruta_xlsx)

    guardar_json(
        RAW_DIR / "emal_fianzas.json",
        registros_emal,
        metadata={
            "fuente": "EMAL - Estadística del Mercado de Alquiler (Open Data Euskadi)",
            "url": URL_EMAL,
            "hojas": ["T2.1", "T2.2", "T2.3"],
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_registros": len(registros_emal),
        },
    )
    columnas_emal = [
        "codigo_ine",
        "municipio",
        "anio",
        "fianzas",
        "renta_media_eur_mes",
        "renta_media_eur_m2_mes",
        "alquileres_vigentes_2024",
        "alquileres_vigentes_2025",
        "ambito",
    ]
    _escribir_csv(RAW_DIR / "emal_fianzas.csv", registros_emal, columnas_emal)
    log.info("EMAL: %d registros", len(registros_emal))

    # ── Etxebide ─────────────────────────────────────────────────────
    ruta_etx = RAW_DIR / "etxebide_indicador_86.csv"
    cliente.descargar(URL_ETXEBIDE, ruta_etx)
    texto_etx = ruta_etx.read_text(encoding="latin-1")
    registros_etx = parsear_etxebide(texto_etx)

    guardar_json(
        RAW_DIR / "etxebide_solicitudes.json",
        registros_etx,
        metadata={
            "fuente": "Udalmap indicador 86 - Solicitudes Etxebide (Open Data Euskadi)",
            "url": URL_ETXEBIDE,
            "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
            "n_registros": len(registros_etx),
        },
    )
    columnas_etx = ["codigo_ine", "municipio", "anio", "etxebide_solicitudes_por_mil"]
    _escribir_csv(RAW_DIR / "etxebide_solicitudes.csv", registros_etx, columnas_etx)
    log.info("Etxebide: %d registros", len(registros_etx))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
