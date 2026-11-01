"""Normaliza la metadata de los 60 JSON de raw a un esquema unico (WP-07).

NO reescribe data/raw (congelado). Para cada JSON genera un sidecar en
data/procesado/_meta/<nombre>.meta.json con los 6 campos obligatorios
(fuente, url, fecha_extraccion, n_registros, hash_sha256, version_parser),
normalizando los alias historicos (fecha, n_filas, n_anuncios, n_series...),
mas data/procesado/_meta/index.json con el estado de cada fichero.

Uso:
    python extract/normalizar_metadata.py            # genera sidecars + indice
    python extract/normalizar_metadata.py --check    # exit 1 si algo incumple
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "extract"))

from _common import REQUIRED_METADATA  # noqa: E402

RAW_DIR = PROJECT_ROOT / "data" / "raw"
META_DIR = PROJECT_ROOT / "data" / "procesado" / "_meta"

ALIASES_FECHA = ("fecha_extraccion", "fecha", "fecha_descarga")
ALIASES_RECUENTO = ("n_registros", "n_filas", "n_anuncios", "n_series",
                    "n_municipios", "n_items", "n_sin_duplicar")
ALIASES_URL = ("url", "url_fuente", "fuente_url")
# WP-18: ficheros legacy congelados sin envoltura {"metadata","datos"}.
# Se rescata su procedencia desde las claves escalares de nivel superior
# (solo lectura de raw; la canonica vive en el sidecar de _meta).
ALIASES_FUENTE = ("fuente", "origen", "descripcion")
# WP-18: procedencia conocida de ficheros legacy congelados cuya unica
# carencia es la fuente (url/fecha/recuento se rescatan del propio fichero).
# No reescribe raw; solo completa el sidecar canonico de _meta.
FUENTES_LEGACY = {
    "emancipacion_juventud_resumen.json":
        "Gobierno Vasco - Observatorio Vasco de la Juventud (opendata euskadi.eus)",
    "b5m_catalogo.json":
        "B5M - Diputacion Foral de Gipuzkoa (b5m.gipuzkoa.eus)",
}


def _primero(meta: dict, claves: tuple[str, ...]):
    for k in claves:
        if meta.get(k) not in (None, "", []):
            return meta[k], k
    return None, None


def _normalizar(ruta: Path) -> tuple[dict, list[str]]:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    cuerpo = datos.get("datos", datos) if isinstance(datos, dict) else datos
    meta = dict(datos.get("metadata", {})) if isinstance(datos, dict) else {}
    incidencias = []
    if not isinstance(datos, dict) or "metadata" not in datos:
        incidencias.append("sin-bloque-metadata")
        if isinstance(datos, dict):  # WP-18: rescate legacy top-level
            for k, v in datos.items():
                if k != "datos" and not isinstance(v, (dict, list)):
                    meta.setdefault(k, v)

    fuente, _ = _primero(meta, ALIASES_FUENTE)
    if not fuente:
        fuente = FUENTES_LEGACY.get(ruta.name)
        if fuente:
            incidencias.append("fuente-rescatada-legacy")
    if not fuente:
        incidencias.append("sin-fuente")
    url, _ = _primero(meta, ALIASES_URL)
    if not url:
        incidencias.append("sin-url")
    fecha, _ = _primero(meta, ALIASES_FECHA)
    if not fecha:
        incidencias.append("sin-fecha")
    recuento, clave_rec = _primero(meta, ALIASES_RECUENTO)
    if recuento is None and isinstance(cuerpo, list):
        # Rescate honesto: contar filas presentes (no se inventa procedencia,
        # se cuenta lo que hay; la coherencia se valida debajo).
        recuento, clave_rec = len(cuerpo), "contado-desde-datos"
        incidencias.append("recuento-contado")
    if recuento is None:
        incidencias.append("sin-recuento")
    if (isinstance(cuerpo, list) and isinstance(recuento, int)
            and recuento != len(cuerpo)):
        incidencias.append(f"recuento-incoherente:{recuento}!={len(cuerpo)}")

    normalizada = {
        "fuente": fuente,
        "url": url,
        "fecha_extraccion": fecha,
        "n_registros": recuento,
        "n_registros_detalle": ({clave_rec: recuento} if clave_rec
                                and clave_rec != "n_registros" else {}),
        "hash_sha256": hashlib.sha256(
            json.dumps(cuerpo, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest(),
        "version_parser": meta.get("version_parser", "1"),
        "fichero": ruta.name,
        "incidencias": incidencias,
    }
    faltan = [k for k in REQUIRED_METADATA if normalizada.get(k) in (None, "", [])]
    normalizada["completa"] = not faltan
    return normalizada, faltan


def main() -> int:
    ap = argparse.ArgumentParser(description="Normaliza metadata JSON a esquema unico.")
    ap.add_argument("--check", action="store_true",
                    help="Solo comprobar, sin escribir.")
    args = ap.parse_args()

    ficheros = sorted(RAW_DIR.rglob("*.json"))
    indice, incompletos = [], 0
    for f in ficheros:
        try:
            norm, _ = _normalizar(f)
        except Exception as exc:  # noqa: BLE001
            norm = {"fichero": f.name, "completa": False,
                    "incidencias": [f"no-parsea:{type(exc).__name__}"]}
        indice.append(norm)
        if not norm["completa"]:
            incompletos += 1

    if not args.check:
        META_DIR.mkdir(parents=True, exist_ok=True)
        for norm in indice:
            (META_DIR / (norm["fichero"] + ".meta.json")).write_text(
                json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
        (META_DIR / "index.json").write_text(
            json.dumps({"n_ficheros": len(indice),
                        "completos": sum(1 for n in indice if n["completa"]),
                        "ficheros": indice}, ensure_ascii=False, indent=2),
            encoding="utf-8")

    completos = sum(1 for n in indice if n["completa"])
    print(f"JSON: {len(indice)} | metadata completa: {completos} | "
          f"incompletos: {incompletos}")
    for n in indice:
        if not n["completa"]:
            print(f"  - {n['fichero']}: {', '.join(n['incidencias'])}")
    return 1 if incompletos else 0


if __name__ == "__main__":
    raise SystemExit(main())
