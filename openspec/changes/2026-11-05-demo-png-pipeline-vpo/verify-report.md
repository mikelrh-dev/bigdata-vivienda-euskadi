# Verify Report: demo-png-pipeline-vpo

Fecha: 2026-11-05 · Rama: `cierre/suficiencia-auditoria`

## Resultado

**PASS** con una desviación de alcance declarada (no se añadió CSV nuevo).

## Evidencia

| Check | Comando | Resultado |
|---|---|---|
| Tests | `pytest tests -q` | **136 passed** (5,24 s) |
| Manifests | `generar_manifest.py --verify` | 354 raw + 185 silver, **0 errores** |
| Check cadena | `run_all.py --check` | **exit 0**, sin avisos |
| Gate | `verificar_fase_datos.py` | **OK 18/18** |
| Pipeline VPO | `pipeline_vpo_terminadas()` | **251 filas**, top Berango 62,55 ‰ |
| Pipelines | `run_all_estandar()` | **9** claves |
| Huella | `huella_resultados` | `08665d03687bbbde663831de8872d129983252de1881027a2e243bfd86f4c30a` |
| Reproducibilidad | dos ejecuciones | huella idéntica |
| PNG | `exportar_png_desde_mongo` | **13 ficheros**, 0 con tamaño <1 KB |

## Causa raíz del PNG

```
File ".../PIL/Image.py", line 2707, in save
    fp = builtins.open(filename, "w+b")
OSError: [Errno 22] Invalid argument:
'data\\resultados\\g5_esfuerzo_robustos.png'
```

PIL recibe una ruta relativa de matplotlib y `open` la rechaza en Windows,
aunque el mismo `open` desde Python puro funciona. Se guarda en `BytesIO` y se
escribe con `Path.write_bytes`, que resuelve la ruta en Python.

**Nota de honestidad:** la sonda de diagnóstico abrió los 13 PNG en `w+b`, lo
que los truncó a 0 bytes. Se regeneraron en la misma sesión y se verificó que
ninguno quedó vacío (`find -size -1k` → 0). Los PNG no están versionados.

## Demo cronometrada

| Paso | Tiempo |
|---|---|
| `generar_manifest.py --verify` | 2,101 s |
| `run_all.py --check` | 0,167 s |
| `pytest tests -q` | 5,24 s |
| `run_analisis_mongo.py` (9 pipelines + 5 CSV + 13 PNG) | 2,497 s |
| `analysis/sensibilidad.py` | 1,208 s |
| `verificar_fase_datos.py` | 3,396 s |
| **Total** | **≈ 15 s** |

## Desviaciones

- **D-01:** no se añadió `mongo_vpo_terminadas.csv`. El pipeline entra en la
  huella, pero el contrato de 5 CSV canónicos no cambia (decisión de design).
- **D-02:** los documentos de auditoría fechados (`auditoria_10_10`,
  `pendiente_duckdb`) conservan la huella antigua: son instantáneas, no docs
  vivos.

## Limitaciones

- La huella cambió respecto a `d7e673…`: cualquier material externo que cite
  la anterior queda obsoleto.
- `vpo_terminadas_por_mil` es flujo 2020-2024; no se infiere stock.
