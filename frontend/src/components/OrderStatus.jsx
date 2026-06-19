import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { getAllOrders } from "../services/orderService";
import { useAuth } from "../context/AuthContext";
import { formatPrice } from "../utils/formatPrice";
import { MetalButton, LiquidButton } from "./ui/liquid-glass-button";

const statusConfig = {
  PENDING: { label: "Pendiente", class: "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800" },
  CONFIRMED: { label: "Confirmado", class: "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800" },
  PROCESSING: { label: "En Preparación", class: "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800" },
  SHIPPED: { label: "En Camino", class: "bg-cyan-50 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800" },
  DELIVERED: { label: "Entregado", class: "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800" },
  CANCELLED: { label: "Cancelado", class: "bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800" },
};

function OrderStatus() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { logout, user } = useAuth();

  useEffect(() => { fetchOrders(); }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await getAllOrders();
      setOrders(response.data || response);
    } catch {
      setError("Error al cargar los pedidos.");
    } finally {
      setLoading(false);
    }
  };

  const getConfig = (status) => statusConfig[status?.toUpperCase()] || statusConfig.PENDING;

  const timelineSteps = [
    { key: "PENDING", label: "Pendiente" },
    { key: "CONFIRMED", label: "Confirmado" },
    { key: "PROCESSING", label: "Preparación" },
    { key: "SHIPPED", label: "En Camino" },
    { key: "DELIVERED", label: "Entregado" },
  ];

  const getCurrentStep = (status) => {
    const idx = timelineSteps.findIndex((s) => s.key === status?.toUpperCase());
    return idx >= 0 ? idx : 0;
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-10">
        <p className="section-subtitle">Seguimiento</p>
        <h2 className="section-title mt-1">Tus Pedidos</h2>
      </div>

      {loading && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-charcoal-800 border border-ivory-100 dark:border-charcoal-700 p-6 animate-pulse space-y-3">
              <div className="h-5 bg-ivory-100 dark:bg-charcoal-700 rounded w-1/3" />
              <div className="h-3 bg-ivory-100 dark:bg-charcoal-700 rounded w-1/2" />
              <div className="h-3 bg-ivory-100 dark:bg-charcoal-700 rounded w-2/3" />
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="text-center py-16">
          <p className="text-rose-500 text-sm">{error}</p>
          <LiquidButton onClick={fetchOrders} variant="outline" size="sm" className="mt-4">Reintentar</LiquidButton>
        </div>
      )}

      {!loading && !error && orders.length === 0 && (
        <div className="text-center py-16">
          <p className="text-charcoal-400 text-sm mb-6">Aún no tienes pedidos</p>
          <Link to="/"><MetalButton variant="gold">Ir a Comprar</MetalButton></Link>
        </div>
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="space-y-8">
          {orders.map((order, i) => {
            const step = getCurrentStep(order.status);
            return (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className="bg-white dark:bg-charcoal-800 border border-ivory-100 dark:border-charcoal-700 overflow-hidden"
              >
                  <div className="px-6 py-4 border-b border-ivory-100 dark:border-charcoal-700 flex items-center justify-between">
                  <div>
                    <span className="font-display text-base font-semibold text-charcoal-800 dark:text-cream-50">Pedido #{order.id}</span>
                    <span className="ml-3 text-xs text-charcoal-400 dark:text-charcoal-400">{new Date(order.createdAt).toLocaleDateString("es-CL", { year: "numeric", month: "long", day: "numeric" })}</span>
                  </div>
                  <span className={`text-[10px] tracking-wider uppercase font-medium px-3 py-1.5 border ${getConfig(order.status).class}`}>
                    {getConfig(order.status).label}
                  </span>
                </div>

                <div className="px-6 py-5">
                  <div className="grid grid-cols-3 gap-4 text-sm mb-5">
                    <div>
                      <p className="text-[10px] text-charcoal-400 dark:text-charcoal-400 tracking-wider uppercase">Cliente</p>
                      <p className="text-charcoal-700 dark:text-cream-200 font-medium mt-0.5">{order.customerName}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-charcoal-400 dark:text-charcoal-400 tracking-wider uppercase">Tipo</p>
                      <p className="text-charcoal-700 dark:text-cream-200 font-medium mt-0.5">{order.orderType}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-charcoal-400 dark:text-charcoal-400 tracking-wider uppercase">Total</p>
                      <p className="font-display text-lg font-bold text-charcoal-800 dark:text-cream-50 mt-0.5">{formatPrice(order.totalAmount)}</p>
                    </div>
                  </div>

                  {order.status?.toUpperCase() !== "CANCELLED" && (
                    <div className="pt-4 border-t border-ivory-100 dark:border-charcoal-700">
                      <div className="flex items-center justify-between">
                        {timelineSteps.map((s, idx) => (
                          <div key={s.key} className="flex flex-col items-center flex-1">
                            <div className={`w-5 h-5 rounded-full flex items-center justify-center transition-all duration-500 ${
                              idx <= step ? "bg-charcoal-800 dark:bg-cream-50" : "bg-ivory-200 dark:bg-charcoal-600"
                            }`}>
                              {idx < step && (
                                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round">
                                  <polyline points="20 6 9 17 4 12"/>
                                </svg>
                              )}
                            </div>
                            <p className={`text-[9px] tracking-wider uppercase mt-1.5 ${
                              idx <= step ? "text-charcoal-700 dark:text-cream-200 font-medium" : "text-charcoal-300 dark:text-charcoal-500"
                            }`}>{s.label}</p>
                          </div>
                        ))}
                      </div>
                      <div className="relative mt-[-16px] mx-[10%]">
                        <div className="h-[1px] bg-ivory-200 dark:bg-charcoal-600 w-full" />
                        <motion.div
                          initial={{ width: "0%" }}
                          animate={{ width: `${(step / (timelineSteps.length - 1)) * 100}%` }}
                          transition={{ duration: 1, ease: [0.25, 0.46, 0.45, 0.94] }}
                          className="h-[1px] bg-charcoal-800 absolute top-0 left-0"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default OrderStatus;
