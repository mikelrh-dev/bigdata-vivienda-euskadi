"""F0: añade codigo_ine a las fuentes de anuncios y alquiler.

Lee ``procesado/dim_municipios.csv`` como tabla de verdad y escribe en
``procesado/``:

- alquiler_municipal_enriquecido.csv
- anuncios_fotocasa_enriquecido.json
- anuncios_pisos_enriquecido.json (marca es_busqueda_no_ubicacion=True)
- anuncios_realtyapi_enriquecido.json (usa municipio_busqueda preferente)

No elimina filas ni modifica ``raw``.
"""

from __future__ import annotations

import csv
import json
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR, RAW_DIR, get_logger  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from entity_resolution import MANUAL_MAP, norm  # noqa: E402

log = get_logger("f0_entity")


@lru_cache(maxsize=1)
def _mapa_municipios_silver() -> dict[str, tuple[str, str]]:
    """Construye el mapa enriquecido de Silver para la fase Transform."""
    ruta = PROCESADO_DIR / "dim_municipios.json"
    data = json.loads(ruta.read_text(encoding="utf-8"))
    registros = data.get("datos", data) if isinstance(data, dict) else data
    mapa: dict[str, tuple[str, str]] = {}
    for registro in registros:
        codigo = str(registro["codigo_ine"]).zfill(5)
        canonico = registro["nombre_canonico"]
        mapa[norm(canonico)] = (codigo, canonico)
        variantes = registro.get("variantes", []) or []
        if isinstance(variantes, str):
            variantes = variantes.split("|")
        for variante in variantes:
            if str(variante).strip():
                mapa.setdefault(norm(variante), (codigo, canonico))
    for alias, canonico in MANUAL_MAP.items():
        destino = mapa.get(norm(canonico))
        if destino:
            mapa.setdefault(alias, destino)
    return mapa


def resolver_municipio(nombre: str | None) -> tuple[str | None, str | None]:
    """Resuelve en la dimensión Silver ya generada por Transform."""
    if nombre is None or not str(nombre).strip():
        return None, None
    return _mapa_municipios_silver().get(norm(nombre), (None, None))


def _zfill(codigo) -> str | None:
    """Normaliza codigo_ine a 5 dígitos sin tocar nulos."""
    if codigo is None:
        return None
    s = str(codigo).strip()
    if s == "" or s.lower() in ("nan", "none", "null"):
        return None
    return s.zfill(5)


def _enriquecer_csv(ruta: Path, col_muni: str, anio: int, destino: Path) -> dict:
    import pandas as pd

    df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    cods, cans = [], []
    for v in df[col_muni].tolist():
        c, n = resolver_municipio(v)
        cods.append(_zfill(c))
        cans.append(n)
    df["codigo_ine"] = cods
    df["nombre_canonico"] = cans
    if "anio_fuente" not in df.columns:
        df["anio_fuente"] = anio
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    n_ok = int(df["codigo_ine"].notna().sum())
    no_res = sorted(df.loc[df["codigo_ine"].isna(), col_muni].dropna().unique().tolist())
    log.info("%s -> %s: %d/%d con codigo_ine. No resueltos: %s",
             ruta.name, destino.name, n_ok, len(df), no_res)
    return {"fichero": destino.name, "total": len(df), "con_codigo": n_ok,
            "sin_codigo": len(df) - n_ok, "no_resueltos": "|".join(no_res)}


def _enriquecer_json(ruta: Path, col_muni: str, anio: int, destino: Path,
                     es_busqueda: bool = False) -> dict:
    data = json.loads(ruta.read_text(encoding="utf-8"))
    meta = data.get("metadata", {}) if isinstance(data, dict) else {}
    regs = data.get("datos", data) if isinstance(data, dict) else data
    for r in regs:
        if not r.get("codigo_ine"):
            c, n = resolver_municipio(r.get(col_muni))
            r["codigo_ine"] = _zfill(c)
            r["nombre_canonico_resuelto"] = n
        r.setdefault("anio_fuente", anio)
        if es_busqueda:
            r.setdefault("es_busqueda_no_ubicacion", True)
    out = {"metadata": {**meta, "f0_entity_resolution": "codigo_ine añadido via dim_municipios"},
           "datos": regs}
    destino.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    n_ok = sum(1 for r in regs if r.get("codigo_ine"))
    no_res = sorted({str(r.get(col_muni)) for r in regs if not r.get("codigo_ine")})
    log.info("%s -> %s: %d/%d con codigo_ine. No resueltos: %s",
             ruta.name, destino.name, n_ok, len(regs), no_res)
    return {"fichero": destino.name, "total": len(regs), "con_codigo": n_ok,
            "sin_codigo": len(regs) - n_ok, "no_resueltos": "|".join(no_res)}


def main() -> int:
    PROCESADO_DIR.mkdir(parents=True, exist_ok=True)
    informe = [
        _enriquecer_csv(RAW_DIR / "alquiler_municipal.csv", "municipio", 2024,
                        PROCESADO_DIR / "alquiler_municipal_enriquecido.csv"),
        _enriquecer_json(RAW_DIR / "anuncios_fotocasa.json", "municipio", 2026,
                         PROCESADO_DIR / "anuncios_fotocasa_enriquecido.json"),
        _enriquecer_json(RAW_DIR / "anuncios_pisos.json", "municipio_busqueda", 2026,
                         PROCESADO_DIR / "anuncios_pisos_enriquecido.json",
                         es_busqueda=True),
    ]

    # RealtyAPI: preferir municipio_busqueda (canónico), fallback municipio.
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
    dest_json = PROCESADO_DIR / "anuncios_realtyapi_enriquecido.json"
    dest_json.write_text(
        json.dumps({"metadata": {**meta, "f0_entity_resolution": "local sin proxy"},
                    "datos": regs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    informe.append({"fichero": dest_json.name, "total": len(regs),
                    "con_codigo": sum(1 for r in regs if r.get("codigo_ine")),
                    "sin_codigo": sum(1 for r in regs if not r.get("codigo_ine")),
                    "no_resueltos": ""})

    ruta_informe = PROCESADO_DIR / "informe_entity_resolution.csv"
    with ruta_informe.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["fichero", "total", "con_codigo",
                                           "sin_codigo", "no_resueltos"])
        w.writeheader()
        w.writerows(informe)
    log.info("Informe -> %s", ruta_informe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
