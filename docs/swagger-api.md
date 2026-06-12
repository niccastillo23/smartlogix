# Documentación Swagger/OpenAPI - SmartLogix

## 1. ¿Qué es Swagger?

Swagger (OpenAPI) es una herramienta que documenta automáticamente todos los endpoints REST de cada microservicio, permitiendo probarlos directamente desde el navegador sin necesidad de Postman ni curl.

Cada componente del proyecto expone su propia interfaz Swagger en `/swagger-ui.html` y su especificación OpenAPI en `/v3/api-docs`.

---

## 2. URLs de Acceso

| Servicio | Puerto | Swagger UI | OpenAPI JSON |
|----------|--------|-----------|--------------|
| **BFF Gateway** | 8080 | http://localhost:8080/swagger-ui.html | http://localhost:8080/v3/api-docs |
| **Inventory Service** | 8081 | http://localhost:8081/swagger-ui.html | http://localhost:8081/v3/api-docs |
| **Order Service** | 8082 | http://localhost:8082/swagger-ui.html | http://localhost:8082/v3/api-docs |
| **Shipping Service** | 8083 | http://localhost:8083/swagger-ui.html | http://localhost:8083/v3/api-docs |

---

## 3. BFF Gateway (Puerto 8080)

El Swagger del BFF incluye seguridad JWT. Para probar endpoints protegidos:

### 3.1 Autenticarse
1. Abrir http://localhost:8080/swagger-ui.html
2. Ir al endpoint `POST /api/auth/register`
3. Enviar:
   ```json
   { "username": "admin", "password": "admin123" }
   ```
4. Copiar el `token` de la respuesta

### 3.2 Configurar Token en Swagger
1. Hacer clic en el botón **"Authorize"** (candado 🔓) arriba a la derecha
2. Pegar: `Bearer <token_copiado>`
3. Clic en **"Authorize"** → **"Close"**

### 3.3 Probar Endpoints Protegidos
Ahora puedes probar todos los endpoints.

### 3.4 Endpoints Disponibles

#### Auth (públicos)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register` | Registrar nuevo usuario |
| POST | `/api/auth/login` | Iniciar sesión |

#### Products (requieren JWT)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/products` | Listar todos los productos |
| GET | `/api/products/{id}` | Obtener producto por ID |
| POST | `/api/products` | Crear nuevo producto |
| PUT | `/api/products/{id}` | Actualizar producto |
| PATCH | `/api/products/{id}/stock` | Actualizar stock |

#### Orders (requieren JWT)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/orders` | Listar todos los pedidos |
| GET | `/api/orders/{id}` | Obtener pedido por ID |
| POST | `/api/orders` | Crear pedido (WEB o MARKETPLACE) |
| PATCH | `/api/orders/{id}/status` | Actualizar estado |

#### Shipments (requieren JWT)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/shipments` | Listar todos los envíos |
| GET | `/api/shipments/{id}` | Obtener envío por ID |
| GET | `/api/shipments/order/{orderId}` | Envío por ID de orden |
| POST | `/api/shipments` | Crear nuevo envío |
| PATCH | `/api/shipments/{id}/status` | Actualizar estado |

---

## 4. Inventory Service (Puerto 8081)

Swagger directo sin autenticación: http://localhost:8081/swagger-ui.html

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/products` | Listar todos los productos |
| GET | `/api/products/{id}` | Obtener producto por ID |
| GET | `/api/products/brand/{brand}` | Filtrar por marca |
| GET | `/api/products/fragrance/{fragrance}` | Filtrar por fragancia |
| GET | `/api/products/price-range` | Filtrar por rango de precio |
| GET | `/api/products/in-stock` | Productos con stock disponible |
| GET | `/api/products/search` | Buscar por nombre |
| POST | `/api/products` | Crear producto |
| PUT | `/api/products/{id}` | Actualizar producto |
| PATCH | `/api/products/{id}/stock` | Actualizar stock |
| DELETE | `/api/products/{id}` | Eliminar producto |

### Ejemplo: Crear Producto
```json
{
  "name": "Nuevo Perfume",
  "brand": "Marca Test",
  "description": "Descripción del perfume",
  "price": 59990,
  "stockQuantity": 20,
  "fragrance": "Floral"
}
```

---

## 5. Order Service (Puerto 8082)

Swagger directo sin autenticación: http://localhost:8082/swagger-ui.html

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/orders` | Listar todos los pedidos |
| GET | `/api/orders/{id}` | Obtener pedido por ID |
| GET | `/api/orders/customer/{customerId}` | Pedidos por cliente |
| GET | `/api/orders/status/{status}` | Pedidos por estado |
| POST | `/api/orders` | Crear pedido |
| PATCH | `/api/orders/{id}/status` | Actualizar estado |

