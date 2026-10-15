#!/usr/bin/env python3
"""
Genera la evidencia visual de la ejecución:
  1) Capturas del flujo real en el navegador (Playwright + Chromium) sobre el frontend desplegado:
     login, registro, acceso protegido, catálogo y error de credenciales.
  2) Una tarjeta PNG por cada caso de prueba (CP-01 a CP-19), a partir de docs/evidencias/mitigado-docker/resultados.json.

Requisitos: el stack Docker en ejecución (frontend en 5173, BFF en 8080) y Playwright con Chromium.
Uso: python3 docs/informe/generar_evidencia_visual.py
"""
import html
import json
import os
import time

from playwright.sync_api import sync_playwright

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAP = os.path.join(RAIZ, "docs", "evidencias", "capturas")
RESULTADOS = os.path.join(RAIZ, "docs", "evidencias", os.environ.get("ETIQUETA_RESULTADOS", "v2-encargo3"), "resultados.json")
FRONT = "http://localhost:5173"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def flujo_navegador():
    usuario = f"ui{int(time.time())}"
    clave = "pass12345"
    rutas = {}
    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
        pg = ctx.new_page()

        # UI-01: acceso protegido sin sesión -> redirección a login
        pg.goto(f"{FRONT}/catalog")
        pg.wait_for_url("**/login", timeout=15000)
        pg.wait_for_timeout(800)
        rutas["UI-01"] = os.path.join(CAP, "UI-01-acceso-protegido-redirige-login.png")
        pg.screenshot(path=rutas["UI-01"])

        # UI-02: registro de usuario nuevo
        pg.get_by_role("button", name="Registrarse").last.click()
        pg.fill("#username", usuario)
        pg.fill("#password", clave)
        pg.locator("button[type=submit]").click()
        pg.get_by_text("Registro exitoso").wait_for(timeout=15000)
        rutas["UI-02"] = os.path.join(CAP, "UI-02-registro-exitoso.png")
        pg.screenshot(path=rutas["UI-02"])

        # UI-03: credenciales incorrectas
        pg.fill("#username", usuario)
        pg.fill("#password", "clave-incorrecta")
        pg.locator("button[type=submit]").click()
        pg.wait_for_timeout(1500)
        rutas["UI-03"] = os.path.join(CAP, "UI-03-credenciales-incorrectas.png")
        pg.screenshot(path=rutas["UI-03"])

        # UI-04: inicio de sesión correcto y llegada a la página principal
        pg.fill("#username", usuario)
        pg.fill("#password", clave)
        pg.locator("button[type=submit]").click()
        pg.wait_for_url(f"{FRONT}/", timeout=15000)
        pg.wait_for_timeout(1200)
        rutas["UI-04"] = os.path.join(CAP, "UI-04-inicio-sesion-pagina-principal.png")
        pg.screenshot(path=rutas["UI-04"])

        # UI-05: catálogo con productos cargados desde el BFF (token en localStorage)
        pg.goto(f"{FRONT}/catalog")
        pg.get_by_text("Nuestra Colección").wait_for(timeout=15000)
        pg.wait_for_timeout(1500)
        rutas["UI-05"] = os.path.join(CAP, "UI-05-catalogo-productos.png")
        pg.screenshot(path=rutas["UI-05"])

        # UI-06: tras cinco intentos fallidos, el sexto (con la clave correcta) muestra el bloqueo temporal
        otro = usuario + "x"
        pg.goto(f"{FRONT}/login")
        pg.get_by_role("button", name="Registrarse").last.click()
        pg.fill("#username", otro)
        pg.fill("#password", clave)
        pg.locator("button[type=submit]").click()
        pg.get_by_text("Registro exitoso").wait_for(timeout=15000)
        for _ in range(5):
            pg.fill("#username", otro)
            pg.fill("#password", "clave-incorrecta")
            pg.locator("button[type=submit]").click()
            pg.wait_for_timeout(900)
        pg.fill("#username", otro)
        pg.fill("#password", clave)
        pg.locator("button[type=submit]").click()
        pg.get_by_text("Demasiados intentos").wait_for(timeout=15000)
        pg.wait_for_timeout(500)
        rutas["UI-06"] = os.path.join(CAP, "UI-06-bloqueo-tras-intentos-fallidos.png")
        pg.screenshot(path=rutas["UI-06"])

        nav.close()
    return rutas


