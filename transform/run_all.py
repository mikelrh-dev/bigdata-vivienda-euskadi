"""Orquestador de transformaciones (silver) del pipeline de vivienda Euskadi.

Cada script declara sus entradas y salidas en ``SCRIPTS``. El orden de
ejecución se calcula por orden topológico sobre esas dependencias (Kahn,
desempate estable por el orden de grupo declarado). Un script que falle no
aborta a los demás; el resultado queda en ``data/procesado/run_manifest.json``.

Uso:
    python transform/run_all.py
    python transform/run_all.py --group analisis
    python transform/run_all.py --check      # solo verifica staleness por script
    python transform/run_all.py --dry-run    # muestra el orden sin ejecutar

Reglas:
- ``in``/``out`` usan prefijos ``raw:`` / ``proc:`` / ``res:`` (data/raw,
  data/procesado, data/resultados). También se admiten globs en ``out_glob``.
- Los scripts sin salidas declaradas conservan su orden relativo y se
  reportan como SIN-DECLARAR en --check (deuda a declarar, no a ocultar).
- Nodos in-place (aplicar_cobertura_mercado.py: dim->dim,
  deduplicar_alquiler_enriquecido.py: json->json): --check es sensible al
  orden; el estado de referencia se obtiene tras una ejecucion completa en
  orden topologico, nunca tras re-ejecuciones parciales.
- Los scripts fuera del pipeline van en ``EXCLUIDOS`` con motivo obligatorio.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
TRANSFORM_DIR = PROJECT_ROOT / "transform"
PROCESADO_DIR = PROJECT_ROOT / "data" / "procesado"
RESULTADOS_DIR = PROJECT_ROOT / "data" / "resultados"

BASES = {"raw": PROJECT_ROOT / "data" / "raw",
         "proc": PROCESADO_DIR,
         "res": RESULTADOS_DIR}

# Registro declarativo: script -> {group, in, out, out_glob}.
# El orden de ejecución se deriva de in/out; el orden escrito aquí solo
# desempata (refleja los grupos históricos).
SCRIPTS: dict[str, dict[str, list[str]]] = {
    # normalizacion
    "normalizar_json_crudos.py": {
        "group": "normalizacion",
        "in": ["raw:*.json"],
        "out": [], "out_glob": ["proc:*_normalizado.json"]},
    # limpieza_base
    "limpiar_ecvi.py": {
        "group": "limpieza_base",
        "in": ["raw:ecvi_compraventa*.csv"],
        "out": ["proc:ecvi_compraventa_limpio.csv"], "out_glob": []},
    "limpiar_eustat_demografia.py": {
        "group": "limpieza_base",
        "in": ["raw:eustat_demografia*.csv"],
        "out": ["proc:eustat_demografia_renta_252.csv",
                "proc:eustat_demografia_renta_252.json"], "out_glob": []},
    "corregir_empleo.py": {
        "group": "limpieza_base",
        "in": ["raw:udalmap_empleo.csv"],
        "out": ["proc:udalmap_empleo_corregido.csv",
                "proc:udalmap_empleo_corregido.json"], "out_glob": []},
    "parsear_secciones.py": {
        "group": "limpieza_base",
        "in": ["raw:alquiler_seccion*.csv"],
        "out": ["proc:alquiler_seccion.csv",
                "proc:alquiler_seccion_resumen.csv"], "out_glob": []},
    "deduplicar_alquiler_enriquecido.py": {
        "group": "limpieza_base",
        "in": ["proc:alquiler_municipal_enriquecido.json"],
        "out": ["proc:alquiler_municipal_enriquecido.json"], "out_glob": []},
    # dim_municipios
    "dim_municipios.py": {
        "group": "dim_municipios",
        "in": ["raw:anuncios_fotocasa.csv", "raw:anuncios_pisos.csv",
               "raw:anuncios_realtyapi.csv", "raw:alquiler_municipal.csv",
               "raw:emal_fianzas.csv", "raw:eustat_renta_municipal.csv"],
        "out": ["proc:dim_municipios.json", "proc:dim_municipios.csv"],
        "out_glob": []},
    # unificacion temprana: los escritores in-place de anuncios_unificados
    # (fingerprint, equipamiento, rescatar) van justo despues de unificar y
    # antes de cualquier lector, para que --check no marque stale espurio.
    "unificar_anuncios.py": {
        "group": "unificacion",
        "in": [],
        "out": ["proc:anuncios_unificados.csv"],
        "out_glob": ["proc:anuncios_unificados.json"]},
    "generar_fingerprint.py": {
        "group": "unificacion",
        "in": ["proc:anuncios_unificados.csv"],
        "out": ["proc:anuncios_unificados.csv"], "out_glob": []},
    "enriquecer_equipamiento_realtyapi.py": {
        "group": "enriquecimiento",
        "in": ["proc:anuncios_unificados.csv"],
        "out": ["proc:anuncios_unificados.csv"], "out_glob": []},
    "rescatar_features_nlp.py": {
        "group": "analisis",
        "in": ["proc:anuncios_unificados.csv"],
        "out": ["proc:anuncios_unificados.csv",
                "proc:anuncios_unificados.json"], "out_glob": []},
    # cobertura (recuento real post-dedup; reescribe dim de forma declarada).
    # Va justo tras los escritores de unificados y antes de todo lector de
    # dim, para que distancias/analisis/gaps lean el dim ya enriquecido.
    "aplicar_cobertura_mercado.py": {
        "group": "cobertura",
        "in": ["proc:dim_municipios.csv", "proc:anuncios_unificados.csv"],
        "out": ["proc:dim_municipios.csv",
                "proc:cobertura_anuncios.csv"], "out_glob": []},
    # distancias (requiere dim ya con cobertura)
    "generar_distancias.py": {
        "group": "distancias",
        "in": ["proc:dim_municipios.csv"],
        "out": ["proc:distancias_capitales_252.csv",
                "proc:distancias_haversine_252.csv",
                "proc:municipios_euskadi_252.geojson"], "out_glob": []},
    # cobertura_alquiler
    "completar_alquiler_comarca.py": {
        "group": "cobertura_alquiler",
        "in": ["raw:alquiler_municipal.csv", "raw:distancias_capitales.csv",
               "proc:distancias_haversine_252.csv"],
        "out": ["proc:alquiler_municipal_completo.csv"], "out_glob": []},
    # analisis_base
    "generar_analisis_variables_base.py": {
        "group": "analisis_base",
        "in": ["proc:dim_municipios.csv", "proc:alquiler_municipal_completo.csv",
               "raw:distancias_capitales_252.csv", "raw:renta_municipal_completa.csv",
               "raw:udalmap_empleo_corregido.csv", "raw:eustat_poblacion_edad.csv",
               "raw:lanbide_paro_juvenil.csv"],
        "out": ["proc:analisis_variables_base.csv"], "out_glob": []},
    # unificacion (lectores: tras los escritores in-place de arriba)
    "filtrar_outliers.py": {
        "group": "unificacion",
        "in": ["proc:anuncios_unificados.csv"],
        "out": [], "out_glob": ["proc:*_filtrado.json", "proc:*_filtrado.csv"]},
    # enriquecimiento
    "enriquecer_gtfs_conectividad.py": {
        "group": "enriquecimiento",
        "in": [],
        "out": ["proc:transporte_paradas_municipio_enriquecido.csv"],
        "out_glob": []},
    "enriquecer_codigo_ine.py": {
        "group": "enriquecimiento",
        "in": [],
        "out": [], "out_glob": ["proc:anuncios_*_enriquecido.csv",
                                "proc:anuncios_*_enriquecido.json"]},
    "generar_cert_energetico_municipal.py": {
        "group": "enriquecimiento",
        "in": [],
        "out": ["proc:cert_energetico_municipal_252.csv"], "out_glob": []},
    "generar_cert_energetico_moda_municipio.py": {
        "group": "enriquecimiento",
        "in": [],
        "out": ["proc:cert_energetico_moda_municipio.csv"], "out_glob": []},
    # gaps93 (tablas auxiliares de los 93 municipios sin serie oficial)
    "generar_municipios_faltantes_93.py": {
        "group": "gaps93",
        "in": ["proc:dim_municipios.csv", "proc:alquiler_municipal_completo.csv"],
        "out": ["proc:municipios_faltantes_93.csv"], "out_glob": []},
    "generar_emancipacion_tier3_93.py": {
        "group": "gaps93",
        "in": ["proc:municipios_faltantes_93.csv"],
        "out": ["proc:emancipacion_tier3_93.csv"], "out_glob": []},
    "generar_poblacion_joven_municipal.py": {
        "group": "gaps93",
        "in": ["raw:eustat_poblacion_edad.csv"],
        "out": ["proc:poblacion_joven_municipal.csv"], "out_glob": []},
    "asignar_area_funcional_ecvi.py": {
        "group": "gaps93",
        "in": ["proc:ecvi_compraventa_limpio.csv"],
        "out": ["proc:municipio_area_funcional_ecvi.csv"], "out_glob": []},
    # analisis
    "limpiar_vpo_municipal.py": {
        "group": "limpieza_base",
        "in": ["raw:udalmap_vpo_terminadas.csv", "proc:dim_municipios.csv"],
        "out": ["proc:vpo_municipal.csv"], "out_glob": []},
    "calcular_renta_joven.py": {
        "group": "analisis",
        "in": ["proc:analisis_variables_base.csv", "raw:eustat_renta_edad.csv",
               "raw:lanbide_paro_juvenil.csv",
               "raw:udalmap_indicadores_adicionales.csv"],
        "out": ["proc:dim_municipios_renta.csv"], "out_glob": []},
    "calcular_tension_social.py": {
        "group": "analisis",
        "in": ["proc:dim_municipios_renta.csv"],
        "out": ["proc:dim_municipios_tension.csv"], "out_glob": []},
    "construir_dim_gold.py": {
        "group": "analisis",
        "in": ["proc:dim_municipios.csv", "proc:dim_municipios_renta.csv",
               "proc:dim_municipios_tension.csv"],
        "out": ["proc:dim_municipios_enriquecido.csv"], "out_glob": []},
    "imputar_nulos_fuentes.py": {
        "group": "analisis",
        "in": [],
        "out": ["proc:serpavi_renta_imputado.csv"], "out_glob": []},
    "generar_mercado_area_funcional.py": {
        "group": "analisis",
        "in": ["proc:alquiler_municipal_completo.csv",
               "proc:ecvi_compraventa_limpio.csv",
               "proc:municipio_area_funcional_ecvi.csv"],
        "out": ["proc:comparativa_compra_alquiler_af.csv"], "out_glob": []},
    "generar_anuncios_residencial_filtrado.py": {
        "group": "analisis",
        "in": ["proc:anuncios_unificados.csv"],
        "out": ["proc:anuncios_vivienda_residencial_filtrado.csv"],
        "out_glob": []},
    "generar_vistas_mercado.py": {
        "group": "analisis",
        "in": ["proc:anuncios_unificados.csv"],
        "out": ["proc:anuncios_vivienda_residencial.csv",
                "proc:anuncios_vivienda_temporal.csv",
                "proc:anuncios_habitaciones_unificados.csv"], "out_glob": []},
    # resultados (Mongo, canonicos: analysis/run_analisis_mongo.py)
    "generar_mapa_esquema.py": {
        "group": "resultados",
        "in": [],
        "out": ["res:mapa_esquema_silver.html"], "out_glob": []},
    "auditar_lagunas_silver.py": {
        "group": "resultados",
        "in": [],
        "out": ["res:auditoria_lagunas_silver.csv"], "out_glob": []},
}

# Scripts fuera del pipeline, con motivo obligatorio.
EXCLUIDOS: dict[str, str] = {
    "run_all.py": "el propio orquestador",
    "f4_pisos_dirigido.py": "captura dirigida manual (escribe en raw con guard)",
    "generar_f4_pisos_objetivo.py": "genera la lista manual de objetivos de f4",
    "generar_fotocasa_dirigido_informe.py": "informe de captura dirigida",
    "muni_resolve.py": "libreria, no script ejecutable del pipeline",
    "validar_renta.py": "Justificación firmada 2026-11-05: no es transformación ETL silver (no declara in/out proc); es QA bajo demanda; se mantiene fuera del orquestador para no alterar manifest 353/184 ni el gate 130.",
    "generar_figuras_N.py": "genera PNG P0 N1,N2,N3,N7 y H2 desde CSV sin Mongo vivo (evidencia visual, no silver)",
    "_raw_guard.py": "libreria de guardia raw, no paso del pipeline",
}


def _resolver(ref: str) -> list[Path]:
    """Traduce 'base:patron' a rutas (globs solo en el patron, no en la base)."""
    base, _, patron = ref.partition(":")
    root = BASES.get(base, PROCESADO_DIR)
    if any(ch in patron for ch in ("*", "?", "[")):
        return sorted(root.glob(patron))
    return [root / patron]  # exista o no: --check informa si falta


def _sha256(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _salidas(script: str) -> list[Path]:
    cfg = SCRIPTS[script]
    rutas = [_resolver(r)[0] for r in cfg.get("out", [])]
    for g in cfg.get("out_glob", []):
        rutas.extend(_resolver(g))
    vistos, unicas = set(), []
    for p in rutas:
        if p not in vistos:
            vistos.add(p)
            unicas.append(p)
    return sorted(unicas)


def _entradas(script: str) -> list[Path]:
    rutas: list[Path] = []
    for ref in SCRIPTS[script].get("in", []):
        rutas.extend(_resolver(ref))
    return sorted(set(rutas))


def _orden_topologico(scripts: list[str]) -> list[str]:
    """Kahn sobre productor->consumidor por nombre de fichero.

    productor[fichero] = script que lo declara en ``out`` (concreto, no glob);
    si varios scripts escriben el mismo fichero, se respeta el orden de grupo.
    Los bucles sobre el mismo script (in == out) se ignoran.
    """
    productor: dict[str, str] = {}
    for s in scripts:
        for r in SCRIPTS[s].get("out", []):
            productor.setdefault(r, s)
    aristas: dict[str, set[str]] = {s: set() for s in scripts}
    grado: dict[str, int] = {s: 0 for s in scripts}
    for s in scripts:
        for ref in SCRIPTS[s].get("in", []):
            base, _, patron = ref.partition(":")
            if any(ch in patron for ch in ("*", "?", "[")):
                continue  # los globs no ordenan
            nombre = f"{base}:{patron}"
            prod = productor.get(nombre)
            if prod and prod != s and s not in aristas[prod]:
                aristas[prod].add(s)
                grado[s] += 1
    orden, pendientes = [], list(scripts)  # estable: respeta el orden dado
    while pendientes:
        listo = next((s for s in pendientes if grado[s] == 0), None)
        if listo is None:  # ciclo: romper por orden declarado y avisar
            listo = pendientes[0]
            print(f"  AVISO: ciclo de dependencias, se fuerza {listo} por orden declarado")
        pendientes.remove(listo)
        orden.append(listo)
        for dep in aristas[listo]:
            grado[dep] -= 1
    return orden


def _estado(script: str) -> tuple[str, str]:
    """Devuelve (estado, detalle) sin ejecutar nada."""
    salidas = _salidas(script)
    # Gobernanza (sin tocar datos): normalizar_json_crudos declara
    # raw:*.json -> proc:*_normalizado.json. Existe un huerfano legacy
    # udalmap_empleo_corregido_normalizado.json (2026-11-05, sin raw
    # correspondiente, parte del manifest silver 188 pero no lo produce
    # el pipeline actual). Si se incluye en min(mtime), cualquier raw
    # posterior (lanbide_paro_*.json 2026-11-07) se marca falsamente
    # como DESACTUALIZADO aunque los bytes sean identicos al manifest
    # (0 diffs vs run_manifest verificado 2026-11-09). Se excluyen las
    # salidas sin entrada correspondiente solo para este script glob->glob.
    if script == "normalizar_json_crudos.py":
        entradas_nombres = {p.name for p in _entradas(script)}
        salidas = [p for p in salidas
                   if p.name.replace("_normalizado.json", ".json")
                   in entradas_nombres]
    if not salidas:
        return "SIN-DECLARAR", "sin salidas declaradas"
    faltan = [p.name for p in salidas if not p.exists()]
    if faltan:
        return "FALTA", "faltan: " + ", ".join(faltan[:3])
    mtime_out = min(p.stat().st_mtime for p in salidas)
    propias = {p.resolve() for p in salidas}
    entradas = [p for p in _entradas(script) if p.resolve() not in propias]
    # Las entradas que son salidas del propio script (nodos in-place como
    # aplicar_cobertura o rescatar_features_nlp) se excluyen: un script no
    # puede estar desactualizado respecto a si mismo por el orden de
    # escritura interno (csv vs json separados por ms).
    if not entradas:
        return "OK", f"{len(salidas)} salidas presentes"
    nuevas = [p.name for p in entradas
              if p.exists() and p.stat().st_mtime > mtime_out]
    if nuevas:
        return "DESACTUALIZADO", "entradas más nuevas: " + ", ".join(nuevas[:3])
    ausentes = [ref for ref in SCRIPTS[script].get("in", [])
                if not any(ch in ref for ch in ("*", "?", "[")) and not _resolver(ref)]
    if ausentes:
        return "DESACTUALIZADO", "entradas inexistentes: " + ", ".join(ausentes[:3])
    return "OK", f"{len(salidas)} salidas al día"


def _run_script(script: Path) -> tuple[int, float]:
    """Ejecuta un script y retorna (returncode, duracion_segundos)."""
    import os
    inicio = time.monotonic()
    try:
        # Higiene Windows: UTF-8 en hijos (pyvis y prints con euskera).
        env = dict(os.environ, PYTHONUTF8="1")
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            env=env,
        )
        rc = proc.returncode
        if proc.stdout:
            for linea in proc.stdout.strip().splitlines()[-5:]:
                print(f"    {linea}")
        if rc != 0 and proc.stderr:
            for linea in proc.stderr.strip().splitlines()[-8:]:
                print(f"    ERR: {linea}")
    except Exception as exc:
        print(f"    EXCEPCION: {exc}")
        rc = 1
    duracion = time.monotonic() - inicio
    return rc, duracion


def _check() -> int:
    print("=== STALENESS CHECK (por script) ===")
    peor = 0
    for script in SCRIPTS:
        estado, detalle = _estado(script)
        marca = {"OK": "OK ", "FALTA": ">>>", "DESACTUALIZADO": " >>",
                 "SIN-DECLARAR": " ??"}[estado]
        print(f"  [{marca}] {script}: {detalle}")
        peor = max(peor, {"OK": 0, "SIN-DECLARAR": 0,
                          "DESACTUALIZADO": 1, "FALTA": 2}[estado])
    return 1 if peor else 0


def _escribir_manifest(resultados: list[dict]) -> None:
    manifest = {
        "generado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "orden_ejecucion": [r["script"] for r in resultados],
        "scripts": resultados,
    }
    destino = PROCESADO_DIR / "run_manifest.json"
    destino.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(f"Manifest escrito en {destino}")


def _ficha(script: str, rc: int, dur: float) -> dict:
    def _info(p: Path) -> dict:
        return {"fichero": str(p.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "sha256": _sha256(p),
                "bytes": p.stat().st_size if p.exists() else None}
    return {
        "script": script,
        "group": SCRIPTS[script]["group"],
        "rc": rc,
        "duracion_s": round(dur, 1),
        "inicio_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entradas": [_info(p) for p in _entradas(script)],
        "salidas": [_info(p) for p in _salidas(script)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Orquestador de transformaciones (silver).")
    parser.add_argument("--group", type=str, default=None,
                        help="Ejecutar solo un grupo específico.")
    parser.add_argument("--check", action="store_true",
                        help="Solo verificar staleness por script, no ejecutar.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar el orden de ejecución sin ejecutar.")
    args = parser.parse_args()

    if args.check:
        return _check()

    orden = _orden_topologico(list(SCRIPTS))
    if args.group:
        orden = [s for s in orden if SCRIPTS[s]["group"] == args.group]
        if not orden:
            print(f"Grupo '{args.group}' no encontrado. Disponibles: "
                  f"{sorted({c['group'] for c in SCRIPTS.values()})}")
            return 1

    if args.dry_run:
        print("=== ORDEN DE EJECUCION ===")
        for i, s in enumerate(orden, 1):
            print(f"  {i:02d}. [{SCRIPTS[s]['group']}] {s}")
        return 0

    print(f"=== TRANSFORM RUN ALL ({len(orden)} scripts) ===")
    print(f"Python: {sys.executable}")
    print(f"Root: {PROJECT_ROOT}")
    print()

    total_fallos = 0
    resultados: list[dict] = []
    inicio_total = time.monotonic()
    grupo_actual = ""

    for nombre in orden:
        script = TRANSFORM_DIR / nombre
        if SCRIPTS[nombre]["group"] != grupo_actual:
            grupo_actual = SCRIPTS[nombre]["group"]
            print(f"--- Grupo: {grupo_actual} ---")
        if not script.exists():
            print(f"  SKIP (no existe): {nombre}")
            resultados.append(_ficha(nombre, 99, 0.0))
            total_fallos += 1
            continue
        print(f"  > {nombre}")
        rc, dur = _run_script(script)
        estado = "OK" if rc == 0 else "FAIL"
        print(f"    -> {estado} ({dur:.1f}s)")
        resultados.append(_ficha(nombre, rc, dur))
        if rc != 0:
            total_fallos += 1
        print()

    duracion_total = time.monotonic() - inicio_total
    print(f"=== RESUMEN: {len(orden)} scripts, {total_fallos} fallos, {duracion_total:.1f}s ===")
    _escribir_manifest(resultados)
    return 0 if total_fallos == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
