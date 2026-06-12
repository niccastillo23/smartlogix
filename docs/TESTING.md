# Guía de Testing - SmartLogix

## 1. Requisitos Previos

| Herramienta | Versión Mínima | Verificar |
|------------|---------------|-----------|
| Java | 21 | `java -version` |
| Maven | 3.9+ | `mvn --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

### Nota sobre Java 25

Si usas **Java 25** (como en este proyecto), se requieren configuraciones especiales:

- **Lombok 1.18.46+**: Necesario para compatibilidad con Java 25
- **ByteBuddy experimental**: `-Dnet.bytebuddy.experimental=true` en el plugin surefire
- **JaCoCo 0.8.15+**: Necesario para soportar class file version 69

Todas estas configuraciones ya están incluidas en los `pom.xml` y los tests deberían funcionar directamente.

---

## 2. Tests del Backend

### 2.1 Ejecutar Tests por Componente

```bash
# Cada comando se ejecuta desde la raíz del proyecto smartlogix/

# Inventory Service
cd inventory-service
mvn clean verify     # Tests + JaCoCo (falla si < 60%)

# Order Service
cd ../order-service
mvn clean verify

# Shipping Service
cd ../shipping-service
mvn clean verify

# BFF Gateway
cd ../bff-gateway
mvn clean verify
```

### 2.2 Ver Reportes de Cobertura (JaCoCo)

```bash
# Abrir en navegador
open inventory-service/target/site/jacoco/index.html
open order-service/target/site/jacoco/index.html
open shipping-service/target/site/jacoco/index.html
open bff-gateway/target/site/jacoco/index.html
```

### 2.3 Ejecutar Tests Individuales

```bash
# Test específico
cd inventory-service
mvn test -Dtest=ProductServiceTest

# Múltiples tests
mvn test -Dtest="ProductServiceTest,ProductControllerTest"

# Método específico
mvn test -Dtest=ProductServiceTest#createProduct_shouldSaveAndReturnDTO
```

### 2.4 Tests por Patrón de Diseño

| Patrón | Componente | Test Clave | Lo que valida |
|--------|-----------|-----------|---------------|
| **Repository** | Inventory Service | `ProductRepositoryTest` | Consultas JPA personalizadas (findByBrand, findByPriceRange, findInStock) |
| **Repository** | Inventory Service | `ProductServiceTest` | Abstracción del repositorio, 15 casos |
| **Factory Method** | Order Service | `OrderFactoryTest` | WebOrderFactory (5% desc) vs MarketplaceOrderFactory (10% desc) |
| **Factory Method** | Order Service | `OrderServiceTest` | Resolución de fábrica por orderType |
| **Circuit Breaker** | Shipping Service | `ShippingServiceTest` | Llamada normal vs fallback del carrier |
| **Circuit Breaker** | Shipping Service | `ExternalCarrierServiceTest` | CircuitBreaker + método de fallback |
| **JWT Security** | BFF Gateway | `JwtUtilTest` | Generación, validación y extracción de tokens |
| **JWT Security** | BFF Gateway | `JwtAuthFilterTest` | Filtro con token válido, inválido y sin header |

### 2.5 Salida Esperada

```
[INFO] Tests run: 31, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

---

## 3. Tests del Frontend

### 3.1 Ejecutar Tests

```bash
cd frontend

# Una vez (modo CI)
npm test

# En modo watch (se queda corriendo)
npm run test:watch

# Con cobertura
npm run test:coverage
```

### 3.2 Ver Reporte de Cobertura

```bash
open coverage/index.html
```

### 3.3 Tests Disponibles

| Archivo | Tests | Descripción |
|---------|-------|-------------|
| `authService.test.js` | 4 | Login, register, error handling |
| `productService.test.js` | 5 | getAllProducts, getProductById |
| `orderService.test.js` | 4 | createOrder, getAllOrders |
| `shippingService.test.js` | 4 | createShipment, getShipmentByOrderId |
| `Login.test.jsx` | 7 | Render, input cambio, submit, toggle register |
| `ProductCard.test.jsx` | 9 | Render info, botón add to cart, stock=0 |
| `Cart.test.jsx` | 8 | Carrito vacío, items, total, place order |
| `ProductCatalog.test.jsx` | 6 | Fetch products, grid render, navegación |
| `OrderStatus.test.jsx` | 5 | Lista de pedidos, estado vacío |
| `OrderForm.test.jsx` | 7 | Formulario, validación, submit |
| `ProtectedRoute.test.jsx` | 2 | Redirect cuando no autenticado |

### 3.4 Agregar Nuevos Tests

Los tests están en `frontend/src/__tests__/`. Para agregar uno nuevo:

```javascript
// __tests__/miComponente.test.jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import MiComponente from "../components/MiComponente";

describe("MiComponente", () => {
  it("debería renderizar correctamente", () => {
    render(<MiComponente />);
    expect(screen.getByText("Título")).toBeInTheDocument();
  });
});
```

---

## 4. Escenarios de Prueba Manual

### 4.1 Flujo de Compra Completo

```bash
# 1. Iniciar todos los servicios
cd inventory-service && mvn spring-boot:run &
cd order-service && mvn spring-boot:run &
cd shipping-service && mvn spring-boot:run &
cd bff-gateway && mvn spring-boot:run &

# 2. Iniciar frontend
cd frontend && npm run dev
```

#### Paso a paso en el navegador:

