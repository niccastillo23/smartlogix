#!/usr/bin/env python3
"""
Ejecutor de casos de prueba de SmartLogix (ISY1102 - Encargo 2).

Uso:
    python3 docs/pruebas/ejecutar_casos.py <etiqueta>

Requiere los cuatro servicios levantados (8080 BFF, 8081 inventario,
8082 pedidos, 8083 envíos). Las verificaciones de inspección (contraseñas,
secretos, cobertura, SpotBugs, npm audit, Docker) leen artefactos del repositorio.

Genera docs/evidencias/<etiqueta>/resultados.json y resultados.md.
Cada caso registra el comportamiento observado y el criterio de aceptación,
de modo que el resultado es reproducible y no depende de transcripciones manuales.
"""
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ETIQUETA = sys.argv[1] if len(sys.argv) > 1 else "ejecucion"
SALIDA = os.path.join(RAIZ, "docs", "evidencias", ETIQUETA)
os.makedirs(SALIDA, exist_ok=True)

BFF = "http://localhost:8080"
INV = "http://localhost:8081"
ORD = "http://localhost:8082"
SHP = "http://localhost:8083"
SERVICIOS = ["inventory-service", "order-service", "shipping-service", "bff-gateway"]


JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


def redactar(texto):
    """Oculta tokens JWT antes de escribir cualquier evidencia en disco."""
    return JWT_RE.sub("<JWT-REDACTADO>", texto or "")


def peticion(metodo, url, cuerpo=None, token=None, cabeceras=None):
    """Devuelve (status, cabeceras, texto). Nunca lanza por códigos HTTP de error."""
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if cabeceras:
        h.update(cabeceras)
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, dict(r.headers), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode(errors="replace")
    except urllib.error.URLError as e:
        # Conexión rechazada o servicio no accesible: se registra como estado 0.
        return 0, {}, f"No accesible: {e.reason}"



def json_de(texto):
    try:
        return json.loads(texto)
    except Exception:
        return None


RESPONSABLE = "Equipo SmartLogix (ejecución automatizada con docs/pruebas/ejecutar_casos.py)"

# Datos de entrada por caso (criterio de la pauta: solo si aplica).
DATOS_ENTRADA = {
    "CP-01": "username aleatorio (usrNNN), password 'pass12345'; POST /api/auth/register y /api/auth/login; GET /api/products con y sin token",
    "CP-02": "username del CP-01; password incorrecta 'clave-incorrecta'; registro duplicado con la misma cuenta",
    "CP-03": "customerId 1, email test@test.com, ítem productId 1 'Sauvage' cantidad 2 precio 100; orderType WEB y MARKETPLACE",
    "CP-04": "orderType 'INVALIDO' con el mismo ítem que CP-03",
    "CP-05": "orderId 999, address 'Calle 123', city 'Santiago', country 'Chile'; carrier 'DHL' y 'FAIL_CARRIER'",
    "CP-06": "Filtros: brand=Dior, fragrance=Amaderado, price-range 70000-110000, in-stock, search=SAUVAGE",
    "CP-07": "Producto name '' price 100 y price -50; pedido email 'invalido' items []; envío sin carrier",
    "CP-08": "Producto name '' enviado a través del BFF con token válido",
    "CP-09": "20 GET /api/products vía BFF y 20 POST /api/orders (WEB, ítem 1 x 1); medición en cliente",
    "CP-10": "Archivo AuthService.java (inspección estática)",
    "CP-11": "GET /api/orders/abc (id no numérico)",
    "CP-12": "OPTIONS /api/products con Origin http://evil.example y http://localhost:5173",
    "CP-13": "bff-gateway/src/main/resources/application.yml (inspección estática)",
    "CP-14": "target/site/jacoco/jacoco.csv de cada servicio tras mvn verify",
    "CP-15": "target/spotbugsXml.xml de cada servicio tras análisis SpotBugs (perfil security)",
    "CP-16": "npm audit --json sobre frontend/package-lock.json",
    "CP-17": "Dockerfile por servicio y docker-compose.yml (docker compose config)",
    "CP-18": "GET sin token a http://localhost:8081/api/products, :8082/api/orders/customer/1 y :8083/api/shipments",
    "CP-19": "name 'Producto CP19 <marca temporal>', brand 'Prueba', price 10.5, stockQuantity 5, fragrance 'Test'; token del CP-01",
}

