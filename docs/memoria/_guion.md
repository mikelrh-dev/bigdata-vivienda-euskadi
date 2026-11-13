# Guion de la memoria

> Documento de trabajo. No forma parte de la entrega: fija el alcance, el orden,
> las fuentes y el estado de cada capítulo.

## 1. Qué es esta memoria

Memoria técnica explicativa para la profesora y el tribunal. Debe responder, con
datos verificables, a cinco preguntas:

1. **Qué se construyó** y qué pregunta responde.
2. **Cómo está arquitecturado** el recorrido del dato, de la fuente al análisis.
3. **Cómo se hizo**: extracción, transformación, carga y análisis.
4. **Qué conclusiones** se sostienen y con qué evidencia.
5. **Qué dificultades** aparecieron y cómo se resolvieron o se declararon.

No es el guion de la defensa, no es el deck y no es el cuaderno NB04. El deck
defiende; la memoria explica. NB04 es la cantera; aquí solo entra lo que el
documento necesita.

## 2. Reglas de la carpeta

| Regla | Motivo |
|---|---|
| `_cifras.json` es la única autoridad de cifras | Evita la deriva 16/17 colecciones, 352/353 HDFS, 182/183 silver |
| Los capítulos usan `{{clave}}`, no números | Una cifra se corrige en un sitio y se propaga |
| `memoria.md`, `memoria.docx` y `memoria.pdf` se generan | Si se editan a mano, el Markdown deja de ser la fuente |
| Cada capítulo declara sus criterios en el comentario `cap` | El anexo de trazabilidad se mantiene solo |
| Las figuras viven en `figuras/` con nombre estable | El DOCX y el PDF comparten los mismos archivos |

## 3. Estructura y presupuesto de páginas

| Cap. | Título | Págs. | Criterios | Estado |
|---|---|---:|---|---|
| 1 | Contexto y pregunta | 2 | C17, C18 | borrador |
| 2 | Arquitectura de datos | 4 | C1–C4 | borrador |
| 3 | Cómo se construyó | 3,5 | C5–C8 | borrador |
| 4 | Modelo MongoDB | 3,5 | C9, C10, C14 | borrador |
| 5 | Análisis e indicadores | 2,5 | C11–C13, C16 | borrador |
| 6 | Resultados y conclusiones | 5 | C17–C19 | borrador |
| 7 | Dificultades y decisiones | 3 | Todos | borrador |
| 8 | Límites y verificación | 2 | C8, C16 | borrador |
| — | Anexos | 3 | Trazabilidad | borrador |

Total previsto: 22–25 páginas más portada.

## 4. Mapa de la rúbrica (19 criterios)

### BDA · RA1 · Gestión de soluciones y almacenamiento

| ID | Criterio | Dónde se demuestra |
|---|---|---|
| C1 | Extracción mediante Python (API y scraping) | 2.1, 3.1 |
| C2 | Almacenamiento HDFS: originales, recuperación | 2.3, 3.3 |
| C3 | Kafka: tópico, productor y consumidor | 2.3, 3.2 |
| C4 | Integración completa hasta MongoDB | 2.4, 3.4 |

### SBD · RA1 · Adquisición, integración y tratamiento (46,7 %)

| ID | Criterio | Dónde se demuestra |
|---|---|---|
| C5 | Integración de 2+ fuentes por un campo común | 3.2, 4.2 |
| C6 | 2+ colecciones y relación embedding/referencing | 4.1, 4.2 |
| C7 | Limpieza: nulos, duplicados, tipos | 3.3, 7.2 |
| C8 | Automatización carga + limpieza + transformación | 3.6, 8.3 |

### SBD · RA3 · Gestión y almacenamiento (13,3 %)

| ID | Criterio | Dónde se demuestra |
|---|---|---|
| C9 | Modelado con decisión embedding/referencing explicada | 4.1 |
| C10 | CRUD con PyMongo y comprobación del resultado | 4.5 |
| C11 | 5 consultas útiles, anidados y 2+ condiciones | 5.3 |
| C12 | 3 pipelines, 5 etapas, `$group` + `$lookup`/`$unwind` | 5.2 |
| C13 | Índice + `explain()` antes/después, COLLSCAN/IXSCAN | 5.4 |
| C14 | Operación atómica y justificación de no transacción | 4.5 |

