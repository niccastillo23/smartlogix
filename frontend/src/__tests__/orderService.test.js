import { describe, it, expect, vi, beforeEach } from "vitest";
import { createOrder, getAllOrders } from "../services/orderService";
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

describe("orderService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("createOrder", () => {
    it("should call api.post with correct endpoint and order data", async () => {
      const orderData = {
        customerName: "John Doe",
        email: "john@test.com",
        items: [{ productId: 1, quantity: 2, price: 120.0 }],
        totalAmount: 240.0,
      };
      const mockResponse = { data: { id: 1, ...orderData } };
      api.post.mockResolvedValue(mockResponse);

      const result = await createOrder(orderData);

      expect(api.post).toHaveBeenCalledWith("/orders", orderData);
      expect(result).toEqual(mockResponse);
    });

    it("should throw error when order creation fails", async () => {
      api.post.mockRejectedValue(new Error("Server error"));

      await expect(createOrder({})).rejects.toThrow("Server error");
    });
  });

  describe("getAllOrders", () => {
    it("should call api.get with correct endpoint", async () => {
      const mockOrders = [
        { id: 1, customerName: "John", totalAmount: 100 },
        { id: 2, customerName: "Jane", totalAmount: 200 },
      ];
      api.get.mockResolvedValue({ data: mockOrders });

      const result = await getAllOrders();

      expect(api.get).toHaveBeenCalledWith("/orders");
      expect(result.data).toEqual(mockOrders);
    });

    it("should handle empty orders list", async () => {
      api.get.mockResolvedValue({ data: [] });

      const result = await getAllOrders();

      expect(result.data).toEqual([]);
    });
  });
});
