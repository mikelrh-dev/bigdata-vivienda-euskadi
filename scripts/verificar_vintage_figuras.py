"""Verifica que cada figura publicada declara su vintage (año) y lo lleva dentro.

Tres comprobaciones sobre artefactos reales, no sobre el codigo fuente:

  1. Cobertura: todo PNG de gold (`data/resultados` + `anexo/`), todo asset del
     deck, toda copia del README y toda figura de la memoria tiene entrada en
     `config/vintage_figuras.yaml`.
  2. Sello: el PNG lleva los chunks de texto `Figura`, `Vintage` y
     `Description` con el valor declarado. Sin OCR: se leen con Pillow.
  3. Coherencia con `config/comparabilidad.yaml`: una figura que mezcla
     `anuncios` (2026) con una fuente 2024 no puede declararse de un solo año
     salvo que marque `muestra_2026: true` (los anuncios solo filtran la muestra).

No escribe nada. Uso:

    python scripts/verificar_vintage_figuras.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis import comparabilidad  # noqa: E402
from analysis.vintage_figuras import (
    CONFIG,
    ROOT as BASE,
    _config,
    codigo,
    etiqueta,
    etiqueta_declarada,
    figuras,
    rango_etxebide,
)

RES = BASE / "data" / "resultados"
ANEXO = RES / "anexo"
ASSETS = BASE / "docs" / "presentacion_v2" / "assets"
MEM_FIG = BASE / "docs" / "memoria" / "figuras"
README_ASSETS = BASE / "docs" / "assets" / "readme"
# Salida intermedia de la capa 2026 (antes de copiarse a assets/).
VIS_2026 = BASE / "visuals" / "esfuerzo_mercado_2026"

# Diagramas de arquitectura/modelo: no son figuras de datos.
MEM_SIN_DATOS = frozenset({"fig-arquitectura.png", "fig-modelo.png"})

CODIGOS_VALIDOS = frozenset({"2024", "2026", "mixto", "flujo", "acumulado", "sin-fecha"})

# Fuentes 2024 frente a la unica fuente 2026 de oferta.
FUENTES_2024 = frozenset(
    {"alquiler_oficial", "renta", "paro_udalmap", "udalmap", "etxebide_2024"}
)
FUENTES_2026 = frozenset({"anuncios", "salario_2026", "gtfs"})


def _pngs(carpeta: Path) -> list[Path]:
    if not carpeta.is_dir():
        return []
    return sorted(p for p in carpeta.glob("*.png"))


def _leer_metadatos(ruta: Path) -> dict[str, str]:
    try:
        from PIL import Image

        with Image.open(ruta) as im:
            return {
                k: v
                for k, v in (im.info or {}).items()
                if isinstance(v, str)
                and k in {"Figura", "Vintage", "Description", "Solapes"}
            }
    except Exception as exc:  # noqa: BLE001
        return {"_error": repr(exc)}


def main() -> int:
    errores: list[str] = []
    avisos: list[str] = []

    declaradas = figuras()
    if not declaradas:
        print(f"FALLO: {CONFIG.name} no declara ninguna figura")
        return 1

    # ---------------------------------------------------------- 1. cobertura
    en_disco: dict[str, Path] = {}
    for carpeta in (RES, ANEXO):
        for png in _pngs(carpeta):
            en_disco.setdefault(png.name, png)

    for nombre, ruta in en_disco.items():
        if nombre not in declaradas:
            errores.append(f"gold sin vintage declarado: {ruta.relative_to(BASE)}")
        elif nombre in _pngs(ANEXO) and nombre not in declaradas:
            errores.append(f"anexo sin vintage declarado: {nombre}")

    for png in _pngs(ASSETS):
        if png.name not in declaradas:
            errores.append(f"asset del deck sin vintage declarado: {png.name}")

    for png in _pngs(README_ASSETS):
        if png.name not in declaradas:
            errores.append(f"asset del README sin vintage declarado: {png.name}")

    memoria_cfg = (_config().get("sincronizacion") or {}).get("memoria") or {}
    for png in _pngs(MEM_FIG):
        if not png.name.startswith("fig-") or png.name in MEM_SIN_DATOS:
            continue
        if png.name in memoria_cfg:
            continue
        avisos.append(f"figura de memoria no sincronizada desde gold: {png.name}")

    # --------------------------------------------------------- 2. sello PNG
    for nombre in sorted(declaradas):
        rutas = [
            p for p in (
                RES / nombre, ANEXO / nombre, ASSETS / nombre, VIS_2026 / nombre,
                README_ASSETS / nombre,
            ) if p.exists()
        ]
        if not rutas:
            avisos.append(f"declarada pero no generada en este checkout: {nombre}")
            continue
        esperado = codigo(nombre)
        # {rango} se resuelve contra Mongo; sin conexion no se puede comparar.
        if "{rango}" in etiqueta_declarada(nombre) and rango_etxebide() is None:
            avisos.append(f"{nombre}: etiqueta con {{rango}} sin Mongo que la resuelva")
            continue
        for ruta in rutas:
            meta = _leer_metadatos(ruta)
            if "_error" in meta:
                errores.append(f"{ruta.name}: no se pudo leer el PNG ({meta['_error']})")
                continue
            if not meta:
                errores.append(
                    f"{ruta.relative_to(BASE)}: sin metadatos de vintage "
                    "(regenerar la figura)"
                )
                continue
            if meta.get("Vintage") != esperado:
                errores.append(
                    f"{ruta.relative_to(BASE)}: vintage {meta.get('Vintage')!r} "
                    f"!= declarado {esperado!r}"
                )
            if meta.get("Description") != f"Vintage: {etiqueta(nombre)}":
                errores.append(
                    f"{ruta.relative_to(BASE)}: etiqueta incrustada distinta del YAML"
                )
            # El sello no puede tapar ningun texto del eje X: el generador lo
            # mide y deja el recuento en el PNG (analysis/vintage_figuras.py).
            solapes = meta.get("Solapes")
            if solapes is None:
                errores.append(
                    f"{ruta.relative_to(BASE)}: sin recuento de solapes del sello "
                    "(regenerar la figura)"
                )
            elif solapes != "0":
                errores.append(
                    f"{ruta.relative_to(BASE)}: el sello de vintage pisa {solapes} "
                    "texto(s); ajustar el generador"
                )

    # ------------------------------------------------- 3. coherencia contrato
    for nombre, entrada in declaradas.items():
        cod = str(entrada.get("vintage"))
        if cod not in CODIGOS_VALIDOS:
            errores.append(f"{nombre}: codigo de vintage invalido {cod!r}")
            continue
        fuentes = set(entrada.get("fuentes") or [])
        mezcla = bool(fuentes & FUENTES_2024) and bool(fuentes & FUENTES_2026)
        exento = bool(entrada.get("muestra_2026"))
        if mezcla and cod != "mixto" and not exento:
            errores.append(
                f"{nombre}: mezcla fuentes 2024 y 2026 pero declara {cod!r} "
                "(deberia ser 'mixto' o marcar muestra_2026: true)"
            )
        if cod == "mixto" and not mezcla and not fuentes:
            avisos.append(f"{nombre}: declara 'mixto' sin declarar fuentes")

    if declaradas.get("P_oficial_vs_anuncios_por_TH.png", {}).get("vintage") != "mixto":
        errores.append("P_oficial_vs_anuncios_por_TH.png debe ser 'mixto' (regla del contrato)")

    # Aviso si el contrato cambia de vintage y el YAML no acompana.
    for metrica in ("alquiler", "anuncios", "renta"):
        try:
            comparabilidad.etiqueta_vintage(metrica)
        except Exception as exc:  # noqa: BLE001
            avisos.append(f"comparabilidad.yaml ilegible para {metrica}: {exc!r}")

    # --------------------------------------------------------------- salida
    for aviso in avisos:
        print(f"AVISO  {aviso}")
    for error in errores:
        print(f"FAIL   {error}")
    total = len(declaradas)
    if errores:
        print(f"\n{len(errores)} fallo(s) sobre {total} figuras declaradas")
        return 1
    print(f"OK  {total} figuras declaradas · gold, deck y memoria sellados y coherentes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
