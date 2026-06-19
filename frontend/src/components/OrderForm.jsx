import { motion } from "framer-motion";
import { useState } from "react";
import { MetalButton, LiquidButton } from "./ui/liquid-glass-button";

function OrderForm({ onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    customerName: "",
    email: "",
    address: "",
    city: "",
    country: "",
    orderType: "WEB",
  });

  const handleChange = (e) => setFormData((p) => ({ ...p, [e.target.name]: e.target.value }));
  const handleSubmit = (e) => { e.preventDefault(); onSubmit(formData); };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onCancel()}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="w-full max-w-lg bg-white dark:bg-charcoal-800 shadow-2xl"
      >
        <div className="px-8 py-6 border-b border-ivory-100 dark:border-charcoal-700 flex items-center justify-between">
          <div>
            <p className="text-xs text-charcoal-400 dark:text-charcoal-400 tracking-[0.15em] uppercase">Checkout</p>
            <p className="font-display text-xl font-semibold text-charcoal-800 dark:text-cream-50 mt-0.5">Detalles de Envío</p>
          </div>
          <button onClick={onCancel} className="p-2 text-charcoal-400 hover:text-charcoal-800 dark:text-charcoal-400 dark:hover:text-cream-50 transition-colors">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-8 py-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label htmlFor="customerName" className="block text-xs text-charcoal-500 tracking-[0.12em] uppercase mb-1">Nombre Completo</label>
              <input id="customerName" name="customerName" value={formData.customerName} onChange={handleChange} required className="input-field" />
            </div>
            <div className="col-span-2">
              <label htmlFor="email" className="block text-xs text-charcoal-500 tracking-[0.12em] uppercase mb-1">Email</label>
              <input id="email" name="email" type="email" value={formData.email} onChange={handleChange} required className="input-field" />
            </div>
            <div className="col-span-2">
              <label htmlFor="address" className="block text-xs text-charcoal-500 tracking-[0.12em] uppercase mb-1">Dirección</label>
              <input id="address" name="address" value={formData.address} onChange={handleChange} required className="input-field" />
            </div>
            <div>
              <label htmlFor="city" className="block text-xs text-charcoal-500 tracking-[0.12em] uppercase mb-1">Ciudad</label>
              <input id="city" name="city" value={formData.city} onChange={handleChange} required className="input-field" />
            </div>
            <div>
              <label htmlFor="country" className="block text-xs text-charcoal-500 tracking-[0.12em] uppercase mb-1">País</label>
              <input id="country" name="country" value={formData.country} onChange={handleChange} required className="input-field" />
            </div>
            <div className="col-span-2">
              <label htmlFor="orderType" className="block text-xs text-charcoal-500 tracking-[0.12em] uppercase mb-1">Tipo de Pedido</label>
              <select id="orderType" name="orderType" value={formData.orderType} onChange={handleChange} className="input-field appearance-none">
                <option value="WEB">WEB — 5% de descuento, envío estándar</option>
                <option value="MARKETPLACE">MARKETPLACE — 10% de descuento, envío express</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <LiquidButton type="button" onClick={onCancel} variant="outline" size="lg" className="flex-1">Cancelar</LiquidButton>
            <MetalButton type="submit" variant="primary" className="flex-1">Confirmar Pedido</MetalButton>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
}

export default OrderForm;