| # | Acción | Resultado Esperado |
|---|--------|-------------------|
| 1 | Abrir http://localhost:5173 | Redirige a /login |
| 2 | Hacer clic en "Registrarse" | Cambia a formulario de registro |
| 3 | Ingresar usuario y contraseña, enviar | Mensaje "Registro exitoso" |
| 4 | Ingresar credenciales, enviar | Redirige al catálogo |
| 5 | Ver el grid de 10 perfumes | Imágenes, precios CLP, stock |
| 6 | Hacer clic en "Agregar al Carrito" | Badge del carrito se actualiza |
| 7 | Ir a "Carrito" en el menú | Ver items, total, botón "Realizar Pedido" |
| 8 | Ajustar cantidad con +/- | Total se actualiza |
| 9 | Hacer clic "Realizar Pedido" | Modal "Detalles de Envío" |
| 10 | Llenar formulario (nombre, email, dirección) | Seleccionar tipo WEB o MARKETPLACE |
| 11 | Confirmar pedido | Mensaje "¡Pedido realizado con éxito!" |
| 12 | Ir a "Pedidos" | Ver la orden creada con estado PENDING |

### 4.2 Probar Circuit Breaker

```bash
# Crear un envío con carrier que falla
curl -X POST http://localhost:8083/api/shipments \
  -H "Content-Type: application/json" \
  -d '{"orderId":999,"carrier":"FAIL_CARRIER","address":"Test","city":"Test","country":"Test"}'

# Respuesta: debe incluir "circuitBreakerFallback": true
```

### 4.3 Probar Factory Method

```bash
# Orden WEB (5% descuento)
curl -X POST http://localhost:8082/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customerId":1,"customerName":"Test","email":"t@t.com","orderType":"WEB","items":[{"productId":1,"productName":"Sauvage","quantity":2,"unitPrice":120}]}'

# Orden MARKETPLACE (10% descuento)
curl -X POST http://localhost:8082/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customerId":1,"customerName":"Test","email":"t@t.com","orderType":"MARKETPLACE","items":[{"productId":1,"productName":"Sauvage","quantity":2,"unitPrice":120}]}'
```

### 4.4 Probar JWT

```bash
# Registrar
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Login (guardar token)
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Usar token para acceder a productos
curl http://localhost:8080/api/products \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 5. Solución de Problemas Comunes

### 5.1 Error: "Unsupported class file major version 69"

```
Caused by: java.lang.IllegalArgumentException: Unsupported class file major version 69
```

**Causa**: JaCoCo versión antigua con Java 25.

**Solución**: Usar JaCoCo 0.8.15+ (ya configurado en los pom.xml).

### 5.2 Error: "Java 25 is not supported by Byte Buddy"

```
Caused by: java.lang.IllegalArgumentException: Java 25 (69) is not supported
by the current version of Byte Buddy
```

**Solución**: Agregar en el pom.xml (ya incluido):
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <argLine>-Dnet.bytebuddy.experimental=true</argLine>
    </configuration>
</plugin>
```

### 5.3 Error: Lombok no procesa anotaciones

```
cannot find symbol: method builder()
cannot find symbol: method getName()
```

**Causa**: Lombok no se está ejecutando en compilación.

**Solución**: Verificar que el pom.xml tenga Lombok en annotationProcessorPaths (ya incluido):
```xml
<annotationProcessorPaths>
    <path>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>1.18.46</version>
    </path>
</annotationProcessorPaths>
```

### 5.4 Error: "Table PRODUCT not found"

```
Caused by: org.h2.jdbc.JdbcSQLSyntaxErrorException: Table "PRODUCT" not found
```

**Causa**: `data.sql` se ejecuta antes de que Hibernate cree las tablas.

**Solución**: Agregar en `application.yml` (ya incluido):
```yaml
spring:
  jpa:
    defer-datasource-initialization: true
```

### 5.5 Error en tests @DataJpaTest con data.sql

**Causa**: `@DataJpaTest` ejecuta `data.sql` pero usa su propia base de datos H2.

**Solución**: Deshabilitar la inicialización SQL en el test (ya incluido):
```java
@DataJpaTest
@TestPropertySource(properties = {
    "spring.sql.init.mode=never",
    "spring.jpa.defer-datasource-initialization=false"
})
```

---

## 6. CI/CD (Integración Continua)

### 6.1 GitHub Actions (workflow sugerido)

Crear `.github/workflows/ci.yml` en cada repositorio:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: mvn clean verify
      - run: npm ci && npm run test:coverage
      - uses: actions/upload-artifact@v4
        with:
          name: jacoco-report
          path: target/site/jacoco/
```

### 6.2 Verificación de Cobertura en Build

JaCoCo está configurado como **gate de calidad** en cada `pom.xml`:

```xml
<execution>
    <id>check</id>
    <goals><goal>check</goal></goals>
    <configuration>
        <rules>
            <rule>
                <element>BUNDLE</element>
                <limits>
                    <limit>
                        <counter>LINE</counter>
                        <value>COVEREDRATIO</value>
                        <minimum>0.60</minimum>
                    </limit>
                </limits>
            </rule>
        </rules>
    </configuration>
</execution>
```

Si la cobertura baja del 60%, `mvn verify` falla inmediatamente.

---

## 7. Resumen de Comandos Rápidos

```bash
# ===== BACKEND =====

# Inventory Service (31 tests, >87% cobertura)
cd inventory-service && mvn clean verify

# Order Service (20 tests, >88% cobertura)
cd order-service && mvn clean verify

# Shipping Service (19 tests, >87% cobertura)
cd shipping-service && mvn clean verify

# BFF Gateway (16 tests, >85% cobertura)
cd bff-gateway && mvn clean verify

# ===== FRONTEND =====

# Frontend (61 tests, >81% cobertura)
cd frontend && npm run test:coverage

# ===== TODOS A LA VEZ =====

# Backend
for dir in inventory-service order-service shipping-service bff-gateway; do
  (cd "$dir" && mvn clean verify) &
done
wait

# Frontend
cd frontend && npm run test:coverage
```