def tarjeta(caso, _unused):
    filas = []
    for paso in caso["pasos"]:
        marca = "OK" if paso["ok"] else "NO"
        color = "#1b7f3b" if paso["ok"] else "#b3261e"
        detalle = html.escape((paso.get("detalle") or "")[:150])
        filas.append(f'<tr><td style="color:{color};font-weight:bold;width:40px">{marca}</td>'
                     f'<td>{html.escape(paso["paso"][:190])}</td></tr>'
                     f'<tr><td></td><td class="det">{detalle}</td></tr>')
    if not caso["pasos"]:
        filas.append(f'<tr><td></td><td>{html.escape(caso.get("observado", ""))}</td></tr>')
    color_res = "#1b7f3b" if caso["resultado"] == "PASA" else "#b3261e"
    cuerpo = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#fff;font:15px Arial,Helvetica,sans-serif;color:#222}}
.card{{width:1240px;padding:22px 26px;border:2px solid #444}}
.head{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #aaa;padding-bottom:8px}}
.id{{font-size:24px;font-weight:bold}} .res{{font-size:22px;font-weight:bold;color:{color_res}}}
.meta td{{padding:3px 8px 3px 0;vertical-align:top}} .meta td:first-child{{font-weight:bold;width:150px}}
table{{border-collapse:collapse;width:100%;margin-top:8px}} td{{padding:3px 6px;vertical-align:top}}
.det{{color:#555;font:13px Menlo,monospace;overflow-wrap:anywhere;white-space:normal}}
table{{table-layout:fixed}}
.foot{{margin-top:10px;color:#777;font-size:12px}}
</style></head><body><div class="card">
<div class="head"><div class="id">{caso['id']} - {html.escape(caso['titulo'])}</div><div class="res">{caso['resultado']}</div></div>
<table class="meta">
<tr><td>Requisito</td><td>{caso['requisito']}</td></tr>
<tr><td>Tipo de prueba</td><td>{html.escape(caso['tipo'])}</td></tr>
<tr><td>Datos de entrada</td><td>{html.escape(caso.get('datos_entrada', ''))}</td></tr>
<tr><td>Resultado esperado</td><td>{html.escape(caso['esperado'])}</td></tr>
<tr><td>Criterio de aceptación</td><td>{html.escape(caso['criterio'])}</td></tr>
<tr><td>Criticidad si falla</td><td>{caso['criticidad_si_falla']}</td></tr>
</table>
<div style="margin-top:12px;font-weight:bold">Verificaciones ejecutadas</div>
<table>{''.join(filas)}</table>
<div class="foot">Ejecutado: {caso.get('fecha', '')} · Responsable: {html.escape(caso.get('responsable', ''))}</div>
</div></body></html>"""
    return cuerpo


def tarjetas(casos):
    """Renderiza cada tarjeta con Chromium y captura solo el bloque de contenido (sin espacio sobrante)."""
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1300, "height": 900}, device_scale_factor=1)
        for c in casos:
            pg.set_content(tarjeta(c, None))
            pg.locator(".card").screenshot(path=os.path.join(CAP, f"{c['id']}-tarjeta.png"))
        nav.close()


def main():
    os.makedirs(CAP, exist_ok=True)
    rutas = flujo_navegador()
    print("capturas de navegador:", len(rutas))
    # Los flujos que fallaban en la base (INC-18) se capturan tal como quedan en esta versión.
    casos = json.load(open(RESULTADOS, encoding="utf-8"))["casos"]
    tarjetas(casos)
    print("tarjetas de casos:", len(casos))


if __name__ == "__main__":
    main()