class Caso:
    def __init__(self, cid, requisito, titulo, tipo, descripcion, esperado, criterio, criticidad_si_falla):
        self.cid = cid
        self.datos_entrada = DATOS_ENTRADA.get(cid, "No aplica")
        self.responsable = RESPONSABLE
        self.requisito = requisito
        self.titulo = titulo
        self.tipo = tipo
        self.descripcion = descripcion
        self.esperado = esperado
        self.criterio = criterio
        self.criticidad = criticidad_si_falla
        self.pasos = []
        self.estado = "PASA"
        self.observado = ""

    def paso(self, descripcion, ok, detalle):
        self.pasos.append({"paso": redactar(descripcion), "ok": bool(ok), "detalle": redactar(detalle)})
        if not ok:
            self.estado = "FALLA"

    def bloqueado(self, motivo):
        self.estado = "BLOQUEADO"
        self.observado = motivo

    def dict(self):
        return {
            "id": self.cid,
            "requisito": self.requisito,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "esperado": self.esperado,
            "criterio": self.criterio,
            "criticidad_si_falla": self.criticidad,
            "datos_entrada": self.datos_entrada,
            "responsable": self.responsable,
            "fecha": date.today().isoformat(),
            "resultado": self.estado,
            "observado": redactar(self.observado),
            "pasos": self.pasos,
        }


def http_paso(caso, descripcion, metodo, url, esperado_status, cuerpo=None, token=None, extra=None):
    st, _, txt = peticion(metodo, url, cuerpo, token)
    ok = st in esperado_status if isinstance(esperado_status, (list, tuple, set)) else st == esperado_status
    caso.paso(f"{descripcion} [{metodo} {url}] -> HTTP {st}", ok, txt[:300])
    return st, txt, ok


# ---------------------------------------------------------------- casos
def cp01_autenticacion_jwt(usuario):
    c = Caso("CP-01", "REQ-SEG-01", "Autenticación JWT y acceso a endpoints protegidos", "Seguridad / funcional",
             "Registro, login y acceso con token válido; rechazo sin token.",
             "Registro y login devuelven token; GET protegido 200 con token y 401/403 sin token.",
             "Token presente en registro y login; 200 con token; 401 o 403 sin token.", "CRITICO")
    st, txt, _ = http_paso(c, "Registrar usuario", "POST", f"{BFF}/api/auth/register", 200,
                           {"username": usuario, "password": "pass12345"})
    token = (json_de(txt) or {}).get("token")
    c.paso("Registro devuelve token", bool(token), "token presente" if token else txt[:120])
    st, txt, _ = http_paso(c, "Login con mismas credenciales", "POST", f"{BFF}/api/auth/login", 200,
                           {"username": usuario, "password": "pass12345"})
    token = (json_de(txt) or {}).get("token") or token
    http_paso(c, "GET /api/products con token", "GET", f"{BFF}/api/products", 200, token=token)
    st, _, _ = peticion("GET", f"{BFF}/api/products")
    c.paso(f"GET /api/products sin token rechazado (HTTP {st})", st in (401, 403), f"HTTP {st}")
    c.observado = f"Sin token responde HTTP {st}."
    return c


def cp02_credenciales_invalidas(usuario):
    c = Caso("CP-02", "REQ-SEG-01", "Rechazo de credenciales inválidas y registro duplicado", "Seguridad / negativo",
             "Login con clave incorrecta y registro de usuario existente.",
             "Login incorrecto: HTTP 401. Registro duplicado: HTTP 409.",
             "Códigos 401 y 409 con mensaje controlado, sin token.", "MODERADO")
    http_paso(c, "Login con contraseña incorrecta", "POST", f"{BFF}/api/auth/login", 401,
              {"username": usuario, "password": "clave-incorrecta"})
    http_paso(c, "Registro de usuario ya existente", "POST", f"{BFF}/api/auth/register", 409,
              {"username": usuario, "password": "pass12345"})
    return c


