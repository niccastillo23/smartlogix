# Build multi-etapa: compila con Maven/JDK 21 y ejecuta sobre JRE 21 con usuario no root.
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -B -q dependency:go-offline
COPY src ./src
RUN mvn -B -q -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
RUN useradd --system --uid 10001 --no-create-home appuser
COPY --from=build /app/target/shipping-service-1.0.0.jar app.jar
USER appuser
EXPOSE 8083
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
