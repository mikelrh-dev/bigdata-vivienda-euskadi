# Preguntas de defensa (25 hostiles)

Formato: **pregunta** → respuesta sólida → lo que **no** hay que decir.

1. **«¿Dónde están los datos procesados en HDFS?»** → «Originales en `/data/raw` con 353 objetos acreditados; procesados en HDFS están exentos por waiver y el resultado vive en `data/procesado` + Mongo.» No decir «están, pero no los veo».
2. **«Demuéstrame Kafka ahora.»** → «Hoy no hay red al centro; la evidencia es del 2026-11-09: 352/352, lag 0, `offset+1`.» No improvises un `kafka-console-consumer` que vas a fallar.
3. **«¿Cuántos tests tienes?»** → «300 colectados, 298 pasan, 2 skipped.» El deck dice 295: corrígelo antes o reconocerlo en voz alta.
4. **«¿Por qué el deck dice 295 y tú 298?»** → «El deck está una tanda por detrás; la suite creció al añadir el verificador de reproducibilidad.» Es la respuesta honesta y no cuesta nada.
5. **«¿Qué es el 87,3 %?»** → «La mediana del esfuerzo de los 287 anuncios individuales, no la mediana municipal, que es 78,6 %.» Nunca decir «el esfuerzo de Euskadi».
6. **«¿Y el 98,3 %?»** → «Porcentaje de esos 287 anuncios que supera el 30 % del salario joven; es nivel de anuncio, no de municipio.»
7. **«287 anuncios de 594: ¿dónde están los otros?»** → «268 son temporales y se descartan por no comparables; 326 son larga estancia y tras el filtro de validez quedan 287 en 50 municipios.» No digas «287 de 594»: es 287 de 297 con precio.
8. **«Tu desglose por tipo suma 277.»** → Reconocer: «10 anuncios no declaran habitaciones; la tabla por tipo se calcula sobre 277.» Tenerlo apuntado.
9. **«¿Por qué 50 municipios si tienes 64 con anuncio?»** → «64 tienen algún anuncio de los 594; 50 tienen precio válido en la capa 2026.»
10. **«¿El 71,2 % de jóvenes con el 19,8 % de municipios no es trampa?»** → «Es cobertura de población, no de territorio, y está declarada como tal; los 4 Tier A concentran el 70,4 % de los anuncios.»
11. **«¿Por qué el esfuerzo 18-24 es el doble del 18-34?»** → «Porque la renta 18-24 se estima con el escalar CAE 0,6311 sobre la renta municipal; es una estimación declarada en `parametros_estudio.yaml`, no un dato observado.»
12. **«Entonces tienes tres columnas con el mismo número.»** → Reconocer y explicar: `${esfuerzo_joven_pct}$, `_16_29` y `esfuerzo_alquiler_pct` coinciden porque comparten numerador y denominador; no son tres indicadores.
13. **«¿Cuántos indicadores distintos hay de verdad?»** → «Esfuerzo, tensión social, VPO, accesibilidad/OSRM, habitaciones, esfuerzo por sexo y sensibilidad IDW: siete, de cuatro fuentes.»
14. **«¿De dónde sale el 30 %?»** → Es una convención de affordability (coste ≤30 % de la renta). Si no tienes fuente citada, dilo: «convención, no umbral legal». (G-02)
15. **«¿Por qué IDW y no dejar el hueco?»** → «Se publica la capa oficial de 159 y la IDW de 93 aparte, con `is_imputed` y una sensibilidad que mueve la mediana de 26,61 a 25,37.»
16. **«¿El IDW no inventa municipios?»** → «No se presenta como municipal observado: `metodo_imputacion=idw` e `is_imputed=True` en las 93 filas.»
17. **«¿Cómo sé que el gold no está tecleado?»** → «Huella `983fa53f…` estable en dos pasadas y 8 CSV byte-idénticos; el deck se verifica con 120 comprobaciones.»
18. **«Tu verificador del deck no comprueba el número de tests.»** → Cierto (H-01). Es la mejor prueba de que la auditoría es honesta: reconocerlo y decir que ya está en la lista.
19. **«El Spearman 0,988, ¿sobre cuántos?»** → «Sobre 159 con alquiler oficial; el universo de 160 da 0,979 y 159/160 dentro de ±25 %.»
20. **«¿Por qué 0,977 en el deck y 0,976 en el README?»** → «Mismo 0,9765 con redondeo distinto; conviene unificarlo.»
21. **«Demuéstrame el E2E.»** → «El gate actual comprueba conectividad y umbrales, no datos; el E2E real es la cadena `run_pipeline --fase mongo` + `run_analisis_mongo` con huella estable.» No vendas el gate como E2E.
22. **«¿Por qué dos colecciones de habitaciones idénticas?»** → «Compatibilidad con el nombre anterior; son 201/201 con los mismos `_id`. Es deuda de unificación.»
23. **«¿Cómo justificas `find_one_and_update` en vez de transacción?»** → «La operación es atómica a nivel de documento y el modelo no tiene invariantes multidocumento; una transacción sería artificial, que es justo lo que el Tema 8 desaconseja.»
24. **«¿Qué campo sería shard key?»** → «`ubicacion.codigo_ine` con hashed para reparto uniforme, o ranged si las consultas son por territorio; hashed evita hotspots pero castiga consultas por rango.»
25. **«¿Qué no funciona hoy?»** → «HDFS y Kafka en vivo por red; el gate E2E no verifica datos; el deck está una tanda por detrás. Todo lo demás está reproducido hoy.»
