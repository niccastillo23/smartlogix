import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { CartProvider } from "../context/CartContext";
import { CartDrawerProvider } from "../context/CartDrawerContext";
import ProductCatalog from "../components/ProductCatalog";
import { getAllProducts } from "../services/productService";
import { vi } from "vitest";

vi.mock("../services/productService");

describe("ProductCatalog Component", () => {
  beforeEach(() => {
    getAllProducts.mockResolvedValue({
      data: [
        { id: 1, name: "Sauvage", brand: "Dior", price: 89990, stockQuantity: 50, fragrance: "Amaderado" },
        { id: 2, name: "Bleu", brand: "Chanel", price: 105990, stockQuantity: 40, fragrance: "Cítrico" },
      ],
    });
  });

  it("should render the catalog title", async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <CartProvider>
            <CartDrawerProvider>
              <ProductCatalog />
            </CartDrawerProvider>
          </CartProvider>
        </AuthProvider>
      </MemoryRouter>
    );
    expect(await screen.findByText(/nuestra colección/i)).toBeInTheDocument();
  });

  it("should render product names from API", async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <CartProvider>
            <CartDrawerProvider>
              <ProductCatalog />
            </CartDrawerProvider>
          </CartProvider>
        </AuthProvider>
      </MemoryRouter>
    );
    expect(await screen.findByText("Sauvage")).toBeInTheDocument();
    expect(await screen.findByText("Bleu")).toBeInTheDocument();
  });

  it("should render the catalog section title", async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <CartProvider>
            <CartDrawerProvider>
              <ProductCatalog />
            </CartDrawerProvider>
          </CartProvider>
        </AuthProvider>
      </MemoryRouter>
    );
    expect(await screen.findByText(/nuestra colección/i)).toBeInTheDocument();
  });
});
