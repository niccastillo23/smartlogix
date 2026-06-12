import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import OrderStatus from "../components/OrderStatus";
import { getAllOrders } from "../services/orderService";
import { vi } from "vitest";

vi.mock("../services/orderService");

const renderOrders = () =>
  render(
    <MemoryRouter>
      <AuthProvider>
        <OrderStatus />
      </AuthProvider>
    </MemoryRouter>
  );

describe("OrderStatus Component", () => {
  beforeEach(() => {
    getAllOrders.mockResolvedValue({ data: [] });
  });

  it("should render the title", () => {
    renderOrders();
    expect(screen.getByText(/tus pedidos/i)).toBeInTheDocument();
  });

  it("should show empty state message", async () => {
    renderOrders();
    expect(await screen.findByText(/aún no tienes pedidos/i)).toBeInTheDocument();
  });

  it("should have link to shop", async () => {
    renderOrders();
    expect(await screen.findByText(/ir a comprar/i)).toBeInTheDocument();
  });

  it("should render orders when data is returned", async () => {
    getAllOrders.mockResolvedValue({
      data: [
        { id: 1, customerName: "Juan Pérez", orderType: "WEB", status: "PENDING", totalAmount: 170980, createdAt: "2024-12-13T00:00:00" },
        { id: 2, customerName: "María López", orderType: "MARKETPLACE", status: "SHIPPED", totalAmount: 95391, createdAt: "2024-12-12T00:00:00" },
      ],
    });
    renderOrders();
    expect(await screen.findByText(/pedido #1/i)).toBeInTheDocument();
    expect(await screen.findByText(/pedido #2/i)).toBeInTheDocument();
    expect(await screen.findByText("Juan Pérez")).toBeInTheDocument();
    expect(await screen.findByText("María López")).toBeInTheDocument();
  });

  it("should show cancelled status correctly", async () => {
    getAllOrders.mockResolvedValue({
      data: [
        { id: 3, customerName: "Test", orderType: "WEB", status: "CANCELLED", totalAmount: 50000, createdAt: "2024-12-11T00:00:00" },
      ],
    });
    renderOrders();
    expect(await screen.findByText(/cancelado/i)).toBeInTheDocument();
  });
});
