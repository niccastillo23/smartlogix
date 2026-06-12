const fs = require("fs");
const path = require("path");

const products = [
  { name: "Sauvage Eau de Parfum", brand: "Dior", frag: "Amaderado" },
  { name: "Bleu de Chanel", brand: "Chanel", frag: "Amaderado Cítrico" },
  { name: "La Vie Est Belle", brand: "Lancôme", frag: "Floral Dulce" },
  { name: "Acqua di Gio Profondo", brand: "Giorgio Armani", frag: "Acuático Fresco" },
  { name: "Black Orchid", brand: "Tom Ford", frag: "Oriental Floral" },
  { name: "Coco Mademoiselle", brand: "Chanel", frag: "Floral Oriental" },
  { name: "Aventus", brand: "Creed", frag: "Frutal Amaderado" },
  { name: "Good Girl", brand: "Carolina Herrera", frag: "Floral Oriental" },
  { name: "1 Million", brand: "Paco Rabanne", frag: "Especiado Dulce" },
  { name: "Flowerbomb", brand: "Viktor & Rolf", frag: "Floral Intenso" },
];

const gradients = {
  "Amaderado": ["#2d1810", "#4a2820"],
  "Amaderado Cítrico": ["#2d4020", "#4a6030"],
  "Floral Dulce": ["#402035", "#603050"],
  "Acuático Fresco": ["#102030", "#204060"],
  "Oriental Floral": ["#302010", "#504030"],
  "Floral Oriental": ["#301020", "#503040"],
  "Frutal Amaderado": ["#201808", "#403020"],
  "Especiado Dulce": ["#2a1510", "#4a2520"],
  "Floral Intenso": ["#201025", "#402040"],
};

const outDir = path.join(__dirname, "..", "public", "images");
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

products.forEach((p) => {
  const slug = p.brand.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
  const nameSlug = p.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").substring(0, 30);
  const filename = `${slug}-${nameSlug}.svg`;
  const g = gradients[p.frag] || ["#1a1a2e", "#2a2a3e"];

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:${g[0]}"/>
      <stop offset="100%" style="stop-color:${g[1]}"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#d4a54a"/>
      <stop offset="100%" style="stop-color:#e8c06a"/>
    </linearGradient>
  </defs>
  <rect width="600" height="600" fill="url(#bg)"/>
  <circle cx="300" cy="300" r="160" fill="none" stroke="url(#gold)" stroke-width="1" opacity="0.3"/>
  <circle cx="300" cy="300" r="120" fill="none" stroke="url(#gold)" stroke-width="0.5" opacity="0.2"/>
  <circle cx="300" cy="200" r="70" fill="url(#gold)" opacity="0.08"/>
  <text x="300" y="310" font-family="'Playfair Display', Georgia, serif" font-size="32" font-weight="700" fill="#d4a54a" text-anchor="middle" dominant-baseline="middle">${p.name}</text>
  <text x="300" y="360" font-family="Arial, sans-serif" font-size="14" font-weight="600" fill="#a09080" text-anchor="middle" letter-spacing="4" dominant-baseline="middle">${p.brand.toUpperCase()}</text>
  <text x="300" y="420" font-family="Georgia, serif" font-size="12" font-style="italic" fill="#6a6662" text-anchor="middle" dominant-baseline="middle">${p.frag}</text>
  <rect x="270" y="270" width="60" height="2" fill="url(#gold)" rx="1" opacity="0.4"/>
</svg>`;

  fs.writeFileSync(path.join(outDir, filename), svg);
  console.log(`✓ ${filename}`);
});

console.log(`\n🎯 Generados ${products.length} placeholders SVG en ${outDir}`);
console.log("📸 Reemplázalos con fotos reales .jpg del mismo nombre");
