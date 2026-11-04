# 06 · Readiness Mongo + infra — dejar silver lista para no re-trabajar

> NADA de esto se exige implementado. Se puntúa `DIFERIDO readiness ✅/⚠️/❌`. Un ❌ hoy = re-trabajo mañana = P2.

## Contrato silver → Mongo (10 checks)

1. **Join key:** `codigo_ine` 5 dígitos string en TODAS las tablas silver que crucen a municipio. Sin joins por nombre.
2. **Tipos BSON:** números como número o string canónico documentado; fechas ISO (`YYYY-MM-DD`); booleanos reales; nada de `"1.200,50"` ni `"NULL"` texto.
3. **Anidados consultables:** ubicación como objeto (`ubicacion.codigo_ine`, `ubicacion.municipio`) o documentado por qué plano.
4. **Arrays estables:** `historico_precios` o equivalente posible (precio + fecha); ningún array que crezca sin límite sin criterio (DOCX §5).
5. **Identidad:** `id_anuncio` + `property_fingerprint` + `portal` estables → idempotencia Kafka→Mongo futura (`upsert` sin duplicar).
6. **Limpieza portable:** reglas de `docs/reglas_limpieza.md` expresables como `update_many` con pipeline (`$set/$unset/$convert`), no solo pandas exótico.
7. **Consultas candidatas:** ≥2 preguntas reales que usen anidados + arrays (ej. "municipios con esfuerzo <30% y ≥5 anuncios, ordenados por tiempo a capital").
8. **Pipeline candidato:** un indicador que encadene `$match→$lookup→$unwind→$group→$sort` sin re-limpieza (joins no pierden municipios).
9. **Índice + shard candidatos:** 1 consulta con filtro+orden que justifique índice compuesto (ESR); 1 campo candidato a shard key con análisis de cardinalidad (p.ej. `codigo_ine` vs `portal`) — conceptual, no implementado.
10. **Transacción:** análisis escrito de si hace falta (DOCX §11): si todo cabe en un documento → atomicidad documental basta; si hay multi-documento crítico → caso + `commit/abort` futuro. No forzar transacción artificial.

## HDFS / Kafka readiness (2 checks)

- Layout `data/raw/` vs `data/procesado/` + manifest con SHA/tamaño = espejo futuro `/raw` vs `/procesado` en HDFS + prueba de recuperación local.
- Anuncios con identidad estable (punto 5) = productor/consumer idempotente mañana.

## Salida

Tabla `check | ✅/⚠️/❌ | evidencia (fichero:línea o conteo)` + frase: "Mongo puede cargarse sin re-limpiar: SÍ/NO, porque ___."
