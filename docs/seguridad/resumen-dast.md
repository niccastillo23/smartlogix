# Resumen DAST (OWASP ZAP)

Escaneo sobre el stack Docker local (solo localhost, en línea con la autorización de la asignatura).

### Baseline del frontend (http://localhost:5173, sin sesión)

| Riesgo | Alerta | Instancias |
|---|---|---|
| Medium | Content Security Policy (CSP) Header Not Set | 3 |
| Low | Cross-Origin-Embedder-Policy Header Missing or Invalid | 3 |
| Low | Cross-Origin-Opener-Policy Header Missing or Invalid | 3 |
| Low | Cross-Origin-Resource-Policy Header Missing or Invalid | 4 |
| Low | Permissions Policy Header Not Set | 4 |
| Low | Server Leaks Version Information via "Server" HTTP Response Header Field | 5 |
| Informational | Modern Web Application | 3 |
| Informational | Storable and Cacheable Content | 5 |


### Escaneo de la API del BFF (OpenAPI, con token válido inyectado)

| Riesgo | Alerta | Instancias |
|---|---|---|
| Low | A Server Error response code was returned by the server | 8 |
| Low | Cross-Origin-Resource-Policy Header Missing or Invalid | 5 |
| Low | Timestamp Disclosure - Unix | 4 |
| Informational | A Client Error response code was returned by the server | 652 |
| Informational | Authentication Request Identified | 1 |
| Informational | Non-Storable Content | 5 |
| Informational | Session Management Response Identified | 2 |
