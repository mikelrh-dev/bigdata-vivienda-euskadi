# Proposal: fase-extraccion-mejora

## Intent
Incorporar fuentes de alta prioridad al raw de forma cuidadosa, empezando por VPO promociones Etxebide, sin romper inmutabilidad.

## Scope
### In Scope
- Nuevo extractor `extract/24_etxebide_promociones.py`.
- Raw `etxebide_promociones.csv/json` + manifest actualizado.
- Tests raw inmutables en verde.

### Out of Scope
- GTFS completo, OSRM, población joven, Udalmap extendido (siguientes iteraciones).

## Rollback Plan
Eliminar archivos nuevos y regenerar manifest previo.

## Success Criteria
- [x] Extractor ejecuta OK.
- [x] Manifest verify OK.
- [x] Tests raw inmutables OK.
