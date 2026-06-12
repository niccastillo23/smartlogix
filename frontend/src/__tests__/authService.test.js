import { describe, it, expect, vi, beforeEach } from "vitest";
import { login, register } from "../services/authService";
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

describe("authService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("login", () => {
    it("should call api.post with correct endpoint and credentials", async () => {
      const mockResponse = { data: { token: "test-token-123" } };
      api.post.mockResolvedValue(mockResponse);

      const result = await login("testuser", "password123");

      expect(api.post).toHaveBeenCalledWith("/auth/login", {
        username: "testuser",
        password: "password123",
      });
      expect(result).toEqual(mockResponse);
    });

    it("should throw error when login fails", async () => {
      api.post.mockRejectedValue(new Error("Invalid credentials"));

      await expect(login("baduser", "badpass")).rejects.toThrow("Invalid credentials");
    });
  });

  describe("register", () => {
    it("should call api.post with correct endpoint and credentials", async () => {
      const mockResponse = { data: { id: 1, username: "newuser" } };
      api.post.mockResolvedValue(mockResponse);

      const result = await register("newuser", "newpassword");

      expect(api.post).toHaveBeenCalledWith("/auth/register", {
        username: "newuser",
        password: "newpassword",
      });
      expect(result).toEqual(mockResponse);
    });

    it("should throw error when registration fails", async () => {
      api.post.mockRejectedValue(new Error("Username taken"));

      await expect(register("taken", "pass")).rejects.toThrow("Username taken");
    });
  });
});
