import { describe, it, expect, vi, beforeEach } from "vitest";
import { createShipment, getShipmentByOrderId } from "../services/shippingService";
import api from "../services/api";

vi.mock("../services/api", () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}));

describe("shippingService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("createShipment", () => {
    it("should call api.post with correct endpoint and shipment data", async () => {
      const shipmentData = {
        orderId: 1,
        address: "123 Main St",
        city: "Paris",
        country: "France",
      };
      const mockResponse = { data: { id: 1, ...shipmentData, status: "PENDING" } };
      api.post.mockResolvedValue(mockResponse);

      const result = await createShipment(shipmentData);

      expect(api.post).toHaveBeenCalledWith("/shipments", shipmentData);
      expect(result).toEqual(mockResponse);
    });

    it("should throw error when shipment creation fails", async () => {
      api.post.mockRejectedValue(new Error("Invalid order"));

      await expect(createShipment({})).rejects.toThrow("Invalid order");
    });
  });

  describe("getShipmentByOrderId", () => {
    it("should call api.get with correct order id", async () => {
      const mockShipment = { id: 1, orderId: 5, status: "SHIPPED" };
      api.get.mockResolvedValue({ data: mockShipment });

      const result = await getShipmentByOrderId(5);

      expect(api.get).toHaveBeenCalledWith("/shipments/order/5");
      expect(result.data).toEqual(mockShipment);
    });

    it("should throw error when shipment not found", async () => {
      api.get.mockRejectedValue(new Error("Not found"));

      await expect(getShipmentByOrderId(999)).rejects.toThrow("Not found");
    });
  });
});