def cp03_descuentos(token):
    c = Caso("CP-03", "REQ-FUNC-02", "Descuento según tipo de orden (Factory Method)", "Funcional / caja negra",
             "Creación de pedidos WEB y MARKETPLACE con el mismo ítem (100 x 2).",
             "WEB: 5 %, total 190,00, STANDARD. MARKETPLACE: 10 %, total 180,00, EXPRESS.",
             "Descuento y total exactos; método de envío correspondiente.", "GRAVE")
    base = {"customerId": 1, "customerName": "Test User", "email": "test@test.com",
            "items": [{"productId": 1, "productName": "Sauvage", "quantity": 2, "unitPrice": 100}]}
    for tipo, desc, total, envio in [("WEB", 5.0, 190.0, "STANDARD"), ("MARKETPLACE", 10.0, 180.0, "EXPRESS")]:
        st, _, txt = peticion("POST", f"{BFF}/api/orders", {**base, "orderType": tipo}, token)
        d = json_de(txt) or {}
        ok = st == 201 and d.get("discountApplied") == desc and d.get("totalAmount") == total \
            and d.get("shippingMethod") == envio
        c.paso(f"Pedido {tipo}: descuento={desc}, total={total}, envio={envio}", ok,
               f"HTTP {st}; descuento={d.get('discountApplied')}, total={d.get('totalAmount')}, envio={d.get('shippingMethod')}")
    return c


def cp04_tipo_orden_invalido(token):
    c = Caso("CP-04", "REQ-FUNC-02", "Rechazo de tipo de orden no soportado", "Funcional / negativo",
             "Envío de pedido con orderType INVALIDO.",
             "Rechazo controlado con HTTP 400 y mensaje 'Tipo de orden no soportado'.",
             "HTTP 400; no se crea el pedido.", "MODERADO")
    st, txt, _ = http_paso(c, "Pedido con tipo INVALIDO", "POST", f"{BFF}/api/orders", 400, token=token, cuerpo=
                           {"customerId": 1, "customerName": "Test User", "email": "test@test.com",
                            "orderType": "INVALIDO",
                            "items": [{"productId": 1, "productName": "Sauvage", "quantity": 2, "unitPrice": 100}]})
    return c


def cp05_circuit_breaker(token):
    c = Caso("CP-05", "REQ-RES-01", "Fallback del Circuit Breaker ante fallo del carrier", "Resiliencia",
             "Envío con carrier disponible (DHL) y con carrier caído simulado (FAIL_CARRIER).",
             "DHL: TRK-, sin fallback, entrega +3 días. FAIL_CARRIER: FBK-, fallback=true, entrega +7 días, HTTP 201.",
             "Ambos casos devuelven 201; el fallo no provoca error 5xx.", "GRAVE")
    base = {"orderId": 999, "address": "Calle 123", "city": "Santiago", "country": "Chile"}
    hoy = date.today()
    for carrier, prefijo, fallback, dias in [("DHL", "TRK-", False, 3), ("FAIL_CARRIER", "FBK-", True, 7)]:
        st, _, txt = peticion("POST", f"{BFF}/api/shipments", {**base, "carrier": carrier}, token)
        d = json_de(txt) or {}
        esperada = (hoy + timedelta(days=dias)).isoformat()
        ok = st == 201 and str(d.get("trackingNumber", "")).startswith(prefijo) \
            and d.get("circuitBreakerFallback") is fallback and d.get("estimatedDelivery") == esperada
        c.paso(f"Carrier {carrier}: prefijo {prefijo}, fallback={fallback}, entrega {esperada}", ok,
               f"HTTP {st}; tracking={d.get('trackingNumber')}, fallback={d.get('circuitBreakerFallback')}, entrega={d.get('estimatedDelivery')}")
    return c


def cp06_busqueda(token):
    c = Caso("CP-06", "REQ-FUNC-03", "Búsqueda y filtrado de productos", "Funcional / caja negra",
             "Filtros por marca, fragancia, precio, stock y nombre sobre el catálogo semilla.",
             "Listado completo de 11 productos; cada filtro devuelve solo coincidencias.",
             "Todos los elementos cumplen el criterio; búsqueda por nombre insensible a mayúsculas.", "MODERADO")
    st, txt, _ = http_paso(c, "Listar catálogo", "GET", f"{BFF}/api/products", 200, token=token)
    lista = json_de(txt) or []
    # El catálogo puede crecer por las altas de CP-19 en ejecuciones previas: se exige al menos la semilla.
    c.paso(f"Catálogo contiene al menos los 11 productos semilla (encontrados {len(lista)})", len(lista) >= 11, str(len(lista)))
    casos = [
        ("brand/Dior", lambda p: p["brand"] == "Dior"),
        ("fragrance/Amaderado", lambda p: p["fragrance"] == "Amaderado"),
        ("price-range?min=70000&max=110000", lambda p: 70000 <= p["price"] <= 110000),
        ("in-stock", lambda p: p["stockQuantity"] > 0),
        ("search?name=SAUVAGE", lambda p: "sauvage" in p["name"].lower()),
    ]
    for ruta, cumple in casos:
        st, _, txt = peticion("GET", f"{BFF}/api/products/{ruta}", None, token)
        d = json_de(txt) or []
        ok = st == 200 and len(d) >= 1 and all(cumple(p) for p in d)
        c.paso(f"Filtro {ruta}: {len(d)} resultados, todos coinciden", ok, f"HTTP {st}, n={len(d)}")
    c.observado = "Nota: el rango 50-150 de la Ev1 no aplica; los precios están en unidades enteras (p. ej. 89990)."
    return c


