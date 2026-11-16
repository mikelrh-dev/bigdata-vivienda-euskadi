<!-- cap: 8 | titulo: Límites y verificación | criterios: C8, C16 | estado: borrador -->
# 8. Límites y verificación

> El capítulo separa lo que el sistema demuestra de lo que solo describe y reúne los comandos que permiten comprobarlo.

## 8.1 Límites de los datos

- La renta es media y de hogar, no per cápita ni salario juvenil municipal; no se ajusta por tamaño del hogar.
- El alquiler oficial no cubre todos los municipios; la interpolación no crea evidencia.
- El ratio de edad es autonómico: la renta joven de un municipio se mueve con su renta, no con su estructura de edad.
- El nivel de renta es neto (INE Atlas); el perfil de edad se calcula con renta personal total (bruta) de Eustat. Con `Renta disponible` (neta) el ratio sería 57,4 % y el esfuerzo bajaría ~0,8 %.
- El campo `nivel_geografico` de las filas imputadas dice `comarcal` por herencia del nombre; el método es distancia entre centroides, no una media de comarca.
- El IPC de 2026 es la media anual disponible en el corte, no el cierre del año.
- El área funcional se asigna por el centroide del municipio: uno que cruce dos áreas se queda con la del centro.
- Los anuncios no representan el parque completo ni el alquiler regulado.
- La capa 2026 y la 2024 no son comparables como serie temporal.
- La VPO es flujo de promoción, no stock disponible; el indicador es un acumulado de cinco años (2020-2024), no el flujo de 2024.
- La cuarentena de 2026 es geolocalización dudosa, no una certeza de que los 45 estén fuera de Euskadi.

## 8.2 Límites del método

El proyecto describe asociaciones territoriales, no relaciones causales. Un esfuerzo alto no implica que la causa sea el precio: también dependen la renta, el empleo y la oferta. El tier de confianza ordena la evidencia; no es una medida de calidad de vida.

## 8.3 Verificación

| Comprobación | Comando | Resultado esperado |
|---|---|---|
| Tests | `pytest -q tests` | {{verif.tests_passed}} passed, {{verif.tests_skipped}} skipped ({{verif.tests_collected}} recogidos) |
| Gobernanza | `python scripts/verificar_gobernanza.py` | {{verif.gobernanza_cabeceras}} cabeceras, {{verif.gobernanza_ids}} ids, {{verif.gobernanza_scripts}} scripts, {{verif.gobernanza_dag}} nodos |
| Manifiestos | `python scripts/run_pipeline.py --check` | {{raw.manifest}} raw + {{silver.manifest}} silver, 0 errores |
| Deck | `python scripts/verificar_cifras_deck.py` | {{verif.deck_checks}}/{{verif.deck_checks}} |
| Memoria | `python docs/memoria/build.py --check` | tokens y figuras resueltos |
| HDFS | `python scripts/hdfs_recuperacion_un_fichero.py` | `HDFS_REC OK SHA_TAMANO_IGUALES` |
| Índices | `python analysis/mongo_indexes.py` | `COLLSCAN` 594 → `IXSCAN` 1 |
| Silver | `python transform/run_all.py --check` | 1 laguna: `auditoria_lagunas_silver.csv` |

`run_pipeline.py --check` es una comprobación previa de hashes, no una ejecución completa: comprueba que el manifiesto de raw y el de silver cuadran con el disco. La comprobación de staleness de silver es la de `transform/run_all.py --check`, y esa sí tiene una laguna declarada.

## 8.4 Trabajo futuro

Tres mejoras pendientes: completar los dos índices 2026, unificar las colecciones de habitaciones y sustituir la renta de hogar por una renta juvenil municipal cuando exista. Ninguna cambia la conclusión.