### Ejemplo: Crear Pedido WEB (5% descuento)
```json
{
  "customerId": 1,
  "customerName": "Juan Pérez",
  "email": "juan@email.com",
  "orderType": "WEB",
  "items": [
    {
      "productId": 1,
      "productName": "Sauvage Eau de Parfum",
      "quantity": 2,
      "unitPrice": 89990
    }
  ]
}
```

### Ejemplo: Crear Pedido MARKETPLACE (10% descuento)
```json
{
  "customerId": 2,
  "customerName": "María López",
  "email": "maria@email.com",
  "orderType": "MARKETPLACE",
  "items": [
    {
      "productId": 2,
      "productName": "Bleu de Chanel",
      "quantity": 1,
      "unitPrice": 105990
    }
  ]
}
```

---

## 6. Shipping Service (Puerto 8083)

Swagger directo sin autenticación: http://localhost:8083/swagger-ui.html

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/shipments` | Listar todos los envíos |
| GET | `/api/shipments/{id}` | Obtener envío por ID |
| GET | `/api/shipments/order/{orderId}` | Envío por ID de orden |
| GET | `/api/shipments/status/{status}` | Envíos por estado |
| POST | `/api/shipments` | Crear envío |
| PATCH | `/api/shipments/{id}/status` | Actualizar estado |

### Ejemplo: Crear Envío (carrier normal)
```json
{
  "orderId": 1,
  "carrier": "DHL",
  "address": "Av. Principal 1234",
  "city": "Santiago",
  "country": "Chile"
}
```

### Ejemplo: Probar Circuit Breaker (carrier falla)
```json
{
  "orderId": 999,
  "carrier": "FAIL_CARRIER",
  "address": "Test",
  "city": "Test",
  "country": "Test"
}
```
La respuesta incluirá `"circuitBreakerFallback": true` y un tracking con prefijo "FBK-".

---

## 7. Configuración Técnica

### 7.1 Dependencia (pom.xml)
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.5.0</version>
</dependency>
```

### 7.2 Configuración (cada servicio)
```yaml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
```

### 7.3 Personalización (Java)
```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("SmartLogix Inventory Service API")
                        .description("API REST para gestión de inventario - Repository Pattern")
                        .version("1.0.0"));
    }
}
```

### 7.4 Seguridad JWT en Swagger (BFF)
```java
@Bean
public OpenAPI bffOpenAPI() {
    return new OpenAPI()
            .info(new Info().title("SmartLogix BFF Gateway API"))
            .addSecurityItem(new SecurityRequirement().addList("Bearer Authentication"))
            .components(new Components()
                    .addSecuritySchemes("Bearer Authentication",
                            new SecurityScheme()
                                    .type(SecurityScheme.Type.HTTP)
                                    .scheme("bearer")
                                    .bearerFormat("JWT")));
}
```

---

## 8. Postman vs Swagger

| Característica | Swagger UI | Postman |
|---------------|-----------|---------|
| **Acceso** | Navegador (sin instalar) | Requiere instalación |
| **Documentación** | Automática desde código | Manual |
| **Colección** | No aplica | `postman/smartlogix-collection.json` |
| **Auth JWT** | Botón "Authorize" | Variable `{{token}}` |
| **Pruebas rápidas** | Excelente | Buena |
| **Testing automatizado** | Limitado | Colections + Newman |

**Recomendación**: Usa Swagger para pruebas rápidas y exploración. Usa Postman para pruebas repetibles y demo.
