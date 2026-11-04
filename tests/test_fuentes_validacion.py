"""Gate de join previo para fuentes nuevas."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fuentes_gate():
    r = subprocess.run([sys.executable, "scripts/validar_fuentes_nuevas.py"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    # Bandas 0-19/20-64 no derivan 15-29: se marca baja
    assert "poblacion_15_29_derivable False" in r.stdout
    # Renta edad sin ambito municipal: baja
    assert "renta_edad_municipal False" in r.stdout
    # Sin raw Alokabide: cobertura cero
    assert "alokabide_cobertura 0" in r.stdout
