import { describe, it, expect, vi, beforeEach } from "vitest";
import { getAllProducts, getProductById } from "../services/productService";
import api from "../services/api";

vi.mock("../services/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}));

describe("productService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getAllProducts", () => {
    it("should call api.get with correct endpoint", async () => {
      const mockProducts = [
        { id: 1, name: "Chanel No. 5", brand: "Chanel", price: 120.0 },
        { id: 2, name: "Sauvage", brand: "Dior", price: 95.0 },
      ];
      api.get.mockResolvedValue({ data: mockProducts });

      const result = await getAllProducts();

      expect(api.get).toHaveBeenCalledWith("/products");
      expect(result.data).toEqual(mockProducts);
      expect(result.data).toHaveLength(2);
    });

    it("should handle empty product list", async () => {
      api.get.mockResolvedValue({ data: [] });

      const result = await getAllProducts();

      expect(result.data).toEqual([]);
    });

    it("should throw error when request fails", async () => {
      api.get.mockRejectedValue(new Error("Network error"));

      await expect(getAllProducts()).rejects.toThrow("Network error");
    });
  });

  describe("getProductById", () => {
    it("should call api.get with correct product id", async () => {
      const mockProduct = { id: 1, name: "Chanel No. 5", brand: "Chanel", price: 120.0 };
      api.get.mockResolvedValue({ data: mockProduct });

      const result = await getProductById(1);

      expect(api.get).toHaveBeenCalledWith("/products/1");
      expect(result.data).toEqual(mockProduct);
    });

    it("should throw error when product not found", async () => {
      api.get.mockRejectedValue(new Error("Not found"));

      await expect(getProductById(999)).rejects.toThrow("Not found");
    });
  });
});
