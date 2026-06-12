import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { CartProvider } from "../context/CartContext";
import { CartDrawerProvider } from "../context/CartDrawerContext";
import ProductCard from "../components/ProductCard";

const mockProduct = {
  id: 1,
  name: "Sauvage Eau de Parfum",
  brand: "Dior",
  price: 89990,
  stockQuantity: 50,
  fragrance: "Amaderado",
};

const renderCard = (product = mockProduct) =>
  render(
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <CartDrawerProvider>
            <ProductCard product={product} index={0} onAddToCart={vi.fn()} />
          </CartDrawerProvider>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );

describe("ProductCard Component", () => {
  it("should render product name", () => {
    renderCard();
    expect(screen.getByText("Sauvage Eau de Parfum")).toBeInTheDocument();
  });

  it("should render brand name", () => {
    renderCard();
    expect(screen.getByText("Dior")).toBeInTheDocument();
  });

  it("should render price in CLP format", () => {
    renderCard();
    expect(screen.getByText("$89.990")).toBeInTheDocument();
  });

  it("should render fragrance", () => {
    renderCard();
    expect(screen.getByText("Amaderado")).toBeInTheDocument();
  });

  it("should render add to cart button", () => {
    renderCard();
    expect(screen.getByText(/agregar al carrito/i)).toBeInTheDocument();
  });

  it("should show out of stock when stockQuantity is 0", () => {
    renderCard({ ...mockProduct, stockQuantity: 0 });
    expect(screen.getByText(/sin stock/i)).toBeInTheDocument();
  });

  it("should show stock count when available", () => {
    renderCard();
    expect(screen.getByText("50 und.")).toBeInTheDocument();
  });
});
