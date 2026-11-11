"""Regresiones de la reconstruccion de `data/resultados` desde cero.

Al borrar la capa y ejecutar solo `gold` aparecieron dos defectos que no se
ven en un arbol ya poblado:

1. La figura O se dibujaba distinta (sin IC bootstrap) porque leia un CSV que
   `sensibilidad.py` escribe despues: el resultado dependia del orden.
2. `F_comparativa_th.png` se escribia como `F_comparativa_TH.png`; en Windows
   es el mismo fichero, en Linux serian dos (uno huerfano).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ANALISIS = ROOT / "analysis" / "run_analisis_mongo.py"
FIGURAS = ROOT / "transform" / "generar_figuras_N.py"


def test_f_comparativa_usa_un_unico_nombre():
    """Un nombre en mayusculas distintas duplica el PNG en Linux."""
    for ruta in (ANALISIS, FIGURAS):
        texto = ruta.read_text(encoding="utf-8")
        assert "F_comparativa_TH" not in texto, ruta
        assert "F_comparativa_th.png" in texto, ruta


def test_run_analisis_mongo_no_depende_del_bootstrap_de_sensibilidad():
    """Sin bootstrap en disco la figura O debe calcularlo, no degradarse."""
    texto = ANALISIS.read_text(encoding="utf-8")
    assert "from analysis.sensibilidad import bootstrap_robustos" in texto
    assert "calculado inline" in texto


def test_mapa_esquema_escribe_utf8():
    """pyvis escribia con el locale (cp1252) y dejaba el HTML vacio."""
    texto = (ROOT / "transform" / "generar_mapa_esquema.py").read_text(encoding="utf-8")
    assert 'OUT_FILE.write_text(net.generate_html' in texto
    assert 'encoding="utf-8"' in texto
