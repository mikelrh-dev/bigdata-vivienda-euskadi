"""F4c: Pisos.com dirigido a top-40 municipios (captura opcional).

Lee opcionalmente raw/f4_pisos_objetivo.json (codigos INE), resuelve nombres
via dim_municipios, scrapea cada municipio con max 3 páginas y registra
resultado individual (OK/FALLO + n anuncios). Fusiona con los existentes
deduplicando por URL.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "extract"))
from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402
from entity_resolution import cargar_dim, resolver_municipio  # noqa: E402
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pisos_mod", Path(__file__).resolve().parent / "08_pisos_scraper.py")
pisos_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(pisos_mod)

log = get_logger("f4_pisos")
MAX_PAG = 3




def _nombre_lote(raw_dir) -> Path:
    raw_dir = Path(raw_dir)
    # WP-09: nombre estable (un lote vigente). La trazabilidad de lotes va en
    # metadata (run_id + contadores), no en el nombre. Los lotes historicos
    # con timestamp que ya existen en raw se conservan congelados.
    return Path(raw_dir) / "anuncios_pisos_dirigido_lote.json"


def _objetivos_raw() -> list[str]:
    """Replica el criterio de baja cobertura sin depender de una salida Silver."""
    fuentes = {
        "anuncios_fotocasa.json": "fotocasa",
        "anuncios_pisos.json": "pisos",
        "anuncios_realtyapi.json": "realtyapi",
    }
    total_por_codigo: dict[str, int] = {}
    fotocasa_por_codigo: dict[str, int] = {}
    for nombre, fuente in fuentes.items():
        ruta = RAW_DIR / nombre
        if not ruta.exists():
            continue
        payload = json.loads(ruta.read_text(encoding="utf-8"))
        anuncios = payload.get("datos", payload) if isinstance(payload, dict) else payload
        for anuncio in anuncios:
            codigo = anuncio.get("codigo_ine")
            if not codigo:
                codigo, _ = resolver_municipio(
                    anuncio.get("municipio_busqueda") or anuncio.get("municipio")
                )
            if not codigo:
                continue
            codigo = str(codigo).zfill(5)
            total_por_codigo[codigo] = total_por_codigo.get(codigo, 0) + 1
            if fuente == "fotocasa":
                fotocasa_por_codigo[codigo] = fotocasa_por_codigo.get(codigo, 0) + 1
    # La tipología silver clasifica como Nivel 1 los municipios con 30+
    # anuncios totales. Los Niveles 2/3 con menos de 5 anuncios Fotocasa son
    # los objetivos de la captura dirigida.
    return sorted(
        codigo for codigo in total_por_codigo
        if total_por_codigo[codigo] < 30 and fotocasa_por_codigo.get(codigo, 0) < 5
    )

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Pisos.com dirigido F4")
    parser.add_argument("--codigos", nargs="+", help="Limitar a códigos INE concretos")
    args = parser.parse_args()

    dim = cargar_dim()
    nombres = {
        str(r["codigo_ine"]).zfill(5): r["nombre_canonico"]
        for r in dim.to_dict(orient="records")
    }
    # La selección la prepara el flujo de calidad/transformación; se lee como
    # configuración de esta captura, pero nunca se escribe en procesado.
    objetivos_path = RAW_DIR / "f4_pisos_objetivo.json"
    if objetivos_path.exists():
        objetivos = json.loads(objetivos_path.read_text(encoding="utf-8"))
    else:
        objetivos = _objetivos_raw()
        log.info("Objetivos derivados desde raw: %d municipios", len(objetivos))
    if args.codigos:
        pedidos = set(args.codigos)
        desconocidos = sorted(pedidos - set(nombres))
        if desconocidos:
            parser.error(f"Códigos INE desconocidos: {', '.join(desconocidos)}")
        objetivos = list(dict.fromkeys(args.codigos))
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
    # Los reintentos dirigidos llevan nombre propio para no reemplazar el lote
    # F4 completo que sirve como evidencia histórica.
    raw_path = _nombre_lote(RAW_DIR)
    from datetime import datetime, timezone  # noqa: E402
    if args.codigos:
        raw_path = RAW_DIR / (
            f"anuncios_pisos_dirigido_reintento_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        )
    guardar_json(raw_path, nuevos, metadata={
        "fuente": "Pisos.com dirigido F4",
        "url": "https://www.pisos.com/alquiler/",
        "fecha_extraccion": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "n_anuncios": len(nuevos),
        "n_registros": len(nuevos),
        "municipios_objetivo": len(objetivos),
        "run_id": f"f4-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
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
    guardar_json(RAW_DIR / "anuncios_pisos_dirigido.json", viejos,
                 metadata={**meta, "f4_nuevos": añadidos,
                           "f4_municipios": len(objetivos)})
    for fila in informe:
        log.info("  %s [%s]: %s", fila["municipio"], fila["codigo_ine"], fila["estado"])
    log.info("F4c: %d nuevos (total %d)", añadidos, len(viejos))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
