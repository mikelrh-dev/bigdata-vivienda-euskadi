"""F17: tiempos reales de conduccion a capitales via OSRM (API publica, sin key).

Consulta el endpoint publico http://router.project-osrm.org/table/v1/driving/
para obtener minutos de coche desde cada uno de los 252 municipios a las
3 capitales (Vitoria, Bilbao, Donostia). Guarda CSV + JSON.

Metodo: API (sin scraping, sin descarga de ficheros grandes).
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("osrm_tiempos")
OSRM = "http://router.project-osrm.org/table/v1/driving/"
CAPITALES = {
    "Vitoria-Gasteiz": (42.8467, -2.6716),
    "Bilbao": (43.2630, -2.9350),
    "Donostia-San Sebastian": (43.3183, -1.9812),
}
CHUNK = 40


def _chunk(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _table(coords_batch, dest):
    # coords: list of (lat, lon); dest: (lat, lon)
    # OSRM expects lon,lat
    parts = [f"{lon},{lat}" for lat, lon in coords_batch] + [f"{dest[1]},{dest[0]}"]
    url = OSRM + ";".join(parts)
    params = f"?sources={';'.join(str(i) for i in range(len(coords_batch)))}&destinations={len(coords_batch)}&annotations=duration"
    import urllib.request
    with urllib.request.urlopen(url + params, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM error: {data}")
    # durations[i][0] seconds
    return [row[0] for row in data["durations"]]


def main() -> int:
    import pandas as pd

    dim = pd.read_csv(RAW_DIR / "distancias_capitales_252.csv", dtype=str, encoding="utf-8-sig")
    cods = dim["codigo_ine"].str.zfill(5).tolist()
    coords = list(zip(dim["centroide_lat"].astype(float), dim["centroide_lon"].astype(float)))

    resultado = {c: {} for c in cods}
    for nombre_cap, dest in CAPITALES.items():
        log.info("Consultando OSRM para %s (%d municipios)", nombre_cap, len(cods))
        duraciones = [None] * len(cods)
        for idxs in _chunk(list(range(len(cods))), CHUNK):
            batch_coords = [coords[i] for i in idxs]
            try:
                durs = _table(batch_coords, dest)
                for j, i in enumerate(idxs):
                    duraciones[i] = durs[j]
                time.sleep(1.0)  # cortesia al servidor publico
            except Exception as exc:  # noqa: BLE001
                log.warning("Chunk %s fallo: %s", idxs[:3], exc)
                time.sleep(2.0)
        for i, c in enumerate(cods):
            d = duraciones[i]
            resultado[c][f"minutos_{nombre_cap}"] = (round(d / 60.0, 1) if d is not None else None)

    # Guardar CSV
    out_csv = RAW_DIR / "osrm_tiempos_capitales.csv"
    with out_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["codigo_ine"] + [f"minutos_{k}" for k in CAPITALES])
        for c in cods:
            w.writerow([c] + [resultado[c][f"minutos_{k}"] for k in CAPITALES])
    log.info("CSV -> %s", out_csv.name)

    # Guardar JSON
    regs = [{"codigo_ine": c, **resultado[c]} for c in cods]
    guardar_json(RAW_DIR / "osrm_tiempos_capitales.json", regs,
                metadata={"fuente": "OSRM public API (router.project-osrm.org)",
                          "capitales": list(CAPITALES.keys()),
                          "n_municipios": len(cods),
                          "nota": "Minutos de conduccion (sin trafico en tiempo real)."})
    log.info("JSON -> osrm_tiempos_capitales.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())