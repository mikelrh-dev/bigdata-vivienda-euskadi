# Framework de Auditoría de DATO PURO — bigdata-vivienda-euskadi
# Objetivo: Determinar si podemos responder con rigor "¿Dónde pueden vivir los jóvenes en Euskadi?"

Copia este framework tal cual a tu agente. Es complementario a `01_plantilla_maestra.md` (técnico) y `02_modulos_fase.md` (infra). Este es SOLO DATO.

```markdown
Actúa como Principal Data Scientist y Auditor Estadístico del proyecto `bigdata-vivienda-euskadi`.
MODO: SOLO LECTURA Y DIAGNÓSTICO PURO (Prohibido modificar `data/raw/`. Solo contar, medir y validar).

### 1. Lectura Obligatoria
Lee `data/raw/dim_municipios.csv` (252 municipios canónicos, 5 dígitos codigo_ine) como tabla de verdad. Todo porcentaje es sobre 252.

### 2. Principio de Suficiencia
No audites filas, audita CAPACIDAD DE RESPUESTA. Para cada fuente, responde: ¿con esto puedo calcular tasa de esfuerzo por municipio con error <20%?

### 3. Fases de Auditoría de Dato Puro (Ejecutar en orden)

#### FASE 0 - Inventario Real (no `ls -lh`)
Para cada CSV/JSON en `data/raw/`:
- Registros brutos vs registros VÁLIDOS (ej: precio>0, superficie_m2 10-600, codigo_ine 5 dígitos)
- Municipios únicos con dato válido
- % cobertura sobre 252

Comando: `df['municipio'].nunique()` y `df.groupby('municipio').size().describe()`

#### FASE 1 - Entity Resolution (El cuello de botella #1)
1.  **codigo_ine 100%:** ¿Qué % de `alquiler_municipal.csv`, `anuncios_fotocasa.csv`, `anuncios_pisos.csv`, `anuncios_realtyapi.csv` tienen codigo_ine que cruza con `dim_municipios.csv`? Objetivo: 100%. Si es por string normalizado, marca P1 CRÍTICO.
2.  **Variantes:** Lista las 4 variantes de Fotocasa (`Arrankudiaga / Zollo` vs `Arrankudiaga-Zollo`) y `Donostia-San Sebastián` de RealtyAPI. ¿Están mapeadas a canónico?
3.  **Eustat agregados:** ¿Filtras las 24 filas no-municipio (CA, provincias, comarcas) de `eustat_renta_municipal.csv`? Si no, tu n=252 es falso.

#### FASE 2 - Cobertura Muestral (El cuello de botella #2)
Esta es la que decide si es serio.

Para `anuncios_fotocasa.csv`, `anuncios_pisos.csv`, `anuncios_realtyapi.csv`:
1.  **Distribución por municipio:** Calcula `counts = df.groupby('municipio').size()`
    - n >=30: ranking fiable (media estable)
    - n 5-29: indicativo (usar mediana, advertir)
    - n <5: no usable para municipio, solo para comarca/territorio
    - Reporta: ¿Cuántos municipios en cada tramo? En auditoría previa eran solo 3 con >=30.
2.  **Temporal vs Larga estancia (Fotocasa):** Separa por flag temporal. Calcula media €/m² temporal vs larga. Si diferencia >15% (en tu caso 16.12€ vs 18.91€), obliga a separar. No mezclar nunca.
3.  **Alquiler oficial:** `alquiler_municipal.csv` tiene 253 filas pero ¿cuántos municipios únicos? ¿Cuántos distritos por municipio? ¿Tienes `n muestral` por distrito? Si no hay n, marca P1: no sabes si media viene de 2 o 200 contratos.

#### FASE 3 - Calidad Estadística y Sesgos
1.  **Outliers €/m²:** Para cada fuente de anuncios, calcula Q1, Q3, IQR. Lista outliers > Q3+1.5*IQR. En auditoría previa: 9 en pisos (30-43€/m²) y 13 en fotocasa (hasta 83€/m², muchos de 15m² mal parseados). ¿Son pisos reales o error de superficie?
2.  **Superficie válida:** ¿Qué % de anuncios tienen `superficie_m2` entre 15 y 300 y `habitaciones` no nulo? Pisos.com tenía 0% según `diagnostico.py` -> P1 CRÍTICO.
3.  **Renta vs Alquiler:** Calcula correlación Pearson renta_municipal vs alquiler_municipal €/m². En auditoría previa r=+0.17 (débil). Si r<0.3, documenta que el precio no lo explica la renta local.
4.  **Emancipación:** `emancipacion_juventud.csv` usa `;` como separador y tiene `;` dentro de campos. ¿Parsea con `delimiter=';' quotechar='"'`? Si no, 14 indicadores salen corruptos.

#### FASE 4 - Validez de Dominio (Lo que hunde una defensa)
1.  **Udalmap empleo:** Verifica `tasa_actividad 0-100`, `tasa_ocupacion 0-100`, `tasa_paro 0-100`. En tu caso media paro -10.10% y -32% en Baliarrain. Marca P1 CRÍTICO si hay negativos: fórmula mal derivada.
2.  **Distancias:** `distancias_capitales.csv` 259 registros con 2 duplicados -> deduplicar. `distancias_municipios.json` 2.4MB = 5.000 pares de ~180.000 (2.7%). ¿Puedes responder "municipio barato a <30km"? No con 5k.
3.  **Salarios:** `ine_salarios_edad.csv` es nacional (1.372€ 16-24 años). No hay salario municipal gratuito. Documenta que usarás renta como proxy y no salario.
4.  **Fechas:** ¿Eustat 2024 vs INE Atlas 2022? Si mezclas años, añade columna `año_fuente`.

#### FASE 5 - Veredicto de Suficiencia para la Pregunta de Investigación
Con todos los números anteriores, responde SÍ/NO a:

1. ¿Puedo hacer ranking de 252 municipios por coste de acceso con error <20%? 
   - Criterio: Necesitas n>=30 o dato oficial con n conocido. Si solo 3 cumplen, respuesta = NO, solo ranking comarcal + capitales.
2. ¿Puedo calcular tasa de esfuerzo = alquiler / renta para 252 municipios?
   - Criterio: Necesitas renta 252/252. Eustat 201/252 -> necesitas INE Atlas para 51 faltantes. Sin eso, NO.
3. ¿Puedo concluir "dónde hay trabajo y vivienda barata"?
   - Criterio: Necesitas paro válido 0-100% y distancias completas. Con paro negativo y 5k distancias, NO hasta corregir.

### 4. Reglas de Ejecución Empírica
- No supongas: ejecuta `pandas`, calcula `nunique()`, `groupby().size()`, `corr()`, IQR.
- Busca fallos silenciosos: `superficie_m2 = 0` convertido a `None`, `precio/m2` infinito por superficie 1m², joins que pierden 93 municipios sin aviso.

### 5. Formato de Salida Requerido (Exclusivamente esto)

1.  **Métricas Reales Observadas (Tabla):**
    | Fuente | Registros válidos | Municipios únicos | % sobre 252 | n>=30 | n 5-29 | n<5 | codigo_ine % | Outliers |
    
2.  **Gaps y Sesgos (P1 Crítico / P2 Alto / P3 Medio):**
    - Lista de 93 municipios sin alquiler oficial, 51 sin renta, 195 sin fotocasa, etc.
    - Sesgo temporal, paro negativo, superficie faltante.

3.  **Veredicto de Suficiencia (1 párrafo serio):**
    - Ej: "Datos suficientes para análisis comarcal y capitales (n>=30 en 3 municipios, oficial 159/252). Insuficientes para ranking municipal fino de 252. Recomendación: agregar a comarca o completar con INE Atlas + scraping hasta n>=30."

4.  **Plan de Corrección Quirúrgico:**
    - Qué archivos tocar, si agregar INE Atlas, cómo corregir paro, cómo separar temporal. Espera mi OK antes de editar.
```

## Cómo usar los 3 frameworks juntos (orden serio)

1.  **Primero este (03 - DATO PURO):** ¿Podemos responder la pregunta? Si dice NO, no sigas con infra.
2.  **Luego 01+02 Módulo A:** ¿Extracción y entity resolution cumplen contrato?
3.  **Luego 01+02 Módulo B y C:** ¿HDFS/Kafka/Mongo y Aggregation son 10pts?

Si tu agente pasa 03, el proyecto es serio. Si solo pasa 01+02, es técnicamente correcto pero científicamente débil.
```

He creado el archivo en `/mnt/data/03_framework_auditoria_dato_puro.md`

¿Quieres que te genere también el `04_modulo_0_suficiencia_listo_para_pegar.md` que combine tu `stats_audit.md` con este framework para que se lo pases directo a tu agente en un solo prompt?
