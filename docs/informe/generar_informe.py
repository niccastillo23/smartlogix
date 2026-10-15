#!/usr/bin/env python3
"""
Genera el informe del Encargo 2 (ISY1102) en formato Word a partir de las evidencias del repositorio.
Las cifras se leen de los artefactos generados (JaCoCo, SpotBugs, Surefire, npm audit y
resultados de docs/pruebas/ejecutar_casos.py), no se escriben a mano.

Uso: python3 docs/informe/generar_informe.py
"""
import csv
import glob
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import date

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVID = os.path.join(RAIZ, "docs", "evidencias")
SALIDA = os.path.join(RAIZ, "docs", "informe", "Informe_EP3_ISY1102_SmartLogix.docx")
SERVICIOS = ["inventory-service", "order-service", "shipping-service", "bff-gateway"]
HOY = date.today()
FECHA_TXT = "14 de octubre de 2026"

# ----------------------------------------------------------------- datos medidos
def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return {c["id"]: c for c in json.load(f)["casos"]}

BASE = leer_json(os.path.join(EVID, "baseline-codigo-original", "resultados.json"))
FINAL = leer_json(os.path.join(EVID, "mitigado-docker", "resultados.json"))


def cobertura(raiz):
    out, ci_t, mi_t = {}, 0, 0
    for s in SERVICIOS:
        f = os.path.join(raiz, s, "target", "site", "jacoco", "jacoco.csv")
        if not os.path.exists(f):
            out[s] = None
            continue
        filas = list(csv.DictReader(open(f)))
        mi = sum(int(x["LINE_MISSED"]) for x in filas)
        ci = sum(int(x["LINE_COVERED"]) for x in filas)
        out[s] = round(100 * ci / (ci + mi), 1)
        ci_t += ci
        mi_t += mi
    out["total"] = round(100 * ci_t / (ci_t + mi_t), 1) if ci_t + mi_t else None
    return out


def spotbugs(raiz):
    out = {}
    for s in SERVICIOS:
        f = os.path.join(raiz, s, "target", "spotbugsXml.xml")
        if not os.path.exists(f):
            out[s] = None
            continue
        b = ET.parse(f).getroot().findall("BugInstance")
        out[s] = (len(b), sum(1 for x in b if x.get("priority") == "1"))
    return out


def pruebas(raiz):
    per, tot = {}, 0
    for s in SERVICIOS:
        n = 0
        for f in glob.glob(os.path.join(raiz, s, "target", "surefire-reports", "*.txt")):
            m = re.search(r"Tests run: (\d+)", open(f).read())
            n += int(m.group(1)) if m else 0
        per[s] = n
        tot += n
    return per, tot


COB_FINAL = cobertura(RAIZ)
SB_FINAL = spotbugs(RAIZ)
PR_FINAL, PR_TOT_FINAL = pruebas(RAIZ)
# Valores de la línea base medidos en el commit 2d7685f (ver docs/evidencias/linea-base y jdk21)
COB_BASE = {"inventory-service": 83.7, "order-service": 83.8, "shipping-service": 79.8, "bff-gateway": 71.1}
SB_BASE = {"inventory-service": (12, 0), "order-service": (24, 0), "shipping-service": (10, 0), "bff-gateway": (21, 1)}
PR_BASE_TOT = 86
NPM_BASE = {"critical": 3, "high": 13, "moderate": 7}
NPM_FINAL = {"critical": 3, "high": 6, "moderate": 6}
ESLINT_TOTAL = 58


def etiqueta(v):
    return "PASA" if v == "PASA" else v


# ----------------------------------------------------------------- requisitos
REQUISITOS = [
    ("REQ-SEG-01", "Autenticación con JWT; rechazo de accesos sin token o con credenciales inválidas.",
     "Ev1 REQ-SEG-01; Ev1 §2.2 (control de acceso)", ["CP-01", "CP-02"], "Seguridad / funcional"),
    ("REQ-FUNC-02", "Descuento WEB 5 %, MARKETPLACE 10 %, envío STANDARD/EXPRESS; rechazo de tipo de orden no soportado.",
     "Ev1 REQ-FUNC-02", ["CP-03", "CP-04"], "Funcional"),
    ("REQ-FUNC-03", "Búsqueda por marca, fragancia, rango de precio, stock y nombre.",
     "Ev1 REQ-FUNC-03", ["CP-06"], "Funcional"),
    ("REQ-RES-01", "Fallback automático del Circuit Breaker ante fallo del carrier externo.",
     "Ev1 REQ-RES-01; Ev1 §2.1 (tolerancia a fallos)", ["CP-05"], "Resiliencia"),
    ("REQ-VAL-01", "Validación de datos de entrada con rechazo HTTP 400 y sin persistencia.",
     "Ev1 REQ-VAL-01; Ev1 §2.2 (integridad)", ["CP-07", "CP-08"], "Seguridad / validación"),
    ("REQ-NFR-01", "Tiempos de respuesta: lectura < 500 ms y escritura < 1000 ms (p95).",
     "Ev1 §2.1 (rendimiento)", ["CP-09"], "No funcional / rendimiento"),
    ("REQ-SEG-02", "Las contraseñas se almacenan como hash, nunca en claro.",
     "Ev1 §2.2 (protección de datos); OWASP A02", ["CP-10"], "Seguridad / inspección"),
    ("REQ-SEG-03", "Los errores no exponen detalles internos al cliente.",
     "Ev1 §2.2 (manejo de errores); OWASP A05", ["CP-11"], "Seguridad / errores"),
    ("REQ-SEG-04", "CORS restringido a los orígenes definidos.",
     "Ev1 §2.2 (CORS)", ["CP-12"], "Seguridad / configuración"),
    ("REQ-SEG-05", "El secreto de firma JWT no figura en el código fuente.",
     "Hallazgo de revisión de código; OWASP A02 y A05", ["CP-13"], "Seguridad / configuración"),
    ("REQ-SEG-06", "Sin vulnerabilidades críticas o altas en dependencias del frontend.",
     "Análisis de composición de software (npm audit); OWASP A06", ["CP-16"], "Seguridad / SCA"),
    ("REQ-CAL-01", "Cobertura de líneas JaCoCo >= 60 % en cada servicio backend.",
     "Ev1 §2.1 (mantenibilidad)", ["CP-14"], "No funcional / mantenibilidad"),
    ("REQ-CAL-02", "Sin hallazgos de prioridad 1 en el análisis estático (SpotBugs + FindSecBugs).",
     "Pauta del Encargo 2, IL 2.3; criterio de aceptación propio", ["CP-15"], "Análisis estático"),
    ("REQ-SEG-07", "Los microservicios de negocio solo son accesibles a través del BFF autenticado.",
     "Ev1 §2.2 (control de acceso); hallazgo de revisión de arquitectura; OWASP A01", ["CP-18"], "Seguridad / control de acceso"),
    ("REQ-FUNC-04", "Alta de producto con persistencia y asignación de identificador.",
     "Ev1 §3.2 (pruebas funcionales de CRUD de productos, prioridad alta)", ["CP-19"], "Funcional"),
    ("REQ-DEP-01", "Despliegue reproducible en contenedores Docker.",
     "Pauta del Encargo 2 (imágenes Docker del software)", ["CP-17"], "Despliegue"),
]

