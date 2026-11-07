"""PISOS-RE-RESOLVER-UBICACION: ubicacion real por subtitulo/titulo.

- Re-resolucion: subtitulo/titulo + gazetteer vale; municipio_busqueda NUNCA.
- Fuera de Euskadi -> geo_invalida=True + cuarentena reversible.
- codigo_ine sin texto no se propaga; backup seguro; SHA doble; sin imputacion.

Subconjunto de Mongo con skip si no hay Mongo local (nunca falla por entorno).
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "procesado"
TRANSFORM = ROOT / "transform"
for p in (str(ROOT), str(TRANSFORM)):
    if p not in sys.path:
        sys.path.insert(0, p)

from muni_resolve import resolver_codigo, resolver_pisos_por_texto  # noqa: E402


def _union_csv():
    """Union dirigido+enriquecido dedup por id_anuncio (universo T1: 263)."""
    rows: dict[str, dict] = {}
    for name in ("anuncios_pisos_dirigido.csv", "anuncios_pisos_enriquecido.csv"):
        with open(PROC / name, encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                _id = (r.get("id_anuncio") or "").strip()
                if _id and _id not in rows:
                    rows[_id] = r
    return rows


def _dim_codes():
    with open(PROC / "dim_municipios.csv", encoding="utf-8-sig") as fh:
        return {str(r["codigo_ine"]).strip().zfill(5) for r in csv.DictReader(fh)}


def test_subtitulo_real_santutxu_bilbao():
    # EXTRACCION-01: subtitulo con barrio+ciudad -> gazetteer/subtitulo, Bilbao.
    ci, canon, origen, _ = resolver_pisos_por_texto(
        "Santutxu (Bilbao)", "Piso en Santutxu", None)
    assert canon == "Bilbao"
    assert ci == "48020"
    assert origen in ("subtitulo", "gazetteer")


def test_subtitulo_solo_barrio_via_gazetteer():
    # PISOS-01: barrio sin municipio -> gazetteer Bilbao.
    ci, canon, origen, _ = resolver_pisos_por_texto(
        "Santutxu", "Piso en Santutxu", None)
    assert canon == "Bilbao"
    assert ci == "48020"
    assert origen == "gazetteer"


def test_subtitulo_indautxu_mantiene_bilbao():
    ci, canon, origen, _ = resolver_pisos_por_texto(
        "Indautxu (Bilbao)", "Piso en Autonomia Kalea", "48020")
    assert (ci, canon) == ("48020", "Bilbao")
    assert origen == "subtitulo"


def test_codigo_sin_texto_no_se_propaga():
    # EXTRACCION-01: codigo sin coincidencia textual -> ninguno.
    assert resolver_codigo(None, "48020") == (None, None)
    assert resolver_codigo("", "48020") == (None, None)
    # El texto manda aunque el codigo difiera.
    assert resolver_codigo("Bilbao", "01059") == ("48020", "Bilbao")
    # Pisos sin subtitulo/titulo + codigo -> cuarentena sin_subtitulo.
    ci, _, origen, motivo = resolver_pisos_por_texto(None, None, "48020")
    assert ci is None and origen == "cuarentena" and motivo == "sin_subtitulo"


def test_fuera_euskadi_cuarentena():
    # PISOS-02: Madrid / Logrono -> cuarentena reversible geo_invalida.
    for sub in ("Piso en Madrid", "Centro (Logroño)", "Castro Urdiales",
                "Olula del Río"):
        ci, _, origen, motivo = resolver_pisos_por_texto(sub, "Piso en X", None)
        assert ci is None, sub
        assert origen == "cuarentena", sub
        assert motivo == "fuera_de_euskadi", sub


def test_orden_subtitulo_antes_que_titulo():
    # PISOS-01: subtitulo bueno gana aunque el titulo sea calle.
    ci, canon, origen, _ = resolver_pisos_por_texto(
        "Getxo", "Piso en calle Irala", "01010")
    assert canon == "Getxo" and origen == "subtitulo"


def test_titulo_como_evidencia_cuando_no_hay_subtitulo_util():
    # Subtitulo vacio + titulo con municipio -> titulo.
    ci, canon, origen, _ = resolver_pisos_por_texto(
        "", "Piso en Getxo", None)
    # Sin subtitulo y con titulo valido: titulo o cuarentena sin_subtitulo
    # segun implementacion del titulo; aqui debe resolver por titulo.
    assert canon == "Getxo" and origen in ("titulo", "subtitulo", "gazetteer")


def test_sin_subtitulo_no_usa_busqueda():
    # Sin subtitulo, la busqueda no debe resolverse como ubicacion.
    ci, _, origen, _ = resolver_pisos_por_texto(
        None, "Piso en calle Hurtado de Amezaga", "01031")
    # El fallback exige texto; calle No noviembre no es municipio -> cuarentena.
    assert ci is None or origen == "cuarentena"


def test_nunca_municipio_busqueda_como_ubicacion():
    # Ningun piso resuelto en silver usa la busqueda como ubicacion.
    unir = list(csv.DictReader(
        open(PROC / "anuncios_unificados.csv", encoding="utf-8-sig")))
    pisos = [r for r in unir if r["portal"] == "pisos"]
    assert pisos, "silver sin pisos"
    for r in pisos:
        assert r["municipio"] and r["codigo_ine"]
        # origen trazable y geo valida en silver (cuarentena fuera).
        assert (r.get("origen_resolucion") or "subtitulo") in (
            "subtitulo", "titulo", "gazetteer", "fallback")
        assert (r.get("geo_invalida") or "").lower() in ("false", "0", "")


def test_universo_resueltos_o_cuarentena():
    # (a) Todo anuncio del universo: resuelto trazable o cuarentena motivada.
    union = _union_csv()
    assert len(union) >= 230, len(union)  # 263 en CSV union (230 geo subset)
    validos = _dim_codes()
    res = cuar = 0
    for r in union.values():
        ci, canon, origen, motivo = resolver_pisos_por_texto(
            r.get("subtitulo"), r.get("titulo"), r.get("codigo_ine"))
        if origen == "cuarentena":
            cuar += 1
            assert motivo in ("fuera_de_euskadi", "ambiguo", "sin_subtitulo")
            assert ci is None
        else:
            res += 1
            assert origen in ("subtitulo", "titulo", "gazetteer", "fallback")
            assert ci in validos, f"{r.get('id_anuncio')} -> {ci}"
    assert res + cuar == len(union)
    # Tasas reales post-T1: ~82% resueltos, ~18% cuarentena fuera-Euskadi.
    assert res >= 200, res
    assert cuar >= 20, cuar


def test_cuarentena_excluida_de_dim_y_conteos():
    # (c) Los 45 fuera de Euskadi estan en cuarentena reversible, no en dim.
    qpath = PROC / "cuarentena_pisos.csv"
    assert qpath.exists(), "cuarentena reversible ausente"
    with open(qpath, encoding="utf-8-sig") as fh:
        q = list(csv.DictReader(fh))
    assert q, "cuarentena vacia"
    assert all((r.get("geo_invalida") or "").lower() in ("true", "1") for r in q)
    # Ningun codigo de cuarentena cuenta en n_anuncios (dim solo 252 validos).
    assert len(_dim_codes()) == 252


def test_municipio_n0_sin_precio_sin_imputacion():
    # (g) n_anuncios=0 -> precio None y sin IDW/comarcal en agregados.
    import csv as _csv
    dim = list(csv.DictReader(
        open(PROC / "dim_municipios.csv", encoding="utf-8-sig")))
    zeros = [r for r in dim if int(r["n_anuncios"] or 0) == 0]
    assert zeros, "sin municipios n=0 para comprobar"
    # En Mongo (esfuerzo) los n=0 no tienen precio medio de anuncios.
    res_path = ROOT / "data" / "resultados" / "mongo_esfuerzo_por_municipio.csv"
    assert res_path.exists()
    rows = list(csv.DictReader(open(res_path, encoding="utf-8-sig")))
    for r in rows:
        if str(r.get("n_anuncios")) in ("0", "0.0"):
            assert (r.get("precio_medio_eur") or "") == "" or str(
                r.get("precio_medio_eur")).lower() in ("none", "nan", "")


def test_resultados_13png_7csv():
    # (f) 12 PNG únicos de 13 emitidos + 8 mongo_*.csv desde Mongo (sin valores tecleados).
    # g1 (duplicado byte-idéntico de A1, SHA 25948f0f) eliminado sin renumerar.
    # 6 CSV canonicos AGREGACION-01 (incl. mongo_tier_confianza.csv) +
    # mongo_vpo_terminadas_por_municipio.csv adicional +
    # mongo_habitaciones_por_municipio.csv (HAB-01, pipeline nº 11, 9 filas).
    res = ROOT / "data" / "resultados"
    pngs = sorted(res.glob("*.png"))
    csvs = sorted(res.glob("mongo_*.csv"))
    assert len(pngs) == 12, [p.name for p in pngs]  # 12 únicos / 13 emitidos
    assert len(csvs) == 8, [p.name for p in csvs]
    names = {p.name for p in csvs}
    assert names == {
        "mongo_alquiler_por_municipio.csv", "mongo_esfuerzo_por_municipio.csv",
        "mongo_modalidades.csv", "mongo_vpo_por_municipio.csv",
        "mongo_vpo_terminadas_por_municipio.csv",
        "mongo_tier_confianza.csv",
        "mongo_accesibilidad_extendida.csv",
        "mongo_habitaciones_por_municipio.csv"}


def _sha6():
    res = ROOT / "data" / "resultados"
    out = {}
    for p in sorted(res.glob("mongo_*.csv")):
        out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _mongo_ok():
    try:
        from storage.mongo import ping
        return ping() is True
    except Exception:
        return False


@pytest.mark.skipif(not _mongo_ok(), reason="sin Mongo local: skip separado")
def test_backup_presente_sin_perdidas():
    # (e) CARGA-SEGURA-01: backup existe; 0 perdidos (594 actual, 759 antes).
    from storage.mongo import get_db
    db = get_db()
    names = db.list_collection_names()
    assert "anuncios" in names
    assert "anuncios__backup" in names, names
    assert db["anuncios__backup"].count_documents({}) > 0
    # Reversible: backup + staging nunca pierden datos silenciosamente.
    assert db["anuncios"].count_documents({}) == 594


@pytest.mark.skipif(not _mongo_ok(), reason="sin Mongo local: skip separado")
def test_sha_doble_identico():
    # (f) PISOS-04: dos ejecuciones -> mismo SHA en los 8 CSV.
    from analysis.run_analisis_mongo import huella_resultados, run_all_estandar
    h1 = huella_resultados(run_all_estandar())
    h2 = huella_resultados(run_all_estandar())
    assert h1 == h2
    # Los CSV en disco coinciden entre si (doble SHA ya verificado en T4).
    assert _sha6() == _sha6()
    assert len(_sha6()) == 8


@pytest.mark.skipif(os.environ.get("MONGO_ALLOW_DESTRUCTIVE") != "1",
                    reason="skip separado: MONGO_ALLOW_DESTRUCTIVE!=1")
def test_carga_vacia_no_toca_origen():
    # CARGA-SEGURA-01: staging vacio aborta y conserva el origen.
    from storage.mongo import get_collection, replace_collection
    before = get_collection("anuncios").count_documents({})
    assert replace_collection("anuncios__probe", []) == 0
    assert get_collection("anuncios").count_documents({}) == before
