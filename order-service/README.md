# SmartLogix - Order Service

Microservicio de gestión de pedidos. Implementa el patrón **Factory Method** para crear órdenes de tipo WEB y MARKETPLACE con diferentes descuentos y métodos de envío.

## Tecnologías
- Spring Boot 3.2.5
- Spring Data JPA
- H2 Database (embebida)
- Swagger/OpenAPI
- JaCoCo (cobertura)

## Ejecutar

```bash
mvn spring-boot:run
```

- API: http://localhost:8082/api/orders
- Swagger: http://localhost:8082/swagger-ui.html
- H2 Console: http://localhost:8082/h2-console (JDBC URL: `jdbc:h2:mem:orderdb`)

## Tests

```bash
mvn clean verify                    # Tests + JaCoCo (falla si < 60%)
open target/site/jacoco/index.html  # Reporte cobertura
```

**20 tests** (Factory: 4, Service: 10, Controller: 6) | Cobertura >88%

### Tests del Factory Method
- `OrderFactoryTest`: Web (5% desc, STANDARD) vs Marketplace (10% desc, EXPRESS)
- `OrderServiceTest`: Resolución de fábrica por tipo, validación de descuentos
- `OrderControllerTest`: Endpoints REST (6 casos)

## Factory Method

| Factory | Tipo | Descuento | Envío |
|---------|------|-----------|-------|
| `WebOrderFactory` | WEB | 5% | STANDARD |
| `MarketplaceOrderFactory` | MARKETPLACE | 10% | EXPRESS |

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /api/orders | Listar todos los pedidos |
| GET | /api/orders/{id} | Obtener pedido por ID |
| GET | /api/orders/customer/{customerId} | Pedidos por cliente |
| GET | /api/orders/status/{status} | Pedidos por estado |
| POST | /api/orders | Crear pedido (WEB o MARKETPLACE) |
| PATCH | /api/orders/{id}/status?status= | Actualizar estado |
