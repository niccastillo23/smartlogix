# SmartLogix - eCommerce de Perfumes

Sistema de comercio electrónico de perfumes con arquitectura de microservicios: Spring Boot 3.2 (Java 21), React 18 y Docker.

Proyecto del caso semestral de **ISY1102 - Seguridad y calidad en el desarrollo de software**. Además del código, el repositorio contiene el plan de pruebas, las evidencias de ejecución y el informe del Encargo 2.

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
| Inventory Service | 41 | 95,1 % |
| Order Service | 29 | 93,8 % |
| Shipping Service | 28 | 92,8 % |
| BFF Gateway | 36 | 77,1 % |
| **Total** | **134** | |

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

El script ejecuta 23 casos (`CP-01` a `CP-23`) contra el BFF con un token real, y escribe los resultados en `docs/evidencias/<etiqueta>/`. Cada caso registra requisito, datos de entrada, resultado esperado, criterio de aceptación, criticidad, responsable y fecha. Los tokens JWT se redactan antes de guardar la evidencia.

Resultado de la última ejecución sobre el stack Docker (rama `v2`): **22 de 23 casos aprobados**. El caso que falla (CP-16) corresponde a un riesgo residual documentado (ver "Estado de seguridad").

### Análisis estático y dependencias

```bash
# Backend (con JDK 21): SpotBugs + FindSecBugs, filtro documentado en bff-gateway/spotbugs-exclude.xml
cd <servicio> && mvn -Psecurity com.github.spotbugs:spotbugs-maven-plugin:4.8.6.6:spotbugs

# Frontend: ESLint con reglas de seguridad y auditoría de dependencias
cd frontend && npx eslint "src/**/*.{js,jsx}"
cd frontend && npm audit
```

## Automatización, DAST y CI/CD

- **Pipeline:** `.github/workflows/ci.yml` se ejecuta en cada push a `main` y `v2` y en cada pull request. Jobs: backend (un job por servicio, con pruebas, JaCoCo y SpotBugs), frontend (pruebas, ESLint y `npm audit --omit=dev`), E2E y API sobre Docker, y DAST con OWASP ZAP baseline. Las puertas que bloquean el merge son: prioridad 1 de SpotBugs, critical/high en producción y alertas de riesgo alto de ZAP.
- **Secreto requerido:** `JWT_SECRET` en *Settings → Secrets and variables → Actions*.
- **E2E y API:** `e2e/` con Playwright (5 flujos de interfaz, 6 pruebas de API):

  ```bash
  cd e2e && npm ci && npx playwright install chromium
  npx playwright test   # con el stack en ejecución
  ```

- **DAST:** `docs/seguridad/ejecutar_zap.sh <etiqueta>` ejecuta ZAP contra el stack local (solo `localhost`).
- **SAST con SonarQube:** configuración en `docs/seguridad/sonarqube/` (análisis local en Docker; no se publican credenciales).
- **Diagrama de controles:** `docs/seguridad/diagramas/pipeline.html`.

## Documentación

- `docs/informe/Informe_Encargo3_ISY1102_SmartLogix.pdf` - informe del Encargo 3: pruebas de seguridad (DAST, SAST, SCA), automatización, CI/CD, incidentes, plan de mantenimiento y análisis ético y normativo.
- `docs/informe/Informe_EP3_ISY1102_SmartLogix.pdf` - informe del Encargo 2: criterios, plan de pruebas, casos, ejecución, incidentes y análisis ético y normativo.
- `docs/evidencias/` - resultados de ejecución (JSON y texto), logs de compilación y capturas.
- `docs/pruebas/ejecutar_casos.py` - ejecutor reproducible de los casos de prueba.
- `docs/informe/generar_informe.py` y `publicar_informe.sh` - regeneran el informe a partir de las evidencias (`publicar_informe.sh` requiere Microsoft Word en macOS).
- `docs/diagrama-arquitectura.md`, `docs/descripcion-persistencia.md`, `docs/swagger-api.md` - arquitectura, persistencia y uso de Swagger.
- `docs/TESTING.md` y `docs/informe-pruebas.md` - guías de pruebas de versiones anteriores; sus cifras no están actualizadas.
- `postman/smartlogix-collection.json` - colección Postman.

## Estado de seguridad

Hallazgos del análisis, con su estado en la rama `v2`. El detalle completo (criticidad, ubicación, tratamiento y evidencia) está en el informe del Encargo 3 (`docs/informe/`).

| Estado | Hallazgo |
|---|---|
| Corregido | Contraseñas almacenadas en texto plano (ahora BCrypt) |
| Corregido | Secreto JWT literal en `application.yml` (ahora `${JWT_SECRET}`) |
| Corregido | Microservicios accesibles sin token desde la red (ahora validan JWT firmado en cada servicio) |
| Corregido | Bloqueo de intentos de login tras 5 fallos (HTTP 429) |
| Corregido | PATCH a través del BFF (503) y parámetro obligatorio ausente (500, ahora 400) |
| Corregido | Valor de `status` concatenado en la URL del BFF (ahora codificado) |
| Corregido | Error de login que no se mostraba en la interfaz |
| Corregido | Ausencia de CSP y cabeceras de aislamiento (ahora en nginx) |
| Corregido | Gate de cobertura JaCoCo inactivo por `argLine`; alta de productos con HTTP 500 |
| Abierto | Secreto JWT original en el historial de git: debe considerarse expuesto y rotarse (SEG-01) |
| Abierto | Token JWT en `localStorage` (SEG-02) |
| Abierto | Duplicación de código entre microservicios: el quality gate de SonarQube falla (SEG-03) |
| Abierto | Dependencias de build del frontend con vulnerabilidades críticas y altas (vitest, vite, tailwind) (SEG-05) |
| Riesgo residual | `style-src 'unsafe-inline'` en la CSP por los estilos en línea de los componentes (SEG-04) |
| Riesgo aceptado | CSRF deshabilitado (4 issues S4502 de SonarQube y prioridad 1 de SpotBugs): API stateless con Bearer, sin cookies |

Los datos son de demostración: H2 en memoria y usuarios que se pierden al reiniciar el BFF.

## Patrones de diseño

1. **Repository** (Inventory): `ProductRepository` con consultas JPQL personalizadas.
2. **Factory Method** (Orders): `OrderFactory` → `WebOrderFactory` (5 %, STANDARD) / `MarketplaceOrderFactory` (10 %, EXPRESS).
3. **Circuit Breaker** (Shipping): Resilience4j con fallback en `ExternalCarrierService` (tracking `FBK-`, entrega en 7 días).
4. **API Gateway / BFF**: autenticación JWT, proxy a los microservicios y traducción de errores.
