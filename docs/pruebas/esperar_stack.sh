#!/bin/bash
# Espera a que el stack esté listo de extremo a extremo antes de ejecutar pruebas:
# registra un usuario de prueba en el BFF y consulta el catálogo (lo que exige que los microservicios respondan).
# Uso: ./docs/pruebas/esperar_stack.sh [segundos_maximos]
MAX=${1:-240}
for i in $(seq 1 "$MAX"); do
  TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/register -H 'Content-Type: application/json' \
    -d "{\"username\":\"ready$(date +%s%N)\",\"password\":\"pass12345\"}" 2>/dev/null | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("token",""))
except Exception: print("")' 2>/dev/null)
  if [ -n "$TOKEN" ]; then
    CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/products -H "Authorization: Bearer $TOKEN")
    FRONT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
    if [ "$CODE" = "200" ] && [ "$FRONT" = "200" ]; then
      echo "stack listo tras ${i}s (catálogo HTTP $CODE, frontend HTTP $FRONT)"
      exit 0
    fi
  fi
  sleep 1
done
echo "el stack no está listo tras ${MAX}s" >&2
exit 1
