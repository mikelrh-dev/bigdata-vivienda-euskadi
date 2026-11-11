"""Orquestador de transformaciones (silver) del pipeline de vivienda Euskadi.

Un solo sitio donde se declara qué transformaciones existen, qué ficheros debe
producir cada una y en qué orden se ejecutan. El orden de esta lista es el
orden topológico del DAG. Cada script corre en su propio proceso: si uno
falla, los demás siguen.

Uso:
    python transform/run_all.py            # menú (sin TTY: solo pendientes)
    python transform/run_all.py --list     # estado de cada paso
    python transform/run_all.py --missing  # ejecutar solo lo pendiente
    python transform/run_all.py --force    # regenerar todo
    python transform/run_all.py --only id1,id2
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

from paths import PROCESADO_DIR, ensure_dirs  # noqa: E402

TRANSFORM_DIR = PROJECT_ROOT / "transform"
LOG_DIR = PROJECT_ROOT / "logs"


@dataclass(frozen=True)
class Paso:
    """Una transformación y las salidas que deben existir al terminar."""

    id: str
    script: str
    salidas: tuple[str, ...]
    nota: str = ""


# El orden de esta lista es el orden de ejecución.
PASOS: tuple[Paso, ...] = (
    Paso("dim-municipios", "dim_municipios.py",
         ("dim_municipios.json", "dim_municipios.csv")),
    Paso("poblacion-joven", "generar_poblacion_joven_municipal.py",
         ("poblacion_joven_municipal.csv",)),
    Paso("eustat-demografia", "limpiar_eustat_demografia.py",
         ("eustat_demografia_renta_252.csv", "eustat_demografia_renta_252.json")),
    Paso("ecvi", "limpiar_ecvi.py",
         ("ecvi_compraventa_limpio.csv", "ecvi_compraventa_limpio.json")),
    Paso("empleo", "corregir_empleo.py",
         ("udalmap_empleo_corregido.csv", "udalmap_empleo_corregido.json")),
    Paso("secciones", "parsear_secciones.py",
         ("alquiler_seccion.csv", "alquiler_seccion_resumen.csv")),
    Paso("codigo-ine", "enriquecer_codigo_ine.py",
         ("alquiler_municipal_enriquecido.csv",
          "anuncios_fotocasa_enriquecido.json",
          "anuncios_pisos_enriquecido.json",
          "anuncios_realtyapi_enriquecido.json",
          "informe_entity_resolution.csv")),
    Paso("dedup-alquiler", "deduplicar_alquiler_enriquecido.py",
         ("alquiler_municipal_enriquecido.csv",)),
    Paso("unificar", "unificar_anuncios.py",
         ("anuncios_unificados.csv", "anuncios_unificados.json")),
    Paso("fingerprint", "generar_fingerprint.py",
         ("anuncios_unificados.json",)),
    Paso("equipamiento", "enriquecer_equipamiento_realtyapi.py",
         ("anuncios_unificados.json", "anuncios_unificados.csv")),
    Paso("rescatar-nlp", "rescatar_features_nlp.py",
         ("anuncios_unificados.csv", "anuncios_unificados.json")),
    Paso("cobertura", "aplicar_cobertura_mercado.py",
         ("dim_municipios.csv", "cobertura_anuncios.csv")),
    Paso("distancias", "generar_distancias.py",
         ("distancias_capitales_252.csv", "distancias_haversine_252.csv",
          "municipios_euskadi_252.geojson")),
    Paso("alquiler-completo", "completar_alquiler_comarca.py",
         ("alquiler_municipal_completo.csv",)),
    Paso("analisis-base", "generar_analisis_variables_base.py",
         ("analisis_variables_base.csv",)),
    Paso("outliers", "filtrar_outliers.py",
         ("anuncios_fotocasa_filtrado.json", "anuncios_pisos_filtrado.json")),
    Paso("gtfs", "enriquecer_gtfs_conectividad.py",
         ("transporte_paradas_municipio_enriquecido.csv",)),
    Paso("cert-energetico", "generar_cert_energetico_municipal.py",
         ("cert_energetico_municipal_252.csv",)),
    Paso("cert-moda", "generar_cert_energetico_moda_municipio.py",
         ("cert_energetico_moda_municipio.csv",)),
    Paso("faltantes-93", "generar_municipios_faltantes_93.py",
         ("municipios_faltantes_93.csv",)),
    Paso("emancipacion-93", "generar_emancipacion_tier3_93.py",
         ("emancipacion_tier3_93.csv",)),
    Paso("area-funcional", "asignar_area_funcional_ecvi.py",
         ("municipio_area_funcional_ecvi.csv",)),
    Paso("vpo", "limpiar_vpo_municipal.py",
         ("vpo_municipal.csv",)),
    Paso("renta-joven", "calcular_renta_joven.py",
         ("dim_municipios_renta.csv",)),
    Paso("tension", "calcular_tension_social.py",
         ("dim_municipios_tension.csv",)),
    Paso("dim-gold", "construir_dim_gold.py",
         ("dim_municipios_enriquecido.csv",)),
    Paso("imputar-serpavi", "imputar_nulos_fuentes.py",
         ("serpavi_renta_imputado.csv",)),
    Paso("mercado-af", "generar_mercado_area_funcional.py",
         ("comparativa_compra_alquiler_af.csv",)),
    Paso("vistas", "generar_vistas_mercado.py",
         ("anuncios_vivienda_residencial.csv",
          "anuncios_vivienda_temporal.csv",
          "anuncios_habitaciones_unificados.csv")),
    Paso("residencial-filtrado", "generar_anuncios_residencial_filtrado.py",
         ("anuncios_vivienda_residencial_filtrado.csv",)),
)

POR_ID = {paso.id: paso for paso in PASOS}


def _coincidencias(patron: str) -> list[Path]:
    if any(c in patron for c in "*?["):
        return sorted(PROCESADO_DIR.glob(patron))
    ruta = PROCESADO_DIR / patron
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
    print(f"procesado: {PROCESADO_DIR}")
    print()
    print(f"{'id':22} {'estado':10} {'salidas':>9}  script")
    print("-" * 78)
    for paso in PASOS:
        nombre, ok, total = estado(paso)
        detalle = f"{ok}/{total}" if total else "-"
        print(f"{paso.id:22} {nombre:10} {detalle:>9}  {paso.script}")


def seleccionar(only: str | None, missing: bool, force: bool) -> list[Paso]:
    if only:
        pedidos = [x.strip() for x in only.split(",") if x.strip()]
        desconocidos = [x for x in pedidos if x not in POR_ID]
        if desconocidos:
            raise SystemExit(
                f"Paso desconocido: {', '.join(desconocidos)}. "
                "Usa --list para ver los ids."
            )
        pedidos_set = set(pedidos)
        return [p for p in PASOS if p.id in pedidos_set]
    if force:
        return list(PASOS)
    return [p for p in PASOS if estado(p)[0] != "completo"]


def _ejecutar(paso: Paso, log) -> bool:
    script = TRANSFORM_DIR / paso.script
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
    ruta_log = LOG_DIR / f"transform_{sello}.log"
    with ruta_log.open("w", encoding="utf-8") as fh:

        def log(texto: str) -> None:
            print(texto)
            fh.write(texto + "\n")
            fh.flush()

        log(f"Transformaciones a ejecutar: {len(pasos)}")
        log(f"procesado: {PROCESADO_DIR}")
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
    print(f"procesado: {PROCESADO_DIR}")
    print(f"Transformaciones: {total}  |  completas: {listos}  |  pendientes: {total - listos}")
    print()
    print("1) Ejecutar solo lo pendiente")
    print("2) Regenerar todo")
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
    parser = argparse.ArgumentParser(description="Ejecuta las transformaciones.")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--list", action="store_true", help="mostrar estado y salir")
    grupo.add_argument("--missing", action="store_true", help="solo lo pendiente")
    grupo.add_argument("--force", action="store_true", help="regenerar todo")
    grupo.add_argument("--only", metavar="ID[,ID]", help="ejecutar solo estos ids")
    args = parser.parse_args(argv)

    if args.list:
        listar()
        return 0

    if args.missing or args.force or args.only:
        pasos = seleccionar(args.only, args.missing, args.force)
        if not pasos:
            print("No hay nada pendiente.")
            return 0
        return ejecutar(pasos)

    if not sys.stdin.isatty():
        return ejecutar(seleccionar(None, missing=True, force=False))
    return menu()


if __name__ == "__main__":
    raise SystemExit(main())
