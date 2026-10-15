# SmartLogix - eCommerce de Perfumes

Sistema de comercio electrónico de perfumes con arquitectura de microservicios: Spring Boot 3.2 (Java 21), React 18 y Docker.

Proyecto del caso semestral de **ISY1102 - Seguridad y calidad en el desarrollo de software**. Además del código, el repositorio contiene el plan de pruebas, las evidencias de ejecución y los informes de los Encargos 2 y 3.

---

## Arquitectura

| Componente | Tecnología | Puerto | Patrón |
|---|---|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Axios | 5173 | Context API |
| **BFF Gateway** | Spring Boot 3.2, Spring Security, JWT | 8080 | API Gateway |
| **Inventory Service** | Spring Boot 3.2, JPA, H2 | 8081 | Repository |
| **Order Service** | Spring Boot 3.2, JPA, H2 | 8082 | Factory Method |
| **Shipping Service** | Spring Boot 3.2, JPA, H2, Resilience4j | 8083 | Circuit Breaker |

El frontend llama a `/api`: en desarrollo lo reenvía Vite al BFF y en Docker lo reenvía nginx. El BFF es el único punto de entrada. Los microservicios no publican puertos fuera de la red de Docker y validan un JWT firmado en cada petición.

### Patrones de diseño

1. **Repository** (Inventory): `ProductRepository` con consultas JPQL personalizadas.
2. **Factory Method** (Orders): `OrderFactory`, con `WebOrderFactory` (descuento 5 %, envío STANDARD) y `MarketplaceOrderFactory` (descuento 10 %, envío EXPRESS).
3. **Circuit Breaker** (Shipping): Resilience4j con fallback en `ExternalCarrierService` (tracking `FBK-`, entrega en 7 días).
4. **API Gateway / BFF**: autenticación JWT, proxy a los microservicios y traducción de errores.

---

## Evolución del proyecto

El caso se desarrolló en tres entregas de la asignatura ISY1102, cada una sobre el mismo código y con un alcance mayor.

| Entrega | Alcance | Resultados principales |
|---|---|---|
| **Encargo 1** (Evaluación Parcial 1) | Arquitectura de microservicios, plan de pruebas inicial y criterios de calidad (ISO/IEC 25010, OWASP y Ley 19.628). | Plan de pruebas con cobertura objetivo de JaCoCo ≥ 60 %. |
| **Encargo 2** | Auditoría sobre el código real, despliegue en Docker y remediación. | Batería de 19 casos: 5/19 aprobados en la línea base y 18/19 en la versión mitigada. Cifrado de contraseñas con BCrypt, secreto JWT fuera del código y gate de JaCoCo activo. Registro de 18 incidentes. |
| **Encargo 3** | Pruebas de seguridad, automatización y CI/CD. | Batería ampliada a 23 casos: 17/23 en la línea base y 22/23 en la versión final. 11 pruebas E2E y de API con Playwright (11/11, 6,8 s). DAST con OWASP ZAP, SAST con SpotBugs, ESLint y SonarQube, SCA con `npm audit`, pipeline en GitHub Actions y plan de mantenimiento. Registro de 24 incidentes (INC-01 a INC-25, sin el INC-17, documentado en el Encargo 2). |

