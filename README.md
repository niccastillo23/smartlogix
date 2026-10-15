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

- `docs/informe/Informe_EP3_ISY1102_SmartLogix.pdf` - informe de seguridad y calidad (Encargo 2): criterios, plan de pruebas, casos, ejecución, incidentes y análisis ético y normativo.
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

\## 📈 Evolución del Proyecto y Entregas Semestrales El desarrollo y aseguramiento de calidad de \*\*SmartLogix\*\* se estructuró en tres entregas semestrales correspondientes a la asignatura \*\*ISY1102 (Seguridad y Calidad en el Desarrollo de Software)\*\* [1, 2]: --- ### 🔹 Encargo 1 (Ev1) – Planteamiento del Marco, Arquitectura y Estrategia Inicial \* \*\*Enfoque\*\*: Definición de la arquitectura base de microservicios (React 18 + Spring Boot 3.2 / Java 21) y diseño del plan de pruebas inicial [1]. \* \*\*Marcos y Estándares\*\*: \* \*\*ISO/IEC 25010\*\*: Criterios de mantenibilidad, usabilidad y fiabilidad [1, 3]. \* \*\*OWASP Top 10\*\*: Seguridad en APIs REST y autenticación centralizada mediante BFF Gateway con JWT [1, 3]. \* \*\*Ley 19.628\*\*: Marco normativo chileno sobre Protección de la Vida Privada para el tratamiento de datos personales [3]. \* \*\*Estrategia propuesto\*\*: Enfoque mixto con pruebas unitarias en backend (JUnit 5 + Mockito) y frontend (Vitest), fijando una meta de cobertura JaCoCo \\\\(\\ge 60\\%\\\\) [1, 4, 5]. --- ### 🔹 Encargo 2 (EP2) – Auditoría sobre Código Real, Docker y Remediación \* \*\*Enfoque\*\*: Medición estricta sobre el código fuente, corrección de premisas iniciales y despliegue reproducible en contenedores Docker [6-8]. \* \*\*Línea Base vs. Versión Mitigada\*\*: \* \*\*Batería de Pruebas\*\*: De \*\*19 casos de prueba (CP-01 a CP-19)\*\*, la línea base aprobó solo \*\*5/19\*\*, mientras que la versión final mitigada en Docker alcanzó \*\*18/19 casos aprobados\*\* [9, 10]. \* \*\*Remediación de Vulnerabilidades\*\*: \* Implementación de \*\*BCrypt\*\* para cifrado de contraseñas (\`INC-01\`) [11, 12]. \* Extracción del secreto JWT a variables de entorno (\`${JWT\_SECRET}\`) fuera del código fuente (\`INC-02\`) [11, 12]. \* Corrección del parámetro \`argLine\` en Maven (\`INC-07\`), activando el gate de \*\*JaCoCo\*\* con coberturas finales entre \*\*74.3% y 95.2%\*\* en microservicios backend [13, 14]. \* \*\*Gestión de Incidentes\*\*: Registro y clasificación de \*\*18 incidentes (INC-01 a INC-18)\*\* [9, 15]. --- ### 🔹 Encargo 3 (EP3) – DevSecOps, Automatización E2E, CI/CD y Mantenimiento \* \*\*Enfoque\*\*: Integración de pruebas automatizadas E2E/API, análisis estático y dinámico de seguridad, pipeline de Integración Continua y plan de mantenimiento sostenible [16, 17]. \* \*\*Cierre de Pruebas y Automatización\*\*: \* Matriz extendida a \*\*23 casos de prueba (CP-01 a CP-23)\*\*, logrando \*\*22/23 casos aprobados\*\* en la versión final [18-20]. \* Suite de \*\*11 pruebas automatizadas E2E y de API con Playwright\*\* (\`e2e/\`), con \*\*100% de éxito (11/11)\*\* en 6.8 segundos [21-23]. \* \*\*Integración de Herramientas de Seguridad (DevSecOps)\*\*: \* \*\*SAST\*\*: SpotBugs + FindSecBugs, ESLint con reglas de seguridad y SonarQube [16, 24, 25]. \* \*\*DAST\*\*: Escaneos dinámicos automatizados sobre la API e interfaz con \*\*OWASP ZAP\*\* [16, 25]. \* \*\*SCA\*\*: Filtrado con \`npm audit --omit=dev\` garantizando 0 vulnerabilidades críticas/altas en producción [16, 24, 26]. \* \*\*CI/CD\*\*: Pipeline automatizado en \*\*GitHub Actions\*\* (\`.github/workflows/ci.yml\`) que ejecuta compilación, tests, Playwright y DAST en cada PR [16, 23]. \* \*\*Mantenimiento y Cumplimiento\*\*: Mapeo acumulado de \*\*25 incidentes (INC-01 a INC-25)\*\*, 7 propuestas de remediación continua (\*\*SEG-01 a SEG-07\*\*) y adecuación técnica ante la reforma de la \*\*Ley 21.719\*\* [20, 27, 28].

1. **Repository** (Inventory): `ProductRepository` con consultas JPQL personalizadas.
2. **Factory Method** (Orders): `OrderFactory` → `WebOrderFactory` (5 %, STANDARD) / `MarketplaceOrderFactory` (10 %, EXPRESS).
3. **Circuit Breaker** (Shipping): Resilience4j con fallback en `ExternalCarrierService` (tracking `FBK-`, entrega en 7 días).
4. **API Gateway / BFF**: autenticación JWT, proxy a los microservicios y traducción de errores.
