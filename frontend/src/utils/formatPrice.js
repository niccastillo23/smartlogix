export function formatPrice(price) {
  const num = Number(price);
  if (Number.isNaN(num)) return '$0';
  // es-CL usa el punto como separador de miles (p. ej. 89990 -> 89.990) sin expresiones regulares.
  return '$' + Math.round(num).toLocaleString('es-CL');
}
