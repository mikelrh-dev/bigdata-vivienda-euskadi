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
from _common import RAW_DIR, get_logger, guardar_json, leer_csv_seguro  # noqa: E402

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

    df = pd.read_csv(RAW_DIR / "eustat_renta_municipal.csv", low_memory=False, dtype={"ámbitos territoriales": str})
    muni = df[df["ámbitos territoriales"].astype(str).str.len().isin([4, 5])][
        ["ámbitos territoriales", "ámbitos territoriales__etiqueta"]
    ].drop_duplicates()
    # Excluir el agregado "C.A. de Euskadi" (codigo 00001, no es municipio) y
    # cualquier ambito que no pertenezca a una provincia valida (01/20/48).
    muni = muni[muni["ámbitos territoriales"].astype(str).str[:2].isin(["01", "20", "48"])]

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

    fot = leer_csv_seguro(RAW_DIR / "anuncios_fotocasa.csv")
    fot_mun = sorted(fot["municipio"].dropna().unique())

    # Variantes de alquiler municipal
    alq = leer_csv_seguro(RAW_DIR / "alquiler_municipal.csv")
    alq_mun = sorted(alq["municipio"].dropna().unique())

    # Variantes de Pisos (si existe)
    pisos_mun = []
    if (RAW_DIR / "anuncios_pisos.csv").exists():
        pisos = leer_csv_seguro(RAW_DIR / "anuncios_pisos.csv")
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

    # --- Tipologia de mercado municipal (clasificacion para analisis) ---
    import pandas as pd

    # Contar anuncios por codigo_ine en las 3 fuentes
    n_anuncios: dict[str, int] = {}
    for ruta, col in [
        (RAW_DIR / "anuncios_fotocasa.csv", "municipio"),
        (RAW_DIR / "anuncios_pisos.csv", "municipio_busqueda"),
        (RAW_DIR / "anuncios_realtyapi.csv", "municipio_busqueda"),
    ]:
        if not ruta.exists():
            continue
        try:
            dfa = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
            col_eff = col if col in dfa.columns else ("municipio" if "municipio" in dfa.columns else None)
            if col_eff is None:
                continue
            if "codigo_ine" not in dfa.columns:
                continue
            for _, row in dfa.iterrows():
                c = str(row.get("codigo_ine", "")).strip().zfill(5)
                if c and c.lower() not in ("nan", "none", ""):
                    n_anuncios[c] = n_anuncios.get(c, 0) + 1
        except Exception as exc:  # noqa: BLE001
            log.warning("No se pudo contar anuncios en %s: %s", ruta.name, exc)

    # Alquiler oficial disponible
    tiene_oficial: set[str] = set()
    ruta_alq = RAW_DIR / "alquiler_municipal.csv"
    if ruta_alq.exists():
        try:
            dfa = pd.read_csv(ruta_alq, dtype=str, encoding="utf-8-sig")
            if "codigo_ine" in dfa.columns:
                for c in dfa["codigo_ine"].dropna().astype(str):
                    tiene_oficial.add(c.strip().zfill(5))
        except Exception as exc:  # noqa: BLE001
            log.warning("No se pudo leer alquiler_municipal: %s", exc)

    # Fianzas EMAL (ultimo anio con fianzas > 0)
    tiene_fianzas: set[str] = set()
    ruta_emal = RAW_DIR / "emal_fianzas.csv"
    if ruta_emal.exists():
        try:
            dfe = pd.read_csv(ruta_emal, dtype=str, encoding="utf-8-sig")
            if "codigo_ine" in dfe.columns and "fianzas" in dfe.columns:
                dfe["fianzas_n"] = pd.to_numeric(dfe["fianzas"], errors="coerce")
                for c in dfe.loc[dfe["fianzas_n"].fillna(0) > 0, "codigo_ine"].dropna().astype(str):
                    tiene_fianzas.add(c.strip().zfill(5))
        except Exception as exc:  # noqa: BLE001
            log.warning("No se pudo leer emal_fianzas: %s", exc)

    for r in registros:
        c = str(r["codigo_ine"]).strip().zfill(5)
        na = n_anuncios.get(c, 0)
        tof = c in tiene_oficial
        tft = c in tiene_fianzas
        if na >= 30:
            tip = "Nivel1_Mercado_Dinamico"
        elif na >= 1 and (tof or tft):
            tip = "Nivel2_Mercado_Regulado"
        else:
            tip = "Nivel3_Mercado_Rural_Cerrado"
        r["n_anuncios"] = na
        r["tiene_alquiler_oficial"] = tof
        r["tiene_fianzas_emal"] = tft
        r["tipologia_mercado"] = tip

    log.info("Tipologia mercado: %s",
             {t: sum(1 for r in registros if r["tipologia_mercado"] == t) for t in
              ("Nivel1_Mercado_Dinamico", "Nivel2_Mercado_Regulado", "Nivel3_Mercado_Rural_Cerrado")})

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
        w.writerow(["codigo_ine", "nombre_canonico", "territorio", "nombre_normalizado", "variantes",
                    "n_anuncios", "tiene_alquiler_oficial", "tiene_fianzas_emal", "tipologia_mercado"])
        for r in registros:
            w.writerow([r["codigo_ine"], r["nombre_canonico"], r["territorio"], r["nombre_normalizado"], "|".join(r["variantes"]),
                        r.get("n_anuncios", 0), r.get("tiene_alquiler_oficial", False),
                        r.get("tiene_fianzas_emal", False), r.get("tipologia_mercado", "")])
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