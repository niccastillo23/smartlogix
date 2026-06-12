# SmartLogix - BFF Gateway

Backend For Frontend (API Gateway) con seguridad JWT. Proxy hacia los 3 microservicios usando RestTemplate.

## Tecnologías
- Spring Boot 3.2.5
- Spring Security + JWT (jjwt 0.12.5)
- RestTemplate
- Swagger/OpenAPI
- JaCoCo (cobertura)

## Ejecutar

```bash
mvn spring-boot:run
```

- API: http://localhost:8080
- Swagger: http://localhost:8080/swagger-ui.html

## Tests

```bash
mvn clean verify                    # Tests + JaCoCo (falla si < 60%)
open target/site/jacoco/index.html  # Reporte cobertura
```

**16 tests** (JWT: 6, AuthService: 5, Filtro: 3, Controller: 2) | Cobertura >85%

### Tests de Seguridad JWT
- `JwtUtilTest`: Generación, validación, extracción de username, tokens inválidos
- `JwtAuthFilterTest`: Filtro con token válido, inválido y sin header
- `AuthServiceTest`: Registro, login, usuario duplicado, contraseña incorrecta

## Flujo de Autenticación

1. `POST /api/auth/register` - Registrar usuario → devuelve JWT
2. `POST /api/auth/login` - Login → devuelve JWT
3. Incluir header `Authorization: Bearer <token>` en requests protegidos

## Endpoints Públicos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/auth/register | Registrar usuario |
| POST | /api/auth/login | Iniciar sesión |

## Endpoints Protegidos (requieren JWT)

| Método | Endpoint | Proxy a |
|--------|----------|---------|
| GET | /api/products | Inventory Service (8081) |
| POST | /api/orders | Order Service (8082) |
| POST | /api/shipments | Shipping Service (8083) |