# ----------------------------------------------------------------- incidentes
INCIDENTES = [
    ("INC-01", "CP-10", "REQ-SEG-02", "Contraseñas de usuario almacenadas en texto plano en un mapa en memoria y comparadas con igualdad directa.",
     "bff-gateway/.../AuthService.java (versión base: líneas 17, 24, 39)", "CRÍTICO",
     "Compromiso de credenciales de todos los usuarios ante cualquier acceso a memoria o volcado.",
     "CERRADO", "Hash BCrypt (PasswordEncoder) y prueba register_shouldStoreBcryptHashNotPlaintext."),
    ("INC-02", "CP-13", "REQ-SEG-05", "Secreto de firma JWT escrito literalmente en application.yml.",
     "bff-gateway/src/main/resources/application.yml (versión base: línea 17)", "CRÍTICO",
     "Quien conozca el secreto puede firmar tokens válidos para cualquier usuario.",
     "CERRADO (con reserva)", "Secreto desde ${JWT_SECRET}, sin valor por defecto. El valor sigue en el historial de git: debe considerarse expuesto y rotarse."),
    ("INC-03", "CP-11", "REQ-SEG-03", "Excepciones de conversión devuelven HTTP 404 con el mensaje interno del framework.",
     "order-service y demás servicios: GlobalExceptionHandler (versión base)", "MODERADO",
     "Revela tecnología y estructura interna; el código de estado es incorrecto.",
     "CERRADO", "Handler que responde 400/404/500 con mensaje genérico; errores no controlados se registran en log."),
    ("INC-04", "CP-02", "REQ-SEG-01", "Credenciales inválidas y registro duplicado responden HTTP 403 sin código controlado.",
     "bff-gateway (versión base: sin GlobalExceptionHandler)", "MODERADO",
     "Código de estado incorrecto para el cliente y para la auditoría de accesos.",
     "CERRADO", "401 para credenciales inválidas (mismo mensaje para usuario inexistente o clave errónea) y 409 para duplicados."),
    ("INC-05", "CP-04", "REQ-FUNC-02", "Tipo de orden no soportado responde HTTP 404 en lugar de 400.",
     "order-service/.../OrderService.java (versión base: RuntimeException)", "MODERADO",
     "El cliente interpreta el error como recurso inexistente.",
     "CERRADO", "IllegalArgumentException mapeada a 400."),
    ("INC-06", "CP-08", "REQ-VAL-01", "Un error 400 de validación del servicio de inventario llega al cliente a través del BFF como HTTP 403.",
     "bff-gateway (versión base). Causa probable: excepción no tratada y despacho de error protegido por autenticación",
     "MODERADO", "El cliente no recibe el motivo del rechazo.",
     "CERRADO", "Propagación de errores 4xx del servicio de destino y ruta /error pública. La causa es probable (no se confirmó con logs del BFF); el cambio elimina el síntoma observado."),
    ("INC-07", "CP-14", "REQ-CAL-01", "El gate de cobertura JaCoCo no se ejecutaba: el argLine de Surefire sustituía al agente y no se generaba jacoco.exec.",
     "pom.xml de los cuatro servicios (versión base: <argLine>)", "MODERADO",
     "La cobertura declarada no se verificaba en el build; el umbral era ineficaz.",
     "CERRADO", "argLine = @{argLine} -Dnet.bytebuddy.experimental=true. Cobertura medida en cada servicio."),
    ("INC-08", "CP-15", "REQ-CAL-02", "SpotBugs de prioridad 1: SPRING_CSRF_PROTECTION_DISABLED en SecurityConfig.",
     "bff-gateway/.../SecurityConfig.java:28", "MODERADO",
     "Riesgo CSRF si el token se transportara en cookies.",
     "RIESGO ACEPTADO", "Filtro de exclusión documentado (bff-gateway/spotbugs-exclude.xml). La API usa Bearer y sesión STATELESS. Se oculta el hallazgo del reporte; se declara aquí para transparencia."),
    ("INC-09", "CP-16", "REQ-SEG-06", "Vulnerabilidades en dependencias de desarrollo: 3 críticas (vitest, @vitest/coverage-v8, tinypool) y 6 altas (vite, tailwindcss, braces, chokidar, fast-glob, micromatch).",
     "frontend/package.json y package-lock.json", "GRAVE",
     "Impacto en la cadena de build y de pruebas; no en las dependencias de ejecución (axios quedó corregido).",
     "ABIERTO", "Corregir exige saltos de versión mayor (vitest 5, vite 7 o 8, tailwind 4). Vitest 5 se probó y redujo la cobertura medida de 68,5 % a 51,8 %, por lo que se descartó (ver sección 3.5)."),
    ("INC-10", "CP-17", "REQ-DEP-01", "El repositorio no contenía Dockerfile ni docker-compose.yml.",
     "Raíz del repositorio (versión base)", "MODERADO",
     "El despliegue no es reproducible y no cumple el insumo 'imágenes Docker' de la pauta.",
     "CERRADO", "Dockerfile multi-etapa por servicio, nginx como proxy de /api y docker-compose.yml con JWT_SECRET obligatorio."),
    ("INC-11", "Revisión documental", "REQ-CAL-01", "Cifras de cobertura de la Ev1 (87,4 % backend y 84,1 % frontend) no reproducibles.",
     "docs de la Ev1 frente a frontend/coverage y target/site/jacoco", "MODERADO",
     "Afirmaciones no verificables en la evaluación anterior.",
     "CERRADO", "Cifras corregidas en este informe con los valores medidos (sección 5.1)."),
    ("INC-12", "Revisión de código", "REQ-SEG-01", "El token JWT se guarda en localStorage, accesible desde cualquier script de la página.",
     "frontend/src/context/AuthContext.jsx:30", "MODERADO",
     "Un fallo de XSS permitiría robar la sesión.",
     "ABIERTO", "No se encontraron sinks de XSS (dangerouslySetInnerHTML, innerHTML, eval). Mitigación recomendada: cookie HttpOnly con SameSite y CSRF habilitado."),
    ("INC-13", "Revisión de código", "REQ-SEG-01", "El endpoint de login no limita los intentos de autenticación (no existe rate limiting en el BFF).",
     "bff-gateway/.../AuthController.java", "MODERADO",
     "Permite ataques de fuerza bruta sobre contraseñas.",
     "ABIERTO", "Recomendado: límite por IP y usuario (p. ej. Bucket4j o Resilience4j RateLimiter) y bloqueo temporal."),
    ("INC-15", "CP-18", "REQ-SEG-07", "Los microservicios de negocio responden sin token en sus puertos: inventario (catálogo), pedidos (datos de clientes con nombre y correo) y envíos.",
     "docker-compose.yml (versión base: puertos 8081-8083 publicados) y ausencia de Spring Security en inventory, order y shipping", "CRÍTICO",
     "Cualquier usuario de la red puede leer pedidos con datos personales y crear productos sin pasar por el BFF; el control de acceso del gateway se elude.",
     "MITIGADO (parcial)", "Puertos 8081-8083 dejan de publicarse; el acceso solo es posible dentro de la red de compose. Pendiente: que cada microservicio valide el JWT (defensa en profundidad)."),
    ("INC-16", "CP-19 / CP-07", "REQ-FUNC-04", "El alta de productos falla siempre con HTTP 500: la secuencia de IDs no avanza después de la semilla con IDs explícitos y el INSERT viola la clave primaria.",
     "inventory-service/src/main/resources/data.sql (versión base) y ProductService.createProduct", "GRAVE",
     "No es posible incorporar productos al catálogo; función de administración prioritaria.",
     "CERRADO", "ALTER TABLE product ALTER COLUMN id RESTART WITH 100. Regresión: ProductSeedIdIntegrationTest falla sin la corrección y pasa con ella."),
    ("INC-17", "CP-06", "REQ-FUNC-03", "El BFF no expone los filtros de búsqueda del inventario (marca, fragancia, precio, stock y nombre). Para el cliente, la búsqueda no existe.",
     "bff-gateway/.../controller/ProductController.java (versión base: solo listado, detalle, alta, actualización y stock)", "MODERADO",
     "La búsqueda solo es accesible si se llama directamente al servicio, lo que el control de acceso ya no permite.",
     "CERRADO", "Endpoints de búsqueda en el BFF con codificación segura de segmentos y parámetros (InventoryProxyServiceTest, 3 pruebas)."),
    ("INC-18", "UI-03 (captura)", "REQ-SEG-01", "Un inicio de sesión con credenciales incorrectas no muestra el mensaje de error: la página se recarga, el formulario queda vacío y el usuario no sabe por qué falló.",
     "frontend/src/services/api.js (interceptor): ante HTTP 401 ejecuta window.location.href = '/login', incluso en /api/auth/login", "MODERADO",
     "Mala retroalimentación en el acceso; el usuario puede repetir intentos sin entender el motivo, y el mensaje controlado del BFF nunca llega a la interfaz.",
     "ABIERTO", "Excluir /api/auth/** del redireccionamiento global en el interceptor, para que el formulario reciba el error. Verificable con UI-03."),
    ("INC-14", "Observación visual", "REQ-CAL-01", "La pantalla de inicio se presenta como 'PERFUMERÍA', mientras el título HTML es 'SmartLogix'.",
     "Captura E07 (docs/evidencias/capturas)", "LEVE",
     "Inconsistencia de marca; no afecta la funcionalidad.",
     "ABIERTO", "Unificar el nombre comercial."),
]

