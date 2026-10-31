# Spec: Fase datos 10/10 — ejecución

## Objective

Cerrar la fase de obtención + transformación al 10/10 medible: fila Extracción al 10,
requisitos binarios (formato, complementarios, limpieza-parte-pandas) demostrables,
y base analítica sin errores conocidos. No incluye HDFS/Kafka/Mongo/informe.

Lectura obligatoria previa: `openspec/audit/contrauditoria_2026-10-31.md` (§2 veredicto,
§6 paquetes WP-15…WP-20) y `openspec/audit/plan_10_10_datos_2026-10-31.md` (WP-01…WP-14).

## Tech Stack

Python 3.12 (`.venv`), pandas 2.2.3, pytest 8.3.3. Sin dependencias nuevas.

## Commands

```bash
.venv/Scripts/python.exe -m pytest -q                      # batería completa
.venv/Scripts/python.exe transform/run_all.py --check       # staleness por script
.venv/Scripts/python.exe openspec/audit/verificar_fase_datos.py  # gate 15/15
```

## Project Structure

```text
transform/            → silver; cada script declara in/out en run_all.SCRIPTS
transform/_io.py      → helper read_csv (dtype=str, utf-8-sig) — nuevo
transform/construir_dim_gold.py → join final dim+renta+tensión — nuevo
transform/aplicar_cobertura_mercado.py → n_anuncios real + tipología — nuevo
extract/generar_manifest.py → manifests raw+silver con --verify — nuevo
extract/normalizar_metadata.py → sidecars _meta/index.json — nuevo
data/procesado/       → única salida de transform/
data/raw/             → NO TOCAR (solo WP-08 con protocolo)
tests/test_fase_datos.py → 19 tests nuevos — nuevo
openspec/audit/verificar_fase_datos.py → gate 15 invariantes — nuevo
docs/reglas_limpieza.md → reglas portables a PyMongo (WP-20) — nuevo
```

## Code Style

- Un escritor por fichero de salida; el dueño se declara en `SCRIPTS[out]`.
- Nombres de columna nuevos con sufijo de unidad (`_pct`, `_pp`, `_eur`).
- Flags de calidad como columnas (`*_valida`, `*_origen`, `nivel_fiabilidad`), nunca comentarios.
- `log.warning`, nunca `except: pass` silencioso en código tocado.

## Testing Strategy

- pytest; cada WP trae su test antes de darse por cerrado (rojo→verde).
- Tests existentes que medían mal se sustituyen por mediciones más estrictas, no se borran.
- Gate final `verificar_fase_datos.py`: solo lectura, <10 s, exit 1 si algo falla.
- Tras cada bloque: `pytest -q` en verde. Si un WP rompe algo, se revierte el WP.

## Boundaries

- Always: pytest en verde tras cada bloque; verificar con sonda antes de afirmar una cifra.
- Ask first: tocar `data/raw` (solo WP-08, con protocolo thaw→verificar→re-freeze anunciado).
- Never: reescribir raw, simular valores, `git push`, borrar tests para que pasen, instalar dependencias.

## Success Criteria

1. `run_all.py --check` OK desde `data/procesado` vacío (se regenera todo).
2. `pytest -q` → ~85 passed.
3. Gate 15/15 OK, exit 0.
4. Manifest raw 316/316 verificado tras los cambios.
5. `git status` limpio de cambios no declarados; commits locales por bloque.

## Open Questions

Ninguna bloqueante. Decisiones tomadas: canónico = esfuerzo fiscal municipal (WP-06;
revoca M-01 de la auditoría rev.2); IDW no se recaptura (D7); Mongo re-hará la
limpieza con PyMongo (WP-20 deja las reglas portables).
