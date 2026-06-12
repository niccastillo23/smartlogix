# SmartLogix - Shipping Service

Microservicio de gestión de envíos. Implementa el patrón **Circuit Breaker** con Resilience4j para proteger las llamadas a APIs externas de carriers de envío.

## Tecnologías
- Spring Boot 3.2.5
- Spring Data JPA
- H2 Database (embebida)
- Resilience4j (Circuit Breaker)
- Swagger/OpenAPI
- JaCoCo (cobertura)

## Ejecutar

```bash
mvn spring-boot:run
```

- API: http://localhost:8083/api/shipments
- Swagger: http://localhost:8083/swagger-ui.html
- H2 Console: http://localhost:8083/h2-console (JDBC URL: `jdbc:h2:mem:shippingdb`)

## Tests

```bash
mvn clean verify                    # Tests + JaCoCo (falla si < 60%)
open target/site/jacoco/index.html  # Reporte cobertura
```

**19 tests** (CarrierService: 3, Service: 10, Controller: 6) | Cobertura >87%

### Tests del Circuit Breaker
- `ExternalCarrierServiceTest`: Llamada exitosa vs fallback (carrier FALLIDO)
- `ShippingServiceTest`: Envío normal vs con Circuit Breaker activado
- `ShippingControllerTest`: Endpoints REST (6 casos)

## Circuit Breaker

| Parámetro | Valor |
|-----------|-------|
| Sliding Window Size | 5 |
| Failure Rate Threshold | 50% |
| Wait Duration (Open) | 10s |
| Half-Open Calls | 3 |

**Fallback**: Cuando el carrier externo falla, se genera un tracking number con prefijo "FBK-" y ETA de 7 días.

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /api/shipments | Listar todos los envíos |
| GET | /api/shipments/{id} | Obtener envío por ID |
| GET | /api/shipments/order/{orderId} | Envío por orderId |
| GET | /api/shipments/status/{status} | Envíos por estado |
| POST | /api/shipments | Crear envío |
| PATCH | /api/shipments/{id}/status?status= | Actualizar estado |
