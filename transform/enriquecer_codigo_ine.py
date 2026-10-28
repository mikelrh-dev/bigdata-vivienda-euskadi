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

import csv
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from _common import RAW_DIR, get_logger  # noqa: E402
from entity_resolution import resolver_municipio  # noqa: E402

log = get_logger("f0_entity")
PROC = RAW_DIR.parent / "procesado"
PROC.mkdir(parents=True, exist_ok=True)


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


def _enriquecer_csv(ruta: Path, col_muni: str, anio: int | None, es_busqueda: bool = False) -> dict:
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
    _backup(ruta)
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    n_ok = int(df["codigo_ine"].notna().sum())
    no_res = sorted(df.loc[df["codigo_ine"].isna(), col_muni].dropna().unique().tolist())
    log.info("%s: %d/%d con codigo_ine. No resueltos: %s", ruta.name, n_ok, len(df), no_res)
    return {"fichero": ruta.name, "total": len(df), "con_codigo": n_ok,
            "sin_codigo": len(df) - n_ok, "no_resueltos": "|".join(no_res)}


def _enriquecer_json(ruta: Path, col_muni: str, anio: int | None, es_busqueda: bool = False) -> dict:
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
    _backup(ruta)
    out = {"metadata": {**meta, "f0_entity_resolution": "codigo_ine añadido via dim_municipios (local, sin proxy)",
                        "anio_fuente_nota": anio}, "datos": regs} if isinstance(data, dict) else regs
    ruta.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    n_ok = sum(1 for r in regs if r.get("codigo_ine"))
    no_res = sorted({str(r.get(col_muni)) for r in regs if not r.get("codigo_ine")})
    log.info("%s: %d/%d con codigo_ine. No resueltos: %s", ruta.name, n_ok, len(regs), no_res)
    return {"fichero": ruta.name, "total": len(regs), "con_codigo": n_ok,
            "sin_codigo": len(regs) - n_ok, "no_resueltos": "|".join(no_res)}


def main() -> int:
    informe = []
    informe.append(_enriquecer_csv(RAW_DIR / "alquiler_municipal.csv", "municipio", 2024))
    informe.append(_enriquecer_json(RAW_DIR / "alquiler_municipal.json", "municipio", 2024))
    informe.append(_enriquecer_csv(RAW_DIR / "anuncios_fotocasa.csv", "municipio", 2026))
    informe.append(_enriquecer_json(RAW_DIR / "anuncios_fotocasa.json", "municipio", 2026))
    informe.append(_enriquecer_csv(RAW_DIR / "anuncios_pisos.csv", "municipio_busqueda", 2026, es_busqueda=True))
    informe.append(_enriquecer_json(RAW_DIR / "anuncios_pisos.json", "municipio_busqueda", 2026, es_busqueda=True))
    # RealtyAPI: preferir municipio_busqueda (canónico), fallback municipio
    import pandas as pd
    ruta = RAW_DIR / "anuncios_realtyapi.csv"
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
    _backup(ruta)
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    informe.append({"fichero": ruta.name, "total": len(df), "con_codigo": int(df["codigo_ine"].notna().sum()),
                    "sin_codigo": int(df["codigo_ine"].isna().sum()), "no_resueltos": ""})
    rj = RAW_DIR / "anuncios_realtyapi.json"
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
    _backup(rj)
    rj.write_text(json.dumps({"metadata": {**meta, "f0_entity_resolution": "local sin proxy"}, "datos": regs},
                             ensure_ascii=False, indent=2), encoding="utf-8")
    informe.append({"fichero": rj.name, "total": len(regs),
                    "con_codigo": sum(1 for r in regs if r.get("codigo_ine")),
                    "sin_codigo": sum(1 for r in regs if not r.get("codigo_ine")), "no_resueltos": ""})

    with open(PROC / "informe_entity_resolution.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["fichero", "total", "con_codigo", "sin_codigo", "no_resueltos"])
        w.writeheader()
        w.writerows(informe)
    log.info("Informe -> %s", PROC / "informe_entity_resolution.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
