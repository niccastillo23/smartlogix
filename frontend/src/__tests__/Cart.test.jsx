import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { CartProvider } from "../context/CartContext";
import { CartDrawerProvider } from "../context/CartDrawerContext";
import Cart from "../components/Cart";

const renderCart = () =>
  render(
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <CartDrawerProvider>
            <Cart />
          </CartDrawerProvider>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );

describe("Cart Component", () => {
  it("should render cart title", () => {
    renderCart();
    const titles = screen.getAllByText(/tu carrito/i);
    expect(titles.length).toBeGreaterThanOrEqual(1);
  });

  it("should show empty cart message when no items", () => {
    renderCart();
    expect(screen.getByText(/vacío/i)).toBeInTheDocument();
  });

  it("should have link to explore products", () => {
    renderCart();
    expect(screen.getByText(/explorar colección/i)).toBeInTheDocument();
  });
});