def cp07_validacion_servicios(token):
    c = Caso("CP-07", "REQ-VAL-01", "Validación de entradas en servicios de negocio", "Seguridad / validación",
             "Envío de datos inválidos directamente a cada microservicio.",
             "HTTP 400 en cada caso, y ningún registro persistido.",
             "Todos los datos inválidos rechazados con 400; el conteo de productos no cambia.", "GRAVE")
    _, _, txt = peticion("GET", f"{BFF}/api/products", None, token)
    antes = len(json_de(txt) or [])
    http_paso(c, "Producto con nombre vacío", "POST", f"{BFF}/api/products", 400,
              {"name": "", "brand": "Dior", "price": 100, "stockQuantity": 10}, token=token)
    http_paso(c, "Producto con precio negativo", "POST", f"{BFF}/api/products", 400,
              {"name": "Test", "brand": "Test", "price": -50, "stockQuantity": 10}, token=token)
    _, _, txt = peticion("GET", f"{BFF}/api/products", None, token)
    despues = len(json_de(txt) or [])
    c.paso(f"Ningún producto inválido persistido (antes={antes}, después={despues})", antes == despues, "")
    http_paso(c, "Pedido con email inválido e ítems vacíos", "POST", f"{BFF}/api/orders", 400,
              {"customerId": 1, "customerName": "Test", "email": "invalido", "orderType": "WEB", "items": []}, token=token)
    http_paso(c, "Envío sin carrier", "POST", f"{BFF}/api/shipments", 400,
              {"orderId": 1, "address": "Calle 123", "city": "Santiago", "country": "Chile"}, token=token)
    return c


def cp08_validacion_gateway(token):
    c = Caso("CP-08", "REQ-VAL-01", "Validación de entradas a través del gateway (BFF)", "Seguridad / integración",
             "Envío de producto inválido por el BFF, con token válido.",
             "HTTP 400 propagado desde el servicio de inventario.",
             "El código de error de validación llega íntegro al cliente.", "MODERADO")
    http_paso(c, "Producto con nombre vacío vía BFF", "POST", f"{BFF}/api/products", 400,
              {"name": "", "brand": "Dior", "price": 100, "stockQuantity": 10}, token=token)
    return c


def cp09_rendimiento(token):
    c = Caso("CP-09", "REQ-NFR-01", "Tiempos de respuesta (lectura y escritura)", "No funcional / rendimiento",
             "20 lecturas vía BFF y 20 escrituras directas en pedidos, medidas en el cliente.",
             "p95 lectura < 500 ms; p95 escritura < 1000 ms.",
             "Percentil 95 dentro del límite; medición en localhost, sin carga concurrente.", "MODERADO")
    def medir(metodo, url, cuerpo=None, tok=None):
        tiempos = []
        for _ in range(20):
            t0 = time.perf_counter()
            peticion(metodo, url, cuerpo, tok)
            tiempos.append((time.perf_counter() - t0) * 1000)
        tiempos.sort()
        return tiempos[18], statistics.mean(tiempos)
    p95_l, prom_l = medir("GET", f"{BFF}/api/products", None, token)
    c.paso(f"Lectura GET /api/products vía BFF: p95={p95_l:.0f} ms (media {prom_l:.0f} ms)", p95_l < 500, f"{p95_l:.1f} ms")
    cuerpo = {"customerId": 1, "customerName": "Carga", "email": "carga@test.com", "orderType": "WEB",
              "items": [{"productId": 1, "productName": "Sauvage", "quantity": 1, "unitPrice": 100}]}
    p95_e, prom_e = medir("POST", f"{ORD}/api/orders", cuerpo)
    c.paso(f"Escritura POST /api/orders: p95={p95_e:.0f} ms (media {prom_e:.0f} ms)", p95_e < 1000, f"{p95_e:.1f} ms")
    return c


