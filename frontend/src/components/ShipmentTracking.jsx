import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { getShipmentByOrderId } from "../services/shippingService";
import { formatPrice } from "../utils/formatPrice";

function ShipmentTracking({ orderId }) {
  const [shipment, setShipment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!orderId) return;
    setLoading(true);
    getShipmentByOrderId(orderId)
      .then((res) => setShipment(res.data))
      .catch(() => setError("No se encontró información de envío."))
      .finally(() => setLoading(false));
  }, [orderId]);

  if (loading) return <div className="h-2 bg-ivory-100 dark:bg-charcoal-700 rounded animate-pulse mt-4" />;
  if (error) return <p className="text-xs text-charcoal-400 mt-4">{error}</p>;
  if (!shipment) return null;

  const statusSteps = ["REGISTERED", "IN_TRANSIT", "DELIVERED"];
  const currentIdx = statusSteps.indexOf(shipment.status?.toUpperCase());

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 pt-4 border-t border-ivory-100"
    >
      <p className="text-[10px] text-charcoal-400 tracking-wider uppercase mb-3">Envío</p>

      <div className="flex items-center gap-3 text-sm">
        <span className={`text-xs font-medium px-2 py-0.5 ${
          shipment.circuitBreakerFallback ? "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300" : "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300"
        }`}>
          {shipment.circuitBreakerFallback ? "Fallback Activo" : shipment.carrier}
        </span>
        <span className="text-charcoal-400 text-xs">•</span>
        <span className="text-charcoal-600 text-xs">{shipment.trackingNumber}</span>
      </div>

      <div className="flex items-center gap-2 mt-3">
        {statusSteps.map((s, i) => (
          <div key={s} className="flex items-center flex-1">
            <div className={`w-2.5 h-2.5 rounded-full ${i <= currentIdx ? "bg-charcoal-800 dark:bg-cream-50" : "bg-ivory-200 dark:bg-charcoal-600"}`} />
            {i < statusSteps.length - 1 && (
              <div className={`flex-1 h-px ${i < currentIdx ? "bg-charcoal-800 dark:bg-cream-50" : "bg-ivory-200 dark:bg-charcoal-600"}`} />
            )}
          </div>
        ))}
      </div>
      <div className="flex justify-between text-[9px] text-charcoal-400 tracking-wider uppercase mt-1">
        <span>Registrado</span>
        <span>En Tránsito</span>
        <span>Entregado</span>
      </div>
    </motion.div>
  );
}

export default ShipmentTracking;
