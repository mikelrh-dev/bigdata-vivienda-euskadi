"""Sello de vintage (año) en las figuras del proyecto.

Fuente única: `config/vintage_figuras.yaml`. El sello se pinta como etiqueta
legible en la esquina inferior derecha y se escribe como metadato PNG, de modo
que `scripts/verificar_vintage_figuras.py` comprueba el artefacto real (no el
código fuente) y no necesita OCR.

Uso desde un generador:

    from analysis.vintage_figuras import anotar, metadatos

    anotar(fig, "H1_ranking_esfuerzo_18_34.png")
    fig.savefig(ruta, metadata=metadatos("H1_ranking_esfuerzo_18_34.png"))

Si la figura no está declarada, `anotar` no inventa un año: pinta
`Datos: sin año declarado` y `codigo` lanza `KeyError` para que la
verificación falle en vez de publicar una figura muda.

Regla del proyecto (`config/comparabilidad.yaml`, regla 4): no se publica una
cifra sin declarar su vintage.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "vintage_figuras.yaml"

RES = ROOT / "data" / "resultados"
ASSETS = ROOT / "docs" / "presentacion_v2" / "assets"
MEM_FIG = ROOT / "docs" / "memoria" / "figuras"

# Color redundante al texto: se elige con contraste >= 4,5:1 sobre blanco
# (WCAG 2.2, texto normal). El texto es la señal principal; el color, refuerzo.
COLORES = {
    "2024": "#0072B2",
    "2026": "#C8451B",
    "mixto": "#4D4D4D",
    "flujo": "#117733",
    "acumulado": "#7A5C00",
    "sin-fecha": "#4D4D4D",
}

SIN_DECLARAR = "Datos: sin año declarado"

_cache: dict[str, Any] | None = None
_rango_cache: str | None | bool = False


def rango_etxebide() -> str | None:
    """Rango real de fechas del registro de promociones de Etxebide.

    La coleccion guarda 406 promociones, pero solo 226 traen `Sorteo`
    (2001-03-26 .. 2014-10-28); el resto (en curso, convenio, proyecto) no
    tiene fecha. Devolver el rango evita decir "sin año" cuando el dato
    existe, y evita inventar un unico ano que no existe.

    Devuelve None si Mongo no esta disponible (el verbo queda en "sin año").
    """
    global _rango_cache
    if _rango_cache is not False:
        return _rango_cache  # type: ignore[return-value]
    try:
        from storage.mongo import get_db

        fechas = [
            str(d["Sorteo"])
            for d in get_db()["etxebide_promociones"].find({}, {"Sorteo": 1})
            if d.get("Sorteo")
        ]
        _rango_cache = f"{min(fechas)[:4]}-{max(fechas)[:4]}" if fechas else None
    except Exception:  # noqa: BLE001 - sin Mongo se degrada, no rompe
        _rango_cache = None
    return _rango_cache


def _campos() -> dict[str, str]:
    return {"rango": rango_etxebide() or "sin año"}


def _formatear(texto: str) -> str:
    """Sustituye {rango} y similares; si falta el dato, no deja un hueco."""
    try:
        salida = texto.format(**_campos())
    except (KeyError, IndexError, ValueError):
        return texto
    return salida.replace("{rango}", "sin año")


def _config() -> dict[str, Any]:
    global _cache
    if _cache is None:
        import yaml

        cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
        if not isinstance(cfg, dict):
            raise ValueError(f"{CONFIG} no contiene un mapa YAML valido")
        _cache = cfg
    return _cache


def figuras() -> dict[str, dict[str, Any]]:
    """Mapa `nombre.png -> {vintage, fuentes}` declarado en el YAML."""
    return dict(_config().get("figuras") or {})


def _entrada(nombre: str) -> dict[str, Any] | None:
    return figuras().get(Path(nombre).name)


def codigo(nombre: str) -> str:
    """Codigo de vintage (`2024`, `2026`, `mixto`, `flujo`, `acumulado`)."""
    entrada = _entrada(nombre)
    if entrada is None:
        raise KeyError(f"figura sin vintage declarado en {CONFIG.name}: {nombre}")
    return str(entrada["vintage"])


def etiqueta(nombre: str) -> str:
    """Texto que se pinta en el PNG. Nunca devuelve una cadena vacia."""
    return _formatear(etiqueta_declarada(nombre))


def etiqueta_declarada(nombre: str) -> str:
    """Etiqueta tal cual esta en el YAML, con {rango} sin sustituir."""
    nombre = Path(nombre).name
    largas = _config().get("etiquetas") or {}
    if nombre in largas:
        return str(largas[nombre])
    entrada = _entrada(nombre)
    if entrada is None:
        return SIN_DECLARAR
    codigos = _config().get("codigos") or {}
    return str(codigos.get(str(entrada["vintage"]), SIN_DECLARAR))


def color(nombre: str) -> str:
    try:
        return COLORES.get(codigo(nombre), "#4D4D4D")
    except KeyError:
        return "#4D4D4D"


def metadatos(nombre: str) -> dict[str, str]:
    """Chunks de texto PNG: permiten verificar el vintage sin OCR."""
    nombre = Path(nombre).name
    try:
        cod = codigo(nombre)
    except KeyError:
        cod = "sin-declarar"
    return {
        "Software": "bigdata-vivienda-euskadi",
        "Description": f"Vintage: {etiqueta(nombre)}",
        "Figura": nombre,
        "Vintage": cod,
        # Cuantos textos pisa el sello. 0 es lo correcto; se comprueba sobre el
        # PNG ya escrito, sin volver a generar la figura.
        "Solapes": str(len(solapes(nombre))),
    }


# Franja inferior del lienzo que queda reservada para el sello. Sin ella el
# sello se pinta encima del titulo del eje X o de una etiqueta inclinada.
BANDA_SELLO = 0.062

# Area (px2) por debajo de la cual el roce de cajas no se considera solape.
UMBRAL_SOLAPE_PX2 = 6.0

# Textos que el sello pisa en cada figura, medidos al generarla. Se escribe el
# recuento en los metadatos del PNG para poder comprobarlo sin regenerar.
_CAMPOS_DE_TEXTO: dict[str, list[str]] = {}


def _textos_pisados(fig, sello) -> list[str]:
    """Textos visibles cuya caja se cruza con la del sello."""
    from matplotlib.text import Text  # noqa: WPS433 (dependencia opcional)

    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        caja = sello.get_window_extent(renderer)
    except Exception:  # noqa: BLE001 - sin lienzo no se puede medir
        return []
    pisados: list[str] = []
    for t in fig.findobj(Text):
        if t is sello or not t.get_visible():
            continue
        texto = (t.get_text() or "").strip()
        if not texto:
            continue
        try:
            otra = t.get_window_extent(renderer)
        except Exception:  # noqa: BLE001
            continue
        ancho = min(caja.x1, otra.x1) - max(caja.x0, otra.x0)
        alto = min(caja.y1, otra.y1) - max(caja.y0, otra.y0)
        if ancho > 0 and alto > 0 and ancho * alto > UMBRAL_SOLAPE_PX2:
            pisados.append(texto[:60].replace("\n", " / "))
    return pisados


def reservar_banda_sello(fig) -> None:
    """Recoloca el area de ejes para dejar libre la franja del sello.

    Se llama desde `anotar`, despues del `tight_layout` del generador, para
    que el eje X, sus etiquetas y el sello no compartan pixeles. Si el lienzo
    no admite el reparto (ejes colocados a mano), no rompe: se degrada al
    comportamiento anterior en vez de tumbar la generacion.
    """
    try:
        fig.tight_layout(rect=(0.0, BANDA_SELLO, 1.0, 1.0))
    except Exception:  # noqa: BLE001 - un lienzo raro no debe romper el gold
        pass


def anotar(fig, nombre: str, fondo: str = "#FFFFFF", tamano: float = 10.5) -> None:
    """Pinta la etiqueta de vintage abajo a la derecha, encima de todo.

    Se llama justo antes de `savefig`, despues de `tight_layout`, y con caja
    opaca para que un pie previo no la haga ilegible. Antes de pintar reserva
    una banda inferior para que el sello no tape ningun texto del eje X.
    """
    reservar_banda_sello(fig)
    sello = fig.text(
        0.988,
        0.006,
        etiqueta(nombre),
        ha="right",
        va="bottom",
        fontsize=tamano,
        fontweight="bold",
        color=color(nombre),
        bbox=dict(
            boxstyle="round,pad=0.36",
            facecolor=fondo,
            edgecolor=color(nombre),
            linewidth=1.0,
            alpha=0.95,
        ),
        zorder=1000,
    )
    _CAMPOS_DE_TEXTO[Path(nombre).name] = _textos_pisados(fig, sello)


def solapes(nombre: str) -> list[str]:
    """Textos que el sello pisa en la ultima generacion de esa figura."""
    return list(_CAMPOS_DE_TEXTO.get(Path(nombre).name, []))


def copias_deck() -> frozenset[str]:
    """Nombres de gold que el deck consume byte a byte (declarados en el YAML)."""
    cfg = _config().get("sincronizacion") or {}
    return frozenset(str(n) for n in (cfg.get("deck") or []))


def sincronizar(verbose: bool = True) -> list[Path]:
    """Copia gold -> deck y gold/assets -> memoria segun el YAML.

    Idempotente. Se ejecuta al final de la cadena gold, cuando ya existen
    todas las figuras (incluidas las que regenera `generar_figuras_N`).
    Devuelve las rutas escritas.
    """
    cfg = _config().get("sincronizacion") or {}
    escritas: list[Path] = []

    for nombre in cfg.get("deck") or []:
        origen = RES / str(nombre)
        if not origen.exists():
            if verbose:
                print(f"AVISO sincronizacion: falta {origen.relative_to(ROOT)}")
            continue
        ASSETS.mkdir(parents=True, exist_ok=True)
        destino = ASSETS / origen.name
        shutil.copyfile(origen, destino)
        escritas.append(destino)

    for destino_nombre, origen_rel in (cfg.get("memoria") or {}).items():
        origen = ROOT / str(origen_rel)
        if not origen.exists():
            if verbose:
                print(f"AVISO sincronizacion: falta {origen.relative_to(ROOT)}")
            continue
        MEM_FIG.mkdir(parents=True, exist_ok=True)
        destino = MEM_FIG / str(destino_nombre)
        shutil.copyfile(origen, destino)
        escritas.append(destino)

    if verbose and escritas:
        print(f"figuras sincronizadas: {len(escritas)} -> assets/ y figuras/")
    return escritas
