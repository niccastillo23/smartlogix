# SmartLogix - Inventory Service

Microservicio de gestión de inventario de perfumes. Implementa el **Repository Pattern** con Spring Data JPA.

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

- API: http://localhost:8081/api/products
- Swagger: http://localhost:8081/swagger-ui.html
- H2 Console: http://localhost:8081/h2-console (JDBC URL: `jdbc:h2:mem:inventorydb`)

## Tests

```bash
mvn clean verify                    # Tests + JaCoCo (falla si < 60%)
open target/site/jacoco/index.html  # Reporte cobertura
```

**31 tests** (Repository: 5, Service: 15, Controller: 11) | Cobertura >87%

### Tests del Repository Pattern
- `ProductRepositoryTest`: Consultas JPA (findByBrand, findByPriceRange, findInStock, search)
- `ProductServiceTest`: Abstracción del repositorio, 15 casos (CRUD + búsquedas)
- `ProductControllerTest`: Endpoints REST (11 casos)

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /api/products | Listar todos los productos |
| GET | /api/products/{id} | Obtener producto por ID |
| GET | /api/products/brand/{brand} | Filtrar por marca |
| GET | /api/products/fragrance/{fragrance} | Filtrar por fragancia |
| GET | /api/products/price-range?min=&max= | Filtrar por rango de precio |
| GET | /api/products/in-stock | Productos con stock |
| GET | /api/products/search?name= | Buscar por nombre |
| POST | /api/products | Crear producto |
| PUT | /api/products/{id} | Actualizar producto |
| PATCH | /api/products/{id}/stock | Actualizar stock |
| DELETE | /api/products/{id} | Eliminar producto |

## Datos de Prueba

Se cargan 10 perfumes automáticamente desde `data.sql` al iniciar el servicio.
