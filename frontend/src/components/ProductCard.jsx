import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { formatPrice } from "../utils/formatPrice";
import { getGradient, getIcon, getProductImageBase } from "../utils/productImages";

const EXTENSIONS = [".webp", ".jpg", ".svg"];

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  show: (i) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94], delay: i * 0.08 },
  }),
};

function ProductCard({ product, index = 0, onAddToCart }) {
  const { id, name, brand, price, fragrance, stockQuantity } = product;
  const [imgSrc, setImgSrc] = useState(null);
  const [loadError, setLoadError] = useState(false);
  const [extIndex, setExtIndex] = useState(0);
  const [added, setAdded] = useState(false);
  const basePath = getProductImageBase(product);

  useEffect(() => {
    setExtIndex(0);
    setLoadError(false);
    setImgSrc(null);
  }, [id]);

  useEffect(() => {
    if (extIndex < EXTENSIONS.length) {
      setImgSrc(basePath + EXTENSIONS[extIndex]);
    } else {
      setLoadError(true);
    }
  }, [extIndex, basePath]);

  const handleImgError = () => setExtIndex((p) => p + 1);

  const handleAdd = () => {
    onAddToCart(product);
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };

  return (
    <motion.div
      custom={index}
      variants={cardVariants}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-50px" }}
      className="group bg-white dark:bg-charcoal-800 border border-ivory-100 dark:border-charcoal-700 overflow-hidden card-hover"
    >
      <div
        className="relative aspect-square overflow-hidden"
        style={{ background: getGradient(fragrance) }}
      >
        {imgSrc && !loadError && (
          <motion.img
            key={imgSrc}
            src={imgSrc}
            alt={name}
            className="w-full h-full object-cover"
            onError={handleImgError}
          />
        )}
        {loadError && (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-5xl">{getIcon(fragrance)}</span>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleAdd}
          disabled={stockQuantity === 0}
          className={`absolute bottom-4 left-4 right-4 py-3 text-xs tracking-[0.15em] uppercase font-medium transition-all duration-500 ${
            added
              ? "bg-emerald-600 text-white"
              : stockQuantity === 0
              ? "bg-charcoal-200 text-charcoal-400 cursor-not-allowed"
              : "bg-white/90 dark:bg-charcoal-900/90 text-charcoal-800 dark:text-cream-50 hover:bg-white dark:hover:bg-charcoal-900 backdrop-blur-sm opacity-0 group-hover:opacity-100"
          }`}
        >
          {added ? "✓ Agregado" : stockQuantity === 0 ? "Sin Stock" : "Agregar al Carrito"}
        </motion.button>
      </div>

      <div className="p-5">
        <p className="text-gold-600 dark:text-gold-400 text-[10px] tracking-[0.2em] uppercase font-medium mb-1">{brand}</p>
        <h3 className="font-display text-lg font-semibold text-charcoal-800 dark:text-cream-50 leading-tight mb-1">{name}</h3>
        {fragrance && <p className="text-charcoal-400 dark:text-charcoal-400 text-xs italic mb-3">{fragrance}</p>}
        <div className="flex items-center justify-between pt-3 border-t border-ivory-100 dark:border-charcoal-700">
          <span className="font-display text-xl font-bold text-charcoal-800 dark:text-cream-50">{formatPrice(price)}</span>
          <span className={`text-[10px] tracking-wider uppercase font-medium px-3 py-1 ${
            stockQuantity > 0 ? "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30" : "text-rose-500 dark:text-rose-400 bg-rose-50 dark:bg-rose-900/30"
          }`}>
            {stockQuantity > 0 ? `${stockQuantity} und.` : "Agotado"}
          </span>
        </div>
      </div>
    </motion.div>
  );
}

export default ProductCard;
