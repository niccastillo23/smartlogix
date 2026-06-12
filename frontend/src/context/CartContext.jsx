import { createContext, useContext, useState, useCallback } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => JSON.parse(localStorage.getItem("cart") || "[]"));
  const [updated, setUpdated] = useState(0);

  const sync = (cart) => {
    setItems(cart);
    localStorage.setItem("cart", JSON.stringify(cart));
    setUpdated((n) => n + 1);
  };

  const addItem = useCallback((product) => {
    const cart = JSON.parse(localStorage.getItem("cart") || "[]");
    const existing = cart.find((i) => i.id === product.id);
    if (existing) existing.quantity += 1;
    else cart.push({ ...product, quantity: 1 });
    sync(cart);
  }, []);

  const removeItem = useCallback((id) => {
    sync(items.filter((i) => i.id !== id));
  }, [items]);

  const updateQuantity = useCallback((id, delta) => {
    sync(items.map((i) => (i.id === id ? { ...i, quantity: Math.max(1, i.quantity + delta) } : i)));
  }, [items]);

  const clearCart = useCallback(() => sync([]), []);

  const count = items.reduce((s, i) => s + i.quantity, 0);
  const total = items.reduce((s, i) => s + (i.price || 0) * i.quantity, 0);

  return (
    <CartContext.Provider value={{ items, count, total, updated, addItem, removeItem, updateQuantity, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
