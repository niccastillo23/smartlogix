# Resultados de ejecución: baseline-codigo-original

Fecha: 2026-10-14

| Caso | Requisito | Resultado | Criticidad si falla | Observado |
|---|---|---|---|---|
| CP-01 | REQ-SEG-01 | PASA | CRITICO | Sin token responde HTTP 403. |
| CP-02 | REQ-SEG-01 | FALLA | MODERADO | Login con contraseña incorrecta [POST http://localhost:8080/api/auth/login] -> HTTP 403; Registro de usuario ya existente [POST http://localhost:8080/api/auth/r |
| CP-03 | REQ-FUNC-02 | PASA | GRAVE |  |
| CP-04 | REQ-FUNC-02 | FALLA | MODERADO | Pedido con tipo INVALIDO [POST http://localhost:8080/api/orders] -> HTTP 403 |
| CP-05 | REQ-RES-01 | PASA | GRAVE |  |
| CP-06 | REQ-FUNC-03 | FALLA | MODERADO | Nota: el rango 50-150 de la Ev1 no aplica; los precios están en unidades enteras (p. ej. 89990). |
| CP-07 | REQ-VAL-01 | FALLA | GRAVE | Producto con nombre vacío [POST http://localhost:8080/api/products] -> HTTP 403; Producto con precio negativo [POST http://localhost:8080/api/products] -> HTTP  |
| CP-08 | REQ-VAL-01 | FALLA | MODERADO | Producto con nombre vacío vía BFF [POST http://localhost:8080/api/products] -> HTTP 403 |
| CP-09 | REQ-NFR-01 | PASA | MODERADO |  |
| CP-10 | REQ-SEG-02 | FALLA | GRAVE | No se almacena request.getPassword() en claro; Se utiliza un PasswordEncoder (hash) |
| CP-11 | REQ-SEG-03 | FALLA | MODERADO | Verificación de ausencia de detalle técnico en el cuerpo de error (HTTP 404) |
| CP-12 | REQ-SEG-04 | PASA | MODERADO |  |
| CP-13 | REQ-SEG-05 | FALLA | GRAVE | jwt.secret usa placeholder ${...} |
| CP-14 | REQ-CAL-01 | FALLA | MODERADO | inventory-service: reporte JaCoCo existe; order-service: reporte JaCoCo existe; shipping-service: reporte JaCoCo existe; bff-gateway: reporte JaCoCo existe |
| CP-15 | REQ-CAL-02 | FALLA | MODERADO | bff-gateway: hallazgos prioridad 1 = 1 ['SPRING_CSRF_PROTECTION_DISABLED'] |
| CP-16 | REQ-SEG-06 | FALLA | GRAVE | Críticas=3, altas=13 |
| CP-17 | REQ-DEP-01 | FALLA | MODERADO | inventory-service/Dockerfile presente; order-service/Dockerfile presente; shipping-service/Dockerfile presente; bff-gateway/Dockerfile presente; docker-compose. |
| CP-18 | REQ-SEG-07 | FALLA | CRITICO | Sin token, los microservicios responden 200 cuando se accede directamente; el control de acceso solo existe en el BFF. |
| CP-19 | REQ-FUNC-04 | FALLA | GRAVE | POST /api/products vía BFF -> HTTP 403; El producto recibe un id asignado |
