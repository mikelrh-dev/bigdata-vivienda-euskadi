# Delta for presentacion-de-resultados

## ADDED Requirements

### Requirement: DASHBOARD-ROBUSTOS-01 — Dashboard con 4 robustos (n>=30)

El sistema MUST presentar en `data/resultados/dashboard_completo.html` exactamente 4 municipios robustos con n>=30 anuncios: Bilbao 48020 n 173, Donostia 20069 n 113, Getxo 48044 n 40 y Vitoria 01059 n 39. El dashboard MUST NOT afirmar 6 robustos.

#### Scenario: La conclusión O2 nombra a los 4 robustos

- GIVEN el HTML regenerado
- WHEN se lee la fila O2 de conclusiones
- THEN nombra a Bilbao, Donostia, Getxo y Vitoria con sus n
- AND no aparece "6 robustos"

#### Scenario: Los PNGs se regeneran con el script

- GIVEN `transform/generar_dashboard_completo.py` corregido en la línea 176
- WHEN se ejecuta el script
- THEN los 8 PNGs del bloque A-G se generan en `data/resultados/`

## MODIFIED Requirements

Ninguno. CONCLUSION-01 y las demás conclusiones no cambian de comportamiento.

## REMOVED Requirements

Ninguno.

## RENAMED Requirements

Ninguno.
