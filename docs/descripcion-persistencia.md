# Informe de Persistencia de Datos - SmartLogix

## 1. Introducción

El presente informe detalla la estrategia de persistencia de datos implementada en el proyecto **SmartLogix**, un sistema eCommerce de perfumes basado en una arquitectura de microservicios. El objetivo principal es demostrar cómo se garantiza el **desacoplamiento total** entre los servicios mediante el patrón de **Base de Datos por Servicio (Database per Service)**, utilizando **Spring Data JPA** como framework de acceso a datos y **H2 Database** como motor embebido.

## 2. Patrón Database per Service

### 2.1 Fundamento Teórico

En una arquitectura de microservicios, cada servicio debe ser autónomo e independiente. El patrón **Database per Service** establece que cada microservicio posee su propia base de datos, y ningún otro servicio puede acceder directamente a ella. La comunicación entre servicios se realiza exclusivamente a través de APIs REST.

Este patrón garantiza:
- **Desacoplamiento**: Cada servicio puede evolucionar su esquema de datos independientemente
- **Autonomía**: Fallos en un servicio no afectan la persistencia de otros
- **Escalabilidad**: Cada base de datos puede escalarse de forma independiente
- **Seguridad**: Los datos están aislados por servicio

### 2.2 Implementación en SmartLogix

El proyecto implementa **3 bases de datos independientes**, una por cada microservicio:

| Microservicio | Base de Datos | URL JDBC | Puerto |
|--------------|--------------|----------|--------|
| Inventory Service | `inventorydb` | `jdbc:h2:mem:inventorydb` | 8081 |
| Order Service | `orderdb` | `jdbc:h2:mem:orderdb` | 8082 |
| Shipping Service | `shippingdb` | `jdbc:h2:mem:shippingdb` | 8083 |

Cada servicio se configura en su propio `application.yml`:

```yaml
# inventory-service/application.yml
spring:
  datasource:
    url: jdbc:h2:mem:inventorydb
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    database-platform: org.hibernate.dialect.H2Dialect
    hibernate:
      ddl-auto: update
    show-sql: true
```

```yaml
# order-service/application.yml
spring:
  datasource:
    url: jdbc:h2:mem:orderdb
    # ... misma estructura, base de datos diferente
```

```yaml
# shipping-service/application.yml
spring:
  datasource:
    url: jdbc:h2:mem:shippingdb
    # ... misma estructura, base de datos diferente
```

## 3. Spring Data JPA - Configuración y Uso

### 3.1 Entidades JPA

Cada microservicio define sus propias entidades JPA anotadas con `@Entity`:

#### Inventory Service - Entidad `Product`
```java
@Entity
@Table(name = "product")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 150)
    private String name;
    
    @Column(nullable = false, length = 100)
    private String brand;
    
    private String description;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;
    
    @Column(name = "stock_quantity", nullable = false)
    private Integer stockQuantity;
    
    private String fragrance;
    
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

#### Order Service - Entidades `Order` y `OrderItem`
```java
@Entity
@Table(name = "orders")
public class Order {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private Long customerId;
    private String customerName;
    private String email;
    
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items;
    
    private BigDecimal totalAmount;
    private String orderType;
    private String status;
    private BigDecimal discountApplied;
    private String shippingMethod;
}

@Entity
@Table(name = "order_item")
public class OrderItem {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private Long productId;
    private String productName;
    private Integer quantity;
    private BigDecimal unitPrice;
    private BigDecimal subtotal;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id")
    private Order order;
}
```

#### Shipping Service - Entidad `Shipment`
```java
@Entity
@Table(name = "shipment")
public class Shipment {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private Long orderId;
    private String carrier;
    private String trackingNumber;
    private String status;
    private LocalDate estimatedDelivery;
    private String address;
    private String city;
    private String country;
    private Boolean circuitBreakerFallback;
}
```

### 3.2 Repositorios Spring Data JPA

Cada servicio define interfaces que extienden `JpaRepository`, aprovechando el **Repository Pattern**:

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByBrand(String brand);
    List<Product> findByFragrance(String fragrance);
    
    @Query("SELECT p FROM Product p WHERE p.price BETWEEN :min AND :max")
    List<Product> findByPriceRange(@Param("min") BigDecimal min, @Param("max") BigDecimal max);
    
    @Query("SELECT p FROM Product p WHERE p.stockQuantity > 0")
    List<Product> findInStock();
}
```

**Ventajas de Spring Data JPA:**
- Generación automática de consultas a partir del nombre del método (`findByBrand`, `findByFragrance`)
- Soporte para consultas JPQL personalizadas con `@Query`
- CRUD completo heredado de `JpaRepository` (save, findById, findAll, delete, etc.)
- Gestión automática de transacciones con `@Transactional`

### 3.3 Ciclo de Vida de las Entidades

Las entidades utilizan callbacks JPA para auditoría automática:

```java
@PrePersist
protected void onCreate() {
    createdAt = LocalDateTime.now();
    updatedAt = LocalDateTime.now();
}

@PreUpdate
protected void onUpdate() {
    updatedAt = LocalDateTime.now();
}
```

## 4. Desacoplamiento entre Servicios

### 4.1 Comunicación vía API REST

Los servicios **nunca** acceden directamente a la base de datos de otro servicio. Toda la comunicación se realiza a través del BFF Gateway usando `RestTemplate`:

```
Frontend → BFF Gateway → Inventory Service (inventorydb)
                        → Order Service (orderdb)
                        → Shipping Service (shippingdb)
```

### 4.2 Datos Duplicados Intencionalmente

Para mantener el desacoplamiento, algunos datos se duplican entre servicios:

- `OrderItem` en Order Service almacena `productName` y `unitPrice` (copiados de Inventory)
- `Shipment` en Shipping Service almacena `orderId` (referencia lógica, no FK física)

Esto es una decisión de diseño consciente: evita acoplamiento temporal y permite que cada servicio funcione aunque otro esté caído.

### 4.3 H2 Console por Servicio

Cada servicio expone su propia consola H2 para inspección directa:

| Servicio | URL de Consola H2 |
|----------|-------------------|
| Inventory | `http://localhost:8081/h2-console` |
| Order | `http://localhost:8082/h2-console` |
| Shipping | `http://localhost:8083/h2-console` |

## 5. Datos de Prueba

El Inventory Service incluye un archivo `data.sql` que se ejecuta automáticamente al iniciar, cargando 10 perfumes de ejemplo:

```sql
INSERT INTO product (id, name, brand, description, price, stock_quantity, fragrance)
VALUES (1, 'Sauvage Eau de Parfum', 'Dior', 'Fragancia masculina...', 120.00, 50, 'Amaderado');
-- ... 9 perfumes más
```

## 6. Migración a PostgreSQL (Producción)

Para migrar a PostgreSQL en producción, solo se requiere cambiar la configuración en cada `application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://host:5432/inventorydb
    driver-class-name: org.postgresql.Driver
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    hibernate:
      ddl-auto: validate
```

El código Java (entidades, repositorios, servicios) **no requiere cambios**, gracias a la abstracción de JPA.

## 7. Conclusiones

1. El patrón **Database per Service** garantiza el desacoplamiento total entre microservicios, permitiendo evolución independiente y tolerancia a fallos.
2. **Spring Data JPA** simplifica significativamente el acceso a datos, eliminando boilerplate y proporcionando un repositorio genérico robusto.
3. **H2 Database** es ideal para desarrollo y pruebas, con la flexibilidad de migrar a PostgreSQL sin cambios en el código.
4. La duplicación intencional de datos entre servicios es un trade-off aceptable para mantener la autonomía de cada microservicio.
