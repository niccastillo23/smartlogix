#!/usr/bin/env python3
"""
Capturas de evidencia del Encargo 3: SonarQube (proyectos y hallazgos), informes OWASP ZAP
y reporte HTML de Playwright. Requiere SonarQube en localhost:9000 y la contraseña en /tmp/sonar-admin-pwd
(fuera del repositorio) o en la variable SONAR_ADMIN_PASSWORD.
Uso: python3 docs/seguridad/capturas_seguridad.py
"""
import os
from playwright.sync_api import sync_playwright

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SAL = os.path.join(RAIZ, "docs", "evidencias", "encargo3")
os.makedirs(SAL, exist_ok=True)
PWD = os.environ.get("SONAR_ADMIN_PASSWORD") or open("/tmp/sonar-admin-pwd").read().strip()


def captura_sonar(pg):
    pg.goto("http://localhost:9000/sessions/new")
    pg.wait_for_timeout(1200)
    pg.fill("#login-input", "admin")
    pg.fill("#password-input", PWD)
    pg.locator("button[type=submit]").click()
    pg.wait_for_timeout(2500)
    pg.goto("http://localhost:9000/dashboard?id=smartlogix-backend")
    pg.wait_for_timeout(4000)
    if pg.get_by_text("Dismiss").count():
        pg.get_by_text("Dismiss").first.click()
    pg.get_by_role("tab", name="Overall Code").click()
    pg.wait_for_timeout(2500)
    pg.screenshot(path=os.path.join(SAL, "S01-sonar-backend.png"))
    pg.goto("http://localhost:9000/project/issues?id=smartlogix-backend&resolved=false")
    pg.wait_for_timeout(3500)
    pg.screenshot(path=os.path.join(SAL, "S02-sonar-issues-backend.png"))
    pg.goto("http://localhost:9000/dashboard?id=smartlogix-frontend")
    pg.wait_for_timeout(4000)
    if pg.get_by_role("tab", name="Overall Code").count():
        pg.get_by_role("tab", name="Overall Code").click()
    pg.wait_for_timeout(2500)
    pg.screenshot(path=os.path.join(SAL, "S03-sonar-frontend.png"))


def captura_zap(pg):
    for etiqueta, nombre in [("main", "Z01-zap-api-base"), ("v2-final", "Z02-zap-api-final")]:
        ruta = os.path.join(RAIZ, "docs", "seguridad", "zap", etiqueta, "api-bff.html")
        if os.path.exists(ruta):
            pg.goto("file://" + ruta)
            pg.wait_for_timeout(1500)
            pg.screenshot(path=os.path.join(SAL, nombre + ".png"), clip={"x": 0, "y": 0, "width": 1280, "height": 900})


def captura_playwright(pg):
    ruta = os.path.join(RAIZ, "e2e", "reports", "html", "index.html")
    if os.path.exists(ruta):
        pg.goto("file://" + ruta)
        pg.wait_for_timeout(1500)
        pg.screenshot(path=os.path.join(SAL, "E01-playwright-reporte.png"))


if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 1000})
        pg = ctx.new_page()
        captura_sonar(pg)
        captura_zap(pg)
        captura_playwright(pg)
        b.close()
    print("capturas en", SAL)
