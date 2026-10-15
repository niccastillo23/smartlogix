#!/usr/bin/env python3
"""Resume los reportes JSON de OWASP ZAP (baseline del frontend y API del BFF) en Markdown."""
import json, os
from collections import Counter

ZAP = os.path.join(os.path.dirname(__file__), "zap")

def resumen(archivo, titulo):
    d = json.load(open(os.path.join(ZAP, archivo), encoding="utf-8"))
    alertas = []
    for s in d.get("site", []):
        for a in s.get("alerts", []):
            alertas.append((a["riskdesc"].split(" ")[0], a["name"], len(a.get("instances", []))))
    orden = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}
    alertas.sort(key=lambda x: (orden.get(x[0], 9), x[1]))
    lineas = [f"### {titulo}", "", "| Riesgo | Alerta | Instancias |", "|---|---|---|"]
    lineas += [f"| {r} | {n} | {i} |" for r, n, i in alertas]
    return "\n".join(lineas) + "\n"

if __name__ == "__main__":
    salida = ["# Resumen DAST (OWASP ZAP)", "",
              "Escaneo sobre el stack Docker local (solo localhost, en línea con la autorización de la asignatura).", "",
              resumen("baseline-frontend.json", "Baseline del frontend (http://localhost:5173, sin sesión)"), "",
              resumen("api-bff.json", "Escaneo de la API del BFF (OpenAPI, con token válido inyectado)")]
    open(os.path.join(os.path.dirname(__file__), "resumen-dast.md"), "w", encoding="utf-8").write("\n".join(salida))
    print("resumen-dast.md generado")
