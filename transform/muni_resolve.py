"""Helper de resolucion de municipios para unificar_anuncios.

PISOS-RE-RESOLVER-UBICACION: el texto (subtitulo/titulo/municipio) manda.
`codigo_ine` SIN coincidencia textual NO se propaga (None, None).
Pisos resuelve solo por subtitulo/titulo + gazetteer; municipio_busqueda
NUNCA es ubicacion. Lo no resuelto -> cuarentena geo_invalida=True.
"""
from __future__ import annotations
import difflib
import os
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESADO_DIR, RAW_DIR  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "extract"))
from entity_resolution import norm, MANUAL_MAP  # noqa: E402

RAW = str(RAW_DIR)


def _load_dim():
    _src = str(PROCESADO_DIR / "dim_municipios.csv")
    dim = pd.read_csv(_src, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    code2name = dict(zip(dim["codigo_ine"], dim["nombre_canonico"]))
    name2code = {}
    for _, r in dim.iterrows():
        name2code.setdefault(norm(r["nombre_canonico"]), r["codigo_ine"])
        for v in str(r.get("variantes", "")).split("|"):
            v = v.strip()
            if v:
                name2code.setdefault(norm(v), r["codigo_ine"])
    # PISOS-01: alias orden inverso + variantes de busqueda frecuente.
    _extra_aliases = {
        "san sebastian": "Donostia / San Sebastián",
        "san sebastian donostia": "Donostia / San Sebastián",
        "donostia san sebastian": "Donostia / San Sebastián",
        "abanto zierbena": "Abanto y Ciérvana-Abanto Zierbena",
        "abanto": "Abanto y Ciérvana-Abanto Zierbena",
    }
    for _key, _canon in _extra_aliases.items():
        _cn = norm(_canon)
        if _cn in name2code:
            name2code.setdefault(norm(_key), name2code[_cn])
    return code2name, name2code, set(dim["codigo_ine"])


CODE2NAME, NAME2CODE, VALID_CODES = _load_dim()

# Municipios fuera de Euskadi observados en el corpus pisos (no estan en dim 252).
FUERA_EUSKADI = {
    norm("Logroño"),
    norm("Castro Urdiales"),
    norm("Ampuero"),
    norm("Olula del Rio"),
    norm("Navarrete"),
    norm("Madrid"),
    norm("Cantabria"),
    norm("La Rioja"),
    norm("Villamediana de Iregua"),
    norm("Fines"),
    norm("Nájera"),
    norm("Pravia"),
    norm("Salas"),
    norm("Xunqueira de Espada"),
    norm("Cutielles"),
    norm("Gibaja"),
    norm("Buigueta"),
    norm("Condado de Treviño"),
}

# Gazetteer barrio -> municipio canonico (verificado contra dim 252).
# None = barrio fuera de Euskadi (cuarentena motivada).
GAZETTEER_RAW = {
    "santutxu": "Bilbao",
    "indautxu": "Bilbao",
    "basurtu": "Bilbao",
    "abando": "Bilbao",
    "casco viejo": "Bilbao",
    "zazpi kaleak": "Bilbao",
    "bilbo zaharra": "Bilbao",
    "ametzola": "Bilbao",
    "iralabarri": "Bilbao",
    "atxuri": "Bilbao",
    "begona": "Bilbao",
    "deusto": "Bilbao",
    "olabeaga": "Bilbao",
    "zurbaran arabella": "Bilbao",
    "matiko loruri": "Bilbao",
    "uribarri": "Bilbao",
    "altamira": "Bilbao",
    "masustegi mintegixueta": "Bilbao",
    "areeta": "Getxo",
    "algorta": "Getxo",
    "neguri aiboa": "Getxo",
    "andra mari": "Getxo",
    "amara": "Donostia / San Sebastián",
    "amara berri": "Donostia / San Sebastián",
    "egia": "Donostia / San Sebastián",
    "gros": "Donostia / San Sebastián",
    "antiguo ondarreta": "Donostia / San Sebastián",
    "parte vieja alde zaharra": "Donostia / San Sebastián",
    "ategorrieta ulia": "Donostia / San Sebastián",
    "peñota san juan de dios": "Santurtzi",
    "san juan de dios": "Santurtzi",
    "mamariga la sardinera": "Santurtzi",
    "arteagabeitia retuerto kareaga": "Barakaldo",
    "olakueta": "Berriz",
    "gandia": "Gorliz",
    "campa": "Urduliz",
    "camping oliden": "Lezo",
    "larrabasterra": "Sopela",
    "el campillo": "Abanto y Ciérvana-Abanto Zierbena",
    "astrabudua": "Erandio",
    "alonsotegui": "Alonsotegi",
    "san mames": "Zierbena",
    "larrauri": "Mungia",
    "el castano": "Sopuerta",
    "gautegiz arteaga": "Gautegiz Arteaga",
    "erdialdea alde zaharra mendibil santiago": "Irun",
    "santurtziko parkea txitxarra": "Santurtzi",
    "san adrian la cava el arco": None,
    "universidad los lirios": None,
    "portillejo valdegastea": None,
    "cascajos piqueras": None,
    "brazomar": None,
    "samano": None,
    "cotolino": None,
    "playa ostende": None,
    "la aparecida": None,
}

GAZETTEER = {norm(k): v for k, v in GAZETTEER_RAW.items()}


def _extraer_parentesis(sub):
    """(barrio_antes, hint_dentro) para 'Barrio (Muni)'; hint tras ultimo punto."""
    if not sub:
        return None
    m = re.search(r"\(([^)]+)\)", str(sub))
    if not m:
        return None
    inside = m.group(1).strip()
    before = str(sub)[: m.start()].strip(" ,")
    hint = inside.rsplit(".", 1)[-1].strip() if "." in inside else inside
    return before, hint


def _norm_code(codigo_ine):
    if codigo_ine is None:
        return None
    s = str(codigo_ine).strip()
    if s.isdigit():
        s = s.zfill(5)
    return s if s else None


def resolver_pisos_por_texto(subtitulo, titulo, codigo_ine=None):
    """Orden PISOS-01: (1) subtitulo, (2) titulo, (3) gazetteer, (4) fallback,
    (5) cuarentena. municipio_busqueda NUNCA entra; codigo_ine solo vale con
    coincidencia textual.

    Devuelve (codigo_ine, nombre_canonico, origen_resolucion, motivo).
    origen en {subtitulo, titulo, gazetteer, fallback, cuarentena}; motivo
    en {fuera_de_euskadi, ambiguo, sin_subtitulo} cuando es cuarentena.
    """
    sub = (subtitulo or "").strip() if subtitulo is not None else ""
    tit = (titulo or "").strip() if titulo is not None else ""
    if sub:
        par = _extraer_parentesis(sub)
        if par and par[1]:
            hint = par[1]
            key = norm(hint)
            if key in NAME2CODE:
                c = NAME2CODE[key]
                return c, CODE2NAME.get(c), "subtitulo", ""
            if key in MANUAL_MAP:
                canon = MANUAL_MAP[key]
                for c, n in CODE2NAME.items():
                    if n == canon:
                        return c, n, "subtitulo", ""
            if key in FUERA_EUSKADI:
                return None, None, "cuarentena", "fuera_de_euskadi"
            if par[0] and norm(par[0]) in FUERA_EUSKADI:
                return None, None, "cuarentena", "fuera_de_euskadi"
        key_sub = norm(sub)
        if key_sub in NAME2CODE:
            c = NAME2CODE[key_sub]
            return c, CODE2NAME.get(c), "subtitulo", ""
        if key_sub in MANUAL_MAP:
            canon = MANUAL_MAP[key_sub]
            for c, n in CODE2NAME.items():
                if n == canon:
                    return c, n, "subtitulo", ""
        if key_sub in FUERA_EUSKADI:
            return None, None, "cuarentena", "fuera_de_euskadi"
        # Subtitulo con prefijo tipo 'Piso en X' (scenario PISOS-02: Madrid).
        _m_pref = re.match(r"^(piso|apartamento|casa|chalet|estudio|duplex|atico)\s+en\s+(.+)$", sub, flags=re.I)
        if _m_pref:
            _tail = _m_pref.group(2).strip()
            _kt = norm(_tail)
            if _kt in NAME2CODE:
                c = NAME2CODE[_kt]
                return c, CODE2NAME.get(c), "subtitulo", ""
            if _kt in FUERA_EUSKADI:
                return None, None, "cuarentena", "fuera_de_euskadi"
    if tit:
        m = re.search(r"\ben\s+(.+)$", tit, flags=re.I)
        if m:
            cand = m.group(1).strip()
            low = norm(cand)
            if not any(low.startswith(p) for p in (
                "calle", "avenida", "paseo", "camino", "carretera",
                "travesia", "rue", "disponible", "plaza", "parque",
            )) and not re.match(r"^\d", cand):
                key_c = norm(cand)
                if key_c in NAME2CODE:
                    c = NAME2CODE[key_c]
                    return c, CODE2NAME.get(c), "titulo", ""
                if key_c in MANUAL_MAP:
                    canon = MANUAL_MAP[key_c]
                    for c, n in CODE2NAME.items():
                        if n == canon:
                            return c, n, "titulo", ""
                if key_c in FUERA_EUSKADI:
                    return None, None, "cuarentena", "fuera_de_euskadi"
    candidatos = []
    par = _extraer_parentesis(sub) if sub else None
    if par and par[0]:
        candidatos.append(par[0])
    if sub and "(" not in sub:
        candidatos.append(sub)
    if tit:
        m = re.search(r"\ben\s+(.+)$", tit, flags=re.I)
        if m:
            candidatos.append(m.group(1).strip())
    for c in candidatos:
        if not c:
            continue
        key = norm(c)
        if key in GAZETTEER:
            canon = GAZETTEER[key]
            if canon is None:
                return None, None, "cuarentena", "fuera_de_euskadi"
            ck = norm(canon)
            if ck in NAME2CODE:
                cc = NAME2CODE[ck]
                return cc, CODE2NAME.get(cc), "gazetteer", ""
            for cc, nn in CODE2NAME.items():
                if nn == canon:
                    return cc, nn, "gazetteer", ""
        for gk, gcv in GAZETTEER.items():
            if gk and key.startswith(gk) and len(gk) >= 6:
                if gcv is None:
                    return None, None, "cuarentena", "fuera_de_euskadi"
                ck = norm(gcv)
                if ck in NAME2CODE:
                    cc = NAME2CODE[ck]
                    return cc, CODE2NAME.get(cc), "gazetteer", ""
                for cc, nn in CODE2NAME.items():
                    if nn == gcv:
                        return cc, nn, "gazetteer", ""
    cine = _norm_code(codigo_ine)
    if cine and cine in CODE2NAME:
        canon = CODE2NAME[cine]
        cn = norm(canon)
        if cn and (cn in norm(sub) or cn in norm(tit)):
            return cine, canon, "fallback", ""
    if not sub:
        return None, None, "cuarentena", "sin_subtitulo"
    return None, None, "cuarentena", "ambiguo"


def resolver_codigo(municipio, codigo_ine):
    """Resuelve (codigo_ine, canonico) SOLO por coincidencia textual.

    EXTRACCION-01: codigo_ine sin texto no vale -> (None, None).
    Si el texto resuelve, manda el texto (aunque el codigo difiera).
    `codigo_ine` solo corrobora cuando es igual al textual.
    """
    if municipio is None:
        return None, None
    texto = str(municipio).strip()
    if not texto:
        return None, None
    key = norm(texto)
    if key in MANUAL_MAP:
        canon = MANUAL_MAP[key]
        for c, n in CODE2NAME.items():
            if n == canon:
                return c, n
    if key in NAME2CODE:
        c = NAME2CODE[key]
        return c, CODE2NAME.get(c)
    best_score = 0.0
    best = None
    for c, n in CODE2NAME.items():
        score = difflib.SequenceMatcher(None, key, norm(n)).ratio()
        if score > best_score:
            best_score = score
            best = (c, n)
    if best and best_score >= 0.85:
        return best
    return None, None