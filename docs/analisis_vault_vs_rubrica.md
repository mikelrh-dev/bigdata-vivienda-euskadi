# Análisis vault vs reto + rúbrica — guardar para revisar (2026-11-05)

> **Histórico (2026-11-05).** Este análisis usa las cifras del pre-change
> (759 anuncios, 151 tests, 9 pipelines, 28 resultados). La auditoría vigente
> está en `vaultVivienda/vault-tecnico/06-Defensa/04-auditoria-vault-vs-reto-2026-11-08.md`.

Fuente de verdad: `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (BDA RA1 4 criterios, SBD RA1 46,7%, RA3 13,3%, RA4 40%) + `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` (§4-17) + `openspec/specs/contrato-reto/spec.md` (27 requisitos, P-01..P-08, canónico 18-34).

## Veredicto global

- Vault-data (qué hay y qué concluir): muy bueno, defendible a nivel teórico.
- Vault-tecnico (cómo funciona y rúbrica v2 + Tema 8): con huecos críticos de defensa.
- Nota global tras arreglos del 05-11: **7,8/10** (ver tabla de puntuación abajo).

## Cambios ya aplicados el 05-11 (solo vault, sin código)

1. `vault-tecnico/01-Arquitectura/00-reto-que-hay-que-demostrar.md`: r paro +0,385 conteos (+0,146 tasas), r renta-alquiler 0,2094 canónico; trazabilidad a 4 notas nuevas + aviso P-05.
2. `vault-data/04-Resultados/01-metricas-canonicas.md`: salarios separados (1381/1564 observados OVJ vs 1402 derivado ±15% a ojo).
3. `vault-tecnico/03-Transformacion/05-alquiler-y-outliers.md`: ratio media-simple 0,353 marcada legacy; canónica ponderada `(2*1599+5*8156+5*20109+5*25609)/17/28170`.
4. `vault-tecnico/01-Arquitectura/07-modelo-mongo-13-colecciones.md`: "imputado comarcal" → IDW 5 vecinos.
5. `vault-tecnico/04-Salidas/02-graficos-y-visuales.md`: A-G por `generar_dashboard_completo.py`, g1-g5 por `generar_dashboard_visual.py` (estaba cruzado).
6. `vault-data/03-Silver/05-variables-base.md`: 16_29 legacy / 18_34 canónico; población estimada etiquetada.
7. `vault-data/05-Conclusiones/02-limitaciones-y-gaps.md`: 355 raw (353 hash, 351 HDFS sin legacy) / 185 silver.
8. `vault-data/03-Silver/03-anuncios-limpios.md`: aritmética 471+230+139=840 → 759; RealtyAPI 139.
9. `vault-data/04-Resultados/02-graficos-y-dashboards.md`: HTML manuales marcados P-05; evidencia RA4 válida = 4 CSV auto.
10. Nuevas: `11-consistencia-transacciones.md`, `12-indices-explain.md`, `13-replica-sharding.md`, `14-pymongo-profesional.md`.
11. `08-aggregation-8-pipelines.md`: tabla pipeline→O1-O4→etapas.
12. `vault-data/00-empezar-aqui-datos.md` + `vault-tecnico/LEARNING_LOG.md`: enlaces a `docs/guion_defensa.md`, `matriz_indicadores.md`, `preguntas_analisis_profesional.md`, `metodologia.md` y nuevas notas.

## Misconceptions e inconsistencias detectadas (origen → estado)

- A. Correlación renta-alquiler 0,2094 vs 0,28: manda 0,2094 Eustat n=159; 0,28 era otra renta (auditoría vieja).
- B. Ratio renta joven media-simple vs ponderada: manda ponderada por anchura; media-simple legacy.
- C. Salarios 1381 vs 1402 vs 1564: observados OVJ CAE vs derivado ajustado ±15% (calibración a ojo, P-02 si se presenta como dato).
- D. Robustos 4 vs 6: 6 antes de unificar, 4 después (Bilbao 173, Donostia 113, Getxo 40, Vitoria 39).
- E. Generadores cruzados + HTML manuales (P-05): PNG auto sí, HTML manual no cuenta para RA4.
- F. "Imputación comarcal" vs IDW: siempre IDW_5_vecinos; nombre de script histórico.
- G. Cifras inventario/tests/desfase manifest: usar `find -type f` + fecha; manifests 353 vs 47.
- H. Población 15-29 vs 18-34: contrato exige 18_34 estimado + bandas reales.

## Huecos frente a rúbrica (qué te deja sin 10)

- BDA RA1 HDFS: solo bronce, rúbrica pide originales + procesados + recuperación → hoy 7 pts.
- BDA RA1 gate: piezas sueltas OK, sin encadenar subir→publicar→consumir→verificar codigo_ine → hoy 7 pts.
- SBD RA1 automatización: `validar_renta.py` fuera de `run_all` rompe "sin tocar Mongo a mano".
- SBD RA3 modelo: falta justificar embedding vs referencing por patrón de acceso (7 preguntas DOCX §5).
- SBD RA3 consultas: faltaba lista de 5 recitables (creada en nota 14, falta pegar salidas reales).
- SBD RA3 aggregation: faltaba mapa pipeline→pregunta→etapas (creado, falta pegar entradas/salidas por etapa).
- SBD RA3 índices: faltaba explain antes/después con números + ESR + coste (nota creada, falta pegar salida real).
- SBD RA3 consistencia: faltaba nota (creada).
- RA4 P-05: HTML manuales no son evidencia auto; evidencia válida = 4 CSV.
- Tema 8 §10/§12: faltaban notas (creadas); falta tabla Tema1-8→reto + checklist §17.

## Puntuación vault 0-10 (tras arreglos)

| Bloque | Nota |
|---|---|
| Vault-data O1-O4 | 9,0 |
| BDA RA1 | 7,0 |
| SBD RA1 46,7% | 8,0 |
| SBD RA3 13,3% | 7,5 |
| SBD RA4 40% | 8,0 |
| Tema 8 + defensa | 7,0 |
| **Global** | **7,8** |

## Plan para llegar al 10 (solo vault, por hacer)

P0 (te quita el 10 hoy):
1. HDFS: documentar subida de `procesado/` o justificación firmada de por qué solo bronce + prueba `read_file_sha256`.
2. Gate: dejar secuencia verificable en una pasada + `codigo_ine` común (o declarar pendiente con fecha).
3. Pegar salidas reales en notas 11/12/14 (explain COLLSCAN→IXSCAN, `matched_count`, 5 consultas con resultado).
4. Tabla Tema1-8→reto (DOCX §15 tabla 13) + checklist §17 en nota nueva o en `00-reto`.
5. Marcar `is_imputed` en tensión (`fillna(mediana)` oculta ausencia) y no perder `metodo_imputacion` en CSV final.

P1:
6. `validar_renta.py` en `run_all` o justificación.
7. Migración total 16-29→18-34 en tablas restantes.
8. Corregir docstring `validar_renta.py` (dice raw, escribe procesado).
9. Unificar tests/manifest en tabla canónica con comando + fecha.

## Preguntas quiz pendientes (teachme)

- P1. Si te dicen "tu r=0,28 no cuadra con metodologia.md", ¿qué respondes? → A) 0,2094 canónico Eustat n=159; 0,28 era otra renta vieja.
- P2. Prueba RA3 de índices, ¿qué enseñas? → B) `explain_before_after`: COLLSCAN 759 examinados → IXSCAN, ESR y coste.
