# SmartLogix - eCommerce de Perfumes

Arquitectura de microservicios para un eCommerce de perfumes, implementada con Spring Boot 3.2, React 18 y patrones de diseño empresariales.

## Arquitectura

| Componente | Tecnología | Puerto | Patrón |
|-----------|-----------|--------|--------|
| **Frontend** | Tailwind CSS + Framer Motion + Axios | 5173 | Context API |
| **BFF Gateway** | Spring Boot 3.2 + JWT | 8080 | API Gateway |
| **Inventory Service** | Spring Boot 3.2 + JPA + H2 | 8081 | Repository Pattern |
| **Order Service** | Spring Boot 3.2 + JPA + H2 | 8082 | Factory Method |
| **Shipping Service** | Spring Boot 3.2 + JPA + H2 + Resilience4j | 8083 | Circuit Breaker |

## Requisitos

- Java 21
- Maven 3.9+
- Node.js 18+
- npm 9+

## Inicio Rápido

### 1. Iniciar Microservicios (en terminales separadas)

```bash
# Inventory Service
cd inventory-service
mvn spring-boot:run

# Order Service
cd order-service
mvn spring-boot:run

# Shipping Service
cd shipping-service
mvn spring-boot:run

# BFF Gateway (debe iniciarse después de los microservicios)
cd bff-gateway
mvn spring-boot:run
```

### 2. Iniciar Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Acceder

- Frontend: http://localhost:5173
- BFF Swagger: http://localhost:8080/swagger-ui.html
- Inventory Swagger: http://localhost:8081/swagger-ui.html
- Order Swagger: http://localhost:8082/swagger-ui.html
- Shipping Swagger: http://localhost:8083/swagger-ui.html

## Ejecutar Tests

### Backend (JUnit 5 + Mockito + JaCoCo)

Cada microservicio tiene su batería de tests con verificación de cobertura mínima del 60%:

```bash
# Tests + cobertura (falla si < 60%)
cd inventory-service && mvn clean verify
cd order-service && mvn clean verify
cd shipping-service && mvn clean verify
cd bff-gateway && mvn clean verify

# Ver reporte HTML de cobertura
open inventory-service/target/site/jacoco/index.html
open order-service/target/site/jacoco/index.html
open shipping-service/target/site/jacoco/index.html
open bff-gateway/target/site/jacoco/index.html
```

### Frontend (Vitest + React Testing Library)

```bash
cd frontend
npm test                 # 50 tests unitarios
npm run test:coverage    # + reporte de cobertura
open coverage/index.html
```

### Resultados Actuales

| Componente | Tests | Pasados | Cobertura (líneas) |
|-----------|-------|---------|-------------------|
| **Inventory Service** | 31 | 31/31 | >87% |
| **Order Service** | 20 | 20/20 | >88% |
| **Shipping Service** | 19 | 19/19 | >87% |
| **BFF Gateway** | 16 | 16/16 | >85% |
| **Frontend** | 50 | 50/50 | >67% |
| **TOTAL** | **116** | **116/116** | **>75%** |

### Guía Detallada

Ver [`docs/TESTING.md`](docs/TESTING.md) para:
- Requisitos previos detallados
- Escenarios de prueba manual (flujo completo)
- Cómo agregar nuevos tests
- Solución de problemas comunes (Java 25, Lombok, ByteBuddy)

## Documentación

- `docs/diagrama-arquitectura.md` - Diagrama de arquitectura (Mermaid.js)
- `docs/descripcion-persistencia.md` - Informe de persistencia JPA
- `docs/informe-pruebas.md` - Informe de pruebas unitarias
- `docs/swagger-api.md` - Guía de uso de Swagger en cada servicio
- `docs/TESTING.md` - Guía completa de testing y troubleshooting
- `postman/smartlogix-collection.json` - Colección Postman

## Patrones de Diseño

1. **Repository Pattern** (Inventory): `ProductRepository` + `ProductService`
2. **Factory Method** (Orders): `OrderFactory` → `WebOrderFactory` / `MarketplaceOrderFactory`
3. **Circuit Breaker** (Shipping): Resilience4j + `ExternalCarrierService` fallback
