# Huecos declarados

Nada de lo que sigue se ha cubierto. Se declara para que no se lea como «verificado».

| ID | Hueco | Motivo | Qué haría falta | Riesgo |
|---|---|---|---|---|
| G-01 | HDFS en vivo (recuperación, `GETCONTENTSUMMARY`, `/data/procesado`) | TCP timeout a `10.22.87.215:50070`; DNS de `hadoop-*.tartangalh.eus` no resuelve fuera del centro | Estar en la red el lunes | C2 se queda en 7 |
| G-02 | Verificación de fuentes externas (definición de alquiler Eustat, salario OVJ, paro Lanbide vs EPA, umbral 30 %, IDW de 5 vecinos, IPC 2024→2026) | No ejecutada: prioridad a la coherencia interna y al código | 6 consultas a fuente primaria con enlace y fecha | Una definición mal citada en defensa no se detectaría |
| G-03 | Kafka en vivo (lag real, consumidor) | TCP timeout a `:9092` | Igual que G-01 | C3 se apoya en evidencia histórica |
| G-04 | `explain()` «antes» (COLLSCAN) | Exigiría borrar/recrear el índice: mutación prohibida | `hint()` o una copia en base temporal | C13 verificado solo en el lado «después» |
| G-05 | `verificar_reproducibilidad.py` y regeneración del gold en dos pasadas | Regenera 55 artefactos en temporal; se hereda la evidencia de v12 (huella `983fa53f…`) | Ejecutarlo si se quiere huella de hoy | La huella citada es de v12, no recalculada hoy |
| G-06 | Barrido completo de `docs/memoria/memoria.md` y del PDF de la memoria | Solo se leyeron las secciones con cifras y tests | Lectura íntegra línea a línea | Puede quedar alguna cifra stale fuera de las secciones revisadas |
| G-07 | Seguridad más allá del índice de git | Solo se comprobó `.gitignore` y `git ls-files` | Historial completo (`git log -p`) y escaneo de secretos | Un secreto en un commit antiguo no se habría visto |
| G-08 | Rendimiento medido | No se hicieron benchmarks | `time` de cada fase del pipeline | No se puede afirmar ni negar «es rápido» |
| G-09 | Portabilidad fuera de Windows | Todo se ejecutó en el entorno local | Prueba en Linux | `osrm`, rutas y `pymupdf` podrían diferir |
| G-10 | Clon limpio end-to-end | No se hizo: el corpus no está versionado (H-14) | Clon en `%TEMP%` + montar raw desde HDFS | No se sabe si el README basta para un tercero |

## Huecos de la rúbrica (no de la auditoría)

Ninguno: los 19 criterios y los 7 de Tema 8 tienen evidencia o una razón explícita de nota.
