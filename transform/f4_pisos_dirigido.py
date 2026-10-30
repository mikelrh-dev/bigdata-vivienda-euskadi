"""F4c: Pisos.com dirigido a top-40 municipios (lento, sin proxy, revisión 1x1).

Lee data/procesado/f4_pisos_objetivo.json (codigos INE), resuelve nombres
via dim_municipios, scrapea cada municipio con max 3 páginas y registra
resultado individual (OK/FALLO + n anuncios). Fusiona con los existentes
deduplicando por URL.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402
from entity_resolution import resolver_municipio  # noqa: E402
try:
    from _raw_guard import assert_raw_writable  # noqa: E402
except Exception:  # pragma: no cover
    from transform._raw_guard import assert_raw_writable  # noqa: E402
from importlib import import_module as _imp
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pisos_mod", Path(__file__).resolve().parent.parent / "extract" / "08_pisos_scraper.py")
pisos_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(pisos_mod)

log = get_logger("f4_pisos")
PROC_DIR = RAW_DIR.parent / "procesado"
PROC_DIR.mkdir(parents=True, exist_ok=True)
MAX_PAG = 3


import hashlib
import itertools

_LOTE_COUNTER = itertools.count()


def _nombre_lote(raw_dir) -> Path:
    raw_dir = Path(raw_dir)
    # Determinista: base fija + contador monotónico (sin datetime.now/uuid.uuid4).
    # Se evita colisión comprobando existencia y avanzando el contador.
    while True:
        n = next(_LOTE_COUNTER)
        ts = f"{20261030000000 + n:014d}"
        token = hashlib.sha256(f"lote:{n}".encode("utf-8")).hexdigest()[:8]
        path = raw_dir / f"anuncios_pisos_dirigido_{ts}_{token}.json"
        if not path.exists():
            return path

def main() -> int:
    dim = json.loads((RAW_DIR / "dim_municipios.json").read_text(encoding="utf-8"))
    regs = dim["datos"] if isinstance(dim, dict) else dim
    nombres = {r["codigo_ine"]: r["nombre_canonico"] for r in regs}
    objetivos = json.loads((RAW_DIR.parent / "procesado" / "f4_pisos_objetivo.json").read_text())
    cliente = Cliente("pisos_f4", delay=3.0, reintentos=2)
    informe, nuevos = [], []
    for cod in objetivos:
        nombre = nombres.get(cod, cod)
        try:
            lote = pisos_mod.scrapear_municipio(cliente, nombre, MAX_PAG)
            nuevos.extend(lote)
            estado = f"OK n={len(lote)} total_portal={lote[0].get('total_resultados') if lote else '-'}"
        except Exception as exc:  # noqa: BLE001
            lote = []
            estado = f"FALLO: {type(exc).__name__}: {exc}"
        log.info("%s [%s]: %s", nombre, cod, estado)
        informe.append({"codigo_ine": cod, "municipio": nombre, "estado": estado})
    # Guardar lote nuevo en raw (append-only, no sobrescribir existentes)
    assert_raw_writable("f4 directed scrape lot")
    raw_path = _nombre_lote(RAW_DIR)
    guardar_json(raw_path, nuevos, metadata={
        "fuente": "Pisos.com dirigido F4",
        "fecha_extraccion": "2026-10-30T00:00:00",
        "n_anuncios": len(nuevos),
        "municipios_objetivo": len(objetivos),
    })
    log.info("Lote nuevo guardado en raw: %s (%d anuncios)", raw_path.name, len(nuevos))

    # fusionar con existentes
    data = json.loads((RAW_DIR / "anuncios_pisos.json").read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    viejos = data.get("datos", data)
    vistos = {(a.get("url_detalle") or a.get("id_anuncio")) for a in viejos}
    añadidos = 0
    for a in nuevos:
        clave = a.get("url_detalle") or a.get("id_anuncio")
        if clave in vistos:
            continue
        vistos.add(clave)
        viejos.append(a)
        añadidos += 1
    guardar_json(PROC_DIR / "anuncios_pisos_dirigido.json", viejos,
                 metadata={**meta, "f4_nuevos": añadidos,
                           "f4_municipios": len(objetivos)})
    cols = ["codigo_ine", "nombre_canonico", "anio_fuente", "id_anuncio", "precio_eur",
            "municipio_busqueda", "titulo", "subtitulo", "tipo_inmueble", "superficie_m2",
            "habitaciones", "banos", "url_detalle", "total_resultados", "es_busqueda_no_ubicacion"]
    with open(PROC_DIR / "anuncios_pisos_dirigido.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(viejos)
    with open(RAW_DIR.parent / "procesado" / "f4_pisos_informe.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["codigo_ine", "municipio", "estado"])
        w.writeheader(); w.writerows(informe)
    log.info("F4c: %d nuevos (total %d). Informe 1x1 en procesado/f4_pisos_informe.csv",
             añadidos, len(viejos))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
