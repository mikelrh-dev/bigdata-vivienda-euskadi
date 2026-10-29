"""Completa alquiler_municipal.csv para los 93 municipios sin dato oficial
usando imputacion espacial IDW (Inverse Distance Weighting) con los 5 vecinos
mas cercanos que si tienen dato oficial.

Genera: data/procesado/alquiler_municipal_completo.csv
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger  # noqa: E402

log = get_logger("completar_alquiler_comarca")

PROC_DIR = RAW_DIR.parent / "procesado"
PROC_DIR.mkdir(parents=True, exist_ok=True)

K_VECINOS = 5
POTENCIA = 2.0


def _cargar_dim() -> dict[str, dict]:
    dim = json.loads((RAW_DIR / "dim_municipios.json").read_text(encoding="utf-8"))
    regs = dim.get("datos", dim) if isinstance(dim, dict) else dim
    return {r["codigo_ine"]: r for r in regs}


def _cargar_distancias_capitales() -> dict[str, str]:
    result = {}
    with (RAW_DIR / "distancias_capitales.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            result[row["codigo_ine"]] = row.get("comarca", "")
    return result


def _cargar_alquiler() -> dict[str, dict]:
    result = {}
    with (RAW_DIR / "alquiler_municipal.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            muni = row["municipio"].strip()
            if muni not in result:
                result[muni] = row
    return result


def _cargar_haversine() -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    with (PROC_DIR / "distancias_haversine_252.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            try:
                out[(row["origen_codigo"], row["destino_codigo"])] = float(row["km_haversine"])
            except (ValueError, TypeError):
                continue
    return out


def _es_numero(v) -> bool:
    try:
        float(v)
        return True
    except (ValueError, TypeError):
        return False


def main() -> int:
    dim = _cargar_dim()
    dist_cap = _cargar_distancias_capitales()
    alquiler = _cargar_alquiler()
    hav = _cargar_haversine()

    codigo_a_nombre = {c: r["nombre_canonico"] for c, r in dim.items()}

    con_dato: set[str] = set()
    codigo_a_fila_oficial: dict[str, dict] = {}
    for codigo, info in dim.items():
        nombre = info["nombre_canonico"]
        row = alquiler.get(nombre)
        if row is not None:
            con_dato.add(codigo)
            codigo_a_fila_oficial[codigo] = row

    cols_numericas = [k for k in next(iter(codigo_a_fila_oficial.values())).keys()
                      if k not in ("territorio", "municipio", "distrito")]

    salida = []
    for codigo in sorted(dim.keys()):
        info = dim[codigo]
        nombre = info["nombre_canonico"]
        territorio = info.get("territorio", "")
        comarca = dist_cap.get(codigo, "")
        row = alquiler.get(nombre)

        if row is not None:
            fila = dict(row)
            fila["codigo_ine"] = codigo
            fila["nivel_geografico"] = "municipal"
            fila["metodo_imputacion"] = "oficial"
            salida.append(fila)
            continue

        vecinos = []
        for dest in con_dato:
            km = hav.get((codigo, dest))
            if km is None or km <= 0:
                continue
            vecinos.append((dest, km))
        vecinos.sort(key=lambda x: x[1])
        vecinos = vecinos[:K_VECINOS]

        pesos = [1.0 / (km ** POTENCIA) for _, km in vecinos]
        suma_pesos = sum(pesos)

        fila = {"territorio": territorio, "municipio": nombre, "distrito": "00 (IDW)"}
        fila["codigo_ine"] = codigo
        for col in cols_numericas:
            if suma_pesos == 0:
                fila[col] = None
                continue
            acc = 0.0
            wsum = 0.0
            for (dest, km), w in zip(vecinos, pesos):
                vrow = codigo_a_fila_oficial[dest]
                val = vrow.get(col)
                if not _es_numero(val):
                    continue
                acc += w * float(val)
                wsum += w
            fila[col] = round(acc / wsum, 2) if wsum > 0 else None

        fila["nivel_geografico"] = "comarcal"
        fila["metodo_imputacion"] = "IDW_5_vecinos"
        fila["idw_vecinos"] = ";".join(f"{codigo_a_nombre[d]}({km:.1f}km)" for d, km in vecinos)
        salida.append(fila)

    columnas = ["codigo_ine", "territorio", "municipio", "distrito", "nivel_geografico", "metodo_imputacion", "idw_vecinos"] + \
               [k for k in salida[0].keys() if k not in ("codigo_ine", "territorio", "municipio", "distrito",
                                                          "nivel_geografico", "metodo_imputacion", "idw_vecinos")]

    ruta_csv = PROC_DIR / "alquiler_municipal_completo.csv"
    with ruta_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(salida)

    n_municipal = sum(1 for r in salida if r.get("nivel_geografico") == "municipal")
    n_idw = sum(1 for r in salida if r.get("metodo_imputacion") == "IDW_5_vecinos")
    log.info("alquiler_municipal_completo: %d municipios (%d municipal, %d IDW)", len(salida), n_municipal, n_idw)
    log.info("CSV -> %s", ruta_csv.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
