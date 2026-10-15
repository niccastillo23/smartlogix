#!/usr/bin/env python3
"""
Genera el informe del Encargo 3 (ISY1102) en Word, a partir de las evidencias del repositorio.
Las cifras se leen de los artefactos (ZAP, SonarQube, SpotBugs, JaCoCo, npm audit, Playwright y
docs/evidencias). Reutiliza el formato del informe del Encargo 2 (generar_informe.py).

Uso: python3 docs/informe/generar_informe_encargo3.py
"""
import csv
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm

sys.path.insert(0, os.path.dirname(__file__))
import generar_informe as base  # noqa: E402  (formato y funciones comunes)
from generar_informe import (estilos, fuente, figura, nueva_seccion, parrafo, pie_pagina,  # noqa: E402
                             sin_partir_filas, tabla, titulo, vinetas)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVID = os.path.join(RAIZ, "docs", "evidencias")
E3 = os.path.join(EVID, "encargo3")
SALIDA = os.path.join(RAIZ, "docs", "informe", "Informe_Encargo3_ISY1102_SmartLogix.docx")
SERVICIOS = ["inventory-service", "order-service", "shipping-service", "bff-gateway"]
FECHA_TXT = "14 de octubre de 2026"


def jload(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def casos(etiqueta):
    return {c["id"]: c for c in jload(os.path.join(EVID, etiqueta, "resultados.json"))["casos"]}


MAIN = casos("main-encargo2-stack")      # línea base: stack del Encargo 2 (commit a602ee5)
FIN = casos("v2-final")                   # versión final (rama v2)


def zap_resumen(ruta):
    d = jload(ruta)
    c = {"High": 0, "Medium": 0, "Low": 0, "Informational": 0}
    tipos = {"High": set(), "Medium": set(), "Low": set(), "Informational": set()}
    for s in d.get("site", []):
        for a in s.get("alerts", []):
            r = a["riskdesc"].split(" ")[0]
            c[r] = c.get(r, 0) + len(a.get("instances", []))
            tipos.setdefault(r, set()).add(a["name"])
    return c, tipos


def spotbugs(ruta_xml):
    if not os.path.exists(ruta_xml):
        return None
    b = ET.parse(ruta_xml).getroot().findall("BugInstance")
    return len(b), sum(1 for x in b if x.get("priority") == "1")


def jacoco(ruta_csv):
    if not os.path.exists(ruta_csv):
        return None
    filas = list(csv.DictReader(open(ruta_csv)))
    mi = sum(int(x["LINE_MISSED"]) for x in filas)
    ci = sum(int(x["LINE_COVERED"]) for x in filas)
    return round(100 * ci / (ci + mi), 1), ci + mi


def surefire_total():
    per, tot = {}, 0
    for s in SERVICIOS:
        n = 0
        for f in glob.glob(os.path.join(RAIZ, s, "target", "surefire-reports", "*.txt")):
            m = re.search(r"Tests run: (\d+)", open(f).read())
            n += int(m.group(1)) if m else 0
        per[s] = n
        tot += n
    return per, tot


def npm(ruta):
    d = jload(ruta)
    return d["metadata"]["vulnerabilities"]


def playwright_tests():
    d = jload(os.path.join(E3, "playwright-resultados-v2.json"))
    out = []

    def walk(s):
        for sp in s.get("specs", []):
            for t in sp.get("tests", []):
                r = t["results"][-1]
                out.append((sp["title"], r["status"], r["duration"] / 1000))
        for c in s.get("suites", []):
            walk(c)
    for s in d["suites"]:
        walk(s)
    return out, d.get("stats", {})


# ---------------------------------------------------------------- datos
ZAP_FM, ZAP_FM_T = zap_resumen(os.path.join(E3, "zap-frontend-main.json"))
ZAP_FV, ZAP_FV_T = zap_resumen(os.path.join(E3, "zap-frontend-v2.json"))
ZAP_AM, ZAP_AM_T = zap_resumen(os.path.join(E3, "zap-api-main.json"))
ZAP_AV, ZAP_AV_T = zap_resumen(os.path.join(E3, "zap-api-v2.json"))
SB = {s: spotbugs(os.path.join(E3, f"spotbugs-{s}.xml")) for s in SERVICIOS}
JC = {s: jacoco(os.path.join(E3, f"jacoco-{s}.csv")) for s in SERVICIOS}
PR_PER, PR_TOT = surefire_total()
NPM_PROD = npm(os.path.join(E3, "npm-audit-produccion.json"))
NPM_FULL = npm(os.path.join(E3, "npm-audit-completo.json"))
SONAR_B = {m["metric"]: m.get("value") for m in jload(os.path.join(E3, "sonar-smartlogix-backend.json"))["component"]["measures"]}
SONAR_F = {m["metric"]: m.get("value") for m in jload(os.path.join(E3, "sonar-smartlogix-frontend.json"))["component"]["measures"]}
SONAR_GATE_B = jload(os.path.join(E3, "sonar-gate-smartlogix-backend.json"))["projectStatus"]
SONAR_GATE_F = jload(os.path.join(E3, "sonar-gate-smartlogix-frontend.json"))["projectStatus"]
SONAR_ACEPT = jload(os.path.join(E3, "sonar-issues-aceptados.json")).get("total", 0)
SONAR_ABIERTOS = jload(os.path.join(E3, "sonar-issues-abiertos.json")).get("total", 0)
PW_TESTS, PW_STATS = playwright_tests()


def pasa(c):
    return "PASA" if c["resultado"] == "PASA" else "FALLA"


# ---------------------------------------------------------------- incidentes (Encargo 3)
# (ID, caso/origen, requisito, descripción, ubicación, criticidad, estado, tratamiento y evidencia)
INC = [
    ("INC-01", "CP-10", "REQ-SEG-02", "Contraseñas almacenadas en texto plano y comparadas por igualdad.",
     "bff-gateway AuthService (base: líneas 17, 24, 39)", "CRÍTICO", "CERRADO",
     "Hash BCrypt. Prueba: AuthServiceTest.register_shouldStoreBcryptHashNotPlaintext; CP-10."),
    ("INC-02", "CP-13", "REQ-SEG-05", "Secreto de firma JWT literal en application.yml, presente en el historial de git.",
     "bff-gateway application.yml (base: línea 17); historial anterior a 2d7685f", "CRÍTICO", "CERRADO EN CÓDIGO; ROTACIÓN PENDIENTE",
     "Secreto desde ${JWT_SECRET}. Debe rotarse: el valor del historial se considera expuesto."),
    ("INC-15", "CP-20", "REQ-SEG-07", "Los microservicios respondían sin token a cualquier petición de la red interna.",
     "inventory, order y shipping: sin Spring Security; puertos publicados (base)", "CRÍTICO", "CERRADO",
     "JwtAuthFilter y SecurityConfig en cada servicio; SecurityIntegrationTest (3 pruebas por servicio); CP-20 (401 desde la red interna)."),
    ("INC-22", "Revisión DAST", "REQ-FUNC-05", "El valor de status se concatenaba en la URL: '&', '#' o llaves alteraban la petición al microservicio.",
     "bff-gateway OrderProxyService y ShippingProxyService (base)", "GRAVE", "CERRADO",
     "Construcción de URI codificada. StatusUrlEncodingTest (2 pruebas) y PATCH de prueba con 'SHIPPED&admin=true' (200, sin parámetros inyectados)."),
    ("INC-16", "CP-19", "REQ-FUNC-04", "Alta de productos con HTTP 500: la secuencia de IDs no avanzaba tras la semilla.",
     "inventory-service data.sql (base)", "GRAVE", "CERRADO",
     "ALTER TABLE ... RESTART WITH. ProductSeedIdIntegrationTest (falla sin la corrección); CP-19."),
    ("INC-19", "API-04 / CP-22", "REQ-FUNC-05", "PATCH a través del BFF respondía 503: RestTemplate con HttpURLConnection no admite PATCH.",
     "bff-gateway RestTemplateConfig (base)", "GRAVE", "CERRADO",
     "JdkClientHttpRequestFactory. API-04 y CP-22 pasan."),
    ("INC-13", "CP-21", "REQ-SEG-09", "Sin límite de intentos de login: fuerza bruta sin freno.",
     "bff-gateway AuthService/AuthController (base)", "MODERADO", "CERRADO",
     "Bloqueo de 15 min tras 5 fallos por usuario (HTTP 429). CP-21; AuthServiceTest (2 pruebas nuevas)."),
    ("INC-18", "UI-03", "REQ-SEG-01", "El login con credenciales incorrectas recargaba la página y no mostraba el error.",
     "frontend api.js (interceptor 401 sin excepción para /auth/)", "MODERADO", "CERRADO",
     "Excepción para /auth/*. UI-03 pasa: se muestra 'Credenciales inválidas' y se conserva el usuario."),
    ("INC-20", "API-05 / CP-23", "REQ-VAL-02", "Parámetro obligatorio ausente devolvía HTTP 500.",
     "GlobalExceptionHandler de los cuatro módulos (base)", "MODERADO", "CERRADO",
     "MissingServletRequestParameterException mapeada a 400. API-05 y CP-23."),
    ("INC-21", "DAST frontend", "REQ-SEG-10", "Sin Content-Security-Policy ni cabeceras de aislamiento; versión del servidor expuesta.",
     "frontend/nginx.conf (base)", "MODERADO", "MITIGADO (residual)",
     "CSP, COOP, CORP, Permissions-Policy y server_tokens off. Residual: 'unsafe-inline' en estilos (componentes con estilos en línea)."),
    ("INC-08", "CP-15", "REQ-CAL-02", "SpotBugs prioridad 1: SPRING_CSRF_PROTECTION_DISABLED en la configuración de seguridad.",
     "SecurityConfig de los cuatro módulos", "MODERADO", "RIESGO ACEPTADO",
     f"API stateless con Bearer, sin cookies. Exclusión documentada en cada módulo y {SONAR_ACEPT} issues S4502 aceptados en SonarQube con justificación."),
    ("INC-09", "CP-16", "REQ-SEG-06", "Vulnerabilidades en dependencias de desarrollo del frontend (vitest, vite, tailwind).",
     "frontend/package.json (devDependencies)", "GRAVE", "ABIERTO (residual)",
     f"Producción sin high ni critical (npm audit --omit=dev). Quedan {NPM_FULL['critical']} críticas y {NPM_FULL['high']} altas en build/test; corregir exige saltos mayores."),
    ("INC-24", "SonarQube", "REQ-CAL-03", "Duplicación de código entre microservicios (SecurityConfig, JwtAuthFilter, manejador de errores y pruebas): el quality gate falla con 29,7 % de duplicación en código nuevo.",
     "inventory, order, shipping y bff-gateway", "MODERADO", "ABIERTO",
     "Extraer un módulo común (librería de seguridad y errores). Ver propuesta SEG-03."),
    ("INC-12", "Revisión de código", "REQ-SEG-01", "El token JWT se guarda en localStorage, accesible desde scripts de la página.",
     "frontend/src/context/AuthContext.jsx", "MODERADO", "ABIERTO",
     "Cookie HttpOnly con SameSite y protección CSRF reactivada. Ver propuesta SEG-02."),
    ("INC-14", "Revisión visual", "REQ-CAL-01", "La pantalla de inicio se presenta como 'PERFUMERÍA' y el título HTML como 'SmartLogix'.",
     "frontend (captura UI-01 a UI-05)", "LEVE", "ABIERTO",
     "Unificar el nombre comercial."),
    ("INC-03", "CP-11", "REQ-SEG-03", "Excepciones de conversión devolvían 404 con el mensaje interno del framework.",
     "GlobalExceptionHandler (base)", "MODERADO", "CERRADO", "Respuesta genérica sin detalle técnico. CP-11."),
    ("INC-04", "CP-02", "REQ-SEG-01", "Credenciales inválidas y registro duplicado respondían 403.",
     "bff-gateway (base)", "MODERADO", "CERRADO", "401 y 409. CP-02."),
    ("INC-05", "CP-04", "REQ-FUNC-02", "Tipo de orden no soportado respondía 404.",
     "order-service OrderService (base)", "MODERADO", "CERRADO", "400 con mensaje controlado. CP-04."),
    ("INC-07", "CP-14", "REQ-CAL-01", "El gate de JaCoCo no se ejecutaba: el argLine de Surefire sustituía al agente.",
     "pom.xml de los cuatro módulos (base)", "MODERADO", "CERRADO", "argLine = @{argLine}. CP-14 con cobertura medida por módulo."),
    ("INC-23", "Revisión de código", "REQ-SEG-03", "Los logs del BFF registraban el mensaje de excepción (riesgo de inyección CRLF en logs).",
     "bff-gateway GlobalExceptionHandler (base)", "LEVE", "CERRADO", "Se registra solo el código HTTP o un texto constante. SpotBugs CRLF: 0."),
    ("INC-25", "SonarQube", "REQ-CAL-03", "Frontend: 2 bugs (promesas sin manejo de error) y 2 code smells (regex super-lineal, isNaN).",
     "OrderStatus.jsx, ProductCatalog.jsx, formatPrice.js", "LEVE", "CERRADO", "Manejo de error en las promesas y expresión sin regex. SonarQube frontend: 0 bugs y 0 smells."),
    ("INC-06", "CP-08", "REQ-VAL-01", "Un error 400 de validación llegaba al cliente como 403 a través del BFF.",
     "bff-gateway (base; causa probable)", "MODERADO", "CERRADO", "Propagación de errores 4xx del servicio de destino. CP-08."),
    ("INC-10", "CP-17", "REQ-DEP-01", "Sin Dockerfile ni docker-compose.yml.",
     "Raíz del repositorio (base)", "MODERADO", "CERRADO", "Imágenes multi-etapa y Compose con JWT_SECRET obligatorio. CP-17."),
    ("INC-11", "Revisión documental", "REQ-CAL-01", "Cifras de cobertura de la Ev1 no reproducibles.",
     "Informe de la Ev1", "MODERADO", "CERRADO", "Cifras medidas y corregidas en el informe del Encargo 2."),
]

# Mapa de regresión: defecto -> pruebas que lo detectan en main y que lo verifican en v2
REGRESION = [
    ("INC-13", "CP-21; AuthServiceTest (bloqueo y reseteo)", "Falla sin bloqueo", "Pasa"),
    ("INC-15", "CP-20; SecurityIntegrationTest x3", "CP-20 falla (200 sin token)", "Pasa"),
    ("INC-18", "UI-03 (Playwright)", "Falla: el error no aparece", "Pasa"),
    ("INC-19", "API-04; CP-22", "503 en PATCH", "Pasa"),
    ("INC-20", "API-05; CP-23", "500 con parámetro ausente", "Pasa"),
    ("INC-22", "StatusUrlEncodingTest x2", "No ejecutada sobre main; el código de main concatena el valor (verificado por lectura del código)", "Pasa"),
    ("INC-16", "CP-19; ProductSeedIdIntegrationTest", "Falla: HTTP 500 en el alta", "Pasa"),
    ("INC-21", "ZAP baseline frontend (DAST)", "Medio: 3 alertas", "Medio: 1 alerta (residual)"),
]


# ---------------------------------------------------------------- portada e índice
def portada(doc):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fuente(p.add_run("Informe de seguridad y calidad\nen el desarrollo de software"), tam=20, negrita=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fuente(p.add_run("Encargo 3: pruebas de seguridad, automatización y mejora continua\nCaso SmartLogix"), tam=12)
    for _ in range(4):
        doc.add_paragraph()
    for k, v in [("Asignatura: ", "ISY1102 - Seguridad y calidad en el desarrollo de software"),
                 ("Evaluación: ", "Encargo 3 (tercera etapa del caso semestral)"),
                 ("Carrera: ", "[completar]"),
                 ("Sección: ", "004V"),
                 ("Docente: ", "Manuel Reyes Ferrada"),
                 ("Fecha: ", FECHA_TXT)]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        fuente(p.add_run(k), negrita=True)
        fuente(p.add_run(v))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fuente(p.add_run("Integrantes"), negrita=True)
    for n in ["Nicolás Castillo", "Benjamín Catalán", "Benjamín Quiroz"]:
        q = doc.add_paragraph()
        q.alignment = WD_ALIGN_PARAGRAPH.LEFT
        fuente(q.add_run(n))
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def indice(doc):
    p = doc.add_paragraph()
    fuente(p.add_run("Índice"), tam=12, negrita=True)
    p = doc.add_paragraph()
    run = p.add_run()
    fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "begin"); run._r.append(fc)
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = 'TOC \\o "1-2" \\h \\z \\u'; run._r.append(it)
    fc2 = OxmlElement("w:fldChar"); fc2.set(qn("w:fldCharType"), "separate"); run._r.append(fc2)
    fuente(p.add_run("Índice generado por Word (clic derecho y 'Actualizar campos')."), cursiva=True, tam=10)
    fc3 = OxmlElement("w:fldChar"); fc3.set(qn("w:fldCharType"), "end"); run._r.append(fc3)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def bloque_figuras(doc, pares, columnas=2, ancho=8.2):
    """Figuras en tabla de dos columnas (imagen + leyenda), con filas que no se parten entre páginas."""
    for i in range(0, len(pares), columnas):
        tbl = doc.add_table(rows=2, cols=columnas)
        tbl.alignment = 1
        for k, (ruta, leyenda) in enumerate(pares[i:i + columnas]):
            cel = tbl.rows[0].cells[k]
            cel.text = ""
            pp = cel.paragraphs[0]
            pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if os.path.exists(ruta):
                pp.add_run().add_picture(ruta, width=Cm(ancho))
            cap = tbl.rows[1].cells[k]
            cap.text = ""
            cp = cap.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fuente(cp.add_run(leyenda), tam=9, cursiva=True)
        sin_partir_filas(tbl)
        doc.add_paragraph().paragraph_format.line_spacing = 1.0


# ---------------------------------------------------------------- secciones
def seccion_introduccion(doc):
    titulo(doc, "1. Introducción")
    titulo(doc, "1.1 Contexto y objetivo del encargo", 2)
    parrafo(doc, "SmartLogix es un eCommerce de perfumes con arquitectura de microservicios: un frontend en React 18, un BFF "
            "(gateway) con JWT y tres microservicios en Spring Boot 3.2 y Java 21 (inventario, pedidos y envíos). El Encargo 3 es la "
            "última etapa del caso: valida el sistema de forma global, ejecuta pruebas de seguridad, automatiza las pruebas "
            "funcionales y no funcionales, y establece cómo preservar la calidad, la seguridad y el cumplimiento normativo en "
            "futuras versiones.")
    parrafo(doc, "El objetivo es comprobar, con evidencia reproducible, qué mejora el trabajo de las etapas anteriores y qué "
            "queda pendiente. Para ello se compara la versión de referencia (rama main, stack del Encargo 2) con la versión final "
            "(rama v2), con el mismo ejecutor y las mismas herramientas.")
    titulo(doc, "1.2 Alcance y estructura", 2)
    parrafo(doc, "Incluye el BFF, los tres microservicios, el frontend, el despliegue en Docker y el pipeline de integración "
            "continua. Quedan fuera la infraestructura de nube, la carga concurrente a escala y las pruebas en dispositivos móviles. "
            "El informe contiene: ajustes a los encargos previos (sección 1.3), enfoques de seguridad (sección 3), controles "
            "automatizados (sección 4), resultados de seguridad (sección 5), resultados de automatización (sección 6), incidentes y "
            "propuestas de mitigación (sección 7), plan de mantenimiento (sección 8), análisis ético y normativo (sección 9) y "
            "conclusiones (sección 10).")
    titulo(doc, "1.3 Ajustes a los encargos previos", 2)
    parrafo(doc, "La revisión técnica de los encargos anteriores (Encargo 1 y Encargo 2) permitió detectar afirmaciones que el código "
            "no respaldaba. La siguiente tabla resume cada una y el ajuste aplicado. No se recibió retroalimentación escrita del "
            "docente sobre esas entregas; los ajustes se basan en la verificación contra el código y la ejecución.")
    tabla(doc, ["Afirmación en el encargo previo", "Verificación con el código o la ejecución", "Ajuste en este encargo"], [
        ["Cobertura de 87,4 % (backend) y 84,1 % (frontend)",
         "El gate de JaCoCo estaba inactivo y el frontend mide 68,5 % de statements.",
         "Gate corregido (INC-07). La cobertura de cada módulo se mide en la sección 6.1, sobre la versión final."],
        ["Errores devueltos con 404 o 500 sin detalles",
         "Todos los errores de negocio respondían 404 y enviaban el mensaje de la excepción.",
         "Respuestas 400/404/409/429 controladas y sin mensajes internos (INC-03, INC-05, INC-20)."],
        ["Sin token, HTTP 401", "La respuesta real era 403 en la base.", "401 con mensaje JSON (INC-04)."],
        ["Contraseñas 'protegidas' (ver Encargo 2)", "Se guardaban en texto plano.", "BCrypt (INC-01)."],
        ["Microservicios protegidos por el BFF", "Eran accesibles directamente desde la red.", "Validación de JWT en cada servicio (INC-15)."],
        ["Búsqueda de productos disponible",
         "El BFF no exponía los filtros de inventario.", "Endpoints añadidos (INC-17)."],
        ["Ley 19.628 como marco vigente",
         "La Ley 21.719 la reforma; BCN indica vigencia el 1-dic-2026, con una propuesta de postergación a 1-dic-2027.",
         "Se analiza la ley reformada y se marca como pendiente la confirmación de la fecha (sección 9)."],
    ], anchos=[4.6, 6.3, 5.9], tam=9)


def seccion_criterios(doc):
    titulo(doc, "2. Criterios de calidad, seguridad y cumplimiento")
    parrafo(doc, "Los criterios son los del Encargo 2, ampliados con los requisitos de seguridad y automatización que surgieron del "
            "análisis. Cada requisito tiene un código, un origen declarado y al menos un caso de prueba. El conjunto no es un ERS "
            "oficial, y así se declara.")
    tabla(doc, ["Código", "Requisito", "Origen", "Caso o prueba que lo verifica"], [
        ["REQ-SEG-01", "Autenticación JWT; rechazo de accesos sin token o con credenciales inválidas.", "Encargo 2", "CP-01, CP-02, API-01, API-06"],
        ["REQ-SEG-02", "Contraseñas almacenadas como hash.", "Encargo 2 (§2.2)", "CP-10; AuthServiceTest"],
        ["REQ-SEG-03", "Errores sin detalles internos.", "Encargo 2 (§2.2)", "CP-11"],
        ["REQ-SEG-04", "CORS restringido a los orígenes definidos.", "Encargo 2 (§2.2)", "CP-12"],
        ["REQ-SEG-05", "Secreto JWT fuera del código.", "Hallazgo", "CP-13"],
        ["REQ-SEG-06", "Dependencias del frontend sin critical o high en producción.", "Análisis SCA", "CP-16 (completo); npm audit --omit=dev"],
        ["REQ-SEG-07", "Microservicios accesibles solo con token firmado.", "Hallazgo (INC-15)", "CP-18, CP-20; SecurityIntegrationTest"],
        ["REQ-SEG-09", "Bloqueo tras intentos fallidos de login.", "Hallazgo (INC-13)", "CP-21; AuthServiceTest"],
        ["REQ-SEG-10", "Cabeceras de seguridad (CSP y aislamiento).", "DAST (INC-21)", "ZAP baseline; cabeceras de nginx"],
        ["REQ-FUNC-02", "Descuento WEB 5 %, MARKETPLACE 10 %; tipo inválido rechazado.", "Encargo 2", "CP-03, CP-04, API-03"],
        ["REQ-FUNC-03", "Búsqueda por marca, fragancia, precio, stock y nombre.", "Encargo 2", "CP-06"],
        ["REQ-FUNC-04", "Alta de producto con identificador.", "Ev1 §3.2", "CP-19; ProductSeedIdIntegrationTest"],
        ["REQ-FUNC-05", "Actualización de estado a través del BFF, sin inyección en la URL.", "Hallazgo (INC-19, INC-22)", "API-04, CP-22; StatusUrlEncodingTest"],
        ["REQ-RES-01", "Fallback del Circuit Breaker ante fallo del carrier.", "Encargo 2", "CP-05"],
        ["REQ-VAL-01 / 02", "Validación de entradas; parámetro obligatorio ausente = 400.", "Encargo 2 / hallazgo (INC-20)", "CP-07, CP-08, API-05, CP-23"],
        ["REQ-NFR-01", "Lectura p95 < 500 ms; escritura p95 < 1000 ms.", "Encargo 2 (§2.1)", "CP-09"],
        ["REQ-CAL-01 / 02", "Cobertura >= 60 % por módulo; sin prioridad 1 en SpotBugs sin tratamiento.", "Encargo 2 / criterio propio", "CP-14, CP-15"],
        ["REQ-DEP-01", "Despliegue reproducible en contenedores.", "Pauta", "CP-17"],
    ], anchos=[2.5, 6.4, 3.5, 4.4], tam=8)


def seccion_enfoques(doc):
    titulo(doc, "3. Enfoques y herramientas de pruebas de seguridad")
    parrafo(doc, "Las pruebas de seguridad se organizan en seis enfoques complementarios. Ninguno basta por sí solo: el análisis "
            "estático no ve la configuración en ejecución, y el dinámico no ve el código que no se expone por HTTP. La tabla indica "
            "la función de cada enfoque en la detección de vulnerabilidades y su aplicación en el proyecto.")
    tabla(doc, ["Enfoque", "Función en la detección", "Herramienta y ejemplo en SmartLogix"], [
        ["SAST (análisis estático de código)", "Detecta patrones inseguros sin ejecutar el código: configuración de CSRF, inyección y registros.",
         "SpotBugs + FindSecBugs (CSRF deshabilitado, CRLF en logs); SonarQube (S4502); ESLint con eslint-plugin-security (inyección de objetos)."],
        ["DAST (análisis dinámico)", "Ataca la aplicación en ejecución y observa cabeceras, errores y respuestas del servidor.",
         "OWASP ZAP baseline sobre el frontend y escaneo de la API con token válido. Detectó errores 500 y 503 en la API (INC-19, INC-20, y el caso que llevó a INC-22) y la ausencia de CSP (INC-21)."],
        ["SCA (composición de software)", "Identifica vulnerabilidades conocidas en dependencias de terceros.",
         "npm audit (producción y completo). Separa dependencias de ejecución de las de build (INC-09)."],
        ["Pruebas de caja negra de seguridad", "Verifican el comportamiento observable frente a entradas hostiles o no autorizadas.",
         "Batería de casos CP-01 a CP-23 y pruebas de API contra el BFF (sin token, token falso, entradas inválidas)."],
        ["Pruebas de configuración", "Comprueban secretos, orígenes permitidos y cabeceras en los archivos de despliegue.",
         "CP-12 (CORS), CP-13 (secreto), CP-17 (Compose) y la revisión de nginx.conf."],
        ["Pruebas de regresión de seguridad", "Garantizan que una corrección no se pierda en versiones posteriores.",
         "Las pruebas que fallaban en main y pasan en v2 quedan en el pipeline (sección 6.5)."],
    ], anchos=[3.6, 5.6, 7.6], tam=8)
    parrafo(doc, "Criterio de selección: se eligieron herramientas gratuitas, con imagen oficial o plugin de Maven y npm, y "
            "adecuadas al lenguaje (Java 21) y al framework (Spring Boot 3.2, React 18). Se descartó Burp Suite Community por sus "
            "limitaciones de automatización; se usa ZAP, que se ejecuta en CI sin licencia.")


def seccion_controles(doc):
    titulo(doc, "4. Diseño de los controles de seguridad automatizados")
    parrafo(doc, "La figura 1 muestra el pipeline de GitHub Actions. Cada etapa tiene una puerta de calidad o de seguridad, y cada "
            "puerta se vincula con un criterio normativo o con un requisito del caso. Las puertas bloquean el merge a main.")
    figura(doc, os.path.join(E3, "D01-pipeline-controles.png"),
           "Figura 1. Pipeline de integración continua y controles automatizados (docs/seguridad/diagramas/pipeline.html).", ancho=16.5)
    tabla(doc, ["Control", "Verifica", "Criterio normativo o de calidad", "Bloquea si..."], [
        ["Pruebas backend + JaCoCo", "Comportamiento y cobertura de 4 módulos", "ISO/IEC 25010 (mantenibilidad)", "Hay pruebas en rojo o cobertura < 60 %"],
        ["SpotBugs + FindSecBugs", "Patrones de seguridad de Spring y Java", "OWASP A05 (configuración)", "Hay hallazgos de prioridad 1 sin tratamiento"],
        ["Pruebas frontend + ESLint", "Comportamiento de componentes y patrones inseguros", "OWASP A03 (inyección)", "Hay pruebas en rojo o errores de lint"],
        ["npm audit --omit=dev", "Vulnerabilidades en dependencias de ejecución", "OWASP A06 (componentes vulnerables)", "Hay critical o high en producción"],
        ["Stack Docker + E2E/API", "Flujos reales con autenticación y validaciones", "Ley 21.719 art. 14 quinquies (medidas de seguridad)", "Falla un flujo o la API responde mal"],
        ["OWASP ZAP baseline", "Cabeceras, errores y configuración en ejecución", "OWASP A05; Ley 21.719 art. 14 quinquies", "Hay alertas de riesgo alto"],
        ["SonarQube (local)", "Calidad, duplicación y vulnerabilidades del código", "ISO/IEC 25010; criterio de la asignatura", "Gate de calidad no superado (ver INC-24)"],
    ], anchos=[3.6, 4.6, 4.8, 3.8], tam=8)
    parrafo(doc, "SonarQube se ejecuta en un servidor local porque el pipeline remoto no puede acceder a localhost. Sus resultados "
            "se incluyen como evidencia del análisis, y el job de SonarQube queda preparado para activarse con los secretos del "
            "repositorio. Esa diferencia se declara en el informe.")


def seccion_resultados_seguridad(doc):
    titulo(doc, "5. Resultados de las pruebas de seguridad")
    titulo(doc, "5.1 Análisis dinámico (OWASP ZAP)", 2)
    parrafo(doc, "Se ejecutó ZAP en modo baseline sobre el frontend y como escaneo de la API (OpenAPI del BFF) con un token válido "
            "inyectado. La tabla compara la versión de referencia (main) con la versión final (v2). Las cifras son instancias de alerta "
            "según el reporte JSON.")
    filas = []
    for nivel in ["High", "Medium", "Low", "Informational"]:
        filas.append([nivel, ZAP_FM.get(nivel, 0), ZAP_FV.get(nivel, 0), ZAP_AM.get(nivel, 0), ZAP_AV.get(nivel, 0)])
    tabla(doc, ["Riesgo", "Frontend (main)", "Frontend (v2)", "API (main)", "API (v2)"], filas, anchos=[3.6, 3.3, 3.3, 3.3, 3.3], tam=9)
    parrafo(doc, "Lectura de los resultados: no hay alertas de riesgo alto en ninguna versión, por lo que la puerta B del pipeline "
            "queda superada. En el frontend, las alertas de riesgo medio bajan de 3 a 1: la residual es 'style-src unsafe-inline', "
            "necesaria porque los componentes usan estilos en línea (INC-21). En la API, las alertas de baja severidad bajan de "
            "17 a 9. Quedan respuestas 500 de baja severidad en pruebas de inyección de plantillas sobre parámetros de búsqueda; "
            "se documentan como observación.")
    figura(doc, os.path.join(E3, "Z01-zap-api-base.png"), "Figura 2. Reporte ZAP de la API en la versión de referencia (main).", ancho=14)
    figura(doc, os.path.join(E3, "Z02-zap-api-final.png"), "Figura 3. Reporte ZAP de la API en la versión final (v2).", ancho=14)

    titulo(doc, "5.2 Análisis estático (SAST)", 2)
    filas = []
    for s in SERVICIOS:
        v = SB.get(s)
        filas.append([s, f"{v[0]} / {v[1]}" if v else "sin reporte"])
    tabla(doc, ["Módulo", "Hallazgos totales / prioridad 1 (v2)"], filas, anchos=[6.0, 6.0], tam=9)
    parrafo(doc, "En v2 no hay hallazgos de prioridad 1 sin tratamiento. El único de prioridad 1 (SPRING_CSRF_PROTECTION_DISABLED) "
            "queda como riesgo aceptado en cada módulo, con su exclusión documentada en spotbugs-exclude.xml. La versión de referencia "
            "tenía un hallazgo de prioridad 1 en el BFF.")
    tabla(doc, ["Métrica SonarQube", "Backend (v2)", "Frontend (v2)"], [
        ["Bugs", SONAR_B.get("bugs"), SONAR_F.get("bugs")],
        ["Vulnerabilidades abiertas", SONAR_B.get("vulnerabilities"), SONAR_F.get("vulnerabilities")],
        ["Vulnerabilidades aceptadas (WONTFIX)", SONAR_ACEPT, 0],
        ["Code smells", SONAR_B.get("code_smells"), SONAR_F.get("code_smells")],
        ["Cobertura", f"{SONAR_B.get('coverage')} %", f"{SONAR_F.get('coverage')} %"],
        ["Duplicación (global)", f"{SONAR_B.get('duplicated_lines_density')} %", f"{SONAR_F.get('duplicated_lines_density')} %"],
        ["Quality gate", SONAR_GATE_B.get("status"), SONAR_GATE_F.get("status")],
    ], anchos=[7.0, 4.0, 4.0], tam=9)
    cond_dup = next((c for c in SONAR_GATE_B.get("conditions", []) if c.get("metricKey") == "new_duplicated_lines_density"), {})
    parrafo(doc, f"El quality gate del backend falla por la duplicación de código en código nuevo ({str(cond_dup.get('actualValue', ''))[:5]} %). "
            "Es un hallazgo real de mantenibilidad (INC-24) y no se ocultó: la propuesta SEG-03 lo resuelve con un módulo común. "
            "Las cuatro vulnerabilidades S4502 son el mismo riesgo CSRF de cada módulo y se aceptaron en SonarQube con una "
            "justificación registrada en el issue.")
    bloque_figuras(doc, [
        (os.path.join(E3, "S01-sonar-backend.png"), "Figura 4. SonarQube, backend (vista general): gate fallido por duplicación."),
        (os.path.join(E3, "S02-sonar-issues-backend.png"), "Figura 5. SonarQube, issues del backend (riesgo CSRF aceptado)."),
        (os.path.join(E3, "S03-sonar-frontend.png"), "Figura 6. SonarQube, frontend: gate superado."),
    ], columnas=2, ancho=8.0)

    titulo(doc, "5.3 Análisis de dependencias (SCA)", 2)
    tabla(doc, ["Alcance", "Crítica", "Alta", "Moderada", "Total"], [
        ["Completo (main, Encargo 2)", 3, 13, 7, 23],
        ["Producción (v2): npm audit --omit=dev", NPM_PROD["critical"], NPM_PROD["high"], NPM_PROD["moderate"], NPM_PROD["total"]],
        ["Completo (v2): incluye build y test", NPM_FULL["critical"], NPM_FULL["high"], NPM_FULL["moderate"], NPM_FULL["total"]],
    ], anchos=[7.0, 2.2, 2.2, 2.2, 2.2], tam=9)
    parrafo(doc, "La versión de referencia tenía 23 vulnerabilidades en total (3 críticas y 13 altas, según el Encargo 2). Las "
            "dependencias de producción quedan sin critical ni high. La moderada restante (react-router-dom 6) exige migrar a la "
            "versión 7, que es un cambio mayor; se mantiene como riesgo documentado. Las críticas y altas que quedan son de vitest, "
            "vite y tailwind, usados solo al compilar y probar (INC-09).")

    titulo(doc, "5.4 Batería de casos de prueba", 2)
    parrafo(doc, f"La batería contiene {len(FIN)} casos. Se ejecutó en la versión de referencia (main) y en la final (v2) con el "
            "mismo script (docs/pruebas/ejecutar_casos.py). Cada caso registra requisito, datos de entrada, resultado esperado, criterio "
            "de aceptación, criticidad y evidencia. Las tarjetas de cada caso están en el anexo A.")
    filas = []
    for cid in FIN:
        m, f = MAIN.get(cid), FIN[cid]
        filas.append([cid, f["titulo"][:60], f["requisito"], pasa(m) if m else "—", pasa(f), f["criticidad_si_falla"]])
    tabla(doc, ["Caso", "Descripción", "Requisito", "Base", "Final", "Criticidad"], filas,
          anchos=[1.5, 7.2, 2.5, 1.6, 1.6, 2.2], tam=8)
    parrafo(doc, "Notas de la comparación. CP-15 falla en la base solo porque la rama v2 regeneró los reportes de SpotBugs; en la "
            "ejecución final pasa con los reportes actualizados. CP-16 es el riesgo residual documentado (INC-09). La versión de "
            "referencia también se evaluó con los casos CP-20 a CP-23, añadidos en este encargo.", negrita_inicio="")


def seccion_resultados_automatizacion(doc):
    titulo(doc, "6. Resultados de las pruebas automatizadas")
    titulo(doc, "6.1 Suites automatizadas y cobertura", 2)
    filas = []
    for s in SERVICIOS:
        j = JC.get(s)
        filas.append([s, PR_PER.get(s, 0), f"{j[0]} %" if j else "—", f"{j[1]} líneas" if j else "—"])
    filas.append(["Total backend", PR_TOT, "—", "—"])
    filas.append(["Frontend (Vitest + RTL)", 55, "68,5 % statements", "13 archivos de prueba"])
    filas.append(["E2E y API (Playwright)", len(PW_TESTS), "—", "5 flujos de interfaz y 6 de API"])
    tabla(doc, ["Suite", "Pruebas", "Cobertura", "Alcance"], filas, anchos=[5.2, 2.4, 3.6, 5.6], tam=9)
    parrafo(doc, "Cada módulo supera el umbral de 60 % de líneas. El gate de JaCoCo está activo porque el argLine se corrigió "
            "(INC-07). Las pruebas nuevas de seguridad son de integración con el contexto completo de Spring, con su propia base "
            "H2 para evitar colisiones entre contextos (SecurityIntegrationTest).")

    titulo(doc, "6.2 Pruebas E2E y de API", 2)
    filas = []
    for titulo_t, estado, dur in PW_TESTS:
        filas.append([titulo_t[:80], estado.upper(), f"{dur:.2f} s"])
    tabla(doc, ["Prueba (versión v2)", "Resultado", "Duración"], filas, anchos=[11.0, 2.5, 2.5], tam=8)
    parrafo(doc, f"Resultado de la ejecución final: {PW_STATS.get('expected', 0)} de {PW_STATS.get('expected', 0)} pruebas aprobadas, "
            f"{PW_STATS.get('unexpected', 0)} fallidas y {PW_STATS.get('flaky', 0)} inestables, en "
            f"{PW_STATS.get('duration', 0) / 1000:.1f} s. En la rama main, la misma suite obtuvo 8 de 11: UI-03 falló por INC-18, "
            "API-04 por INC-19 (503) y API-05 por INC-20 (500). La transcripción de esa ejecución está en "
            "docs/evidencias/encargo3/e2e-linea-base-main.txt.")
    bloque_figuras(doc, [
        (os.path.join(E3, "E01-playwright-reporte.png"), "Figura 7. Reporte HTML de Playwright (ejecución final)."),
        (os.path.join(EVID, "capturas", "UI-03-credenciales-incorrectas.png"), "Figura 8. UI-03 en v2: se muestra el error y se conserva el usuario (INC-18 cerrado)."),
        (os.path.join(EVID, "capturas", "UI-06-bloqueo-tras-intentos-fallidos.png"), "Figura 9. UI-06 en v2: bloqueo temporal tras cinco intentos fallidos (INC-13)."),
        (os.path.join(EVID, "capturas", "UI-05-catalogo-productos.png"), "Figura 10. UI-05: catálogo cargado desde el BFF con token."),
    ], columnas=2, ancho=7.8)

    titulo(doc, "6.3 Pipeline de integración continua", 2)
    parrafo(doc, "El workflow .github/workflows/ci.yml se ejecutó en la rama v2 y en el pull request #1. Todos los jobs terminaron "
            "con éxito en la última ejecución (ejecución 38665699298, 9 minutos de duración total). La primera ejecución del DAST "
            "falló por permisos de escritura del directorio de reportes; el registro del job lo mostró y se corrigió en un commit "
            "posterior (incidente de pipeline, no de producto).")
    tabla(doc, ["Job", "Resultado", "Duración"], [
        ["Backend (bff-gateway)", "Éxito", "41 s"],
        ["Backend (inventory-service)", "Éxito", "45 s"],
        ["Backend (order-service)", "Éxito", "45 s"],
        ["Backend (shipping-service)", "Éxito", "42 s"],
        ["Frontend", "Éxito", "28 s"],
        ["E2E y API sobre Docker", "Éxito", "5 min 15 s"],
        ["DAST (OWASP ZAP baseline)", "Éxito", "2 min 56 s"],
    ], anchos=[8.0, 4.0, 4.0], tam=9)
    bloque_figuras(doc, [
        (os.path.join(E3, "A01-github-actions-run.png"), "Figura 11. Ejecución del pipeline en GitHub Actions: todos los jobs en verde."),
        (os.path.join(E3, "A02-github-pr-1.png"), "Figura 12. Pull request #1 hacia main con el pipeline ejecutado."),
    ], columnas=2, ancho=8.0)

    titulo(doc, "6.4 Eficiencia de la automatización", 2)
    parrafo(doc, "La automatización cubre 134 pruebas de backend, 55 de frontend, 11 de E2E y API, y la batería de 23 casos. El "
            "tiempo de ejecución automatizado de la suite E2E y de API es de 6,8 segundos. Cada job de backend del pipeline tarda "
            "entre 41 y 49 segundos, incluida la preparación del entorno. El ahorro frente a la verificación manual no se midió con cronómetro: "
            "esa comparación requiere ejecutar los mismos casos a mano y registrar su tiempo, y no se hizo. La eficiencia se justifica "
            "en la repetibilidad: los mismos casos se ejecutan en cada PR y detectan regresiones sin intervención.")

    titulo(doc, "6.5 Regresión: qué prueba detecta cada defecto corregido", 2)
    parrafo(doc, "Para cada defecto corregido se identifica la prueba que lo detecta. El criterio es que la prueba falle sobre la "
            "versión de referencia y pase sobre la versión final. Así, la corrección queda protegida frente a cambios futuros.")
    tabla(doc, ["Incidente", "Prueba que lo detecta", "Comportamiento en main", "Comportamiento en v2"],
          [list(r) for r in REGRESION], anchos=[2.2, 5.6, 4.5, 4.5], tam=8)


def seccion_incidentes(doc):
    titulo(doc, "7. Incidentes identificados, criticidad y propuestas de mitigación")
    parrafo(doc, "La escala de criticidad es la de la plantilla: CRÍTICO (compromete credenciales o datos, o impide el uso; "
            "remediación inmediata), GRAVE (afecta funcionalidades importantes o la cadena de desarrollo; corrección urgente), "
            "MODERADO (afecta casos específicos; próxima iteración) y LEVE (apariencia o texto). El estado distingue entre cerrado, "
            "mitigado con residual, riesgo aceptado y abierto.")
    cab = ["ID", "Caso / origen", "Requisito", "Descripción", "Ubicación", "Criticidad", "Estado", "Tratamiento y evidencia"]
    nueva_seccion(doc, horizontal=True)
    tabla(doc, cab, [list(i) for i in INC], anchos=[1.5, 2.1, 2.1, 5.0, 4.0, 1.9, 2.6, 6.0], tam=7)
    conteo = {}
    for i in INC:
        conteo[i[5]] = conteo.get(i[5], 0) + 1
    cerrados = sum(1 for i in INC if i[6].startswith("CERRADO"))
    parrafo(doc, f"Resumen: {len(INC)} incidentes ({', '.join(f'{k.lower()}: {v}' for k, v in conteo.items())}). Cerrados: "
            f"{cerrados}. Abiertos, mitigados con residual o con riesgo aceptado: {len(INC) - cerrados}. Los incidentes críticos "
            "INC-01, INC-02 y INC-15 están cerrados en el código; INC-02 requiere además rotar el secreto, porque el valor "
            "original sigue en el historial de git.")
    nueva_seccion(doc, horizontal=False)

    titulo(doc, "7.1 Propuestas de mitigación para los defectos abiertos", 2)
    propuestas = [
        ("SEG-01", "Rotación del secreto JWT y limpieza del historial", "CRÍTICO (por historial público)",
         "Generar un nuevo JWT_SECRET en GitHub Secrets y en el .env de cada entorno, invalidar los tokens emitidos con el secreto anterior "
         "y reescribir el historial con git filter-repo (operación destructiva que requiere autorización expresa del equipo)."),
        ("SEG-02", "Mover el token a una cookie HttpOnly", "MODERADO (INC-12)",
         "Emitir el JWT en una cookie HttpOnly, Secure y SameSite=Strict; el frontend deja de leer el token. Reactivar la protección CSRF "
         "con token sincronizado y retirar la exclusión de SpotBugs. Impacto: cambio de la autenticación del frontend y pruebas E2E nuevas."),
        ("SEG-03", "Módulo común de seguridad y manejo de errores", "MODERADO (INC-24)",
         "Extraer SecurityConfig, JwtAuthFilter, GlobalExceptionHandler y la plantilla de pruebas de integración a una librería "
         "compartida (common-security). Reduce la duplicación en los cuatro módulos, cumple el gate de SonarQube y concentra las "
         "correcciones de seguridad en un solo lugar."),
        ("SEG-04", "Eliminar 'unsafe-inline' de la CSP", "MODERADO (INC-21)",
         "Sustituir los estilos en línea por clases de Tailwind y usar hashes o nonces para los estilos generados. Verificar con ZAP y con "
         "las pruebas E2E, porque framer-motion aplica estilos dinámicos."),
        ("SEG-05", "Migración de herramientas de build y react-router", "GRAVE (INC-09)",
         "Actualizar vitest, vite y tailwind a versiones mayores compatibles, y evaluar react-router 7. Revalidar la cobertura con "
         "Vitest 5 antes de adoptarla: la versión 5 probada redujo la cobertura medida de 68,5 % a 51,8 %."),
        ("SEG-06", "Protección de la autenticación", "MODERADO (INC-13 residual)",
         "El bloqueo por usuario puede usarse para negar el acceso a una cuenta legítima. Añadir límite por IP y un tiempo de bloqueo "
         "creciente, y notificar al titular de los intentos de acceso."),
        ("SEG-07", "Revisión de la clasificación de SonarQube", "MODERADO (INC-08)",
         "Revisar cada cuatro meses los cuatro issues S4502 aceptados, para confirmar que la API sigue siendo stateless y sin cookies."),
    ]
    for idp, nombre, impacto, prop in propuestas:
        tabla(doc, ["ID", "NOMBRE", "IMPACTO"], [[idp, nombre, impacto]], anchos=[2.0, 8.5, 6.0], tam=9)
        tabla(doc, ["PROPUESTA DE REMEDIACIÓN"], [[prop]], anchos=[16.5], tam=9)


def seccion_mantenimiento(doc):
    titulo(doc, "8. Plan de mantenimiento y preservación de la calidad, la seguridad y la normativa")
    parrafo(doc, "El plan asegura que las mejoras de este encargo se mantengan en versiones futuras. Define qué se revisa, con qué "
            "frecuencia, quién lo hace y qué criterio determina si el cambio puede avanzar. Los responsables son los integrantes del "
            "grupo, con asignación rotativa, según la práctica de la asignatura.")
    tabla(doc, ["Actividad", "Frecuencia", "Responsable", "Criterio de éxito"], [
        ["Regresión completa: pruebas unitarias, batería de casos, E2E y DAST", "En cada PR y antes de cada versión", "Quien abre el PR", "Pipeline en verde y ninguna prueba de regresión fallida"],
        ["Auditoría de dependencias (npm audit --omit=dev y completo) y Maven", "Cada semana (Dependabot) y antes de cada versión", "Responsable de dependencias", "Sin critical ni high en producción"],
        ["Revisión de SpotBugs y SonarQube", "Cada PR y mensual", "Revisor de calidad", "Prioridad 1 tratada; gate superado o deuda registrada"],
        ["Revisión de cabeceras, CORS y CSP con ZAP", "Mensual y ante cambios en nginx o en la configuración de seguridad", "Responsable de seguridad", "Sin alertas de riesgo alto; residuales en el registro"],
        ["Rotación de JWT_SECRET", "Cada 90 días y tras cualquier sospecha", "Responsable de despliegue", "Secreto nuevo en GitHub Secrets; tokens antiguos invalidados"],
        ["Revisión normativa (Ley 21.719 y reglamentos de la Agencia)", "Cada seis meses y al publicarse cada reglamento", "Responsable de cumplimiento", "Registro de la revisión y de las obligaciones pendientes"],
        ["Registro y revisión de incidentes de seguridad", "Continuo; revisión mensual", "Responsable de seguridad", "Todo incidente con criticidad, causa y corrección"],
        ["Verificación de copias y de retención de logs", "Mensual", "Responsable de operación", "Logs sin datos personales innecesarios"],
        ["Gestión de la deuda técnica (SEG-03, INC-24)", "Trimestral", "Equipo", "Duplicación del gate por debajo del umbral"],
    ], anchos=[5.4, 3.6, 3.4, 4.1], tam=8)
    titulo(doc, "8.1 Política de regresión y de cambios", 2)
    vinetas(doc, [
        ("Todo defecto corregido tiene una prueba: ", "la prueba debe fallar antes de la corrección y pasar después (sección 6.5)."),
        ("Ningún cambio de seguridad se fusiona sin pruebas: ", "autenticación, cabeceras y configuración requieren prueba automatizada o caso en la batería."),
        ("Las excepciones se documentan: ", "un riesgo aceptado se registra en el informe, en SonarQube y en el archivo de exclusión, con su justificación y revisión periódica."),
        ("Las pruebas nuevas no dependen del orden: ", "cada contexto de prueba usa su propia base y cada prueba de usuario crea un usuario único."),
    ])
    titulo(doc, "8.2 Preservación de los aspectos normativos y legales", 2)
    parrafo(doc, "La Ley 21.719 reforma la Ley 19.628 y crea la Agencia de Protección de Datos Personales. Según la Biblioteca del "
            "Congreso Nacional, entra en vigencia el 1 de diciembre de 2026; en septiembre de 2026 el Gobierno propuso postergarla al "
            "1 de diciembre de 2027. Este informe no puede confirmar si la propuesta se aprobó: debe verificarse en bcn.cl antes de la "
            "entrega y antes de tratar datos reales.")
    tabla(doc, ["Obligación (ley reformada)", "Estado en SmartLogix", "Acción propuesta"], [
        ["Medidas de seguridad apropiadas (art. 14 quinquies): cifrado, confidencialidad e integridad",
         "Parcial: BCrypt, JWT entre servicios, CSP, bloqueo de intentos. Sin HTTPS en el entorno de demostración y con H2 en memoria.",
         "TLS terminado en el gateway; base de datos persistente cifrada en reposo (propuesta del Encargo 2, R6)."],
        ["Reporte de vulneraciones a la Agencia (art. 14 sexies)",
         "No existe procedimiento ni registro de vulneraciones.",
         "Procedimiento de respuesta a incidentes con plazos, responsable y plantilla de notificación."],
        ["Derechos del titular: acceso, rectificación, supresión, oposición, portabilidad (arts. 4 y 9)",
         "No hay endpoints para ejercerlos.",
         "Endpoints de consulta, corrección, supresión y exportación en formato estructurado."],
        ["Consentimiento y transparencia (arts. 12 y 14 ter)",
         "El registro no solicita consentimiento ni publica política de privacidad.",
         "Casilla de consentimiento en el registro y política de privacidad publicada."],
        ["Minimización y conservación de datos (principio de proporcionalidad)",
         "Se guardan nombre, correo y dirección de envío sin plazo de conservación.",
         "Política de retención y purga; logs sin datos personales."],
    ], anchos=[5.2, 5.6, 5.7], tam=8)


def seccion_etica(doc):
    titulo(doc, "9. Análisis ético y normativo de los resultados")
    titulo(doc, "9.1 Análisis ético", 2)
    vinetas(doc, [
        ("Independencia de la evaluación: ", "el equipo evalúa código propio. Para reducir el sesgo, los resultados esperados se fijaron "
         "antes de ejecutar y las discrepancias se registran como incidentes, no como cambios silenciosos de la expectativa."),
        ("Resultados desfavorables incluidos: ", "se reportan los fallos de la versión de referencia, el riesgo residual (INC-09), la "
         "cobertura que bajó con Vitest 5 y el quality gate de SonarQube que no se supera. Ocultar esos datos sería engañoso."),
        ("Divulgación responsable: ", "las vulnerabilidades se describen con su ubicación para permitir la corrección. El secreto y las "
         "contraseñas no se reproducen; los tokens se redactan antes de guardar cualquier evidencia."),
        ("Alcance autorizado: ", "todas las pruebas dinámicas se ejecutaron sobre el stack local y sobre el repositorio propio, en "
         "línea con la autorización de la asignatura. No se apuntó a sistemas de terceros."),
        ("Datos personales: ", "los usuarios de prueba son sintéticos y las ejecuciones usan datos de semilla. Aun así, el "
         "análisis trata la protección de datos como un requisito, porque el diseño permitiría tratar datos reales sin las medidas faltantes."),
        ("Responsabilidad sobre los riesgos aceptados: ", "el riesgo CSRF y el 'unsafe-inline' se aceptan con una razón técnica "
         "concreta y una fecha de revisión, para que no se conviertan en deuda olvidada."),
    ])
    titulo(doc, "9.2 Análisis normativo", 2)
    parrafo(doc, "Desde la perspectiva normativa, los controles técnicos avanzan de forma clara: la autenticación, el secreto, el "
            "bloqueo y las cabeceras reducen el riesgo de acceso indebido. Las brechas que quedan son de gobierno de datos más que "
            "de código: derechos del titular, consentimiento, respuesta a incidentes y conservación. Esas brechas deben cerrarse antes "
            "del tratamiento de datos reales. El cumplimiento de la Ley 21.719 depende además de la fecha de entrada en vigencia, que "
            "debe confirmarse, y de los reglamentos que dicte la Agencia.")


def seccion_conclusiones(doc):
    titulo(doc, "10. Conclusiones y propuestas para preservar la calidad")
    base_ok = sum(1 for c in MAIN.values() if c["resultado"] == "PASA")
    fin_ok = sum(1 for c in FIN.values() if c["resultado"] == "PASA")
    parrafo(doc, f"La versión de referencia aprobó {base_ok} de {len(MAIN)} casos de la batería, y la versión final aprueba {fin_ok} de {len(FIN)}. "
            "Las 11 pruebas E2E y de API pasan en la versión final (8 de 11 en la de referencia). Los incidentes críticos de "
            "credenciales, secreto y exposición de microservicios quedan cerrados en el código. Se identificaron además cuatro defectos "
            "nuevos mediante el análisis dinámico y las pruebas de interfaz (INC-19 a INC-22), que también se corrigieron.")
    parrafo(doc, "Quedan pendientes el secreto del historial (SEG-01), la duplicación entre módulos (SEG-03) y las dependencias de build "
            "(SEG-05). Son los puntos que más afectan a la calidad sostenible del proyecto.")
    vinetas(doc, [
        "R1. Ejecutar el pipeline en cada PR y no fusionar con puertas en rojo (sección 4).",
        "R2. Cumplir el plan de mantenimiento de la sección 8, con responsables asignados y registro de cada revisión.",
        "R3. Ejecutar la batería de casos y la suite E2E después de cada cambio de seguridad, y tratar toda regresión como incidente.",
        "R4. Confirmar la fecha de vigencia de la Ley 21.719 y completar las obligaciones de la sección 8.2 antes de tratar datos reales.",
        "R5. Activar el job de SonarQube en el pipeline remoto con un servidor accesible y los secretos del repositorio.",
        "R6. Medir el tiempo de la verificación manual para completar la comparación de eficiencia (sección 6.4).",
    ])


def anexos(doc):
    titulo(doc, "Anexo A. Tarjetas de los casos de prueba (ejecución final)")
    parrafo(doc, "Cada tarjeta muestra el requisito, los datos de entrada, el resultado esperado, el criterio, la criticidad y cada "
            "verificación con su resultado observado. Se generan desde docs/evidencias/v2-final/resultados.json.")
    ids = list(FIN.keys())
    pares = [(os.path.join(EVID, "capturas", f"{cid}-tarjeta.png"), f"{cid}: {FIN[cid]['titulo'][:70]}") for cid in ids]
    bloque_figuras(doc, pares, columnas=2, ancho=8.3)

    titulo(doc, "Anexo B. Reproducibilidad", 2)
    for c in ["cp .env.example .env            # definir JWT_SECRET (openssl rand -base64 64)",
              "docker compose up -d --build",
              "./docs/pruebas/esperar_stack.sh 240",
              "python3 docs/pruebas/ejecutar_casos.py <etiqueta>",
              "cd e2e && npm ci && npx playwright test",
              "./docs/seguridad/ejecutar_zap.sh <etiqueta>",
              "cd <servicio> && mvn -B clean verify",
              "cd <servicio> && mvn -Psecurity com.github.spotbugs:spotbugs-maven-plugin:4.8.6.6:spotbugs",
              "cd frontend && npm ci && npx vitest run --coverage && npm audit --omit=dev",
              "python3 docs/informe/generar_informe_encargo3.py"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.0
        fuente(p.add_run(c), tam=9)

    titulo(doc, "Anexo C. Mapa de evidencias", 2)
    tabla(doc, ["Archivo", "Contenido"], [
        ["docs/evidencias/main-encargo2-stack/resultados.json", "Batería de 23 casos sobre la versión de referencia"],
        ["docs/evidencias/v2-final/resultados.json", "Batería de 23 casos sobre la versión final"],
        ["docs/evidencias/encargo3/e2e-linea-base-main.txt", "Salida de E2E y API en la versión de referencia"],
        ["docs/evidencias/encargo3/playwright-resultados-v2.json", "Resultados de E2E y API en la versión final"],
        ["docs/seguridad/zap/main y v2-final", "Reportes ZAP (HTML y JSON) de ambas versiones"],
        ["docs/evidencias/encargo3/sonar-*.json", "Métricas y quality gate de SonarQube"],
        ["docs/evidencias/encargo3/npm-audit-*.json", "Auditoría de dependencias (producción y completa)"],
        ["docs/evidencias/encargo3/spotbugs-*.xml y jacoco-*.csv", "Hallazgos de análisis estático y cobertura por módulo"],
        ["docs/evidencias/encargo3/A01 a A03, S01 a S03, Z01, Z02, E01, D01", "Capturas de GitHub Actions, SonarQube, ZAP, Playwright y del pipeline"],
        ["docs/evidencias/capturas/UI-01 a UI-06", "Capturas del flujo en el navegador"],
        ["e2e/tests, .github/workflows/ci.yml, docs/pruebas", "Código de las pruebas y del pipeline"],
    ], anchos=[7.5, 9.0], tam=8)

    titulo(doc, "Anexo D. Responsables de la ejecución", 2)
    parrafo(doc, "Asignación de responsabilidades dentro del grupo. Se define como propuesta del equipo y debe confirmarse con cada "
            "integrante antes de la defensa, porque la defensa es individual y cada uno debe poder explicar el conjunto.")
    tabla(doc, ["Integrante", "Responsabilidad en el Encargo 3"], [
        ["Nicolás Castillo", "Stack Docker, mitigaciones del backend, análisis SpotBugs y pipeline de CI/CD."],
        ["Benjamín Catalán", "Análisis dinámico (ZAP), pruebas E2E y de API, y capturas de la interfaz."],
        ["Benjamín Quiroz", "Análisis estático (SonarQube y ESLint), auditoría de dependencias y revisión normativa."],
    ], anchos=[4.5, 12.0], tam=9)


def construir():
    doc = Document()
    estilos(doc)
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Cm(2.5)
        sec.top_margin = sec.bottom_margin = Cm(2.5)
    portada(doc)
    indice(doc)
    seccion_introduccion(doc)
    seccion_criterios(doc)
    seccion_enfoques(doc)
    seccion_controles(doc)
    seccion_resultados_seguridad(doc)
    seccion_resultados_automatizacion(doc)
    seccion_incidentes(doc)
    seccion_mantenimiento(doc)
    seccion_etica(doc)
    seccion_conclusiones(doc)
    anexos(doc)
    pie_pagina(doc)
    doc.save(SALIDA)
    print("Informe generado:", SALIDA)


if __name__ == "__main__":
    construir()
