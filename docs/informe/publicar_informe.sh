#!/bin/bash
# Pipeline de publicación del informe (Encargo 2):
#  1) regenera el .docx desde las evidencias,
#  2) actualiza el índice (campo TOC) con Microsoft Word,
#  3) exporta el PDF definitivo.
# Requiere Microsoft Word instalado (macOS).
set -e
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
DOCX="$RAIZ/docs/informe/Informe_EP3_ISY1102_SmartLogix.docx"
PDF="$RAIZ/docs/informe/Informe_EP3_ISY1102_SmartLogix.pdf"
python3 "$RAIZ/docs/informe/generar_informe.py"
osascript -e 'tell application "Microsoft Word" to close every document saving no' >/dev/null 2>&1 || true
osascript <<OSA
tell application "Microsoft Word"
  open POSIX file "$DOCX"
  delay 4
  update table of contents of table of contents 1 of active document
  save active document
  save as active document file name POSIX file "$PDF" file format format PDF
  close active document saving no
end tell
OSA
echo "Publicado: $DOCX y $PDF"