Los informes de cada entrega están en `docs/informe/` (ver [Documentación](#documentación)).

## Requisitos

- Java 21. JDK 25 sirve para compilar y probar, pero SpotBugs 4.8 no lee sus clases: los análisis estáticos deben ejecutarse con JDK 21.
- Maven 3.9 o superior.
- Node.js 18 o superior, y npm 9 o superior.
- Docker y Docker Compose, para el despliegue completo.

---

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

---

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

El script ejecuta 23 casos (`CP-01` a `CP-23`) contra el BFF con un token real y escribe los resultados en `docs/evidencias/<etiqueta>/`. Cada caso registra requisito, datos de entrada, resultado esperado, criterio de aceptación, criticidad, responsable y fecha. Los tokens JWT se redactan antes de guardar la evidencia.

Resultado de la última ejecución sobre el stack Docker (rama `v2`): **22 de 23 casos aprobados**. El caso que falla (CP-16) corresponde a un riesgo residual documentado (ver [Estado de seguridad](#estado-de-seguridad)).

### Análisis estático y dependencias

```bash
# Backend (con JDK 21): SpotBugs + FindSecBugs; filtros documentados en <servicio>/spotbugs-exclude.xml
cd <servicio> && mvn -Psecurity com.github.spotbugs:spotbugs-maven-plugin:4.8.6.6:spotbugs

# Frontend: ESLint con reglas de seguridad y auditoría de dependencias
cd frontend && npx eslint "src/**/*.{js,jsx}"
cd frontend && npm audit
```

---

## Automatización, DAST y CI/CD

### Pipeline de integración continua

`.github/workflows/ci.yml` se ejecuta en cada push a `main` y `v2` y en cada pull request. Sus jobs son:

- **Backend** (un job por servicio): pruebas, JaCoCo y SpotBugs.
- **Frontend**: pruebas, ESLint y `npm audit --omit=dev`.
- **E2E y API sobre Docker**: Playwright contra el stack levantado.
- **DAST**: OWASP ZAP baseline sobre el frontend desplegado.

Las puertas que bloquean el merge son: prioridad 1 de SpotBugs, critical o high en producción, y alertas de riesgo alto de ZAP.

El pipeline requiere el secreto `JWT_SECRET` en *Settings → Secrets and variables → Actions*.

### Pruebas E2E y de API

Suite en `e2e/` con Playwright: 5 flujos de interfaz y 6 pruebas de API.

```bash
cd e2e && npm ci && npx playwright install chromium
npx playwright test   # con el stack en ejecución
```

### DAST y SAST

- **DAST:** `docs/seguridad/ejecutar_zap.sh <etiqueta>` ejecuta OWASP ZAP contra el stack local (solo `localhost`).
- **SAST con SonarQube:** configuración en `docs/seguridad/sonarqube/`. El análisis corre en un servidor local en Docker y no se publican credenciales.
- **Diagrama de controles:** `docs/seguridad/diagramas/pipeline.html`.

---

## Estado de seguridad

Hallazgos del análisis, con su estado en la rama `v2`. El detalle completo (criticidad, ubicación, tratamiento y evidencia) está en el informe del Encargo 3.

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

---

## Documentación

### Informes

- `docs/informe/Informe_Encargo3_ISY1102_SmartLogix.pdf`: Encargo 3. Pruebas de seguridad (DAST, SAST, SCA), automatización, CI/CD, incidentes, plan de mantenimiento y análisis ético y normativo.
- `docs/informe/Informe_EP3_ISY1102_SmartLogix.pdf`: Encargo 2. Criterios, plan de pruebas, casos, ejecución, incidentes y análisis ético y normativo.

### Evidencias y scripts

- `docs/evidencias/`: resultados de ejecución (JSON y texto), logs de compilación, métricas y capturas.
- `docs/pruebas/ejecutar_casos.py`: ejecutor reproducible de los casos de prueba.
- `docs/informe/generar_informe_encargo3.py`: genera el informe del Encargo 3 a partir de las evidencias.
- `docs/informe/generar_informe.py` y `publicar_informe.sh`: generan y publican el informe del Encargo 2 (`publicar_informe.sh` requiere Microsoft Word en macOS).

### Referencias técnicas

- `docs/diagrama-arquitectura.md`, `docs/descripcion-persistencia.md` y `docs/swagger-api.md`: arquitectura, persistencia y uso de Swagger.
- `docs/TESTING.md` y `docs/informe-pruebas.md`: guías de pruebas de versiones anteriores. Sus cifras no están actualizadas.
- `postman/smartlogix-collection.json`: colección Postman.
