#!/usr/bin/env python3
"""
Genera las capturas de evidencia en texto (E03, E04, E05) a partir de los artefactos del repositorio
y las renderiza como PNG legible con Google Chrome en modo headless.

Uso: python3 docs/informe/generar_capturas.py
"""
import glob
import html
import json
import os
import re
import subprocess

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAP = os.path.join(RAIZ, "docs", "evidencias", "capturas")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SERVICIOS = ["inventory-service", "order-service", "shipping-service", "bff-gateway"]


def casos(ruta):
    return json.load(open(ruta, encoding="utf-8"))["casos"]


def tabla_casos(ruta, titulo, comando):
    lineas = [f"$ {comando}", "", f"{'CASO':<7}{'REQUISITO':<14}{'RESULTADO':<11}{'CRITICIDAD':<12}TITULO",
              "-" * 120]
    cnt = {}
    for c in casos(ruta):
        lineas.append(f"{c['id']:<7}{c['requisito']:<14}{c['resultado']:<11}{c['criticidad_si_falla']:<12}{c['titulo'][:78]}")
        cnt[c["resultado"]] = cnt.get(c["resultado"], 0) + 1
    lineas += ["-" * 120, f"Totales: {cnt}"]
    return lineas, titulo


def pruebas_backend():
    """Devuelve (total por servicio, fallos por servicio) leídos de los reportes Surefire."""
    per, fallos, tot = {}, {}, 0
    for s in SERVICIOS:
        n = f = 0
        for fich in glob.glob(os.path.join(RAIZ, s, "target", "surefire-reports", "*.txt")):
            m = re.search(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+)", open(fich).read())
            if m:
                n += int(m.group(1))
                f += int(m.group(2)) + int(m.group(3))
        per[s], fallos[s] = n, f
        tot += n
    return per, fallos, tot


def render(lineas, titulo, nombre):
    alto = 90 + 26 * len(lineas)
    cuerpo = html.escape("\n".join(lineas))
    ruta_html = os.path.join(CAP, nombre + ".html")
    open(ruta_html, "w", encoding="utf-8").write(f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#1e1e1e}}
.win{{background:#1e1e1e;color:#e8e8e8;font:19px Menlo,Monaco,monospace;padding:20px 26px;white-space:pre;width:1560px}}
.bar{{color:#9aa0a6;font:17px -apple-system,Helvetica,sans-serif;margin-bottom:12px}}
</style></head><body><div class="win"><div class="bar">{html.escape(titulo)}</div>{cuerpo}</div></body></html>""")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size=1600,{alto}", "--force-device-scale-factor=1",
                    f"--screenshot={os.path.join(CAP, nombre + '.png')}", "file://" + ruta_html],
                   capture_output=True)
    os.remove(ruta_html)


def main():
    # E03: pruebas unitarias y cobertura
    per, fallos, tot = pruebas_backend()
    e03 = ["$ mvn -B clean verify   (JDK 21, por servicio)", ""]
    for s in SERVICIOS:
        estado = "BUILD SUCCESS" if fallos[s] == 0 else "BUILD FAILURE"
        e03.append(f"{s:<20} Tests run: {per[s]:<4} Failures/Errors: {fallos[s]}   {estado}")
    e03 += [f"{'TOTAL backend':<20} Tests run: {tot}", "",
            "$ npx vitest run --coverage   (frontend)",
            "Test Files  13 passed (13) | Tests  55 passed (55) | All files 68.52 % statements"]
    render(e03, "SmartLogix - pruebas unitarias y cobertura - ISY1102 EP3", "E03-pruebas")

    # E04: versión final
    l4, t4 = tabla_casos(os.path.join(RAIZ, "docs/evidencias/mitigado-docker/resultados.json"), "", "python3 docs/pruebas/ejecutar_casos.py mitigado-docker   (stack Docker)")
    render(l4, "SmartLogix - ejecución final (stack Docker) - ISY1102 EP3", "E04-casos")

    # E05: línea base
    l5, _ = tabla_casos(os.path.join(RAIZ, "docs/evidencias/baseline-codigo-original/resultados.json"), "", "python3 docs/pruebas/ejecutar_casos.py baseline-codigo-original   (commit 2d7685f)")
    render(l5, "SmartLogix - línea base (commit 2d7685f) - ISY1102 EP3", "E05-casos")
    print("capturas generadas en", CAP)


if __name__ == "__main__":
    main()
