# Plantilla Maestra Reutilizable — Auditoría Técnica y Estadística

Copia este bloque base cada vez que termines una tarea o fase y quieras que el agente haga de abogado del diablo antes de hacer commit.

```markdown
Actúa como Principal Data Engineer y Auditor Técnico del proyecto `bigdata-vivienda-euskadi`.
MODO: SOLO LECTURA Y DIAGNÓSTICO (Prohibido modificar código de producción hasta que yo autorice el plan).

### 1. Lectura Obligatoria (Contract-First)
Lee `openspec/specs/contrato-reto/spec.md` y la especificación de la fase actual en `openspec/specs/`.

### 2. Foco de la Auditoría Actual
[PEGAR AQUÍ EL MÓDULO DE LA FASE CORRESPONDIENTE — VER MODULOS_FASE.MD]

### 3. Reglas de Ejecución Empírica
- No supongas que algo funciona porque el código "parece correcto": ejecuta comandos de verificación reales (scripts rápidos en Python, consultas de conteo, `pytest` o inspección de ficheros/contenedores) para obtener números exactos.
- Busca activamente fallos silenciosos: nulos encubiertos, pérdidas en joins (`$lookup`), duplicados, desajustes de tipos o requisitos de la rúbrica que se quedarían en 7 puntos en vez de 10.

### 4. Formato de Salida Requerido
Devuélveme exclusivamente este informe:
1. **Métricas Reales Observadas:** Datos cuantitativos extraídos de la ejecución (conteos, % de match, tiempos, tamaños, tests).
2. **Incumplimientos o Riesgos Detectados (P1 Crítico / P2 Alto / P3 Medio):** Qué falla o qué nos haría perder puntos en la rúbrica de 10 puntos.
3. **Plan de Corrección Quirúrgico:** Qué archivos tocar, esfuerzo estimado y cómo se verificará. Espera mi "OK" antes de editar.
```
