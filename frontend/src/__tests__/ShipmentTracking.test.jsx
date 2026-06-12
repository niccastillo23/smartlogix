import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import ShipmentTracking from "../components/ShipmentTracking";
import { getShipmentByOrderId } from "../services/shippingService";
import { vi } from "vitest";

vi.mock("../services/shippingService");

describe("ShipmentTracking Component", () => {
  beforeEach(() => {
    getShipmentByOrderId.mockResolvedValue({
      data: {
        id: 1,
        orderId: 1,
        carrier: "DHL",
        trackingNumber: "TRK-TEST123",
        status: "REGISTERED",
        estimatedDelivery: "2024-12-20",
        circuitBreakerFallback: false,
        address: "Calle 123",
        city: "Santiago",
        country: "Chile",
        createdAt: "2024-12-13T00:00:00",
      },
    });
  });

  it("should render without crashing when no orderId", () => {
    const { container } = render(
      <MemoryRouter>
        <AuthProvider>
          <ShipmentTracking />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(container).toBeTruthy();
  });

  it("should fetch shipment when orderId is provided", async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <ShipmentTracking orderId={1} />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(await screen.findByText(/DHL/i)).toBeInTheDocument();
    expect(await screen.findByText("TRK-TEST123")).toBeInTheDocument();
  });

  it("should show fallback indicator when circuit breaker was used", async () => {
    getShipmentByOrderId.mockResolvedValue({
      data: {
        id: 2, orderId: 2, carrier: "FAIL_CARRIER",
        trackingNumber: "FBK-00001", status: "REGISTERED",
        circuitBreakerFallback: true,
        address: "Test", city: "Test", country: "Test",
        createdAt: "2024-12-13T00:00:00",
      },
    });
    render(
      <MemoryRouter>
        <AuthProvider>
          <ShipmentTracking orderId={2} />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(await screen.findByText(/fallback activo/i)).toBeInTheDocument();
  });

  it("should show error when shipment is not found", async () => {
    getShipmentByOrderId.mockRejectedValue(new Error("Not found"));
    render(
      <MemoryRouter>
        <AuthProvider>
          <ShipmentTracking orderId={999} />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(await screen.findByText(/no se encontró/i)).toBeInTheDocument();
  });
});
