import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getAllProducts } from "../services/productService";
import ProductCard from "./ProductCard";
import Hero from "./Hero";
import { useCart } from "../context/CartContext";
import { useCartDrawer } from "../context/CartDrawerContext";

const container = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.08, delayChildren: 0.2 },
  },
};

function ProductCatalog() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { addItem } = useCart();
  const { openDrawer } = useCartDrawer();

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await getAllProducts();
      setProducts(response.data || response);
    } catch {
      setError("Error al cargar productos. Intenta de nuevo más tarde.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    addItem(product);
    openDrawer();
  };

  return (
    <div>
      <Hero />

      <div className="mb-10">
        <p className="section-subtitle">Catálogo</p>
        <h2 className="section-title mt-1">Nuestra Colección</h2>
      </div>

      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-charcoal-800 border border-ivory-100 dark:border-charcoal-700 animate-pulse">
              <div className="aspect-square bg-ivory-100 dark:bg-charcoal-700" />
              <div className="p-5 space-y-3">
                <div className="h-4 bg-ivory-100 dark:bg-charcoal-700 rounded w-3/4" />
                <div className="h-3 bg-ivory-100 dark:bg-charcoal-700 rounded w-1/2" />
                <div className="h-8 bg-ivory-100 dark:bg-charcoal-700 rounded" />
              </div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="text-center py-16">
          <p className="text-rose-500 text-sm">{error}</p>
          <button onClick={fetchProducts} className="btn-outline mt-4">Reintentar</button>
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="text-center py-16">
          <p className="text-charcoal-400 text-sm">No hay productos disponibles.</p>
        </div>
      )}

      {!loading && !error && products.length > 0 && (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8"
        >
          {products.map((product, i) => (
            <ProductCard key={product.id} product={product} index={i} onAddToCart={handleAddToCart} />
          ))}
        </motion.div>
      )}
    </div>
  );
}

export default ProductCatalog;
