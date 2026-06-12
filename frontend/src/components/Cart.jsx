import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { createOrder } from "../services/orderService";
import { createShipment } from "../services/shippingService";
import OrderForm from "./OrderForm";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
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

  if (err) return <span className="text-xl text-charcoal-300">✦</span>;
  return <img key={src} src={src} alt={item.name} className="w-full h-full object-cover" onError={() => setIdx((p) => p + 1)} />;
}

function Cart() {
  const { items, total, removeItem, updateQuantity, clearCart } = useCart();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handlePlaceOrder = async (orderData) => {
    try {
      setError("");
      const orderPayload = {
        customerId: 1,
        customerName: orderData.customerName,
        email: orderData.email,
        orderType: orderData.orderType,
        items: items.map((item) => ({
          productId: item.id, productName: item.name,
          quantity: item.quantity, unitPrice: item.price,
        })),
      };
      const orderResponse = await createOrder(orderPayload);
      const orderId = orderResponse.data.id;

      await createShipment({
        orderId, carrier: "DHL",
        address: orderData.address, city: orderData.city, country: orderData.country,
      });

      clearCart();
      setSuccess("¡Pedido realizado con éxito!");
      setShowOrderForm(false);
      setTimeout(() => navigate("/orders"), 2000);
    } catch {
      setError("Error al realizar el pedido. Intenta de nuevo.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-10">
        <p className="section-subtitle">Revisión</p>
        <h2 className="section-title mt-1">Tu Carrito</h2>
      </div>

      <AnimatePresence>
        {error && (
          <motion.p initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="text-rose-500 text-xs bg-rose-50 dark:bg-rose-900/30 py-2 px-4 mb-6">{error}</motion.p>
        )}
        {success && (
          <motion.p initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="text-emerald-600 text-xs bg-emerald-50 dark:bg-emerald-900/30 py-2 px-4 mb-6">{success}</motion.p>
        )}
      </AnimatePresence>

      {items.length === 0 && !success && (
        <div className="text-center py-16">
          <p className="text-charcoal-400 text-sm mb-6">Tu carrito está vacío</p>
          <Link to="/" className="btn-primary">Explorar Colección</Link>
        </div>
      )}

      {items.length > 0 && (
        <>
          <div className="space-y-4 mb-8">
            {items.map((item) => (
              <motion.div
                key={item.id} layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-5 p-5 bg-white dark:bg-charcoal-800 border border-ivory-100 dark:border-charcoal-700"
              >
                <div
                  className="w-20 h-20 flex-shrink-0 overflow-hidden"
                  style={{ background: getGradient(item.fragrance) }}
                >
                  <CartItemImage item={item} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gold-600 dark:text-gold-400 tracking-wider uppercase font-medium">{item.brand}</p>
                  <p className="font-display text-base font-semibold text-charcoal-800 dark:text-cream-50 truncate">{item.name}</p>
                  <p className="font-display text-lg font-bold text-charcoal-800 dark:text-cream-50 mt-1">{formatPrice(item.price)}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center border border-ivory-200 dark:border-charcoal-600">
                    <button onClick={() => updateQuantity(item.id, -1)} className="w-8 h-8 flex items-center justify-center text-xs text-charcoal-400 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-cream-50 transition-colors">−</button>
                    <span className="w-8 h-8 flex items-center justify-center text-xs font-medium text-charcoal-700 dark:text-cream-200 border-x border-ivory-200 dark:border-charcoal-600">{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, 1)} className="w-8 h-8 flex items-center justify-center text-xs text-charcoal-400 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-cream-50 transition-colors">+</button>
                  </div>
                  <button onClick={() => removeItem(item.id)} className="text-[10px] text-charcoal-400 hover:text-rose-500 tracking-wider uppercase transition-colors ml-2">Eliminar</button>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="bg-white dark:bg-charcoal-800 border border-ivory-100 dark:border-charcoal-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <span className="text-sm text-charcoal-500 dark:text-charcoal-400">Subtotal</span>
              <span className="font-display text-2xl font-bold text-charcoal-800 dark:text-cream-50">{formatPrice(total)}</span>
            </div>
            <button onClick={() => setShowOrderForm(true)} className="btn-primary w-full">Finalizar Compra</button>
          </div>
        </>
      )}

      <AnimatePresence>
        {showOrderForm && (
          <OrderForm onSubmit={handlePlaceOrder} onCancel={() => setShowOrderForm(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}

export default Cart;
