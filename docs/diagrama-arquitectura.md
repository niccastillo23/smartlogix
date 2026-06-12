# Diagrama de Arquitectura - SmartLogix

## Descripción

El siguiente diagrama muestra la arquitectura de microservicios del proyecto **SmartLogix**, un eCommerce de perfumes construido con Spring Boot 3.2, React y patrones de diseño empresariales.

## Diagrama Mermaid.js

```mermaid
graph TB
    subgraph Frontend["Frontend - React + Vite (Puerto 5173)"]
        UI["Interfaz de Usuario<br/>React 18 + Axios"]
        RC["React Router<br/>Navegación SPA"]
        CTX["AuthContext<br/>Gestión JWT"]
    end

    subgraph BFF["BFF Gateway - Spring Boot (Puerto 8080)"]
        AUTH["AuthController<br/>/api/auth/**"]
        JWT["JwtUtil + JwtAuthFilter<br/>Seguridad JWT"]
        PP["ProductProxy<br/>RestTemplate"]
        OP["OrderProxy<br/>RestTemplate"]
        SP["ShippingProxy<br/>RestTemplate"]
        SWAGGER_BFF["Swagger UI<br/>/swagger-ui.html"]
    end

    subgraph MS1["Inventory Service - Puerto 8081"]
        PC["ProductController<br/>/api/products/**"]
        PS["ProductService<br/>Repository Pattern"]
        PR["ProductRepository<br/>Spring Data JPA"]
        DB1[("H2 Database<br/>inventorydb")]
        SWAGGER1["Swagger UI<br/>/swagger-ui.html"]
    end

    subgraph MS2["Order Service - Puerto 8082"]
        OC["OrderController<br/>/api/orders/**"]
        OS["OrderService"]
        WF["WebOrderFactory<br/>5% desc. + Standard"]
        MF["MarketplaceOrderFactory<br/>10% desc. + Express"]
        OR["OrderRepository<br/>Spring Data JPA"]
        DB2[("H2 Database<br/>orderdb")]
        SWAGGER2["Swagger UI<br/>/swagger-ui.html"]
    end

    subgraph MS3["Shipping Service - Puerto 8083"]
        SC["ShippingController<br/>/api/shipments/**"]
        SS["ShippingService"]
        CB["Circuit Breaker<br/>Resilience4j"]
        ECS["ExternalCarrierService"]
        SR["ShipmentRepository<br/>Spring Data JPA"]
        DB3[("H2 Database<br/>shippingdb")]
        EXT["Carrier API Externa<br/>(Simulada)"]
        SWAGGER3["Swagger UI<br/>/swagger-ui.html"]
    end

    UI -->|"HTTP/Axios<br/>Bearer JWT"| BFF
    AUTH --> JWT
    JWT -->|"Token válido"| PP
    JWT -->|"Token válido"| OP
    JWT -->|"Token válido"| SP

    PP -->|"REST GET/POST/PUT/PATCH"| PC
    OP -->|"REST GET/POST/PATCH"| OC
    SP -->|"REST GET/POST/PATCH"| SC

    PS --> PR
    PR --> DB1

    OS --> WF
    OS --> MF
    OS --> OR
    OR --> DB2

    SS --> CB
    CB -->|"Cerrado/Semi-abierto"| ECS
    CB -->|"Abierto - Fallback"| ECS
    ECS -->|"HTTP"| EXT
    SS --> SR
    SR --> DB3

    style Frontend fill:#1a1a2e,stroke:#e94560,color:#fff
    style BFF fill:#16213e,stroke:#0f3460,color:#fff
    style MS1 fill:#0f3460,stroke:#533483,color:#fff
    style MS2 fill:#0f3460,stroke:#533483,color:#fff
    style MS3 fill:#0f3460,stroke:#533483,color:#fff
    style DB1 fill:#e94560,stroke:#333,color:#fff
    style DB2 fill:#e94560,stroke:#333,color:#fff
    style DB3 fill:#e94560,stroke:#333,color:#fff
```

## Flujo de una Compra Completa

```mermaid
sequenceDiagram
    participant U as Usuario (Browser)
    participant FE as Frontend React
    participant BFF as BFF Gateway
    participant INV as Inventory Service
    participant ORD as Order Service
    participant SHP as Shipping Service
    participant EXT as Carrier Externo

    U->>FE: 1. Registro/Login
    FE->>BFF: POST /api/auth/register
    BFF-->>FE: JWT Token
    FE-->>U: Token guardado en localStorage

    U->>FE: 2. Ver catálogo
    FE->>BFF: GET /api/products (Bearer JWT)
    BFF->>INV: GET /api/products
    INV-->>BFF: Lista de perfumes
    BFF-->>FE: Lista de perfumes
    FE-->>U: Grid de productos

    U->>FE: 3. Agregar al carrito + Checkout
    FE->>BFF: POST /api/orders (Bearer JWT)
    BFF->>ORD: POST /api/orders
    Note over ORD: Factory Method:<br/>WEB (5% desc) o<br/>MARKETPLACE (10% desc)
    ORD-->>BFF: Orden creada (id=1)
    BFF-->>FE: Respuesta de orden

    FE->>BFF: POST /api/shipments (Bearer JWT)
    BFF->>SHP: POST /api/shipments
    Note over SHP: Circuit Breaker:<br/>Llama al carrier externo
    SHP->>EXT: Registrar envío
    EXT-->>SHP: Tracking number + ETA
    SHP-->>BFF: Envío creado
    BFF-->>FE: Confirmación de envío
    FE-->>U: Compra completada

    U->>FE: 4. Ver estado del pedido
    FE->>BFF: GET /api/orders (Bearer JWT)
    BFF->>ORD: GET /api/orders
    ORD-->>BFF: Lista de órdenes
    BFF-->>FE: Lista de órdenes
    FE-->>U: Estado de pedidos
```

## Componentes y Tecnologías

| Componente | Tecnología | Puerto | Patrón de Diseño |
|-----------|-----------|--------|-----------------|
| Frontend | React 18 + Vite + Axios | 5173 | Context API |
| BFF Gateway | Spring Boot 3.2 + Spring Security + JWT | 8080 | API Gateway |
| Inventory Service | Spring Boot 3.2 + Spring Data JPA + H2 | 8081 | Repository Pattern |
| Order Service | Spring Boot 3.2 + Spring Data JPA + H2 | 8082 | Factory Method |
| Shipping Service | Spring Boot 3.2 + Spring Data JPA + H2 + Resilience4j | 8083 | Circuit Breaker |

## Patrones de Diseño Implementados

### 1. Repository Pattern (Inventory Service)
- `ProductRepository` extiende `JpaRepository`
- `ProductService` abstrae la lógica de negocio del acceso a datos
- Consultas personalizadas con `@Query` (JPQL)

### 2. Factory Method (Order Service)
- `OrderFactory` (clase abstracta) define `createOrder()`
- `WebOrderFactory`: descuento 5%, envío STANDARD
- `MarketplaceOrderFactory`: descuento 10%, envío EXPRESS
- `OrderService.resolveFactory()` selecciona la factory según `orderType`

### 3. Circuit Breaker (Shipping Service)
- Resilience4j protege las llamadas al carrier externo
- Configuración: sliding window 5, failure rate 50%, wait 10s
- Fallback automático: genera tracking "FBK-" con ETA de 7 días
- Campo `circuitBreakerFallback` en la entidad para trazabilidad
