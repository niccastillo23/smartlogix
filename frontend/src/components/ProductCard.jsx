import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { formatPrice } from "../utils/formatPrice";
import { getGradient, getIcon, getProductImageBase } from "../utils/productImages";
import { LiquidButton } from "./ui/liquid-glass-button";

const EXTENSIONS = [".png", ".webp", ".jpg", ".svg"];

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
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [extIndex, setExtIndex] = useState(0);
  const [added, setAdded] = useState(false);
  const basePath = getProductImageBase(product);

  useEffect(() => {
    setExtIndex(0);
    setLoadError(false);
    setLoaded(false);
    setImgSrc(null);
  }, [id]);

  useEffect(() => {
    if (extIndex < EXTENSIONS.length) {
      setLoaded(false);
      setImgSrc(basePath + EXTENSIONS[extIndex]);
    } else {
      setLoadError(true);
    }
  }, [extIndex, basePath]);

  const handleImgError = () => {
    setLoaded(false);
    setExtIndex((p) => p + 1);
  };

  const handleImgLoad = () => {
    setLoaded(true);
  };

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
        className={`aspect-square overflow-hidden ${
          loadError ? "" : "bg-ivory-50 dark:bg-charcoal-800"
        }`}
        style={loadError ? { background: getGradient(fragrance) } : {}}
      >
        {imgSrc && !loadError && (
          <img
            src={imgSrc}
            alt={name}
            className={`w-full h-full object-cover transition-opacity duration-500 ${loaded ? "opacity-100" : "opacity-0"}`}
            onError={handleImgError}
            onLoad={handleImgLoad}
          />
        )}
        {loadError && (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-5xl">{getIcon(fragrance)}</span>
          </div>
        )}
      </div>

      <div className="p-5 flex flex-col gap-3">
        <div>
          <p className="text-gold-600 dark:text-gold-400 text-[10px] tracking-[0.2em] uppercase font-medium mb-1">{brand}</p>
          <h3 className="font-display text-lg font-semibold text-charcoal-800 dark:text-cream-50 leading-tight mb-1">{name}</h3>
          {fragrance && <p className="text-charcoal-400 dark:text-charcoal-400 text-xs italic">{fragrance}</p>}
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-ivory-100 dark:border-charcoal-700">
          <span className="font-display text-xl font-bold text-charcoal-800 dark:text-cream-50">{formatPrice(price)}</span>
          <span className={`text-[10px] tracking-wider uppercase font-medium px-3 py-1 ${
            stockQuantity > 0 ? "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30" : "text-rose-500 dark:text-rose-400 bg-rose-50 dark:bg-rose-900/30"
          }`}>
            {stockQuantity > 0 ? `${stockQuantity} und.` : "Agotado"}
          </span>
        </div>

        <LiquidButton
          onClick={handleAdd}
          disabled={stockQuantity === 0}
          variant="default"
          size="sm"
          className={`w-full !text-xs !py-2.5 ${
            added
              ? "!bg-emerald-600 !text-white !shadow-none !border-emerald-700 hover:!brightness-110"
              : stockQuantity === 0
              ? "!opacity-40 !cursor-not-allowed"
              : ""
          }`}
        >
          {added ? (
            <span className="flex items-center justify-center gap-2">✓ Agregado</span>
          ) : stockQuantity === 0 ? (
            "Sin Stock"
          ) : (
            "Agregar al Carrito"
          )}
        </LiquidButton>
      </div>
    </motion.div>
  );
}

export default ProductCard;