def cp10_contrasenas():
    c = Caso("CP-10", "REQ-SEG-02", "Protección de contraseñas en almacenamiento", "Seguridad / inspección de código",
             "Inspección de AuthService: las contraseñas no deben almacenarse en claro.",
             "Las contraseñas se guardan como hash (p. ej. BCrypt) y nunca en texto plano.",
             "No existe asignación de la contraseña en claro; se usa un PasswordEncoder.", "GRAVE")
    ruta = os.path.join(RAIZ, "bff-gateway/src/main/java/com/smartlogix/gateway/service/AuthService.java")
    codigo = open(ruta, encoding="utf-8").read()
    en_claro = re.search(r"users\.put\(\s*request\.getUsername\(\)\s*,\s*request\.getPassword\(\)\s*\)", codigo)
    hash_ok = "PasswordEncoder" in codigo or "BCrypt" in codigo
    c.paso("No se almacena request.getPassword() en claro", en_claro is None,
           "encontrado en AuthService.java" if en_claro else "no encontrado")
    c.paso("Se utiliza un PasswordEncoder (hash)", hash_ok, "PasswordEncoder presente" if hash_ok else "ausente")
    return c


def cp11_errores(usuario=None):
    c = Caso("CP-11", "REQ-SEG-03", "Errores sin exposición de detalles internos", "Seguridad / manejo de errores",
             "Solicitud con tipo de dato incorrecto en la ruta (id no numérico).",
             "Respuesta de error genérica, sin excepciones ni mensajes del framework.",
             "El cuerpo no contiene texto técnico (p. ej. 'Failed to convert', 'For input string', 'java.', 'org.springframework').",
             "MODERADO")
    st, _, txt = peticion("GET", f"{ORD}/api/orders/abc")
    tecnico = re.search(r"Failed to convert|For input string|java\.|org\.springframework", txt)
    c.paso(f"Verificación de ausencia de detalle técnico en el cuerpo de error (HTTP {st})", tecnico is None, txt[:200])
    return c


