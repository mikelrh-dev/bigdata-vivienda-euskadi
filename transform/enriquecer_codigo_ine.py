"""F0: enriquece las 4 fuentes con codigo_ine (sin re-scrapear, sin proxys).

Lee dim_municipios.csv como tabla de verdad y añade codigo_ine +
nombre_canonico + anio_fuente a:
  - alquiler_municipal.csv/.json
  - anuncios_fotocasa.csv/.json
  - anuncios_pisos.csv/.json (marca es_busqueda_no_ubicacion=True)
  - anuncios_realtyapi.csv/.json (usa municipio_busqueda preferente)

No elimina filas. Genera informe en data/procesado/informe_entity_resolution.csv.
Los originales se conservan con sufijo .bak_f0 una sola vez.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger  # noqa: E402
from entity_resolution import resolver_municipio  # noqa: E402
try:
    from _raw_guard import assert_raw_writable  # noqa: E402
except Exception:  # pragma: no cover
    from transform._raw_guard import assert_raw_writable  # noqa: E402

log = get_logger("f0_entity")
PROC = RAW_DIR.parent / "procesado"
PROC.mkdir(parents=True, exist_ok=True)

# Excepción de inmutabilidad: por defecto escribe en silver (data/procesado).
# Solo con --write-raw (y --reason) se permite escribir in-place en data/raw,
# previa comprobación de .FROZEN y --force. Documentado como excepción temporal.
FROZEN_MARKER = RAW_DIR / ".FROZEN"


def _check_frozen(force: bool) -> None:
    if FROZEN_MARKER.exists() and not force:
        log.error(
            "data/raw está CONGELADO (%s). Abortando para no modificar raw in place. "
            "Usa --force para override consciente.",
            FROZEN_MARKER,
        )
        raise SystemExit(2)


def _zfill(codigo) -> str | None:
    """Normaliza codigo_ine a 5 digitos (zfill) sin tocar nulos."""
    if codigo is None:
        return None
    s = str(codigo).strip()
    if s == "" or s.lower() in ("nan", "none", "null"):
        return None
    return s.zfill(5)


def _backup(ruta: Path) -> None:
    bak = ruta.with_suffix(ruta.suffix + ".bak_f0")
    if not bak.exists() and ruta.exists():
        shutil.copy2(ruta, bak)
        log.info("Backup %s", bak.name)


def _enriquecer_csv(ruta: Path, col_muni: str, anio: int | None, es_busqueda: bool = False,
                    destino: Path | None = None, sufijo: str = "") -> dict:
    import pandas as pd
    df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    # conservar columnas originales + añadir
    cods, cans = [], []
    for v in df[col_muni].tolist():
        c, n = resolver_municipio(v)
        cods.append(_zfill(c))
        cans.append(n)
    df["codigo_ine"] = cods
    df["nombre_canonico"] = cans
    if "anio_fuente" not in df.columns:
        df["anio_fuente"] = anio
    if es_busqueda and "es_busqueda_no_ubicacion" not in df.columns:
        df["es_busqueda_no_ubicacion"] = True
    if destino is None:
        destino = ruta
    else:
        destino = destino / (ruta.stem + sufijo + ruta.suffix)
    if destino == ruta:
        _backup(ruta)  # conservar original solo en legacy in-place
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    n_ok = int(df["codigo_ine"].notna().sum())
    no_res = sorted(df.loc[df["codigo_ine"].isna(), col_muni].dropna().unique().tolist())
    log.info("%s -> %s: %d/%d con codigo_ine. No resueltos: %s", ruta.name, destino.name, n_ok, len(df), no_res)
    return {"fichero": destino.name, "total": len(df), "con_codigo": n_ok,
            "sin_codigo": len(df) - n_ok, "no_resueltos": "|".join(no_res)}


def _enriquecer_json(ruta: Path, col_muni: str, anio: int | None, es_busqueda: bool = False,
                     destino: Path | None = None, sufijo: str = "") -> dict:
    data = json.loads(ruta.read_text(encoding="utf-8"))
    meta = data.get("metadata", {}) if isinstance(data, dict) else {}
    regs = data.get("datos", data) if isinstance(data, dict) else data
    if isinstance(regs, dict) and "filas" in regs:
        regs = regs["filas"]  # eustat-like, no tocar
        return {"fichero": ruta.name, "total": len(regs), "con_codigo": -1, "sin_codigo": -1, "no_resueltos": "OMITIDO"}
    for r in regs:
        if "codigo_ine" not in r or not r.get("codigo_ine"):
            c, n = resolver_municipio(r.get(col_muni))
            r["codigo_ine"] = _zfill(c)
            r["nombre_canonico_resuelto"] = n
        if anio and "anio_fuente" not in r:
            r["anio_fuente"] = anio
        if es_busqueda:
            r.setdefault("es_busqueda_no_ubicacion", True)
    if destino is None:
        destino = ruta
    else:
        destino = destino / (ruta.stem + sufijo + ruta.suffix)
    if destino == ruta:
        _backup(ruta)
    out = {"metadata": {**meta, "f0_entity_resolution": "codigo_ine añadido via dim_municipios (local, sin proxy)",
                        "anio_fuente_nota": anio}, "datos": regs} if isinstance(data, dict) else regs
    destino.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    n_ok = sum(1 for r in regs if r.get("codigo_ine"))
    no_res = sorted({str(r.get(col_muni)) for r in regs if not r.get("codigo_ine")})
    log.info("%s -> %s: %d/%d con codigo_ine. No resueltos: %s", ruta.name, destino.name, n_ok, len(regs), no_res)
    return {"fichero": destino.name, "total": len(regs), "con_codigo": n_ok,
            "sin_codigo": len(regs) - n_ok, "no_resueltos": "|".join(no_res)}


def main(force: bool = False, silver: bool = True, write_raw: bool = False,
        reason: str | None = None) -> int:
    if write_raw:
        if not reason or not str(reason).strip():
            log.error("Se requiere --reason para --write-raw. Abortando.")
            return 2
        assert_raw_writable(reason)
        silver = False
        _check_frozen(force)
        log.warning(
            "DEPRECACION: escritura in-place en data/raw (legacy). "
            "Preferir salida silver (default)."
        )
    else:
        silver = True
    if not silver:
        _check_frozen(force)
    dest_dir = (RAW_DIR.parent / "procesado") if silver else RAW_DIR
    sufijo = "_enriquecido" if silver else ""
    informe = []
    informe.append(_enriquecer_csv(RAW_DIR / "alquiler_municipal.csv", "municipio", 2024,
                                  destino=dest_dir, sufijo=sufijo))
    informe.append(_enriquecer_json(RAW_DIR / "alquiler_municipal.json", "municipio", 2024,
                                   destino=dest_dir, sufijo=sufijo))
    informe.append(_enriquecer_csv(RAW_DIR / "anuncios_fotocasa.csv", "municipio", 2026,
                                  destino=dest_dir, sufijo=sufijo))
    informe.append(_enriquecer_json(RAW_DIR / "anuncios_fotocasa.json", "municipio", 2026,
                                   destino=dest_dir, sufijo=sufijo))
    informe.append(_enriquecer_csv(RAW_DIR / "anuncios_pisos.csv", "municipio_busqueda", 2026, es_busqueda=True,
                                  destino=dest_dir, sufijo=sufijo))
    informe.append(_enriquecer_json(RAW_DIR / "anuncios_pisos.json", "municipio_busqueda", 2026, es_busqueda=True,
                                   destino=dest_dir, sufijo=sufijo))
    # RealtyAPI: preferir municipio_busqueda (canónico), fallback municipio
    import pandas as pd
    ruta = RAW_DIR / "anuncios_realtyapi.csv"
    dest_csv = (dest_dir / ("anuncios_realtyapi" + sufijo + ".csv")) if silver else ruta
    df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    cods, cans = [], []
    for _, row in df.iterrows():
        c, n = resolver_municipio(row.get("municipio_busqueda"))
        if not c:
            c, n = resolver_municipio(row.get("municipio"))
        cods.append(_zfill(c))
        cans.append(n)
    df["codigo_ine"] = cods
    df["nombre_canonico"] = cans
    if "anio_fuente" not in df.columns:
        df["anio_fuente"] = 2026
    if dest_csv == ruta:
        _backup(ruta)
    df.to_csv(dest_csv, index=False, encoding="utf-8-sig")
    informe.append({"fichero": dest_csv.name, "total": len(df), "con_codigo": int(df["codigo_ine"].notna().sum()),
                    "sin_codigo": int(df["codigo_ine"].isna().sum()), "no_resueltos": ""})
    rj = RAW_DIR / "anuncios_realtyapi.json"
    dest_json = (dest_dir / ("anuncios_realtyapi" + sufijo + ".json")) if silver else rj
    data = json.loads(rj.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    regs = data.get("datos", data)
    for r in regs:
        if not r.get("codigo_ine"):
            c, n = resolver_municipio(r.get("municipio_busqueda")) or (None, None)
            if not c:
                c, n = resolver_municipio(r.get("municipio"))
            r["codigo_ine"] = _zfill(c)
            r["nombre_canonico_resuelto"] = n
        r.setdefault("anio_fuente", 2026)
    if dest_json == rj:
        _backup(rj)
    dest_json.write_text(json.dumps({"metadata": {**meta, "f0_entity_resolution": "local sin proxy"}, "datos": regs},
                             ensure_ascii=False, indent=2), encoding="utf-8")
    informe.append({"fichero": dest_json.name, "total": len(regs),
                    "con_codigo": sum(1 for r in regs if r.get("codigo_ine")),
                    "sin_codigo": sum(1 for r in regs if not r.get("codigo_ine")), "no_resueltos": ""})

    with open(PROC / "informe_entity_resolution.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["fichero", "total", "con_codigo", "sin_codigo", "no_resueltos"])
        w.writeheader()
        w.writerows(informe)
    log.info("Informe -> %s", PROC / "informe_entity_resolution.csv")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Override raw congelado (no recomendado)")
    parser.add_argument("--silver", action="store_true", help="Compat: ya es el default (no-op)")
    parser.add_argument("--write-raw", action="store_true", help="Opt-in: escribir in-place en data/raw")
    parser.add_argument("--reason", default=None, help="Motivo para --write-raw (obligatorio)")
    args = parser.parse_args()
    raise SystemExit(main(force=args.force, silver=args.silver, write_raw=args.write_raw,
                         reason=args.reason))
