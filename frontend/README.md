# SmartLogix - Frontend

Frontend React para el eCommerce de perfumes SmartLogix. Diseño premium con Tailwind CSS + Framer Motion.

## Tecnologías
- React 18
- Vite
- Axios
- React Router DOM
- Tailwind CSS (diseño)
- Framer Motion (animaciones)
- Vitest + React Testing Library

## Diseño

Paleta de colores monocromática con detalles dorados. Tipografía: Playfair Display (títulos) + Inter (cuerpo).

| Color | Uso |
|-------|-----|
| Charcoal (#1a1a1a → #f5f5f5) | Textos y fondos |
| Ivory (#fdfcfa → #e0d4b8) | Fondos de cards y bordes |
| Gold (#d4a54a → #e8c56a) | Detalles y acentos premium |
| Rose (#e05074 → #f4a9b8) | Errores y advertencias |

## Componentes

| Componente | Descripción | Animación |
|-----------|-------------|-----------|
| `Hero` | Banner minimalista con gradiente oscuro | Fade-in + slide-up |
| `Header` | Navbar translúcido con scroll | Sticky + backdrop blur |
| `ProductCard` | Card de perfume con imagen y precio | Stagger grid + hover scale |
| `CartDrawer` | Panel lateral deslizable | Slide-in-right desde la derecha |
| `OrderForm` | Modal de checkout | Scale-in + backdrop blur |
| `OrderStatus` | Timeline de seguimiento de pedidos | Progress bar animada |
| `ShipmentTracking` | Estado de envío con indicador de Circuit Breaker | Timeline dots |

## Instalar y Ejecutar

```bash
npm install
npm run dev
```

- App: http://localhost:5173

## Generar imágenes placeholder

```bash
npm run images
```

## Tests

```bash
npm test                # 50 tests unitarios
npm run test:coverage   # + reporte de cobertura
open coverage/index.html
```
