# `transform/` — `raw` → `data/procesado` (silver y gold)

## El DAG

`run_all.py` es el orquestador. Los pasos se declaran en `SCRIPTS` por **nombre de fichero** y se resuelven contra esta carpeta (`TRANSFORM_DIR`).

→ Mover un script fuera de `transform/` rompe el DAG aunque el código sea idéntico.

Cada entrada declara `in` / `out`, de modo que se puede comprobar que nadie lee algo que nadie escribe.

## Todo fichero debe estar en `SCRIPTS` o en `EXCLUIDOS`

`EXCLUIDOS`, al final de `run_all.py`, es la lista de lo que queda fuera del pipeline **con motivo obligatorio**. `scripts/verificar_gobernanza.py` exige 47 scripts y 40 nodos DAG: si añades uno, actualiza el número o quedará fuera de la comprobación.

## Nombres que engañan (y por qué están aquí)

| Fichero | Qué hace de verdad |
|---|---|
| `f4_pisos_dirigido.py` | Captura dirigida **manual**: escribe en `data/raw` con guard, no en procesado. Está en `EXCLUIDOS` y `verificar_fase_datos.py` le da trato especial |
| `validar_renta.py` | No es un verificador del gate: produce `renta_municipal_referencia.csv`, que consume el análisis. **Es nodo del DAG** |
| `auditar_lagunas_silver.py` | Auditoría de cobertura de silver. Escribe `data/resultados/auditoria_lagunas_silver.csv` |

## Siete scripts no se pueden importar

Sin `if __name__ == "__main__"`, ejecutan el pipeline entero al importarse:

`asignar_area_funcional_ecvi.py`, `enriquecer_equipamiento_realtyapi.py`, `generar_analisis_variables_base.py`, `generar_emancipacion_tier3_93.py`, `generar_fingerprint.py`, `generar_municipios_faltantes_93.py`, `generar_poblacion_joven_municipal.py`.

Funciona porque `run_all` los lanza como subproceso. Si alguna vez necesitas importarlos, envuélvelos en `main()` primero.

Librerías legítimas, sin efectos al importar: `_anuncios_2026.py`, `_raw_guard.py`, `muni_resolve.py`.
