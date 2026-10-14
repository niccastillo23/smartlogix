# SmartLogix - eCommerce de Perfumes

Sistema de comercio electrónico de perfumes con arquitectura de microservicios: Spring Boot 3.2 (Java 21), React 18 y Docker.

Proyecto del caso semestral de **ISY1102 - Seguridad y calidad en el desarrollo de software**. Además del código, el repositorio contiene el plan de pruebas, las evidencias de ejecución y el informe de la Evaluación Parcial 3.

## Arquitectura

| Componente | Tecnología | Puerto | Patrón |
|---|---|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Axios | 5173 | Context API |
| **BFF Gateway** | Spring Boot 3.2, Spring Security, JWT | 8080 | API Gateway |
| **Inventory Service** | Spring Boot 3.2, JPA, H2 | 8081 | Repository |
| **Order Service** | Spring Boot 3.2, JPA, H2 | 8082 | Factory Method |
| **Shipping Service** | Spring Boot 3.2, JPA, H2, Resilience4j | 8083 | Circuit Breaker |

El frontend llama a `/api`. En desarrollo lo reenvía Vite al BFF; en Docker lo reenvía nginx. Los microservicios solo son accesibles dentro de la red de Docker, y el BFF es el único punto de entrada autenticado.

## Requisitos

- Java 21 (JDK 25 funciona para compilar y probar, pero SpotBugs 4.8 no lee sus clases: los análisis estáticos deben ejecutarse con JDK 21)
- Maven 3.9+
- Node.js 18+ y npm 9+
- Docker y Docker Compose (para el despliegue completo)

## Despliegue con Docker (recomendado)

```bash
cp .env.example .env
# Reemplazar JWT_SECRET por un valor aleatorio de al menos 64 caracteres:
#   openssl rand -base64 64
docker compose up -d --build
```

- Aplicación: http://localhost:5173
- Documentación del BFF (Swagger): http://localhost:8080/swagger-ui.html

`JWT_SECRET` es obligatorio. Sin esa variable, `docker compose` no inicia y el BFF no arranca. El archivo `.env` está en `.gitignore` y no debe versionarse.

## Ejecución local (sin Docker)

```bash
export JWT_SECRET="<valor de al menos 64 caracteres>"

cd inventory-service && mvn spring-boot:run    # 8081
cd order-service     && mvn spring-boot:run    # 8082
cd shipping-service  && mvn spring-boot:run    # 8083
cd bff-gateway       && mvn spring-boot:run    # 8080 (después de los anteriores)

cd frontend && npm install && npm run dev      # 5173
```

## Pruebas

### Unitarias e integración (backend)

Cada microservicio tiene su suite con JUnit 5, Mockito y MockMvc. JaCoCo verifica que la cobertura de líneas sea de al menos 60 %.

```bash
cd <servicio> && JWT_SECRET=<valor> mvn clean verify
```

| Servicio | Pruebas | Cobertura de líneas |
|---|---|---|
| Inventory Service | 38 | 95,2 % |
| Order Service | 26 | 88,7 % |
| Shipping Service | 25 | 86,3 % |
| BFF Gateway | 32 | 74,3 % |
| **Total** | **121** | |

### Unitarias (frontend)

```bash
cd frontend
npm test                  # 55 pruebas con Vitest y React Testing Library
npm run test:coverage     # cobertura: 68,52 % de statements
```

### Casos de prueba funcionales, de seguridad y de rendimiento

Con los servicios en ejecución (Docker o local):

```bash
python3 docs/pruebas/ejecutar_casos.py <etiqueta>
```

El script ejecuta 19 casos (`CP-01` a `CP-19`) contra el BFF con un token real, y escribe los resultados en `docs/evidencias/<etiqueta>/`. Cada caso registra requisito, datos de entrada, resultado esperado, criterio de aceptación, criticidad, responsable y fecha. Los tokens JWT se redactan antes de guardar la evidencia.

Resultado de la última ejecución sobre el stack Docker: **18 de 19 casos aprobados**. El caso que falla (CP-16) corresponde a un riesgo residual documentado (ver "Estado de seguridad").

### Análisis estático y dependencias

```bash
# Backend (con JDK 21): SpotBugs + FindSecBugs, filtro documentado en bff-gateway/spotbugs-exclude.xml
cd <servicio> && mvn -Psecurity com.github.spotbugs:spotbugs-maven-plugin:4.8.6.6:spotbugs

# Frontend: ESLint con reglas de seguridad y auditoría de dependencias
cd frontend && npx eslint "src/**/*.{js,jsx}"
cd frontend && npm audit
```

## Documentación

- `docs/informe/Informe_EP3_ISY1102_SmartLogix.pdf` - informe de seguridad y calidad (Evaluación Parcial 3): criterios, plan de pruebas, casos, ejecución, incidentes y análisis ético y normativo.
- `docs/evidencias/` - resultados de ejecución (JSON y texto), logs de compilación y capturas.
- `docs/pruebas/ejecutar_casos.py` - ejecutor reproducible de los casos de prueba.
- `docs/informe/generar_informe.py` y `publicar_informe.sh` - regeneran el informe a partir de las evidencias (`publicar_informe.sh` requiere Microsoft Word en macOS).
- `docs/diagrama-arquitectura.md`, `docs/descripcion-persistencia.md`, `docs/swagger-api.md` - arquitectura, persistencia y uso de Swagger.
- `docs/TESTING.md` y `docs/informe-pruebas.md` - guías de pruebas de versiones anteriores; sus cifras no están actualizadas.
- `postman/smartlogix-collection.json` - colección Postman.

## Estado de seguridad

Hallazgos del análisis, con su estado al momento del informe. El detalle completo (criticidad, ubicación y tratamiento) está en la sección 5.3 del informe.

| Estado | Hallazgo |
|---|---|
| Corregido | Contraseñas almacenadas en texto plano (ahora BCrypt) |
| Corregido | Secreto JWT literal en `application.yml` (ahora `${JWT_SECRET}`) |
| Corregido | Microservicios accesibles directamente desde la red del host (ya no se publican puertos) |
| Corregido | Gate de cobertura JaCoCo inactivo por `argLine` |
| Corregido | Alta de productos con HTTP 500 por secuencia de IDs |
| Abierto | 3 vulnerabilidades críticas y 6 altas en herramientas de desarrollo del frontend (vitest, vite, tailwind). Corregirlas exige saltos de versión mayor |
| Abierto | Los microservicios no validan el JWT por sí mismos; dependen de la red y del BFF |
| Abierto | El token JWT se guarda en `localStorage` |
| Abierto | El endpoint de login no limita intentos |
| Abierto | El secreto JWT original aparece en el historial de git: debe considerarse expuesto y rotarse |
| Riesgo aceptado | Advertencia CSRF de SpotBugs en `SecurityConfig`: la API usa Bearer y sesiones stateless |

Los datos son de demostración: H2 en memoria y usuarios que se pierden al reiniciar el BFF.

## Patrones de diseño

1. **Repository** (Inventory): `ProductRepository` con consultas JPQL personalizadas.
2. **Factory Method** (Orders): `OrderFactory` → `WebOrderFactory` (5 %, STANDARD) / `MarketplaceOrderFactory` (10 %, EXPRESS).
3. **Circuit Breaker** (Shipping): Resilience4j con fallback en `ExternalCarrierService` (tracking `FBK-`, entrega en 7 días).
4. **API Gateway / BFF**: autenticación JWT, proxy a los microservicios y traducción de errores.
