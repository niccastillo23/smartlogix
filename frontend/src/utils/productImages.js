const gradientMap = {
  'Amaderado': ['#2d1810', '#4a2820', '#6b3a2f'],
  'Amaderado Cítrico': ['#2d4020', '#4a6030', '#6b8040'],
  'Floral Dulce': ['#402035', '#603050', '#80406b'],
  'Acuático Fresco': ['#102030', '#204060', '#306080'],
  'Oriental Floral': ['#302010', '#504030', '#705040'],
  'Floral Oriental': ['#301020', '#503040', '#704060'],
  'Frutal Amaderado': ['#201808', '#403020', '#604838'],
  'Especiado Dulce': ['#2a1510', '#4a2520', '#6a3530'],
  'Floral Intenso': ['#201025', '#402040', '#603060'],
  'default': ['#1a1a2e', '#2a2a3e', '#3a3a4e'],
};

const fragranceIcons = {
  'Amaderado': '🪵',
  'Amaderado Cítrico': '🍊',
  'Floral Dulce': '🌸',
  'Acuático Fresco': '🌊',
  'Oriental Floral': '🌙',
  'Floral Oriental': '🪷',
  'Frutal Amaderado': '🍎',
  'Especiado Dulce': '🌶️',
  'Floral Intenso': '🌹',
  'default': '✨',
};

export function getGradient(fragrance) {
  const colors = gradientMap[fragrance] || gradientMap.default;
  return `linear-gradient(135deg, ${colors[0]}, ${colors[1]}, ${colors[2]})`;
}

export function getIcon(fragrance) {
  return fragranceIcons[fragrance] || fragranceIcons.default;
}

export function getProductImageBase(product) {
  const slug = product.brand.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  const nameSlug = product.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '').substring(0, 30);
  return `/images/${slug}-${nameSlug}`;
}
