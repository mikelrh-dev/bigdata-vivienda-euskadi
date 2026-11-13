<!-- cap: 8 | titulo: Límites y verificación | criterios: C8, C16 | estado: borrador -->
# 8. Límites y verificación

> **Objetivo.** Separar lo que el sistema demuestra de lo que solo describe, y dar los comandos que permiten comprobarlo.

## 8.1 Límites de los datos

- La renta es media, no salario juvenil municipal.
- El alquiler oficial no cubre todos los municipios; la interpolación no crea evidencia.
- Los anuncios no representan el parque completo ni el alquiler regulado.
- La capa 2026 y la 2024 no son comparables como serie temporal.
- La VPO es flujo de promoción, no stock disponible.

## 8.2 Límites del método

El proyecto describe asociaciones territoriales, no relaciones causales. Un esfuerzo alto no implica que la causa sea el precio: también dependen la renta, el empleo y la oferta. El tier de confianza ordena la evidencia; no es una medida de calidad de vida.

## 8.3 Verificación

| Comprobación | Comando | Resultado esperado |
|---|---|---|
| Tests | `pytest -q tests` | {{verif.tests_passed}} passed, {{verif.tests_skipped}} skipped |
| Gobernanza | `python scripts/verificar_gobernanza.py` | {{verif.gobernanza_cabeceras}} cabeceras, {{verif.gobernanza_ids}} ids, {{verif.gobernanza_scripts}} scripts |
| Pipeline | `python scripts/run_pipeline.py --check` | {{raw.manifest}} raw + {{silver.manifest}} silver |
| Deck | `python scripts/verificar_cifras_deck.py` | 44/44 |
| Memoria | `python docs/memoria/build.py --check` | tokens y figuras resueltos |
| HDFS | `python scripts/hdfs_recuperacion_un_fichero.py` | `HDFS_REC OK SHA_TAMANO_IGUALES` |

## 8.4 Trabajo futuro

Tres líneas con retorno claro: completar los dos índices 2026, unificar las colecciones de habitaciones y sustituir la renta media por una renta juvenil municipal cuando exista. Ninguna cambia la conclusión; las tres mejoran la confianza.
