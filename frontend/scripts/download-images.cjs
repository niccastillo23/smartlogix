const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");

const images = [
  {
    url: "https://cosmetic.cl/cdn/shop/products/2_8e76edfd-0c1b-43d1-8189-96b61838b706_1024x.jpg?v=1629320524",
    name: "carolina-herrera-good-girl",
  },
  {
    url: "https://http2.mlstatic.com/D_NQ_NP_869150-MLA47620519703_092021-O.webp",
    name: "chanel-bleu-de-chanel",
  },
  {
    url: "https://media.falabella.com/falabellaCL/6381793_1/public?wid=200&hei=200&qlt=70&fmt=webp",
    name: "chanel-coco-mademoiselle",
  },
  {
    url: "https://www.santiagoperfumes.cl/wp-content/uploads/2021/03/CREED-AVENTUS-2.jpeg.webp",
    name: "creed-aventus",
  },
  {
    url: "https://http2.mlstatic.com/D_Q_NP_998669-MLB50122440560_052022-O.webp",
    name: "dior-sauvage-eau-de-parfum",
  },
  {
    url: "https://yauras.cl/cdn/shop/files/CarolinaHerrera212men100mledtHombre_32_6cf59e1c-df6b-4e62-a92a-3c4008f1f8c5_700x700.jpg?v=1776466336",
    name: "giorgio-armani-acqua-di-gio-profondo",
  },
  {
    url: "https://fimgs.net/mdimg/perfume/o.14982.jpg",
    name: "lanc-me-la-vie-est-belle",
  },
  {
    url: "https://static.sweetcare.com/img/prd/488/v-638200525104736210/paco-rabanne-005025pc_01.webp",
    name: "paco-rabanne-1-million",
  },
  {
    url: "https://dperfumes.cl/wp-content/uploads/2023/12/black-orchid-parfum-100-ml-tom-ford.jpg",
    name: "tom-ford-black-orchid",
  },
  {
    url: "https://yauras.cl/cdn/shop/files/RaveNowWhite100MlEdp_44_700x700.jpg?v=1777315123",
    name: "viktor-rolf-flowerbomb",
  },
];

const outDir = path.join(__dirname, "..", "public", "images");
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith("https") ? https : http;
    client
      .get(url, { headers: { "User-Agent": "Mozilla/5.0" } }, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          download(res.headers.location, dest).then(resolve).catch(reject);
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`Status ${res.statusCode} for ${url}`));
          return;
        }
        const ext = path.extname(dest);
        const finalDest = ext ? dest : dest + ".webp";
        const file = fs.createWriteStream(finalDest);
        res.pipe(file);
        file.on("finish", () => {
          file.close();
          console.log(`✓ ${path.basename(finalDest)}`);
          resolve(finalDest);
        });
        file.on("error", reject);
      })
      .on("error", reject);
  });
}

async function main() {
  console.log("Descargando imágenes de perfumes...\n");
  for (const img of images) {
    try {
      const ext = path.extname(new URL(img.url).pathname).split("?")[0] || ".jpg";
      if (ext.includes("jpeg")) {
        await download(img.url, path.join(outDir, `${img.name}.jpg`));
      } else {
        await download(img.url, path.join(outDir, `${img.name}${ext}`));
      }
    } catch (err) {
      console.error(`✗ ${img.name}: ${err.message}`);
    }
  }
  console.log("\n✅ Todas las imágenes descargadas en public/images/");
}

main();
