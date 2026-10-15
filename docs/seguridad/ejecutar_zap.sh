#!/bin/bash
# DAST con OWASP ZAP (imagen oficial) contra el stack Docker local.
# Uso: ./ejecutar_zap.sh <etiqueta>   -> resultados en docs/seguridad/zap/<etiqueta>/
# Solo localhost: el stack propio, según la autorización de la asignatura.
set -e
ETIQUETA="${1:?Indique una etiqueta, p. ej. v2}"
DIR="$(cd "$(dirname "$0")" && pwd)/zap/$ETIQUETA"
mkdir -p "$DIR"
ZAP_IMG=ghcr.io/zaproxy/zaproxy:stable
# Token válido para cubrir los endpoints protegidos (no se guarda en disco).
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/register -H 'Content-Type: application/json' \
  -d "{\"username\":\"zap$(date +%s)\",\"password\":\"pass12345\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
docker run --rm --add-host=host.docker.internal:host-gateway -v "$DIR":/zap/wrk/:rw $ZAP_IMG \
  zap-baseline.py -t http://host.docker.internal:5173/ -r baseline-frontend.html -J baseline-frontend.json -I -m 3 > "$DIR/baseline-frontend.log" 2>&1 || true
docker run --rm --add-host=host.docker.internal:host-gateway -v "$DIR":/zap/wrk/:rw $ZAP_IMG \
  zap-api-scan.py -t http://host.docker.internal:8080/v3/api-docs -f openapi -r api-bff.html -J api-bff.json -I -m 3 \
  -z "-config replacer.full_list(0).description=auth -config replacer.full_list(0).enabled=true -config replacer.full_list(0).matchtype=REQ_HEADER -config replacer.full_list(0).matchstr=Authorization -config replacer.full_list(0).replacement=Bearer\ $TOKEN" > "$DIR/api-bff.log" 2>&1 || true
# Comprobación: el token no debe aparecer en la evidencia.
if grep -rq "$TOKEN" "$DIR"; then echo "ERROR: token en la evidencia"; exit 1; fi
echo "ZAP $ETIQUETA listo en $DIR"
