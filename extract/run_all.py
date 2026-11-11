"""Orquestador de extracción.

Un solo sitio donde se declara qué extractores existen, qué ficheros debe
producir cada uno y en qué orden se ejecutan. Cada script corre en su propio
proceso: si uno falla, los demás siguen.

Uso:
    python extract/run_all.py            # menú (sin TTY: solo pendientes)
    python extract/run_all.py --list     # estado de cada extractor
    python extract/run_all.py --check    # alias de --list
    python extract/run_all.py --missing  # ejecutar solo lo pendiente
    python extract/run_all.py --run      # alias de --missing
    python extract/run_all.py --force    # regenerar todo
    python extract/run_all.py --only id1,id2
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import RAW_DIR, ensure_dirs  # noqa: E402

LOG_DIR = PROJECT_ROOT / "logs"


@dataclass(frozen=True)
class Paso:
    """Un extractor y las salidas que deben existir al terminar."""

    id: str
    script: str
    salidas: tuple[str, ...]
    lento: bool = False
    nota: str = ""
    credenciales: tuple[str, ...] = ()
    activo: bool = True
    scraper: bool = False


# El orden de esta lista es el orden de ejecución. `dim-municipios` no es un
# extractor: es el catálogo que varios extractores necesitan, así que se
# ejecuta después de las fuentes que lo alimentan y antes de sus consumidores.
PASOS: tuple[Paso, ...] = (
    Paso("eustat", "01_eustat_api.py", (
        "eustat_poblacion_edad.csv",
        "eustat_renta_municipal.csv",
        "eustat_renta_edad.csv",
        "eustat_pib_municipal.csv",
        "eustat_tenencia.csv",
    ), lento=True),
    Paso("eustat-alquiler", "02_eustat_alquiler.py", (
        "alquiler_municipal.csv",
        "alquiler_*_original.csv",
    ), lento=True),
    Paso("emancipacion", "03_euskadi_emancipacion.py", (
        "emancipacion_juventud.csv",
    )),
    Paso("b5m", "04_b5m_geo.py", (
        "municipios_gipuzkoa.geojson",
        "distancias_municipios.zip",
        "b5m_catalogo.json",
        "municipios_gipuzkoa_lista.json",
        "distancias_b5m_gipuzkoa.json",
    ), lento=True),
    Paso("fotocasa", "05_fotocasa_scraper.py", (
        "anuncios_fotocasa.json",
    ), lento=True, nota="scraper", scraper=True),
    Paso("ine", "06_ine_api.py", (
        "ine_69301.json",
        "ine_69302.json",
        "ine_69303.json",
        "ine_69323.json",
        "ine_69330.json",
    ), lento=True),
    Paso("ine-salarios", "07_ine_salarios.py", (
        "ine_salarios_edad.json",
        "ine_salarios_decil.json",
    ), lento=True),
    Paso("pisos", "08_pisos_scraper.py", (
        "anuncios_pisos.json",
    ), lento=True, nota="scraper", scraper=True),
    Paso("realtyapi", "09_realtyapi.py", (
        "anuncios_realtyapi.json",
    ), lento=True, nota="API con clave", credenciales=("REALTYAPI_KEY",)),
    Paso("opendata-etxebide", "10_opendata_bizilagun_etxebide.py", (
        "emal_barrios_municipios_2016_2025.xlsx",
        "emal_fianzas.csv",
        "etxebide_indicador_86.csv",
        "etxebide_solicitudes.csv",
    ), lento=True),
    Paso("dim-municipios", "transform/dim_municipios.py", (
        "procesado/dim_municipios.json",
    ), nota="catálogo (transform)"),
    Paso("euskadi-geo", "euskadi_geo.py", (
        "municipios_euskadi.geojson",
        "distancias_capitales.csv",
    )),
    Paso("fotocasa-dirigido", "09_fotocasa_dirigido.py", (
        "anuncios_fotocasa_dirigido_*.json",
    ), lento=True, nota="scraper dirigido", scraper=True),
    Paso("ovj-salario", "10_ovj_salario.py", (
        "ovj_salario_joven_2024.json",
    )),
    Paso("faltantes", "10_scraping_faltantes.py", (
        "anuncios_faltantes_*_batch*.json",
    ), lento=True, nota="scraper dirigido", scraper=True),
    Paso("transporte", "11_transporte_gtfs_paradas.py", (
        "transporte_paradas_municipio.csv",
    ), lento=True),
    Paso("habitaciones", "13_scraping_habitaciones.py", (
        "anuncios_fotocasa_habitaciones.json",
        "anuncios_pisos_habitaciones.json",
    ), lento=True, nota="scraper", scraper=True),
    Paso("serpavi", "16_serpavi_renta.py", (
        "serpavi_renta_municipal.xlsx",
        "serpavi_renta_municipal.csv",
    )),
    Paso("osrm", "17_osrm_tiempos.py", (
        "osrm_tiempos_capitales.csv",
    ), lento=True),
    Paso("lanbide-juvenil", "18_lanbide_paro_juvenil.py", (
        "lanbide_paro_historico.xlsx",
        "lanbide_paro_juvenil.csv",
    )),
    Paso("udalmap-adicionales", "19_udalmap_indicadores_adicionales.py", (
        "udalmap_indicadores_adicionales.csv",
    )),
    Paso("ecvi", "20_ecvi_compraventa.py", (
        "ECVI_*.xlsx",
        "ecvi_*.csv",
    ), lento=True),
    Paso("lanbide-historico", "21_lanbide_historico_paro_joven.py", (
        "lanbide_paro_historico_joven.csv",
    )),
    Paso("areas-funcionales", "22_geo_areas_funcionales.py", (
        "areas_funcionales_municipios.csv",
    )),
    Paso("certificados", "23_certificados_energeticos.py", (
        "certificados_energeticos_araba_completo.csv",
        "certificados_energeticos_bizkaia_completo.csv",
        "certificados_energeticos_gipuzkoa_completo.csv",
    ), lento=True),
    Paso("etxebide-promociones", "24_etxebide_promociones.py", (
        "etxebide_promociones.json",
    ), lento=True),
    Paso("udalmap-extendido", "25_udalmap_extendido.py", (
        "udalmap_extendido.json",
    ), lento=True),
    Paso("vpo-terminadas", "26_vpo_terminadas.py", (
        "udalmap_vpo_terminadas.csv",
    )),
    Paso("educacion", "educacion_centros.py", (
        "educacion_centros.csv",
    )),
    Paso("salud", "salud_centros.py", (
        "salud_centros.csv",
    )),
    Paso("fotocasa-detalle", "fotocasa_detalle.py", (
        "anuncios_fotocasa_detalle.json",
    ), lento=True, nota="scraper detalle", scraper=True),
    Paso("ine-atlas", "ine_atlas_renta.py", (
        "ine_atlas_renta.csv",
        "renta_municipal_completa.csv",
    )),
    Paso("udalmap-empleo", "udalmap_empleo.py", (
        "udalmap_empleo.csv",
    )),
    Paso("f4-dirigido", "f4_pisos_dirigido.py", (
        "anuncios_pisos_dirigido.json",
    ), lento=True, nota="scraper dirigido", scraper=True),
)

POR_ID = {paso.id: paso for paso in PASOS}


def _coincidencias(patron: str) -> list[Path]:
    base = RAW_DIR
    if patron.split("/")[0] in {"procesado", "resultados"}:
        base = RAW_DIR.parent
    if any(c in patron for c in "*?["):
        return sorted(base.glob(patron))
    ruta = base / patron
    return [ruta] if ruta.exists() else []


def estado(paso: Paso) -> tuple[str, int, int]:
    if not paso.salidas:
        return "sin-salidas", 0, 0
    encontradas = sum(1 for patron in paso.salidas if _coincidencias(patron))
    total = len(paso.salidas)
    if encontradas == total:
        return "completo", encontradas, total
    if encontradas == 0:
        return "pendiente", encontradas, total
    return "parcial", encontradas, total


def listar() -> None:
    print(f"DATA_DIR: {RAW_DIR.parent}")
    print(f"raw:      {RAW_DIR}")
    print()
    print(f"{'id':22} {'estado':10} {'salidas':>9}  {'lento':5} script")
    print("-" * 78)
    for paso in PASOS:
        nombre, ok, total = estado(paso)
        lento = "sí" if paso.lento else ""
        detalle = f"{ok}/{total}" if total else "-"
        print(f"{paso.id:22} {nombre:10} {detalle:>9}  {lento:5} {paso.script}")


def seleccionar(
    only: str | None, missing: bool, force: bool, incluir_lentos: bool = False
) -> list[Paso]:
    if only:
        pedidos = [x.strip() for x in only.split(",") if x.strip()]
        desconocidos = [x for x in pedidos if x not in POR_ID]
        if desconocidos:
            raise SystemExit(
                f"Extractor desconocido: {', '.join(desconocidos)}. "
                "Usa --list para ver los ids."
            )
        pedidos_set = set(pedidos)
        inactivos = [p.id for p in PASOS if p.id in pedidos_set and not p.activo]
        if inactivos:
            raise SystemExit(f"Extractor inactivo: {', '.join(inactivos)}")
        return [p for p in PASOS if p.id in pedidos_set]
    if force:
        return [p for p in PASOS if p.activo]
    return [
        p for p in PASOS
        if p.activo and estado(p)[0] != "completo"
        and (incluir_lentos or not (p.lento or p.scraper))
    ]


def _ejecutar(paso: Paso, log) -> bool:
    if "/" in paso.script:
        script = PROJECT_ROOT / paso.script
    else:
        script = PROJECT_ROOT / "extract" / paso.script
    if not script.exists():
        log(f"  ✗ no existe {script}")
        return False
    log(f"\n▶ {paso.id}  ({paso.script})")
    proceso = subprocess.Popen(
        [sys.executable, str(script)],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert proceso.stdout is not None
    for linea in proceso.stdout:
        log("  " + linea.rstrip())
    codigo = proceso.wait()
    if codigo != 0:
        log(f"  ✗ {paso.id} terminó con código {codigo}")
        return False
    estado_final, ok, total = estado(paso)
    if estado_final != "completo":
        log(f"  ⚠ {paso.id} terminó bien pero faltan salidas ({ok}/{total})")
        return False
    log(f"  ✓ {paso.id}")
    return True


def ejecutar(pasos: list[Paso]) -> int:
    ensure_dirs()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_log = LOG_DIR / f"extract_{sello}.log"
    with ruta_log.open("w", encoding="utf-8") as fh:

        def log(texto: str) -> None:
            print(texto)
            fh.write(texto + "\n")
            fh.flush()

        log(f"Extractores a ejecutar: {len(pasos)}")
        log(f"DATA_DIR: {RAW_DIR.parent}")
        correctos: list[str] = []
        fallidos: list[str] = []
        for paso in pasos:
            try:
                if _ejecutar(paso, log):
                    correctos.append(paso.id)
                else:
                    fallidos.append(paso.id)
            except KeyboardInterrupt:
                log("\nInterrumpido por el usuario.")
                fallidos.append(paso.id)
                break

        log("\n" + "=" * 60)
        log(f"Correctos: {len(correctos)}")
        log(f"Fallidos:  {len(fallidos)}")
        if fallidos:
            log("Fallidos: " + ", ".join(fallidos))
        log(f"Log: {ruta_log}")
    return 0 if not fallidos else 1


def menu() -> int:
    total = len(PASOS)
    listos = sum(1 for p in PASOS if estado(p)[0] == "completo")
    print(f"DATA_DIR: {RAW_DIR.parent}")
    print(f"Extractores: {total}  |  completos: {listos}  |  pendientes: {total - listos}")
    if RAW_DIR.exists() and any(RAW_DIR.iterdir()):
        print(f"Aviso: {RAW_DIR} ya tiene contenido. Regenerar sobrescribe salidas.")
    print()
    print("1) Ejecutar solo lo pendiente")
    print("2) Regenerar todo (incluye lentos y scrapers)")
    print("3) Salir")
    try:
        opcion = input("\nOpción [1]: ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        print()
        return 1
    if opcion == "2":
        return ejecutar(seleccionar(None, missing=False, force=True))
    if opcion == "3":
        return 0
    return ejecutar(seleccionar(None, missing=True, force=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta los extractores.")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--list", "--check", dest="check", action="store_true", help="mostrar estado y salir")
    grupo.add_argument("--missing", "--run", dest="run", action="store_true", help="ejecutar pendientes (excluye lentos/scrapers)")
    grupo.add_argument("--force", action="store_true", help="regenerar todo")
    grupo.add_argument("--only", metavar="ID[,ID]", help="ejecutar solo estos ids")
    args = parser.parse_args(argv)

    if args.check:
        listar()
        return 0

    if args.run or args.force or args.only:
        pasos = seleccionar(args.only, args.run, args.force)
        if not pasos:
            print("No hay nada pendiente.")
            return 0
        return ejecutar(pasos)

    if not sys.stdin.isatty():
        return ejecutar(seleccionar(None, missing=True, force=False))
    return menu()


if __name__ == "__main__":
    raise SystemExit(main())
