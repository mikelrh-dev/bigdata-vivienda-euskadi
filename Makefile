
# Makefile — Windows (.venv). Mongo local localhost:27017;
# HDFS/Kafka centro solo en vivo manana con GATE_LIVE=1.

PY=.venv/Scripts/python.exe

test:
	$(PY) -m pytest tests -q

gate-offline:
	$(PY) scripts/gate_extremo_a_extremo.py --offline

gate-vivo:
	GATE_LIVE=1 $(PY) scripts/gate_extremo_a_extremo.py --vivo

verify: test gate-offline

.PHONY: test gate-offline gate-vivo verify