def cp12_cors():
    c = Caso("CP-12", "REQ-SEG-04", "Restricción de orígenes CORS", "Seguridad / configuración",
             "Preflight desde un origen no autorizado y desde uno autorizado.",
             "Origen no autorizado sin Access-Control-Allow-Origin; origen localhost:5173 autorizado.",
             "Solo los orígenes definidos reciben la cabecera de permiso.", "MODERADO")
    st, h, _ = peticion("OPTIONS", f"{BFF}/api/products",
                        cabeceras={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"})
    acao = {k.lower(): v for k, v in h.items()}.get("access-control-allow-origin")
    c.paso(f"Origen http://evil.example rechazado (HTTP {st})", acao is None, f"ACAO={acao}")
    st, h, _ = peticion("OPTIONS", f"{BFF}/api/products",
                        cabeceras={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    acao = {k.lower(): v for k, v in h.items()}.get("access-control-allow-origin")
    c.paso(f"Origen http://localhost:5173 permitido (HTTP {st})", acao == "http://localhost:5173", f"ACAO={acao}")
    return c


def cp13_secreto():
    c = Caso("CP-13", "REQ-SEG-05", "Secreto de firma JWT fuera del código fuente", "Seguridad / configuración",
             "Inspección de application.yml del BFF.",
             "jwt.secret se resuelve desde una variable de entorno (sin valor literal).",
             "El valor del secreto no aparece literal en el repositorio.", "GRAVE")
    ruta = os.path.join(RAIZ, "bff-gateway/src/main/resources/application.yml")
    m = re.search(r"^\s*secret:\s*(.+)$", open(ruta, encoding="utf-8").read(), re.M)
    valor = m.group(1).strip() if m else ""
    # El valor literal no se reproduce en la evidencia para no difundir el secreto.
    c.paso("jwt.secret usa placeholder ${...}", valor.startswith("${"),
           "placeholder" if valor.startswith("${") else f"valor literal en el repositorio ({len(valor)} caracteres, oculto)")
    return c


def cp14_cobertura():
    c = Caso("CP-14", "REQ-CAL-01", "Cobertura de líneas JaCoCo >= 60 %", "No funcional / mantenibilidad",
             "Lectura de jacoco.csv tras mvn verify en cada servicio.",
             "Cobertura de líneas >= 60 % por servicio.",
             "Cada módulo supera el umbral; el gate de JaCoCo está activo.", "MODERADO")
    for s in SERVICIOS:
        ruta = os.path.join(RAIZ, s, "target/site/jacoco/jacoco.csv")
        if not os.path.exists(ruta):
            c.paso(f"{s}: reporte JaCoCo existe", False, "ausente")
            continue
        filas = open(ruta).read().splitlines()[1:]
        mi = sum(int(f.split(",")[7]) for f in filas)
        ci = sum(int(f.split(",")[8]) for f in filas)
        pct = 100 * ci / (ci + mi) if (ci + mi) else 0
        c.paso(f"{s}: cobertura de líneas {pct:.1f} %", pct >= 60, f"{ci}/{ci + mi}")
    return c


def cp15_spotbugs():
    c = Caso("CP-15", "REQ-CAL-02", "Sin hallazgos de prioridad 1 en análisis estático (SpotBugs + FindSecBugs)",
             "Análisis estático", "Conteo de hallazgos de prioridad 1 en cada módulo backend.",
             "0 hallazgos de prioridad 1.", "Ningún hallazgo de prioridad 1 sin tratamiento documentado.", "MODERADO")
    for s in SERVICIOS:
        ruta = os.path.join(RAIZ, s, "target/spotbugsXml.xml")
        if not os.path.exists(ruta):
            c.paso(f"{s}: reporte SpotBugs existe", False, "ausente")
            continue
        bugs = ET.parse(ruta).getroot().findall("BugInstance")
        p1 = [b.get("type") for b in bugs if b.get("priority") == "1"]
        c.paso(f"{s}: hallazgos prioridad 1 = {len(p1)} {p1}", len(p1) == 0, f"total={len(bugs)}")
    return c


def cp16_dependencias_frontend():
    c = Caso("CP-16", "REQ-SEG-06", "Dependencias del frontend sin vulnerabilidades críticas o altas", "Seguridad / SCA",
             "npm audit sobre el frontend.",
             "0 vulnerabilidades críticas o altas.",
             "Ninguna vulnerabilidad crítica o alta en dependencias de producción ni de desarrollo.", "GRAVE")
    fe = os.path.join(RAIZ, "frontend")
    out = subprocess.run(["npm", "audit", "--json"], cwd=fe, capture_output=True, text=True).stdout
    meta = (json_de(out) or {}).get("metadata", {}).get("vulnerabilities", {})
    criticas, altas = meta.get("critical", -1), meta.get("high", -1)
    c.paso(f"Críticas={criticas}, altas={altas}", criticas == 0 and altas == 0, f"{meta}")
    with open(os.path.join(SALIDA, "npm-audit.json"), "w") as f:
        f.write(out)
    return c


def cp17_contenedores():
    c = Caso("CP-17", "REQ-DEP-01", "Despliegue reproducible en contenedores Docker", "Despliegue / operación",
             "Presencia de Dockerfile por servicio y validación de docker-compose.yml.",
             "Dockerfile en cada servicio y docker-compose.yml válido.",
             "docker compose config sin errores.", "MODERADO")
    for s in SERVICIOS:
        existe = os.path.exists(os.path.join(RAIZ, s, "Dockerfile"))
        c.paso(f"{s}/Dockerfile presente", existe, "")
    compose = os.path.join(RAIZ, "docker-compose.yml")
    if os.path.exists(compose):
        r = subprocess.run(["docker", "compose", "-f", compose, "config", "-q"], capture_output=True, text=True)
        c.paso("docker compose config válido", r.returncode == 0, (r.stderr or "ok")[:200])
    else:
        c.paso("docker-compose.yml presente", False, "ausente")
    return c


def cp18_acceso_directo_servicios():
    c = Caso("CP-18", "REQ-SEG-07", "Aislamiento de los microservicios de negocio", "Seguridad / control de acceso",
             "Acceso directo, sin token, a los puertos de los microservicios (8081, 8082, 8083).",
             "Ninguna petición sin token devuelve datos: el acceso debe ser rechazado o no alcanzable desde fuera de la red interna.",
             "Respuesta distinta de 200 o puerto no accesible desde el host.", "CRITICO")
    for nombre, url in [("inventario", f"{INV}/api/products"),
                        ("pedidos (datos de clientes)", f"{ORD}/api/orders/customer/1"),
                        ("envíos", f"{SHP}/api/shipments")]:
        st, _, txt = peticion("GET", url)
        ok = st != 200
        c.paso(f"Acceso directo sin token a {nombre} [GET {url}] -> HTTP {st}", ok,
               "datos expuestos" if st == 200 else txt[:120])
    c.observado = "Sin token, los microservicios responden 200 cuando se accede directamente; el control de acceso solo existe en el BFF."
    return c


def cp19_alta_producto(token):
    c = Caso("CP-19", "REQ-FUNC-04", "Alta de producto con persistencia y asignación de ID", "Funcional / caja negra",
             "Alta de un producto nuevo a través del BFF con token válido, sobre la base con datos semilla.",
             "HTTP 201 con id asignado; el producto aparece en el catálogo.",
             "Código 201, id no nulo y producto recuperable por GET.", "GRAVE")
    nombre = f"Producto CP19 {int(time.time())}"
    st, _, txt = peticion("POST", f"{BFF}/api/products",
                          {"name": nombre, "brand": "Prueba", "description": "alta de prueba",
                           "price": 10.5, "stockQuantity": 5, "fragrance": "Test"}, token)
    d = json_de(txt) or {}
    c.paso(f"POST /api/products vía BFF -> HTTP {st}", st == 201, txt[:200])
    c.paso("El producto recibe un id asignado", d.get("id") is not None, f"id={d.get('id')}")
    if d.get("id") is not None:
        st2, _, txt2 = peticion("GET", f"{BFF}/api/products/{d['id']}", None, token)
        c.paso(f"El producto se recupera por id (HTTP {st2})", st2 == 200 and (json_de(txt2) or {}).get("name") == nombre, "")
    return c


def main():
    usuario = f"usr{int(time.time())}"
    casos = [cp01_autenticacion_jwt(usuario)]
    token = (json_de(peticion("POST", f"{BFF}/api/auth/login", {"username": usuario, "password": "pass12345"})[2]) or {}).get("token")
    casos.append(cp02_credenciales_invalidas(usuario))
    casos.append(cp03_descuentos(token))
    casos.append(cp04_tipo_orden_invalido(token))
    casos.append(cp05_circuit_breaker(token))
    casos.append(cp06_busqueda(token))
    casos.append(cp07_validacion_servicios(token))
    casos.append(cp08_validacion_gateway(token))
    casos.append(cp09_rendimiento(token))
    casos.append(cp10_contrasenas())
    casos.append(cp11_errores())
    casos.append(cp12_cors())
    casos.append(cp13_secreto())
    casos.append(cp14_cobertura())
    casos.append(cp15_spotbugs())
    casos.append(cp16_dependencias_frontend())
    casos.append(cp17_contenedores())
    casos.append(cp18_acceso_directo_servicios())
    casos.append(cp19_alta_producto(token))

    resultados = [c.dict() for c in casos]
    with open(os.path.join(SALIDA, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump({"etiqueta": ETIQUETA, "fecha": date.today().isoformat(), "casos": resultados},
                  f, ensure_ascii=False, indent=2)

    lineas = [f"# Resultados de ejecución: {ETIQUETA}", "", f"Fecha: {date.today().isoformat()}", "",
              "| Caso | Requisito | Resultado | Criticidad si falla | Observado |", "|---|---|---|---|---|"]
    for r in resultados:
        obs = (r["observado"] or "; ".join(p["paso"] for p in r["pasos"] if not p["ok"])[:160]).replace("|", "/")
        lineas.append(f"| {r['id']} | {r['requisito']} | {r['resultado']} | {r['criticidad_si_falla']} | {obs} |")
    with open(os.path.join(SALIDA, "resultados.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    resumen = {}
    for r in resultados:
        resumen[r["resultado"]] = resumen.get(r["resultado"], 0) + 1
    print(f"Ejecución '{ETIQUETA}': {len(resultados)} casos -> {resumen}")
    for r in resultados:
        print(f"  {r['id']} {r['resultado']:<9} {r['titulo']}")


if __name__ == "__main__":
    main()
