import api from "./api";

export async function getAllProducts() {
  return api.get("/products");
}

export async function getProductById(id) {
  return api.get(`/products/${id}`);
}
