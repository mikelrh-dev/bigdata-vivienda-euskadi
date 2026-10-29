# Radiografía del proyecto — bigdata-vivienda-euskadi (para Argon)

Carpeta preparada para que otra IA (Argon) tenga el estado actual del proyecto sin acceder al repo completo.

## Archivos principales (raíz de argon/)

- `README_proyecto.md` — visión general, cómo ejecutar, estructura.
- `estado_proyecto_2026-10-29.md` — estado actual: raw inmutable, silver regenerado, tests, deuda, próximos pasos.
- `informe_preguntas_respuesta.md` — 42 preguntas con archivos concretos, conclusiones y puntuación 0–10 (media 8.24).
- `preguntas_analisis_profesional.md` — preguntas objetivo del reto (obligatorias + bloques A–G).
- `inventario_datos.md` — inventario de 325 archivos crudos (raw + procesado pre-Fase 1).
- `metodologia.md` — fórmulas y metodología.
- `trazabilidad_datos.md` — trazabilidad de datos.
- `plan_silver_sin_tocar_raw.md` — plan de silver sin tocar raw.
- `contrato_reto_spec.md` — contrato OpenSpec del reto (requisitos formales).

## Subcarpetas

- `audit/` — auditorías multiagente (puntuaciones por fuente, reauditorías).
- `openspec_change/` — change fase1-obtencion-procesado (proposal, design, spec, tasks, verify-report).

## Resumen rápido para veredicto

- **Raw**: inmutable, 301 archivos, congelado (`.FROZEN`), manifest SHA-256, test en verde.
- **Silver**: 88 archivos regenerados, byte-idénticos (MD5) al backup, 0 regresiones.
- **Tests**: 59 passed.
- **Preguntas**: 42 evaluadas, media 8.6/10; 6 preguntas ≤7 requieren más datos.
- **Deuda**: entity resolution aún en raw (mover a silver), renta joven proxy, cobertura parcial ECVI/EMAL/SERPAVI, infraestructura Docker pendiente.

## Lo que NO está aquí (consultar repo si se necesita)

- Código: `extract/`, `transform/`, `tests/`.
- Datos: `data/raw/`, `data/procesado/`.
- Configuración: `config/parametros_estudio.yaml`, `requirements.txt`.
