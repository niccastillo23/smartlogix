import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { useCart } from "../context/CartContext";
import { useCartDrawer } from "../context/CartDrawerContext";
import { formatPrice } from "../utils/formatPrice";
import { getGradient, getProductImageBase } from "../utils/productImages";

const IMG_EXT = [".webp", ".jpg", ".svg"];

function CartItemImage({ item }) {
  const [src, setSrc] = useState(null);
  const [err, setErr] = useState(false);
  const [idx, setIdx] = useState(0);
  const base = getProductImageBase(item);

  useEffect(() => {
    setIdx(0); setErr(false); setSrc(null);
  }, [item.id]);

  useEffect(() => {
    if (idx < IMG_EXT.length) setSrc(base + IMG_EXT[idx]);
    else setErr(true);
  }, [idx, base]);

  if (err) {
    return <span className="text-lg">✦</span>;
  }

  return (
    <img
      key={src}
      src={src}
      alt={item.name}
      className="w-full h-full object-cover"
      onError={() => setIdx((p) => p + 1)}
    />
  );
}

function CartDrawer() {
  const { isOpen, closeDrawer } = useCartDrawer();
  const { items, count, total, removeItem, updateQuantity } = useCart();
  const navigate = useNavigate();

  const handleCheckout = () => {
    closeDrawer();
    navigate("/cart");
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={closeDrawer}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50"
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="fixed top-0 right-0 bottom-0 w-full max-w-md bg-white dark:bg-charcoal-800 z-50 shadow-2xl flex flex-col"
          >
            <div className="flex items-center justify-between px-6 py-5 border-b border-ivory-100 dark:border-charcoal-700">
              <div>
                <p className="text-xs text-charcoal-400 dark:text-charcoal-400 tracking-[0.15em] uppercase">Carrito</p>
                <p className="text-sm text-charcoal-600 dark:text-cream-300">{count} {count === 1 ? "artículo" : "artículos"}</p>
              </div>
              <button onClick={closeDrawer} className="p-2 text-charcoal-400 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-cream-50 transition-colors">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto scrollbar-thin px-6 py-4 space-y-3">
              <AnimatePresence>
                {items.length === 0 && (
                  <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center text-charcoal-400 text-sm py-12">
                    Tu carrito está vacío
                  </motion.p>
                )}
                {items.map((item) => (
                  <motion.div
                    key={item.id}
                    layout
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="flex gap-4 py-4 border-b border-ivory-50 dark:border-charcoal-700"
                  >
                    <div
                      className="w-16 h-16 flex-shrink-0 overflow-hidden"
                      style={{ background: getGradient(item.fragrance) }}
                    >
                      <CartItemImage item={item} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-charcoal-800 dark:text-cream-50 truncate">{item.name}</p>
                      <p className="text-[11px] text-charcoal-400 tracking-wider uppercase">{item.brand}</p>
                      <p className="text-sm font-semibold text-charcoal-700 dark:text-cream-200 mt-1">{formatPrice(item.price)}</p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <div className="flex items-center gap-2 border border-ivory-200 dark:border-charcoal-600 px-2 py-1">
                        <button onClick={() => updateQuantity(item.id, -1)} className="text-charcoal-400 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-cream-50 text-xs w-5 h-5 flex items-center justify-center transition-colors">−</button>
                        <span className="text-xs font-medium text-charcoal-700 dark:text-cream-200 w-4 text-center">{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.id, 1)} className="text-charcoal-400 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-cream-50 text-xs w-5 h-5 flex items-center justify-center transition-colors">+</button>
                      </div>
                      <button onClick={() => removeItem(item.id)} className="text-[10px] text-charcoal-400 hover:text-rose-500 tracking-wider uppercase transition-colors">Eliminar</button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {items.length > 0 && (
              <div className="border-t border-ivory-100 dark:border-charcoal-700 px-6 py-5 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-charcoal-500 dark:text-charcoal-400">Subtotal</span>
                  <span className="font-display text-lg font-semibold text-charcoal-800 dark:text-cream-50">{formatPrice(total)}</span>
                </div>
                <p className="text-[11px] text-charcoal-400 dark:text-charcoal-400 tracking-wider">Los costos de envío se calculan al finalizar la compra.</p>
                <button onClick={handleCheckout} className="btn-primary w-full">Finalizar Compra</button>
              </div>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}

export default CartDrawer;
