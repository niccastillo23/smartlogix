import api from "./api";

export async function createOrder(orderData) {
  return api.post("/orders", orderData);
}

export async function getAllOrders() {
  return api.get("/orders");
}
