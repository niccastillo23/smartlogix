# Cómo agregar fotos reales a los perfumes

## Opción 1: Reemplazar los placeholders SVG (Rápido)

Los placeholders SVG ya se generaron. Para poner tus fotos reales:

1. Consigue tus imágenes (fotos de perfumes)
2. Renómbralas según la siguiente tabla
3. Colócalas en `public/images/` (sobrescribiendo los .svg o como .jpg)

### Nombres de archivo esperados

| Perfume | Nombre de archivo |
|---------|------------------|
| Sauvage Eau de Parfum - Dior | `dior-sauvage-eau-de-parfum.jpg` |
| Bleu de Chanel - Chanel | `chanel-bleu-de-chanel.jpg` |
| La Vie Est Belle - Lancôme | `lanc-me-la-vie-est-belle.jpg` |
| Acqua di Gio Profondo - Giorgio Armani | `giorgio-armani-acqua-di-gio-profondo.jpg` |
| Black Orchid - Tom Ford | `tom-ford-black-orchid.jpg` |
| Coco Mademoiselle - Chanel | `chanel-coco-mademoiselle.jpg` |
| Aventus - Creed | `creed-aventus.jpg` |
| Good Girl - Carolina Herrera | `carolina-herrera-good-girl.jpg` |
| 1 Million - Paco Rabanne | `paco-rabanne-1-million.jpg` |
| Flowerbomb - Viktor & Rolf | `viktor-rolf-flowerbomb.jpg` |

### Tamaño recomendado
- **600x600px** (cuadrado, 1:1)
- Formato: **.jpg** (pesan menos)

## Opción 2: Descargar fotos gratis desde internet

Puedes descargar fotos reales de perfumes gratis desde:

### Unsplash (recomendado)
Busca "perfume" o la marca específica:
- https://unsplash.com/s/photos/perfume
- https://unsplash.com/s/photos/dior-perfume
- https://unsplash.com/s/photos/chanel-perfume

### Pexels
- https://www.pexels.com/search/perfume/

### Pasos:
1. Descarga la foto que más te guste
2. Recórtala a 600x600px (puedes usar Preview en Mac)
3. Nómbrala según la tabla de arriba
4. Colócala en `public/images/`
5. Recarga la página

## Opción 3: Script de descarga automática (avanzado)

Si quieres bajar fotos en lote, ejecuta:

```bash
cd frontend
node scripts/download-product-images.mjs
```

*(Este script no existe aún - puedes pedirme que lo genere si tienes URLs de las imágenes que quieres usar)*

## Regenerar placeholders

Si agregas más productos al `data.sql`, regenera los placeholders:

```bash
cd frontend
npm run images
```

## Nota técnica

El sistema primero intenta cargar `.svg` y si falla, muestra el ícono + gradiente. Si pones un `.jpg` con el mismo nombre, el navegador lo cargará automáticamente (Vite sirve archivos estáticos desde `public/` en la raíz).
