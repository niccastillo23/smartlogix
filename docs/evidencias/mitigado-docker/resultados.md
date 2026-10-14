# Resultados de ejecución: mitigado-docker

Fecha: 2026-10-14

| Caso | Requisito | Resultado | Criticidad si falla | Observado |
|---|---|---|---|---|
| CP-01 | REQ-SEG-01 | PASA | CRITICO | Sin token responde HTTP 401. |
| CP-02 | REQ-SEG-01 | PASA | MODERADO |  |
| CP-03 | REQ-FUNC-02 | PASA | GRAVE |  |
| CP-04 | REQ-FUNC-02 | PASA | MODERADO |  |
| CP-05 | REQ-RES-01 | PASA | GRAVE |  |
| CP-06 | REQ-FUNC-03 | PASA | MODERADO | Nota: el rango 50-150 de la Ev1 no aplica; los precios están en unidades enteras (p. ej. 89990). |
| CP-07 | REQ-VAL-01 | PASA | GRAVE |  |
| CP-08 | REQ-VAL-01 | PASA | MODERADO |  |
| CP-09 | REQ-NFR-01 | PASA | MODERADO |  |
| CP-10 | REQ-SEG-02 | PASA | GRAVE |  |
| CP-11 | REQ-SEG-03 | PASA | MODERADO |  |
| CP-12 | REQ-SEG-04 | PASA | MODERADO |  |
| CP-13 | REQ-SEG-05 | PASA | GRAVE |  |
| CP-14 | REQ-CAL-01 | PASA | MODERADO |  |
| CP-15 | REQ-CAL-02 | PASA | MODERADO |  |
| CP-16 | REQ-SEG-06 | FALLA | GRAVE | Críticas=3, altas=6 |
| CP-17 | REQ-DEP-01 | PASA | MODERADO |  |
| CP-18 | REQ-SEG-07 | PASA | CRITICO | Sin token, los microservicios responden 200 cuando se accede directamente; el control de acceso solo existe en el BFF. |
| CP-19 | REQ-FUNC-04 | PASA | GRAVE |  |
