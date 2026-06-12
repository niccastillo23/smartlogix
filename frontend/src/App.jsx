import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import { CartDrawerProvider } from "./context/CartDrawerContext";
import { ThemeProvider } from "./context/ThemeContext";
import Login from "./components/Login";
import ProductCatalog from "./components/ProductCatalog";
import Cart from "./components/Cart";
import OrderStatus from "./components/OrderStatus";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <CartProvider>
          <CartDrawerProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                <Route path="/" element={<ProductCatalog />} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/orders" element={<OrderStatus />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </CartDrawerProvider>
        </CartProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
