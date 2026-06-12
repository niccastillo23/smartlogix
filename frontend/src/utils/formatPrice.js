export function formatPrice(price) {
  const num = Number(price);
  if (isNaN(num)) return '$0';
  return '$' + Math.round(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}