# ----------------------------------------------------------------- helpers docx
def fuente(run, nombre="Arial", tam=11, negrita=None, cursiva=None):
    run.font.name = nombre
    run.font.size = Pt(tam)
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for atr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(atr), nombre)
    if negrita is not None:
        run.bold = negrita
    if cursiva is not None:
        run.italic = cursiva


def estilos(doc):
    for nombre, tam, negrita in [("Normal", 11, False), ("Heading 1", 12, True),
                                 ("Heading 2", 12, True), ("Heading 3", 12, True), ("Title", 12, True)]:
        st = doc.styles[nombre]
        st.font.name = "Arial"
        st.font.size = Pt(tam)
        st.font.bold = negrita
        st.font.color.rgb = None
        rpr = st.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        for atr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(atr), "Arial")
        for atr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rf.get(qn(atr)) is not None:
                del rf.attrib[qn(atr)]
    pf = doc.styles["Normal"].paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for h in ("Heading 1", "Heading 2", "Heading 3"):
        doc.styles[h].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        doc.styles[h].paragraph_format.space_before = Pt(12)
        doc.styles[h].paragraph_format.line_spacing = 1.5


def parrafo(doc, texto, negrita_inicio=None, alineado=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = alineado
    if negrita_inicio:
        r = p.add_run(negrita_inicio)
        fuente(r, negrita=True)
    r = p.add_run(texto)
    fuente(r)
    return p


def titulo(doc, texto, nivel=1):
    h = doc.add_heading(level=nivel)
    r = h.add_run(texto)
    fuente(r, tam=12, negrita=True)
    return h


def vinetas(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        if isinstance(it, tuple):
            r = p.add_run(it[0])
            fuente(r, negrita=True)
            r = p.add_run(it[1])
            fuente(r)
        else:
            r = p.add_run(it)
            fuente(r)


def sombrear(celda, color):
    tcpr = celda._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcpr.append(shd)


def tabla(doc, cabecera, filas, anchos=None, tam=9):
    t = doc.add_table(rows=1, cols=len(cabecera))
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(cabecera):
        cel = t.rows[0].cells[i]
        cel.text = ""
        p = cel.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(c)
        fuente(r, tam=tam, negrita=True)
        sombrear(cel, "D9D9D9")
    for fila in filas:
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(v))
            fuente(r, tam=tam)
    if anchos:
        t.autofit = False
        for i, w in enumerate(anchos):
            t.columns[i].width = Cm(w)
        for row in t.rows:
            for i, w in enumerate(anchos):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.line_spacing = 1.0
    return t


def figura(doc, ruta, texto, ancho=15.5):
    if not os.path.exists(ruta):
        parrafo(doc, f"[Falta la captura {os.path.basename(ruta)}]")
        return
    doc.add_picture(ruta, width=Cm(ancho))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(texto)
    fuente(r, tam=9, cursiva=True)


def nueva_seccion(doc, horizontal):
    from docx.enum.section import WD_ORIENT, WD_SECTION
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    ancho, alto = (Cm(21.0), Cm(29.7))
    if horizontal:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = alto, ancho
        sec.left_margin = sec.right_margin = Cm(1.8)
    else:
        sec.orientation = WD_ORIENT.PORTRAIT
        sec.page_width, sec.page_height = ancho, alto
        sec.left_margin = sec.right_margin = Cm(2.5)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    return sec


def sin_partir_filas(tbl):
    """Evita que una fila (imagen + leyenda) se corte entre páginas."""
    for fila in tbl.rows:
        trpr = fila._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trpr.append(cs)


def pie_pagina(doc):
    for sec in doc.sections[:1]:
        p = sec.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("ISY1102 - Informe de seguridad y calidad - SmartLogix - página ")
        fuente(r, tam=8)
        for tipo, txt in (("begin", None), (None, "PAGE"), ("end", None)):
            run = p.add_run()
            fuente(run, tam=8)
            if tipo:
                fc = OxmlElement("w:fldChar")
                fc.set(qn("w:fldCharType"), tipo)
                run._r.append(fc)
            else:
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = txt
                run._r.append(it)


# ----------------------------------------------------------------- documento
def construir():
    doc = Document()
    estilos(doc)
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Cm(2.5)
        sec.top_margin = sec.bottom_margin = Cm(2.5)

    # Portada
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fuente(p.add_run("Informe de seguridad y calidad\nen el desarrollo de software"), tam=20, negrita=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fuente(p.add_run("Caso SmartLogix: plataforma eCommerce de perfumes en microservicios"), tam=12)
    for _ in range(4):
        doc.add_paragraph()
    datos = [
        ("Asignatura: ", "ISY1102 - Seguridad y calidad en el desarrollo de software"),
        ("Evaluación: ", "Encargo 2 (ISY1102)"),
        ("Carrera: ", "[completar]"),
        ("Sección: ", "004V"),
        ("Docente: ", "Manuel Reyes Ferrada"),
        ("Fecha: ", FECHA_TXT),
    ]
    for k, v in datos:
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

    # Índice (campo para actualizar en Word)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fuente(p.add_run("Índice"), tam=12, negrita=True)
    p = doc.add_paragraph()
    run = p.add_run()
    fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "begin"); run._r.append(fc)
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = 'TOC \\o "1-2" \\h \\z \\u'; run._r.append(it)
    fc2 = OxmlElement("w:fldChar"); fc2.set(qn("w:fldCharType"), "separate"); run._r.append(fc2)
    fuente(p.add_run("Clic derecho sobre el índice y 'Actualizar campos' para mostrar la numeración."), cursiva=True, tam=10)
    fc3 = OxmlElement("w:fldChar"); fc3.set(qn("w:fldCharType"), "end"); run._r.append(fc3)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # 1. Introducción
    titulo(doc, "1. Introducción")
    titulo(doc, "1.1 Contexto del software evaluado", 2)
    parrafo(doc, "SmartLogix es un sistema de comercio electrónico de perfumes desarrollado con arquitectura de microservicios. "
            "Está formado por un frontend en React 18 y Vite, un API Gateway (BFF) con autenticación JWT sobre Spring Security, "
            "y tres microservicios independientes en Spring Boot 3.2 y Java 21: Inventory Service (catálogo y stock), Order Service "
            "(pedidos con el patrón Factory Method para los tipos de orden WEB y MARKETPLACE) y Shipping Service (envíos con Circuit "
            "Breaker de Resilience4j). Cada servicio usa su propia base de datos H2 en memoria.")
    titulo(doc, "1.2 Propósito del plan y de las pruebas", 2)
    parrafo(doc, "El plan busca comprobar que el sistema cumple los requisitos funcionales, de seguridad, de rendimiento y de "
            "mantenibilidad que se le exigen, y que lo hace de forma reproducible. Un eCommerce gestiona credenciales, datos personales "
            "(nombre, correo y dirección de envío) y pedidos, por lo que una falla de seguridad tiene consecuencias directas sobre los "
            "usuarios y sobre el cumplimiento de la Ley 19.628 y de su reforma.")
    titulo(doc, "1.3 Origen de los requisitos", 2)
    parrafo(doc, "El caso no dispone de un documento de especificación de requisitos (ERS) con códigos propios. Por ello, los "
            "requisitos de este informe se derivan de tres fuentes, que se indican en la sección 2: los requisitos y criterios del "
            "informe de la Evaluación Parcial 1, el código fuente del proyecto y la normativa aplicable. Los códigos REQ-SEG-01, "
            "REQ-FUNC-02, REQ-FUNC-03, REQ-RES-01 y REQ-VAL-01 provienen de la Ev1; el resto se añadió en esta evaluación a partir "
            "del código y de la normativa. La cobertura del 100 % se entiende respecto de este conjunto de requisitos, no de un ERS oficial.", negrita_inicio="Limitación declarada. ")
    titulo(doc, "1.4 Ajustes a la Evaluación Parcial 1", 2)
    parrafo(doc, "No se dispone de la retroalimentación escrita del docente a la Ev1, por lo que los ajustes se basan en la verificación "
            "contra el código y la ejecución. Se corrigieron las siguientes afirmaciones: la cobertura de la Ev1 (87,4 % backend y "
            "84,1 % frontend) no se reproduce; el reporte de cobertura del frontend registra 68,52 % de statements; las respuestas "
            "sin token eran HTTP 403, no 401; el tipo de orden inválido respondía 404, no 500; y el rango de precio 50-150 del caso "
            "CP-06 no aplica porque los precios se almacenan en unidades enteras.")
    titulo(doc, "1.5 Estructura del informe", 2)
    parrafo(doc, "La sección 2 define los criterios de calidad, seguridad y cumplimiento. La sección 3 presenta el plan de pruebas. "
            "La sección 4 detalla los casos de prueba y la matriz de trazabilidad. La sección 5 registra la ejecución, los "
            "incidentes y su criticidad. Las secciones 6 y 7 contienen el análisis ético y normativo y las conclusiones.")

    # 2. Criterios
    titulo(doc, "2. Criterios de calidad, seguridad y cumplimiento normativo")
    titulo(doc, "2.1 Calidad del software (ISO/IEC 25010)", 2)
    vinetas(doc, [
        ("Funcionalidad: ", "los pedidos, descuentos, envíos y búsquedas deben producir los resultados especificados (REQ-FUNC-02, REQ-FUNC-03, REQ-RES-01)."),
        ("Rendimiento: ", "lecturas con p95 inferior a 500 ms y escrituras con p95 inferior a 1000 ms en condiciones de uso normal (REQ-NFR-01)."),
        ("Fiabilidad: ", "el Circuit Breaker debe activar el fallback ante fallo del carrier sin colapsar el servicio (REQ-RES-01)."),
        ("Mantenibilidad: ", "cobertura de líneas JaCoCo de al menos 60 % en cada servicio y gate de build activo (REQ-CAL-01)."),
        ("Usabilidad y compatibilidad: ", "se consideran en el plan (pruebas de usabilidad y navegadores Chrome, Firefox y Safari), pero no se ejecutaron en esta evaluación; se declara como limitación en la sección 3.3."),
    ])
    titulo(doc, "2.2 Seguridad", 2)
    vinetas(doc, [
        ("Autenticación y control de acceso: ", "los endpoints distintos de /api/auth/** requieren JWT; las credenciales inválidas se rechazan con 401 (REQ-SEG-01)."),
        ("Protección de credenciales: ", "las contraseñas se almacenan como hash BCrypt (REQ-SEG-02)."),
        ("Gestión de secretos: ", "la clave de firma JWT se obtiene de una variable de entorno y no se versiona (REQ-SEG-05)."),
        ("Manejo de errores: ", "las respuestas de error indican el código correcto y no incluyen trazas ni mensajes del framework (REQ-SEG-03)."),
        ("Integridad de entradas: ", "validación con Jakarta Validation y rechazo con HTTP 400 (REQ-VAL-01)."),
        ("Configuración de red: ", "CORS limitado a http://localhost:5173 y http://localhost:3000 (REQ-SEG-04)."),
        ("Dependencias: ", "sin vulnerabilidades críticas ni altas en dependencias; el estado real se reporta en INC-09 (REQ-SEG-06)."),
    ])
    titulo(doc, "2.3 Cumplimiento normativo", 2)
    parrafo(doc, "Ley 19.628 y su reforma (Ley 21.719). La Ley 19.628 rige actualmente. La Ley 21.719 la reforma integralmente y, "
            "según la Biblioteca del Congreso Nacional, entra en vigencia el 1 de diciembre de 2026. El 1 de septiembre de 2026 el "
            "Gobierno propuso postergar esa fecha al 1 de diciembre de 2027. Este informe no puede confirmar el estado de esa "
            "propuesta; debe verificarse en bcn.cl antes de la entrega. Las obligaciones que se analizan en la sección 6 son las "
            "de la ley reformada, porque son las que el sistema deberá cumplir en el mediano plazo.")
    vinetas(doc, [
        ("Principio de seguridad (art. 3 f) y medidas de seguridad (art. 14 quinquies): ", "cifrado o seudonimización, confidencialidad, integridad y resiliencia, y verificación periódica de la eficacia de las medidas."),
        ("Reporte de vulneraciones (art. 14 sexies): ", "comunicación a la Agencia sin dilaciones indebidas cuando exista riesgo razonable para los titulares."),
        ("Derechos del titular (arts. 4 y 9): ", "acceso, rectificación, supresión, oposición, portabilidad y bloqueo."),
        ("OWASP Top 10 (2021): ", "A01 control de acceso, A02 fallas criptográficas, A05 configuración incorrecta, A06 componentes vulnerables, A07 fallas de autenticación."),
        ("Estándares técnicos: ", "Java 21, Spring Boot 3.2, React 18, OpenAPI 3.0 y convenciones REST."),
    ])

    # 3. Plan
    titulo(doc, "3. Plan de pruebas")
    titulo(doc, "3.1 Alcance y objetivos", 2)
    parrafo(doc, "El alcance comprende los cuatro servicios backend (BFF, inventario, pedidos y envíos), el frontend y el despliegue "
            "en contenedores. Quedan fuera la infraestructura de nube, la carga concurrente a escala de producción y las pruebas en "
            "dispositivos móviles.")
    vinetas(doc, [
        "O1. Verificar los requisitos funcionales y de seguridad mediante casos ejecutados sobre el sistema real.",
        "O2. Medir la línea base del código original y el efecto de las mitigaciones con el mismo ejecutor.",
        "O3. Identificar y clasificar incidentes con criticidad y estado de tratamiento.",
        "O4. Dejar el sistema desplegable y las pruebas reproducibles con un único comando.",
    ])
    titulo(doc, "3.2 Estrategia de pruebas", 2)
    parrafo(doc, "El enfoque es mixto. Las pruebas unitarias y de integración son automatizadas (JUnit 5, Mockito y Vitest). Las "
            "pruebas funcionales y de seguridad se ejecutan contra los servicios en ejecución mediante un script reproducible "
            "(docs/pruebas/ejecutar_casos.py). El análisis estático y la auditoría de dependencias son automatizados. La inspección "
            "de código se usa cuando la propiedad a verificar no es observable desde el exterior (almacenamiento de contraseñas y "
            "configuración de secretos).")
    parrafo(doc, "Etapas: (1) línea base con pruebas unitarias y cobertura; (2) análisis estático y SCA; (3) ejecución de casos sobre "
            "el código original; (4) mitigación de incidentes; (5) regresión sobre el mismo ejecutor en contenedores Docker; "
            "(6) documentación de resultados.")
    parrafo(doc, "Priorización: crítica (autenticación y secretos), alta (pedidos, envíos y validación), media (búsqueda, "
            "rendimiento y fallback del Circuit Breaker), baja (cumplimiento documental).")
    parrafo(doc, "Criterios de entrada: build compilado sin errores, servicios desplegados en sus puertos y bases H2 inicializadas. "
            "Criterios de salida: todos los casos críticos y altos aprobados, cobertura de líneas por servicio >= 60 % y ningún "
            "incidente crítico abierto sin tratamiento documentado.")
    titulo(doc, "3.3 Tipos de prueba y justificación", 2)
    tabla(doc, ["Tipo", "Propósito en el aseguramiento de la calidad", "Aplicación en SmartLogix", "Estado"], [
        ["Funcional (caja negra)", "Verificar que cada función produce el resultado especificado.", "CP-03, CP-04, CP-06", "Ejecutada"],
        ["Unitaria (caja blanca)", "Verificar unidades aisladas y su lógica interna.", "112 pruebas JUnit y 55 Vitest", "Ejecutada"],
        ["Integración", "Verificar la comunicación entre BFF y servicios.", "CP-08 y pruebas de proxy", "Ejecutada"],
        ["Seguridad", "Verificar autenticación, autorización, secretos, errores y CORS.", "CP-01, CP-02, CP-07, CP-10 a CP-13", "Ejecutada"],
        ["Resiliencia", "Verificar la recuperación ante fallos de dependencias.", "CP-05 (Circuit Breaker)", "Ejecutada"],
        ["Rendimiento (no funcional)", "Medir tiempos frente a los umbrales definidos.", "CP-09 (20 muestras por operación, sin carga concurrente)", "Ejecutada con limitaciones"],
        ["Mantenibilidad (cobertura)", "Medir la proporción de código verificado por pruebas.", "CP-14 (JaCoCo)", "Ejecutada"],
        ["Análisis estático", "Detectar defectos y vulnerabilidades sin ejecutar el código.", "CP-15 (SpotBugs + FindSecBugs), ESLint", "Ejecutada"],
        ["Composición de software (SCA)", "Detectar vulnerabilidades en dependencias de terceros.", "CP-16 (npm audit)", "Ejecutada"],
        ["Despliegue", "Verificar que el sistema se despliega de forma reproducible.", "CP-17 (Docker, compose)", "Ejecutada"],
        ["Usabilidad", "Evaluar la experiencia de navegación y el feedback visual.", "Solo capturas de inicio (E07)", "No ejecutada en profundidad"],
        ["Compatibilidad de navegadores", "Verificar el funcionamiento en Chrome, Firefox y Safari.", "No realizada (solo Chrome headless)", "No ejecutada"],
    ], anchos=[3.4, 5.6, 5.2, 2.6])
    titulo(doc, "3.4 Criterios de aceptación", 2)
    vinetas(doc, [
        ("Funcional: ", "el resultado observado coincide con el esperado (estado, código HTTP y campos indicados)."),
        ("No funcional: ", "p95 de lectura < 500 ms y de escritura < 1000 ms; cobertura de líneas >= 60 %."),
        ("Seguridad: ", "sin token o con credenciales inválidas, respuesta 401; sin exposición de trazas ni mensajes internos; secreto no literal en el repositorio."),
        ("Reglas de negocio: ", "descuento WEB 5 % (total 190,00) y MARKETPLACE 10 % (total 180,00); envío STANDARD o EXPRESS según el tipo."),
        ("Análisis estático: ", "cero hallazgos de prioridad 1 sin tratamiento documentado."),
    ])
    titulo(doc, "3.5 Herramientas y justificación", 2)
    tabla(doc, ["Herramienta", "Tipo", "Justificación"], [
        ["JUnit 5 y Mockito", "Unitarias e integración (backend)", "Estándar de Spring Boot; permite aislar dependencias."],
        ["Spring MockMvc (standalone)", "Controladores y handlers", "Verifica códigos HTTP y cuerpos de error sin levantar la aplicación completa."],
        ["JaCoCo 0.8.15", "Cobertura (backend)", "Gate de cobertura de líneas en el build (REQ-CAL-01)."],
        ["Vitest 1.6 y React Testing Library", "Unitarias y componentes (frontend)", "Compatible con Vite. Se descartó Vitest 5 porque dejó de reportar cobertura de los servicios (ver nota)."],
        ["SpotBugs 4.8.6 + FindSecBugs 1.13.0", "Análisis estático (backend)", "Detección de patrones de seguridad de Spring y Java (REQ-CAL-02)."],
        ["ESLint 9 + eslint-plugin-security", "Análisis estático (frontend)", "Detecta inyección de objetos y expresiones regulares inseguras."],
        ["npm audit", "SCA (frontend)", "Vulnerabilidades conocidas en dependencias (REQ-SEG-06)."],
        ["Script Python (ejecutar_casos.py)", "Casos funcionales, de seguridad y de rendimiento", "Reproducible, con evidencia JSON y tabla por caso."],
        ["curl y Chrome headless", "Evidencias", "Respuestas HTTP y capturas de Swagger y del frontend."],
        ["Docker y Docker Compose", "Despliegue", "Reproducibilidad del entorno (REQ-DEP-01)."],
        ["Git / GitHub", "Control de versiones", "Trazabilidad de cambios (rama main, commit base 2d7685f)."],
    ], anchos=[4.5, 4.5, 7.8])
    parrafo(doc, "Nota sobre Vitest 5: con @vitest/coverage-v8 5.0.4 y vite 7, las 55 pruebas pasan, pero el informe de cobertura "
            "omite los archivos de servicios (src/services), lo que reduce la cobertura medida de 68,5 % a 51,8 %. Se mantuvo la "
            "versión 1.6 para no alterar la medición de cobertura. Esta decisión deja abierto el INC-09.", negrita_inicio="")
    titulo(doc, "3.6 Recursos (humanos, técnicos y de entorno)", 2)
    tabla(doc, ["Recurso", "Detalle"], [
        ["Humanos", "Tres integrantes del grupo: desarrollo y revisión de pruebas, ejecución manual y revisión de calidad. La defensa es individual."],
        ["Equipo", "MacBook (arm64), macOS. Docker Desktop 29.5.2."],
        ["Software", "JDK 21.0.12 (OpenJDK, Homebrew), Maven 3.9.16, Node 24.15 / npm 11.12, Python 3.14, Google Chrome."],
        ["Entorno de ejecución", "Contenedores Docker: cuatro servicios Spring Boot (puertos 8080 a 8083) y frontend nginx (puerto 5173)."],
        ["Entorno de línea base", "Procesos locales sobre el commit 2d7685f, sin cambios, para comparar."],
        ["Datos de prueba", "Catálogo semilla de 11 perfumes (data.sql). Usuarios de prueba sintéticos; no se usan datos reales de personas."],
    ], anchos=[4.0, 12.8])
    titulo(doc, "3.7 Cronograma", 2)
    parrafo(doc, "El cronograma asigna fechas concretas a cada fase y termina el 10 de octubre de 2026. El estado refleja la "
            "situación real del trabajo al momento de redactar el informe.")
    tabla(doc, ["Fase", "Actividad", "Fechas (2026)", "Estado"], [
        ["F0", "Preparación del entorno y congelamiento de la versión (commit 2d7685f)", "1 al 2 de octubre", "Completada"],
        ["F1", "Línea base: pruebas unitarias, cobertura y ejecución de casos", "3 de octubre", "Completada"],
        ["F2", "Análisis estático (SpotBugs, ESLint) y composición de software (npm audit)", "4 de octubre", "Completada"],
        ["F3", "Mitigación de incidentes y pruebas de regresión", "5 al 7 de octubre", "Completada (INC-09 abierto)"],
        ["F4", "Despliegue en Docker y ejecución final de casos", "8 de octubre", "Completada"],
        ["F5", "Redacción del informe y verificación de cifras contra evidencias", "9 de octubre", "En curso"],
        ["F6", "Preparación de la defensa individual (guion y preguntas probables)", "10 de octubre", "Pendiente"],
    ], anchos=[1.5, 8.3, 3.6, 3.4])

    # 4. Casos (sección horizontal para legibilidad de tablas)
    nueva_seccion(doc, horizontal=True)
    titulo(doc, "4. Diseño de casos de prueba")
    parrafo(doc, f"Se diseñaron {len(FINAL)} casos. Cada uno incluye identificador, descripción, requisito asociado, datos de entrada, "
            "resultado esperado, criterio de aceptación y tipo de prueba. Los resultados esperados se redactaron antes de ejecutar y "
            "se ajustaron solo cuando la ejecución mostró que la especificación previa era incorrecta; en esos casos se indica en "
            "la sección 5.")
    filas = []
    for cid, c in FINAL.items():
        filas.append([cid, c["titulo"], c["requisito"], c["datos_entrada"], c["esperado"], c["criterio"], c["tipo"]])
    tabla(doc, ["ID", "Descripción", "Requisito", "Datos de entrada", "Resultado esperado", "Criterio de aceptación", "Tipo"],
          filas, anchos=[1.4, 3.6, 2.3, 5.2, 4.8, 4.2, 2.6], tam=8)

    titulo(doc, "4.1 Matriz de trazabilidad requisito → caso → incidente", 2)
    incid_por_req = {}
    for inc in INCIDENTES:
        incid_por_req.setdefault(inc[2], []).append(inc[0])
    filas = []
    for codigo, desc, origen, casos, tipo in REQUISITOS:
        estado_base = all(BASE[c]["resultado"] == "PASA" for c in casos)
        estado_fin = all(FINAL[c]["resultado"] == "PASA" for c in casos)
        filas.append([codigo, desc, origen, ", ".join(casos),
                      "PASA" if estado_base else "FALLA",
                      "PASA" if estado_fin else "FALLA",
                      ", ".join(incid_por_req.get(codigo, [])) or "-"])
    tabla(doc, ["Requisito", "Descripción", "Origen", "Casos", "Base", "Final", "Incidentes"], filas,
          anchos=[2.2, 6.5, 4.8, 2.3, 1.6, 1.6, 2.8], tam=8)
    parrafo(doc, f"Cobertura del conjunto declarado: {len(REQUISITOS)} de {len(REQUISITOS)} requisitos tienen al menos un caso "
            "asociado (100 %). Esta cobertura se refiere al conjunto de la sección 1.3 y no a un ERS oficial. "
            "Requisitos sin prueba automatizada: usabilidad y compatibilidad de navegadores (ver sección 3.3).")

    # 5. Ejecución
    titulo(doc, "5. Ejecución de pruebas")
    titulo(doc, "5.1 Resumen de ejecución", 2)
    base_pasa = sum(1 for c in BASE.values() if c["resultado"] == "PASA")
    fin_pasa = sum(1 for c in FINAL.values() if c["resultado"] == "PASA")
    parrafo(doc, f"Casos diseñados: {len(FINAL)}. Casos ejecutados: {len(BASE)} sobre la línea base y {len(FINAL)} sobre la versión final, "
            f"en ambos casos con el mismo ejecutor. Resultados: línea base, {base_pasa} aprobados y {len(BASE) - base_pasa} fallidos; "
            f"versión final, {fin_pasa} aprobados y {len(FINAL) - fin_pasa} fallido. Ningún caso quedó bloqueado ni sin ejecutar. "
            "El caso fallido de la versión final (CP-16) corresponde a un riesgo residual documentado en INC-09.")
    fb = lambda d: d
    tabla(doc, ["Indicador", "Línea base (2d7685f)", "Versión final"], [
        ["Casos aprobados / fallidos", f"{base_pasa} / {len(BASE) - base_pasa}", f"{fin_pasa} / {len(FINAL) - fin_pasa}"],
        ["Pruebas JUnit (backend)", f"{PR_BASE_TOT}", f"{PR_TOT_FINAL} (0 fallos)"],
        ["Pruebas Vitest (frontend)", "55 (0 fallos)", "55 (0 fallos)"],
        ["Cobertura de líneas: inventario", f"{COB_BASE['inventory-service']} %", f"{COB_FINAL['inventory-service']} %"],
        ["Cobertura de líneas: pedidos", f"{COB_BASE['order-service']} %", f"{COB_FINAL['order-service']} %"],
        ["Cobertura de líneas: envíos", f"{COB_BASE['shipping-service']} %", f"{COB_FINAL['shipping-service']} %"],
        ["Cobertura de líneas: BFF", f"{COB_BASE['bff-gateway']} %", f"{COB_FINAL['bff-gateway']} %"],
        ["SpotBugs prioridad 1 (backend)", "1 (CSRF)", f"{sum(v[1] for v in SB_FINAL.values())} (1 riesgo aceptado documentado)"],
        ["npm audit: críticas / altas", "3 / 13", f"{NPM_FINAL['critical']} / {NPM_FINAL['high']}"],
        ["ESLint (frontend, seguridad)", "no ejecutado", f"{ESLINT_TOTAL} avisos (47 no-unused-vars, 8 object-injection, 2 hooks, 1 regex)"],
        ["Despliegue Docker", "no existía", "4 servicios + frontend levantados"],
    ], anchos=[6.0, 4.5, 6.3])
    parrafo(doc, "En el commit original no se generaba el reporte JaCoCo (INC-07); la cobertura de la línea base se midió sobre el "
            "mismo código con el argLine corregido. Los valores finales se leen de target/site/jacoco de cada servicio. "
            "La línea base de la batería de casos usa el mismo ejecutor que la versión final (19 casos).",
            negrita_inicio="Nota de medición. ")
    titulo(doc, "5.2 Detalle de ejecución de casos", 2)
    filas = []
    for cid in FINAL:
        b, f = BASE[cid], FINAL[cid]
        evid = "E04 / E05 / resultados.json"
        filas.append([cid, f["titulo"], etiqueta(b["resultado"]), etiqueta(f["resultado"]), f["fecha"], "Equipo (script)", evid])
    tabla(doc, ["Caso", "Descripción", "Base", "Final", "Fecha", "Responsable", "Evidencia"], filas,
          anchos=[1.4, 8.0, 1.8, 1.8, 2.4, 5.2, 3.2], tam=8)
    parrafo(doc, "Detalle de los casos con diferencia entre línea base y versión final:")
    for cid in FINAL:
        b, f = BASE[cid], FINAL[cid]
        if b["resultado"] != f["resultado"]:
            pasos_fallidos = [p["paso"] for p in b["pasos"] if not p["ok"]]
            detalle = "; ".join(pasos_fallidos[:2]) if pasos_fallidos else b.get("observado", "")
            vinetas(doc, [(f"{cid} ({b['resultado']} → {f['resultado']}): ", detalle[:400])])
    titulo(doc, "5.2.1 Evidencias visuales", 3)
    figura(doc, os.path.join(EVID, "capturas", "E06-swagger-bff.png"),
           "Figura 1. Swagger UI del BFF Gateway (documentación OpenAPI 3.0 generada por springdoc).")
    figura(doc, os.path.join(EVID, "capturas", "E07-frontend-inicio.png"),
           "Figura 2. Pantalla de inicio de sesión del frontend desplegado en Docker (puerto 5173). Ver INC-14.")
    figura(doc, os.path.join(EVID, "capturas", "E08-swagger-inventario.png"),
           "Figura 3. Swagger UI del Inventory Service (puerto 8081).")
    figura(doc, os.path.join(EVID, "capturas", "E04-casos.png"),
           "Figura 4. Resultados de la ejecución final de los 19 casos (docs/evidencias/mitigado-docker/resultados.md).")
    figura(doc, os.path.join(EVID, "capturas", "E05-casos.png"),
           "Figura 5. Resultados de la línea base sobre el código original (commit 2d7685f).")
    figura(doc, os.path.join(EVID, "capturas", "E03-pruebas.png"),
           "Figura 6. Pruebas unitarias y cobertura por servicio.")
    parrafo(doc, "Evidencia textual (respuestas HTTP reales) en docs/evidencias/capturas/E02-curl-seguridad-validacion.txt: "
            "sin token, 401; con token válido, 200; tipo de orden inválido, 400 con mensaje controlado; producto con nombre vacío, 400 "
            "indicando el campo.")

    titulo(doc, "5.2.2 Evidencia del flujo en el navegador", 3)
    parrafo(doc, "Las capturas siguientes se generaron automáticamente con Playwright y Chromium sobre el frontend desplegado en "
            "Docker. Cada una corresponde a un paso del flujo de usuario. El script es docs/informe/generar_evidencia_visual.py.")
    ui = [("UI-01", "Acceso a /catalog sin sesión: la aplicación redirige a /login (REQ-SEG-01)."),
          ("UI-02", "Registro de un usuario nuevo con mensaje de confirmación (REQ-SEG-01)."),
          ("UI-03", "Inicio de sesión con clave incorrecta: el formulario se recarga vacío y no muestra el error (INC-18)."),
          ("UI-04", "Inicio de sesión correcto y llegada a la página principal (REQ-SEG-01)."),
          ("UI-05", "Catálogo con los productos obtenidos a través del BFF y con token (REQ-FUNC-03).")]
    for i in range(0, len(ui), 2):
        tbl = doc.add_table(rows=2, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for k, (codigo, leyenda) in enumerate(ui[i:i + 2]):
            cel = tbl.rows[0].cells[k]
            cel.text = ""
            pic = cel.paragraphs[0]
            pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pic.add_run().add_picture(os.path.join(EVID, "capturas", f"{codigo}-" + {
                "UI-01": "acceso-protegido-redirige-login", "UI-02": "registro-exitoso",
                "UI-03": "credenciales-incorrectas", "UI-04": "inicio-sesion-pagina-principal",
                "UI-05": "catalogo-productos"}[codigo] + ".png"), width=Cm(11.5))
            cap = tbl.rows[1].cells[k]
            cap.text = ""
            cp = cap.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fuente(cp.add_run(f"Figura {codigo}. {leyenda}"), tam=9, cursiva=True)
        sin_partir_filas(tbl)
        doc.add_paragraph().paragraph_format.line_spacing = 1.0

    titulo(doc, "5.2.3 Evidencia por caso de prueba", 3)
    parrafo(doc, f"Cada uno de los {len(FINAL)} casos tiene una tarjeta con sus datos de entrada, el resultado esperado, el criterio de "
            "aceptación y cada verificación ejecutada con su resultado observado. Las tarjetas se generan a partir de "
            "docs/evidencias/mitigado-docker/resultados.json.")
    casos_ids = list(FINAL.keys())
    for i in range(0, len(casos_ids), 2):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for k, cid in enumerate(casos_ids[i:i + 2]):
            cel = tbl.rows[0].cells[k]
            cel.text = ""
            pp = cel.paragraphs[0]
            pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ruta = os.path.join(EVID, "capturas", f"{cid}-tarjeta.png")
            if os.path.exists(ruta):
                pp.add_run().add_picture(ruta, width=Cm(11.8))
        sin_partir_filas(tbl)
        doc.add_paragraph().paragraph_format.line_spacing = 1.0

    titulo(doc, "5.3 Incidentes identificados y criticidad", 2)
    parrafo(doc, "Escala de criticidad, según la plantilla de la asignatura: CRÍTICO (impide el funcionamiento o compromete "
            "credenciales o datos; requiere remediación inmediata), GRAVE (afecta funcionalidades importantes o la cadena de "
            "desarrollo; debe corregirse con urgencia), MODERADO (afecta casos específicos; se corrige en la siguiente iteración) "
            "y LEVE (apariencia o texto).")
    tabla(doc, ["ID", "Caso / origen", "Requisito", "Descripción", "Evidencia (ubicación)", "Criticidad", "Impacto", "Estado", "Tratamiento"],
          [list(i) for i in INCIDENTES],
          anchos=[1.5, 2.3, 2.2, 5.0, 4.0, 2.2, 3.5, 2.2, 4.7], tam=8)
    cnt = {}
    for i in INCIDENTES:
        cnt[i[5]] = cnt.get(i[5], 0) + 1
    abiertos = [i[0] for i in INCIDENTES if i[7].startswith("ABIERTO") or i[7].startswith("RIESGO")]
    parrafo(doc, f"Resumen: {len(INCIDENTES)} incidentes ({', '.join(f'{k}: {v}' for k, v in cnt.items())}). Abiertos o con riesgo "
            f"aceptado: {', '.join(abiertos)}. Los incidentes CRÍTICOS INC-01 e INC-02 están cerrados; INC-02 requiere además rotar el "
            "secreto, porque permanece en el historial del repositorio. INC-15 (CRÍTICO) está mitigado solo en parte: los puertos "
            "ya no se publican, pero los microservicios no validan el token por sí mismos.")

    # 6. Ético y normativo (vuelve a formato vertical)
    nueva_seccion(doc, horizontal=False)
    titulo(doc, "6. Análisis ético y normativo de los resultados")
    titulo(doc, "6.1 Análisis ético", 2)
    vinetas(doc, [
        ("Independencia de la evaluación: ", "el equipo evalúa código propio y redactó los resultados esperados. Para reducir el sesgo, los resultados esperados se fijaron antes de ejecutar y las discrepancias se documentan como incidentes en lugar de corregir la expectativa en silencio."),
        ("Divulgación responsable: ", "las vulnerabilidades se describen con ubicación exacta para permitir su corrección, pero el informe no reproduce el valor del secreto ni contraseñas reales. El valor literal del secreto se registró como 'oculto' en la evidencia."),
        ("Alcance autorizado: ", "todas las pruebas se ejecutaron sobre entornos locales y contenedores propios, sin apuntar a sistemas de terceros, en línea con las instrucciones de la asignatura."),
        ("Honestidad en la medición: ", "los cambios de cobertura que resultaban incómodos (Vitest 5) se reportan igual que los favorables. Un riesgo aceptado (CSRF en INC-08) también se declara, porque ocultarlo en el reporte sería engañoso."),
        ("Responsabilidad sobre los datos: ", "el sistema maneja datos personales; un fallo de confidencialidad afecta a personas que no participaron en el desarrollo. Esto justifica priorizar INC-01 y INC-02."),
    ])
    titulo(doc, "6.2 Análisis normativo", 2)
    vinetas(doc, [
        ("Seguridad de los datos (art. 14 quinquies de la Ley 21.719): ", "las contraseñas en texto plano (INC-01) incumplen el deber de adoptar medidas que aseguren la confidencialidad. La corrección con BCrypt es una medida adecuada, aunque no suficiente por sí sola: falta el cifrado de la base de datos en reposo, que hoy es H2 en memoria."),
        ("Reporte de vulneraciones (art. 14 sexies): ", "si un incidente como INC-01 o INC-02 se hubiera materializado sobre datos reales, el responsable debería reportarlo a la Agencia sin dilaciones indebidas. El sistema actual no cuenta con un procedimiento de respuesta a incidentes ni con registro de vulneraciones."),
        ("Derechos del titular (arts. 4, 9 y 10): ", "no se identificaron endpoints para consultar, rectificar, suprimir u obtener la portabilidad de los datos de un usuario. Se verificó por búsqueda en el código. Es un incumplimiento que debe corregirse antes de un uso real."),
        ("Consentimiento y transparencia: ", "no se identificó en la interfaz un mecanismo de consentimiento para el tratamiento de datos al registrarse. Esto se verificó en el formulario de registro y no fue probado de forma exhaustiva en el navegador."),
        ("Límite de intentos y autenticación robusta (OWASP A07): ", "la ausencia de límites de intentos (INC-13) y el almacenamiento del token en localStorage (INC-12) están fuera de lo que recomiendan OWASP y las buenas prácticas de gestión de sesiones."),
        ("Dependencias (OWASP A06): ", "las vulnerabilidades críticas en herramientas de desarrollo (INC-09) no afectan directamente a los usuarios finales, pero sí a la integridad del proceso de construcción. El riesgo residual debe comunicarse."),
    ])
    parrafo(doc, "Conclusión normativa: el sistema avanza hacia el cumplimiento de la seguridad técnica, pero no cumple todavía con las "
            "obligaciones de derechos del titular, consentimiento ni respuesta a incidentes. Estas brechas se deben cerrar antes de "
            "tratar datos reales de personas.")

    # 7. Conclusiones
    titulo(doc, "7. Conclusiones y recomendaciones")
    parrafo(doc, f"La línea base cumplió {base_pasa} de {len(BASE)} casos; tras las mitigaciones, la versión final cumple {fin_pasa} de {len(FINAL)}. "
            "Las mitigaciones cerraron los incidentes críticos INC-01 (credenciales en claro) e INC-02 (secreto JWT literal), y "
            "corrigieron el manejo de errores, la validación del gateway, el gate de cobertura, el alta de productos y el despliegue. "
            "El acceso directo a los microservicios (INC-15, crítico) se mitigó a nivel de red, pero no a nivel de aplicación. "
            "Los incidentes abiertos restantes son INC-09 (GRAVE), INC-12, INC-13 e INC-18 (MODERADO) e INC-14 (LEVE). INC-18 se "
            "detectó al generar la evidencia visual: el error de login no llega a la interfaz.")
    vinetas(doc, [
        "R1. Rotar el secreto JWT y reescribir el historial de git si el repositorio es público.",
        "R2. Actualizar la cadena de herramientas del frontend (vitest, vite, tailwind) y revalidar la cobertura antes de declarar cerrado INC-09.",
        "R3. Implementar límite de intentos en /api/auth/login (INC-13).",
        "R4. Migrar el token a cookie HttpOnly con SameSite y reactivar la protección CSRF (INC-08, INC-12).",
        "R5. Implementar los endpoints de derechos del titular y un registro de consentimiento (sección 6.2).",
        "R6. Cifrar los datos personales en reposo y reemplazar H2 en memoria por una base persistente antes de un uso real.",
        "R0. Validar el JWT en cada microservicio (filtro compartido) para completar la defensa en profundidad de INC-15.",
        "R7. Incorporar las pruebas de este plan a un pipeline de integración continua (GitHub Actions) que ejecute el script de casos y el análisis estático en cada cambio.",
    ])

    # Anexos
    titulo(doc, "Anexo A. Reproducibilidad")
    parrafo(doc, "Comandos para repetir la evaluación:")
    for c in ["cp .env.example .env   # definir JWT_SECRET",
              "docker compose up -d --build",
              "python3 docs/pruebas/ejecutar_casos.py <etiqueta>",
              "cd <servicio> && mvn -B clean verify   # pruebas y JaCoCo",
              "cd <servicio> && mvn -Psecurity com.github.spotbugs:spotbugs-maven-plugin:4.8.6.6:spotbugs",
              "cd frontend && npx vitest run --coverage && npm audit"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.0
        fuente(p.add_run(c), tam=9)
    titulo(doc, "Anexo B. Cambios realizados al código", 2)
    vinetas(doc, [
        f"bff-gateway: AuthService con BCrypt y excepciones tipadas; GlobalExceptionHandler; SecurityConfig con PasswordEncoder y entry point 401; jwt.secret desde variable de entorno; endpoints de búsqueda en ProductController e InventoryProxyService. Pruebas: {PR_FINAL['bff-gateway']}.",
        f"inventory-service, order-service, shipping-service: ResourceNotFoundException, GlobalExceptionHandler sin mensajes internos, IllegalArgumentException para tipo de orden; corrección de la secuencia de IDs en data.sql. Pruebas: {PR_FINAL['inventory-service']}, {PR_FINAL['order-service']} y {PR_FINAL['shipping-service']}.",
        "Los cuatro pom.xml: argLine corregido, perfil security con SpotBugs y FindSecBugs, filtro de exclusión documentado en el BFF.",
        "frontend: ESLint 9 con reglas de seguridad, npm audit fix sin cambios de versión mayor, Dockerfile y nginx.conf.",
        "Raíz: docker-compose.yml (sin puertos publicados para los microservicios), .env.example, .gitignore (.env), docs/pruebas/ejecutar_casos.py, docs/informe/generar_informe.py.",
    ])

    pie_pagina(doc)
    doc.save(SALIDA)
    print("Informe generado:", SALIDA)


if __name__ == "__main__":
    construir()