### SBD · RA4 · Procesamiento y resultados (40 %)

| ID | Criterio | Dónde se demuestra |
|---|---|---|
| C15 | Datos heterogéneos adaptados con Python/PyMongo | 3.3, 4.3 |
| C16 | Script que ejecuta todos los análisis | 5.2, 8.3 |
| C17 | 5 indicadores con 2+ fuentes | 5.1, 6.1–6.4 |
| C18 | 3+ municipios comparados, conclusión ligada a indicador | 6.6 |
| C19 | 3+ conjuntos preparados para visualización | 6.1–6.5 |

## 5. Plan de figuras

| Figura | Archivo | Cap. | Pie previsto |
|---|---|---|---|
| Mapa de esfuerzo 2024 | `figuras/fig-mapa-2024.png` | 6 | Esfuerzo por municipio; el gris es ausencia de dato, no esfuerzo cero |
| Ranking 18–34 | `figuras/fig-ranking-2024.png` | 6 | Municipios ordenados por esfuerzo con alquiler oficial |
| Tier de confianza | `figuras/fig-tier.png` | 6 | A/B/C/D según cobertura y tamaño de muestra |
| Oficial vs anuncios | `figuras/fig-oficial-vs-anuncios.png` | 6 | Discrepancia entre alquiler oficial y oferta observada |
| Modalidades | `figuras/fig-modalidades.png` | 6 | Larga estancia frente a temporal |
| Mapa 2026 | `figuras/fig-mapa-2026.png` | 6 | Oferta de mercado 2026, capa separada de 2024 |
| Histograma 2026 | `figuras/fig-hist-2026.png` | 6 | Distribución del esfuerzo con anuncios |
| VPO por estado | `figuras/fig-vpo.png` | 6 | Promociones protegidas: flujo, no stock |
| Arquitectura de dos ramas | por generar | 2 | Fuentes → raw → silver → Mongo → gold, con HDFS/Kafka |
| Modelo de colecciones | por generar | 4 | `_id` = código INE; embedding y referencing |

Las dos últimas se dibujan en HTML/CSS y se rasterizan con Chrome headless. No
hay `mmdc` ni `dot` instalados; no se añade una dependencia solo para esto.

## 6. Reglas de redacción

- Español técnico, voz activa, frases cortas. Nada de “se procede a”.
- Una idea por párrafo; la primera frase dice qué demuestra el párrafo.
- Cifras siempre con token. Si una cifra no está en `_cifras.json`, no entra.
- Separador de miles español (`1.420`) y decimal con coma (`26,61`).
- Cada figura lleva pie con qué enseña, fuente exacta y fecha.
- Los límites se declaran antes de que los pregunte el tribunal.
- No se afirma nada que no esté verificado hoy; lo que depende de la red se
  fecha.
- Nada de `TODO`, `TBD` ni secciones vacías en la entrega.

## 7. Comandos

```bash
python docs/memoria/build.py --refresh   # recalcula cifras desde Mongo/CSV
python docs/memoria/build.py --check     # valida tokens, figuras y metadatos
python docs/memoria/build.py --build     # genera memoria.md, DOCX y HTML
python docs/memoria/build.py --pdf       # genera el PDF con Chrome
python docs/memoria/build.py --all       # las tres cosas
```

## 8. Decisiones pendientes

| Decisión | Valor por defecto | Quién |
|---|---|---|
| Nombres de autores y curso | “Equipo bigdata-vivienda-euskadi” | equipo |
| Formato de entrega | DOCX + PDF | profesora |
| ¿Capa 2026 en capítulo propio? | Sí, dentro del cap. 6 | equipo |
| ¿Fragmentos de código? | 6–8 cortos en anexo | equipo |
| ¿`informe_final.md` se marca como histórico? | Sí, al cerrar la memoria | equipo |
