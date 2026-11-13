# Índice de documentación — BigData Vivienda Euskadi

`docs/` conserva solo lo que el repositorio necesita para ejecutarse y defenderse.

| Ruta | Qué es |
|---|---|
| `raw_manifest_sha256.txt` | SHA-256 canónico de los 355 ficheros raw. Lo leen `scripts/gate_extremo_a_extremo.py`, `scripts/verificar_fase_datos.py`, `extract/generar_manifest.py` y `tests/test_raw_inmutable.py`; no se mueve. |
| `presentacion/` | Deck de defensa v1 (13 diapositivas, PDF y assets). Ver `presentacion/README.md`. |
| `presentacion_v2/` | Deck v2 (22 diapositivas + 8 backups), guion y PDF. Ver `presentacion_v2/README.md`. |
| `matriz-comparabilidad.md` | Matriz de comparabilidad entre fuentes y años. |

## Dónde está el resto

- **Referenciado por el contrato, el README raíz o el propio código** → `openspec/archive/2026-11-10-docs/`: `modelo_mongodb.md`, `matriz_indicadores.md`, `guion_defensa.md`, `guion_defensa_12min.md`, `conclusiones_municipios.md`, `trazabilidad_vm.md`, `datos_finales_conclusiones_2026-11-05.md`, `informe_final.md`, `contrato_datos_raw.md`, `arquitectura_datos.md`, `diccionario_columnas.md`, `reglas_limpieza.md`. Las rutas de `openspec/specs/` y del `README.md` raíz ya apuntan a esa carpeta.
- **Sin dependencias de contrato, código ni CI** → archivo local no versionado, fuera del repositorio (`archiveVivienda/archive/2026-11-limpieza/docs/`): `metodologia.md`, `informe_capacidad_mongo.md`, `preguntas_analisis_profesional.md`.
- El histórico antiguo (planes, auditorías y versiones) sigue en ese mismo archivo local externo.
