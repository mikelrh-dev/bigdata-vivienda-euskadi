"""Filtrado heuristico de outliers en anuncios de alquiler (Fotocasa + Pisos.com).

Marca (no elimina) anuncios con valores fuera de rango razonable:
  - precio_m2 < 3 o > 50  -> outlier = true
  - superficie_m2 < 10 o > 500 -> outlier = true

MOTIVO canonical (M1 OUTLIER-01, aditivos a los motivos legacy):
  - `motivo_exclusion`: `precio_m2_fuera_3_50` / `superficie_fuera_10_500` /
    `iqr_excluido` (precio_m2 dentro de [3, 50] pero fuera del IQR).
    Los valores fuera de rango se descartan con motivo, nunca se recortan
    ni winsorizan en esta capa.
  - `habitaciones` se castea a entero (`2,5` -> `2`).

Genera:
  - data/procesado/anuncios_fotocasa_filtrado.json / .csv
  - data/procesado/anuncios_pisos_filtrado.json / .csv
  - data/procesado/log_filtrado.txt (conteos por motivo)

Los originales en data/raw/ no se modifican.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR, RAW_DIR, get_logger, guardar_json  # noqa: E402

log = get_logger("filtrar_outliers")

PROC_DIR = PROCESADO_DIR
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


def _habitaciones_int(v) -> int | None:
    try:
        return int(float(v)) if v is not None and str(v).strip() not in ("", "nan", "None") else None
    except (ValueError, TypeError):
        return None


def _filtrar(anuncios: list[dict]) -> list[dict]:
    # Primera pasada: calcular precio_m2 y tipo_alquiler
    preparados = []
    for a in anuncios:
        copia = dict(a)
        precio_m2 = _calcular_precio_m2(copia)
        if precio_m2 is not None:
            copia["precio_m2_calculado"] = precio_m2
        else:
            copia["precio_m2_calculado"] = copia.get("precio_m2")

        if "alquiler_temporal" in copia:
            copia["tipo_alquiler"] = "temporal" if copia.get("alquiler_temporal") else "larga_estancia"
        else:
            copia["tipo_alquiler"] = "desconocido"
        # M1 OUTLIER-01: habitaciones siempre entera (2,5 -> 2).
        if "habitaciones" in copia:
            copia["habitaciones"] = _habitaciones_int(copia.get("habitaciones"))
        preparados.append(copia)

    # Limites IQR por segmento
    grupos: dict[str, list[float]] = {}
    for c in preparados:
        pm2 = c.get("precio_m2_calculado")
        if pm2 is None:
            continue
        try:
            grupos.setdefault(c["tipo_alquiler"], []).append(float(pm2))
        except (ValueError, TypeError):
            pass

    limites_iqr: dict[str, tuple[float, float]] = {}
    for grupo, vals in grupos.items():
        if len(vals) < 4:
            continue
        vals_sorted = sorted(vals)
        n = len(vals_sorted)
        q1 = vals_sorted[n // 4]
        q3 = vals_sorted[(3 * n) // 4]
        iqr = q3 - q1
        if iqr <= 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        limites_iqr[grupo] = (lower, upper)

    resultado = []
    for copia in preparados:
        outlier = False
        motivos = []
        motivos_excl = []
        pm2_fuera = False
        sup_fuera = False
        iqr_excl = False

        pm2 = copia.get("precio_m2_calculado")
        if pm2 is not None:
            try:
                v = float(pm2)
                # Guarda exterior (compatibilidad con test_filtrar_outliers_validos)
                if v < PRECIO_M2_MIN:
                    outlier = True
                    motivos.append("precio_m2_bajo")
                    pm2_fuera = True
                if v > PRECIO_M2_MAX:
                    outlier = True
                    motivos.append("precio_m2_alto")
                    pm2_fuera = True
                if pm2_fuera:
                    motivos_excl.append("precio_m2_fuera_3_50")
                elif True:
                    # IQR por segmento: solo excluye del precio_medio si ya
                    # esta dentro de [3, 50] (OUTLIER-01).
                    lim = limites_iqr.get(copia["tipo_alquiler"])
                    if lim is not None:
                        lo, hi = lim
                        if v < lo:
                            outlier = True
                            motivos.append("precio_m2_iqr_bajo")
                            iqr_excl = True
                        if v > hi:
                            outlier = True
                            motivos.append("precio_m2_iqr_alto")
                            iqr_excl = True
                    if iqr_excl:
                        motivos_excl.append("iqr_excluido")
            except (ValueError, TypeError):
                pass

        sup = copia.get("superficie_m2") or copia.get("superficie")
        if sup is not None:
            try:
                s = float(sup)
                if s < SUPERFICIE_MIN:
                    outlier = True
                    motivos.append("superficie_baja")
                    sup_fuera = True
                if s > SUPERFICIE_MAX:
                    outlier = True
                    motivos.append("superficie_alta")
                    sup_fuera = True
                if sup_fuera:
                    motivos_excl.append("superficie_fuera_10_500")
            except (ValueError, TypeError):
                pass

        copia["outlier"] = outlier
        copia["motivo_outlier"] = ";".join(motivos) if motivos else ""
        # M1 OUTLIER-01: motivo canonical + flags por motivo (nunca recorte).
        copia["motivo_exclusion"] = ";".join(motivos_excl) if motivos_excl else ""
        copia["precio_m2_fuera_3_50"] = bool(pm2_fuera)
        copia["superficie_fuera_10_500"] = bool(sup_fuera)
        copia["iqr_excluido"] = bool(iqr_excl)
        # guardar limites aplicados (trazabilidad)
        lim = limites_iqr.get(copia["tipo_alquiler"])
        if lim is not None:
            copia["iqr_lower"] = round(lim[0], 2)
            copia["iqr_upper"] = round(lim[1], 2)
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
            "fecha": "2026-10-30T00:00:00",
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
    tot_pm2 = tot_sup = tot_iqr = tot_int_ok = tot_hab = 0
    lineas_log = []
    for nombre_json, nombre_base in [
        ("anuncios_fotocasa.json", "anuncios_fotocasa"),
        ("anuncios_pisos.json", "anuncios_pisos"),
    ]:
        anuncios = _cargar_anuncios(nombre_json)
        if not anuncios:
            continue
        filtrados = _filtrar(anuncios)
        n_out = sum(1 for a in filtrados if a.get("outlier"))
        n_pm2 = sum(1 for a in filtrados if a.get("precio_m2_fuera_3_50"))
        n_sup = sum(1 for a in filtrados if a.get("superficie_fuera_10_500"))
        n_iqr = sum(1 for a in filtrados if a.get("iqr_excluido"))
        n_hab = sum(1 for a in filtrados if a.get("habitaciones") is not None)
        n_int = sum(1 for a in filtrados if isinstance(a.get("habitaciones"), int))
        tot_pm2 += n_pm2
        tot_sup += n_sup
        tot_iqr += n_iqr
        tot_int_ok += n_int
        tot_hab += n_hab
        log.info("%s: %d anuncios, %d outliers", nombre_base, len(filtrados), n_out)
        log.info("excluidos_precio_m2=%d, excluidos_superficie=%d, "
                 "excluidos_iqr_precio_medio=%d, habitaciones_int=%s"
                 % (n_pm2, n_sup, n_iqr,
                    "100%" if n_hab and n_int == n_hab else
                    (f"{n_int}/{n_hab}" if n_hab else "sin datos")))
        for a in filtrados:
            if a.get("motivo_exclusion"):
                lineas_log.append(
                    f"{nombre_base} id={a.get('id_anuncio')} motivo={a.get('motivo_exclusion')}")
        _guardar(nombre_base, filtrados)

    # OUTLIER-01: log de filtrado con conteos por motivo (grep iqr_excluido).
    ruta_log = PROC_DIR / "log_filtrado.txt"
    with ruta_log.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"excluidos_precio_m2={tot_pm2}, excluidos_superficie={tot_sup}, "
                 f"excluidos_iqr_precio_medio={tot_iqr}, "
                 f"habitaciones_int={'100%' if tot_hab and tot_int_ok == tot_hab else f'{tot_int_ok}/{tot_hab}'}\n")
        for ln in lineas_log:
            fh.write(ln + "\n")
    print(f"excluidos_precio_m2={tot_pm2}, excluidos_superficie={tot_sup}, "
          f"excluidos_iqr_precio_medio={tot_iqr}, "
          f"habitaciones_int={'100%' if tot_hab and tot_int_ok == tot_hab else f'{tot_int_ok}/{tot_hab}'}")
    log.info("P1a completado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
